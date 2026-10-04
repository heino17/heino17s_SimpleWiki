import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

inhalt = """# Syntax

Siehe [[Einkaufsliste]] und [[Einkaufsliste]] noch einmal.

Mit eigenem Text: [[die Rezeptseite|Rezept (Kopie)]].

Ziel fehlt: [[Gibt es nicht]].

Sonderzeichen im Namen: [[*Bezeichnung*]].

Und so geht es auch: [Einkaufsliste](wiki:Einkaufsliste).

```
Beispiel:
[[Einkaufsliste]]
```

inline: `[[Einkaufsliste]]`
"""

pages = [
    {"id": "a", "title": "Syntax", "content": inhalt, "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Einkaufsliste", "content": "# Einkaufsliste", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "c", "title": "Rezept (Kopie)", "content": "# Rezept", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "d", "title": "*Bezeichnung*", "content": "# Bezeichnung", "links": [], "tags": [], "created": "x", "updated": "x"},
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
      function txt() { return q('.preview').textContent.replace(/\s+/g, ' '); }
        function txtOhneCode() {
          var k = q('.preview').cloneNode(true);
          [].slice.call(k.querySelectorAll('pre, code')).forEach(function (c) { c.parentNode.removeChild(c); });
          return k.textContent.replace(/\s+/g, ' ');
        }
        function zurueck(titel, dann) {
          q('.menu-toggle').click();
          setTimeout(function () {
            all('.toc-item-title').filter(function (t) { return t.textContent.trim() === titel; })[0].click();
            setTimeout(dann, 600);
          }, 600);
        }
      function zielVon(a) { return a.getAttribute('data-wiki-link'); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('[[Seite]]');
        var links = all('.preview a[data-wiki-link]');
        var ziele = links.map(zielVon);
        ok(links.length >= 5, 'Links im Text: ' + links.length);
        ok(ziele.indexOf('Einkaufsliste') >= 0, 'Ziel erkannt');
        ok(links[0].className.indexOf('wiki-link') >= 0 && links[0].className.indexOf('wiki-link-fehlt') < 0, 'vorhandenes Ziel ohne Fehlermarkierung');
        ok(links[0].textContent === 'Einkaufsliste', 'Beschriftung = Seitentitel: ' + links[0].textContent);
        ok(txtOhneCode().indexOf('[[') < 0, 'keine rauen Klammern mehr im Text (Code ausgenommen)');

        head('fehlendes Ziel');
        var fehlt = links.filter(function (a) { return zielVon(a) === 'Gibt es nicht'; })[0];
        ok(!!fehlt, 'Link auf nicht vorhandene Seite vorhanden');
        ok(!!fehlt && fehlt.className.indexOf('wiki-link-fehlt') >= 0, 'rot markiert');

        head('[[Text|Seite]]');
        var mitText = links.filter(function (a) { return zielVon(a) === 'Rezept (Kopie)'; })[0];
        ok(!!mitText, 'Ziel mit Leerzeichen und Klammern: ' + (mitText ? zielVon(mitText) : '-'));
        ok(!!mitText && mitText.textContent === 'die Rezeptseite', 'eigener Text wird angezeigt: ' + (mitText ? mitText.textContent : '-'));
        ok(!!mitText && mitText.className.indexOf('wiki-link-fehlt') < 0, 'Ziel existiert, also nicht rot');

        head('Sonderzeichen im Seitennamen');
        var sonder = links.filter(function (a) { return zielVon(a) === '*Bezeichnung*'; })[0];
        ok(!!sonder, 'Ziel mit * gefunden');
        ok(!!sonder && sonder.querySelector('em, strong') === null, 'Beschriftung bleibt Literaltext, keine Auszeichnung: ' + (sonder ? sonder.innerHTML : '-'));
        ok(!!sonder && sonder.textContent === '*Bezeichnung*', 'Beschriftung: ' + (sonder ? sonder.textContent : '-'));

        head('Code bleibt Code');
        var pre = q('.preview pre');
        ok(!!pre, 'Codeblock gerendert');
        ok(!!pre && pre.textContent.indexOf('[[Einkaufsliste]]') >= 0, 'im Codeblock unveraendert: ' + JSON.stringify(pre ? pre.textContent.replace(/\s+/g, ' ').trim() : ''));
        ok(!!pre && pre.querySelector('a') === null, 'kein Link im Codeblock');
        ok(txt().indexOf('inline: [[Einkaufsliste]]') >= 0, 'Inline-Code unveraendert');

        head('alte Markdown-Schreibweise');
        var md = links.filter(function (a) { return zielVon(a) === 'Einkaufsliste' && a.textContent === 'Einkaufsliste'; });
        ok(md.length >= 3, 'beide Schreibweisen funktionieren: ' + md.length + ' Links auf Einkaufsliste');

        head('Klick');
        links[0].click();
        setTimeout(function () {
          ok(q('.content-title').textContent.trim() === 'Einkaufsliste', 'Klick auf [[..]] folgt der Seite: ' + q('.content-title').textContent.trim());

          head('Klick auf [[Text|Seite]]');
          zurueck('Syntax', function () {
            var m2 = all('.preview a[data-wiki-link]').filter(function (a) { return a.textContent === 'die Rezeptseite'; })[0];
            ok(!!m2, 'Link wieder da');
            m2.click();
            setTimeout(function () {
              ok(q('.content-title').textContent.trim() === 'Rezept (Kopie)', 'folgt dem Ziel, nicht dem Text: ' + q('.content-title').textContent.trim());
              log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 500);
          });
        }, 500);
      }, 1200);
    })();
    </script>
"""

pruefe(
    build('_wikisyn.html', script, pages, startpage='a')
)
