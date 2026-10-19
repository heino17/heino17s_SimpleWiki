"""Ein Tiddlyhost-Server als Testfigur.

Startet auf einem freien Port und spielt genau das nach, was die Wiki
vom Tiddlyhost-Wikiwise-Fork zu sehen bekommt:

  GET    /wiki/<name>/            simplewiki.html, mit den Server-Metas
                                  im Kopf und der Dateninsel des Wikis
  GET    /simplewiki/status       wer angemeldet ist
  GET    /simplewiki/data         die Dateninsel als JSON, mit ETag
  PUT    /simplewiki/data         die Dateninsel ersetzen (If-Match -> 409)
  DELETE /users/sign_out          Sitzung loeschen

Die Wiki erkennt den Server an drei Meta-Zeilen im Kopf:

    <meta name="simplewiki-server" content="tiddlyhost">
    <meta name="simplewiki-status-url" content="<adresse>/simplewiki/status">
    <meta name="simplewiki-data-url"   content="<adresse>/simplewiki/data">

Diese Testfigur setzt genau diese drei Zeilen und ersetzt die Dateninsel
durch den JSON-Stand des Wikis. Geschrieben wird als Ganzes - so, wie es
der Fork tut.

Wie mwsserver.py: der Server merkt sich jeden Aufruf in einer Liste
(anfragen), damit der Test nachsehen kann, ob die Wiki die vereinbarten
Wege geht - mit dem Kopf X-Requested-With, mit If-Match, ohne die Insel
zu ueberschreiben.

Das ist eine Testfigur, kein Tiddlyhost: sie spricht nur die wenigen
Punkte an, die die Wiki braucht.
"""

import io
import json
import os
import re
import sys
import threading

try:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
except ImportError:                                    # pragma: no cover
    BaseHTTPRequestHandler = ThreadingHTTPServer = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy                                             # noqa: E402

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(PROJEKT, 'simplewiki.html')

# Die Vorlage der Dateninsel - leer, aber gueltig.
LEERE_INSEL = {'version': 1, 'seiten': [], 'startseite': '',
               'sprache': 'de', 'thema': 'light'}


def insel_aus_seiten(seiten, startseite='', sprache='de', thema='light',
                     palette='', eigeneFarben=None, fremd=None):
    """Eine Dateninsel in der Austauschform bauen."""
    daten = dict(fremd or {})
    daten.update({
        'version': 1,
        'seiten': list(seiten or []),
        'startseite': startseite,
        'sprache': sprache,
        'thema': thema,
        'palette': palette,
        'eigeneFarben': eigeneFarben,
    })
    return daten


class Wiki:
    """Der Inhalt eines Wikis: die Dateninsel und ihre Fassung."""

    def __init__(self, slug, insel=None, nurLesen=False, angemeldet=True,
                 name='Testnutzer', skript='', vorab='', ersetzungen=None,
                 status_aus=False, schreib_aus=False):
        self.slug = slug
        # Die Dateninsel. Ohne Vorgabe: leer.
        self.insel = dict(insel) if insel else dict(LEERE_INSEL)
        self.nurLesen = nurLesen
        self.angemeldet = angemeldet
        self.name = name
        # Was die Testfigur in die ausgelieferte Seite einhaengt.
        self.skript = skript
        self.vorab = vorab
        self.ersetzungen = list(ersetzungen or [])
        # Der Server bricht /status ab, statt zu antworten.
        self.status_aus = status_aus
        # Jeder PUT antwortet mit 409: so laesst sich der Konflikt
        # nachstellen, ohne zwei Browser zu brauchen.
        self.schreib_aus = schreib_aus
        self.zaehler = 0

    def etag(self):
        """Die Fassung der Insel - ihr Inhalt kurz und stabil benannt.

        Kein Hash aus Zeit und Zufall: derselbe Inhalt hat dieselbe
        Fassung, ein anderer Inhalt eine andere. So kann der Test ein
        409 ausloesen, indem er dem Wiki vorher eine andere Insel gibt.
        """
        roh = json.dumps(self.insel, sort_keys=True, ensure_ascii=False)
        h = 0x811c9dc5
        for ch in roh:
            h = ((h ^ ord(ch)) * 0x01000193) & 0xffffffff
        return '"%s-%d"' % (self.slug, h)

    def schreiben(self, daten):
        """Die Insel ersetzen. Liefert die neue Fassung."""
        self.insel = daten
        self.zaehler += 1
        return self.etag()

    def status_antwort(self):
        return {
            'kind': 'simple',
            'version': 'v0.1.47',
            'logged_in': bool(self.angemeldet),
            'logged_in_as': self.name if self.angemeldet else None,
            'etag': self.etag(),
        }


# ------------------------------------------------------------------ Server

