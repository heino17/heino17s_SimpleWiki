import sys, io, re, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, KOPIEN, zahlen
import html as H

# Der Report-Block des Tests darf nicht mitgedruckt werden.
mkcopy.EXTRA_REPLACEMENTS = [('</style>', '    #report { display: none !important; }\n    </style>')]

seiten = [
    {"id": "z", "title": "Zwiebeln", "content": "# Zwiebeln\n\nZwiebeln sind scharf. Siehe [[Kartoffeln]].", "links": ["Kartoffeln"], "tags": [], "created": "x", "updated": "x"},
    {"id": "a", "title": "Kartoffeln", "content": "# Kartoffeln\n\nMan kocht sie mit [[Zwiebeln]].", "links": ["Zwiebeln"], "tags": [], "created": "x", "updated": "x"},
    {"id": "m", "title": "Leere Seite", "content": "", "links": [], "tags": [], "created": "x", "updated": "x"},
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
      function flussTitel() { return all('.fluss-eintrag-titel').map(function (t) { return t.textContent.trim(); }); }
      /* Der Fluss wird ueber den Knopf im Kopf geoeffnet. Das
         Inhaltsverzeichnis ist eine Spalte und kein Panel mehr, und in
         ihm steht kein Knopf - nur der Hinweis auf die Reihenfolge. */
      function knopfImVerzeichnis() { return all('.toc-menu .new-page-btn'); }
      function flussOeffnen() { q('.kopf-fluss').click(); }
      function zurueck() { q('.kopf-fluss').click(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Start');
        ok(!q('.fluss'), 'kein Fluss beim Start');
        ok(!!q('.content-title'), 'normale Seitenansicht: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

        setTimeout(function () {
          var knoepfe = knopfImVerzeichnis();
          ok(knoepfe.length === 0, 'im Verzeichnis steht kein Knopf: ' + knoepfe.map(function (b) { return b.textContent.trim(); }).join(' / '));
          ok(!q('.toc-menu .toc-footer') && !q('.toc-hint'),
             'und darunter steht nichts mehr');
          ok(!!q('.toc-menu .toc-grip'), 'nur die Zeilen mit ihren Griffen');
          ok(!q('.toc-menu').textContent.match(/Fluss|River/), 'im Verzeichnis steht kein Fluss-Knopf');
          ok(!!q('.kopf-fluss'), 'der Fluss-Knopf sitzt im Kopf');
          ok(!!q('.kopf-neu'), 'und "Neue Seite" auch');

          head('Fluss oeffnen');
          flussOeffnen();
          setTimeout(function () {
            ok(!!q('.fluss'), 'Fluss sichtbar');
            ok(!!q('.toc-menu'), 'das Verzeichnis steht daneben weiter');
            ok(q('.content-title') === null, 'normale Seitenansicht verschwunden');
            ok(q('.footer') === null, 'keine Fussleiste zum Bearbeiten');
            ok(!!q('.header') && !!q('.search-box') && !!q('.settings-toggle'), 'Kopfmenu bleibt');
            ok(q('.fluss-titel').textContent.trim() === 'Fluss – alle Seiten', 'Titel: ' + q('.fluss-titel').textContent.trim());
            ok(q('.fluss-zahl').textContent.indexOf('3') >= 0, 'Seitenzahl: ' + q('.fluss-zahl').textContent.trim());

            head('Inhalt und Reihenfolge');
            ok(flussTitel().join('|') === 'Zwiebeln|Kartoffeln|Leere Seite', 'Reihenfolge wie im Verzeichnis: ' + flussTitel().join('|'));
            var texte = all('.fluss-eintrag .preview').map(function (p) { return p.textContent.replace(/\s+/g, ' ').trim(); });
            ok(texte[0].indexOf('Zwiebeln sind scharf') >= 0, 'Inhalt der ersten Seite: ' + texte[0]);
            ok(all('.fluss-eintrag .preview a[data-wiki-link]').length === 2, 'Links im Text klickbar: ' + all('.fluss-eintrag .preview a[data-wiki-link]').length);
            ok(all('.fluss-eintrag')[2].textContent.indexOf('ohne Text') >= 0, 'Seite ohne Text wird gekennzeichnet');
            ok(!!q('.fluss-verweise') && q('.fluss-verweise').textContent.indexOf('Kartoffeln') >= 0,
               'Verweise stehen dabei: ' + (q('.fluss-verweise') ? q('.fluss-verweise').textContent.trim() : '-'));

            head('Suche filtert den Fluss');
            var suche = q('.search-box');
            suche.value = 'scharf';
            suche.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(function () {
              ok(flussTitel().join('|') === 'Zwiebeln', 'nur noch passende Seiten: ' + flussTitel().join('|'));
              suche.value = '';
              suche.dispatchEvent(new Event('input', { bubbles: true }));
              setTimeout(function () {
                ok(flussTitel().length === 3, 'wieder alle drei');

                head('Link im Fluss oeffnet die Seite');
                all('.fluss-eintrag .preview a[data-wiki-link]')[0].click();
                setTimeout(function () {
                  ok(!q('.fluss'), 'Fluss verlassen');
                  ok(q('.content-title').textContent.trim() === 'Kartoffeln', 'Seite geoeffnet: ' + q('.content-title').textContent.trim());
                  ok(!!q('.footer'), 'Fussleiste wieder da');

                  head('Titel im Fluss oeffnet die Seite');
                  setTimeout(function () {
                    flussOeffnen();
                    setTimeout(function () {
                      all('.fluss-titel-knopf')[1].click();
                      setTimeout(function () {
                        ok(!q('.fluss') && q('.content-title').textContent.trim() === 'Kartoffeln', 'Titelknopf oeffnet die Seite');

                        head('Zurueck-Knopf');
                        setTimeout(function () {
                          flussOeffnen();
                          setTimeout(function () {
                            zurueck();
                            setTimeout(function () {
                              ok(!q('.fluss') && !!q('.content-title'), 'zurueck in der Einzelansicht');

                              head('Drucken aus dem Fluss');
                              setTimeout(function () {
                                flussOeffnen();
                                setTimeout(function () {
                                  ok(all('.fluss-aktionen .btn').length === 1, 'im Fluss bleibt nur der Druck-Knopf: ' + all('.fluss-aktionen .btn').map(function (b) { return b.textContent.trim(); }).join(' / '));
                                  ok(!q('.fluss-aktionen .btn-primary'), 'kein Zurueck-Knopf mehr im Fluss - der Kopf-Knopf schaltet');
                                  ok(!!all('.fluss-aktionen .btn')[0], 'Druck-Knopf: ' + all('.fluss-aktionen .btn')[0].textContent.trim());
                                  window.__print = 0;
                                  window.print = function () { window.__print++; };
                                  all('.fluss-aktionen .btn')[0].click();
                                  setTimeout(function () {
                                    ok(window.__print === 1, 'Drucken aufgerufen');
                                    ok(!!q('.fluss'), 'man bleibt im Fluss, wie man kam');

                                    head('Drucken von einer normalen Seite');
                                    zurueck();
                                    setTimeout(function () {
                                      ok(!q('.fluss'), 'wieder Einzelansicht');
                                      window.dispatchEvent(new Event('beforeprint'));
                                      setTimeout(function () {
                                        ok(!!q('.fluss'), 'beim Druck kommt der Fluss');
                                        window.dispatchEvent(new Event('afterprint'));
                                        setTimeout(function () {
                                          ok(!q('.fluss'), 'nach dem Druck wieder weg');
                                          ende();
                                        }, 600);
                                      }, 600);
                                    }, 700);
                                  }, 800);
                                }, 600);
                              }, 600);
                            }, 600);
                          }, 600);
                        }, 600);
                      }, 600);
                    }, 600);
                  }, 600);
                }, 600);
              }, 600);
            }, 600);
          }, 800);
        }, 900);
      }, 1500);
    })();
    </script>
