"""Ein Export aus dem Server ist ein eigenes Datei-Wiki.

Tiddlyhost liefert die Shell mit drei Meta-Zeilen aus (simplewiki-server,
simplewiki-status-url, simplewiki-data-url). Eine gesicherte Datei bringt
diese Zeilen mit, weil die Vorlage beim Ausliefern kopiert wurde - der
Server dahinter ist aber nicht mehr da.

Die Datei muss das merken und wie jedes andere file://-Wiki arbeiten:

  1. Sie ist ein Datei-Wiki: kein Serverhinweis, Titel und Untertitel
     sind anklickbar (nicht vom Server verwaltet).
  2. "Als Datei sichern" entfernt die drei Server-Metas; Titel,
     Untertitel und Datenblock bleiben.
  3. Die so gesicherte Datei wieder geoeffnet ist ebenfalls ein
     Datei-Wiki mit bearbeitbarem Titel und Untertitel.

Der Serverfall selbst steht in t_tiddlyhost.py - dort antwortet der
Server unter demselben Origin, und die Wiki bleibt im Serverbetrieb.
"""

import sys, os, io, re, json, html as htmlmod
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, ziel, zahlen

ISO = '2026-01-01T00:00:00.000Z'
SEITEN = [
    {'id': 'a', 'title': 'Erste', 'content': '# Erste\n\nEin Text.',
     'links': [], 'tags': [], 'created': ISO, 'updated': ISO},
    {'id': 'b', 'title': 'Zweite', 'content': '# Zweite\n\nNoch ein Text.',
     'links': [], 'tags': [], 'created': ISO, 'updated': ISO},
]
DATEN = {
    'version': 1, 'startseite': 'a', 'sprache': 'de', 'thema': 'light',
    'palette': 'pergament', 'seiten': SEITEN,
}

TITEL = 'Mein neues Wiki'
UNTERTITEL = 'opencode ist cool :)'

# Die ausgelieferte Seite: Titel, Untertitel und die drei Server-Metas
# im Kopf, dazu die Dateninsel. Genau das, was Tiddlyhost ausliefert.
mkcopy.EXTRA_REPLACEMENTS = [(
    '    <meta name="simplewiki-title" content="">\n'
    '    <meta name="simplewiki-subtitle" content="">\n',
    '    <meta name="simplewiki-title" content="%s">\n'
    '    <meta name="simplewiki-subtitle" content="%s">\n'
    '    <meta name="simplewiki-server" content="tiddlyhost">\n'
    '    <meta name="simplewiki-status-url" content="http://ddd.tiddlyhost.local:8080/simplewiki/status">\n'
    '    <meta name="simplewiki-data-url" content="http://ddd.tiddlyhost.local:8080/simplewiki/data">\n'
    % (TITEL, UNTERTITEL),
)]

TEIL1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function knopf(muster) {
        return [].slice.call(document.querySelectorAll('.settings-btn'))
                .filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      function titel() { return q('.header h1'); }
      function untertitel() { return q('.kopf-untertitel'); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }

      setTimeout(function () {
        log.push('--- Der Export ist ein Datei-Wiki');
        ok(!!q('.header h1'), 'Oberflaeche ist da');
        ok(!q('.mws-hinweis'), 'kein Serverhinweis');
        ok(titel() && titel().textContent.indexOf('Mein neues Wiki') >= 0,
           'Titel aus dem Kopf: ' + (titel() ? titel().textContent.trim() : '-'));
        ok(titel() && titel().className.indexOf('kopf-titel-editierbar') >= 0,
           'Titel ist anklickbar');
        ok(untertitel() && untertitel().textContent.trim() === 'opencode ist cool :)',
           'Untertitel aus dem Kopf: ' + (untertitel() ? untertitel().textContent.trim() : '-'));
        ok(untertitel() && untertitel().className.indexOf('kopf-untertitel-editierbar') >= 0,
           'Untertitel ist anklickbar');

        log.push('--- Titel und Untertitel lassen sich bearbeiten');
        titel().click();
        setTimeout(function () {
          ok(!!q('.kopf-titel-feld'), 'Klick auf den Titel oeffnet das Eingabefeld');
          ok(q('.kopf-titel-feld') && q('.kopf-titel-feld').value === 'Mein neues Wiki',
             'Feld traegt den Titel: ' + (q('.kopf-titel-feld') ? q('.kopf-titel-feld').value : '-'));
          if (q('.kopf-titel-feld')) {
            q('.kopf-titel-feld').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
          }
          setTimeout(function () {
            untertitel().click();
            setTimeout(function () {
              ok(!!q('.kopf-untertitel-feld'), 'Klick auf den Untertitel oeffnet das Eingabefeld');
              ok(q('.kopf-untertitel-feld') && q('.kopf-untertitel-feld').value === 'opencode ist cool :)',
                 'Feld traegt den Untertitel: ' + (q('.kopf-untertitel-feld') ? q('.kopf-untertitel-feld').value : '-'));
              if (q('.kopf-untertitel-feld')) {
                q('.kopf-untertitel-feld').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
              }
              setTimeout(function () {
                log.push('--- Als Datei sichern');
                q('.settings-toggle').click();
                setTimeout(function () {
                  ok(!!knopf('Als Datei sichern|Save as file'), 'Knopf "Als Datei sichern" da');
                  knopf('Als Datei sichern|Save as file').click();
                  setTimeout(function () {
                    ok(!!window.__blob, 'Datei erzeugt');
                    ok(window.__name === 'simplewiki.html', 'Dateiname: ' + window.__name);
                    if (!window.__blob) { ende(); return; }
                    window.__blob.text().then(function (text) {
                      ok(text.indexOf('<meta name="simplewiki-server"') < 0,
                         'keine Server-Meta simplewiki-server');
                      ok(text.indexOf('<meta name="simplewiki-status-url"') < 0,
                         'keine Server-Meta simplewiki-status-url');
                      ok(text.indexOf('<meta name="simplewiki-data-url"') < 0,
                         'keine Server-Meta simplewiki-data-url');
                      ok(text.indexOf('<meta name="simplewiki-title" content="Mein neues Wiki"') >= 0,
                         'Titel steht im Kopf der Datei');
                      ok(text.indexOf('<meta name="simplewiki-subtitle" content="opencode ist cool :)"') >= 0,
                         'Untertitel steht im Kopf der Datei');
                      var m = text.match(/<script id="simplewiki-daten"[^>]*>([\s\S]*?)<\/script>/);
                      ok(!!m, 'Datenblock vorhanden');
                      if (m) {
                        var d = JSON.parse(m[1].replace(/\\u003c/g, '<'));
                        ok(d.seiten.length === 2, 'Seiten im Datenblock: ' + d.seiten.length);
                        ok(d.seiten.map(function (s) { return s.title; }).join('|') === 'Erste|Zweite',
                           'Reihenfolge im Datenblock: ' + d.seiten.map(function (s) { return s.title; }).join('|'));
                      }
                      var feld = document.createElement('textarea');
                      feld.id = 'export';
                      feld.textContent = text;
                      document.body.appendChild(feld);
                      ende();
                    });
                  }, 800);
                }, 600);
              }, 150);
            }, 150);
          }, 150);
        }, 150);
      }, 1600);
    })();
    </script>
