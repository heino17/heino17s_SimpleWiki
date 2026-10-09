import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

# Alpha traegt zwei Schlagworte, Beta eines, Gamma keines. Ein Schlagwort
# steht an der Seite, nicht im Text - der Verweisgraph bleibt davon
# unberuehrt.
pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": ["Mathe", "Physik"], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": ["Mathe"], "created": "x", "updated": "x"},
    {"id": "g", "title": "Gamma", "content": "# Gamma", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "d", "title": "Delta", "content": "# Delta", "links": [], "tags": ["Sport"], "created": "x", "updated": "x"},
]

# Erster Lauf: Pillen an der Seite, Register, Bearbeiten mit Aufnehmen und
# Entfernen, und was davon im Speicher ankommt.
script = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function texte(sel) { return all(sel).map(function (e) { return e.textContent.replace(/[×\s]+/g, ' ').trim(); }); }
      function zuSeite(titel, dann) {
        all('.toc-item-title').filter(function (t) { return t.textContent.trim() === titel; })[0].click();
        setTimeout(dann, 600);
      }
      function pilleMit(sel, name) {
        return all(sel).filter(function (p) { return p.textContent.replace(/[×\s]/g, '') === name; })[0];
      }
      function speicherSeite(titel) {
        return JSON.parse(localStorage.getItem('simplewiki_pages')).filter(function (p) { return p.title === titel; })[0];
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Ansicht: Pillen unter dem Titel');
        zuSeite('Alpha', function () {
          ok(q('.content-title').textContent.trim() === 'Alpha', 'Alpha offen');
          var pillen = texte('.tags-row .tag-pill');
          ok(pillen.length === 2, 'zwei Schlagworte: ' + pillen.join(' | '));
          ok(pillen.indexOf('Mathe') >= 0 && pillen.indexOf('Physik') >= 0, 'die Namen stimmen');
          ok(all('.tags-row .tag-pill')[0].tagName === 'BUTTON', 'die Pille ist anklickbar');

          head('Register');
          all('.tags-row .tag-pill').filter(function (p) { return p.textContent.trim() === 'Mathe'; })[0].click();
          setTimeout(function () {
            ok(!!q('.modal-tag'), 'Register offen');
            ok(q('.modal-tag h3').textContent.trim() === 'Seiten mit Schlagwort', 'Titel: ' + q('.modal-tag h3').textContent.trim());
            ok(q('.modal-tag .refs-current').textContent.trim() === 'Mathe', 'Schlagwort: ' + q('.modal-tag .refs-current').textContent.trim());
            ok(/2 Seiten/.test(q('.tag-dialog-count').textContent), 'Zahl: ' + q('.tag-dialog-count').textContent.replace(/\s+/g, ' ').trim());
            var namen = texte('.modal-tag .link-item-titel');
            ok(namen.length === 2 && namen.indexOf('Alpha') >= 0 && namen.indexOf('Beta') >= 0, 'beide Seiten: ' + namen.join(' | '));
            ok(namen.indexOf('Gamma') < 0, 'Gamma ohne das Schlagwort fehlt');

            head('Klick im Register fuehrt zur Seite');
            all('.modal-tag .link-item').filter(function (b) { return b.textContent.trim() === 'Beta'; })[0].click();
            setTimeout(function () {
              ok(!q('.modal-tag'), 'Register wieder zu');
              ok(q('.content-title').textContent.trim() === 'Beta', 'Beta offen: ' + q('.content-title').textContent.trim());

              head('Bearbeiten: vorhandenes Schlagwort im Feld');
              q('.footer .btn-primary').click();
              setTimeout(function () {
                ok(!!q('.tags-editor'), 'Schlagwort-Zeile im Editor');
                ok(texte('.tags-editor .tag-pill').join('|') === 'Mathe', 'vorhandenes Schlagwort: ' + texte('.tags-editor .tag-pill').join(' | '));

                head('Ein Schlagwort aufnehmen');
                var feld = q('.tag-input');
                feld.value = 'Neu';
                feld.dispatchEvent(new Event('input', { bubbles: true }));
                feld.dispatchEvent(new Event('blur'));
                setTimeout(function () {
                  var namen = texte('.tags-editor .tag-pill');
                  ok(namen.length === 2 && namen.indexOf('Neu') >= 0, 'Neu aufgenommen: ' + namen.join(' | '));

                  head('Ein Schlagwort entfernen');
                  var mathe = pilleMit('.tags-editor .tag-pill', 'Mathe');
                  ok(!!mathe, 'Mathe-Pille gefunden');
                  mathe.querySelector('.tag-pill-x').click();
                  setTimeout(function () {
                    ok(texte('.tags-editor .tag-pill').indexOf('Mathe') < 0, 'Mathe entfernt: ' + texte('.tags-editor .tag-pill').join(' | '));

                    head('Sichern');
                    q('.footer .btn-primary').click();
                    setTimeout(function () {
                      var seite = speicherSeite('Beta');
                      ok(!!seite, 'Beta steht im Speicher');
                      ok(seite.tags.indexOf('Neu') >= 0, 'Neu gespeichert: ' + seite.tags.join(', '));
                      ok(seite.tags.indexOf('Mathe') < 0, 'Mathe nicht mehr da');
                      ok(!!q('.tags-row') && texte('.tags-row .tag-pill').indexOf('Neu') >= 0, 'Ansicht zeigt die neuen Schlagworte');
                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                      out();
                    }, 500);
                  }, 300);
                }, 300);
              }, 700);
            }, 500);
          }, 500);
        });
      }, 1200);
    })();
    </script>
