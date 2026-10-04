import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
import mwsfixture
from mwsfixture import bauen
from _hilfe import dumpdom, bericht, zahlen

# ------------------------------------------------------------------ Inhalt
def zw(jahr, monat, tag, stunde, minute, sekunde, ms):
    return '%d%02d%02d%02d%02d%02d%03d' % (jahr, monat, tag, stunde, minute, sekunde, ms)

# Konvention §102: der Tiddler heisst wie die Seite, die Kennung
# wandert als sw-id mit.
ERSTE = {
    'title': 'Erste Seite', 'sw-id': 'b1',
    # beide Schreibweisen, beide Richtungen: hin zur zweiten und
    # zurueck zur ersten
    'text': '# Erste\n\nSiehe [[Zweite Seite]] und [Text](wiki:Zweite Seite).',
    'tags': '[[beispiel]]',
    'created': zw(2026, 7, 4, 12, 0, 0, 0),
    'modified': zw(2026, 7, 4, 12, 0, 0, 0),
    'reihenfolge': '0001',
    'thema': 'dark', 'sprache': 'de',
}
ZWEITE = {
    'title': 'Zweite Seite', 'sw-id': 'b2',
    'text': '# Zweite\n\nZurueck mit [Text](wiki:Erste Seite) und [[Erste Seite]].',
    'tags': '',
    'created': zw(2026, 7, 4, 12, 1, 0, 0),
    'modified': zw(2026, 7, 4, 12, 1, 0, 0),
    'reihenfolge': '0000',
}
STANDARD = {'title': '$:/DefaultTiddlers', 'text': 'Erste Seite'}
BAG = {'title': '$:/bag-info', 'text': '{"bag":"default"}'}

# ---------------------------------------------------------------- Teil 1
# Die Auswahl: Marker mit Inhalt, Marker leer, gar kein Marker
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        log.push('--- Die Wahl faellt am Marker');
        var gesetzt = !!document.querySelector('script.tiddlywiki-tiddler-store');
        log.push('INFO Marker im Dokument: ' + gesetzt + ', Inhalt: ' +
                 (document.querySelector('script.tiddlywiki-tiddler-store') || { textContent: '' }).textContent.slice(0, 12) + '...');

        log.push('--- Seiten und Reihenfolge aus dem Marker');
        ok(titel().join('|') === 'Zweite Seite|Erste Seite',
           'zwei Seiten in der Reihenfolge aus reihenfolge: ' + titel().join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Erste Seite',
           'Startseite aus $:/DefaultTiddlers: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.bag-info'), '$:/bag-info ist keine Seite');
        ok(document.body.className.indexOf('dark') >= 0, 'dunkel aus den Feldern der Startseite');
        ok(localStorage.getItem('simplewiki_pages') === null, 'nichts im Browser');

        log.push('--- Verweise in beiden Schreibweisen');
        var html = q('.preview').innerHTML;
        log.push('INFO Vorschau: ' + html.replace(/\s+/g, ' ').slice(0, 400));
        var mitId = (html.match(/data-wiki-link=/g) || []).length;
        ok(mitId === 2, 'zwei klickbare Verweise auf der Startseite: ' + mitId);
        ok(html.indexOf('wiki-link-fehlt') < 0, 'die Ziele sind vorhanden, nichts rot');

        log.push('--- Klick auf einen Verweis');
        var link = q('.preview a[data-wiki-link="Zweite Seite"]');
        ok(!!link, 'der Verweis ist ein Knopf in der Seite');
        if (link) link.click();
        setTimeout(function () {
          ok(q('.content-title') && q('.content-title').textContent.trim() === 'Zweite Seite',
             'der Verweis fuehrt zur zweiten Seite: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

          log.push('--- Verweise in beide Richtungen');
          q('.refs-toggle').click();
          setTimeout(function () {
            var refs = q('.refs-panel') ? q('.refs-panel').textContent : (document.body.textContent || '');
            ok(/Erste Seite/.test(refs), 'die zweite Seite verweist zurueck: ' + refs.replace(/\s+/g, ' ').slice(0, 120));
            q('.refs-toggle').click();
            setTimeout(ende, 400);
          }, 900);
        }, 900);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 2
# Aus einer Datei heraus kann man nicht schreiben - und das muss man sagen
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function hinweis() { var h = q('.hinweis'); return h ? h.textContent.trim() : ''; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        log.push('--- Aus einer Datei ist nicht zu schreiben');
        log.push('INFO Pfad: ' + location.pathname.slice(-40));
        all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
        setTimeout(function () {
          if (window.__ed) window.__ed.setMarkdown('# Erste\n\nGeaendert.');
          setTimeout(function () {
            all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0].click();
            setTimeout(function () {
              log.push('--- Der Versuch muss sichtbar scheitern');
              ok(hinweis().length > 0, 'es steht ein Hinweis: "' + hinweis() + '"');
              ok(/nicht auf dem server gespeichert|not saved on the server/i.test(hinweis()),
                 'sagt, dass es nicht gespeichert wurde: ' + hinweis());
              ok(!q('.nurlesen-hinweis'),
                 'kein Nur-Lesen-Hinweis: das ist kein Rechteproblem, sondern eine fehlende Verbindung');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 1500);
          }, 700);
        }, 2800);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 3
# Marker ohne Inhalt: dann gilt der Browser, auch wenn die Datei vom
# Server kommt
BROWSER = mkcopy._maskieren(json.dumps([{
    'id': 'x1', 'title': 'Aus dem Browser', 'content': '# Aus dem Browser',
    'links': [], 'tags': [], 'created': '2026-03-01T10:00:00.000Z',
    'updated': '2026-03-01T10:00:00.000Z'
}], ensure_ascii=False))
VORAB = ('<script>try{localStorage.setItem("simplewiki_pages",' + BROWSER + ');'
         'localStorage.setItem("simplewiki_startpage","x1");}catch(e){}</' + 'script>')

teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        log.push('--- Marker vorhanden, aber leer');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Aus dem Browser',
           'der Browser liefert die Seite: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.mws-hinweis'), 'kein Serverhinweis');
        ok(all('.toc-item-title').length === 1, 'genau eine Seite: ' + all('.toc-item-title').length);
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 4
# Ohne jede Spur eines Markers: ganz normale Datei im Browser
BROWSER2 = mkcopy._maskieren(json.dumps([{
    'id': 'y1', 'title': 'Ganz normal', 'content': '# Ganz normal',
    'links': [], 'tags': [], 'created': '2026-03-01T10:00:00.000Z',
    'updated': '2026-03-01T10:00:00.000Z'
}], ensure_ascii=False))
VORAB2 = ('<script>try{localStorage.setItem("simplewiki_pages",' + BROWSER2 + ');'
          'localStorage.setItem("simplewiki_startpage","y1");}catch(e){}</' + 'script>')

