"""Einruecken und Ausruecken im Editor - auch fuer normale Absaetze.

Toast UI bietet die beiden Knoepfe nur in Listen an, ausserhalb sind sie
grau. SimpleWiki ersetzt sie durch eigene: in einer Liste verschachteln
sie weiter wie bisher, ausserhalb machen sie aus dem Absatz ein Zitat
(Einruecken) und nehmen die Zitat-Ebene wieder weg (Ausruecken). Im
Markdown-Modus bleibt das eingebaute Verhalten (Leerzeichen vor der
Zeile). Teil 1 prueft den WYSIWYG-Modus, Teil 2 den Markdown-Modus -
jeweils ueber den echten Knopf in der Werkzeugleiste.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkcopy import build
from _hilfe import pruefe

INHALT = "Erste Zeile\n\n- Punkt eins\n- Punkt zwei\n"
# Teil 2 startet mit einer Liste: Der Markdown-Befehl rueckt nur
# Listenzeilen ein (sonst braeuchte er eine Nutzlast).
INHALT2 = "- Punkt eins\n- Punkt zwei\n"

seiten = [
    {"id": "a", "title": "Alpha", "content": INHALT,
     "links": [], "tags": [], "created": "x", "updated": "x"},
]
seiten2 = [
    {"id": "a", "title": "Alpha", "content": INHALT2,
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
      function einKnopf() { return q('.toastui-editor-toolbar-icons.indent'); }
      function ausKnopf() { return q('.toastui-editor-toolbar-icons.outdent'); }
      function md() { return window.__ed.getMarkdown(); }
      function platzieren(el) {
        var r = document.createRange(); r.selectNodeContents(el); r.collapse(true);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        ['mousedown', 'mouseup', 'click'].forEach(function (t) {
          try { el.dispatchEvent(new MouseEvent(t, { bubbles: true, cancelable: true })); } catch (e) {}
        });
        document.dispatchEvent(new Event('selectionchange'));
      }
      /* Nur der WYSIWYG-Bereich: der Markdown-Bereich traegt dieselbe
         Klasse und wuerde die Listenpunkte sonst doppelt zaehlen. */
      function ww(sel) { return all('.toastui-editor-ww-container .toastui-editor-contents ' + sel); }
      function modus(name) { return all('.tab-item').filter(function (t) { return t.textContent.trim() === name; })[0]; }
      var schritte = [];
      function naechster() { var f = schritte.shift(); if (f) f(); }
      function spaeter(f) { schritte.push(f); setTimeout(naechster, 350); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""

# ---------------------------------------------------------------- Teil 1
# WYSIWYG: Einruecken macht ein Zitat, Ausruecken nimmt es weg; in einer
# Liste verschachteln die Knoepfe weiter.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Bearbeiten oeffnen');
        knopf(/Bearbeiten/).click();
        spaeter(function () {
          ok(!!q('.md-host .toastui-editor-defaultUI'), 'Editor ist da');
          ok(!!window.__ed, 'Testhaken am Editor');
          ok(!!einKnopf(), 'Einruecken-Knopf ist da');
          ok(!!ausKnopf(), 'Ausruecken-Knopf ist da');
          ok(all('.toastui-editor-toolbar-icons.indent').length === 1, 'genau ein Einruecken-Knopf');
          ok(all('.toastui-editor-toolbar-icons.outdent').length === 1, 'genau ein Ausruecken-Knopf');
          ok(einKnopf().disabled === false, 'im Absatz ist Einruecken waehlbar');
          ok(einKnopf().getAttribute('aria-label') === 'Einrücken',
             'Beschriftung deutsch: ' + einKnopf().getAttribute('aria-label'));

          head('Ein Absatz wird eingerueckt - als Zitat');
          platzieren(ww('p')[0]);
          einKnopf().click();
          spaeter(function () {
            ok(/^> Erste Zeile/.test(md()), 'aus dem Absatz wurde ein Zitat: ' + JSON.stringify(md().split('\n')[0]));

            head('Ausruecken nimmt die Zitat-Ebene wieder weg');
            platzieren(ww('blockquote p')[0] || ww('p')[0]);
            ausKnopf().click();
            spaeter(function () {
              ok(/^Erste Zeile/.test(md()), 'der Absatz steht wieder vorn: ' + JSON.stringify(md().split('\n')[0]));

              head('In einer Liste bleibt die Verschachtelung');
              var li = ww('li');
              ok(li.length === 2, 'zwei Listenpunkte: ' + li.length);
              platzieren(li[1]);
              einKnopf().click();
              spaeter(function () {
                ok(/\n {2,}\* Punkt zwei/.test(md()), 'der zweite Punkt ist verschachtelt: ' + JSON.stringify(md()));
                platzieren(ww('li')[1]);
                ausKnopf().click();
                spaeter(function () {
                  ok(/\n\* Punkt zwei/.test(md()), 'wieder flach: ' + JSON.stringify(md()));
                  schluss();
                });
              });
            });
          });
        });
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 2
# Markdown: der Knopf wirkt und ist in der Befehlsliste angemeldet.
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
          tab.click();
          spaeter(function () {
            var cm = window.__ed.commandManager;
            ok(cm.getEditorType() === 'markdown', 'Editor ist im Markdown-Modus: ' + cm.getEditorType());
            ok(typeof cm.mdCommands.eingerueckt === 'function', 'Einruecken ist im Markdown-Modus angemeldet');
            ok(typeof cm.mdCommands.ausgerueckt === 'function', 'Ausruecken ist im Markdown-Modus angemeldet');
            var vorher = md();
            einKnopf().click();
            spaeter(function () {
              ok(md() !== vorher, 'der Knopf wirkt im Markdown-Modus: ' + JSON.stringify(vorher) + ' -> ' + JSON.stringify(md()));
              schluss();
            });
          });
        });
      }, 2500);
    })();
    </script>
"""

pruefe(
    build('_einrueck1.html', teil1, seiten, startpage='a'),
    build('_einrueck2.html', teil2, seiten2, startpage='a'),
)
