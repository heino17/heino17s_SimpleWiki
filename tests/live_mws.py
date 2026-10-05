"""Live-Check gegen eine echte MWS-Instanz.

Kein Teil von alle.py, denn hier wird ein Server gestartet, und der
braucht ein gebautes dist/mws.js aus dem MWS-Quellbaum. Das ist die
einzige Pruefung, die das echte MWS und nicht die Testfigur aus
mwsserver.py sieht - die Testfigur kann sich namlich genau so
verhalten, wie man es fuer den Test braucht.

    python3 tests/live_mws.py                 # wikiwise-booklet
    python3 tests/live_mws.py mein-wiki
    MWS=/pfad/zum/mws python3 tests/live_mws.py

Ablauf: der Dev-Store wird nach tests/_kopien/live kopiert (der
Originalstore wird nur gelesen), die gebaute simplewiki.html wird in
die Kopie provisioniert, der Server auf einem freien Port gestartet,
die Wiki in Chromium geoeffnet und nachgesehen. Danach wird alles
wieder weggeraeumt - der Store, der Server und der Runner.

Geprueft wird der anonyme Besuch. Einen angemeldeten zu erzeugen
braucht ein Passwort, und die Anmeldung selbst ist noch nicht gebaut
(Schritt 2). Der Fall "angemeldet, aber kein Schreibrecht" und der
Fall "angemeldet und zustaendig" stehen deshalb in t_anmeldung.py.
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hilfe

HIN = os.path.dirname(os.path.abspath(__file__))
KOPIEN = os.path.join(HIN, '_kopien', 'live')

# Wo der MWS-Quellbaum liegt. Ueberschreiben mit MWS=..., falls er
# woanders liegt.
MWS = os.environ.get('MWS', '')
QUELLE = os.path.join(os.path.dirname(HIN), 'simplewiki.html')

log = []


def pruefe(bedingt, text):
    log.append(('OK   ' if bedingt else 'FAIL ') + text)


def fazit():
    print()
    for zeile in log:
        print(zeile)
    bestanden = sum(1 for z in log if z.startswith('OK'))
    print()
    print('>>> ' + ('ALLE %d BESTANDEN' % bestanden if bestanden == len(log)
                    else '%d FEHLGESCHLAGEN' % (len(log) - bestanden)))
    return 0 if bestanden == len(log) else 1


def freier_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def hole(url, kopf=None):
    anfrage = urllib.request.Request(url)
    for k, v in (kopf or {}).items():
        anfrage.add_header(k, v)
    try:
        with urllib.request.urlopen(anfrage, timeout=15) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')[:200]
    except Exception:
        return None, ''


def text_von(dom, klasse):
    """Der Text im Element mit dieser Klasse, ohne Tags."""
    m = re.search(r'<[a-z]+ class="[^"]*\b%s\b[^"]*"[^>]*>(.*?)</[a-z]+>' % klasse, dom, re.S)
    return re.sub(r'<[^>]+>', ' ', m.group(1)).split() if m else None


def main():
    wiki = sys.argv[1] if len(sys.argv) > 1 else 'wikiwise-booklet'
    mwsjs = os.path.join(MWS, 'dist', 'mws.js')
    if not os.path.exists(mwsjs):
        print('Kein dist/mws.js unter %s.' % MWS)
        print('Im MWS-Quellbaum "npm run build" laufen lassen, oder MWS=... setzen.')
        return 1
    if not os.path.exists(QUELLE):
        print('Keine simplewiki.html neben tests/.')
        return 1

    # ---- Kopie des Stores. Der Originalstore wird nur gelesen, und am
    # Ende ist die Kopie wieder weg - sie ist 200 MB groß.
    if os.path.isdir(KOPIEN):
        shutil.rmtree(KOPIEN)
    os.makedirs(KOPIEN)
    print('--- Store kopieren ...')
    for teil in ('store', 'tw5', 'passwords.key', 'package.json'):
        quelle = os.path.join(MWS, 'dev', 'wiki', teil)
        if not os.path.exists(quelle):
            print('Fehlt: %s' % quelle)
            return 1
        ziel = os.path.join(KOPIEN, teil)
        if os.path.isdir(quelle):
            shutil.copytree(quelle, ziel)
        else:
            shutil.copy2(quelle, ziel)

    port = freier_port()
    runner = os.path.join(KOPIEN, 'starten.mjs')
    with open(runner, 'w') as f:
        f.write('import runMWS from "%s";\n'
                'process.argv = [process.argv[0], process.argv[1], "listen",\n'
                '\t"--listener", "host=127.0.0.1", "port=%d"];\n'
                'runMWS().catch((e) => { console.error(e); process.exit(1); });\n'
                % (mwsjs, port))

    # ---- Die Schale in die Kopie provisionieren: erst dann liefert die
    # Wiki den neuen Code. Sonst prueft man die alte Schale und ist
    # sich nichts.
    print('--- Schale provisionieren ...')
    einrichten = os.path.join(KOPIEN, 'einrichten.mjs')
    with open(einrichten, 'w') as f:
        f.write('import runMWS from "%s";\n'
                'process.argv = [process.argv[0], process.argv[1],\n'
                '\t"provision-simplewiki", "%s"];\n'
                'runMWS().catch((e) => { console.error(e); process.exit(1); });\n'
                % (mwsjs, QUELLE))
    rc = subprocess.run(['node', einrichten], cwd=KOPIEN, capture_output=True)
    if rc.returncode:
        print('Provisionieren schlug fehl: %s' % rc.stderr.decode()[-400:])
        return 1

    server = subprocess.Popen(['node', runner], cwd=KOPIEN,
                              stdout=open(os.path.join(KOPIEN, 'server.log'), 'w'),
                              stderr=subprocess.STDOUT)
    try:
        basis = 'http://127.0.0.1:%d' % port
        for _ in range(120):
            time.sleep(1)
            if hole(basis + '/recipe/%s/status' % wiki)[0] == 200:
                break
        else:
            print('Der Server kam nicht hoch. Log:')
            print(open(os.path.join(KOPIEN, 'server.log')).read()[-1500:])
            return 1

        print('--- Die echten Routen von MWS ---')
        code, roh = hole(basis + '/recipe/%s/status' % wiki)
        pruefe(code == 200, 'GET /recipe/%s/status -> %s' % (wiki, code))
        try:
            status = json.loads(roh)
        except ValueError:
            status = {}
        pruefe(status.get('isLoggedIn') is False, 'isLoggedIn: %r' % status.get('isLoggedIn'))
        pruefe(status.get('username') == '(anon)',
               'username: %r (der Platzhalter des Servers)' % status.get('username'))
        beutel = (status.get('bags') or [{}])[0]
        pruefe(beutel.get('canUserWrite') is False,
               'canUserWrite: %r - der Server selbst verweigert das Schreiben'
               % beutel.get('canUserWrite'))

        print('--- Die Wiki-Seite ---')
        code, seite = hole(basis + '/wiki/%s' % wiki)
        pruefe(code == 200, 'GET /wiki/%s -> %s (%d Bytes)' % (wiki, code, len(seite)))
        # Der abschliessende Slash ist keine Alternative, sondern ein
        # 400. Das steht hier, damit ihn niemand "repariert".
        code_mit, _ = hole(basis + '/wiki/%s/' % wiki)
        pruefe(code_mit == 400, 'mit Slash: %s (die Route kennt kein Slash)' % code_mit)
        pruefe('MwsStore.prototype.status' in seite, 'die ausgelieferte Schale traegt den neuen Code')
        pruefe('$tw.preloadTiddler' in seite, 'der Speicher kommt als preloadTiddler')

        print('--- Der echte Browser ---')
        dom = _hilfe.dumpdom_url(basis + '/wiki/%s' % wiki, '1280,900', budget=25000)
        name = text_von(dom, 'benutzer-anzeige')
        hinweis = text_von(dom, 'nurlesen-hinweis')
        pruefe(bool(name), 'im Kopf steht eine Anzeige: %s' % (' '.join(name or []) or 'KEINE'))
        pruefe('class="benutzer-anzeige ist-anonym"' in dom,
               'sie ist als anonym markiert, nicht als angemeldet')
        pruefe(bool(name) and '(anon)' not in ' '.join(name),
               'der Platzhalter "(anon)" steht nirgends')
        pruefe(bool(hinweis), 'der Hinweis steht da')
        pruefe(bool(hinweis) and 'nicht angemeldet' in ' '.join(hinweis),
               'und nennt die Anmeldung: %s' % ' '.join(hinweis or [])[:90])
        knoepfe = re.findall(r'<button class="btn[^"]*"[^>]*>\s*([^<]+)', dom)
        pruefe(not knoepfe, 'keine Schreibknoepfe im Fuss: %s' % (knoepfe or 'keine'))
        pruefe('class="toc-item-delete"' not in dom, 'kein Loeschkreuz im Verzeichnis')
        pruefe('class="new-page-btn"' not in dom, 'kein Knopf "Neue Seite" im Verzeichnis')
        # Der Fluss-Knopf im Kopf traegt auch die Klasse new-page-btn -
        # er schreibt nichts und muss dastehen bleiben.
        pruefe('kopf-fluss' in dom, 'der Fluss-Knopf im Kopf ist da (er schreibt nichts)')
        pruefe(all(k in dom for k in ('menu-toggle', 'settings-toggle', 'theme-toggle')),
               'die Knöpfe zum Lesen und Einstellen sind da')
        titel = re.search(r'class="content-title"[^>]*>\s*([^<]*)', dom)
        pruefe(bool(titel) and titel.group(1).strip() != '',
               'die Seite laesst sich lesen: %s' % (titel.group(1).strip() if titel else 'keine'))
        pruefe(dom.count('toc-item-title') > 0,
               'das Verzeichnis zeigt %d Seiten' % dom.count('toc-item-title'))
    finally:
        server.terminate()
        try:
            server.wait(timeout=20)
        except Exception:
            server.kill()
        shutil.rmtree(KOPIEN, ignore_errors=True)

    return fazit()


if __name__ == '__main__':
    sys.exit(main())