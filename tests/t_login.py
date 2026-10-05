"""Anmelden und abmelden.

MWS prueft ein Passwort mit OPAQUE: der Browser startet einen Handshake
und beweist damit, das Passwort zu kennen, ohne es zu schicken. Das
Programm dafuer liegt in einem TiddlyWiki-Plugin - und diese Wiki laedt
keine Plugins, sie holt ihre Seiten ueber /recipe. Die Anmeldung
gehoert deshalb dem Server: die Wiki schickt niemanden zu /login und
laesst sich dort anmelden. Nach der Anmeldung gilt die Sitzung fuer
alles, weil das Cookie dem ganzen Server gehoert.

Abmelden geht anders: es muss nichts beweisen, nur eine Sitzung
ungueltig machen. Dafuer braucht es kein Passwort und keine
Kryptografie - ein POST an /logout mit dem Kopf X-Requested-With: fetch
genuegt.

Geprueft wird:

  1) als Gast gibt es genau einen Weg zur Anmeldung: ein Link auf /login,
     ohne Passwortfeld in der Wiki
  2) nach der Anmeldung nennt der Kopf den Namen, die Schreibtasten
     sind zurueck
  3) nach dem Abmelden ist wieder alles weg - auch ohne Neuladen, und
     auch nach einem Neuladen
  4) ein Abmelden, das scheitert, sagt das und erfindet nichts
  5) im Browser gibt es keine Anmeldefunktion, weil es dort keinen
     Server gibt

Siehe sessions.ts in MWS fuer /login/1, /login/2 und /logout.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mwsserver import Wiki, starten, beenden, anfragen, leeren
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

try:
    from urllib.request import urlopen
except ImportError:                                     # pragma: no cover
    urlopen = None

# ------------------------------------------------------------------ Inhalt
ALPHA = {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nText.',
         'reihenfolge': '0000'}
BETA = {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta\n\nNur Inhalt.',
        'reihenfolge': '0001'}
STANDARD = {'title': '$:/DefaultTiddlers', 'text': 'Alpha'}
SEITEN = [ALPHA, BETA]

# Der Kopfteil, den jedes Skript unten braucht. Ohne ihn stuende in jedem
# Skript dieselbe Zeile, und beim naechsten Umbau waere nicht mehr zu
# sehen, was geprueft wird und was nur Hilfszeug ist.
#
# Bewusst ohne IIFE: die Skriptbloecke stecken einzeln im Dokument und
# kaemen so nicht aneinander.
KOPF = r"""
    <script>
    var log = [], fails = 0;
    function q(s) { return document.querySelector(s); }
    function all(s) { return [].slice.call(document.querySelectorAll(s)); }
    function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
    function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
    function fertig() {
      log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
      out();
    }
    function bearbeiten() { return all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0]; }
    function neueSeite() { return all('.new-page-btn').filter(function (b) { return /Neue Seite|New Page/.test(b.textContent); })[0]; }
    window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
    </script>
"""

# ------------------------------------------------------------------ Test 1
# Als Gast: "Nicht angemeldet" ist ein Knopf, und der fuehrt aus der Wiki
# heraus. Am Ende wird wirklich geklickt - der Lauf endet dann auf der
# Anmeldeseite des Servers, und der Beweis kommt aus dessen Protokoll.
gast = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Als Gast');
        var anzeige = q('.benutzer-anzeige');
        ok(!!anzeige, 'die Anzeige steht da: ' + (anzeige ? anzeige.textContent.trim() : 'KEINE'));
        ok(anzeige && /nicht angemeldet|Not logged in/i.test(anzeige.textContent),
           'und sagt, dass niemand angemeldet ist');
        ok(anzeige && anzeige.classList.contains('ist-anonym'), 'und als anonym markiert');
        ok(!q('.abmelden-btn'), 'es gibt nichts abzumelden');

        log.push('--- Und der Weg nach draussen');
        /* Ein Link, kein Knopf mit Rumpeln: die Anmeldung ist Sache des
           Servers, und ein Link bringt den ganzen Browser mit - mittlere
           Maustaste, Tab, Link im Statusfenster. */
        ok(anzeige && anzeige.tagName === 'A', 'die Anzeige ist ein Link: ' + (anzeige ? anzeige.tagName : '-'));
        ok(anzeige && anzeige.getAttribute('href') === '/login',
           'und er fuehrt zur Anmeldeseite des Servers: ' + (anzeige ? anzeige.getAttribute('href') : '-'));
        ok(anzeige && anzeige.title.length > 0, 'mit einem erklaerenden Text: ' + (anzeige ? anzeige.title : '-'));

        log.push('--- Die Wiki fragt kein Passwort ab');
        /* Das Passwort gehoert an den Server. Waere hier ein Passwortfeld,
           gaebe es zwei Orte fuer ein Geheimnis. */
        ok(all('input[type=password]').length === 0, 'kein Passwortfeld in der Wiki');
        fertig();
      }, 2500);
    })();
    </script>
    """

