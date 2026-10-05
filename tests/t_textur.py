"""Die Textur kommt in beiden Modi an.

Ein Fehler, den nur das Ansehen findet und den kein Test von sich aus
sucht: die Punktttextur war im dunklen Modus unsichtbar, weil eine
CSS-Variable das Muster als Ganzes trug.

    --textur-bild: radial-gradient(var(--textur-inhalt) 1px, ...)

Eine Variable loest ihre Verweise dort auf, wo sie **deklariert** ist -
hier am :root, mit dem hellen Wert. Was die Elemente erben, ist schon
ein fertiger String mit hellen Farben. Im dunklen Modus stand die
Textur damit mit dunkler Tinte auf dunklem Grund.

Der Nutzer hat es gemerkt, weil er den Wert in `body.dark-mode`
geaendert hat und nichts passiert ist. Genau das steht hier jetzt als
Pruefung: **der Wert, der an `body` steht, muss in der fertigen
Farbe wiederzuerkennen sein.** In beiden Modi.

Und der Fallstrick steht als Kommentar in der Datei, weil er nicht
sieht aus, wenn man ihn nicht kennt.
"""

import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkcopy import build
from _hilfe import pruefe

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
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

      /* Die Farbe, die gerade gilt, als Zahl: 61,47,31 ist die Tinte
         des Hellen, 245,240,225 die des Dunklen. */
      function zahlen(text) { return (text.match(/[\d.]+/g) || []); }

      /* Nur die drei Farbkanaele. Die Deckkraft des Kopfes wird nicht
         verglichen: bei einem WIEDERHOLTEN Verlauf liest der Browser
         einen gemittelten Wert zurueck - 0.045 ergibt 0.043 - und das
         ist eine Eigenschaft der Anzeige, nicht der Absicht. Beim
         Punktraster ist der Fleck ein echter Stopp, dort wird die
         Deckkraft weiter unten genau verglichen. */
      function farbe(derName) {
        return zahlen(getComputedStyle(document.body).getPropertyValue(derName).trim()).slice(0, 3).join(',');
      }
      function gezeichnet(sel) {
        var bild = getComputedStyle(q(sel)).backgroundImage;
        var m = bild.match(/rgba?\(([^)]+)/);
        if (!m) return 'keine Farbe';
        return zahlen(m[1]).slice(0, 3).join(',');
      }
      function deckkraft(sel) {
        var m = getComputedStyle(q(sel)).backgroundImage.match(/rgba?\(([^)]+)/);
        return m ? (zahlen(m[1])[3] || '0') : '?';
      }
      function pruefeAlle(was) {
        ['.main-content', '.toc-menu', '.header'].forEach(function (sel) {
          var soll = sel === '.header' ? farbe('--textur-kopf') : farbe('--textur-inhalt');
          var ist = gezeichnet(sel);
          ok(soll === ist, was + ' ' + sel + ': gezeichnet wird ' + ist + ', gewuenscht war ' + soll);
        });
      }

      /* Der helle Wert wird VOR dem Umschalten notiert. Wer ihn danach
         holt, hat schon das Dunkel und vergleicht nichts mehr. */
      var hell = null;

      setTimeout(function () {
        head('Im hellen Modus');
        ok(document.body.classList.contains('dark-mode') === false, 'nicht dunkel');
        pruefeAlle('hell');
        hell = gezeichnet('.main-content');

        head('Im dunklen Modus');
        q('.theme-toggle').click();
        setTimeout(function () {
          ok(document.body.classList.contains('dark-mode'), 'dunkel geworden');
          pruefeAlle('dunkel');
          ok(hell !== gezeichnet('.main-content'),
             'und die Textur hat sich mitgedreht - vorher ' + hell + ', jetzt ' + gezeichnet('.main-content'));
          ok(/^245,240,225/.test(gezeichnet('.main-content')),
             'mit Licht statt mit Tinte: ' + gezeichnet('.main-content'));

          head('Die Deckkraft kommt an');
          /* Beim Punktraster ist der Fleck ein Stopp und nicht eine
             gemittelte Flaeche - hier wird sie genau gelesen. */
          ['.main-content', '.toc-menu'].forEach(function (sel) {
            var soll = (zahlen(getComputedStyle(document.body).getPropertyValue('--textur-inhalt').trim())[3]);
            ok(deckkraft(sel) === soll, sel + ': ' + deckkraft(sel) + ' statt ' + soll);
          });

          head('Das Raster ist ueberall gleich weit');
          var a = getComputedStyle(q('.main-content')).backgroundSize;
          var b = getComputedStyle(q('.toc-menu')).backgroundSize;
          ok(a === b && a !== 'auto', 'Text und Verzeichnis: ' + a + ' und ' + b);

          ende();
        }, 800);
      }, 2000);
    })();
    </script>
"""
kopie = build('_textur.html', script, seiten, startpage='a')

# Und die Falle selbst, nachgelesen in der Datei. Wer sie wieder einbaut,
# soll es wenigstens im Kommentar nachlesen koennen.
quelle = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'simplewiki.html'), encoding='utf-8').read()
print('\n=== Die Falle im Stylesheet ===')
fehler_d = 0
bestanden_d = 0


def merde(name, treffer, moeglich):
    global fehler_d, bestanden_d
    ok = treffer == moeglich
    bestanden_d += 1 if ok else 0
    fehler_d += 0 if ok else 1
    print('%-4s %-52s %s' % ('OK' if ok else 'FAIL', name,
                             treffer if ok else '%s (erwartet: %s)' % (treffer, moeglich)))


merde('keine Variable, die das Muster als Ganzes traegt',
      bool(re.search(r'--textur-bild', quelle)), False)
merde('die Farbe steht an beiden Benutzern direkt',
      len(re.findall(r'radial-gradient\(var\(--textur-inhalt\)', quelle)), 2)
merde('und die Schraffur ebenso',
      bool(re.search(r'var\(--textur-kopf\)', quelle)), True)
merde('die Farbe ist je Modus an genau einer Stelle ueberschrieben',
      len(re.findall(r'--textur-inhalt:', quelle)), 2)   # hell und dunkel

pruefe(kopie, schon_fehler=fehler_d)
