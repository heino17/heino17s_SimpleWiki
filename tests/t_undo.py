"""Einen Schritt zurueck: die letzte Aenderung am Inhalt zuruecknehmen.

Ein Schritt, kein Stapel. Gemerkt wird der Inhalt (Seiten, Startseite,
Blick); eine Einstellung wie Farbe oder Sprache gehoert nicht dazu. Der
Test loescht eine Seite, aendert einen Text und legt eine Seite an - und
nimmt jedes Mal zurueck. Teil 1 im Browser, Teil 2 am Server.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ("<script>try{localStorage.setItem('simplewiki_toolbar','1');}"
                     "catch(e){}</script>")

seiten = [
    {"id": "a", "title": "Alpha", "content": "A",
     "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "B",
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

KOPF = r"""
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function tick(fn) { setTimeout(fn, 250); }
      function vm() { return window.__vm; }
      function speich() { var p = []; try { p = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]'); } catch (e) {} return p; }
      function seite(t) { return speich().filter(function (x) { return x.title === t; })[0] || {}; }
      function undoKnopf() { return q('.werkzeugleiste button'); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""

# ---------------------------------------------------------------- Teil 1
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        var v = vm();
        ok(!!v, 'die App ist da');
        ok(v.pages.length === 2, 'zwei Seiten: ' + v.pages.length);
        ok(!!undoKnopf(), 'der Werkzeugkasten ist da');
        ok(undoKnopf().disabled === true, 'ohne Aenderung ist Zuruecknehmen aus');

        head('Eine Seite loeschen');
        v.deletePage('b');
        v.confirmDelete();
        ok(v.pages.length === 1, 'nach dem Loeschen eine Seite: ' + v.pages.length);
        ok(speich().length === 1, 'im Speicher auch eine: ' + speich().length);
        /* Der Knopf folgt dem Zustand erst im naechsten Bild - deshalb
           wird er nach einem Bild (tick) beurteilt und geklickt. */
        tick(function () {
          ok(undoKnopf().disabled === false, 'Zuruecknehmen ist jetzt moeglich');

          head('Zuruecknehmen holt sie wieder');
          undoKnopf().click();
          tick(function () {
            ok(v.pages.length === 2, 'wieder zwei Seiten: ' + v.pages.length);
            ok(seite('Beta').content === 'B', 'Beta ist mit Inhalt zurueck: ' + JSON.stringify(seite('Beta').content));
            ok(undoKnopf().disabled === true, 'kein zweiter Schritt - der Knopf ist wieder aus');

            head('Einen Text aendern');
            v.currentPage = v.pages.filter(function (p) { return p.id === 'a'; })[0];
            v.editTitle = 'Alpha'; v.editContent = 'GEaENDERT'; v.editTags = []; v.isEditing = true;
            v.savePage();
            ok(seite('Alpha').content === 'GEaENDERT', 'der neue Text steht: ' + JSON.stringify(seite('Alpha').content));

            head('Zuruecknehmen stellt den Text wieder her');
            tick(function () {
              undoKnopf().click();
              tick(function () {
                ok(seite('Alpha').content === 'A', 'der alte Text ist zurueck: ' + JSON.stringify(seite('Alpha').content));

                head('Eine Seite anlegen');
                v.currentPage = v.pages.filter(function (p) { return p.id === 'a'; })[0];
                v.linkAndCreate('Neu');
                ok(v.pages.length === 3, 'jetzt drei Seiten: ' + v.pages.length);

                head('Zuruecknehmen nimmt die neue Seite wieder weg');
                tick(function () {
                  undoKnopf().click();
                  tick(function () {
                    ok(v.pages.length === 2, 'wieder zwei Seiten: ' + v.pages.length);
                    ok(v.pages.filter(function (p) { return p.title === 'Neu'; }).length === 0, 'die neue Seite ist weg');
                    ok(!seite('Neu').id, 'im Speicher steht sie nicht mehr');
                    ende();
                  });
                });
              });
            });
          });
        });
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_undo1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Am Server: loeschen, zuruecknehmen - beides muss am Server ankommen.
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        var v = vm();
        ok(!!v, 'die App ist da');
        ok(v.pages.length === 2, 'zwei Seiten: ' + v.pages.length);

        head('Loeschen und zuruecknehmen am Server');
        v.deletePage('b');
        v.confirmDelete();
        ok(v.pages.length === 1, 'geloescht: ' + v.pages.length);
        v.rueckgaengig();
        ok(v.pages.length === 2, 'zurueckgeholt: ' + v.pages.length);
        ok(v.pages.filter(function (p) { return p.title === 'Beta'; }).length === 1, 'Beta ist wieder da');
        setTimeout(ende, 600);
      }, 2500);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a', 'text': 'A', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000'},
    {'title': 'Beta', 'sw-id': 'b', 'text': 'B', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'undo': Wiki('undo', TIDDLER, titel='Zuruecknehmen', skript=teil2,
                     ersetzungen=[("        createApp({",
                                   "        window.__vm = createApp({")])}
server, thread, port = starten(wikis)

fehler_gesamt = 0


def drucken(name, text):
    print('%-22s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
    print()


try:
    text = bericht(dumpdom('_undo1.html', budget=120000))
    drucken('_undo1.html', text)
    fehler_gesamt += zahlen(text)[1]

    leeren()
    text2 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/undo/' % port, None, 120000))
    drucken('_undo2.html', text2)
    fehler_gesamt += zahlen(text2)[1]
    server2 = anfragen()
finally:
    beenden(server)

loesch = [a for a in server2 if a.get('op') == 'delete'
          and any(t == 'Beta' for t in (a['nutzlast'].get('titles') or []))]
wieder = [t for a in server2 if a.get('op') == 'save'
          for t in (a['nutzlast'].get('tiddlers') or [])
          if t.get('title') == 'Beta']
print('Loeschen am Server: %s' % ('angekommen' if loesch else 'fehlt'))
print('Zurueckgeholte Seite am Server: %s' % ('angekommen' if wieder else 'fehlt'))
if not loesch or not wieder:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0], fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
