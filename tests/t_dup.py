import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nInhalt mit *Betonung*", "links": ["Beta"], "tags": ["wichtig"], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": ["Alpha (Kopie)"], "tags": [], "created": "x", "updated": "x"},
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
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      function seite(t) { return speicher().filter(function (p) { return p.title === t; })[0]; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Anker');
        ok(q('.content-title').textContent.trim() === 'Alpha', 'Startseite: ' + q('.content-title').textContent.trim());

        head('Knopf');
        btn(/Bearbeiten/).click();
        setTimeout(function () {
          var d = btn(/Duplizieren/);
          ok(!!d, 'Knopf "Duplizieren" im Bearbeitungsmodus vorhanden');
          ok(!!d && !!d.title, 'Knopf hat einen Hinweis als title');
          d.click();
          setTimeout(function () {
            var alle = speicher();
            var k = seite('Alpha (Kopie)');
            ok(alle.length === 3, 'eine Seite mehr: ' + alle.length);
            ok(!!k, 'Kopie existiert mit kenntlichgemachtem Namen');
            ok(!!k && k.content === '# Alpha\n\nInhalt mit *Betonung*', 'Inhalt uebernommen');
            ok(!!k && JSON.stringify(k.links) === '["Beta"]', 'Verknuepfungen uebernommen: ' + (k ? JSON.stringify(k.links) : '-'));
            ok(!!k && JSON.stringify(k.tags) === '["wichtig"]', 'Schlagworte uebernommen');
            ok(!!k && k.id !== 'a', 'eigene Kennung: ' + (k ? k.id : '-'));
            ok(q('.content-title').textContent.trim() === 'Alpha (Kopie)', 'Kopie ist die angezeigte Seite: ' + q('.content-title').textContent.trim());
            ok(!q('.md-host'), 'Editor verlassen, Anzeigemodus');

            head('Die Kopie ist eine vollwertige Seite');
            var m2 = (function () { var b = q('.menu-badge'); return b ? b.textContent.trim() : ''; })();
            ok(m2 === '2', 'Kopie hat einen Aus- und einenRueckverweis: ' + m2);
            ok(!q('.refs-item-fehlt'), 'alle Ziele der Kopie vorhanden, nichts rot');

            head('Die Vorlage bleibt unberuehrt');
            var a = seite('Alpha');
            ok(!!a && a.content === '# Alpha\n\nInhalt mit *Betonung*', 'Inhalt unveraendert');
            ok(!!a && JSON.stringify(a.links) === '["Beta"]', 'Verknuepfungen unveraendert');
            ok(!!a && a.title === 'Alpha', 'Titel unveraendert');
            ok(speicher()[0].title === 'Alpha (Kopie)', 'Kopie steht in der Liste vorn');

            head('Zweite Kopie: Nummerierung');
            btn(/Bearbeiten/).click();
            setTimeout(function () {
              btn(/Duplizieren/).click();
              setTimeout(function () {
                ok(!!seite('Alpha (Kopie 2)'), 'zweiter Name ist eindeutig: ' + speicher().map(function (p) { return p.title; }).join(' | '));
                ok(speicher().length === 4, 'Seiten: ' + speicher().length);
                ok(q('.content-title').textContent.trim() === 'Alpha (Kopie 2)', 'zeigt die zweite Kopie');

                head('Eigenstaendige Verknuepfungen');
                btn(/Bearbeiten/).click();
                setTimeout(function () {
                  btn(/Verlinken/).click();
                  setTimeout(function () {
                    all('.link-item').filter(function (b) { return /Beta/.test(b.textContent); })[0].click();
                    setTimeout(function () {
                      ok(JSON.stringify(seite('Alpha (Kopie 2)').links) === '[]', 'Verknuepfung der Kopie geloest');
                      ok(JSON.stringify(seite('Alpha').links) === '["Beta"]', 'Vorlage haelt ihre Verknuepfung');
                      ok(JSON.stringify(seite('Alpha (Kopie)').links) === '["Beta"]', 'erste Kopie ebenfalls unberuehrt');
                      btn(/Abbrechen/).click();
                      setTimeout(function () {
                        head('Bedienung der Kopie');
                        q('.menu-toggle').click();
                        setTimeout(function () {
                          all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Alpha (Kopie)'; })[0].click();
                          setTimeout(function () {
                            ok(q('.content-title').textContent.trim() === 'Alpha (Kopie)', 'Kopie ueber das Inhaltsverzeichnis erreichbar');
                            q('.refs-toggle').click();
                            setTimeout(function () {
                            var zurueck = all('.refs-item').filter(function (b) { return /Beta/.test(b.textContent); })[0];
                            ok(!!zurueck, 'Rueckverweis auf Beta im Panel');
                            zurueck.click();
                            }, 600);
                            setTimeout(function () {
                              ok(q('.content-title').textContent.trim() === 'Beta', 'Rueckverweis fuehrt zu Beta: ' + q('.content-title').textContent.trim());
                              q('.refs-toggle').click();
                              setTimeout(function () {
                                var inhalt = q('.refs-body').textContent.replace(/\s+/g, ' ').trim();
                                ok(inhalt.indexOf('Alpha') >= 0 && inhalt.indexOf('Verlinkt') >= 0, 'Panel zeigt die Verweise der Kopie: ' + inhalt.slice(0, 70));
                                log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                                out();
                              }, 500);
                            }, 1400);
                          }, 600);
                        }, 600);
                      }, 400);
                    }, 500);
                  }, 600);
                }, 2200);
              }, 700);
            }, 2200);
          }, 900);
        }, 2200);
      }, 1200);
    })();
    </script>
"""

pruefe(
    build('_dup1.html', script, pages)
)
