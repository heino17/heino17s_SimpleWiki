import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

# Die Huellseite, die beim Anlegen entsteht, lebt auf Widerruf: wer
# "Abbrechen" klickt oder die Seite verlässt, ohne zu sichern, bekommt
# sie ersatzlos zurueckgenommen - aus der Liste und aus dem Speicher.
# "Sichern" macht sie dauerhaft. Die Seiten fuessen auf den gleichen
# Startpunkt: Alpha, Beta, Alpha offen.
pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
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
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      /* Benoetigte Syntaxteile - vom Aufrufer eingefuegt. */
      __INHALT__
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });
    })();
    </script>
"""

# --- Teil 1: das "+" und dann Abbrechen -----------------------------------
teil1 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Anlegen und Abbrechen');
          q('.kopf-neu').click();
          setTimeout(function () {
            ok(speicher().length === 3, 'erst einmal angelegt: drei Seiten: ' + speicher().length);
            ok(titel().indexOf('Neue Seite') >= 0, 'die Huellseite steht im Verzeichnis');

            btn(/Abbrechen/).click();
            setTimeout(function () {
              ok(speicher().length === 2, 'Abbrechen nimmt sie zurueck: ' + speicher().length);
              ok(titel()[0] === 'Alpha' && titel()[1] === 'Beta',
                 'Verzeichnis wieder nur Alpha|Beta: ' + titel().join('|'));
              ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
                 'zurueck auf der vorherigen Seite: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
              ok(!q('.md-host'), 'Editor zu, Anzeigemodus');
              ok(speicher().every(function (p) { return p.title !== 'Neue Seite'; }),
                 'auch im Speicher nirgends mehr: ' +
                 speicher().map(function (p) { return p.title; }).join('|'));
              head('Ende Teil 1');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 600);
          }, 1200);
        }, 600);
      }, 1500);
"""

# --- Teil 2: das "+" und dann wegklicken ohne zu sichern -------------------
teil2 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Anlegen und ohne Sichern wegklicken');
          q('.kopf-neu').click();
          setTimeout(function () {
            ok(speicher().length === 3, 'erst einmal angelegt');
            ok(btn(/Abbrechen/) !== undefined, 'im Bearbeiten, Abbrechen steht da');

            /* Wer eine andere Zeile anklickt, hat die Seite ebenso
               verlassen wie mit Abbrechen - sie verschwindet auch da. */
            all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === 'Beta'; })[0].click();
            setTimeout(function () {
              ok(speicher().length === 2, 'wegklicken nimmt sie zurueck: ' + speicher().length);
              ok(titel().join('|') === 'Alpha|Beta', 'Verzeichnis: ' + titel().join('|'));
              ok(q('.content-title') && q('.content-title').textContent.trim() === 'Beta',
                 'die neue Seite ist geoeffnet: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
              ok(speicher().every(function (p) { return p.title !== 'Neue Seite'; }),
                 'auch im Speicher keine Spur');
              head('Ende Teil 2');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 600);
          }, 1200);
        }, 600);
      }, 1500);
"""

# --- Teil 3: gesicherte Seiten verlassen sich auf nichts -------------------
teil3 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Sichern macht die Seite dauerhaft');
          q('.kopf-neu').click();
          setTimeout(function () {
            var feld = q('.title-editor');
            feld.value = 'Gamma';
            feld.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(function () {
              btn(/Speichern/).click();
              setTimeout(function () {
                ok(speicher().some(function (p) { return p.title === 'Gamma'; }),
                   'nach dem Sichern ist Gamma da: ' +
                   speicher().map(function (p) { return p.title; }).join('|'));

                head('Bearbeiten und Abbrechen laesst Gamma stehen');
                btn(/Bearbeiten/).click();
                setTimeout(function () {
                  btn(/Abbrechen/).click();
                  setTimeout(function () {
                    ok(speicher().some(function (p) { return p.title === 'Gamma'; }),
                       'Abbrechen nach dem Sichern nimmt nichts weg');
                    ok(titel().indexOf('Gamma') >= 0,
                       'und das Verzeichnis zeigt Gamma weiter: ' + titel().join('|'));
                    ok(q('.content-title') && q('.content-title').textContent.trim() === 'Gamma',
                       'weiterhin auf Gamma: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
                    head('Ende Teil 3');
                    log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                    out();
                  }, 600);
                }, 1200);
              }, 1400);
            }, 600);
          }, 1200);
        }, 600);
      }, 1500);
"""

pfad1 = build('_abb1.html', schablone.replace('__INHALT__', teil1), pages)
pfad2 = build('_abb2.html', schablone.replace('__INHALT__', teil2), pages)
pfad3 = build('_abb3.html', schablone.replace('__INHALT__', teil3), pages)

pruefe(pfad1, pfad2, pfad3)