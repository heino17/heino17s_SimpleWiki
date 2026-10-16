"""Code und Formeln in der Leseansicht und in der Editor-Vorschau.

Teil 1 oeffnet eine Seite in der Leseansicht: der eingezaeunte Codeblock
traegt highlight.js-Farben, $$ ... $$ steht als Block, $ ... $ im Text.
Ein Preis wie "$5 und $10" bleibt Text - das einzelne $ gilt nur als
Formel, wenn kein Leerzeichen dahinter und keine Ziffer dahinter folgt.

Teil 2 oeffnet denselben Inhalt im Editor und schaltet auf Markdown um:
die Vorschau ist TOAST UIs eigene Anzeige und kennt beides nicht - die
App holt es ueber simplewikiVeredle nach (Ereignisse change/changeMode).

Teil 3 prueft den Round-Trip im WYSIWYG-Modus: Text mit Math oeffnen,
speichern, erneut oeffnen und speichern - die Formeln muessen erhalten
bleiben. Der Token-Trick stellt die Unvertraeglichkeit zwischen TOAST UI
und $$ ... $$ her.

Teil 4 prueft den Wechsel der Modi: im Markdown-Modus steht in der Quelle
die echte Formel (keine Marke), und der Weg Markdown -> WYSIWYG ->
Markdown beschaedigt sie nicht.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkcopy import build
from _hilfe import pruefe

INHALT = (
    "# Alpha\n\n"
    "```js\nconst x = 1;\n```\n\n"
    "$$a^2 + b^2 = c^2$$\n\n"
    "Text mit $e^{i\\pi}$ und $x_1$.\n\n"
    "Es kostet $5 und $10.\n"
)

INHALT3 = (
    "# Math\n\n"
    "$$\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$\n\n"
    "Inline $a_b^c$ und $x_0$.\n"
)

seiten = [
    {"id": "a", "title": "Alpha", "content": INHALT,
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

seiten3 = [
    {"id": "m", "title": "Math", "content": INHALT3,
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

KOPF = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function schluss() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function modus(name) { return all('.tab-item').filter(function (t) { return t.textContent.trim() === name; })[0]; }
      var schritte = [];
      function naechster() { var f = schritte.shift(); if (f) f(); }
      function spaeter(f) { schritte.push(f); setTimeout(naechster, 350); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""

teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        var bereich = q('.preview');
        ok(!!bereich, 'Leseansicht ist da');

        head('Codeblock bekommt Farben');
        ok(!!bereich.querySelector('pre code'), 'ein Codeblock ist da');
        ok(!!bereich.querySelector('pre code.hljs'), 'der Codeblock traegt die hljs-Klasse');
        ok(!!bereich.querySelector('.hljs-keyword'), 'Konstanten sind als Token gefaerbt');

        head('Formeln werden gesetzt');
        ok(!!bereich.querySelector('.sw-mathe .katex-display'), 'Blockformel steht als Block');
        ok(bereich.querySelectorAll('.sw-mathe-inline .katex').length === 2,
           'beide Formeln im Text gesetzt: ' + bereich.querySelectorAll('.sw-mathe-inline .katex').length);

        head('Ein Preis bleibt Text');
        var absaetze = all('.preview p');
        var preis = absaetze[absaetze.length - 1];
        ok((preis.textContent || '').trim() === 'Es kostet $5 und $10.',
           'der Preis steht woertlich: ' + JSON.stringify((preis.textContent || '').trim()));
        ok(preis.querySelectorAll('.katex').length === 0, 'im Preis steckt keine Formel');

        schluss();
      }, 2500);
    })();
    </script>
"""

teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Bearbeiten oeffnen, dann Markdown');
        knopf(/Bearbeiten/).click();
        spaeter(function () {
          ok(!!window.__ed, 'Testhaken am Editor');
          var tab = modus('Markdown');
          ok(!!tab, 'Umschalter Markdown ist da');
          if (!tab) { schluss(); return; }
          tab.click();
          spaeter(function () {
            var bereich = q('.toastui-editor-md-preview .toastui-editor-contents');
            ok(!!bereich, 'die Vorschau ist da');

            head('Code in der Vorschau bekommt Farben');
            ok(!!bereich.querySelector('pre code.hljs'), 'der Codeblock traegt die hljs-Klasse');
            ok(!!bereich.querySelector('.hljs-keyword'), 'Konstanten sind als Token gefaerbt');

            head('Formeln werden auch in der Vorschau gesetzt');
            ok(!!bereich.querySelector('.sw-mathe .katex-display'), 'Blockformel steht als Block');
            ok(bereich.querySelectorAll('.sw-mathe-inline .katex').length === 2,
               'beide Formeln im Text gesetzt: ' + bereich.querySelectorAll('.sw-mathe-inline .katex').length);

            head('Die Quelle zeigt im Markdown-Modus die echte Formel');
            var quelle = window.__ed.getMarkdown();
            ok(quelle.indexOf('@@MWS') < 0, 'keine Marke in der Quelle: ' + JSON.stringify(quelle));
            ok(quelle.indexOf('$$a^2 + b^2 = c^2$$') >= 0, 'Blockformel steht in der Quelle');
            ok(quelle.indexOf('$x_1$') >= 0, 'Inline-Formel steht in der Quelle');

            head('Ein Preis bleibt Text');
            var absaetze = all('.toastui-editor-md-preview .toastui-editor-contents p');
            var preis = absaetze[absaetze.length - 1];
            ok((preis.textContent || '').trim() === 'Es kostet $5 und $10.',
               'der Preis steht woertlich: ' + JSON.stringify((preis.textContent || '').trim()));
            ok(preis.querySelectorAll('.katex').length === 0, 'im Preis steckt keine Formel');

            schluss();
          });
        });
      }, 2500);
    })();
    </script>
