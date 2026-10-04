import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

# Alpha verlinkt Beta und ein fehlendes Ziel, schreibt [[Gamma]] in den Text
# und wird von Beta zurueckverwiesen. Delta steht ganz allein.
pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nText mit [[Gamma]]", "links": ["Beta", "Fehlt"], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": ["Delta"], "tags": [], "created": "x", "updated": "x"},
    {"id": "g", "title": "Gamma", "content": "# Gamma", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "d", "title": "Delta", "content": "# Delta", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "e", "title": "Epsilon", "content": "# Epsilon", "links": [], "tags": [], "created": "x", "updated": "x"},
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
      function panelOffen() { return q('.refs-panel').classList.contains('open'); }
      function knopf() { return q('.refs-toggle'); }
      function marke() { var b = q('.menu-badge'); return b ? b.textContent.trim() : ''; }
      function eintraege() { return all('.refs-item').map(function (b) { return b.textContent.replace(/\s+/g, ' ').trim(); }); }
      function gruppen() { return all('.refs-group h3').map(function (h) { return h.textContent.replace(/\s+/g, ' ').trim(); }); }
      function zuSeite(titel, dann) {
        q('.menu-toggle').click();
        setTimeout(function () {
          all('.toc-item-title').filter(function (t) { return t.textContent.trim() === titel; })[0].click();
          setTimeout(dann, 600);
        }, 500);
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Start: Alpha');
        ok(!panelOffen(), 'Panel ist geschlossen');
        ok(!!knopf() && /Verweise/.test(knopf().title), 'Knopf mit Hinweis: ' + knopf().title);
        ok(marke() === '3', 'Zaehler zeigt alle drei Verweise: ' + marke());
        ok(!q('.backlinks') && !q('.outgoing'), 'keine Verweisabschnitte mehr in der Seite');
        ok(localStorage.getItem('simplewiki_refs') === '0', 'das Laden aendert den gespeicherten Zustand nicht: ' + localStorage.getItem('simplewiki_refs'));

        head('Oeffnen');
        knopf().click();
        setTimeout(function () {
          ok(panelOffen(), 'Panel offen');
          ok(q('.refs-panel h2').textContent.trim() === 'Verweise', 'Titel: ' + q('.refs-panel h2').textContent.trim());
          ok(q('.refs-current').textContent.trim() === 'Alpha', 'gilt fuer: ' + q('.refs-current').textContent.trim());
          ok(localStorage.getItem('simplewiki_refs') === '1', 'Zustand gespeichert: ' + localStorage.getItem('simplewiki_refs'));

          head('Menue');
          var items = eintraege();
          ok(items.length === 3, 'drei Eintraege: ' + items.join(' | '));
          ok(items.join('|').indexOf('Beta') >= 0, 'Beta verlinkt');
          ok(items.join('|').indexOf('Gamma') >= 0, '[[..]] im Text wird mitgezaehlt: ' + items.join(' | '));
          ok(items.join('|').indexOf('Fehlt') >= 0, 'fehlendes Ziel verlinkt');
          ok(items.join('|').indexOf('[[') < 0, 'keine Klammern im Namen');
          ok(all('.refs-item-fehlt').length === 1, 'genau ein fehlendes Ziel markiert');
          ok(!!q('.refs-hint-badge') && /anlegen/i.test(q('.refs-hint-badge').getAttribute('title')), 'Hinweis-Zeichen mit Text');
          ok(all('.refs-arrow').map(function (a) { return a.textContent.trim(); }).join('') === '→→→', 'Richtungspfeile zeigen nach draussen');
          ok(gruppen().join('|').indexOf('Verlinkt auf') >= 0, 'Gruppe: ' + gruppen().join(' | '));
          ok(gruppen().join('|').indexOf('Verlinkt von') < 0, 'keine leere Gruppe dabei');
          ok(q('.refs-count').textContent.trim() === '3', 'Gruppenzaehler: ' + q('.refs-count').textContent.trim());

          head('Klick im Panel');
          q('.refs-item .refs-name').click();
          setTimeout(function () {
            ok(q('.content-title').textContent.trim() === 'Beta', 'Klick folgt der Seite: ' + q('.content-title').textContent.trim());
            ok(panelOffen(), 'Panel bleibt offen – es wird nicht von allein geschlossen');
            ok(q('.refs-current').textContent.trim() === 'Beta', 'zeigt jetzt Beta');
            ok(marke() === '2', 'Beta hat beide Richtungen, Zaehler: ' + marke());
            ok(gruppen().length === 2, 'zwei Gruppen: ' + gruppen().join(' | '));
            ok(gruppen().join('|').indexOf('Verlinkt von') >= 0, 'Rueckverweis auf Alpha sichtbar');
            ok(eintraege().join('|').indexOf('←Alpha') >= 0, 'Pfeil zeigt zurueck: ' + eintraege().join(' | '));

            head('Seite ganz ohne Verweise');
            q('.refs-panel .side-close').click();
            setTimeout(function () {
              ok(!panelOffen(), 'Panel geschlossen');
              ok(localStorage.getItem('simplewiki_refs') === '0', 'Zustand gespeichert: ' + localStorage.getItem('simplewiki_refs'));
              zuSeite('Epsilon', function () {
                ok(q('.content-title').textContent.trim() === 'Epsilon', 'Epsilon geoeffnet');
                ok(marke() === '', 'kein Zaehler ohne Verweise');
                knopf().click();
                setTimeout(function () {
                  ok(panelOffen(), 'Panel offen');
                  ok(!!q('.refs-empty'), 'Hinweis statt Menu');
                  ok(q('.refs-empty').textContent.indexOf('Keine Verweise') >= 0, 'Text: ' + q('.refs-empty').textContent.replace(/\s+/g, ' ').trim().slice(0, 32) + '...');
                  ok(q('.refs-empty').textContent.indexOf('[[Seitenname]]') >= 0, 'nennt beide Wege zum Verlinken');

                  head('Gegenseitigkeit');
                  q('.menu-toggle').click();
                  setTimeout(function () {
                    ok(!panelOffen() && q('.toc-panel').classList.contains('open'), 'Inhaltsverzeichnis schliesst das Verweis-Panel');
                    knopf().click();
                    setTimeout(function () {
                      ok(panelOffen() && !q('.toc-panel').classList.contains('open'), 'Verweis-Panel schliesst das Inhaltsverzeichnis');
                      log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                      out();
                    }, 500);
                  }, 500);
                }, 500);
              });
            }, 500);
          }, 500);
        }, 500);
      }, 1200);
    })();
    </script>