# ------------------------------------------------------------------ Test 2
# Nach der Anmeldung: der Name steht da, die Schreibtasten sind zurueck.
da = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Nach der Anmeldung');
        var anzeige = q('.benutzer-anzeige');
        ok(!!anzeige && /admin/.test(anzeige.textContent), 'der Kopf nennt den Namen: ' + (anzeige ? anzeige.textContent.trim() : 'KEINER'));
        ok(anzeige && !anzeige.classList.contains('ist-anonym'), 'und nicht mehr als anonym markiert');
        ok(anzeige && anzeige.tagName !== 'BUTTON', 'der Name ist eine Anzeige, kein Knopf');
        ok(!!q('.abmelden-btn'), 'und es gibt jetzt etwas abzumelden');
        ok(!!q('.abmelden-btn') && !q('.abmelden-btn').disabled, 'der Abmelde-Knopf ist frei');
        ok(!q('.nurlesen-hinweis'), 'kein Nur-Lesen-Hinweis mehr');
        ok(!!bearbeiten(), 'Bearbeiten ist zurueck');
        ok(!!neueSeite(), 'Neue Seite ist zurueck');
        fertig();
      }, 2500);
    })();
    </script>
    """

# ------------------------------------------------------------------ Test 3
# Abmelden: ohne Neuladen wieder Gast. Der Name muss verschwinden und die
# Schreibtasten mit ihm.
raus = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Vorher angemeldet');
        ok(!!q('.abmelden-btn'), 'es gibt einen Abmelde-Knopf');

        log.push('--- Abmelden');
        q('.abmelden-btn').click();
        setTimeout(function () {
          var anzeige = q('.benutzer-anzeige');
          ok(!!anzeige && /nicht angemeldet|Not logged in/i.test(anzeige.textContent),
             'der Kopf sagt wieder "nicht angemeldet": ' + (anzeige ? anzeige.textContent.trim() : 'KEINER'));
          ok(!!anzeige && !/\badmin\b/.test(anzeige.textContent), 'der Name ist weg');
          ok(!q('.abmelden-btn'), 'der Abmelde-Knopf ist weg');
          ok(!bearbeiten(), 'Bearbeiten ist weg');
          ok(!neueSeite(), 'Neue Seite ist weg');
          var hinweis = q('.nurlesen-hinweis');
          ok(!!hinweis && /nicht angemeldet|not logged in/i.test(hinweis.textContent),
             'der Hinweis nennt den Grund: ' + (hinweis ? hinweis.textContent.trim() : '-'));
          ok(!!q('.content-title'), 'die Seite laesst sich weiter lesen');
          ok(!!q('a.benutzer-anzeige[href="/login"]'), 'und der Weg zur Anmeldung ist wieder da');
          fertig();
        }, 2000);
      }, 2500);
    })();
    </script>
    """

