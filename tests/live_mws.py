"""Live-Check gegen eine echte MWS-Instanz.

Kein Teil von alle.py, denn hier wird ein Server gestartet, und der
braucht ein gebautes dist/mws.js aus dem MWS-Quellbaum. Das ist die
einzige Pruefung, die das echte MWS und nicht die Testfigur aus
mwsserver.py sieht - die Testfigur kann sich namlich genau so
verhalten, wie man es fuer den Test braucht.

    python3 tests/live_mws.py                 # wikiwise-booklet
    python3 tests/live_mws.py mein-wiki
    MWS=/pfad/zum/mws python3 tests/live_mws.py

    MWS_USER=admin MWS_PASS=geheim python3 tests/live_mws.py

Ablauf: der Dev-Store wird nach tests/_kopien/live kopiert (der
Originalstore wird nur gelesen), die gebaute simplewiki.html wird in
die Kopie provisioniert, der Server auf einem freien Port gestartet,
die Wiki in Chromium geoeffnet und nachgesehen. Danach wird alles
wieder weggeraeumt - der Store, der Server und der Runner.

Geprueft wird der anonyme Besuch und - wenn MWS_USER und MWS_PASS
gesetzt sind - eine echte Anmeldung. Fuer die braucht es ein
Passwort, und ein Passwort gehoert in die Umgebung und nicht in
eine Datei. Ohne die beiden wird dieser Teil uebersprungen und
nicht als Fehler gezaehlt: der anonyme Lauf ist auch ohne
Passwort vollstaendig.

Die Anmeldung selbst macht die Wiki nicht: ihr Kopf verweist auf
/login, wo MWS das Passwort per OPAQUE prueft. Geprueft wird hier
deshalb das, was die Wiki wirklich tut - der Weg auf /login und die
zwei Aufrufe, die MwsStore.abmelden() macht.
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
import urllib.parse
import urllib.request

from urllib.parse import quote, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hilfe

HIN = os.path.dirname(os.path.abspath(__file__))
KOPIEN = os.path.join(HIN, '_kopien', 'live')

# Wo der MWS-Quellbaum liegt. Ueber die Umgebungsvariable MWS angeben,
# z. B.: MWS=/pfad/zum/mws python3 tests/live_mws.py
MWS = os.environ.get('MWS', '').rstrip('/')
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


# Der OPAQUE-Handshake mit dem echten Server, gesprochen mit genau der
# Bibliothek, die auch der MWS-Client benutzt. Als Text hier und nicht
# als Datei im Baum: sie gehoert nur zu diesem Lauf, und ein zusaetzlicher
# JavaScript-Einstieg in den Testordner waere eine zweite Sache, die man
# pflegen muss.
#
# Gesendet wird genau das, was die Wiki auch sendet: JSON, der Kopf
# X-Requested-With und das Sitzungs-Cookie. Kein Referer von Hand -
# den setzt ein Browser von selbst, und die Pruefung in RequestState.ts
# sieht ihn als freiwillig an.
OPAQUE_LAUF = r"""
const opaque = require(process.argv[2]);
const basis = process.argv[3];
const nutzer = process.argv[4];
const passwort = process.argv[5];
const wiki = process.argv[6];

const kopf = { "Content-Type": "application/json", "X-Requested-With": "fetch" };