"""

build('_sf1.html', TEIL1, SEITEN, seed=False, daten=DATEN)

print('=== Teil 1: Export aus dem Server, als Datei geoeffnet ===')
dom = dumpdom('_sf1.html', budget=120000)
text1 = bericht(dom)
print(text1 if text1 else 'KEIN REPORT')
bestanden, fehler = zahlen(text1)

m = re.search(r'<textarea id="export">(.*?)</textarea>', dom, re.S)
if not m:
    print('\n=== Teil 2: kein Datei-Inhalt im Dump ===')
    raise SystemExit(1)

exportiert = htmlmod.unescape(m.group(1))
with io.open(ziel('_sf2.html'), 'w', encoding='utf-8') as fh:
    fh.write(exportiert)
print('\n=== Teil 2: gesicherte Datei geschrieben ===')
print('Groesse: %d KB' % (len(exportiert.encode()) // 1024))

# Die gesicherte Datei wieder oeffnen - wie die Person es tut: frischer
# Browser, kein Speicher aus dem ersten Lauf.
TEIL3 = r"""
    <script>
    try { localStorage.clear(); } catch (e) {}
    </script>
"""
PRUEF3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        ok(!!q('.header h1'), 'Oberflaeche ist da');
        ok(!q('.mws-hinweis'), 'kein Serverhinweis');
        ok(q('.header h1') && q('.header h1').textContent.indexOf('Mein neues Wiki') >= 0,
           'Titel: ' + (q('.header h1') ? q('.header h1').textContent.trim() : '-'));
        ok(q('.kopf-untertitel') && q('.kopf-untertitel').textContent.trim() === 'opencode ist cool :)',
           'Untertitel: ' + (q('.kopf-untertitel') ? q('.kopf-untertitel').textContent.trim() : '-'));
        ok(q('.header h1') && q('.header h1').className.indexOf('kopf-titel-editierbar') >= 0,
           'Titel ist bearbeitbar');
        ok(q('.kopf-untertitel') && q('.kopf-untertitel').className.indexOf('kopf-untertitel-editierbar') >= 0,
           'Untertitel ist bearbeitbar');
        q('.header h1').click();
        setTimeout(function () {
          ok(!!q('.kopf-titel-feld'), 'Titel wird zum Eingabefeld');
          if (q('.kopf-titel-feld')) {
            q('.kopf-titel-feld').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
          }
          setTimeout(function () {
            ok(q('.content-title') && q('.content-title').textContent.trim() === 'Erste',
               'Startseite aus der Datei: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 200);
        }, 200);
      }, 1600);
    })();
    </script>
"""

with io.open(ziel('_sf2.html'), encoding='utf-8') as fh:
    h = fh.read()
h = mkcopy.hauptskripte(h, pre=TEIL3, script=PRUEF3)
with io.open(ziel('_sf2.html'), 'w', encoding='utf-8') as fh:
    fh.write(h)

print('\n=== Teil 3: gesicherte Datei wieder geoeffnet ===')
text3 = bericht(dumpdom('_sf2.html', budget=120000))
print(text3 if text3 else 'KEIN REPORT')
bestanden += zahlen(text3)[0]
fehler += len(re.findall(r'(?m)^FAIL ', text3))

print()
print('>>> ' + ('%d FEHLGESCHLAGEN' % fehler if fehler else 'ALLE BESTANDEN'))
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (bestanden, fehler))
sys.exit(1 if fehler else 0)