# ------------------------------------------------------------------ Test 4
# Und dasselbe nach einem Neuladen: die Sitzung ist beim Server weg, nicht
# nur aus dem Bild. Ein Abmelden, das nur die Anzeige raeumt, faellt hier
# durch.
raus_neu = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Nach dem Neuladen');
        var anzeige = q('.benutzer-anzeige');
        ok(!!anzeige && /nicht angemeldet|Not logged in/i.test(anzeige.textContent),
           'weiterhin niemand angemeldet: ' + (anzeige ? anzeige.textContent.trim() : 'KEINER'));
        ok(!/\badmin\b/.test(document.body.innerText), 'der Name taucht nirgends mehr auf');
        ok(!q('.abmelden-btn'), 'nichts mehr abzumelden');
        ok(!bearbeiten(), 'Bearbeiten bleibt weg');
        fertig();
      }, 2500);
    })();
    </script>
    """

# ------------------------------------------------------------------ Test 5
# Ein Abmelden, das nicht klappt, wird gesagt. Vor allem darf es nicht
# aussehen, als waere man abgemeldet: die Sitzung besteht ja noch.
fehler = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Abmelden, aber der Server sagt 500');
        q('.abmelden-btn').click();
        setTimeout(function () {
          var anzeige = q('.benutzer-anzeige');
          ok(!!anzeige && /admin/.test(anzeige.textContent),
             'der Name bleibt stehen - man ist ja noch angemeldet: ' + (anzeige ? anzeige.textContent.trim() : 'KEINER'));
          ok(!!q('.abmelden-btn'), 'der Abmelde-Knopf bleibt da, es ist ja noch was abzumelden');
          ok(!q('.abmelden-btn').disabled, 'und ist wieder frei');
          ok(!!bearbeiten(), 'Bearbeiten bleibt moeglich - es wurde nichts abgelehnt');
          ok(!q('.nurlesen-hinweis'), 'und es gibt keinen erfundenen Nur-Lesen-Zustand');
          var hinweis = q('.hinweis');
          ok(!!hinweis && /abmelden/i.test(hinweis.textContent),
             'der Fehler steht als Hinweis da: ' + (hinweis ? hinweis.textContent.trim() : 'KEINER'));
          fertig();
        }, 2200);
      }, 2500);
    })();
    </script>
    """

# ------------------------------------------------------------------ Test 6
# Ohne Server gibt es niemanden, weder anzumelden noch abzumelden. Im
# Kopf steht dann gar nichts.
im_browser = KOPF + r"""
    <script>
    (function () {
      setTimeout(function () {
        log.push('--- Die Wiki als Datei im Browser');
        ok(!q('.benutzer-anzeige'), 'keine Namensanzeige');
        ok(!q('a.benutzer-anzeige'), 'kein Weg zum Anmelden - wohin auch?');
        ok(!document.querySelector('a[href="/login"]'), 'kein Link auf eine Anmeldeseite');
        ok(!q('.abmelden-btn'), 'kein Knopf zum Abmelden');
        ok(!q('.nurlesen-hinweis'), 'kein Rechtehinweis aus dem Nichts');
        ok(!!q('.content-title'), 'und die Seite laesst sich lesen');
        ok(!!bearbeiten(), 'Bearbeiten ist moeglich - hier gibt es niemanden, der es verbietet');
        fertig();
      }, 2500);
    })();
    </script>
    """


def zeige(name, text):
    """Einen Lauf ausgeben und die Zahlen liefern."""
    if not text:
        print('%-16s KEIN REPORT' % name)
        return 0, 1
    print('%-16s %s' % (name, text.split('\n')[-1]))
    for l in [l for l in text.split('\n') if l.startswith('FAIL')]:
        print('    ' + l)
    return zahlen(text)


def anmelden(basis):
    """Die Anmeldeseite des Testservers aufrufen.

    Kein Browser noetig: es geht nur darum, dass die Testfigur danach
    eine Sitzung hat - genau so, wie es nach dem Absenden des
    echten Formulars waere. Dass der Knopf der Wiki aber wirklich
    hinfuehrt, prueft der erste Lauf im Browser.
    """
    urlopen(basis + '/login').read()
    leeren()


print('=== Anmelden und abmelden gegen den Testserver ===')
ok = fail = 0

# --- Schritt 1: als Gast, mit dem Weg nach draussen ------------------
wiki = Wiki('gast', SEITEN + [STANDARD], titel='Gastwiki',
            status={'isLoggedIn': False, 'username': '(anon)',
                    'canUserWrite': False})