teil4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        log.push('--- Kein Marker: die gewoehnliche Datei');
        ok(!document.querySelector('script.tiddlywiki-tiddler-store'), 'kein Marker im Dokument');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Ganz normal',
           'der Browser liefert die Seite: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.mws-hinweis') && !q('.nurlesen-hinweis'), 'kein Serverhinweis, kein Nur-Lesen-Hinweis');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

TIDDLER = [ERSTE, ZWEITE, STANDARD, BAG]

kopien = [
    bauen('_datei_server.html', TIDDLER, skript=teil1),
    bauen('_datei_schreiben.html', TIDDLER, skript=teil2),
    bauen('_datei_markerleer.html', TIDDLER, skript=teil3, vorab=VORAB, marker_leer=True),
    bauen('_datei_ohne.html', TIDDLER, skript=teil4, vorab=VORAB2,
          marker_keiner=True),
]

# Beim letzten ist der Marker schon weg, und zwar durch die Fixture
# oben: marker_keuner=True. Ein zweites, handgeschnittenes Entfernen
# gab es hier früher - es hat aber nichts entfernt, sondern die Datei
# verdoppelt.
#
# Gesucht wurde nach '<script class="tiddlywiki-tiddler-store"' vor dem
# ersten echten Tag. Diese Zeichenkette stand im Dokumentationskommentar
# - dieselbe Abschrift, die jetzt aus dem Kommentar rausmusste. Also
# fand die Suche immer die Abschrift, schnitt sie heraus und liess die
# echte Datei unangetastet: zwei Kills, der zweite davon ein No-op.
#
# Kaum war die Abschrift weg, fand die Suche nichts, i war -1, und aus
# h[:i] + h[j+9:] wurde h[:-1] + h[8:] - die komplette Datei nochmal
# hinterher. Der Browser zeigt das erste Dokument und ignoriert den Rest,
# also sind fast alle Pruefungen weiterhin gruen gewesen, und nur eine
# ist gescheitert.
#
# Genau deshalb wird jetzt geprueft, dass jede Kopie genau ein Dokument
# enthaelt. Das ist derselbe Fehler wie beim Marker: eine Pruefung, die
# das Wegzaehlen ueberlaesst, sieht genau das nicht.
for pfad in kopien:
    ist, passt = mkcopy.groesse_waechter(os.path.basename(pfad))
    if not passt:
        print('FEHLER: %s ist %d Bytes gross - das Dokument steht '
              'wahrscheinlich doppelt darin' % (os.path.basename(pfad), ist))
        sys.exit(1)

fehler = 0
for pfad in kopien:
    text = bericht(dumpdom(os.path.basename(pfad), budget=120000))
    name = os.path.basename(pfad)
    print('%-22s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
            fehler += 1
        if z.startswith('INFO'):
            print('    ' + z)

bestanden = 0
for pfad in kopien:
    bestanden += zahlen(bericht(dumpdom(os.path.basename(pfad), budget=120000)))[0]

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (bestanden, fehler))
sys.exit(1 if fehler else 0)