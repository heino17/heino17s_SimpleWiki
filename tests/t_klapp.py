import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

# Verzeichnis auf- und zuklappen: eine Elternseite kann ihre Unter-Seiten
# hinter einem Zaehler verbergen. Das ist ein Anzeige-Ding dieser Ansicht,
# kein Feld der Seite und kein Teil des Austauschformats - und es gilt
# ab dem Neuladen wieder der Ausgangszustand: zugeklappt. Gemerkt wird
# also nichts, schon gar nichts in localStorage.
pages = [
    {"id": "1", "title": "Haupt", "content": "# Haupt", "links": [], "tags": [], "created": "x", "updated": "x", "eltern": ""},
    {"id": "2", "title": "Unter1", "content": "# Unter1", "links": [], "tags": [], "created": "x", "updated": "x", "eltern": "Haupt"},
    {"id": "3", "title": "Unter2", "content": "# Unter2", "links": [], "tags": [], "created": "x", "updated": "x", "eltern": "Unter1"},
    {"id": "4", "title": "Andere", "content": "# Andere", "links": [], "tags": [], "created": "x", "updated": "x", "eltern": ""},
    {"id": "5", "title": "Zweig", "content": "# Zweig", "links": [], "tags": [], "created": "x", "updated": "x", "eltern": ""},
]

schablone = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function zeile(i) { return all('.toc-menu .toc-item')[i]; }
      function klappen() { return all('.toc-menu .toc-klappen'); }
      function sichtbar(el) { return !!el && getComputedStyle(el).display !== 'none'; }
      function nichtsGemerkt() { return localStorage.getItem('simplewiki_zugeklappt') === null; }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function taste(key, alt) {
        return new KeyboardEvent('keydown', { key: key, altKey: !!alt, bubbles: true, cancelable: true });
      }
      /* Benoetigte Syntaxteile - vom Aufrufer eingefuegt. */
      __INHALT__
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
    })();
    </script>
"""

# --- Teil 1: ab dem Start ist jede Elternseite zugeklappt -----------------
teil1 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Nach dem Laden: Haupt ist zugeklappt');
          ok(sichtbar(zeile(0)) && !sichtbar(zeile(1)) && !sichtbar(zeile(2)),
             'nur die oberste Ebene steht da: ' +
             all('.toc-menu .toc-item').map(function (_, i) { return sichtbar(zeile(i)) ? titel()[i] : '(' + titel()[i] + ')'; }).join('|'));
          ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig',
             'verdeckt ist nur die Anzeige, versetzt ist nichts: ' + titel().join('|'));
          ok(klappen().length === 2, 'zwei Zaehler (Haupt, Unter1): ' + klappen().length);
          var z = zeile(0).querySelector('.toc-klappen');
          ok(!!z && z.getAttribute('aria-expanded') === 'false'
             && z.className.indexOf('ist-zugeklappt') !== -1,
             'Zaehler von Haupt sagt aus-komma-zu: ' +
             (z ? 'expanded=' + z.getAttribute('aria-expanded') + ' class=' + z.className : 'KEINER'));
          ok(nichtsGemerkt(), 'nichts in localStorage: die Deckung gilt neu');

          head('Anklicken klappt auf und oeffnet die Seite');
          zeile(0).click();
          setTimeout(function () {
            ok(sichtbar(zeile(1)) && !sichtbar(zeile(2)),
               'Unter1 ist da; Unter2 wartet hinter dem eigenen Zaehler: ' +
               all('.toc-menu .toc-item').map(function (_, i) { return sichtbar(zeile(i)) ? titel()[i] : '(' + titel()[i] + ')'; }).join('|'));
            ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
               'die Seite ist geoeffnet: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

            head('Unter1 anklicken klappt die naechste Ebene auf');
            zeile(1).click();
            setTimeout(function () {
              ok(sichtbar(zeile(2)),
                 'auch Unter2 ist da');
              ok(q('.content-title') && q('.content-title').textContent.trim() === 'Unter1',
                 'geoeffnet ist jetzt Unter1: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
              ok(nichtsGemerkt(), 'offen bleiben ist die Sache dieser Anzeige');
              head('Ende Teil 1');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 600);
          }, 600);
        }, 600);
      }, 1500);
"""

