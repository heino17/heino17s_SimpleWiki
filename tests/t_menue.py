"""Das Inhaltsverzeichnis links als Menue.

Zwei Dinge werden hier geprueft, die vorher nicht da waren:

  - das Verzeichnis steht beim Oeffnen da und laesst sich am
    Faehnchen weg- und wieder zuklappen
  - im Verzeichnis gibt es kein Loeschkreuz mehr. Geloescht wird nur
    noch im Editor, wo man es gerade tut - im Verzeichnis stand der
    Knopf eine Zeile entfernt vom Loeschen einer ganzen Seite.

Zu den Positionen: gemessen wird nur dort, wo noch keine Bewegung
stattgefunden hat, also beim ersten Bild. Nach einem Klick waere eine
Messung der Mittellinie einer 300ms-Fahrt und damit dem Zufall
ueberlassen - siehe tests/README.md, "Teste die Aufgabe, nicht die
Umsetzung". Fuer die Wirkung des Zustands wird deshalb die Klasse
geprueft und fuer die Wirkung der Klasse die CSS-Regel selbst.
"""

import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkcopy import build
from _hilfe import pruefe

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": ["Beta"], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": ["Alpha"], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
script1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) { ok(false, 'unbehandelte Zusage: ' + e.reason); });

      setTimeout(function () {
        head('Das Verzeichnis steht da, ohne dass man es aufmacht');
        var m = q('.toc-menu');
        ok(!!m, 'Menue vorhanden');
        ok(!!m && m.classList.contains('offen'), 'und ist von Anfang an offen');
        var r = m ? m.getBoundingClientRect() : null;
        var kopf = q('.header').getBoundingClientRect();
        ok(r && Math.round(r.left) === 0, 'liegt am linken Rand: ' + (r ? Math.round(r.left) : '?'));
        ok(r && Math.round(r.height) > 400, 'und reicht ueber die ganze Hoehe: ' + (r ? Math.round(r.height) : '?'));
        ok(!!q('.side-overlay') && !q('.side-overlay').classList.contains('open'),
           'der Bildschirm ist nicht abgedunkelt - das ist ein Menue, kein Overlay');

        head('Die Kopfzeile bleibt frei');
        ok(r && Math.round(r.top) >= Math.round(kopf.bottom) - 1,
           'das Menue beginnt erst unter der Kopfzeile: ' + Math.round(r ? r.top : -1) + ' von ' + Math.round(kopf.bottom));
        var knopf = q('.search-box').getBoundingClientRect();
        ok(knopf.right <= kopf.right + 1 && knopf.top >= kopf.top - 1,
           'und das Suchfeld liegt sichtbar in der Kopfzeile');
        var reiter = q('.settings-toggle').getBoundingClientRect();
        ok(reiter.right <= kopf.right + 1, 'auch der letzte Knopf rechts: ' + Math.round(reiter.right) + ' von ' + Math.round(kopf.right));

        head('Der Inhalt rueckt zur Seite');
        var inhalt = q('.main-content').getBoundingClientRect();
        ok(Math.abs(inhalt.left - r.right) <= 2,
           'die Spalte haengt genau an der Innenkante des Menues: ' + Math.round(inhalt.left) + ' von ' + Math.round(r.right));
        ok(Math.round(q('.content-body').getBoundingClientRect().right) <= window.innerWidth + 1,
           'und reicht bis an den rechten Fensterrand - es ist nichts abgeschnitten');
        ok(getComputedStyle(q('.main-content')).overflow === 'hidden',
           'die Spalte ist breit genug und laesst nichts seitlich heraus');

        head('Darin steht die Liste');
        var zeilen = all('.toc-menu .toc-item-title');
        ok(zeilen.length === 2, 'beide Seiten: ' + zeilen.length);
        ok(zeilen.map(function (z) { return z.textContent.trim(); }).join('|') === 'Alpha|Beta',
           'in der Reihenfolge des Verzeichnisses: ' + zeilen.map(function (z) { return z.textContent.trim(); }).join('|'));
        ok(!!q('.toc-menu .toc-item-start'), 'mit Stern fuer die Startseite');
        ok(all('.toc-menu .toc-grip').length === 2, 'mit Griffen zum Ziehen');

        head('Kein Loeschkreuz im Verzeichnis');
        ok(all('.toc-item-delete').length === 0, 'im ganzen Verzeichnis keiner: ' + all('.toc-item-delete').length);
        ok(all('.toc-panel .toc-item-delete').length === 0, 'auch im Panel rechts keiner');

        head('Das Faehnchen');
        var f = q('.toc-faehnchen');
        ok(!!f, 'Faehnchen vorhanden');
        ok(!!f && f.getAttribute('aria-expanded') === 'true', 'und es sagt, dass offen ist');
        ok(!!f && /einklappen|collapse/i.test(f.getAttribute('title')),
           'mit einem Hinweis, der zum Zustand passt: ' + (f ? f.getAttribute('title') : '-'));
        var fr = f.getBoundingClientRect();
        ok(Math.abs(fr.left - r.right) <= 2,
           'es sitzt an der Innenkante des Menues: ' + Math.round(fr.left) + ' von ' + Math.round(r.right));
        ok(fr.top >= kopf.bottom - 1, 'und nicht in der Kopfzeile: ' + Math.round(fr.top));

        head('Zuklappen');
        f.click();
        setTimeout(function () {
          ok(!q('.toc-menu').classList.contains('offen'), 'Menue ist zu');
          ok(q('.toc-faehnchen').getAttribute('aria-expanded') === 'false', 'und das Faehnchen meldet es mit');
          ok(/ausklappen|expand/i.test(q('.toc-faehnchen').getAttribute('title')),
             'der Hinweis dreht mit: ' + q('.toc-faehnchen').getAttribute('title'));
          /* Breite und Position werden hier nicht gemessen: die Spalte
             faehrt 250ms, und unter Virtual Time laeuft die Uhr nicht
             mit. Was der Zustand bewirkt, steht in der CSS-Regel -
             weiter unten wird sie nachgelesen. */
          ok(all('.toc-item-title').length === 4,
             'die Liste ist noch im Dokument, nur die Spalte ist weg: ' + all('.toc-item-title').length);

          head('Wieder aufklappen');
          q('.toc-faehnchen').click();
          setTimeout(function () {
            ok(q('.toc-menu').classList.contains('offen'), 'Menue ist wieder da');
            ok(q('.toc-faehnchen').getAttribute('aria-expanded') === 'true', 'und das Faehnchen wieder zurueck');

            head('Eine Seite aus dem Menue oeffnen');
            all('.toc-menu .toc-item-title')[1].click();
            setTimeout(function () {
              ok(q('.content-title').textContent.trim() === 'Beta', 'Beta steht da: ' + q('.content-title').textContent.trim());
              ok(q('.toc-menu').classList.contains('offen'),
                 'und das Menue bleibt offen - ein Menue geht nicht zu, wenn man darin etwas waehlt');
              ok(all('.toc-menu .toc-item')[1].className.indexOf('active') >= 0, 'die Zeile ist markiert');
              ok(all('.toc-panel .toc-item')[1].className.indexOf('active') >= 0,
                 'im Panel rechts genauso - es ist dieselbe Seite');

              head('Geloescht wird nur noch im Editor');
              var bearbeiten = all('.footer .btn').filter(function (x) { return /Bearbeiten|Edit/.test(x.textContent); })[0];
              ok(!!bearbeiten, 'Bearbeiten steht in der Fussleiste');
              bearbeiten.click();
              setTimeout(function () {
                var loeschen = all('.footer .btn').filter(function (x) { return /öschen|Delete/.test(x.textContent); })[0];
                ok(!!loeschen, 'und dort steht das Loeschen - absichtlich, mit Bestaetigung');
                ok(all('.footer .btn').filter(function (x) { return /Abbrechen|Cancel/.test(x.textContent); })[0] !== undefined,
                   'daneben Abbrechen: es passiert nichts ohne Absicht');

                /* Die Taste bleibt in der Liste, in der man gedrueckt
                   hat. Beim ersten Bau des Menues war das nicht so: der
                   Fokus sprang nach einem Alt+Pfeil aus dem Panel in das
                   Menue, weil beide Zeilen im Dokument nebeneinander
                   lagen und die eine nicht wusste, zu welcher sie
                   gehoert. */
                head('Alt + Pfeil bleibt in seiner Liste');
                all('.toc-menu .toc-item')[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', altKey: true, bubbles: true, cancelable: true }));
                setTimeout(function () {
                  ok(q('.toc-menu').contains(document.activeElement),
                     'im Menue: ' + (document.activeElement ? document.activeElement.className : 'nichts'));
                  all('.toc-panel .toc-item')[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', altKey: true, bubbles: true, cancelable: true }));
                  setTimeout(function () {
                    ok(q('.toc-panel').contains(document.activeElement),
                       'im Panel rechts: ' + (document.activeElement ? document.activeElement.className : 'nichts'));
                    ok(all('.toc-menu .toc-item-title').map(function (z) { return z.textContent.trim(); }).join('|')
                       === all('.toc-panel .toc-item-title').map(function (z) { return z.textContent.trim(); }).join('|'),
                       'und beide Listen zeigen danach dasselbe: ' + all('.toc-panel .toc-item-title').map(function (z) { return z.textContent.trim(); }).join('|'));
                    ende();
                  }, 500);
                }, 500);
              }, 700);
            }, 700);
          }, 400);
        }, 400);
      }, 1500);
    })();
    </script>
