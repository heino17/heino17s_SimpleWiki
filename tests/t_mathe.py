"""Code und Formeln in der Leseansicht und in der Editor-Vorschau.

Teil 1 oeffnet eine Seite in der Leseansicht: der eingezaeunte Codeblock
traegt highlight.js-Farben, $$ ... $$ steht als Block, $ ... $ im Text.
Ein Preis wie "$5 und $10" bleibt Text - das einzelne $ gilt nur als
Formel, wenn kein Leerzeichen dahinter und keine Ziffer dahinter folgt.

Teil 2 oeffnet denselben Inhalt im Editor und schaltet auf Markdown um:
die Vorschau ist TOAST UIs eigene Anzeige und kennt beides nicht - die
App holt es ueber simplewikiVeredle nach (Ereignisse change/changeMode).
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

seiten = [
    {"id": "a", "title": "Alpha", "content": INHALT,
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

# ---------------------------------------------------------------- Teil 1
# Leseansicht: Code, Blockformel, Formel im Text - und der Preis bleibt Text.
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

# ---------------------------------------------------------------- Teil 2
# Editor-Vorschau: Umschalten auf Markdown, dann muss veredelt sein.
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

pruefe(
    build('_mathe1.html', teil1, seiten, startpage='a'),
    build('_mathe2.html', teil2, seiten, startpage='a'),
)