# --- Teil 2: Zaehler klappt auf und zu, Pfeile tun dasselbe ---------------
teil2 = """
      setTimeout(function () {
        setTimeout(function () {
          function verdeckt() {
            return !sichtbar(zeile(1)) && !sichtbar(zeile(2));
          }

          head('Zugeklappt beginnen, Zaehler klappt auf');
          ok(verdeckt(), 'das Verzeichnis kommt zugeklappt');
          ok(klappen().length === 2, 'zwei Zaehler: ' + klappen().length);

          klappen()[0].click();
          setTimeout(function () {
            ok(!verdeckt(), 'Unter1 und Unter2 sind da');
            ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
               'der Zaehler oeffnet nichts: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
            ok(nichtsGemerkt(), 'nichts in localStorage: ' + localStorage.getItem('simplewiki_zugeklappt'));

            head('Pfeil links klappt zu');
            zeile(0).dispatchEvent(taste('ArrowLeft', false));
            setTimeout(function () {
              ok(verdeckt(), 'Pfeil links klappt zu');
              var z = zeile(0).querySelector('.toc-klappen');
              ok(!!z && z.getAttribute('aria-expanded') === 'false',
                 'Zaehler sagt wieder aus-komma-zu: ' + (z ? z.getAttribute('aria-expanded') : 'KEINER'));
              ok(nichtsGemerkt(), 'auch hier nichts in localStorage');

              head('Pfeil rechts klappt auf');
              zeile(0).dispatchEvent(taste('ArrowRight', false));
              setTimeout(function () {
                ok(!verdeckt(), 'Pfeil rechts klappt auf');
                ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
                   'auch der Pfeil oeffnet nichts: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

                head('Ohne Kinder passiert nichts');
                zeile(3).dispatchEvent(taste('ArrowRight', false));
                setTimeout(function () {
                  ok(!verdeckt(), 'Andere hat keine Kinder - die Liste bleibt wie sie ist');
                  ok(klappen().length === 2, 'kein neuer Zaehler: ' + klappen().length);

                  head('Zaehler klappt zu');
                  klappen()[0].click();
                  setTimeout(function () {
                    ok(verdeckt(), 'wieder zu');
                    ok(!verdeckt() || zeile(0).querySelector('.toc-klappen').getAttribute('aria-expanded') === 'false',
                       'und der Zaehler sagt aus-komma-zu');
                    head('Ende Teil 2');
                    log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                    out();
                  }, 500);
                }, 500);
              }, 500);
            }, 500);
          }, 600);
        }, 600);
      }, 1500);
"""

# --- Teil 3: Suchen hebt die Deckung auf -----------------------------------
teil3 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Suchen zeigt auch verdeckte Treffer');
          ok(!sichtbar(zeile(1)) && !sichtbar(zeile(2)), 'Haupt ist von Anfang an zu');
          var feld = q('.search-box');
          feld.value = 'Unter2';
          feld.dispatchEvent(new Event('input', { bubbles: true }));
          setTimeout(function () {
            ok(titel().join('|') === 'Unter2', 'Trefferliste: ' + titel().join('|'));
            ok(sichtbar(zeile(0)), 'der Treffer ist sichtbar, obwohl verdeckt');
            ok(klappen().length === 0, 'im Treffer keine Zaehler');

            head('Suche weg - die Deckung ist wieder da');
            feld.value = '';
            feld.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(function () {
              ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig', 'alle wieder da: ' + titel().join('|'));
              ok(!sichtbar(zeile(1)) && !sichtbar(zeile(2)), 'und Haupt immer noch zu');
              head('Ende Teil 3');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 500);
          }, 500);
        }, 600);
      }, 1500);
"""

pfad1 = build('_klapp1.html', schablone.replace('__INHALT__', teil1), pages)
pfad2 = build('_klapp2.html', schablone.replace('__INHALT__', teil2), pages)
pfad3 = build('_klapp3.html', schablone.replace('__INHALT__', teil3), pages)

pruefe(pfad1, pfad2, pfad3)