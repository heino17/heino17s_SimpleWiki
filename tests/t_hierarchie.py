import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

# Verschachtelung: das Feld "eltern" nennt den Titel der Elternseite.
# Die Liste bleibt in Tiefensuche-Reihenfolge - die Elternseite steht
# direkt vor ihrem Unterbaum, und der Unterbaum wandert immer mit.
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
      function grips() { return all('.toc-menu .toc-grip'); }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function gespeichert() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      function folge() { return gespeichert().map(function (p) { return p.title; }).join('|'); }
      function eltern(t) { var p = gespeichert().filter(function (s) { return s.title === t; })[0]; return p ? (p.eltern || '') : null; }
      function ebene(i) { var m = /--ebene:\s*(\d+)/.exec(zeile(i).getAttribute('style') || ''); return m ? Number(m[1]) : -1; }
      function ebenen() { return all('.toc-menu .toc-item').map(function (_, i) { return ebene(i); }).join(', '); }
      function taste(key, alt) {
        return new KeyboardEvent('keydown', { key: key, altKey: !!alt, bubbles: true, cancelable: true });
      }
      function oben(z) { return z.getBoundingClientRect().top + 2; }
      function mitte(z) { var k = z.getBoundingClientRect(); return k.top + k.height / 2; }
      function unten(z) { return z.getBoundingClientRect().bottom - 2; }
      function ziehe(griff, ziel, clientY) {
        var d = new DataTransfer();
        griff.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d }));
        ziel.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: clientY }));
        ziel.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: d }));
        griff.dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d }));
      }
      /* Benoetigte Syntaxteile - vom Aufrufer eingefuegt. */
      __INHALT__
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
    })();
    </script>
"""

# --- Teil 1: Tastatur, Ebenen, gespeicherte eltern ------------------------
teil1 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Anzeige: die Ebenen stehen im Zeichenabstand');
          ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig', 'Reihenfolge: ' + titel().join('|'));
          ok(ebenen() === '0, 1, 2, 0, 0', 'Tiefen: ' + ebenen());
          ok(eltern('Unter1') === 'Haupt' && eltern('Unter2') === 'Unter1', 'Unter-Seiten kennen ihre Elternseite');
          ok(eltern('Andere') === '' && eltern('Zweig') === '', 'oberste Ebenen haben keine Elternseite');
          ok(folge() === titel().join('|'), 'gespeichert in derselben Reihenfolge');

          head('Alt + runter zieht den ganzen Unterbaum mit');
          zeile(0).dispatchEvent(taste('ArrowDown', true));
          setTimeout(function () {
            ok(titel().join('|') === 'Andere|Haupt|Unter1|Unter2|Zweig', 'Haupt mit Kindern hinter Andere: ' + titel().join('|'));
            ok(eltern('Unter1') === 'Haupt' && eltern('Unter2') === 'Unter1', 'Kinder haengen weiter unter Haupt');
            ok(folge() === titel().join('|'), 'und sind gespeichert');
            ok(ebenen() === '0, 0, 1, 2, 0', 'Tiefen danach: ' + ebenen());
            ok(document.activeElement === zeile(1), 'Fokus folgt der Zeile');

            head('Alt + hoch stellt es wieder hin');
            zeile(1).dispatchEvent(taste('ArrowUp', true));
            setTimeout(function () {
              ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig', 'wieder vorn: ' + titel().join('|'));
              ok(folge() === titel().join('|'), 'gespeichert');

              head('Alt + rechts rueckt ein');
              zeile(3).dispatchEvent(taste('ArrowRight', true));
              setTimeout(function () {
                ok(eltern('Andere') === 'Unter2', 'Andere steckt unter Unter2: ' + eltern('Andere'));
                ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig', 'Reihenfolge bleibt');
                ok(ebenen() === '0, 1, 2, 3, 0', 'Tiefen: ' + ebenen());

                head('Alt + rechts noch einmal');
                zeile(4).dispatchEvent(taste('ArrowRight', true));
                setTimeout(function () {
                  ok(eltern('Zweig') === 'Andere', 'Zweig steckt unter Andere: ' + eltern('Zweig'));
                  ok(ebenen() === '0, 1, 2, 3, 4', 'Kette: ' + ebenen());

                  head('Alt + links rueckt aus und nimmt die Elternseite weiter');
                  zeile(4).dispatchEvent(taste('ArrowLeft', true));
                  setTimeout(function () {
                    ok(eltern('Zweig') === 'Unter2', 'Zweig ist Geschwister der Elternseite: ' + eltern('Zweig'));
                    ok(ebenen() === '0, 1, 2, 3, 3', 'Tiefen: ' + ebenen());
                    zeile(3).dispatchEvent(taste('ArrowLeft', true));
                    setTimeout(function () {
                      ok(eltern('Andere') === 'Unter1', 'Andere ruet ist noch eine Ebene aus: ' + eltern('Andere'));
                      ok(titel().join('|') === 'Haupt|Unter1|Unter2|Zweig|Andere', 'Unterbaum folgt: ' + titel().join('|'));
                      ok(ebenen() === '0, 1, 2, 3, 2', 'Tiefen: ' + ebenen());
                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                      out();
                    }, 500);
                  }, 500);
                }, 500);
              }, 500);
            }, 500);
          }, 500);
        }, 700);
      }, 1300);
"""

