import sys, os, re, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe, dumpdom, bericht, ziel, app_da

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "2026-01-01T10:00:00.000Z", "updated": "2026-01-01T10:00:00.000Z"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "2026-01-01T10:00:00.000Z", "updated": "2026-01-01T10:00:00.000Z"},
]

# Datei einer fremden Anwendung mit Angaben OBEN, die SimpleWiki nicht kennt
FREMDE = {
    "version": 1,
    "seiten": [
        {"id": "f1", "title": "Fremd", "content": "# Fremd\n\nText", "links": [], "tags": [],
         "created": "2026-03-03T08:00:00.000Z", "updated": "2026-03-03T08:00:00.000Z"},
        {"id": "f2", "title": "Zweite", "content": "# Zweite", "links": ["Fremd"], "tags": [],
         "created": "2026-03-03T08:00:00.000Z", "updated": "2026-03-03T08:00:00.000Z"},
    ],
    "startseite": "f2",
    "sprache": "de",
    "thema": "light",
    "autor": "Fremdes Werk",
    "herkunft": "MWS",
    "exportdatum": "2026-03-03T09:00:00.000Z",
}

# ---------------------------------------------------------------- Teil 1
# Aufgaben 1 und 3: obere Fremdfelder ueberstehen, Hinweis ist sichtbar
script1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      function hinweisLog() {
        var arr = [];
        new MutationObserver(function () {
          var h = q('.hinweis');
          if (h && h.textContent.trim()) arr.push(h.textContent.trim());
        }).observe(document.body, { childList: true, subtree: true, characterData: true });
        return arr;
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      var gemeldet = hinweisLog();
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          head('Hinweis auf den Zwei-Schritt-Weg');
          var hinweis = q('.settings-hint.data-hinweis');
          ok(!!hinweis, 'Hinweis vorhanden');
          ok(hinweis && hinweis.textContent.indexOf('JSON') >= 0, 'nennt JSON: ' + (hinweis ? hinweis.textContent.trim().slice(0, 60) + '...' : '-'));
          ok(hinweis && hinweis.textContent.indexOf('Als Datei sichern') >= 0, 'nennt den zweiten Schritt');
          ok(hinweis && hinweis.textContent.split(/[.!?]/).filter(function (x) { return x.trim(); }).length >= 2, 'zwei Saetze');

          head('Fremde Datei mit Angaben oben einlesen');
          var feld = q('input.datei-feld');
          var dt = new DataTransfer();
          dt.items.add(new File([window.__FREMDE], 'fremd.json', { type: 'application/json' }));
          feld.files = dt.files;
          feld.dispatchEvent(new Event('change', { bubbles: true }));
          var versuche = 0;
          (function warten() {
            versuche++;
            if (gemeldet.length || versuche > 40) {
              setTimeout(function () {
                ok(gemeldet.length > 0 && gemeldet[gemeldet.length - 1].indexOf('2') >= 0,
                   'eingelesen: ' + (gemeldet.length ? gemeldet[gemeldet.length - 1] : 'kein Hinweis'));

                head('Angaben oben ueberstehen den Weg zurueck');
                all('.settings-btn').forEach(function () {});
                var knoepfe = all('.settings-btn');
                var jsonKnopf = knoepfe.filter(function (b) { return /JSON/.test(b.textContent); })[0];
                jsonKnopf.click();
                setTimeout(function () {
                  ok(window.__name === 'simplewiki.json', 'JSON-Datei: ' + window.__name);
                  window.__blob.text().then(function (text) {
                    var d = JSON.parse(text);
                    ok(d.autor === 'Fremdes Werk', 'autor erhalten: ' + d.autor);
                    ok(d.herkunft === 'MWS', 'herkunft erhalten: ' + d.herkunft);
                    ok(d.exportdatum === '2026-03-03T09:00:00.000Z', 'exportdatum erhalten: ' + d.exportdatum);
                    ok(d.version === 1, 'version geschrieben: ' + d.version);
                    ok(d.seiten.length === 2, 'Seiten geschrieben: ' + d.seiten.length);
                    ok(d.startseite === 'f2', 'startseite geschrieben: ' + d.startseite);
                    ok(d.thema === 'light', 'thema geschrieben: ' + d.thema);
                    ende();
                  });
                }, 900);
              }, 300);
              return;
            }
            setTimeout(warten, 200);
          })();
        }, 800);
      }, 1500);
    })();
    </script>
