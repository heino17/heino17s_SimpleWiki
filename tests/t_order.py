import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

pages = [
    {"id": "1", "title": "Eins", "content": "# Eins", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Zwei", "content": "# Zwei", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "3", "title": "Drei", "content": "# Drei", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "4", "title": "Vier", "content": "# Vier", "links": [], "tags": [], "created": "x", "updated": "x"},
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
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function gespeichert() { return JSON.parse(localStorage.getItem('simplewiki_pages')).map(function (p) { return p.title; }); }
      function zeile(i) { return all('.toc-menu .toc-item')[i]; }
      function grips() { return all('.toc-menu .toc-grip'); }
      /* Erwartung selbst berechnen: die Seite von Position "von" wird
         vor Position "nach" geschoben. */
      function erwartet(vorher, von, nach) {
        var a = vorher.slice();
        var x = a.splice(von, 1)[0];
        a.splice(nach, 0, x);
        return a.join('|');
      }
      function taste(key, alt) {
        return new KeyboardEvent('keydown', { key: key, altKey: !!alt, bubbles: true, cancelable: true });
      }
      /* Drei Zonen: die oberste Treppe zielt davor, die unterste dahinter,
         die Mitte drauf. Der Abstand nach aussen muss sicher in die Zone
         treffen - darum der Abstand 2 statt des Rechnens aufs Drittel. */
      function oben(z) { var k = z.getBoundingClientRect(); return k.top + 2; }
      function unten(z) { var k = z.getBoundingClientRect(); return k.bottom - 2; }
      function ziehe(griff, ziel, clientY) {
        var d = new DataTransfer();
        griff.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d }));
        ziel.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: clientY }));
        ziel.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: d }));
        griff.dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d }));
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        setTimeout(function () {
          head('Griff und Hinweis');
          ok(grips().length === 4, 'jede Zeile hat einen Griff: ' + grips().length);
          /* Der Hinweis auf die Reihenfolge steht am Griff, nicht als
             Zeile unter der Liste. Man braucht ihn nur, wenn man anfasst,
             und dann ist er genau dort. */
          ok(!q('.toc-hint') && !q('.toc-footer'), 'unter der Liste steht kein Hinweis mehr');
          ok(grips()[0].getAttribute('title').indexOf('Alt') >= 0,
             'am Griff steht er und nennt den Tastaturweg: ' + grips()[0].getAttribute('title'));
          ok(grips()[0].getAttribute('draggable') === 'true', 'Griff ist ziehbar');
          ok(zeile(0).getAttribute('tabindex') === '0', 'Zeile ist fokussierbar');
          ok(titel().join('|') === 'Eins|Zwei|Drei|Vier', 'Startreihenfolge: ' + titel().join('|'));

          head('Tastatur: Alt + Pfeil runter');
          zeile(0).dispatchEvent(taste('ArrowDown', true));
          setTimeout(function () {
            ok(titel().join('|') === 'Zwei|Eins|Drei|Vier', 'Eins ist eine Zeile tiefer: ' + titel().join('|'));
            ok(gespeichert().join('|') === 'Zwei|Eins|Drei|Vier', 'und gespeichert: ' + gespeichert().join('|'));
            ok(document.activeElement === zeile(1), 'Fokus folgt der Zeile');

            head('Tastatur: Alt + Pfeil hoch');
            zeile(1).dispatchEvent(taste('ArrowUp', true));
            setTimeout(function () {
              ok(titel().join('|') === 'Eins|Zwei|Drei|Vier', 'und wieder hoch: ' + titel().join('|'));

              head('Grenzen');
              zeile(0).dispatchEvent(taste('ArrowUp', true));
              setTimeout(function () {
                zeile(3).dispatchEvent(taste('ArrowDown', true));
                setTimeout(function () {
                  ok(titel().join('|') === 'Eins|Zwei|Drei|Vier', 'am Anfang und Ende bleibt alles stehen: ' + titel().join('|'));
                  ok(gespeichert().join('|') === 'Eins|Zwei|Drei|Vier', 'und nichts wird gespeichert');

                  head('Pfeil ohne Alt');
                  zeile(0).dispatchEvent(taste('ArrowDown', false));
                  setTimeout(function () {
                    ok(titel().join('|') === 'Eins|Zwei|Drei|Vier', 'Reihenfolge bleibt: ' + titel().join('|'));

                    head('Ziehen: oberhalb einfuegen');
                    var v1 = titel();
                    ziehe(grips()[3], zeile(1), oben(zeile(1)));
                    setTimeout(function () {
                      var s1 = erwartet(v1, 3, 1);
                      ok(titel().join('|') === s1, 'Vier vor die zweite Zeile: ' + titel().join('|'));
                      ok(gespeichert().join('|') === s1, 'gespeichert: ' + gespeichert().join('|'));

                      head('Ziehen: unterhalb einfuegen');
                      var v2 = titel();
                      ziehe(grips()[0], zeile(3), unten(zeile(3)));
                      setTimeout(function () {
                        ok(titel().join('|') === erwartet(v2, 0, 4), 'erste Seite ans Ende: ' + titel().join('|'));
                        ok(titel()[3] === v2[0], 'und zwar als letzte: ' + titel().join('|'));

                        head('Ziehen stoert den Rest nicht');
                        ok(q('.content-title').textContent.trim() === 'Eins', 'geoeffnete Seite unveraendert: ' + q('.content-title').textContent.trim());
                        ok(q('.toc-menu').classList.contains('offen'), 'Verzeichnis bleibt da');

                        head('Anzeige waehrend des Ziehens');
                        var d = new DataTransfer();
                        grips()[0].dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d }));
                        setTimeout(function () {
                          ok(!!q('.toc-item.wird-gezogen'), 'gezogene Zeile wird blasser');
                          zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d, clientY: oben(zeile(2)) }));
                          setTimeout(function () {
                            ok(!!q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-kind'), 'Zeiger oben: Linie davor');
                            grips()[0].dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d }));
                            setTimeout(function () {
                              var d2 = new DataTransfer();
                              grips()[1].dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: d2 }));
                              setTimeout(function () {
                                zeile(2).dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: d2, clientY: unten(zeile(2)) }));
                                setTimeout(function () {
                                  ok(!!q('.toc-item.einfuegen-unten') && !q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-kind'), 'Zeiger unten: Linie dahinter');
                                  grips()[1].dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: d2 }));
                                  setTimeout(function () {
                                    ok(!q('.toc-item.wird-gezogen') && !q('.toc-item.einfuegen-oben') && !q('.toc-item.einfuegen-unten'), 'nach dem Ziehen ist alles weg');
                                    log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                    out();
                                  }, 300);
                                }, 300);
                              }, 300);
                            }, 300);
                          }, 300);
                        }, 300);
                      }, 400);
                    }, 400);
                  }, 400);
                }, 400);
              }, 400);
            }, 400);
          }, 400);
        }, 700);
      }, 1300);
    })();
    </script>
