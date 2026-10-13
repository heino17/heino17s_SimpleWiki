import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

# Der Test braucht Zugriff auf die beiden Auspraegungen. Das geht nicht
# durch die Oberflaeche - also haengt die Testkopie einen Haken an die
# eine Stelle, an der die Wahl faellt, genau wie mkcopy es mit dem
# Editor-Haken macht.
WAHL = """        const MWS_TIDDLER = mwsTiddlerLesen();
        const SPEICHER = (MWS_TIDDLER && MWS_TIDDLER.length)
            ? new MwsStore(MWS_TIDDLER)
            : LocalStore;"""

HAKEN = WAHL + """
        window.__sp = { SPEICHER: SPEICHER, LocalStore: LocalStore,
                        MwsStore: MwsStore, vertrag: SPEICHER_METHODEN };"""

# ---------------------------------------------------------------- Teil 1
# Im Browser: beide Auspraegungen bieten denselben Vertrag
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      var VERTRAG = ['laden', 'uebernehmen', 'seiteSichern', 'seiteLoeschen',
                     'startseiteSetzen', 'themaSetzen', 'paletteSetzen', 'eigeneFarbenSetzen', 'spracheSetzen', 'toolbarSetzen', 'seiteninhaltSetzen'];
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        var sp = window.__sp;
        ok(!!sp, 'Testhaken gefunden');
        if (!sp) { ende(); return; }

        log.push('--- Es ist der Browserspeicher');
        ok(sp.SPEICHER.art === 'browser', 'art: ' + sp.SPEICHER.art);
        ok(!document.querySelector('.mws-hinweis'), 'kein Serverhinweis');

        log.push('--- Beide Auspraegungen haben denselben Vertrag');
        function methodenVon(obj) {
          var raus = [];
          for (var k in obj) { if (typeof obj[k] === 'function') raus.push(k); }
          return raus.sort();
        }
        var server = new sp.MwsStore([]);
        var imBrowser = methodenVon(sp.LocalStore);
        var amServer = methodenVon(server);
        var fehltBrowser = VERTRAG.filter(function (m) { return typeof sp.LocalStore[m] !== 'function'; });
        var fehltServer = VERTRAG.filter(function (m) { return typeof server[m] !== 'function'; });
        ok(fehltBrowser.length === 0, 'dem Browser fehlt nichts: ' + (fehltBrowser.join(',') || 'nichts'));
        ok(fehltServer.length === 0, 'dem Server fehlt nichts: ' + (fehltServer.join(',') || 'nichts'));
        ok(sp.vertrag.join(',') === VERTRAG.join(','),
           'der Vertrag im Programm: ' + sp.vertrag.join(','));
        ok(server.art === 'mws', 'der Server heisst sich mws: ' + server.art);

        log.push('--- laden() liefert bei beiden dieselben Felder');
        var l = Object.create(sp.LocalStore);
        var a = Object.keys(l.laden()).sort().join(',');
        var b = Object.keys(server.laden()).sort().join(',');
        ok(a === b, 'gleiche Feldnamen: ' + (a === b ? a : a + ' <> ' + b));

        log.push('--- Der Browserspeicher arbeitet mit dem, was er bekommt');
        /* Diese Versuche schreiben in dasselbe localStorage wie die
           laufende App. Darum wird der Stand gemerkt und danach
           wiederhergestellt - sonst vergleicht der naechste Abschnitt
           gegen eine kaputte Ausgangslage. */
        var stand = localStorage.getItem('simplewiki_pages');
        var eins = { id: 'a', title: 'Alpha', content: '# Alpha', links: [], tags: [] };
        var geaendert = { id: 'a', title: 'Alpha neu', content: '# anders', links: [], tags: [] };
        var neu = { id: 'b', title: 'Beta', content: '', links: [], tags: [] };
        l.seiten = [eins];
        l.seiteSichern(geaendert);
        ok(l.seiten.length === 1, 'ein bekanntes Blatt ersetzt statt daneben gelegt: ' + l.seiten.length);
        ok(l.seiten[0].title === 'Alpha neu', 'und zwar mit dem neuen Namen');
        l.seiteSichern(neu);
        ok(l.seiten.length === 2, 'ein unbekanntes Blatt kommt dazu: ' + l.seiten.length);

        log.push('--- Die Liste wird geaendert, nie ersetzt');
        var vorher = l.seiten;
        l.seiteLoeschen('a');
        ok(l.seiten === vorher, 'nach dem Loeschen dieselbe Liste');
        ok(l.seiten.length === 1 && l.seiten[0].id === 'b', 'nur die gesuchte Seite ist weg: ' + l.seiten.map(function (x) { return x.id; }).join('|'));
        var eigene = [{ id: 'z', title: 'Eigen', content: '', links: [], tags: [] }];
        l.uebernehmen(eigene);
        ok(l.seiten === eigene, 'uebernehmen zeigt auf die uebergebene Liste');

        localStorage.setItem('simplewiki_pages', stand);

        log.push('--- Und das laeuft im laufenden Betrieb wirklich ueber den Vertrag');
        var benutzt = [];
        ['laden', 'uebernehmen', 'seiteSichern', 'seiteLoeschen', 'startseiteSetzen', 'themaSetzen', 'paletteSetzen', 'eigeneFarbenSetzen', 'spracheSetzen', 'toolbarSetzen', 'seiteninhaltSetzen'].forEach(function (m) {
          var original = sp.SPEICHER[m];
          sp.SPEICHER[m] = function () { benutzt.push(m); return original.apply(this, arguments); };
        });
        var gespeichert = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]');
        var palStand = localStorage.getItem('simplewiki_palette');
        document.querySelectorAll('.toc-item-title')[0].click();
        setTimeout(function () {
          var bearbeiten = [].slice.call(document.querySelectorAll('.footer .btn')).filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0];
          bearbeiten.click();
          setTimeout(function () {
            [].slice.call(document.querySelectorAll('.footer .btn')).filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0].click();
            setTimeout(function () {
              ok(benutzt.indexOf('seiteSichern') >= 0, 'beim Speichern: ' + benutzt.join('|'));
              var neuListe = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]');
              ok(neuListe.length === gespeichert.length, 'keine Seite dazu gekommen: ' + gespeichert.length + ' -> ' + neuListe.length);
              document.querySelector('.theme-toggle').click();
              setTimeout(function () {
                ok(benutzt.indexOf('themaSetzen') >= 0, 'beim Farbwechsel: ' + benutzt.join('|'));
                document.querySelector('.settings-toggle').click();
                setTimeout(function () {
                  var pal = document.getElementById('settings-palette');
                  var andere = [].slice.call(pal.options).filter(function (o) { return o.value && o.value !== pal.value; })[0];
                  if (andere) { pal.value = andere.value; pal.dispatchEvent(new Event('change', { bubbles: true })); }
                  setTimeout(function () {
                    ok(benutzt.indexOf('paletteSetzen') >= 0, 'beim Wechsel der Farbwelt: ' + benutzt.join('|'));
                    var jetzt = localStorage.getItem('simplewiki_palette');
                    ok(jetzt === 'nord', 'Farbwelt steht im Speicher: ' + jetzt);
                    /* Den Stand zurueckbauen, damit dieser Lauf nichts hinterlaesst. */
                    if (palStand === null) localStorage.removeItem('simplewiki_palette');
                    else localStorage.setItem('simplewiki_palette', palStand);
                    var aus = document.getElementById('settings-startpage');
                    var anders = [].slice.call(aus.options).filter(function (o) { return o.value && o.value !== aus.value; })[0];
                    if (anders) { aus.value = anders.value; aus.dispatchEvent(new Event('change', { bubbles: true })); }
                    setTimeout(function () {
                      ok(benutzt.indexOf('startseiteSetzen') >= 0, 'beim Wechsel der Startseite: ' + benutzt.join('|'));
                      ende();
                    }, 700);
                  }, 700);
                }, 700);
              }, 700);
            }, 900);
          }, 2800);
        }, 800);
      }, 2500);

      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 2
