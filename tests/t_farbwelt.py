"""Die eigene Farbwelt: aus einer vorhandenen Welt klonen, einzelne
Farbwerte aendern, in beiden Modi, und den Stand behalten.

Die eigene Welt hat keine CSS-Regel. Stattdessen stehen ihre Werte als
Inline-Variablen am body und ueberschreiben die Klasse der Basiswelt.
Gespeichert wird das Objekt {basis, hell, dunkel} - im Browser unter
simplewiki_eigene_farben, am Server als Feld des Startseiten-Tiddlers.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Klonen, aendern, dunkler Zweig, Export
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
      function wert(name) { return getComputedStyle(document.body).getPropertyValue('--' + name).trim(); }
      function inline(name) { return document.body.style.getPropertyValue('--' + name); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      var eigStand = localStorage.getItem('simplewiki_eigene_farben');

      setTimeout(function () {
        head('Die Auswahl im Einstellungen-Dialog');
        q('.settings-toggle').click();
        setTimeout(function () {
          var pal = document.getElementById('settings-palette');
          var ids = all('#settings-palette option').map(function (o) { return o.value; });
          ok(ids.length === 9, 'neun Welten im Dropdown: ' + ids.length);
          ok(ids[ids.length - 1] === 'eigene', 'die letzte ist die eigene: ' + ids[ids.length - 1]);

          head('Die eigene Welt waehlen');
          pal.value = 'eigene';
          pal.dispatchEvent(new Event('change', { bubbles: true }));
          setTimeout(function () {
            ok(!!q('.farb-editor'), 'der Farb-Editor ist da');
            ok(q('.farb-editor-inhalt').offsetParent === null, 'der Editor ist zugeklappt');
            ok(!!q('.farb-editor-schalter'), 'der Schalter zum Aufklappen ist da');
            q('.farb-editor-schalter').click();
            ok(all('.farb-feld').length === 18, 'achtzehn Farbwaehler: ' + all('.farb-feld').length);
            ok(all('.farb-text').length === 4, 'vier Textfelder fuer Transparenz: ' + all('.farb-text').length);
            var gruppen = all('.farb-gruppe-titel').map(function (g) { return g.textContent.trim(); });
            ok(gruppen.indexOf('Überschriften') >= 0, 'die Gruppe Ueberschriften: ' + gruppen.join('|'));

            head('Aus Nord klonen');
            var quelle = q('.farb-klon select');
            quelle.value = 'nord';
            quelle.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(function () {
              ok(q('.farb-editor-inhalt').offsetParent !== null, 'der Schalter hat den Editor aufgeklappt');
              q('.farb-klon .settings-btn').click();
              setTimeout(function () {
                ok(document.body.classList.contains('pal-nord'), 'Basis Nord am body: ' + document.body.className);
                ok(inline('bg-primary') !== '', 'die Werte stehen inline: [' + inline('bg-primary') + ']');
                ok((localStorage.getItem('simplewiki_eigene_farben') || '').indexOf('"basis":"nord"') >= 0,
                   'im Speicher mit Basis: ' + (localStorage.getItem('simplewiki_eigene_farben') || '').slice(0, 40));

                head('Eine Farbe aendern');
                var bg = all('.farb-feld')[0];
                bg.value = '#123456';
                bg.dispatchEvent(new Event('input', { bubbles: true }));
                head('Die Ueberschriften tragen eigene Farben');
                var h1f = all('.farb-feld')[4];
                var h2f = all('.farb-feld')[5];
                var h3f = all('.farb-feld')[6];
                h1f.value = '#aa0000';
                h1f.dispatchEvent(new Event('input', { bubbles: true }));
                h2f.value = '#00aa00';
                h2f.dispatchEvent(new Event('input', { bubbles: true }));
                h3f.value = '#0000aa';
                h3f.dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(function () {
                  ok(wert('bg-primary') === '#123456', 'die neue Hintergrundfarbe wirkt: ' + wert('bg-primary'));
                  ok(getComputedStyle(q('.header h1')).color === 'rgb(170, 0, 0)',
                     'h1: der Wiki-Titel: ' + getComputedStyle(q('.header h1')).color);
                  ok(getComputedStyle(q('.preview h1')).color === 'rgb(170, 0, 0)',
                     'h1: die Ueberschrift im Text: ' + getComputedStyle(q('.preview h1')).color);
                  ok(getComputedStyle(q('.content-title')).color === 'rgb(0, 170, 0)',
                     'h2: der Seitentitel: ' + getComputedStyle(q('.content-title')).color);

                  head('Der dunkle Zweig');
                  all('.farb-modus')[1].click();
                  setTimeout(function () {
                    ok(document.body.classList.contains('dark-mode'), 'dunkel geworden');
                    ok(all('.farb-modus')[1].classList.contains('aktiv'), 'Dunkel ist der aktive Reiter');
                    ok(all('.farb-feld')[0].value !== '#123456',
                       'dunkel hat einen eigenen Wert: ' + all('.farb-feld')[0].value);
                    var bgd = all('.farb-feld')[0];
                    bgd.value = '#ffffff';
                    bgd.dispatchEvent(new Event('input', { bubbles: true }));
                    setTimeout(function () {
                      ok(wert('bg-primary') === '#ffffff', 'der dunkle Wert wirkt: ' + wert('bg-primary'));

                      head('Der Export traegt die eigenen Farben');
                      knopf('JSON').click();
                      setTimeout(function () {
                        ok(window.__name === 'simplewiki.json', 'Dateiname: ' + window.__name);
                        window.__blob.text().then(function (text) {
                          var d = JSON.parse(text);
                          ok(d.palette === 'eigene', 'Welt im Export: ' + d.palette);
                          ok(d.eigeneFarben && d.eigeneFarben.hell['bg-primary'] === '#123456',
                             'hell im Export: ' + (d.eigeneFarben && d.eigeneFarben.hell['bg-primary']));
                          ok(d.eigeneFarben && d.eigeneFarben.dunkel['bg-primary'] === '#ffffff',
                             'dunkel im Export: ' + (d.eigeneFarben && d.eigeneFarben.dunkel['bg-primary']));
                          if (eigStand === null) localStorage.removeItem('simplewiki_eigene_farben');
                          else localStorage.setItem('simplewiki_eigene_farben', eigStand);
                          localStorage.removeItem('simplewiki_palette');
                          ende();
                        });
                      }, 800);
                    }, 400);
                  }, 400);
                }, 300);
              }, 300);
            }, 300);
          }, 400);
        }, 700);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_fw1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Persistenz: der eigene Stand kommt beim Start wieder an
EIGEN = {'basis': 'nord', 'hell': {'bg-primary': '#123456', 'h2-color': '#00aa00'},
         'dunkel': {'bg-primary': '#ffffff'}}
mkcopy.PRE_SCRIPT = ("<script>try{localStorage.setItem('simplewiki_eigene_farben',"
                     + json.dumps(json.dumps(EIGEN))
                     + ");}catch(e){}</script>")

teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function wert(name) { return getComputedStyle(document.body).getPropertyValue('--' + name).trim(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        ok(document.body.classList.contains('pal-nord'), 'Basis Nord aus dem Speicher: ' + document.body.className);
        ok(wert('bg-primary') === '#123456', 'der helle Wert aus dem Speicher: ' + wert('bg-primary'));
        q('.kopf-fluss').click();
        setTimeout(function () {
          var fk = q('.fluss-titel-knopf');
          ok(!!fk && getComputedStyle(fk).color === 'rgb(0, 170, 0)',
             'der Fluss-Titel traegt die eigene h2-Farbe: ' + (fk ? getComputedStyle(fk).color : 'kein Knopf'));
          q('.kopf-fluss').click();
          setTimeout(function () {
            q('.theme-toggle').click();
            setTimeout(function () {
              ok(document.body.classList.contains('dark-mode'), 'dunkel geworden');
              ok(wert('bg-primary') === '#ffffff', 'der dunkle Wert aus dem Speicher: ' + wert('bg-primary'));
              log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 400);
          }, 400);
        }, 400);
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_fw2.html', teil2, seiten, startpage='a', palette='eigene')

# ---------------------------------------------------------------- Teil 3
# Am Server: die eigenen Farben reisen auf dem Startseiten-Tiddler
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function wert(name) { return getComputedStyle(document.body).getPropertyValue('--' + name).trim(); }
      function head(m) { log.push('--- ' + m); out(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Der Server schickt die eigenen Farben mit');
        ok(document.body.classList.contains('pal-nord'), 'Server: Basis Nord: ' + document.body.className);
        ok(wert('bg-primary') === '#0a0b0c', 'Server: der eigene Wert: ' + wert('bg-primary'));

        head('Der leere dunkle Zweig faellt auf die Basis zurueck');
        q('.theme-toggle').click();
        setTimeout(function () {
          ok(document.body.classList.contains('dark-mode'), 'dunkel geworden');
          ok(wert('bg-primary') === '#2e3440', 'dunkel faellt auf die Basis zurueck: ' + wert('bg-primary'));

          head('Aendern am Server');
          q('.settings-toggle').click();
          setTimeout(function () {
            var pal = document.getElementById('settings-palette');
            ok(pal.value === 'eigene', 'die eigene Welt ist gewaehlt: ' + pal.value);
            ok(!!q('.farb-editor'), 'der Farb-Editor ist da');
            ok(q('.farb-editor-inhalt').offsetParent === null, 'der Editor ist zugeklappt');
            q('.farb-editor-schalter').click();
            document.querySelectorAll('.farb-modus')[1].click();
            setTimeout(function () {
              ok(q('.farb-editor-inhalt').offsetParent !== null, 'der Editor ist aufgeklappt');
              var bg = document.querySelectorAll('.farb-feld')[0];
              bg.value = '#0d0e0f';
              bg.dispatchEvent(new Event('input', { bubbles: true }));
              setTimeout(function () {
                ok(wert('bg-primary') === '#0d0e0f', 'der dunkle Wert wirkt: ' + wert('bg-primary'));
                ende();
              }, 400);
            }, 400);
          }, 700);
        }, 400);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

EIGEN_FELD = json.dumps({'basis': 'nord', 'hell': {'bg-primary': '#0a0b0c'}})
TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000',
     'palette': 'eigene', 'eigeneFarben': EIGEN_FELD},
    {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta', 'tags': '',
     'created': '20260203100500000', 'modified': '20260203100500000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'farbwelt': Wiki('farbwelt', TIDDLER, titel='Farbwelt', skript=teil3)}
server, thread, port = starten(wikis)

fehler_gesamt = 0
try:
    text = bericht(dumpdom('_fw1.html', budget=120000))
    text2 = bericht(dumpdom('_fw2.html', budget=120000))

    def drucken(name, textx):
        print('%-22s %s' % (name, textx.split('\n')[-1] if textx else 'KEIN REPORT'))
        for z in textx.split('\n'):
            if z.startswith('FAIL'):
                print('    ' + z)
        print()

    drucken('_fw1.html', text)
    drucken('_fw2.html', text2)
    fehler_gesamt += zahlen(text)[1] + zahlen(text2)[1]

    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/farbwelt/' % port, None, 120000))
    drucken('_fw3_server.html', text3)
    fehler_gesamt += zahlen(text3)[1]
finally:
    beenden(server)

# Die geaenderte eigene Farbe muss beim Speichern am Startseiten-Tiddler
# ankommen, zusammen mit der Welt.
saves = [a for a in anfragen() if a.get('op') == 'save' and a['nutzlast'].get('tiddlers')]
eigenStarts = [t for a in saves for t in a['nutzlast']['tiddlers']
               if t.get('title') == 'Alpha' and t.get('palette') == 'eigene'
               and '0d0e0f' in (t.get('eigeneFarben') or '')]
print('Eigene Farben am Startseiten-Tiddler: %s' % ('angekommen' if eigenStarts else 'fehlt'))
if not eigenStarts:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0] + zahlen(text3)[0], fehler_gesamt))
sys.exit(1 if fehler_gesamt else 0)