"""
kopie1 = build('_menue1.html', script1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Scharfes Fenster: dort faengt das Verzeichnis zugeklappt an, weil es
# offen zu viel wegnehmen wuerde - und es laesst sich am Faehnchen
# aufklappen, ohne dass etwas verdeckt wird.
#
# ACHTUNG: gewollt sind 380 Pixel, gemessen werden 500. Headless nimmt
# kein Fenster unter 500. Siehe t_kopf.py und tests/README.md,
# "Headless nimmt kein Fenster unter 500 Pixeln".
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function ende() {
        var n = log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length;
        var f = log.filter(function (l) { return /^FAIL/.test(l); }).length;
        log.push(''); log.push('>>> ' + (f ? f + ' FEHLGESCHLAGEN' : 'ALLE ' + n + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        ok(window.innerWidth <= 560, 'Fenster ist schmal: ' + window.innerWidth +
           ' - und 500 ist das schmalste, was Headless zulässt (siehe oben)');

        head('Auf einem schmalen Fenster faengt es zu an');
        var m = q('.toc-menu');
        ok(!m.classList.contains('offen'), 'das Verzeichnis ist nicht offen');
        ok(q('.toc-faehnchen').getAttribute('aria-expanded') === 'false', 'und das Faehnchen sagt es');
        ok(/ausklappen|expand/i.test(q('.toc-faehnchen').getAttribute('title')),
           'mit dem richtigen Hinweis: ' + q('.toc-faehnchen').getAttribute('title'));
        /* Auf einem Fenster von 420 Pixeln waeren es 300 fuer das
           Verzeichnis und 120 fuer den Text. Hier sind es 500 und 500 -
           das Verzeichnis faengt aber aus demselben Grund zu, weil 500
           unter der Grenze von 640 liegt. */
        ok(m.getBoundingClientRect().width === 0, 'und die Spalte nimmt nichts: ' + m.getBoundingClientRect().width);
        ok(Math.round(q('.main-content').getBoundingClientRect().left) === 0,
           'der Text hat das ganze Fenster: ' + Math.round(q('.main-content').getBoundingClientRect().left));
        ok(Math.round(q('.toc-faehnchen').getBoundingClientRect().left) === 0, 'das Faehnchen sitzt am Rand');

        head('Und laesst sich aufklappen');
        q('.toc-faehnchen').click();
        setTimeout(function () {
          ok(m.classList.contains('offen'), 'jetzt ist es offen');
          var mr = m.getBoundingClientRect();
          var fr = q('.toc-faehnchen').getBoundingClientRect();
          var kr = q('.header').getBoundingClientRect();
          ok(Math.round(mr.width) === 300, 'es wurde schmaler als im weiten Fenster: ' + Math.round(mr.width) + 'px');
          ok(Math.round(q('.main-content').getBoundingClientRect().left) === Math.round(mr.right),
             'die Spalte haengt dran: ' + Math.round(q('.main-content').getBoundingClientRect().left));
          ok(Math.abs(fr.left - mr.right) <= 2, 'das Faehnchen ist mitgewandert: ' + Math.round(fr.left) + ' von ' + Math.round(mr.right));
          ok(Math.round(mr.top) >= Math.round(kr.bottom) - 1, 'und die Kopfzeile ist frei');
          ok(all('.toc-menu .toc-item-title').length === 2, 'die Liste ist vollstaendig');
          ok(!!q('.content-title'), 'und der Text steht trotzdem da: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
          ende();
        }, 900);
      }, 1500);
    })();
    </script>
"""
kopie2 = build('_menue2.html', script2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# Was der Zustand bewirkt, steht im Stylesheet. Das ist eine Frage an
# die Datei und keine an den Browser - und damit eine Antwort, die
# nicht davon abhaengt, ob eine Animation schon fertig ist.
print('\n=== Die Fahrtrichtung steht in der Datei ===')
quelle = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'simplewiki.html'), encoding='utf-8').read()
fehler_druck = 0
bestanden_druck = 0


