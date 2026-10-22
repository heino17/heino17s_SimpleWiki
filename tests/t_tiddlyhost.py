import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from _hilfe import bericht, zahlen, dumpdom_url

# Der Test haengt einen Haken an die eine Stelle, an der die Wahl faellt -
# genau wie t_speicher.py. So kommt er an den Speicher, ohne durch die
# ganze Oberflaeche zu gehen.
WAHL = """        const MWS_TIDDLER = mwsTiddlerLesen();
        const SPEICHER = tiddlyhostServerAktiv()
            ? new TiddlyhostStore()
            : ((MWS_TIDDLER && MWS_TIDDLER.length)
                ? new MwsStore(MWS_TIDDLER)
                : LocalStore);"""

HAKEN = WAHL + """
        window.__th = { SPEICHER: SPEICHER, TiddlyhostStore: TiddlyhostStore,
                        LocalStore: LocalStore, vertrag: SPEICHER_METHODEN };"""

# ---------------------------------------------------------------- Testskript
# Laeuft im ausgelieferten Wiki auf dem Fixture-Server. Prueft in einem
# Durchgang: Erkennung, gleicher Vertrag, Insel gelesen, Schreiben als
# gebuendelter PUT mit If-Match, 409, Status-Anpassung, Abmelden.
skript = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      var VERTRAG = ['laden', 'uebernehmen', 'seiteSichern', 'seiteLoeschen',
                     'startseiteSetzen', 'themaSetzen', 'paletteSetzen', 'eigeneFarbenSetzen', 'spracheSetzen', 'toolbarSetzen', 'seiteninhaltSetzen'];
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      function warte(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

      setTimeout(function () {
        var sp = window.__th;
        ok(!!sp, 'Testhaken gefunden');
        if (!sp) { ende(); return; }

        log.push('--- Der Server wird erkannt');
        ok(!!document.querySelector('meta[name="simplewiki-server"][content="tiddlyhost"]'),
           'die Meta-Zeile simplewiki-server steht im Kopf');
        ok(sp.SPEICHER.art === 'tiddlyhost', 'art: ' + sp.SPEICHER.art);
        ok(sp.SPEICHER.serverseitig === true, 'serverseitig: ' + sp.SPEICHER.serverseitig);
        ok(!!document.querySelector('.mws-hinweis'), 'Serverhinweis steht da');
        var h = document.querySelector('.header h1');
        ok(h && h.textContent.indexOf('Tiddlyhost-Wiki') >= 0,
           'Kopf zeigt simplewiki-title: ' + (h ? h.textContent.trim() : '-'));
        var u = document.querySelector('.kopf-untertitel');
        ok(u && u.textContent.trim() === 'Klein und fein',
           'Kopf zeigt simplewiki-subtitle: ' + (u ? u.textContent.trim() : '-'));

        log.push('--- Derselbe Vertrag wie im Browser');
        ok(sp.vertrag.join(',') === VERTRAG.join(','), 'der Vertrag im Programm');
        var fehlt = VERTRAG.filter(function (m) { return typeof sp.SPEICHER[m] !== 'function'; });
        ok(fehlt.length === 0, 'dem Speicher fehlt nichts: ' + (fehlt.join(',') || 'nichts'));

        log.push('--- laden() liefert dieselben Felder wie der Browserspeicher');
        var l = Object.create(sp.LocalStore);
        ok(Object.keys(l.laden()).sort().join(',') === Object.keys(sp.SPEICHER.laden()).sort().join(','),
           'gleiche Feldnamen');

        log.push('--- Die Insel aus der Seite ist der Ausgangsstand');
        var g = sp.SPEICHER.laden();
        ok(g.vorhanden === true, 'vorhanden: ' + g.vorhanden);
        ok(g.seiten.length === 2, 'zwei Seiten: ' + g.seiten.length);
        ok(g.startseite === 'a1', 'startseite: ' + g.startseite);
        ok(g.thema === 'dark', 'thema aus der Insel: ' + g.thema);
        ok(g.sprache === 'en', 'sprache aus der Insel: ' + g.sprache);
        ok(g.seiten[0].title === 'Alpha', 'die erste Seite: ' + g.seiten[0].title);

        log.push('--- Eine Aenderung wird gebuendelt geschrieben');
        var vorher = log.filter(function (x) { return /^OK|^FAIL/.test(x); }).length;
        sp.SPEICHER.seiteSichern({ id: 'c3', title: 'Gamma', content: '# Gamma', links: [], tags: [] });
        warte(900).then(function () {
          return fetch('/__pruefstand', {}).catch(function () { return null; });
        }).then(function () {
          /* Statt einen eigenen Endpunkt zu bauen, liest der Test den
             Stand ueber den normalen Weg zurueck: ein zweiter GET der
             Insel. Was drinsteht, ist die Probe. */
          return fetch(document.querySelector('meta[name="simplewiki-data-url"]').content,
                       { headers: { 'X-Requested-With': 'fetch' } });
        }).then(function (r) { return r.json(); }).then(function (daten) {
          ok((daten.seiten || []).length === 3, 'die neue Seite ist in der Insel: ' + (daten.seiten || []).length);
          ok((daten.seiten || []).some(function (s) { return s.id === 'c3'; }),
             'und sie heisst Gamma');
          ok(daten.thema === 'dark', 'thema bleibt erhalten: ' + daten.thema);

          log.push('--- Der Konflikt: der Server hat inzwischen etwas anderes');
          /* Der Server wird von aussen auf eine neue Fassung gestellt
             (siehe Testende). Hier wird mit einer veralteten Fassung
             geschrieben - das muss 409 geben, ohne etwas zu ueberschreiben. */
          return erwarteKonflikt(sp.SPEICHER);
        }).then(function (ergebnis) {
          ok(ergebnis === 'konflikt', 'ein veraltetes If-Match gibt einen Konflikt: ' + ergebnis);

          log.push('--- status() wird auf die Form gebracht, die die App kennt');
          return sp.SPEICHER.status();
        }).then(function (st) {
          ok(!!st && st.isLoggedIn === true, 'angemeldet: ' + (st && st.isLoggedIn));
          ok(st.username === 'Testnutzer', 'der Name: ' + st.username);
          ok(st.bags[0].canUserWrite === true, 'Schreibrecht gemeldet');

          log.push('--- abmelden() spricht den Abmeldeweg an');
          return sp.SPEICHER.abmelden();
        }).then(function (ok2) {
          ok(ok2 === true, 'Abmelden gilt als gelungen: ' + ok2);
          return sp.SPEICHER.status();
        }).then(function (st) {
          ok(st.isLoggedIn === false, 'danach nicht mehr angemeldet: ' + st.isLoggedIn);
          ende();
        }).catch(function (e) { ok(false, 'Fehler: ' + e.message); ende(); });
      }, 1500);

      /* Ein Schreiben mit einer veralteten Fassung: der Server hat eine
         andere. Erwartet wird ein 409 und die Meldung des Konflikts. */
      function erwarteKonflikt(speicher) {
        return new Promise(function (fertig) {
          var gesehen = false;
          document.addEventListener('simplewiki:konflikt', function () { gesehen = true; });
          /* Den ETag im Speicher absichtlich veralten lassen. */
          speicher.etag = '"veraltet-0"';
          speicher.jetztSchreiben().then(function (r) {
            setTimeout(function () { fertig(gesehen ? 'konflikt' : 'kein Ereignis'); }, 200);
          });
        });
      }

      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (x) { return /^OK|^FAIL/.test(x); }).length + ' BESTANDEN')); out(); }
    })();
    </script>
