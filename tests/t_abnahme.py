import sys, os, io, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
import mwsfixture
from mwsfixture import bauen
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

# ======================================================================
# Abnahme. Jede der fuenf Zeilen aus der Aufgabe bekommt hier eine
# Pruefung, die man nachlesen kann - und einen Namen, der sagt, welche.
#
#   1  grep auf externe Lade-Referenz ist leer
#   2  die Suite ist gruen (das macht tests/alle.py, nicht diese Datei)
#   3  die Datei oeffnet per Doppelklick ohne Netz und zeigt den
#      alten localStorage-Zustand
#   4  mit injiziertem Store erscheint der Inhalt in der Oberflaeche
#   5  eine Aenderung ist nach Neuladen wieder da
#
# Fuer Punkt 3 laeuft Chromium ohne Namensaufloesung: kann irgendein
# Name aufgeloest werden, kann auch nichts von aussen nachgeladen
# worden sein.
# ======================================================================

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OHNE_NETZ = ['--host-resolver-rules=MAP * ~NOTFOUND', '--disable-background-networking']

fehler_gesamt = 0
bestanden_gesamt = 0


def melde(name, treffer, moeglich):
    """Ein Abnahmepunkt mit seinem Namen."""
    global fehler_gesamt, bestanden_gesamt
    ok = treffer == moeglich
    bestanden_gesamt += 1
    if not ok:
        fehler_gesamt += 1
    print('%-4s %-46s %s' % ('OK' if ok else 'FAIL', name,
                             treffer if ok else '%s (erwartet: %s)' % (treffer, moeglich)))


# ---------------------------------------------------------------- 1
print('=== 1. grep auf externe Lade-Referenz ===')
quelle = io.open(os.path.join(PROJEKT, 'simplewiki.html'), encoding='utf-8').read()
lader = re.findall(r'<script[^>]*\ssrc=', quelle) + \
        re.findall(r'<link[^>]*rel=["\']?stylesheet', quelle, re.I) + \
        re.findall(r'@import', quelle)
melde('kein <script src>, kein <link stylesheet>, kein @import', len(lader), 0)

# Kein src= und kein href= zeigt nach draussen. Das ist die eigentliche
# Frage. Im Code der eingebetteten Bibliotheken stehen durchaus
# Adressen - Vues Fehlerverzeichnis, das marked-Repository, eine
# Analytics-Adresse von Toast UI. Sie stehen als Zeichenkette im
# Programm und werden nirgends geladen.
nach_draussen = re.findall(r'(?:src|href)\s*=\s*["\']?(https?://[^"\'\s>]+)', quelle)
melde('kein src= oder href= zeigt nach draussen', len(nach_draussen), 0)

# Und keine Datei wird ueber url() nachgeladen: alles ist data:.
# Nur die style-Bloecke ansehen - im JavaScript gibt es eine Methode
# namens url(), die nichts mit CSS zu tun hat.
styles = '\n'.join(re.findall(r'<style[^>]*>([\s\S]*?)</style>', quelle))
url_ohne_data = [u for u in re.findall(r'url\(\s*["\']?([^)"\']+)', styles)
                 if not u.strip().startswith('data:')]
melde('jedes url() im CSS zeigt auf data:', len(url_ohne_data), 0)
daten_bilder = len(re.findall(r'url\(\s*["\']?data:', quelle))
melde('Bilder stecken als data: drin', daten_bilder > 0, True)

# Nur zur Kenntnis, nicht als Pruefung: Adressen als Text im Code.
print('     (zur Kenntnis: %d Adressen als Zeichenkette im eingebetteten Code,'
      ' Hosts: %s)'
      % (len(re.findall(r'https?://', quelle)),
         ', '.join(sorted(set(re.findall(r'https?://([a-z.]+)/', quelle))))))
groesse = len(quelle.encode('utf-8'))
print('     Groesse der Datei: %d Bytes' % groesse)
print()

