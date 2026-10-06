"""Die Farbwelten: Auswahl im Einstellungen-Dialog, Hell und Dunkel
darin, und der Austausch - im Browser ueber localStorage, am Server
ueber den Startseiten-Tiddler.

Der Knopf im Kopf (die Sonne / der Mond) ist eine Sache fuer sich:
Er ist die Hell/Dunkel-Achse, die in jeder Welt bleibt, was sie ist.
Deshalb verschwindet die gewaehlte Welt nach dem Umschalten nicht -
sofort kommt derselbe Ton in dunkel, weil die Regel
body.dark-mode.pal-<name> genauso da ist wie body.pal-<name>.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Im Browser: Dialog, Wechsel, Hell/Dunkel in der Welt, Export
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function knopf(muster) {
        return all('.settings-btn').filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      /* Das musterbare Zeichen der Welt: die Farbe des Punktrasters.
         Die Zahl ist die Tinte in den ersten drei Kanaelen - dieselbe
         Ablesung wie in t_textur. */
      function tint() {
        var text = getComputedStyle(document.body).getPropertyValue('--textur-inhalt').trim();
        return (text.match(/[\d.]+/g) || []).slice(0, 3).join(',');
      }
      function welt() {
        return all('body')[0].className.split(/\s+/).filter(function (k) { return k.indexOf('pal-') === 0; }).join('|');
      }
      /* Den Dialog oeffnen und die Farbwelt im Dropdown wechseln. */
      function farbwelt(id, dann) {
        var pal = document.getElementById('settings-palette');
        pal.value = id;
        pal.dispatchEvent(new Event('change', { bubbles: true }));
        setTimeout(dann, 400);
      }

      /* Den Export abfangen, wie es der Austausch-Test tut. */
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      var palStand = localStorage.getItem('simplewiki_palette');

      setTimeout(function () {
        head('Die Ausgangslage ist Pergament');
        ok(welt() === 'pal-pergament', 'die Welt steht als Klasse am body: ' + welt());
        ok(document.body.classList.contains('dark-mode') === false, 'hell');
        ok(tint() === '61,47,31', 'die Tinte von Pergament: ' + tint());

        head('Die Auswahl im Einstellungen-Dialog');
        q('.settings-toggle').click();
        setTimeout(function () {
          var pal = document.getElementById('settings-palette');
          ok(!!pal, 'das Dropdown ist da');
          var ids = all('#settings-palette option').map(function (o) { return o.value; });
          ok(ids.join('|') === 'pergament|nord|wacholder|sol', 'alle vier Welten: ' + ids.join('|'));
          var namen = all('#settings-palette option').map(function (o) { return o.textContent.trim(); });
          ok(namen.join('|') === 'Pergament|Nord|Wacholder|Sol', 'mit Namen: ' + namen.join('|'));
          ok(pal.value === 'pergament', 'gewaehlt ist Pergament: ' + pal.value);

          head('Wechsel in eine andere Welt');
          farbwelt('nord', function () {
            ok(welt() === 'pal-nord', 'Nord steht am body: ' + welt());
            ok(tint() === '46,52,64', 'die Tinte von Nord: ' + tint());
            ok(localStorage.getItem('simplewiki_palette') === 'nord',
               'im Speicher: ' + localStorage.getItem('simplewiki_palette'));

            head('Hell und Dunkel bleiben in der Welt');
            q('.theme-toggle').click();
            setTimeout(function () {
              ok(welt() === 'pal-nord', 'Nord ist geblieben: ' + welt());
              ok(document.body.classList.contains('dark-mode'), 'dunkel geworden');
              ok(tint() === '236,239,244', 'die Tinte von Nord im Dunkeln: ' + tint());

              head('Und wieder zurueck: Welt und Helligkeit zusammen');
              q('.theme-toggle').click();
              setTimeout(function () {
                ok(document.body.classList.contains('dark-mode') === false, 'wieder hell');
                ok(tint() === '46,52,64', 'wieder die helle Nord-Tinte: ' + tint());

                head('Noch zwei weitere Welten');
                farbwelt('wacholder', function () {
                  ok(tint() === '59,52,32', 'Wacholder: ' + tint());
                  farbwelt('sol', function () {
                    ok(tint() === '88,110,117', 'Sol: ' + tint());

                    head('Die Welt steht im Austausch');
                    knopf('JSON').click();
                    setTimeout(function () {
                      ok(window.__name === 'simplewiki.json', 'Dateiname: ' + window.__name);
                      window.__blob.text().then(function (text) {
                        var d = JSON.parse(text);
                        ok(d.palette === 'sol', 'im Export: ' + d.palette);
                        localStorage.setItem('simplewiki_palette', palStand || '');
                        ende();
                      });
                    }, 800);
                  });
                });
              }, 400);
            }, 400);
          });
        }, 700);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_pal1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Persistenz: die gespeicherte Welt kommt beim Start wieder an
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function tint() {
        var text = getComputedStyle(document.body).getPropertyValue('--textur-inhalt').trim();
        return (text.match(/[\d.]+/g) || []).slice(0, 3).join(',');
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        ok(document.body.classList.contains('pal-nord'), 'Nord steht am body');
        ok(tint() === '46,52,64', 'mit der Nord-Tinte: ' + tint());
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_pal2.html', teil2, seiten, startpage='a', palette='nord')

# ---------------------------------------------------------------- Teil 3
# Am Server: die Farbwelt reist auf dem Startseiten-Tiddler
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function tint() {
        var text = getComputedStyle(document.body).getPropertyValue('--textur-inhalt').trim();
        return (text.match(/[\d.]+/g) || []).slice(0, 3).join(',');
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Der Server schickt die Farbwelt mit');
        ok(document.body.classList.contains('pal-nord'), 'Nord steht am body');
        ok(tint() === '46,52,64', 'mit der Nord-Tinte: ' + tint());

        head('Aendern am Server');
        q('.settings-toggle').click();
        setTimeout(function () {
          var pal = document.getElementById('settings-palette');
          pal.value = 'sol';
          pal.dispatchEvent(new Event('change', { bubbles: true }));
          setTimeout(function () {
            ok(document.body.classList.contains('pal-sol'), 'Sol steht am body');
            ok(tint() === '88,110,117', 'mit der Sol-Tinte: ' + tint());
            ende();
          }, 400);
        }, 700);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000',
     'palette': 'nord'},
    {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta', 'tags': '',
     'created': '20260203100500000', 'modified': '20260203100500000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'palette': Wiki('palette', TIDDLER, titel='Palette', skript=teil3)}
server, thread, port = starten(wikis)

fehler_gesamt = 0
try:
    text = bericht(dumpdom('_pal1.html', budget=120000))
    text2 = bericht(dumpdom('_pal2.html', budget=120000))

    def drucken(name, textx):
        print('%-22s %s' % (name, textx.split('\n')[-1] if textx else 'KEIN REPORT'))
        for z in textx.split('\n'):
            if z.startswith('FAIL'):
                print('    ' + z)
        print()

    drucken('_pal1.html', text)
    drucken('_pal2.html', text2)
    fehler_gesamt += zahlen(text)[1] + zahlen(text2)[1]

    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/palette/' % port, None, 120000))
    drucken('_pal3_server.html', text3)
    fehler_gesamt += zahlen(text3)[1]
finally:
    beenden(server)

# Der Wechsel auf Sol muss beim Speichern am Startseiten-Tiddler ankommen.
saves = [a for a in anfragen() if a.get('op') == 'save' and a['nutzlast'].get('tiddlers')]
solStarts = [t for a in saves for t in a['nutzlast']['tiddlers']
             if t.get('title') == 'Alpha' and t.get('palette') == 'sol']
print('Farbwelt am Startseiten-Tiddler: %s' % ('sol' if solStarts else 'fehlt'))
if not solStarts:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0] + zahlen(text3)[0], fehler_gesamt))
sys.exit(1 if fehler_gesamt else 0)