"""



# Zweiter Lauf: gespeicherter Zustand "offen" muss nach dem Neuladen gelten.
# Der Zustand wird unten beim Bauen der Kopie gesetzt.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      setTimeout(function () {
        ok(q('.refs-panel').classList.contains('open'), 'Panel ist nach dem Neuladen wieder offen');
        ok(q('.refs-panel h2').textContent.trim() === 'Verweise', 'Titel stimmt');
        q('.refs-panel .side-close').click();
        setTimeout(function () {
          ok(!q('.refs-panel').classList.contains('open'), 'Schliessen wirkt');
          ok(localStorage.getItem('simplewiki_refs') === '0', 'und wird gespeichert');
          log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 400);
      }, 1400);
    })();
    </script>
"""


# Dritter Lauf: Klick auf ein fehlendes Ziel legt die Seite an.
script3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        q('.refs-toggle').click();
        setTimeout(function () {
          q('.refs-item-fehlt').click();
          setTimeout(function () {
            ok(!!speicher().filter(function (p) { return p.title === 'Fehlt'; })[0], 'fehlendes Ziel wurde angelegt');
            ok(!!q('.md-host'), 'ist gleich im Bearbeitungsmodus');
            ok(q('.title-editor').value === 'Fehlt', 'Titel im Eingabefeld: ' + q('.title-editor').value);
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 2600);
        }, 500);
      }, 1200);
    })();
    </script>
"""

# Reihenfolge wichtig: die zweite und dritte Kopie bekommen einen
# anderen Startzustand. Deshalb einzeln bauen, nicht in einem Aufruf.
kopie1 = build('_refs1.html', script, pages, startpage='a')

mkcopy.PRE_SCRIPT = "<script>try{localStorage.setItem('simplewiki_refs','1');}catch(e){}</script>"
kopie2 = build('_refs2.html', script2, pages, startpage='a')
kopie3 = build('_refs3.html', script3, pages, startpage='a')

pruefe(kopie1, kopie2, kopie3)
