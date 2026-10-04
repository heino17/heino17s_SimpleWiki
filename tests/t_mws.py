import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe

# Ausgangs-Wiki im Browser
seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "2026-01-01T10:00:00.000Z", "updated": "2026-01-01T10:00:00.000Z"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "2026-01-01T10:00:00.000Z", "updated": "2026-01-01T10:00:00.000Z"},
]

# Datei, wie ein fremdes Werkzeug sie schreibt:
# unbekannte Felder, Verweise nur im Text, englisch, dunkel, eigene Startseite
MWS = {
    "version": 1,
    "seiten": [
        {"id": "m1", "title": "Von MWS", "content": "# Von MWS\n\nSiehe [[Alpha]] und [[Beta]].",
         "links": [], "tags": ["extern"], "created": "2026-02-02T08:00:00.000Z",
         "updated": "2026-02-02T09:00:00.000Z",
         "mwsId": 4711, "mwsEigenschaften": {"fach": "Rezept", "pruefer": "ok"}},
        {"id": "m2", "title": "Alpha", "content": "# Alpha\n\ngibt es auch in MWS",
         "links": [], "tags": [], "created": "2026-02-02T08:00:00.000Z", "updated": "2026-02-02T08:00:00.000Z"},
        {"id": "m3", "title": "Beta", "content": "# Beta", "links": [], "tags": [],
         "created": "2026-02-02T08:00:00.000Z", "updated": "2026-02-02T08:00:00.000Z"},
        {"id": "m4", "title": "Zweite Seite", "content": "# Zweite\n\nText", "links": ["Von MWS"],
         "tags": [], "created": "2026-02-02T08:00:00.000Z", "updated": "2026-02-02T08:00:00.000Z"},
    ],
    "startseite": "m4",
    "sprache": "en",
    "thema": "dark",
}

# ---------------------------------------------------------------- Teil 1
# JSON einlesen: Felder, Reihenfolge, Einstellungen, Verweise, Knopfzustand
script1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      /* Knopf im Bereich Wiki-Daten nach Text suchen, statt nach Nummer:
         ein weiterer Knopf soll einen Test nicht umhauen. */
      function knopf(muster) {
        return [].slice.call(document.querySelectorAll('.settings-btn'))
                .filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      /* Nach dem Einlesen erst weiterlaufen, wenn ein neuer Hinweis
         erschienen ist. Das Einlesen braucht unter Virtual Time
         zwischen einer und drei Sekunden - eine feste Wartezeit ist
         hier Lotterie. */
      function lade(text, dann, name) {
        var vorher = hinweisLog.length;
        var feld = q('input.datei-feld');
        var dt = new DataTransfer();
        dt.items.add(new File([text], name || 'daten.json', { type: 'application/json' }));
        feld.files = dt.files;
        feld.dispatchEvent(new Event('change', { bubbles: true }));
        var versuche = 0;
        (function warten() {
          versuche++;
          if (hinweisLog.length > vorher || versuche > 60) {
            setTimeout(dann, 400);
            return;
          }
          setTimeout(warten, 200);
        })();
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      /* Alle Hinweise notieren: sie verschwinden nach sechs Sekunden
         von selbst. */
      var hinweisLog = [];
      new MutationObserver(function () {
        var h = q('.hinweis');
        if (h) {
          var t = h.textContent.trim();
          if (t && hinweisLog[hinweisLog.length - 1] !== t) hinweisLog.push(t);
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          var knoepfe = all('.settings-btn').map(function (b) { return b.textContent.trim(); });
          head('Einstellungen');
          ok(!!knopf('JSON'), 'JSON-Knopf vorhanden');
          ok(!!knopf('Als Datei sichern|Save as file'), 'sichern vorhanden');
          ok(!!knopf('Datei laden|Load file'), 'laden vorhanden');
          ok(!!knopf('Leeres Wiki|Export empty'), 'leeres Wiki vorhanden');
          ok(knoepfe.length >= 4, 'Knöpfe im Bereich: ' + knoepfe.join(' / '));
          ok(q('input.datei-feld').getAttribute('accept').indexOf('.json') >= 0,
             'Dateiauswahl nimmt JSON an: ' + q('input.datei-feld').getAttribute('accept'));

          head('JSON einlesen');
          lade(window.__MWS, function () {
            var s = speicher();
            ok(s.length === 4, 'vier Seiten uebernommen: ' + s.length);
            ok(titel().join('|') === 'Von MWS|Alpha|Beta|Zweite Seite', 'Reihenfolge aus der Datei: ' + titel().join('|'));
            ok(hinweisLog.join(' | ').indexOf('4') >= 0, 'Hinweis: ' + (hinweisLog.join(' | ') || 'KEINER'));

            head('Fremde Felder bleiben erhalten');
            var erste = s.filter(function (p) { return p.title === 'Von MWS'; })[0] || {};
            ok(erste.mwsId === 4711, 'einfaches Feld: ' + erste.mwsId);
            ok(erste.mwsEigenschaften && erste.mwsEigenschaften.fach === 'Rezept',
               'verschachteltes Feld: ' + JSON.stringify(erste.mwsEigenschaften));
            ok(erste.tags && erste.tags[0] === 'extern', 'Schlagworte: ' + JSON.stringify(erste.tags));
            ok(erste.created === '2026-02-02T08:00:00.000Z', 'Zeitstempel unveraendert: ' + erste.created);

            head('Verweise aus dem Text ergaenzt');
            ok(JSON.stringify(erste.links) === '["Alpha","Beta"]', 'links aus [[..]]: ' + JSON.stringify(erste.links));

            head('Startseite, Sprache und Farbe werden immer uebernommen');
            ok(q('.content-title').textContent.trim() === 'Zweite Seite',
               'Startseite aus der Datei: ' + q('.content-title').textContent.trim());
            ok(document.body.className.indexOf('dark') >= 0, 'dunkel uebernommen');
            ok(q('.settings-toggle').getAttribute('title') === 'Settings',
               'englisch uebernommen: ' + q('.settings-toggle').getAttribute('title'));

            head('Knopfzustand stimmt jetzt');
            q('.menu-toggle').click();
            setTimeout(function () {
              all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Von MWS'; })[0].click();
              setTimeout(function () {
                all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
                setTimeout(function () {
                  all('.footer .btn').filter(function (b) { return /Verlinken|Link/.test(b.textContent); })[0].click();
                  setTimeout(function () {
                    var zeilen = all('.link-item').map(function (b) {
                      return (b.className.indexOf('link-item-aktiv') >= 0 ? '+' : '-') +
                        b.textContent.split('\u2713').join('').replace(/\s+/g, ' ').trim();
                    });
                    ok(!!q('.modal-link'), 'Dialog offen');
                    ok(zeilen.indexOf('+Alpha') >= 0, 'Alpha als verlinkt markiert: ' + zeilen.join(' | '));
                    ok(zeilen.indexOf('+Beta') >= 0, 'Beta als verlinkt markiert: ' + zeilen.join(' | '));
                    var knopf = all('.modal button').filter(function (b) { return /Abbrechen|Cancel/.test(b.textContent); })[0];
                    if (knopf) knopf.click();
                    setTimeout(ende, 500);
                  }, 1200);
                }, 3000);
              }, 900);
            }, 900);
          }, 'mws.json');
        }, 800);
      }, 1500);
    })();
    </script>
