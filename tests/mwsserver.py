"""Ein MWS-Server als Testfigur.

Startet auf einem freien Port und liefert genau das, was der Vertrag
im Kopf von simplewiki.html verspricht:

  GET  /wiki/<name>/               simplewiki.html mit gesetztem Marker
  GET  /recipe/<name>/status       wer angemeldet ist und ob hier
                                   geschrieben werden darf
  PUT  /recipe/<name>/batch/<op>   list | read | save | delete
  PUT  /recipe/<name>/batch/<op>   bei /nurlesen/<name>/ stattdessen 403

  PUT, nicht POST: so ist es in RecipeRoutes.ts in MWS festgeschrieben
  (packages/mws/src/new-managers/RecipeRoutes.ts). Ein Testserver, der
  nur POST nimmt, bestaetigt genau das, was man ihm vorgegeben hat -
  und die App haette gegen die echte Route keinen Erfolg.

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
import mwsfixture                                         # noqa: E402

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(PROJEKT, 'simplewiki.html')


class Wiki:
    """Der Inhalt eines Wikis: Titel -> Felder."""

    def __init__(self, slug, tiddler, nurLesen=False, titel='Testwiki',
                 skript='', vorab='', store_leer=False, ersetzungen=None,
                 fehler=None, status=None, ablauf=False, status_aus=False):
        self.slug = slug
        self.nurLesen = nurLesen
        # Was /status antwortet. Ohne Vorgabe wird aus nurLesen abgeleitet
        # (angemeldet, aber kein Schreibrecht), damit die vorhandenen
        # Tests ihr Verhalten behalten und nur der neue Test den Fall
        # "nicht angemeldet" aufbaut:
        #   {'isLoggedIn': bool, 'username': str, 'canUserWrite': bool}
        self.status = dict(status) if status else None
        # Der Server bricht die Verbindung zu /status ab, statt zu
        # antworten. Ein Ausfall ist kein Rechteproblem - daran darf die
        # App nichts erfinden und nichts wegnehmen.
        self.status_aus = status_aus
        # Die Sitzung stirbt beim ersten Schreibversuch: der Server gibt
        # 403, und /status meldet danach "nicht angemeldet". So laesst
        # sich pruefen, was die App im laufenden Betrieb macht.
        self.ablauf = ablauf
        # Was die Testfigur in die ausgelieferte Seite einhaengt - so
        # wie mkcopy es fuer Dateikopien macht.
        self.skript = skript
        self.vorab = vorab
        # Ein Server, der keine Tiddler schickt: so sieht eine Seite aus,
        # die der Browser bedienen soll, obwohl sie vom Server kommt.
        self.store_leer = store_leer
        # Antworten, die der Server fuer einen Aufruf geben soll, statt
        # zu arbeiten: {'save': 500}. Damit laesst sich pruefen, was die
        # App tut, wenn es keinen Fehler ist, sondern einen Ausfall.
        self.fehler = dict(fehler or {})
        # Eingriffe in die Datei, bevor sie ausgeliefert wird - damit
        # kommen Testhaaken an dieselbe Stelle wie bei Dateikopien.
        self.ersetzungen = list(ersetzungen or [])
        self.tiddler = {}
        for t in tiddler:
            self.tiddler[t['title']] = dict(t)
        self.tiddler.setdefault('$:/SiteTitle', {'title': '$:/SiteTitle', 'text': titel})

    def alle(self):
        return [self.tiddler[k] for k in self.tiddler]

    def status_antwort(self):
        """Die Antwort von GET /recipe/<name>/status.

        So gebaut wie die echte Route in RecipeRoutes.ts: die Rechte
        stehen nicht oben, sondern pro Bag.
        """
        s = dict(self.status) if self.status is not None else {
            'isLoggedIn': True,
            'username': 'Testnutzer',
            'canUserWrite': not self.nurLesen,
        }
        schreiben = s.pop('canUserWrite', not self.nurLesen)
        s.setdefault('isAdmin', False)
        return {
            'user_id': None if not s['isLoggedIn'] else 1,
            'username': s['username'],
            'isAdmin': s['isAdmin'],
            'isLoggedIn': s['isLoggedIn'],
            'bags': [{'slug': self.slug, 'canUserWrite': schreiben}],
        }

    def ablauf_ausloesen(self):
        """Die Sitzung stirbt: ab jetzt 403 und 'nicht angemeldet'."""
        self.status = {'isLoggedIn': False, 'username': '(anon)',
                       'canUserWrite': False}
        self.nurLesen = True


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
        # Der Status gehoert zu diesem Aufruf, nicht zum letzten in der
        # Liste: zwei Anfragen koennen sich ueberholen, dann landet die
        # Antwort sonst bei der falschen.
        if getattr(self, 'eintrag', None) is not None:
            self.eintrag['antwort'] = code
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
            self.eintrag = None
            self.anfragen.append({'weg': 'GET', 'pfad': self.path})
            self._html(200, self._mit_store(self.wikis[m.group(1)]))
            return
        # Der Status steht in der Antwort, nicht im Request - deshalb ist
        # das ein GET ohne Koerper.
        m = re.match(r'^/recipe/([^/]+)/status$', self.path)
        if m:
            wiki = self.wikis.get(m.group(1))
            if wiki is None:
                self._json(404, {'error': 'not found'})
                return
            self.eintrag = None
            self.anfragen.append({'weg': 'GET', 'pfad': self.path,
                                  'xhr': self.headers.get('X-Requested-With')})
            if wiki.status_aus:
                # Keine Antwort, sondern ein Abbruch: das, was ein
                # abgestuerzter Server macht.
                self.close_connection = True
                return
            self._json(200, wiki.status_antwort())
            return
        self._json(404, {'error': 'not found'})

    # -------------------------------------------------------------- Schreiben
    def do_PUT(self):
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
        self.eintrag = {
            'weg': 'POST',
            'pfad': self.path,
            'op': op,
            'kopf': self.headers.get('X-Requested-With'),
            'nutzlast': koerper
        }
        self.anfragen.append(self.eintrag)

        # Der Kopf ist Pflicht. Ohne ihn ist es eine fremde Anfrage -
        # zum Beispiel ein Lesezugriff aus einem anderen Programm. Das
        # wird vor allem anderen geprueft, wie es der echte Server tut.
        if self.headers.get('X-Requested-With') != 'fetch':
            self._json(400, {'error': 'INVALID_X_REQUESTED_WITH'})
            return

        # Ein Ausfall, den der Test braucht.
        if op in wiki.fehler:
            self._json(wiki.fehler[op], {'error': 'SERVER_TEAPOT_' + op})
            return

        if wiki.nurLesen and op in ('save', 'delete'):
            self._json(403, {'error': 'BAG_NO_WRITE_PERMISSION'})
            return

        # Die Sitzung stirbt im Moment des Schreibens - das 403 und der
        # Status kommen aus demselben Augenblick.
        if wiki.ablauf and op in ('save', 'delete'):
            wiki.ablauf_ausloesen()
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
    def _mit_store(self, wiki):
        """simplewiki.html mit den Tiddlern vor dem Store-Punkt."""
        with io.open(QUELLE, encoding='utf-8') as fh:
            html = fh.read()
        inhalt = wiki.alle()
        for a, b in wiki.ersetzungen:
            html = html.replace(a, b)
        # Der Aufbau ist derselbe wie in der Datei-Fixture: erst die
        # Tiddler an den Punkt, dann die Testskripte. So gibt es nur eine
        # Stelle, die weiss, wie ein Server auszusehen hat.
        html = mwsfixture.einsetzen(html, [] if wiki.store_leer else inhalt)
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