import sys, io, re, json, subprocess, os, html as htmlmod
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, ziel
mkcopy.EXTRA_REPLACEMENTS = []

seiten = [
    {"id": "1", "title": "Alpha", "content": "# Alpha\n\nText mit <script>alert(1)</script>", "links": ["Beta"], "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "3", "title": "Gamma", "content": "# Gamma", "links": [], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Export im Browser ausloesen und den Datei-Inhalt abfangen.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          [].slice.call(document.querySelectorAll('.settings-btn'))[0].click();
          setTimeout(function () {
            ok(!!window.__blob, 'Datei erzeugt');
            window.__blob.text().then(function (text) {
              window.__text = text;
              ok(text.indexOf('<!DOCTYPE html>') === 0, 'beginnt mit doctype');
              ok(window.__name === 'simplewiki.html', 'Dateiname: ' + window.__name);

              /* Der Aufbau muss in der Datei stehen - sonst zeigt sie
                 beim Oeffnen nichts an. */
              ok(text.indexOf('id="app"') > 0, 'Container app vorhanden');
              ok(text.indexOf('class="header"') > 0, 'Kopfzeile vorhanden');
              ok(text.indexOf('side-panel toc-panel') > 0, 'Inhaltsverzeichnis vorhanden');
              ok(text.indexOf('side-panel refs-panel') > 0, 'Verweis-Panel vorhanden');
              ok(text.indexOf('class="footer"') > 0, 'Fusszeile vorhanden');
              ok(text.indexOf('v-for') > 0, 'Vue-Anweisungen vorhanden');
              ok(text.indexOf('VORLAGE_HTML') > 0, 'Vorlage im Skript');

              var treffer = text.match(/<script id="simplewiki-daten"[^>]*>([\s\S]*?)<\/script>/);
              var daten = JSON.parse(treffer[1].replace(/\\u003c/g, '<'));
              ok(daten.seiten.length === 3, 'drei Seiten drin');
              ok(daten.seiten.map(function (s) { return s.title; }).join('|') === 'Alpha|Beta|Gamma',
                 'Reihenfolge drin: ' + daten.seiten.map(function (s) { return s.title; }).join('|'));
              ok(daten.seiten[0].content.indexOf('<script>') >= 0, 'Inhalt mit spitzen Klammern unversehrt');

              /* Datei-Inhalt fuer den naechsten Schritt ausgeben: als
                 Textarea, weil der DOM-Serializer sie maskiert. */
              var feld = document.createElement('textarea');
              feld.id = 'export';
              /* als Kindknoten, nicht ueber .value: der DOM-Serializer
                 schreibt bei textarea den Rohwert */
              feld.textContent = text;
              document.body.appendChild(feld);
              log.push('>>> AUSGABE');
              out();
            });
          }, 800);
        }, 800);
      }, 1500);
    })();
    </script>
"""
build('_exp1.html', teil1, seiten)

dom = dumpdom('_exp1.html', budget=90000)
fehler_gesamt = 0

print('=== Teil 1: Export im Browser ===')
print(bericht(dom))
fehler_gesamt += len(re.findall(r'(?m)^FAIL ', bericht(dom)))

# ---------------------------------------------------------------- Teil 2
# Die gesicherte Datei wirklich auf die Platte schreiben und öffnen.
m = re.search(r'<textarea id="export">(.*?)</textarea>', dom, re.S)
if not m:
    print('\n=== Teil 2: kein Datei-Inhalt im Dump ===')
    raise SystemExit(1)

exportiert = htmlmod.unescape(m.group(1))
with io.open(ziel('_exportiert.html'), 'w', encoding='utf-8') as fh:
    fh.write(exportiert)
print('\n=== Teil 2: gesicherte Datei geschrieben ===')
print('Groesse: %d KB, Zeilen: %d' % (len(exportiert.encode()) // 1024, exportiert.count('\n')))

teil2 = r"""
    <script>
    /* Frischer Browser: localStorage leeren, damit wirklich die Datei
       geprueft wird und nicht der Stand des letzten Laufs. */
    try { localStorage.clear(); } catch (e) {}
    </script>
"""
pruefskript = r"""
    <script>
    setTimeout(function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        ok(q('.header') !== null, 'Oberflaeche ist da: ' + (q('.header') ? 'Kopfzeile gefunden' : 'KEINE Oberflaeche'));
        ok(q('.content-title') !== null, 'Seitenanzeige da');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite geoeffnet: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(q('.preview') && q('.preview').textContent.indexOf('alert(1)') >= 0, 'Inhalt mit spitzen Klammern da');
        q('.menu-toggle').click();
        setTimeout(function () {
          var titel = all('.toc-item-title').map(function (t) { return t.textContent.trim(); });
          ok(titel.join('|') === 'Alpha|Beta|Gamma', 'Reihenfolge aus der Datei: ' + titel.join('|'));
          ok(all('.toc-grip').length === 3, 'Griffe vorhanden: ' + all('.toc-grip').length);
          q('.settings-toggle').click();
          setTimeout(function () {
            ok(all('.settings-btn').length === 2, 'Sichern/Laden vorhanden');
            ok(q('.refs-toggle') !== null, 'Verweis-Knopf vorhanden');
            all('.footer .btn').length;
            ok(!!q('.footer .btn'), 'Fusszeile bedienbar');
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 600);
        }, 600);
      }, 1600);
    });
    </script>
"""
with io.open(ziel('_exportiert.html'), encoding='utf-8') as fh:
    h = fh.read()
h = h.replace('<body>', '<body>\n' + teil2, 1)
h = h.replace('</body>', pruefskript + '</body>', 1)
with io.open(ziel('_exportiert.html'), 'w', encoding='utf-8') as fh:
    fh.write(h)

print('\n=== Teil 3: gesicherte Datei wieder geoeffnet ===')
teil3 = bericht(dumpdom('_exportiert.html', budget=90000))
print(teil3 if teil3 else 'KEIN REPORT')
fehler_gesamt += len(re.findall(r'(?m)^FAIL ', teil3))

print()
print('>>> ' + ('%d FEHLGESCHLAGEN' % fehler_gesamt if fehler_gesamt else 'ALLE BESTANDEN'))
sys.exit(1 if fehler_gesamt else 0)