# Auf dem Server: dieselbe Abstraktion, andere Auspraegung
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      var VERTRAG = ['laden', 'uebernehmen', 'seiteSichern', 'seiteLoeschen',
                     'startseiteSetzen', 'themaSetzen', 'paletteSetzen', 'eigeneFarbenSetzen', 'spracheSetzen', 'toolbarSetzen', 'seiteninhaltSetzen'];
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        var sp = window.__sp;
        ok(!!sp, 'Testhaken gefunden');
        if (!sp) { ende(); return; }

        log.push('--- Auf dem Server ist die andere Auspraegung dran');
        ok(sp.SPEICHER.art === 'mws', 'art: ' + sp.SPEICHER.art);
        ok(!!document.querySelector('.mws-hinweis'), 'Serverhinweis steht da');
        var fehlt = VERTRAG.filter(function (m) { return typeof sp.SPEICHER[m] !== 'function'; });
        ok(fehlt.length === 0, 'dem Server fehlt nichts: ' + (fehlt.join(',') || 'nichts'));
        ok(sp.vertrag.join(',') === VERTRAG.join(','), 'derselbe Vertrag wie im Browser');

        log.push('--- Und sie verhaelt sich wie die aus dem Browser');
        var l = Object.create(sp.LocalStore);
        ok(Object.keys(l.laden()).sort().join(',') === Object.keys(sp.SPEICHER.laden()).sort().join(','),
           'laden() liefert dieselben Felder');
        var g = sp.SPEICHER.laden();
        ok(g.vorhanden === true, 'vorhanden: ' + g.vorhanden);
        ok(g.seiten.length === 2, 'zwei Seiten: ' + g.seiten.length);
        ok(g.thema === '' && g.sprache === '' && g.palette === '',
           'ohne sprache, thema und palette auf der Startseite: ' + g.thema + '/' + g.sprache + '/' + g.palette);
        ok(g.wikiTitel === 'Vertrag', 'wikiTitel: ' + g.wikiTitel);
        ok(g.nurLesen === false, 'nurLesen: ' + g.nurLesen);
        ok(g.startseite === 'a1',
           'startseite als Kennung aufgeloest: ' + g.startseite);
        ok(g.seiten[0].id === 'a1' && g.seiten[0].title === 'Alpha',
           'die Seite: id=' + g.seiten[0].id + ' title=' + g.seiten[0].title);


        log.push('--- Kennung und Name werden auseinander gehalten');
        ok(sp.SPEICHER.titelVon('a1') === 'Alpha',
           'titelVon: der Tiddler heisst wie die Seite: ' + sp.SPEICHER.titelVon('a1'));
        ok(sp.SPEICHER.idVonTitel('Alpha') === 'a1',
           'idVonTitel: und die Kennung kommt aus sw-id: ' + sp.SPEICHER.idVonTitel('Alpha'));
        ok(sp.SPEICHER.idVonTitel('gibtsnicht') === '',
           'idVonTitel von einem unbekannten Namen: "' + sp.SPEICHER.idVonTitel('gibtsnicht') + '"');

        log.push('--- list und read spricht der Serverspeicher an');
        sp.SPEICHER.alleTiddlerLesen().then(function (alle) {
          ok(Array.isArray(alle), 'list liefert eine Liste: ' + typeof alle);
          var namen = alle.map(function (t) { return t.title; });
          ok(namen.indexOf('Alpha') >= 0 && namen.indexOf('Beta') >= 0 &&
             namen.indexOf('$:/DefaultTiddlers') >= 0,
             'list liefert die Seiten und den Systemtiddler: ' + namen.join('|'));
          /* read fragt nach dem Namen des Tiddlers - nach der Kennung
             gibt es nichts, denn die heisst nicht so. */
          return sp.SPEICHER.tiddlerLesen('Alpha');
        }).then(function (t) {
          ok(!!t && t['sw-id'] === 'a1',
             'read liefert den Tiddler mit sw-id: ' + JSON.stringify(t && t['sw-id']));
          return sp.SPEICHER.tiddlerLesen('a1');
        }).then(function (t) {
          ok(t === null, 'read nach der Kennung findet nichts: ' + JSON.stringify(t));
          return sp.SPEICHER.tiddlerLesen('gibtsnicht');
        }).then(function (t) {
          ok(t === null, 'read von etwas, das es nicht gibt: ' + JSON.stringify(t));
          ok(typeof sp.LocalStore.alleTiddlerLesen !== 'function',
             'der Browserspeicher hat kein list - es gibt nichts zu fragen');
          /* Zuletzt, damit die beiden Abfragen oben noch etwas zu lesen
             finden: geloescht wird der Tiddler mit dem Namen der Seite. */
          log.push('--- Loeschen geht den Tiddler-Namen, nicht die Kennung');
          return sp.SPEICHER.seiteLoeschen('a1');
        }).then(function () {
          ende();
        }).catch(function (e) { ok(false, 'Fehler bei list oder read: ' + e.message); ende(); });
      }, 2500);

      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
    })();
    </script>