"""
kopie1 = build('_mws1.html',
               '<script>window.__MWS = ' + json.dumps(json.dumps(MWS, ensure_ascii=False)) + ';</script>' + script1,
               seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Ablehnungen und doppelte Titel
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      /* Knopf im Bereich Wiki-Daten nach Text suchen, statt nach Nummer:
         ein weiterer Knopf soll einen Test nicht umhauen. */
      function knopf(muster) {
        return [].slice.call(document.querySelectorAll('.settings-btn'))
                .filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function hinweis() { var h = q('.hinweis'); return h ? h.textContent.trim() : ''; }
      /* Nach dem Einlesen erst weiterlaufen, wenn der Hinweis sich
         geaendert hat - sonst prueft man den Hinweis des Schritts
         davor. */
      function lade(text, dann, name) {
        var vorher = hinweis();
        var feld = q('input.datei-feld');
        var dt = new DataTransfer();
        dt.items.add(new File([text], name || 'x.json', { type: 'application/json' }));
        feld.files = dt.files;
        feld.dispatchEvent(new Event('change', { bubbles: true }));
        var versuche = 0;
        (function warten() {
          versuche++;
          if ((hinweis() && hinweis() !== vorher) || versuche > 40) {
            setTimeout(dann, 300);
            return;
          }
          setTimeout(warten, 200);
        })();
      }
      function neueSeite() {
        q('.menu-toggle').click();
        setTimeout(function () {
          all('.new-page-btn').filter(function (b) { return /Neue Seite|New Page/.test(b.textContent); })[0].click();
        }, 700);
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        var vorher = titel().join('|');
        q('.settings-toggle').click();
        setTimeout(function () {
          head('Version zu neu');
          lade(JSON.stringify({ version: 2, seiten: [{ id: 'z', title: 'Zukunft', content: 'x', links: [], tags: [], created: '', updated: '' }], startseite: 'z' }), function () {
            ok(titel().join('|') === vorher, 'nichts uebernommen: ' + titel().join('|'));
            ok(hinweis().indexOf('2') >= 0 && hinweis().indexOf('1') >= 0, 'nennt beide Versionen: ' + hinweis());
            ok(hinweis().indexOf('nichts') >= 0, 'sagt, dass nichts uebernommen wurde');

            head('Version fehlt');
            lade(JSON.stringify({ seiten: [{ id: 'z', title: 'Ohne Version', content: 'x', links: [], tags: [], created: '', updated: '' }] }), function () {
              ok(titel().join('|') === vorher, 'nichts uebernommen: ' + titel().join('|'));
              ok(hinweis().toLowerCase().indexOf('version') >= 0, 'nennt die Version als Grund: ' + hinweis());

              head('Version unbrauchbar');
              lade(JSON.stringify({ version: 'erste', seiten: [{ id: 'z', title: 'X', content: 'x', links: [], tags: [], created: '', updated: '' }] }), function () {
                ok(titel().join('|') === vorher, 'nichts uebernommen: ' + titel().join('|'));
                ok(hinweis().indexOf('erste') >= 0, 'nennt die schlechte Version: ' + hinweis());

                head('Leeres Seiten-Array');
                lade(JSON.stringify({ version: 1, seiten: [] }), function () {
                  ok(titel().join('|') === vorher, 'nichts ersetzt: ' + titel().join('|'));
                  ok(hinweis().indexOf('keine Seiten') >= 0, 'Grund: ' + hinweis());

                  head('Fremde Datei');
                  lade('irgendwas anderes', function () {
                    ok(titel().join('|') === vorher, 'nichts ersetzt: ' + titel().join('|'));
                    ok(hinweis().length > 0, 'Hinweis: ' + hinweis());

                    head('Kaputtes JSON');
                    lade('{"version": 1, "seiten": [', function () {
                      ok(titel().join('|') === vorher, 'nichts ersetzt: ' + titel().join('|'));

                      head('Doppelte Titel beim Anlegen');
                      neueSeite();
                      setTimeout(function () {
                        ok(speicher()[0].title === 'Neue Seite', 'erste neue Seite heisst ' + speicher()[0].title);
                        neueSeite();
                        setTimeout(function () {
                          ok(speicher()[0].title === 'Neue Seite 2', 'zweite heisst ' + speicher()[0].title);
                          var alle = speicher().map(function (p) { return p.title; });
                          ok(alle.join('|').split('|').filter(function (x, i, a) { return a.indexOf(x) === i; }).length === alle.length,
                             'keine doppelten Namen: ' + alle.join('|'));

                          head('Doppelter Titel beim Speichern');
                          q('.menu-toggle').click();
                          setTimeout(function () {
                            all('.toc-item-title').filter(function (t) { return t.textContent.trim() === 'Beta'; })[0].click();
                            setTimeout(function () {
                              all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
                              setTimeout(function () {
                                q('.title-editor').value = 'Alpha';
                                q('.title-editor').dispatchEvent(new Event('input', { bubbles: true }));
                                setTimeout(function () {
                                  all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0].click();
                                  setTimeout(function () {
                                    var namen = speicher().map(function (p) { return p.title; });
                                    ok(namen.filter(function (t) { return t === 'Alpha'; }).length === 1, 'kein doppeltes Alpha: ' + namen.join('|'));
                                    ok(hinweis().indexOf('Alpha') >= 0, 'Hinweis nennt den Namen: ' + hinweis());
                                    ok(!!q('.md-host') || !!q('.editor'), 'bleibt im Bearbeitungsmodus');
                                    ende();
                                  }, 800);
                                }, 600);
                              }, 3000);
                            }, 900);
                          }, 900);
                        }, 2600);
                      }, 2500);
                    }, 2500);
                  }, 2500);
                }, 2500);
              }, 2500);
            }, 2500);
          }, 'neu.json');
        }, 800);
      }, 1500);
    })();
    </script>
"""
kopie2 = build('_mws2.html', script2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# JSON-Export
script3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      /* Knopf im Bereich Wiki-Daten nach Text suchen, statt nach Nummer:
         ein weiterer Knopf soll einen Test nicht umhauen. */
      function knopf(muster) {
        return [].slice.call(document.querySelectorAll('.settings-btn'))
                .filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          knopf('JSON').click();
          setTimeout(function () {
            ok(window.__name === 'simplewiki.json', 'Dateiname: ' + window.__name);
            ok(!!window.__blob, 'Datei erzeugt');
            ok(!!q('.hinweis') && q('.hinweis').textContent.indexOf('JSON') >= 0,
               'Hinweis: ' + (q('.hinweis') ? q('.hinweis').textContent.trim() : 'KEINER'));
            window.__blob.text().then(function (text) {
              var d = JSON.parse(text);
              ok(d.version === 1, 'Version: ' + d.version);
              ok(Array.isArray(d.seiten) && d.seiten.length === 2, 'zwei Seiten: ' + d.seiten.length);
              ok(d.seiten.map(function (s) { return s.title; }).join('|') === 'Alpha|Beta',
                 'Reihenfolge: ' + d.seiten.map(function (s) { return s.title; }).join('|'));
              ok(d.startseite === 'a', 'Startseite: ' + d.startseite);
              ok(d.sprache === 'de', 'Sprache: ' + d.sprache);
              ok(d.thema === 'light', 'Farbe: ' + d.thema);
              ok(d.seiten[0].created === '2026-01-01T10:00:00.000Z', 'Zeitstempel unveraendert: ' + d.seiten[0].created);
              ok(text.indexOf('&lt;') < 0 && text.indexOf('\\u003c') < 0, 'kein HTML-Escaping in der JSON-Datei');
              ok(text.indexOf('\n') > 0, 'lesbar formatiert');
              log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            });
          }, 800);
        }, 800);
      }, 1500);
    })();
    </script>
"""
kopie3 = build('_mws3.html', script3, seiten, startpage='a')

pruefe(kopie1, kopie2, kopie3)