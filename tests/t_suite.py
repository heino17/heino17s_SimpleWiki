import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkcopy import build
from _hilfe import pruefe

pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nEin **fetter** Text.\n\n- Punkt 1", "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta\n\nInhalt von Beta", "tags": [], "created": "x", "updated": "x"},
    {"id": "c", "title": "Leer", "content": "", "tags": [], "created": "x", "updated": "x"},
]

script = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() {
        var p = document.getElementById('report');
        if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); }
        p.textContent = log.join('\n');
      }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ' : 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function fuss() { return all('.footer .btn'); }
      function modus() {
        var a = all('.md-host .toastui-editor-mode-switch .tab-item')
                 .filter(function (t) { return /active/.test(t.className); })[0];
        return a ? a.textContent.trim() : '?';
      }
      function reiter(x) {
        return all('.md-host .toastui-editor-mode-switch .tab-item')
               .filter(function (t) { return new RegExp(x, 'i').test(t.textContent); })[0];
      }
      function klick(el) {
        ['mousedown', 'mouseup', 'click'].forEach(function (t) {
          el.dispatchEvent(new MouseEvent(t, { bubbles: true, cancelable: true, view: window }));
        });
      }
      function tswitch() {
        return new Promise(function (res) {
          setTimeout(function () {
            var b = btn(/Bearbeiten|Edit/);
            if (b) b.click();
            setTimeout(res, 2200);
          }, 350);
        });
      }
      function sprache(code) {
        q('.settings-toggle').click();
        return new Promise(function (res) {
          setTimeout(function () {
            var s = q('#settings-language');
            s.value = code; s.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(res, 500);
          }, 400);
        });
      }

      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Grundzustand');
        ok(!!q('.content-title'), 'Startseite wird angezeigt: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '?'));
        ok(all('.toc-panel .toc-item').length === 3, 'Inhaltsverzeichnis zeigt 3 Seiten');
        ok(!!q('.toc-item-start'), 'Stern-Markierung vorhanden');
        ok(localStorage.getItem('simplewiki_startpage') === 'a', 'Startseite gespeichert: ' + localStorage.getItem('simplewiki_startpage'));

        head('Einstellungen');
        q('.settings-toggle').click();
        setTimeout(function () {
          ok(q('.settings-panel').classList.contains('open'), 'Einstellungen öffnen');
          ok(all('#settings-startpage option').map(function (o) { return o.textContent.trim(); }).join('|') === 'Alpha|Beta|Leer',
             'Startseiten-Auswahl: ' + all('#settings-startpage option').map(function (o) { return o.textContent.trim(); }).join('|'));
          var sp = q('#settings-startpage');
          sp.value = 'b'; sp.dispatchEvent(new Event('change', { bubbles: true }));
          setTimeout(function () {
            ok(localStorage.getItem('simplewiki_startpage') === 'b', 'Startseite geändert: ' + localStorage.getItem('simplewiki_startpage'));
            var sterne = all('.toc-panel .toc-item').filter(function (i) {
              return !i.querySelector('.toc-item-start').classList.contains('is-empty');
            }).map(function (i) { return i.querySelector('.toc-item-title').textContent.trim(); });
            ok(sterne.join() === 'Beta', 'Stern wandert mit: ' + sterne.join());
            q('.side-close').click();

            head('Suche');
            var s = q('.search-box');
            s.value = 'Inhalt'; s.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(function () {
              ok(q('.toc-panel').classList.contains('open'), 'Suche öffnet das Verzeichnis');
              var treffer = all('.toc-panel .toc-item-title').map(function (e) { return e.textContent.trim(); });
              ok(treffer.join() === 'Beta', 'Suche findet genau Beta: ' + treffer.join('|'));
              s.value = 'gibtsnicht'; s.dispatchEvent(new Event('input', { bubbles: true }));
              setTimeout(function () {
                ok(!!q('.toc-empty'), 'Leerhinweis: "' + q('.toc-empty').textContent.trim() + '"');
                q('.clear-search').click();
                setTimeout(function () {
                  ok(all('.toc-panel .toc-item-title').length === 3, 'Suche zurückgesetzt');

                  head('Editor');
                  tswitch().then(function () {
                    ok(!!q('.md-host .toastui-editor-defaultUI'), 'WYSIWYG-Editor geöffnet');
                    ok(!q('.editor'), 'kein Textfeld-Rückfall');
                    ok(all('.md-host .toastui-editor-toolbar-icons').length > 10,
                       'Toolbar: ' + all('.md-host .toastui-editor-toolbar-icons').length + ' Knöpfe');
                    var t1 = all('.md-host .tab-item').map(function (x) { return x.textContent.trim(); }).join('/');
                    ok(t1 === 'Verfassen/Vorschau/Markdown/WYSIWYG', 'Reiter deutsch: ' + t1);
                    klick(reiter('Markdown'));
                    setTimeout(function () {
                      ok(modus() === 'Markdown', 'Umschalter -> Markdown');
                      klick(reiter('WYSIWYG'));
                      setTimeout(function () {
                        ok(modus() === 'WYSIWYG', 'Umschalter -> WYSIWYG');
                        btn(/Speichern|Save/).click();
                        setTimeout(function () {
                          ok(!!q('.preview h1'), 'Vorschau mit H1');
                          ok(!q('.md-host .toastui-editor-defaultUI'), 'Editor abgebaut nach Speichern');
                          var ps = JSON.parse(localStorage.getItem('simplewiki_pages'));
                          ok(ps[1].content === '# Beta\n\nInhalt von Beta', 'Inhalt unverändert: ' + JSON.stringify(ps[1].content));

                          head('Leere Seite / Platzhalter');
                          q('.menu-toggle').click();
                          setTimeout(function () {
                            all('.toc-item-title')[2].click();
                            setTimeout(function () {
                              tswitch().then(function () {
                                var ph = q('.md-host .placeholder');
                                ok(!!ph && ph.textContent.indexOf('Schreibe hier') === 0,
                                   'Platzhalter auf leerer Seite: ' + (ph ? JSON.stringify(ph.textContent.trim()) : 'fehlt'));
                                btn(/Abbrechen|Cancel/).click();
                                setTimeout(function () {
                                  ok(!q('.md-host .toastui-editor-defaultUI'), 'Abbrechen baut den Editor ab');
                                  ok(JSON.parse(localStorage.getItem('simplewiki_pages'))[2].content === '',
                                     'Abbrechen verwirft nichts');

                                  head('Sprache mitten im Betrieb');
                                  sprache('en').then(function () {
                                    ok(q('.settings-panel .side-header h2').textContent.trim() === 'Settings',
                                       'Panel auf Englisch: ' + q('.settings-panel .side-header h2').textContent.trim());
                                    q('.side-close').click();
                                    tswitch().then(function () {
                                      var t2 = all('.md-host .tab-item').map(function (x) { return x.textContent.trim(); }).join('/');
                                      ok(t2 === 'Write/Preview/Markdown/WYSIWYG', 'Editor-Oberfläche englisch: ' + t2);
                                      btn(/Cancel/).click();
                                      setTimeout(function () {
                                        head('Dunkelmodus');
                                        q('.theme-toggle').click();
                                        setTimeout(function () {
                                          /* Das dunkle Stylesheet steckt inline in der Datei und wird ueber
                                             media geschaltet - 'disabled' gibt es bei
                                             einem <style>-Element nicht. */
                                             var ds = document.getElementById('mdEditorDarkTheme');
                                             ok(!!ds && ds.tagName === 'STYLE' && ds.media === 'all',
                                                'dunkles Editor-Stylesheet aktiv: media=' + (ds ? ds.media : 'fehlt'));
                                          ok(!!q('.toc-item-start'), 'Stern weiterhin sichtbar');
                                          q('.theme-toggle').click();

                                          head('Seite löschen');
                                          q('.menu-toggle').click();
setTimeout(function () {
                                                 /* und wieder zurueck - sonst prueft der
                                                    Test nur die eine Richtung */
                                                 var ds2 = document.getElementById('mdEditorDarkTheme');
                                                 ok(!!ds2 && ds2.media === 'not all',
                                                    'heller Modus: media=' + (ds2 ? ds2.media : 'fehlt'));
all('.toc-item')[0].querySelector('.toc-item-title').click();
                                                 setTimeout(function () {
                                                   /* Geloescht wird nur noch im Editor -
                                                      im Verzeichnis gibt es kein Kreuz mehr. */
                                                   ok(!q('.toc-item-delete'), 'im Verzeichnis ist kein Loeschkreuz mehr');
                                                   var bearbeiten = all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0];
                                                   ok(!!bearbeiten, 'Bearbeiten-Knopf da');
                                                   bearbeiten.click();
                                                   setTimeout(function () {
                                                     var loeschen = all('.footer .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0];
                                                     ok(!!loeschen, 'Löschen-Knopf im Editor');
                                                     loeschen.click();
                                                     setTimeout(function () {
                                                       ok(!!q('.modal-overlay'), 'Löschen-Dialog');
                                                       all('.modal .btn').filter(function (b) { return /Delete|Delete|öschen/.test(b.textContent); })[0].click();
                                                       setTimeout(function () {
                                                         ok(all('.toc-panel .toc-item').length === 2, 'Seite gelöscht, verbleiben: ' + all('.toc-panel .toc-item-title').map(function (e) { return e.textContent.trim(); }).join('|'));
                                                         log.push('');
                                                         log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                                         out();
                                                       }, 600);
                                                     }, 400);
                                                   }, 500);
                                                 }, 600);
                                               }, 500);
                                             }, 500);
                                           }, 2400);
                                    });
                                  });
                                }, 2400);
                              }, 400);
                            }, 500);
                          }, 500);
                        }, 700);
                      }, 800);
                    }, 1000);
                  });
                }, 500);
              }, 500);
            }, 500);
          }, 500);
        }, 500);
      }, 3000);
    })();
    </script>
"""

pruefe(
    build('_suite.html', script, pages, theme='light', lang='de', startpage='a')
)
