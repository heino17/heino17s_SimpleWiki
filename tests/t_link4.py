import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ("<script>window.__errs=[];var oe=console.error;"
 "console.error=function(){window.__errs.push([].slice.call(arguments).map(String).join(' '));"
 "oe.apply(console,arguments);};" + chr(60) + "/script>")

pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nText", "links": ["Beta", "Gibt es noch nicht"], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": ["Alpha"], "tags": [], "created": "x", "updated": "x"},
]

script = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ' : 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      function imEditor(fn) {
        if (!btn(/Bearbeiten|Edit/)) { fn(); return; }          // schon im Editor
        btn(/Bearbeiten|Edit/).click();
        setTimeout(fn, 2400);
      }
      function dialogOeffnen(dann) {
        imEditor(function () {
          btn(/Verlinken|Link/).click();
          setTimeout(dann, 600);
        });
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Verweise');
        var marke = (function () { var b = q('.menu-badge'); return b ? b.textContent.trim() : ''; })();
        ok(marke === '3', 'Alpha hat drei Verweise (Beta, fehlendes Ziel, rueckverwiesen): ' + marke);
        ok(!q('.backlinks') && !q('.outgoing'), 'Verweise stehen nur noch im Panel, nicht in der Seite');

        dialogOeffnen(function () {
          head('Dialog');
          ok(!!q('.modal-link'), 'Dialog offen');
          ok(q('.modal-link h3').textContent.trim() === 'Seite verlinken', 'Titel: ' + q('.modal-link h3').textContent.trim());
          var zeilen = all('.link-item');
          ok(zeilen.length === 1, 'nur die andere Seite wird angeboten: ' + zeilen.map(function (b) { return b.textContent.trim(); }).join('|'));
          ok(!!all('.link-item-aktiv').length, 'verlinkte Seite ist markiert');
          ok(all('.modal-link input').length === 2, 'Suchfeld und Eingabefeld vorhanden');
          ok(all('.modal-actions .btn').filter(function (b) { return b.textContent.trim() === 'Speichern'; }).length === 1, 'Knopf heißt Speichern');

          head('Verknüpfung loesen');
          all('.link-item')[0].click();
          setTimeout(function () {
            ok(!!q('.modal-link'), 'Dialog bleibt beim Auswählen offen');
            ok(speicher()[0].links.indexOf('Beta') < 0, 'Beta gelöst: ' + JSON.stringify(speicher()[0].links));
            ok(JSON.stringify(speicher()[1].links) === '["Alpha"]', 'Beta verweist weiter auf Alpha');

            dialogOeffnen(function () {
              head('Neu verlinken');
              all('.link-item')[0].click();
              setTimeout(function () {
                ok(speicher()[0].links.indexOf('Beta') >= 0, 'Beta wieder verlinkt: ' + JSON.stringify(speicher()[0].links));

                dialogOeffnen(function () {
                  head('Seite suchen und neue anlegen');
                  var suche = all('.modal-link input')[0];
                  suche.value = 'Be'; suche.dispatchEvent(new Event('input', { bubbles: true }));
                  setTimeout(function () {
                    var treffer = all('.link-item').map(function (b) { return b.textContent.trim(); });
                    ok(treffer.length === 1 && treffer[0].indexOf('Beta') >= 0, 'Suche "Be" liefert: ' + treffer.join('|'));
                    suche.value = ''; suche.dispatchEvent(new Event('input', { bubbles: true }));
                    setTimeout(function () {
                      var feld = all('.modal-link input')[1];
                      feld.value = 'Gamma'; feld.dispatchEvent(new Event('input', { bubbles: true }));
                      setTimeout(function () {
                        var knopf = all('.modal-actions .btn').filter(function (b) { return /Anlegen|Create/.test(b.textContent); })[0];
                        ok(!!knopf && !knopf.disabled, 'Knopf "Anlegen und verlinken" bereit');
                        knopf.click();
                        setTimeout(function () {
                          var sp = speicher();
                          var vonAlpha = sp.filter(function (p) { return p.title === 'Alpha'; })[0];
                          ok(sp.some(function (p) { return p.title === 'Gamma'; }), 'neue Seite angelegt: ' + sp.map(function (p) { return p.title; }).join('|'));
                          ok(vonAlpha && vonAlpha.links.indexOf('Gamma') >= 0, 'und mit Alpha verlinkt: ' + JSON.stringify(vonAlpha ? vonAlpha.links : []));
                          ok(!q('.modal-link'), 'Dialog schließt über den Knopf');

                          head('Speichern im Editor');
                          btn(/Speichern|Save/).click();
                          setTimeout(function () {
                            ok(!q('.md-host .toastui-editor-defaultUI'), 'Editor geschlossen');
                            var alphaNach = speicher().filter(function (p) { return p.title === 'Alpha'; })[0];
                            ok(alphaNach && JSON.stringify(alphaNach.links).indexOf('Gamma') >= 0,
                               'Verknüpfungen überleben das Speichern: ' + JSON.stringify(alphaNach ? alphaNach.links : []));

                            head('Klick auf verlinkte Seite');
                            setTimeout(function () {
                              all('.toc-item-title').filter(function (e) { return e.textContent.trim() === 'Alpha'; })[0].click();
                              setTimeout(function () {
                                q('.refs-toggle').click();
                                setTimeout(function () {
                                var ziel = all('.refs-item .refs-name').map(function (a) { return a.textContent.trim(); });
                                log.push('     Ziele: ' + ziel.join('|'));
                                var ziel2 = all('.refs-item').filter(function (b) { return /Beta/.test(b.textContent); })[0];
                                ok(!!ziel2, 'Beta steht im Verweis-Panel');
                                ziel2.click();
                                }, 600);
                                setTimeout(function () {
                                  ok(q('.content-title') && q('.content-title').textContent.trim() === 'Beta',
                                     'nach Klick auf Beta: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '?'));
                                  log.push('');
                                  log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                  out();
                                }, 700);
                              }, 700);
                            }, 500);
                          }, 800);
                        }, 700);
                      }, 600);
                    }, 600);
                  }, 600);
                });
              }, 600);
            });
          }, 600);
        });
      }, 3000);
    })();
    </script>
"""

pruefe(
    build('_link3.html', script, pages, theme='light', lang='de', startpage='a')
)