# ---------------------------------------------------------------- 3
def abnahme_durchgang(write):
    """Ein Testskript, das beim zweiten Durchlauf nach der Aenderung
    schaut. Der Durchgangszähler steht im sessionStorage, das einen
    Neuladen im selben Tab ueberlebt - localStorage waere hier falsch,
    weil die App dort ihre Seiten ablegt.

    Wichtig: beim Neuladen wird die Seite neu aufgebaut, der Bericht der
    ersten Runde waere weg. Deshalb kommt jede Zeile zusaetzlich ins
    sessionStorage und wird am Ende vorangestellt. Genau die Zeile, die
    man sonst nie zu sehen bekommt.
    """
    return (r"""
    <script>
    (function () {
      var log = [], fails = 0;
      var frueher = '';
      try { frueher = sessionStorage.getItem('__abnahme_log') || ''; } catch (e) {}
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out(text) {
        var p = document.getElementById('report');
        if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); }
        p.textContent = text === undefined ? log.join('\n') : text;
      }
      function merke(z) {
        log.push(z);
        try { sessionStorage.setItem('__abnahme_log', (sessionStorage.getItem('__abnahme_log') || '') + z + '\n'); } catch (e) {}
        out();
      }
      function ok(c, m) { if (!c) fails++; merke((c ? 'OK   ' : 'FAIL ') + m); }
      function kopf(m) { merke('--- ' + m); }
      function info(m) { merke('INFO ' + m); }
      function ende() {
        var alles = frueher + log.join('\n');
        var nf = (alles.match(/(^|\n)FAIL /g) || []).length;
        var no = (alles.match(/(^|\n)OK\s/g) || []).length;
        out(alles + '\n\n>>> ' + (nf ? nf + ' FEHLGESCHLAGEN' : 'ALLE ' + no + ' BESTANDEN'));
      }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        """ + write + r"""
      }, 2500);
    })();
    </script>
    """)


# --- 3: alter localStorage-Zustand gewinnt, ganz ohne Netz
ALTER_STAND = mkcopy._maskieren(json.dumps([
    {'id': 'alt1', 'title': 'Alter Stand', 'content': '# Alter Stand\n\nAus dem Browser.',
     'links': [], 'tags': [], 'created': '2026-01-01T10:00:00.000Z',
     'updated': '2026-01-01T10:00:00.000Z'},
    {'id': 'alt2', 'title': 'Zweite alt', 'content': '# Zweite alt',
     'links': [], 'tags': [], 'created': '2026-01-01T10:00:00.000Z',
     'updated': '2026-01-01T10:00:00.000Z'},
], ensure_ascii=False))
# Nur einmal saeen. Ein blinder Seed laeuft bei jedem Laden und macht
# den gerade gespeicherten Stand wieder rueckgaengig - das sieht dann
# aus wie ein Fehler im Programm und ist keiner.
VORAB_ALT = ('<script>try{if(!localStorage.getItem("__abnahme_gesaet")){'
             'localStorage.setItem("simplewiki_pages",' + ALTER_STAND + ');'
             'localStorage.setItem("simplewiki_startpage","alt1");'
             'localStorage.setItem("__abnahme_gesaet","1");}}catch(e){}</' + 'script>')

skript3 = abnahme_durchgang("""
        var schon = sessionStorage.getItem('__abnahme');
        kopf('Durchgang: ' + (schon ? 'zweiter' : 'erster'));
        if (schon === 'save') {
          kopf('Nach dem Neuladen');
          var stand = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]');
          info('Browser nach dem Neuladen: ' + stand.map(function (x) { return x.id + '=' + x.title; }).join('|'));
          ok(titel().indexOf('Umbenannt alt') >= 0,
             'die Aenderung ist wieder da: ' + titel().join('|'));
          var alt = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]');
          ok(alt.length === 2, 'und nichts dazu gekommen: ' + alt.length);
          ok(JSON.stringify(localStorage.getItem('simplewiki_startpage')) === '"alt1"',
             'die Startseite ist dieselbe');
          ende();
          return;
        }
        kopf('Der alte Stand im Browser');
        ok(titel().join('|') === 'Alter Stand|Zweite alt',
           'der Browser gewinnt vor dem Datei-Inhalt: ' + titel().join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alter Stand',
           'Startseite aus dem Browser');
        ok(q('.preview').textContent.indexOf('Aus dem Browser') >= 0, 'Inhalt aus dem Browser');
        kopf('Und jetzt aendern und neu laden');
        sessionStorage.setItem('__abnahme', 'save');
        knopf(/Bearbeiten|Edit/).click();
        setTimeout(function () {
          q('.title-editor').value = 'Umbenannt alt';
          q('.title-editor').dispatchEvent(new Event('input', { bubbles: true }));
          setTimeout(function () {
            knopf(/Speichern|Save/).click();
            setTimeout(function () {
              var d = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]');
              info('Browser direkt nach dem Speichern: ' + d.map(function (x) { return x.id + '=' + x.title; }).join('|'));
              info('Titel im Bild: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
              location.reload();
            }, 1200);
          }, 700);
        }, 2800);
""")