"""

# Zweiter Lauf: ein Schlagwort mit eckigen Klammern wird abgelehnt, statt
# still zu verschwinden - die Klammern sind das Listenformat selbst.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function texte(sel) { return all(sel).map(function (e) { return e.textContent.replace(/[×\s]+/g, ' ').trim(); }); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Gamma'; })[0].click();
        setTimeout(function () {
          head('Bearbeiten ohne Schlagworte');
          q('.footer .btn-primary').click();
          setTimeout(function () {
            ok(texte('.tags-editor .tag-pill').length === 0, 'keine Pille am Anfang');
            var feld = q('.tag-input');
            feld.value = 'a[b';
            feld.dispatchEvent(new Event('input', { bubbles: true }));
            feld.dispatchEvent(new Event('blur'));
            setTimeout(function () {
              ok(texte('.tags-editor .tag-pill').length === 0, 'das kaputte Schlagwort wird nicht aufgenommen');
              ok(!!q('.hinweis') && q('.hinweis').textContent.indexOf(']') >= 0, 'und der Grund wird gesagt: ' + (q('.hinweis') ? q('.hinweis').textContent.replace(/\s+/g, ' ').trim().slice(0, 40) + '...' : '(kein Hinweis)'));

              head('Mehrere auf einmal, durch Komma getrennt');
              feld = q('.tag-input');
              feld.value = 'eins, zwei';
              feld.dispatchEvent(new Event('input', { bubbles: true }));
              feld.dispatchEvent(new Event('blur'));
              setTimeout(function () {
                var namen = texte('.tags-editor .tag-pill');
                ok(namen.length === 2 && namen.indexOf('eins') >= 0 && namen.indexOf('zwei') >= 0, 'beide aufgenommen: ' + namen.join(' | '));
                log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                out();
              }, 300);
            }, 300);
          }, 700);
        }, 600);
      }, 1200);
    })();
    </script>
"""

# Dritter Lauf: dieselbe Sache in englischer Oberflaeche.
script3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Alpha'; })[0].click();
        setTimeout(function () {
          all('.tags-row .tag-pill').filter(function (p) { return p.textContent.trim() === 'Mathe'; })[0].click();
          setTimeout(function () {
            ok(q('.modal-tag h3').textContent.trim() === 'Pages with tag', 'Titel: ' + q('.modal-tag h3').textContent.trim());
            ok(/2 pages/.test(q('.tag-dialog-count').textContent), 'Zahl: ' + q('.tag-dialog-count').textContent.replace(/\s+/g, ' ').trim());
            ok(/river/i.test(q('.modal-tag .btn-primary').textContent), 'Fluss-Knopf: ' + q('.modal-tag .btn-primary').textContent.replace(/\s+/g, ' ').trim());
            log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 500);
        }, 600);
      }, 1200);
    })();
    </script>