def merde(name, treffer, moeglich):
    global fehler_druck, bestanden_druck
    ok = treffer == moeglich
    bestanden_druck += 1 if ok else 0
    fehler_druck += 0 if ok else 1
    print('%-4s %-52s %s' % ('OK' if ok else 'FAIL', name,
                             treffer if ok else '%s (erwartet: %s)' % (treffer, moeglich)))


menue = quelle[quelle.index('.toc-menu {'):quelle.index('.toc-menu-kopf {')]
koerper = quelle[quelle.index('.app-koerper {'):quelle.index('.app-spalte {')]
faehn = quelle[quelle.index('.toc-faehnchen {'):quelle.index('@media (max-width: 768px)')]

merde('zu ist die Spalte schmal und drueckt nichts beiseite',
      bool(re.search(r'\.toc-menu\s*{[^}]*width:\s*0', menue, re.S)), True)
merde('offen nimmt sie die Breite an',
      bool(re.search(r'\.toc-menu\.offen\s*{[^}]*width:\s*var\(\-\-toc-breite\)', menue)), True)
merde('sie schrumpft nie unter den Inhalt',
      bool(re.search(r'\.toc-menu\s*{[^}]*max-width:\s*85%', menue, re.S)), True)
merde('der Koerper ist eine Zeile',
      bool(re.search(r'\.app-koerper\s*{[^}]*display:\s*flex', koerper, re.S)), True)