"""



# Beim Suchen darf sich nichts verschieben lassen.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function gespeichert() { return JSON.parse(localStorage.getItem('simplewiki_pages')).map(function (p) { return p.title; }); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        setTimeout(function () {
          var suche = q('.search-box');
          suche.value = 'dr';            /* trifft nur "Drei" */
          suche.dispatchEvent(new Event('input', { bubbles: true }));
          setTimeout(function () {
            var vorher = gespeichert().join('|');
            ok(titel().join('|') === 'Drei', 'gefiltert: ' + titel().join('|'));
            ok(all('.toc-menu .toc-grip')[0].getAttribute('draggable') === 'false', 'Griff ist gesperrt');
            ok(all('.toc-menu .toc-grip')[0].className.indexOf('ist-ruhig') >= 0, 'Griff sieht gesperrt aus');
            ok(all('.toc-menu .toc-grip')[0].getAttribute('title').indexOf('Suche') >= 0,
               'am Griff nennt er die Suche: ' + all('.toc-menu .toc-grip')[0].getAttribute('title'));
            all('.toc-menu .toc-item')[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', altKey: true, bubbles: true, cancelable: true }));
            all('.toc-menu .toc-item')[0].dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: new DataTransfer() }));
            setTimeout(function () {
              ok(gespeichert().join('|') === vorher, 'Reihenfolge unveraendert: ' + gespeichert().join('|'));
              suche.value = '';
              suche.dispatchEvent(new Event('input', { bubbles: true }));
              setTimeout(function () {
                ok(all('.toc-menu .toc-grip')[0].getAttribute('draggable') === 'true', 'nach dem Leeren wieder ziehbar');
                ok(titel().length === 4, 'alle Zeilen wieder da: ' + titel().join('|'));
                log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                out();
              }, 400);
            }, 400);
          }, 600);
        }, 700);
      }, 1300);
    })();
    </script>
"""

pruefe(
    build('_ord1.html', script, pages),
    build('_ord2.html', script2, pages)
)