"""

# Vierter Lauf: die Vorschlagsliste am Feld. Beta traegt Mathe, im Wiki
# gibt es ausserdem Physik und Sport - die stehen zur Auswahl, Mathe
# nicht mehr, weil die Seite es schon traegt.
script4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function vorschlaege() { return all('.tag-vorschlaege .tag-vorschlag').map(function (e) { return e.textContent.trim(); }); }
      function taste(feld, key) { feld.dispatchEvent(new KeyboardEvent('keydown', { key: key, bubbles: true, cancelable: true })); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Beta'; })[0].click();
        setTimeout(function () {
          q('.footer .btn-primary').click();
          setTimeout(function () {
            head('Fokus ins Feld zeigt die vorhandenen Schlagworte');
            ok(!q('.tag-vorschlaege'), 'die Liste ist vor dem Fokus zu');
            var feld = q('.tag-input');
            feld.focus();
            setTimeout(function () {
              ok(!!q('.tag-vorschlaege'), 'die Liste ist offen');
              ok(vorschlaege().join(' | ') === 'Physik | Sport', 'was fehlt, steht zur Wahl: ' + vorschlaege().join(' | '));
              ok(vorschlaege().indexOf('Mathe') < 0, 'die Seite hat Mathe schon, es fehlt in der Liste');

              head('Tippen schraenkt ein');
              feld.value = 'Sp';
              feld.dispatchEvent(new Event('input', { bubbles: true }));
              setTimeout(function () {
                ok(vorschlaege().join(' | ') === 'Sport', 'nur der Treffer bleibt: ' + vorschlaege().join(' | '));

                head('Anklicken nimmt auf und laesst die Liste offen');
                all('.tag-vorschlaege .tag-vorschlag')[0].dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
                setTimeout(function () {
                  ok(all('.tags-editor .tag-pill').map(function (e) { return e.textContent.replace(/[×\s]+/g, ' ').trim(); }).indexOf('Sport') >= 0, 'Sport ist aufgenommen');
                  ok(document.activeElement === q('.tag-input'), 'der Fokus blieb im Feld');
                  ok(vorschlaege().join(' | ') === 'Physik', 'die gewaehlte fehlt jetzt in der Liste: ' + vorschlaege().join(' | '));

                  head('Pfeil und Enter waehlen auch');
                  feld = q('.tag-input');
                  taste(feld, 'ArrowDown');
                  setTimeout(function () {
                    ok(q('.tag-vorschlag-aktiv') && q('.tag-vorschlag-aktiv').textContent.trim() === 'Physik', 'der Pfeil markiert: ' + (q('.tag-vorschlag-aktiv') ? q('.tag-vorschlag-aktiv').textContent.trim() : '(nichts)'));
                    taste(feld, 'Enter');
                    setTimeout(function () {
                      var namen = all('.tags-editor .tag-pill').map(function (e) { return e.textContent.replace(/[×\s]+/g, ' ').trim(); });
                      ok(namen.indexOf('Physik') >= 0, 'Enter hat Physik genommen: ' + namen.join(' | '));
                      ok(!q('.tag-vorschlaege'), 'nichts mehr zur Wahl, die Liste ist weg');
                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                      out();
                    }, 300);
                  }, 200);
                }, 300);
              }, 300);
            }, 300);
          }, 700);
        }, 600);
      }, 1200);
    })();
    </script>
"""

