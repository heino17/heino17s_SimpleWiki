import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

# Verzeichnis auf- und zuklappen: eine Elternseite kann ihre Unter-Seiten
# hinter einem Zaehler verbergen. Das ist ein Anzeige-Ding des Browsers,
# kein Feld der Seite und kein Teil des Austauschformats - gemerkt wird
# es in localStorage unter eigenem Schluessel, und nur das Zuklappen.
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
      function gezaehlt() { return JSON.parse(localStorage.getItem('simplewiki_zugeklappt') || '{}'); }
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

# --- Teil 1: ein vorgetragenes Zuklappen haelt beim Start ----------------
# PRE_SCRIPT setzt den localStorage-Eintrag, bevor die App hochfaehrt.
teil1 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Vor dem Klicken: Haupt ist zugeklappt');
          var ton = gezaehlt();
          ok(ton['1'] === true, 'der Eintrag zu id 1 ist da');
          ok(sichtbar(zeile(0)) && !sichtbar(zeile(1)) && !sichtbar(zeile(2)),
             'Unter1 und Unter2 sind verdeckt, Haupt nicht: ' +
             all('.toc-menu .toc-item').map(function (_, i) { return sichtbar(zeile(i)) ? titel()[i] : '(' + titel()[i] + ')'; }).join('|'));
          ok(klappen().length === 2, 'zwei Zaehler (Haupt, Unter1): ' + klappen().length);
          var z = zeile(0).querySelector('.toc-klappen');
          ok(!!z && z.getAttribute('aria-expanded') === 'false',
             'Zaehler von Haupt sagt aus ', z ? z.getAttribute('aria-expanded') : 'KEINER');

          head('Anklicken klappt auf und oeffnet die Seite');
          zeile(0).click();
          setTimeout(function () {
            ok(sichtbar(zeile(1)) && sichtbar(zeile(2)),
               'Unter1 und Unter2 sind wieder da');
            ok(!('1' in gezaehlt()), 'der Eintrag ist weg: ' + JSON.stringify(gezaehlt()));
            ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
               'die Seite ist geoeffnet: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
            head('Ende Teil 1');
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 600);
        }, 600);
      }, 1500);
"""

# --- Teil 2: Zaehler klappt zu und auf, Pfeile tun dasselbe --------------
teil2 = """
      setTimeout(function () {
        setTimeout(function () {
          function verdeckt() {
            return !sichtbar(zeile(1)) && !sichtbar(zeile(2));
          }

          head('Offen beginnen, Zaehler klappt zu');
          ok(sichtbar(zeile(1)) && sichtbar(zeile(2)), 'alles offen');
          ok(klappen().length === 2, 'zwei Zaehler: ' + klappen().length);

          klappen()[0].click();
          setTimeout(function () {
            ok(verdeckt(), 'Unter1 und Unter2 sind weg');
            ok(gezaehlt()['1'] === true, 'gemerkt: ' + JSON.stringify(gezaehlt()));
            ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
               'Zuklappen hat nichts geoeffnet: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

            head('Pfeil rechts klappt auf');
            zeile(0).dispatchEvent(taste('ArrowRight', false));
            setTimeout(function () {
              ok(!verdeckt(), 'Pfeil rechts klappt auf');
              ok(!('1' in gezaehlt()), 'gemerkt ist nichts mehr: ' + JSON.stringify(gezaehlt()));

              head('Pfeil links klappt zu');
              zeile(0).dispatchEvent(taste('ArrowLeft', false));
              setTimeout(function () {
                ok(verdeckt(), 'wieder zu');
                ok(gezaehlt()['1'] === true, 'wieder gemerkt: ' + JSON.stringify(gezaehlt()));
                ok(q('.content-title') && q('.content-title').textContent.trim() === 'Haupt',
                   'auch der Pfeil oeffnet nichts');

                head('Ohne Zaehler passiert nichts');
                zeile(3).dispatchEvent(taste('ArrowLeft', false));
                setTimeout(function () {
                  ok(verdeckt(), 'Andere hat keine Kinder - Liste bleibt zu');
                  ok(gezaehlt()['1'] === true, 'kein neuer Eintrag: ' + JSON.stringify(gezaehlt()));

                  head('Zaehler klappt wieder auf');
                  klappen()[0].click();
                  setTimeout(function () {
                    ok(!verdeckt(), 'wieder alles offen');
                    ok(!('1' in gezaehlt()), 'Schluessel weg: ' + JSON.stringify(gezaehlt()));
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

# --- Teil 3: Suchen hebt die Deckung auf ----------------------------------
teil3 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Suchen zeigt auch verdeckte Treffer');
          klappen()[0].click();
          setTimeout(function () {
            ok(!sichtbar(zeile(1)) && !sichtbar(zeile(2)), 'Haupt ist zu');
            var feld = q('.search-box');
            feld.value = 'Unter2';
            feld.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(function () {
              ok(titel().join('|') === 'Unter2', 'Trefferliste: ' + titel().join('|'));
              ok(sichtbar(zeile(0)), 'der Treffer ist sichtbar, obwohl verdeckt');
              ok(klappen().length === 0, 'im Treffer keine Zaehler');

              head('Suche weg - das Zuklappen ist wieder da');
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
        }, 600);
      }, 1500);
"""

mkcopy.PRE_SCRIPT = ('<script>try{localStorage.setItem("simplewiki_zugeklappt",'
                     'JSON.stringify({"1":true}));}catch(e){}</script>')
pfad1 = build('_klapp1.html', schablone.replace('__INHALT__', teil1), pages)
mkcopy.PRE_SCRIPT = ''

pfad2 = build('_klapp2.html', schablone.replace('__INHALT__', teil2), pages)
pfad3 = build('_klapp3.html', schablone.replace('__INHALT__', teil3), pages)

pruefe(pfad1, pfad2, pfad3)