# --- Teil 2: Drag & Drop mit drei Zonen -----------------------------------
teil2 = """
      setTimeout(function () {
        setTimeout(function () {
          head('Anzeige waehrend des Ziehens: drei Zonen');
          var d = new DataTransfer();
          grips()[3].dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d }));
          setTimeout(function () {
            zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: oben(zeile(2)) }));
            setTimeout(function () {
              ok(!!q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-kind'), 'Zeiger oben: Linie davor');
              zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: mitte(zeile(2)) }));
              setTimeout(function () {
                ok(!!q('.toc-item.einfuegen-kind') && !q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten'), 'Zeiger Mitte: Kinderbalken');
                zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: unten(zeile(2)) }));
                setTimeout(function () {
                  ok(!!q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-kind'), 'Zeiger unten: Linie dahinter');
                  grips()[3].dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d }));
                  setTimeout(function () {
                    ok(!q('.toc-item.wird-gezogen') && !q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-kind'), 'nach dem Ziehen ist alles weg');

                    head('Der eigene Unterbaum nimmt nichts an');
                    var d2 = new DataTransfer();
                    grips()[0].dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d2 }));
                    setTimeout(function () {
                      zeile(1).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d2, clientY: mitte(zeile(1)) }));
                      setTimeout(function () {
                        ok(!q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-kind'), 'im Unterbaum: keine Markierung');
                        zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d2, clientY: mitte(zeile(2)) }));
                        setTimeout(function () {
                          ok(!q('.toc-item.einfuegen-kind'), 'auch tief drin nicht');
                          grips()[0].dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d2 }));
                          setTimeout(function () {
                            ok(titel().join('|') === 'Haupt|Unter1|Unter2|Andere|Zweig', 'nichts verschoben');

                            head('Unterhalb landet nach dem ganzen Unterbaum');
                            ziehe(grips()[4], zeile(0), unten(zeile(0)));
                            setTimeout(function () {
                              ok(titel().join('|') === 'Haupt|Unter1|Unter2|Zweig|Andere', 'Zweig hinter dem Unterbaum von Haupt: ' + titel().join('|'));
                              ok(eltern('Zweig') === '', 'und bleibt auf oberster Ebene');
                              ok(folge() === titel().join('|'), 'gespeichert');

                              head('Mitte macht die Zeile zur Elternseite');
                              ziehe(grips()[4], zeile(1), mitte(zeile(1)));
                              setTimeout(function () {
                                ok(eltern('Andere') === 'Unter1', 'Andere ist jetzt Kind von Unter1: ' + eltern('Andere'));
                                ok(folge() === 'Haupt|Unter1|Unter2|Andere|Zweig', 'und landet als letztes Kind: ' + folge());
                                ok(ebenen() === '0, 1, 2, 2, 0', 'Tiefen: ' + ebenen());

                                head('Mitte zieht den ganzen Unterbaum mit ein');
                                ziehe(grips()[0], zeile(4), mitte(zeile(4)));
                                setTimeout(function () {
                                  ok(titel().join('|') === 'Zweig|Haupt|Unter1|Unter2|Andere', 'Haupt mit Kindern unter Zweig: ' + titel().join('|'));
                                  ok(eltern('Haupt') === 'Zweig', 'Haupt haengt unter Zweig');
                                  ok(eltern('Unter1') === 'Haupt' && eltern('Unter2') === 'Unter1', 'die Kinder haengen unveraendert');
                                  ok(ebenen() === '0, 1, 2, 3, 3', 'Tiefen: ' + ebenen());
                                  ok(folge() === titel().join('|'), 'gespeichert');
                                  log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                  out();
                                }, 500);
                              }, 500);
                            }, 500);
                          }, 500);
                        }, 400);
                      }, 400);
                    }, 400);
                  }, 400);
                }, 400);
              }, 400);
            }, 400);
          }, 400);
        }, 700);
      }, 1300);
"""

