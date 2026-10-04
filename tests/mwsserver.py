"""Ein MWS-Server als Testfigur.

Startet auf einem freien Port und liefert genau das, was der Vertrag
im Kopf von simplewiki.html verspricht:

  GET  /wiki/<name>/               simplewiki.html mit gesetztem Marker
  POST /recipe/<name>/batch/<op>   list | read | save | delete
  POST /recipe/<name>/batch/<op>   bei /nurlesen/<name>/ stattdessen 403

Der Server merkt sich jeden Aufruf in einer Liste (anfragen), damit die
Tests nachsehen koennen, ob die App wirklich die vereinbarten Wege geht:
mit dem Kopf X-Requested-With, mit den richtigen Feldern, und ohne den
Endpunkt fuer den Abgleich.

Das ist eine Testfigur, kein MWS: sie spricht nur die im Wiki
beschriebenen Punkte an.
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


class Wiki:
    """Der Inhalt eines Wikis: Titel -> Felder."""

    def __init__(self, slug, tiddler, nurLesen=False, titel='Testwiki',
                 skript='', vorab='', marker_leer=False, ersetzungen=None):
        self.slug = slug
        self.nurLesen = nurLesen
        # Was die Testfigur in die ausgelieferte Seite einhaengt - so
        # wie mkcopy es fuer Dateikopien macht.
        self.skript = skript
        self.vorab = vorab
        # Ein Marker ohne Inhalt: so sieht eine Seite aus, die der
        # Browser bedienen soll, obwohl sie vom Server kommt.
        self.marker_leer = marker_leer
        # Eingriffe in die Datei, bevor sie ausgeliefert wird - damit
        # kommen Testhaaken an dieselbe Stelle wie bei Dateikopien.
        self.ersetzungen = list(ersetzungen or [])
        self.tiddler = {}
        for t in tiddler:
            self.tiddler[t['title']] = dict(t)
        self.tiddler.setdefault('$:/SiteTitle', {'title': '$:/SiteTitle', 'text': titel})

    def alle(self):
        return [self.tiddler[k] for k in self.tiddler]


# ------------------------------------------------------------------ Server

class Handler(BaseHTTPRequestHandler):
    """Beantwortet die vier Aufrufe und sonst nichts."""

    # vom Test gesetzt
    wikis = {}
    anfragen = None

    def log_message(self, *args):
        """Nichts auf die Konsole - der Testlauf soll lesbar bleiben."""

    # ---------------------------------------------------------- Hilfsmittel
    def _json(self, code, daten):
        if self.anfragen:
            self.anfragen[-1]['antwort'] = code
        roh = json.dumps(daten, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def _html(self, code, text):
        roh = text.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def _koerper(self):
        laenge = int(self.headers.get('Content-Length') or 0)
        if not laenge:
            return {}
        roh = self.rfile.read(laenge).decode('utf-8')
        try:
            return json.loads(roh)
        except ValueError:
            return {}

    # -------------------------------------------------------------- Holen
    def do_GET(self):
        m = re.match(r'^/wiki/([^/]+)/$', self.path)
        if m and m.group(1) in self.wikis:
            self.anfragen.append({'weg': 'GET', 'pfad': self.path})
            self._html(200, self._mit_marker(self.wikis[m.group(1)]))
            return
        self._json(404, {'error': 'not found'})

    # -------------------------------------------------------------- Schreiben
    def do_POST(self):
        m = re.match(r'^/recipe/([^/]+)/batch/(\w+)$', self.path)
        if not m:
            self._json(404, {'error': 'not found'})
            return
        slug, op = m.group(1), m.group(2)
        wiki = self.wikis.get(slug)
        if wiki is None:
            self._json(404, {'error': 'not found'})
            return

        koerper = self._koerper()
        self.anfragen.append({
            'weg': 'POST',
            'pfad': self.path,
            'op': op,
            'kopf': self.headers.get('X-Requested-With'),
            'nutzlast': koerper
        })

        # Der Kopf ist Pflicht. Ohne ihn ist es eine fremde Anfrage -
        # zum Beispiel ein Lesezugriff aus einem anderen Programm.
        if self.headers.get('X-Requested-With') != 'fetch':
            self._json(400, {'error': 'MISSING_HEADER_X_REQUESTED_WITH'})
            return

        if wiki.nurLesen and op in ('save', 'delete'):
            self._json(403, {'error': 'BAG_NO_WRITE_PERMISSION'})
            return

        if op == 'list':
            self._json(200, wiki.alle())
        elif op == 'read':
            titel = koerper.get('titles') or []
            self._json(200, [wiki.tiddler[t] for t in titel if t in wiki.tiddler])
        elif op == 'save':
            for t in koerper.get('tiddlers') or []:
                if t.get('title'):
                    wiki.tiddler[t['title']] = dict(t)
            self._json(200, [{} for _ in (koerper.get('tiddlers') or [])])
        elif op == 'delete':
            for t in koerper.get('titles') or []:
                wiki.tiddler.pop(t, None)
            self._json(200, [{} for _ in (koerper.get('titles') or [])])
        else:
            self._json(400, {'error': 'unknown op'})

    # ------------------------------------------------------- Marker setzen
    def _mit_marker(self, wiki):
        """simplewiki.html mit dem Marker als erstes Element nach dem Kopf."""
        with io.open(QUELLE, encoding='utf-8') as fh:
            html = fh.read()
        inhalt = [] if wiki.marker_leer else wiki.alle()
        koerper = json.dumps(inhalt, ensure_ascii=False).replace('<', '\\u003c')
        marker = ('<script class="tiddlywiki-tiddler-store" '
                  'type="application/json">' + koerper + '</' + 'script>\n')
        # Die echte Head-Grenze suchen: im Dokument steht </head> auch
        # im Kommentar, und dort gehoert der Marker nicht hin.
        for a, b in wiki.ersetzungen:
            html = html.replace(a, b)
        head_at = mkcopy._echte_tags(html)[0]
        html = html[:head_at] + marker + html[head_at:]
        html = mkcopy.hauptskripte(html, pre=wiki.vorab, script=wiki.skript)
        return html


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
    """Alles, was der Server bisher bekommen hat - als Kopie.

    Eine Kopie, nicht die Liste selbst: leeren() raeumt die Liste auf, und
    ein Test, der sein Protokoll schon geholt hat, soll es behalten.
    """
    return list(Handler.anfragen or [])


def leeren():
    """Anfrageliste zuruecksetzen, damit ein Test allein geprueft wird."""
    if Handler.anfragen is not None:
        del Handler.anfragen[:]