"""

from tiddlyhostserver import Wiki, insel_aus_seiten, starten, beenden, anfragen, leeren

SEITEN = [
    {"id": "a1", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [],
     "created": "2026-02-03T10:00:00.000Z", "updated": "2026-02-03T10:00:00.000Z"},
    {"id": "b2", "title": "Beta", "content": "# Beta", "links": [], "tags": [],
     "created": "2026-02-03T10:05:00.000Z", "updated": "2026-02-03T10:05:00.000Z"},
]
INSEL = insel_aus_seiten(SEITEN, startseite='a1', sprache='en', thema='dark')

wikis = {'wiki': Wiki('wiki', insel=INSEL, skript=skript,
                      ersetzungen=[
                          (WAHL, HAKEN),
                          ('<meta name="simplewiki-title" content="">',
                           '<meta name="simplewiki-title" content="Tiddlyhost-Wiki">'),
                          ('<meta name="simplewiki-subtitle" content="">',
                           '<meta name="simplewiki-subtitle" content="Klein und fein">'),
                      ])}
server, thread, port = starten(wikis)

fehler_gesamt = 0
text = ''
try:
    leeren()
    dom = dumpdom_url('http://127.0.0.1:%d/wiki/wiki/' % port, None, 120000)
    text = bericht(dom)
    print('%-22s %s' % ('_tiddlyhost.html', text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
finally:
    beenden(server)

# Das Protokoll nach dem Lauf: die Wege, die die Wiki wirklich ging.
put = [a for a in anfragen() if a.get('weg') == 'PUT']
del_ = [a for a in anfragen() if a.get('weg') == 'DELETE']
print()
print('PUT-Aufrufe: %d' % len(put))
for a in put:
    print('    kopf=%r if_match=%r instanz=%s' % (
        a.get('kopf'), a.get('if_match'),
        ('ja' if isinstance(a.get('nutzlast'), dict) and 'seiten' in a['nutzlast'] else 'nein')))
print('DELETE /users/sign_out: %s' % [a['pfad'] for a in del_])

# Ein paar harte Proben am Protokoll - unabhaengig vom Browserbericht.
browser_ok, browser_fehler = zahlen(text)
protokoll = []


def pruefe(c, m):
    protokoll.append(bool(c))
    print(('    OK   ' if c else '    FAIL  ') + m)


pruefe(len(put) >= 1, 'die Wiki hat mindestens einmal per PUT geschrieben')
pruefe(put and all(a.get('kopf') == 'fetch' for a in put),
       'jeder PUT traegt X-Requested-With: fetch')
pruefe(all(isinstance(a.get('nutzlast'), dict) and 'seiten' in a['nutzlast'] for a in put),
       'jeder PUT traegt die Insel (seiten)')
pruefe(any(a.get('if_match') for a in put),
       'mindestens ein PUT trug ein If-Match')
pruefe(len(del_) == 1 and del_[0]['pfad'] == '/users/sign_out',
       'abgemeldet wurde ueber DELETE /users/sign_out')

proto_fehler = len([p for p in protokoll if not p])
gesamt_ok = browser_ok + (len(protokoll) - proto_fehler)
gesamt_fehler = browser_fehler + proto_fehler
print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (gesamt_ok, gesamt_fehler))
sys.exit(1 if gesamt_fehler else 0)