"""

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
]

mkcopy.EXTRA_REPLACEMENTS = [(WAHL, HAKEN)]
kopie = build('_vertrag.html', teil1, seiten, startpage='a')

# --- Teil 2 braucht einen Server, weil nur dort der Server-Speicher läuft
from mwsserver import Wiki, starten, beenden, anfragen, leeren

# Die Konvention aus §102: der Tiddler heisst wie die Seite, die
# Kennung wandert als sw-id mit.
TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000'},
    {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta', 'tags': '',
     'created': '20260203100500000', 'modified': '20260203100500000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'vertrag': Wiki('vertrag', TIDDLER, titel='Vertrag', skript=teil2,
                         ersetzungen=[(WAHL, HAKEN)])}
server, thread, port = starten(wikis)

fehler_gesamt = 0
try:
    text1 = bericht(dumpdom('_vertrag.html', budget=120000))
    print('%-22s %s' % ('_vertrag.html', text1.split('\n')[-1] if text1 else 'KEIN REPORT'))
    for z in text1.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
            fehler_gesamt += 1
    print()
    leeren()
    text2 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/vertrag/' % port, None, 120000))
    print('%-22s %s' % ('_vertrag_server.html', text2.split('\n')[-1] if text2 else 'KEIN REPORT'))
    for z in text2.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
            fehler_gesamt += 1
finally:
    beenden(server)

geloescht = [a for a in anfragen() if a.get('op') == 'delete']
print('delete beim Server: %s' % [a['nutzlast'].get('titles') for a in geloescht])

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text1)[0] + zahlen(text2)[0], fehler_gesamt))
sys.exit(1 if fehler_gesamt else 0)