"""
kopie1 = build('_weg1.html',
               '<script>window.__FREMDE = ' + json.dumps(json.dumps(FREMDE, ensure_ascii=False)) + ';</script>' + script1,
               seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Aufgabe 2: leere Wiki-Datei. Zwei Kopien: eine holt die Datei, die
# andere ist die Datei selbst, die geoeffnet wird.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      /* Jeder Hinweis wird notiert: er verschwindet nach sechs Sekunden
         von selbst, und unter Virtual Time ist das schnell passiert. */
      var gemeldet = [];
      new MutationObserver(function () {
        var h = q('.hinweis');
        if (h) {
          var t = h.textContent.trim();
          if (t && gemeldet[gemeldet.length - 1] !== t) gemeldet.push(t);
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });

      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          var knoepfe = all('.settings-btn').map(function (b) { return b.textContent.trim(); });
          var leerKnopf = all('.settings-btn').filter(function (b) { return /Leeres Wiki|Export empty/.test(b.textContent); })[0];  /* nach Text, nicht nach Nummer */
          ok(!!leerKnopf, 'Knopf vorhanden: ' + knoepfe.join(' / '));
          ok(knoepfe.length >= 4, 'Knoepfe im Bereich Wiki-Daten: ' + knoepfe.join(' / '));
          leerKnopf.click();
          setTimeout(function () {
            ok(window.__name === 'simplewiki-leer.html', 'Dateiname: ' + window.__name);
            ok(!!window.__blob, 'Datei erzeugt');
            window.__blob.text().then(function (text) {
              var p=document.createElement('pre');p.id='exportiert';p.textContent=text;document.body.appendChild(p);
              ok(gemeldet.join(' | ').indexOf('simplewiki-leer') >= 0,
                 'Hinweis beim Sichern: ' + (gemeldet.join(' | ') || 'KEINER'));
              ende();
            });
          }, 900);
        }, 800);
      }, 1500);
    })();
    </script>
"""
kopie2 = build('_weg2.html', script2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# Die leere Datei wirklich auf die Platte schreiben, die Dateninsel
# pruefen, die Datei mit einer fremden Insel fuellen und dann oeffnen.
dom = dumpdom('_weg2.html', budget=60000)
exportiert = ''
m = re.search(r'<pre id="exportiert">([\s\S]*?)</pre>', dom)
if m:
    import html as H
    exportiert = H.unescape(m.group(1))
else:
    print('FEHLER: Kopie 2 hat die Datei nicht geliefert')
    sys.exit(1)

print('\n--- Leere Datei von aussen beurteilt ---')
fehler = 0
ist_ok = lambda c, t: print('  %-46s %s' % (t, 'ok' if c else 'FEHLER')) or (0 if c else 1)

fehler += ist_ok(exportiert.startswith('<!DOCTYPE html>'), 'beginnt mit doctype')
insel = re.search(r'<script id="simplewiki-daten"[^>]*>([\s\S]*?)</script>', exportiert)
fehler += ist_ok(bool(insel), 'Dateninsel vorhanden mit id="simplewiki-daten"')
fehler += ist_ok('type="application/json"' in exportiert, 'type="application/json"')
daten = json.loads(insel.group(1)) if insel else {}
fehler += ist_ok(daten.get('version') == 1, 'version: %s' % daten.get('version'))
fehler += ist_ok(daten.get('seiten') == [], 'seiten ist leer: %r' % daten.get('seiten'))
fehler += ist_ok(daten.get('startseite') == '', 'startseite leer: %r' % daten.get('startseite'))
fehler += ist_ok('sprache' in daten and 'thema' in daten, 'sprache und thema vorhanden')
fehler += ist_ok('class="header"' in exportiert, 'Oberflaeche vorhanden')
fehler += ist_ok('VORLAGE_HTML' in exportiert, 'Anwendungscode vorhanden')
fehler += ist_ok(len(daten) == 5, 'genau die fuenf bekannten Felder: %s' % sorted(daten.keys()))

# Jetzt tun, was die fremde Anwendung tut: die Insel fuellen
mit_inhalt = dict(daten)
mit_inhalt['seiten'] = [
    {"id": "x1", "title": "Von MWS", "content": "# Von MWS\n\nSiehe [[Ziel]].",
     "links": [], "tags": ["extern"], "created": "2026-04-04T08:00:00.000Z",
     "updated": "2026-04-04T08:00:00.000Z", "mwsFeld": 7},
    {"id": "x2", "title": "Ziel", "content": "# Ziel", "links": [], "tags": [],
     "created": "2026-04-04T08:00:00.000Z", "updated": "2026-04-04T08:00:00.000Z"},
]
mit_inhalt['startseite'] = 'x1'
mit_inhalt['autor'] = 'MWS'
neu_insel = json.dumps(mit_inhalt, ensure_ascii=False).replace('<', '\\u003c')
fertig = exportiert[:insel.start(1)] + neu_insel + exportiert[insel.end(1):]

pruefskript = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p=document.getElementById('report'); if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);} p.textContent=log.join('\n'); }
      function ok(c, m) { if(!c) fails++; log.push((c?'OK   ':'FAIL ')+m); out(); }
      window.addEventListener('error', function(e){ ok(false,'JS-Fehler: '+e.message); });
      setTimeout(function () {
        ok(!!q('.content-title'), 'Oberflaeche da');
        ok(q('.content-title').textContent.trim() === 'Von MWS', 'gefuellte Insel wird gelesen: ' + (q('.content-title')?q('.content-title').textContent.trim():'-'));
        ok(q('.preview').textContent.indexOf('Siehe') >= 0, 'Inhalt da');
        q('.menu-toggle').click();
        setTimeout(function () {
          var titel = all('.toc-item-title').map(function(t){return t.textContent.trim();});
          ok(titel.join('|') === 'Von MWS|Ziel', 'Reihenfolge: ' + titel.join('|'));
          log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function(l){return /^OK|^FAIL/.test(l);}).length + ' BESTANDEN'));
          out();
        }, 700);
      }, 1800);
    })();
    </script>
    <script>try { localStorage.clear(); } catch (e) {}</script>
"""
with open(ziel('_weg_fertig.html'), 'w', encoding='utf-8') as fh:
    fh.write(fertig.replace('<body>', '<body>\n' + pruefskript, 1))

print('\n--- Gefuellte Vorlage geoeffnet (der Weg, den ein Kind geht) ---')
dom2 = dumpdom('_weg_fertig.html', budget=60000)
text2 = bericht(dom2)
fehler += len(re.findall(r'(?m)^FAIL ', text2))
if not app_da(dom2):
    print('  FEHLER: die gefuellte Datei zeigt keine Oberflaeche')
    fehler += 1
    text2 = text2 or 'KEIN REPORT'
print(text2)

print()
print('>>> ' + ('ALLE BESTANDEN' if fehler == 0 else '%d FEHLGESCHLAGEN' % fehler))
sys.exit(1 if fehler else 0)

# ---------------------------------------------------------------- Teil 4
# Die beiden Browser-Kopien am Ende durchlaufen lassen; pruefe() beendet
# das Skript und gibt den Exitcode vor.
print()
pruefe(kopie1, kopie2)
