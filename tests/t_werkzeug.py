"""Die Werkzeugleiste unter dem Kopf: Wortzahl und Lesezeit, der
ablenkungsfreie Modus und der Druck der offenen Seite.

Sie ist standardmaessig aus und im Einstellungen-Dialog einschaltbar.
Wie die Farbe ist das eine Einstellung, kein Inhalt: im Browser steht
sie in localStorage, am Server als Feld `toolbar` am Tiddler der
Startseite, und in der Austauschform als `toolbar` oben.

Der Druck der offenen Seite ist die Gegenprobe zum Fluss: wer die
Leiste benutzt, will genau diese eine Seite auf Papier - nicht das
ganze Wiki. Deshalb schaltet der beforeprint-Zuhoerer in diesem Fall
nicht in den Fluss. Genau das prueft Teil 1.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

# Vier Woerter, damit die Lesezeit genau eine Minute ist (aufgerundet).
seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nzwei drei vier",
     "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [],
     "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Im Browser: Schalter, Zaehler, Zen, Druck der offenen Seite, Export
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
      function wzBtn(titel) {
        return all('.werkzeug-btn').filter(function (b) { return b.getAttribute('title') === titel; })[0];
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      /* Den Export abfangen, wie es die anderen Tests tun. */
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      var wzStand = localStorage.getItem('simplewiki_toolbar');

      setTimeout(function () {
        head('Ausgangslage: keine Werkzeugleiste');
        ok(!q('.werkzeugleiste'), 'sie ist aus');
        ok(!q('.zen-ausgang'), 'kein Ausgang im Bild');

        head('Der Schalter im Einstellungen-Dialog');
        q('.settings-toggle').click();
        setTimeout(function () {
          var kasten = q('#settings-toolbar');
          ok(!!kasten, 'es gibt den Kaestchen-Schalter');
          ok(kasten && kasten.checked === false, 'er steht aus');

          if (kasten) kasten.click();
          setTimeout(function () {
            ok(!!q('.werkzeugleiste'), 'sie ist jetzt da');
            ok(localStorage.getItem('simplewiki_toolbar') === '1',
               'im Speicher: ' + localStorage.getItem('simplewiki_toolbar'));

            head('Wortzahl und Lesezeit der offenen Seite');
            var zaehler = q('.werkzeug-zaehler');
            ok(!!zaehler, 'es gibt den Zaehler');
            var text = zaehler ? zaehler.textContent.trim() : '';
            ok(/4 Wörter/.test(text), 'vier Woerter: ' + text);
            ok(/1 Min\. Lesezeit/.test(text), 'eine Minute: ' + text);

            head('Ablenkungsfrei: Klasse, Ausgang, Escape');
            wzBtn('Ablenkungsfrei lesen').click();
            setTimeout(function () {
              ok(q('.app').classList.contains('zen'), 'die Klasse zen steht am .app');
              ok(getComputedStyle(q('.header')).display === 'none', 'der Kopf ist weg');
              ok(!!q('.zen-ausgang'), 'der Ausgang steht im Bild');

              q('.zen-ausgang').click();
              setTimeout(function () {
                ok(q('.app').classList.contains('zen') === false, 'der Ausgang holt zurueck');
                ok(!q('.zen-ausgang'), 'der Ausgang ist wieder weg');

                head('Druck der offenen Seite');
                window.__gedruckt = 0;
                window.print = function () { window.__gedruckt++; };
                var druck = wzBtn('Diese Seite drucken');
                ok(!!druck, 'es gibt den Druck-Knopf');
                if (druck) druck.click();
                ok(window.__gedruckt === 1, 'window.print wurde gerufen: ' + window.__gedruckt);
                ok(!q('.fluss'), 'die offene Seite bleibt eine Seite, kein Fluss');

                /* beforeprint darf hier nicht in den Fluss schalten -
                   der Ausgang ueberschreibt die Einstellung nicht. */
                window.dispatchEvent(new Event('beforeprint'));
                setTimeout(function () {
                  ok(!q('.fluss'), 'auch Strg+P bringt hier keinen Fluss');
                  window.dispatchEvent(new Event('afterprint'));

                  /* Ohne das Kennzeichen ist es der alte Weg: Fluss. */
                  window.dispatchEvent(new Event('beforeprint'));
                  setTimeout(function () {
                    ok(!!q('.fluss'), 'von Hand bringt beforeprint den Fluss weiterhin');
                    window.dispatchEvent(new Event('afterprint'));

                    head('Der Schalter steht im Austausch');
                    knopf('JSON').click();
                    setTimeout(function () {
                      ok(window.__name === 'simplewiki.json', 'Dateiname: ' + window.__name);
                      window.__blob.text().then(function (text) {
                        var d = JSON.parse(text);
                        ok(d.toolbar === true, 'im Export: ' + d.toolbar);
                        localStorage.setItem('simplewiki_toolbar', wzStand || '');
                        ende();
                      });
                    }, 800);
                  }, 200);
                }, 200);
              }, 200);
            }, 200);
          }, 400);
        }, 700);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_wz1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Persistenz: der gespeicherte Zustand kommt beim Start wieder an
mkcopy.PRE_SCRIPT = "<script>try{localStorage.setItem('simplewiki_toolbar','1');}catch(e){}</script>"
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        ok(!!q('.werkzeugleiste'), 'die gespeicherte Leiste ist beim Start da');
        var zaehler = q('.werkzeug-zaehler');
        ok(!!zaehler, 'mit ihrem Zaehler');
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_wz2.html', teil2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# Am Server: der Schalter reist am Startseiten-Tiddler
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Der Server schickt die Werkzeugleiste mit');
        ok(!!q('.werkzeugleiste'), 'sie ist an');

        head('Aendern am Server');
        q('.settings-toggle').click();
        setTimeout(function () {
          var kasten = q('#settings-toolbar');
          ok(kasten && kasten.checked === true, 'der Schalter steht an');
          if (kasten) kasten.click();
          setTimeout(function () {
            ok(!q('.werkzeugleiste'), 'ausgeschaltet');
            ende();
          }, 300);
        }, 700);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nzwei drei vier', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000',
     'toolbar': 'true'},
    {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta', 'tags': '',
     'created': '20260203100500000', 'modified': '20260203100500000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'werkzeug': Wiki('werkzeug', TIDDLER, titel='Werkzeug', skript=teil3)}
server, thread, port = starten(wikis)

fehler_gesamt = 0
try:
    text = bericht(dumpdom('_wz1.html', budget=120000))
    text2 = bericht(dumpdom('_wz2.html', budget=120000))

    def drucken(name, textx):
        print('%-22s %s' % (name, textx.split('\n')[-1] if textx else 'KEIN REPORT'))
        for z in textx.split('\n'):
            if z.startswith('FAIL'):
                print('    ' + z)
        print()

    drucken('_wz1.html', text)
    drucken('_wz2.html', text2)
    fehler_gesamt += zahlen(text)[1] + zahlen(text2)[1]

    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/werkzeug/' % port, None, 120000))
    drucken('_wz3_server.html', text3)
    fehler_gesamt += zahlen(text3)[1]
finally:
    beenden(server)

# Das Ausschalten muss beim Speichern am Startseiten-Tiddler ankommen.
saves = [a for a in anfragen() if a.get('op') == 'save' and a['nutzlast'].get('tiddlers')]
ausStarts = [t for a in saves for t in a['nutzlast']['tiddlers']
             if t.get('title') == 'Alpha' and t.get('toolbar') == 'false']
print('Werkzeugleiste am Startseiten-Tiddler: %s' % ('false' if ausStarts else 'fehlt'))
if not ausStarts:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0] + zahlen(text3)[0], fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