# Fuenfter Lauf: aus dem Register in den Fluss - alle Seiten mit dem
# Schlagwort hintereinander, danach der Schlagwort-Filter im Fluss-Kopf
# als Auswahlliste: ein anderes nehmen, auf "alle" zurueckstellen, und
# ueber den Fluss-Knopf die ganze Wiki.
script5 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function titel() { return all('.fluss-eintrag-titel .fluss-titel-knopf').map(function (e) { return e.textContent.trim(); }); }
      function zahl() { return q('.fluss-zahl') ? q('.fluss-zahl').textContent.replace(/\s+/g, ' ').trim() : '(keine)'; }
      function tagPille(name) { return all('.tags-row .tag-pill').filter(function (p) { return p.textContent.trim() === name; })[0]; }
      function waehle(sel, wert) { sel.value = wert; sel.dispatchEvent(new Event('change', { bubbles: true })); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Alpha'; })[0].click();
        setTimeout(function () {
          tagPille('Mathe').click();
          setTimeout(function () {
            head('Aus dem Register in den Fluss');
            var knopf = q('.modal-tag .btn-primary');
            ok(!!knopf && /Fluss/.test(knopf.textContent), 'der Knopf steht im Register: ' + (knopf ? knopf.textContent.trim() : '(fehlt)'));
            knopf.click();
            setTimeout(function () {
              ok(!q('.modal-tag'), 'das Register ist zu');
              ok(!!q('.fluss'), 'der Fluss steht');
              ok(titel().join(' | ') === 'Alpha | Beta', 'nur das Schlagwort, in Reihenfolge: ' + titel().join(' | '));
              ok(document.querySelector('.footer') === null, 'die Fusszeile bleibt im Fluss weg');
              var wahl = q('.fluss-tag-filter');
              ok(!!wahl, 'die Auswahlliste steht im Fluss-Kopf');
              ok(wahl.value === 'Mathe' && wahl.options[wahl.selectedIndex].text === 'Mathe', 'sie steht auf dem Schlagwort: ' + wahl.value);
              ok(/2 Seiten mit dem Schlagwort/.test(zahl()) && /Mathe/.test(zahl()), 'die Zahl nennt Schlagwort und Seiten: ' + zahl());

              head('In der Liste auf ein anderes Schlagwort');
              waehle(wahl, 'Sport');
              setTimeout(function () {
                ok(titel().join(' | ') === 'Delta', 'nur Sport bleibt: ' + titel().join(' | '));
                ok(/1 Seite mit dem Schlagwort/.test(zahl()) && /Sport/.test(zahl()), 'die Zahl folgt der Wahl: ' + zahl());

                head('In der Liste auf "alle" zurueck');
                waehle(q('.fluss-tag-filter'), '');
                setTimeout(function () {
                  ok(titel().join(' | ') === 'Alpha | Beta | Gamma | Delta', 'alle Seiten stehen da: ' + titel().join(' | '));
                  ok(/4 Seiten hintereinander/.test(zahl()), 'die Zahl ist die ganze Wiki: ' + zahl());

                  head('Eine Seite im Fluss anklicken beendet ihn');
                  all('.fluss-titel-knopf').filter(function (b) { return b.textContent.trim() === 'Gamma'; })[0].click();
                  setTimeout(function () {
                    ok(!q('.fluss'), 'der Fluss ist zu');
                    ok(q('.content-title') && q('.content-title').textContent.trim() === 'Gamma', 'Gamma ist offen');

                    head('Der Fluss-Knopf im Kopf zeigt wieder die ganze Wiki');
                    q('.kopf-fluss').click();
                    setTimeout(function () {
                      var wahl2 = q('.fluss-tag-filter');
                      ok(!!q('.fluss') && wahl2 && wahl2.value === '', 'ganze Wiki, die Liste steht auf "alle"');
                      ok(titel().length === 4, 'alle vier Seiten: ' + titel().join(' | '));
                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                      out();
                    }, 400);
                  }, 400);
                }, 400);
              }, 400);
            }, 500);
          }, 500);
        }, 600);
      }, 1200);
    })();
    </script>
"""

kopie1 = build('_tags1.html', script, pages, startpage='a')
kopie2 = build('_tags2.html', script2, pages, startpage='a')
kopie3 = build('_tags3.html', script3, pages, lang='en', startpage='a')
kopie4 = build('_tags4.html', script4, pages, startpage='a')
kopie5 = build('_tags5.html', script5, pages, startpage='a')

pruefe(kopie1, kopie2, kopie3, kopie4, kopie5)