# --- Teil 3: Duplizieren, Loeschen mit Kindern, Umbenennen -----------------
teil3 = """
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function seite(t) { return gespeichert().filter(function (p) { return p.title === t; })[0]; }
      setTimeout(function () {
        setTimeout(function () {
          head('Duplizieren: die Kopie erbt die Elternseite');
          all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === 'Unter1'; })[0].click();
          setTimeout(function () {
            knopf(/Bearbeiten|Edit/).click();
            setTimeout(function () {
              knopf(/Duplizieren|Duplicate/).click();
              setTimeout(function () {
                var k = seite('Unter1 (Kopie)');
                ok(!!k, 'die Kopie steht da');
                ok(!!k && k.eltern === 'Haupt', 'und teilt sich die Elternseite: ' + (k ? k.eltern : '-'));
                ok(folge() === 'Haupt|Unter1|Unter2|Unter1 (Kopie)|Andere|Zweig', 'direkt hinter dem Unterbaum der Vorlage: ' + folge());
                ok(q('.content-title').textContent.trim() === 'Unter1 (Kopie)', 'die Kopie ist die angezeigte Seite');

                head('Loeschen stuft die Kinder hoch - zwei Kinder');
                all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === 'Haupt'; })[0].click();
                setTimeout(function () {
                  knopf(/Bearbeiten|Edit/).click();
                  setTimeout(function () {
                    knopf(/öschen|Delete/).click();
                    setTimeout(function () {
                      ok(!!q('.modal-hint'), 'der Dialog nennt das Hochstufen');
                      ok(q('.modal-hint').textContent.indexOf('Unter-Seiten rücken') >= 0, 'Mehrzahl-Hinweis: ' + q('.modal-hint').textContent.trim().slice(0, 60));
                      all('.modal .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0].click();
                      setTimeout(function () {
                        ok(folge() === 'Unter1|Unter2|Unter1 (Kopie)|Andere|Zweig', 'Kinder fuellen die Luecke: ' + folge());
                        ok(eltern('Unter1') === '' && eltern('Unter1 (Kopie)') === '', 'beide Kinder stehen jetzt oben');
                        ok(eltern('Unter2') === 'Unter1', 'Enkelkind bleibt unveraendert');

                        head('Umbenennen: der neue Name wandert zu den Kindern');
                        all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === 'Unter1'; })[0].click();
                        setTimeout(function () {
                          knopf(/Bearbeiten|Edit/).click();
                          setTimeout(function () {
                            q('.title-editor').value = 'Unter neu';
                            q('.title-editor').dispatchEvent(new Event('input', { bubbles: true }));
                            setTimeout(function () {
                              knopf(/Speichern|Save/).click();
                              setTimeout(function () {
                                ok(!!seite('Unter neu'), 'der neue Name steht in der Liste');
                                ok(eltern('Unter2') === 'Unter neu', 'das Kind haengt am neuen Namen: ' + eltern('Unter2'));
                                ok(folge() === 'Unter neu|Unter2|Unter1 (Kopie)|Andere|Zweig', 'Reihenfolge bleibt: ' + folge());
                                ok(q('.content-title').textContent.trim() === 'Unter neu', 'angezeigt wird: ' + q('.content-title').textContent.trim());

                                head('Loeschen stuft das eine Kind hoch - Einzahl');
                                knopf(/Bearbeiten|Edit/).click();
                                setTimeout(function () {
                                  knopf(/öschen|Delete/).click();
                                  setTimeout(function () {
                                    ok(q('.modal-hint').textContent.indexOf('Unter-Seite rückt') >= 0, 'Einzahl-Hinweis: ' + q('.modal-hint').textContent.trim().slice(0, 60));
                                    all('.modal .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0].click();
                                    setTimeout(function () {
                                      ok(folge() === 'Unter2|Unter1 (Kopie)|Andere|Zweig', 'wieder eine Reihe kuerzer: ' + folge());
                                      ok(eltern('Unter2') === '', 'das Kind der geloeschten Seite steht jetzt oben');
                                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                      out();
                                    }, 800);
                                  }, 500);
                                }, 500);
                              }, 1500);
                            }, 500);
                          }, 2000);
                        }, 600);
                      }, 800);
                    }, 500);
                  }, 500);
                }, 600);
              }, 500);
            }, 2000);
          }, 600);
        }, 700);
      }, 1300);
"""

pruefe(
    build('_hier1.html', schablone.replace('__INHALT__', teil1), pages),
    build('_hier2.html', schablone.replace('__INHALT__', teil2), pages),
    build('_hier3.html', schablone.replace('__INHALT__', teil3), pages)
)