"""
build('_fluss1.html', script, seiten, startpage='z')

text = bericht(dumpdom('_fluss1.html', budget=150000))
print('=== Fluss im Browser ===')
print(text if text else 'KEIN REPORT')
bestanden_browser, fehler_browser = zahlen(text)

# ---------------------------------------------------------------- Drucken
pdf = os.path.join(KOPIEN, '_fluss_druck.pdf')
if os.path.exists(pdf):
    os.remove(pdf)
subprocess.run(['chromium', '--headless', '--disable-gpu', '--no-sandbox',
                '--virtual-time-budget=40000', '--no-pdf-header-footer',
                '--print-to-pdf=' + pdf,
                'file://' + os.path.join(KOPIEN, '_fluss1.html')],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)

print('\n=== Ausdruck als PDF (echter Druck) ===')
if os.path.exists(pdf):
    info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    zeilen = [l for l in info.split('\n') if l.startswith('Pages')]
    print('  ', zeilen[0].strip() if zeilen else '?')
    txt = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    alles = ' '.join(txt.split())
    fehler = 0
    bestanden_druck = 0
    for erwartet in ['Zwiebeln sind scharf', 'Man kocht sie mit', 'Leere Seite', 'ohne Text']:
        da = erwartet in alles
        fehler += 0 if da else 1
        bestanden_druck += 1 if da else 0
        print('  %-22s %s' % (erwartet, 'ja' if da else 'NEIN'))
    for unerwartet in ['Neue Seite', 'Einstellungen', 'Bearbeiten', 'Speichern', 'Fluss – alle Seiten']:
        weg = unerwartet not in alles
        fehler += 0 if weg else 1
        bestanden_druck += 1 if weg else 0
        print('  %-22s %s' % ('ohne ' + unerwartet, 'ok' if weg else 'NOCH DA'))
    print('\n>>> Druckansicht: ' + ('BESTANDEN' if fehler == 0 else '%d FEHLGESCHLAGEN' % fehler))
    gesamt = fehler_browser + fehler
else:
    print('   PDF wurde nicht erzeugt')
    gesamt = fehler_browser + 1
    bestanden_druck = 0

print()
print('>>> ' + ('%d FEHLGESCHLAGEN' % gesamt if gesamt else 'ALLE BESTANDEN'))
# Ohne diese Zeile zaehlt dieser Test in der Suite als null: die Pruefungen
# im Browser und die am PDF laufen, ihre Zahl kommt aber nirgends an.
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (bestanden_browser + bestanden_druck, gesamt))
sys.exit(1 if gesamt else 0)