# Ohne Marker und mit altem Stand im Browser: die gewoehnliche Datei,
# per Doppelklick geoeffnet.
kopie3 = bauen('_abnahme_ohne_net.html', [], skript=skript3, vorab=VORAB_ALT,
               marker_keiner=True)

# --- 4: injizierter Store
TIDDLER = [
    {'title': 'i1', 'caption': 'Injizierte Seite',
     'text': '# Injizierte Seite\n\nDer Inhalt kam vom Server.',
     'tags': '[[abnahme]]', 'created': '20260203000000000',
     'modified': '20260203000000000', 'reihenfolge': '0000'},
    {'title': '$:/DefaultTiddlers', 'text': 'i1'},
]

skript4 = abnahme_durchgang("""
        var schon = sessionStorage.getItem('__abnahme');
        if (schon === 'save') {
          kopf('Nach dem Neuladen');
          ok(titel().indexOf('Injiziert umbenannt') >= 0,
             'der Server hat die Aenderung: ' + titel().join('|'));
          ende();
          return;
        }
        kopf('Mit injiziertem Store');
        ok(!!document.querySelector('script.tiddlywiki-tiddler-store'), 'der Marker ist im Dokument');
        ok(titel().join('|') === 'Injizierte Seite', 'die Seite steht in der Oberflaeche: ' + titel().join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Injizierte Seite',
           'und ist offen');
        ok(q('.preview').textContent.indexOf('Der Inhalt kam vom Server') >= 0, 'mit ihrem Inhalt');
        ok(!!q('.mws-hinweis'), 'und das Wiki weiss, dass es beim Server liegt');
        ok(localStorage.getItem('simplewiki_pages') === null, 'nichts steht im Browser');
        kopf('Und jetzt aendern und neu laden');
        sessionStorage.setItem('__abnahme', 'save');
        knopf(/Bearbeiten|Edit/).click();
        setTimeout(function () {
          q('.title-editor').value = 'Injiziert umbenannt';
          q('.title-editor').dispatchEvent(new Event('input', { bubbles: true }));
          setTimeout(function () {
            knopf(/Speichern|Save/).click();
            setTimeout(function () { location.reload(); }, 1500);
          }, 700);
        }, 2800);
""")

kopie4 = bauen('_abnahme_store.html', TIDDLER, skript=skript4)

# ---------------------------------------------------------------- Ausfuehren
print('=== 3. Doppelklick ohne Netz, mit altem localStorage ===')
text3 = bericht(dumpdom('_abnahme_ohne_net.html', budget=120000, zusatz=OHNE_NETZ))
print(text3.split('\n')[-1] if text3 else 'KEIN REPORT')
for z in text3.split('\n'):
    if True:
        print('    ' + z)
bestanden_gesamt += zahlen(text3)[0]
fehler_gesamt += zahlen(text3)[1]
print()

print('=== 4./5. Mit injiziertem Store, Aenderung uebersteht das Neuladen ===')
from mwsserver import Wiki, starten, beenden, anfragen
server, thread, port = starten({'abnahme': Wiki('abnahme', TIDDLER, skript=skript4)})
try:
    text4 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/abnahme/' % port, None, 120000))
finally:
    beenden(server)
print(text4.split('\n')[-1] if text4 else 'KEIN REPORT')
for z in text4.split('\n'):
    if True:
        print('    ' + z)
bestanden_gesamt += zahlen(text4)[0]
fehler_gesamt += zahlen(text4)[1]
gesendet = [a for a in anfragen() if a.get('op') == 'save']
print('    save-Aufrufe mit dem Aendernamen: %s'
      % (any('Injiziert umbenannt' in json.dumps(a['nutzlast'], ensure_ascii=False)
             for a in gesendet)))
print()

print('GESAMT: %d bestanden, %d fehlgeschlagen' % (bestanden_gesamt, fehler_gesamt))
sys.exit(1 if fehler_gesamt else 0)