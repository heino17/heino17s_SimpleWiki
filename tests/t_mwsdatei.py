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
# Die Auswahl: Tiddler vom Server, und keiner davon
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-panel .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        log.push('--- Die Wahl faellt an den Tiddlern im Aufbau');
        var gesetzt = !!(window.$tw && window.$tw.preloadTiddlers.length);
        log.push('INFO Tiddler im Aufbau: ' + (window.$tw ? window.$tw.preloadTiddlers.length : 0) +
                 ', Aufrufe im Dokument: ' + all('script').filter(function (s) {
                     return /^\s*\$tw\.preloadTiddler\(/.test(s.textContent || '');
                 }).length);

        log.push('--- Seiten und Reihenfolge aus den Tiddlern');
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
# Der Server schickt keine Tiddler: dann gilt der Browser. Ein Wiki ohne
# Seiten kommt bei MWS nicht vor - zu jeder gehoeren die Verwaltungs-
# Tiddler - aber genau darin liegt die Gefahr: faellt einer davon aus,
# darf die Wiki nicht zur Stilllegnung schreiten und jede Eingabe im
# Browser lassen.
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
        log.push('--- Keine Tiddler vom Server');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Aus dem Browser',
           'der Browser liefert die Seite: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.mws-hinweis'), 'kein Serverhinweis');
        ok(!q('.nurlesen-hinweis'), 'kein Nur-Lesen-Hinweis');
        ok(all('.toc-panel .toc-item-title').length === 1, 'genau eine Seite: ' + all('.toc-panel .toc-item-title').length);
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
    bauen('_datei_ohne_tiddler.html', [], skript=teil3, vorab=VORAB),
]

# Jede Kopie muss genau ein Dokument enthalten. Ein Test, der das
# Wegzaehlen ueberlaesst, sieht genau das nicht: die Datei stand einmal
# doppelt darin, der Browser zeigte das erste Dokument und ignorierte
# den Rest, und fast alle Pruefungen blieben gruen.
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