wiki.skript = gast
server, thread, port = starten({'gast': wiki})
basis = 'http://127.0.0.1:%d' % port
try:
    dom = dumpdom_url(basis + '/wiki/gast/', None, budget=120000)
    o, f = zeige('gast', bericht(dom))
    ok += o
    fail += f
finally:
    beenden(server)

# --- Schritt 2: zurueck im Browser, jetzt angemeldet ------------------
# Jeder Schritt bekommt einen eigenen Server: die Sitzung des ersten
# Laufs gehoert zum ersten Server. So haengt hier nichts an dort, und
# ein Fehler laesst sich einzeln zuordnen.
wiki = Wiki('da', SEITEN + [STANDARD], titel='Wiki der Angemeldeten',
            status={'isLoggedIn': False, 'username': '(anon)',
                    'canUserWrite': False})
server, thread, port = starten({'da': wiki})
basis = 'http://127.0.0.1:%d' % port
try:
    anmelden(basis)
    wiki.skript = da
    o, f = zeige('angemeldet', bericht(dumpdom_url(basis + '/wiki/da/', None,
                                                  budget=120000)))
    ok += o
    fail += f
finally:
    beenden(server)

# --- Schritt 3: abmelden, ohne Neuladen, dann mit ---------------------
wiki = Wiki('raus', SEITEN + [STANDARD], titel='Abmeldewiki',
            status={'isLoggedIn': False, 'username': '(anon)',
                    'canUserWrite': False})
server, thread, port = starten({'raus': wiki})
basis = 'http://127.0.0.1:%d' % port
try:
    anmelden(basis)
    wiki.skript = raus
    o, f = zeige('abgemeldet', bericht(dumpdom_url(basis + '/wiki/raus/', None,
                                                    budget=160000)))
    ok += o
    fail += f
    ruf = anfragen()
finally:
    beenden(server)

# Der POST ist der ganze Vertrag mit MWS: an /logout, mit dem Kopf, den
# der echte Server verlangt, und genau einmal - nicht auch noch einmal
# von einem zweiten Klick.
post = [a for a in ruf if a.get('weg') == 'POST' and a.get('pfad') == '/logout']
kopf = bool(post) and all(a.get('xhr') == 'fetch' for a in post)
if len(post) == 1 and kopf:
    print('%-16s OK   genau ein POST /logout, Kopf: fetch' % 'abschicken')
    ok += 1
else:
    print('%-16s FAIL %d POST(s) /logout, Kopf: %s'
          % ('abschicken', len(post), 'fetch' if kopf else 'fehlt'))
    fail += 1

# Und die Sitzung ist wirklich weg, nicht nur aus dem Bild. Derselbe
# Server, ein frischer Seitenaufruf.
wiki.skript = raus_neu
server, thread, port = starten({'raus': wiki})
basis = 'http://127.0.0.1:%d' % port
try:
    o, f = zeige('nach neuladen', bericht(dumpdom_url(basis + '/wiki/raus/', None,
                                                      budget=120000)))
    ok += o
    fail += f
finally:
    beenden(server)

# --- Schritt 4: ein Abmelden, das scheitert --------------------------
wiki = Wiki('fest', SEITEN + [STANDARD], titel='Feste Wiki',
            status={'isLoggedIn': False, 'username': '(anon)',
                    'canUserWrite': False})
server, thread, port = starten({'fest': wiki}, fehler={'logout': 500})
basis = 'http://127.0.0.1:%d' % port
try:
    anmelden(basis)
    wiki.skript = fehler
    o, f = zeige('abmelden geht nicht', bericht(dumpdom_url(basis + '/wiki/fest/',
                                                           None, budget=160000)))
    ok += o
    fail += f
finally:
    beenden(server)

# --- Schritt 5: die Datei im Browser ---------------------------------
mkcopy.build('_login_browser.html', im_browser, SEITEN, startpage='1')
o, f = zeige('im browser', bericht(dumpdom('_login_browser.html', budget=120000)))
ok += o
fail += f

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (ok, fail))
sys.exit(1 if fail else 0)