"""

teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      var testId = 'm';
      setTimeout(function () {
        head('Round-Trip: Bearbeiten, Sichern, Neu oeffnen, Sichern');
        knopf(/Bearbeiten/).click();
        spaeter(function () {
          ok(!!window.__ed, 'Testhaken am Editor');
          var speichern1 = knopf(/Speichern/);
          ok(!!speichern1, 'Knopf Speichern vorhanden');
          if (!speichern1) { schluss(); return; }
          speichern1.click();
          spaeter(function () {
            ok(true, 'Erste Speicherung erfolgt');
            var seiten1 = window.__vm ? window.__vm.pages : [];
            var s1 = seiten1.filter(function (p) { return p.id === testId; })[0];
            ok(!!s1, 'Seite nach Speichern vorhanden');
            if (!s1) { schluss(); return; }
            var c1 = s1.content || '';
            ok(c1.indexOf('$$\\int_{0}^{\\infty}') >= 0, 'Blockformel nach erstem Speichern erhalten');
            ok(c1.indexOf('Inline $a_b^c') >= 0 || c1.indexOf('$a_b^c') >= 0, 'Inline-Formeln nach erstem Speichern erhalten');

            knopf(/Bearbeiten/).click();
            spaeter(function () {
              var speichern2 = knopf(/Speichern/);
              ok(!!speichern2, 'Zweite Speicherung moeglich');
              speichern2.click();
              spaeter(function () {
                var seiten2 = window.__vm ? window.__vm.pages : [];
                var s2 = seiten2.filter(function (p) { return p.id === testId; })[0];
                ok(!!s2, 'Seite nach zweitem Speichern vorhanden');
                if (!s2) { schluss(); return; }
                var c2 = s2.content || '';
                ok(c2 === c1, 'Inhalt nach zweitem Speichern unveraendert (Round-Trip)');
                ok(c2.indexOf('$$\\int_{0}^{\\infty}') >= 0, 'Blockformel bleibt erhalten');
                ok(c2.indexOf('$a_b^c') >= 0, 'Inline-Formel a_b^c bleibt erhalten');
                ok(c2.indexOf('$x_0') >= 0, 'Inline-Formel x_0 bleibt erhalten');

                schluss();
              });
            });
          });
        });
      }, 2500);
    })();
    </script>
"""

teil4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Wechsel Markdown -> WYSIWYG -> Markdown');
        knopf(/Bearbeiten/).click();
        spaeter(function () {
          var tab = modus('Markdown');
          ok(!!tab, 'Umschalter Markdown ist da');
          if (!tab) { schluss(); return; }
          tab.click();
          spaeter(function () {
            ok(window.__ed.getMarkdown().indexOf('$$a^2 + b^2 = c^2$$') >= 0,
               'im Markdown-Modus echte Formel in der Quelle');

            var wz = modus('WYSIWYG');
            ok(!!wz, 'Umschalter WYSIWYG ist da');
            if (!wz) { schluss(); return; }
            wz.click();
            spaeter(function () {
              var m = window.__ed.getMarkdown();
              ok(m.indexOf('\\\\') < 0, 'kein doppelter Backslash nach dem Weg: ' + JSON.stringify(m));
              ok(m.indexOf('x\\_') < 0, 'kein escapter Unterstrich nach dem Weg');
              ok(m.indexOf('@@MWS') >= 0, 'im WYSIWYG stehen wieder Marken');

              modus('Markdown').click();
              spaeter(function () {
                var q = window.__ed.getMarkdown();
                ok(q.indexOf('@@MWS') < 0, 'zurueck im Markdown-Modus ohne Marke');
                ok(q.indexOf('$$a^2 + b^2 = c^2$$') >= 0, 'Blockformel wieder echt');
                ok(q.indexOf('$x_1$') >= 0, 'Inline-Formel wieder echt');
                schluss();
              });
            });
          });
        });
      }, 2500);
    })();
    </script>
"""

pruefe(
    build('_mathe1.html', teil1, seiten, startpage='a'),
    build('_mathe2.html', teil2, seiten, startpage='a'),
    build('_mathe3.html', teil3, seiten3, startpage='m'),
    build('_mathe4.html', teil4, seiten, startpage='a'),
)
