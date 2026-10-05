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
        ok(!!m && m.classList.contains('side-panel'), 'es benutzt dieselbe Panel-Klasse wie rechts - und erbt damit die Druckregel');
        var r = m ? m.getBoundingClientRect() : null;
        ok(!!r && Math.round(r.left) === 0, 'liegt am linken Rand: ' + (r ? Math.round(r.left) : '?'));
        ok(!!r && r.height > 400, 'und reicht ueber die ganze Hoehe: ' + (r ? Math.round(r.height) : '?'));
        ok(!!q('.side-overlay') && !q('.side-overlay').classList.contains('open'),
           'der Bildschirm ist nicht abgedunkelt - das ist ein Menue, kein Overlay');

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
        var mr = m.getBoundingClientRect();
        ok(Math.abs(fr.left - mr.right) <= 2,
           'es sitzt an der Innenkante des Menues: ' + Math.round(fr.left) + ' von ' + Math.round(mr.right));
        ok(fr.top > 40 && fr.bottom < window.innerHeight - 40, 'und mittig am Rand: ' + Math.round(fr.top));

        head('Zuklappen');
        f.click();
        setTimeout(function () {
          ok(!q('.toc-menu').classList.contains('offen'), 'Menue ist zu');
          ok(q('.toc-faehnchen').getAttribute('aria-expanded') === 'false', 'und das Faehnchen meldet es mit');
          ok(/ausklappen|expand/i.test(q('.toc-faehnchen').getAttribute('title')),
             'der Hinweis dreht mit: ' + q('.toc-faehnchen').getAttribute('title'));
          ok(all('.toc-item-title').length === 4,
             'die Liste ist noch im Dokument, nur das Panel ist weg - sie ist Teil des Panels: ' + all('.toc-item-title').length);

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
                ende();
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
# Scharfes Fenster: das Menue wird schmaler, und das Faehnchen muss mit
# an die Innenkante wandern.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        ok(window.innerWidth <= 560, 'Fenster ist schmal: ' + window.innerWidth);
        var mr = q('.toc-menu').getBoundingClientRect();
        var fr = q('.toc-faehnchen').getBoundingClientRect();
        ok(mr.width < 360, 'das Menue ist schmaler geworden: ' + Math.round(mr.width) + 'px');
        ok(Math.abs(fr.left - mr.right) <= 2, 'das Faehnchen ist mitgewandert: ' + Math.round(fr.left) + ' von ' + Math.round(mr.right));
        ok(fr.right <= window.innerWidth, 'es ragt nicht aus dem Fenster: ' + Math.round(fr.right) + ' von ' + window.innerWidth);
        ok(all('.toc-menu .toc-item-title').length === 2, 'die Liste ist vollstaendig');
        var n = log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length;
        var f = log.filter(function (l) { return /^FAIL/.test(l); }).length;
        log.push('');
        log.push('>>> ' + (f ? f + ' FEHLGESCHLAGEN' : 'ALLE ' + n + ' BESTANDEN'));
        out();
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


menue = quelle[quelle.index('.toc-menu {'):quelle.index('.toc-faehnchen {')]
faehn = quelle[quelle.index('.toc-faehnchen {'):quelle.index('@media (max-width: 768px)')]

merde('zu liegt das Menue links neben dem Fenster',
      bool(re.search(r'\.toc-menu\s*{[^}]*left:\s*calc\(\-1 \* var\(\-\-toc-breite\)\)', menue, re.S)), True)
merde('offen liegt es bei null', bool(re.search(r'\.toc-menu\.offen\s*{[^}]*left:\s*0', menue)), True)
merde('es haelt sich nicht mehr an der rechten Kante',
      bool(re.search(r'\.toc-menu\s*{[^}]*right:\s*auto', menue, re.S)), True)
merde('das Faehnchen sitzt an der Innenkante',
      bool(re.search(r'\.toc-faehnchen\.offen\s*{[^}]*left:\s*min\(var\(--toc-breite\), 90vw\)', faehn)), True)
merde('im Druck ist das Faehnchen weg',
      bool(re.search(r'@media print[\s\S]*?\.toc-faehnchen,', quelle)), True)
merde('und das Menue mit, ueber .side-panel',
      bool(re.search(r'@media print[\s\S]*?\.side-panel,', quelle)), True)
merde('das Panel wird im Druck nicht gebraucht',
      'side-panel toc-menu' in quelle, True)

pruefe(kopie1, kopie2, fenster={'_menue2.html': '380,700'},
       schon_fehler=fehler_druck)