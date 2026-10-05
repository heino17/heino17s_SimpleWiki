"""Die drei Panels rechts: zu ist zu, offen ist offen.

Das ist eine kleine Pruefung fuer eine kleine Zahl. Ein Panel parkte mit
`right: -360px` - einer Zahl im Stylesheet, die zur Breite des Panels
gehoerte, aber nicht mit ihr verbunden war. Unterhalb von 768 Pixeln macht
eine Media Query daraus 300 Pixel, und der Versatz bleibt 360. Auf einem
schmalen Fenster stand daraufhin ein Streifen der Panels im Bild, ohne
dass jemand sie geoeffnet haette - im Geraetemodus von Chrome war das zu
sehen.

Geparkt wird jetzt mit `translateX(100%)`, also mit dem eigenen Mass des
Panels. Das haengt an keiner Zahl mehr, und damit an keiner Breite.

Und hier ist der Grund fuer die Pruefung: die Massgabe lautet nicht
"das Panel ist nicht zu sehen" - das war auch vorher schon so. Sie
lautet "das Panel steht genau auf der Kante des Fensters", und genau
das gibt es erst mit dem neuen Weg. Diese Pruefung ist an dem alten
Gesetz fehlgeschlagen und an dem neuen gruen.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkcopy import build
from _hilfe import pruefe

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
]

script = r"""
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

var panels = ['.toc-panel', '.refs-panel', '.settings-panel'];
      /* Der Layout-Bereich, nicht die Fensterbreite. Ein Panel steht an
         'right: 0' am Rand des Layouts - und dort sitzt die Bildlaufleiste
         daneben, nicht darueber. window.innerWidth zaehlt den Balken mit
         und liegt deshalb um seine Breite daneben: 780 gegen 765. Beides
         ist richtig, man darf sie nur nicht verwechseln. */
      function kante() { return document.documentElement.clientWidth; }

      setTimeout(function () {
        head('Zu stehen die Panels genau auf der Fensterkante');
        panels.forEach(function (sel) {
          var e = q(sel), k = e.getBoundingClientRect();
          /* Genau auf der Kante - nicht 60 Pixel daneben. Das ist der
             Unterschied zwischen einem Weg, der zur eigenen Breite
             gehoert, und einer Zahl, die einmal gestimmt hat. */
          ok(Math.abs(k.left - kante()) <= 1,
             sel + ' steht auf der Kante: ' + Math.round(k.left) + ' von ' + kante());
          ok(e.classList.contains('side-panel'), sel + ' ist ein side-panel');
          ok(!e.classList.contains('open'), sel + ' ist zu');
        });
        ok(!q('.side-overlay').classList.contains('open'), 'und der Bildschirm ist nicht abgedunkelt');
        var letzte = all('.header button').pop().getBoundingClientRect();
        ok(letzte.right <= q('.header').getBoundingClientRect().right + 1,
           'der letzte Knopf im Kopf ragt nicht aus dem Fenster: ' + Math.round(letzte.right));

        head('Auf geht es');
        q('.menu-toggle').click();
        setTimeout(function () {
          ok(q('.toc-panel').classList.contains('open'), 'das Verzeichnis ist offen');
          /* Die Lage des Panels wird hier nicht gemessen: es faehrt
             300ms ein, und unter Virtual Time steht die Fahrung am
             Anfang. Dass 'offen' bei null landet, steht als Regel im
             Stylesheet und wird weiter unten nachgelesen - dort ist
             nichts in Bewegung. */
          ok(q('.side-overlay').classList.contains('open'), 'der Bildschirm ist abgedunkelt');

          head('Und wieder zu');
          q('.toc-panel .side-close').click();
          setTimeout(function () {
            ok(!q('.toc-panel').classList.contains('open'), 'zu');
            /* Und die anderen beiden stehen noch, wo sie sollten. */
            ['.refs-panel', '.settings-panel'].forEach(function (sel) {
              var k2 = q(sel).getBoundingClientRect();
              ok(Math.abs(k2.left - kante()) <= 1,
                 sel + ' steht wieder auf der Kante: ' + Math.round(k2.left) + ' von ' + kante());
            });
            ende();
          }, 900);
        }, 900);
      }, 1500);
    })();
    </script>
"""
kopie = build('_panels.html', script, seiten, startpage='a')

# Und die Regel selbst, im Stylesheet nachgelesen: der Weg, auf dem
# geparkt wird, muss die eigene Breite sein.
import re
quelle = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'simplewiki.html'), encoding='utf-8').read()
# Ohne Kommentare. In diesem Projekt steht die Begruendung ausgerechnet
# neben dem Code, und eine Regel, nach der geparkt wird, stehtwoertlich
# in der Erklaerung fuer das alte Parken. Wer nach 'right: -360px' sucht,
# findet es zuerst dort - und nicht im Stylesheet.
ohne_kommentare = re.sub(r'/\*[\s\S]*?\*/', '', quelle)
regel = ohne_kommentare[ohne_kommentare.index('.side-panel {'):ohne_kommentare.index('.side-header {')]
print('\n=== Womit geparkt wird ===')
bestanden = 0
fehler = 0


def merde(name, treffer, moeglich):
    global bestanden, fehler
    ok = treffer == moeglich
    bestanden += 1 if ok else 0
    fehler += 0 if ok else 1
    print('%-4s %-46s %s' % ('OK' if ok else 'FAIL', name,
                             treffer if ok else '%s (erwartet: %s)' % (treffer, moeglich)))


merde('mit dem eigenen Mass des Panels',
      bool(re.search(r'transform:\s*translateX\(100%\)', regel)), True)
merde('und nicht mit einer Zahl im Stylesheet',
      bool(re.search(r'right:\s*-\d+px', regel)), False)
merde('offen steht es bei null',
      bool(re.search(r'\.side-panel\.open\s*{[^}]*translateX\(0\)', regel)), True)
merde('und die Bewegung heisst transform',
      bool(re.search(r'transition:\s*transform', regel)), True)

pruefe(kopie, schon_fehler=fehler)