(async () => {
  const r = {};
  try {
    await opaque.ready;
    const { clientLoginState, startLoginRequest } = opaque.client.startLogin({ password: passwort });
    const r1 = await fetch(basis + "/login/1", {
      method: "POST", headers: kopf,
      body: JSON.stringify({ username: nutzer, startLoginRequest }),
    });
    r.login1 = r1.status;
    if (r1.status === 200) {
      const { loginResponse, loginSession } = await r1.json();
      const fertig = opaque.client.finishLogin({ clientLoginState, loginResponse, password: passwort });
      r.finishLogin = !!fertig;
      const r2 = await fetch(basis + "/login/2", {
        method: "POST", headers: kopf,
        body: JSON.stringify({ finishLoginRequest: fertig.finishLoginRequest, loginSession }),
      });
      r.login2 = r2.status;
      const setc = r2.headers.getSetCookie ? r2.headers.getSetCookie() : [];
      r.cookie = (setc || []).map(c => c.split(";")[0]).join("; ");
      r.cookieNamen = (setc || []).map(c => c.split("=")[0].trim());
    }
    if (r.cookie) {
      const mit = { "X-Requested-With": "fetch", Cookie: r.cookie };
      const rs = await fetch(basis + "/recipe/" + wiki + "/status", { headers: mit });
      r.statusAntwort = rs.status;
      r.status = await rs.json();
      // Abmelden, genau wie die Wiki es macht.
      const rl = await fetch(basis + "/logout", { method: "POST", headers: mit });
      r.logout = rl.status;
      const rs2 = await fetch(basis + "/recipe/" + wiki + "/status", { headers: mit });
      r.statusNachher = (await rs2.json()).isLoggedIn;
    }
  } catch (e) {
    r.fehler = String((e && e.message) || e);
  }
  process.stdout.write(JSON.stringify(r));
})();
"""


def main():
    wiki = sys.argv[1] if len(sys.argv) > 1 else 'wikiwise-booklet'
    if not MWS:
        print('Bitte den Quellbaum des MWS ueber MWS=... angeben:')
        print('  MWS=/pfad/zum/mws python3 tests/live_mws.py')
        return 1
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
        anzeige_tag = re.search(r'<(?:a|span) class="[^"]*benutzer-anzeige[^"]*"[^>]*>', dom)
        pruefe(bool(anzeige_tag) and 'ist-anonym' in anzeige_tag.group(0),
               'sie ist als anonym markiert, nicht als angemeldet')
        pruefe(bool(anzeige_tag) and 'href="/login?redirect=' in anzeige_tag.group(0),
               'und fuehrt als Link zur Anmeldeseite des Servers: %s'
               % (anzeige_tag.group(0)[:70] if anzeige_tag else 'kein Tag'))
        # Der Zusatz muss auf genau diese Wiki zeigen, sonst landet man
        # nach dem Anmelden im falschen Wiki. Im Attribut stehen die
        # Schraegstriche kodiert (%2F), deshalb wird hier decodiert.
        pruefe('/wiki/%s' % wiki in unquote(anzeige_tag.group(0)
                                           if anzeige_tag else ''),
               'und der Rueckweg zeigt auf diese Wiki: /wiki/%s' % wiki)
        pruefe(bool(name) and '(anon)' not in ' '.join(name),
               'der Platzhalter "(anon)" steht nirgends')
        pruefe(bool(hinweis), 'der Hinweis steht da')
        pruefe(bool(hinweis) and 'nicht angemeldet' in ' '.join(hinweis),
               'und nennt die Anmeldung: %s' % ' '.join(hinweis or [])[:90])
        knoepfe = re.findall(r'<button class="btn[^"]*"[^>]*>\s*([^<]+)', dom)
        pruefe(not knoepfe, 'keine Schreibknoepfe im Fuss: %s' % (knoepfe or 'keine'))
        pruefe('class="toc-item-delete"' not in dom, 'kein Loeschkreuz im Verzeichnis')
        # "Neue Seite" steht im Kopf, nicht im Verzeichnis - und eine
        # Nur-Lesen-Wiki zeigt ihn gar nicht. Gesucht wird nach .kopf-neu
        # und nicht nach dem Text: der Knopf traegt ein Zeichen.
        pruefe('kopf-neu' not in dom, 'kein Knopf "Neue Seite" im Kopf')
        # Der Fluss-Knopf im Kopf traegt auch die Klasse new-page-btn -
        # er schreibt nichts und muss dastehen bleiben.
        pruefe('kopf-fluss' in dom, 'der Fluss-Knopf im Kopf ist da (er schreibt nichts)')
        pruefe(all(k in dom for k in ('search-box', 'settings-toggle', 'theme-toggle')),
               'Suchfeld und die Knöpfe zum Einstellen sind da')
        pruefe('menu-toggle' not in dom,
               'der Knopf für das Inhaltsverzeichnis ist weg - es ist eine Spalte')
        titel = re.search(r'class="content-title"[^>]*>\s*([^<]*)', dom)
        pruefe(bool(titel) and titel.group(1).strip() != '',
               'die Seite laesst sich lesen: %s' % (titel.group(1).strip() if titel else 'keine'))
        pruefe(dom.count('toc-item-title') > 0,
               'das Verzeichnis zeigt %d Seiten' % dom.count('toc-item-title'))

        # ---- Wo der Link im Kopf hingeht
        print('--- Der Weg zur Anmeldung')
        code, loginseite = hole(basis + '/login')
        pruefe(code == 200, 'GET /login -> %s (%d Bytes)'
               % (code, len(loginseite)))
        # Die Seite ist eine TiddlyWiki-Seite: das Formular entsteht erst
        # im Browser. Im HTML des Servers steht davon nichts - wer nur den
        # Rohtext liest, wuerde den ganzen Aufbau fuer nichtig halten.
        login_dom = _hilfe.dumpdom_url(basis + '/login', '1280,900', budget=25000)
        pruefe('login-password' in login_dom or 'type="password"' in login_dom,
               'und der Browser zeigt ein Passwortfeld')
        pruefe('login-username' in login_dom, 'sowie ein Feld fuer den Benutzernamen')
        pruefe('/login' in seite,
               'die ausgelieferte Schale zeigt auf /login')

        # Der Link aus dem Kopf traegt den Rueckweg in diese Wiki mit. Ob
        # der Server danach wirklich dorthin weiterleitet, entscheidet der
        # Browser erst nach dem Absenden des Formulars - das kann hier
        # niemand nachstellen, ohne ein Passwort einzutippen. Pruefbar
        # bleibt, dass der Server den Link mit dem Parameter ueberhaupt
        # ausliefert und nicht etwa mit einer Fehlermeldung antwortet.
        print('--- Der Weg zur Anmeldung, mit Rueckweg')
        tief = '/login?redirect=' + quote('/wiki/' + wiki, safe='')
        code, tief_dom = hole(basis + tief)
        pruefe(code == 200, 'GET %s -> %s' % (tief, code))
        pruefe('login-username' in _hilfe.dumpdom_url(basis + tief, '1280,900',
                                                      budget=25000)
               or 'login-username' in tief_dom,
               'und die Seite ist weiterhin das Anmeldeformular')

        # ---- Die Anmeldung selbst, wenn ein Passwort da ist
        passwort = os.environ.get('MWS_PASS')
        nutzer = os.environ.get('MWS_USER', 'admin')
        if not passwort:
            print('--- Anmeldung: uebersprungen (MWS_PASS nicht gesetzt)')
        else:
            print('--- Die echte Anmeldung als %s' % nutzer)
            # .cjs, nicht .mjs: der Lauf benutzt require fuer die
            # OPAQUE-Bibliothek, und require gibt es nur im CommonJS.
            helfer = os.path.join(KOPIEN, 'anmelden.cjs')
            with open(helfer, 'w') as f:
                f.write(OPAQUE_LAUF)
            befund = subprocess.run(
                ['node', helfer,
                 os.path.join(MWS, 'plugins', 'client', 'tiddlers', 'library', 'opaque.js'),
                 basis, nutzer, passwort, wiki],
                capture_output=True)
            roh = befund.stdout.decode('utf-8', 'replace').strip()
            try:
                r = json.loads(roh)
            except ValueError:
                r = {'fehler': (roh or befund.stderr.decode('utf-8', 'replace'))[-400:]}
            if r.get('fehler'):
                pruefe(False, 'die Anmeldung lief durch: %s' % r['fehler'])
            else:
                pruefe(r.get('login1') == 200, 'POST /login/1 -> %s' % r.get('login1'))
                pruefe(r.get('finishLogin') is True, 'der Handshake ging auf')
                pruefe(r.get('login2') == 200, 'POST /login/2 -> %s' % r.get('login2'))
                pruefe('session' in (r.get('cookieNamen') or []),
                       'und es kam ein Sitzungs-Cookie: %s'
                       % ', '.join(r.get('cookieNamen') or []) or 'keins')
                angemeldet = r.get('status') or {}
                pruefe(angemeldet.get('isLoggedIn') is True,
                       'der Server erkennt die Sitzung: isLoggedIn=%r'
                       % angemeldet.get('isLoggedIn'))
                pruefe(angemeldet.get('username') == nutzer,
                       'und nennt %r: %r' % (nutzer, angemeldet.get('username')))
                beutel = (angemeldet.get('bags') or [{}])[0]
                pruefe(beutel.get('canUserWrite') is True,
                       'und darf in diesem Wiki schreiben: %r'
                       % beutel.get('canUserWrite'))

                # Genau der Aufruf, den MwsStore.abmelden() macht.
                pruefe(r.get('logout') in (200, 204),
                       'POST /logout mit dem Kopf X-Requested-With -> %s'
                       % r.get('logout'))
                pruefe(r.get('statusNachher') is False,
                       'danach wieder niemand angemeldet: %r'
                       % r.get('statusNachher'))
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