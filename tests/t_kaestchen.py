"""Aufgabenlisten: das Kaestchen im Text ist anklickbar und schreibt
zurueck.

Marked gibt "[ ]" und "[x]" als Kaestchen aus, aber immer abgeschaltet.
SimpleWiki macht sie wieder anklickbar, solange geschrieben werden darf:
ein Klick aendert nur den Haken in der Quellzeile, nichts sonst, und
speichert die Seite. Wo nur gelesen werden darf, bleibt das Kaestchen
abgeschaltet; im Codeblock ist "[ ]" kein Kaestchen, sondern Text.

Teil 1 prueft das Schreiben im Browser, Teil 2 das Abschalten im
Nur-Lese-Zustand, Teil 3 und 4 dasselbe am Server.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

INHALT = ("# Aufgaben\n\n"
          "- [ ] offen\n"
          "- [x] fertig\n"
          "- [ ] noch eins\n"
          "\n"
          "```\n- [ ] im Code\n```\n")

seiten = [
    {"id": "a", "title": "Aufgaben", "content": INHALT,
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

KOPF = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function kaestchen() { return [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]')); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""

# ---------------------------------------------------------------- Teil 1
# Im Browser: Kaestchen anklicken aendert den Haken in der Quellzeile.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      function quelle() {
        var p = [];
        try { p = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]'); } catch (e) {}
        var s = p.filter(function (x) { return x.title === 'Aufgaben'; })[0] || {};
        return (s.content || '').split('\n');
      }

      setTimeout(function () {
        head('Die Kaestchen stehen bereit');
        var k = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
        ok(k.length === 3, 'drei Kaestchen: ' + k.length);
        ok(k.every(function (x) { return !x.disabled; }), 'alle anklickbar');
        ok(k[0].checked === false && k[1].checked === true && k[2].checked === false,
           'Zustand passt zur Quelle');
        ok(k[0].getAttribute('data-zeile') === '2' && k[1].getAttribute('data-zeile') === '3'
           && k[2].getAttribute('data-zeile') === '4', 'Zuordnung zur Zeile');

        head('Ein Klick schaltet [ ] zu [x]');
        k[0].click();
        setTimeout(function () {
          var z = quelle();
          ok(z[2] === '- [x] offen', 'aus [ ] wurde [x]: ' + JSON.stringify(z[2]));
          ok(z[3] === '- [x] fertig', 'die Nachbarzeile blieb: ' + JSON.stringify(z[3]));
          ok(z[7] === '- [ ] im Code', 'der Code blieb unberuehrt: ' + JSON.stringify(z[7]));
          var k2 = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
          ok(k2[0].checked === true, 'das Kaestchen steht jetzt an');

          head('Ein Klick zurueck schaltet [x] zu [ ]');
          k2[1].click();
          setTimeout(function () {
            var z2 = quelle();
            ok(z2[3] === '- [ ] fertig', 'aus [x] wurde [ ]: ' + JSON.stringify(z2[3]));
            ok(z2[2] === '- [x] offen', 'die erste Aenderung blieb');
            ende();
          }, 250);
        }, 250);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_kaestchen1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Im Browser: nur lesen schaltet die Kaestchen wieder ab.
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      function quelle() {
        var p = [];
        try { p = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]'); } catch (e) {}
        var s = p.filter(function (x) { return x.title === 'Aufgaben'; })[0] || {};
        return (s.content || '').split('\n');
      }

      setTimeout(function () {
        head('Erst schreibbar');
        var k = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
        ok(k.length === 3 && !k[0].disabled, 'die Kaestchen sind anklickbar');

        head('Der Server meldet nur lesen');
        document.dispatchEvent(new CustomEvent('simplewiki:nurlesen'));
        setTimeout(function () {
          var k2 = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
          ok(k2.every(function (x) { return x.disabled === true; }), 'alle wieder abgeschaltet');
          ok(!k2[0].getAttribute('data-zeile'), 'keine Zuordnung mehr');
          var vorher = quelle()[2];
          k2[0].click();
          setTimeout(function () {
            ok(quelle()[2] === vorher, 'ein Klick aendert nichts: ' + JSON.stringify(quelle()[2]));
            ende();
          }, 250);
        }, 250);
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_kaestchen2.html', teil2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# Am Server: ein Klick schreibt die geaenderte Seite.
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Am Server: die Kaestchen sind anklickbar');
        var k = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
        ok(k.length === 3, 'drei Kaestchen: ' + k.length);
        ok(k.every(function (x) { return !x.disabled; }), 'alle anklickbar');

        head('Ein Klick schreibt die Seite');
        k[0].click();
        setTimeout(function () {
          var k2 = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
          ok(k2[0].checked === true, 'das Kaestchen steht jetzt an');
          ok(k2[1].checked === true && k2[2].checked === false, 'die anderen blieben');
          ende();
        }, 400);
      }, 2000);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 4
# Am Server ohne Schreibrecht: die Kaestchen bleiben abgeschaltet.
teil4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Am Server nur lesen');
        var k = [].slice.call(document.querySelectorAll('.content-body .preview input[type="checkbox"]'));
        ok(k.length === 3, 'drei Kaestchen: ' + k.length);
        ok(k.every(function (x) { return x.disabled === true; }), 'alle abgeschaltet');
        ok(!k[0].getAttribute('data-zeile'), 'ohne Zuordnung');
        var vor = k[0].checked;
        k[0].click();
        setTimeout(function () {
          ok(k[0].checked === vor, 'ein Klick aendert nichts');
          ende();
        }, 250);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Aufgaben', 'sw-id': 'k1', 'text': INHALT, 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000',
     'reihenfolge': '0000'},
    {'title': '$:/DefaultTiddlers', 'text': 'Aufgaben'},
]
wikis = {
    'kaestchen': Wiki('kaestchen', TIDDLER, titel='Kaestchen', skript=teil3),
    'kaestchen_ro': Wiki('kaestchen_ro', TIDDLER, nurLesen=True,
                         titel='Kaestchen', skript=teil4),
}
server, thread, port = starten(wikis)

fehler_gesamt = 0


def drucken(name, text):
    print('%-22s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
    print()


try:
    text = bericht(dumpdom('_kaestchen1.html', budget=120000))
    text2 = bericht(dumpdom('_kaestchen2.html', budget=120000))
    drucken('_kaestchen1.html', text)
    drucken('_kaestchen2.html', text2)
    fehler_gesamt += zahlen(text)[1] + zahlen(text2)[1]

    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/kaestchen/' % port, None, 120000))
    drucken('_kaestchen3.html', text3)
    fehler_gesamt += zahlen(text3)[1]
    # Vor dem naechsten leeren holen: sonst ist das Protokoll weg.
    server3 = anfragen()

    leeren()
    text4 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/kaestchen_ro/' % port, None, 120000))
    drucken('_kaestchen4.html', text4)
    fehler_gesamt += zahlen(text4)[1]
    server4 = anfragen()
finally:
    beenden(server)

saves = [a for a in server3 if a.get('op') == 'save'
         and a['pfad'].startswith('/recipe/kaestchen/')]
neu = [t for a in saves for t in (a['nutzlast'].get('tiddlers') or [])
       if t.get('title') == 'Aufgaben' and '- [x] offen' in (t.get('text') or '')]
print('Geaenderte Aufgabenliste am Server: %s' % ('angekommen' if neu else 'fehlt'))
if not neu:
    fehler_gesamt += 1

# Nur lesen: der Klick darf keine Schreibanfrage ausgeloest haben.
ro_saves = [a for a in server4 if a.get('op') == 'save']
print('Schreibversuch ohne Schreibrecht: %s'
      % ('keiner' if not ro_saves else '%d - falsch' % len(ro_saves)))
if ro_saves:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0] + zahlen(text3)[0] + zahlen(text4)[0],
         fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