merde('und gibt die uebrige Hoehe weiter',
      bool(re.search(r'\.app-koerper\s*{[^}]*min-height:\s*0', koerper, re.S)), True)
merde('das Faehnchen haengt an dieser Zeile',
      bool(re.search(r'\.app-koerper\s*{[^}]*position:\s*relative', koerper, re.S)), True)
merde('das Faehnchen sitzt an der Innenkante',
      bool(re.search(r'\.toc-faehnchen\.offen\s*{[^}]*left:\s*min\(var\(\-\-toc-breite\), 85%\)', faehn)), True)
merde('und sitzt zu am Fensterrand',
      bool(re.search(r'\.toc-faehnchen\s*{[^}]*left:\s*0', faehn, re.S)), True)

# Der Startzustand. Er haengt an einer Fenstermasse, nicht an einer
# Empfindung, und die steht an genau einer Stelle.
merde('die Grenze steht an einer Stelle',
      len(re.findall(r'const TOC_MENUE_OFFEN_BIS', quelle)), 1)
merde('und sie ist eine Fenstermasse',
      bool(re.search(r'const TOC_MENUE_OFFEN_BIS = \d+;', quelle)), True)
merde('der Start richtet sich danach',
      bool(re.search(r'tocMenuOffen:\s*window\.innerWidth > TOC_MENUE_OFFEN_BIS', quelle)), True)
merde('und es wird nirgends gemerkt',
      bool(re.search(r'simplewiki_\w*toc\w*', quelle)), False)

merde('im Druck ist das Menue weg',
      bool(re.search(r'@media print[\s\S]*?\.toc-menu,', quelle)), True)
merde('und das Faehnchen auch',
      bool(re.search(r'@media print[\s\S]*?\.toc-faehnchen,', quelle)), True)
merde('die Panels werden im Druck auch nicht gebraucht',
      bool(re.search(r'@media print[\s\S]*?\.side-panel,', quelle)), True)

pruefe(kopie1, kopie2, fenster={'_menue2.html': '380,700'},
       schon_fehler=fehler_druck)