class Handler(BaseHTTPRequestHandler):
    """Beantwortet die Aufrufe, die die Wiki macht, und sonst nichts."""

    wikis = {}
    anfragen = None

    def log_message(self, *args):
        """Nichts auf die Konsole - der Testlauf soll lesbar bleiben."""

    # ---------------------------------------------------------- Hilfsmittel
    def _json(self, code, daten, extra=None):
        if getattr(self, 'eintrag', None) is not None:
            self.eintrag['antwort'] = code
        roh = json.dumps(daten, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(roh)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(roh)

    def _html(self, code, text):
        roh = text.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def _leer(self, code, extra=None):
        if getattr(self, 'eintrag', None) is not None:
            self.eintrag['antwort'] = code
        self.send_response(code)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def _koerper(self):
        laenge = int(self.headers.get('Content-Length') or 0)
        if not laenge:
            return None
        roh = self.rfile.read(laenge).decode('utf-8')
        try:
            return json.loads(roh)
        except ValueError:
            return 'kaputt'

    def _wiki(self, slug):
        return self.wikis.get(slug)

    # -------------------------------------------------------------- Holen
    def do_GET(self):
        m = re.match(r'^/wiki/([^/]+)/$', self.path)
        if m and m.group(1) in self.wikis:
            self.eintrag = None
            self.anfragen.append({'weg': 'GET', 'pfad': self.path})
            self._html(200, self._mit_insel(self.wikis[m.group(1)]))
            return
        m = re.match(r'^/simplewiki/status$', self.path)
        if m:
            # Einen Status gibt es pro Host; im Test gibt es nur einen
            # Haupt-Wiki. Welcher gemeint ist, steht nicht im Pfad - die
            # Testfigur nimmt das erste.
            wiki = next(iter(self.wikis.values()))
            self.eintrag = None
            self.anfragen.append({'weg': 'GET', 'pfad': self.path,
                                  'xhr': self.headers.get('X-Requested-With')})
            if wiki.status_aus:
                self.close_connection = True
                return
            self._json(200, wiki.status_antwort(), extra={'ETag': wiki.etag()})
            return
        m = re.match(r'^/simplewiki/data$', self.path)
        if m:
            wiki = next(iter(self.wikis.values()))
            self.eintrag = None
            self.anfragen.append({'weg': 'GET', 'pfad': self.path,
                                  'xhr': self.headers.get('X-Requested-With')})
            self._json(200, wiki.insel, extra={'ETag': wiki.etag()})
            return
        self._json(404, {'error': 'not found'})

    # -------------------------------------------------------------- Schreiben
    def do_PUT(self):
        m = re.match(r'^/simplewiki/data$', self.path)
        if not m:
            self._json(404, {'error': 'not found'})
            return
        wiki = next(iter(self.wikis.values()))
        koerper = self._koerper()
        self.eintrag = {
            'weg': 'PUT',
            'pfad': self.path,
            'kopf': self.headers.get('X-Requested-With'),
            'if_match': self.headers.get('If-Match'),
            'nutzlast': koerper,
        }
        self.anfragen.append(self.eintrag)

        # Der Kopf ist Pflicht - ohne ihn ist es eine fremde Anfrage.
        if self.headers.get('X-Requested-With') != 'fetch':
            self._json(400, {'error': 'INVALID_X_REQUESTED_WITH'})
            return
        if wiki.nurLesen:
            self._json(403, {'error': 'NO_WRITE_PERMISSION'})
            return
        if wiki.schreib_aus:
            self._json(409, {'error': 'CONFLICT'},
                       extra={'ETag': wiki.etag()})
            return
        if koerper == 'kaputt' or not isinstance(koerper, dict) or 'seiten' not in koerper:
            self._json(422, {'error': 'INVALID_PAYLOAD'})
            return
        # Wenn ein If-Match mitkam, muss es zur aktuellen Fassung passen.
        if_match = self.headers.get('If-Match')
        if if_match and if_match != wiki.etag():
            self._json(409, {'error': 'CONFLICT'}, extra={'ETag': wiki.etag()})
            return
        neu = wiki.schreiben(koerper)
        self._leer(204, extra={'ETag': neu})

    def do_DELETE(self):
        m = re.match(r'^/users/sign_out$', self.path)
        if not m:
            self._json(404, {'error': 'not found'})
            return
        self.eintrag = None
        self.anfragen.append({'weg': 'DELETE', 'pfad': self.path,
                              'xhr': self.headers.get('X-Requested-With')})
        for w in self.wikis.values():
            w.angemeldet = False
        self._leer(204)

    # ------------------------------------------------------- Metas und Insel
    def _mit_insel(self, wiki):
        """simplewiki.html mit Server-Metas und der Insel des Wikis."""
        with io.open(QUELLE, encoding='utf-8') as fh:
            html = fh.read()
        for a, b in wiki.ersetzungen:
            html = html.replace(a, b)
        basis = 'http://%s' % self.headers.get('Host', '127.0.0.1')
        metas = (
            '<meta name="simplewiki-server" content="tiddlyhost">\n'
            '    <meta name="simplewiki-status-url" content="%s/simplewiki/status">\n'
            '    <meta name="simplewiki-data-url" content="%s/simplewiki/data">\n'
            % (basis, basis)
        )
        # Die Metas hinter <meta charset>, damit sie sicher im Kopf landen.
        html = html.replace('<meta charset="UTF-8">',
                            '<meta charset="UTF-8">\n    ' + metas, 1)
        # Die Dateninsel durch den Stand des Wikis ersetzen.
        inhalt = json.dumps(wiki.insel, ensure_ascii=False).replace('<', '\\u003c')
        html = re.sub(r'(<script id="simplewiki-daten"[^>]*>)[\s\S]*?(</script>)',
                      lambda mm: mm.group(1) + inhalt + mm.group(2), html, count=1)
        return mkcopy.hauptskripte(html, pre=wiki.vorab, script=wiki.skript)


# ------------------------------------------------------------------ Start

def starten(wikis, port=0):
    """Server hochfahren. Liefert (server, thread, port)."""
    if ThreadingHTTPServer is None:                     # pragma: no cover
        raise RuntimeError('http.server fehlt - Python 2?')
    Handler.wikis = wikis
    Handler.anfragen = []
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread, server.server_address[1]


def beenden(server):
    server.shutdown()
    server.server_close()


def anfragen():
    """Alles, was der Server bisher bekommen hat - als Kopie."""
    return list(Handler.anfragen or [])


def leeren():
    """Anfrageliste zuruecksetzen, damit ein Test allein geprueft wird."""
    if Handler.anfragen is not None:
        del Handler.anfragen[:]
