"""Markdown hin und zurueck: die offene Seite als .md sichern und
.md-Dateien als Seiten einlesen.

Der Inhalt einer Seite ist schon Markdown - der Austausch wandelt
deshalb nichts um. Beim Sichern traegt der Dateiname den Titel (ohne
Zeichen, die kein Dateisystem mag), beim Lesen wird er der Titel der
neuen Seite. Anders als beim Laden einer Wiki-Datei ersetzt der Import
nichts, sondern haengt an. Genau das pruefen die drei Teile: Sichern im
Browser, Einlesen im Browser (samt Titeln, Anhaengen und Verweisen) und
beides am Server.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

# Ohne Werkzeugleiste ist der Sichern-Knopf nicht im Bild; der
# Schalter wird deshalb vor dem Start gesetzt.
mkcopy.PRE_SCRIPT = '<script>try{localStorage.setItem("simplewiki_toolbar","1");}catch(e){}</script>'

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha\n\nzwei drei vier",
     "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "b", "title": "Beta", "content": "# Beta", "links": [], "tags": [],
     "created": "x", "updated": "x"},
    {"id": "c", "title": "Bericht / 2026", "content": "Ein Bericht",
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Im Browser: die offene Seite als .md sichern, Name aus dem Titel.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function wzBtn(titel) {
        return [].slice.call(document.querySelectorAll('.werkzeug-btn')).filter(function (b) { return b.getAttribute('title') === titel; })[0];
      }
      function waehle(titel) {
        var z = [].slice.call(document.querySelectorAll('.toc-item-title')).filter(function (s) { return s.textContent.trim() === titel; })[0];
        if (z) z.closest('.toc-item').click();
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        head('Die offene Seite sichern');
        var knopf = wzBtn('Diese Seite als Markdown-Datei sichern');
        ok(!!knopf, 'es gibt den Knopf');
        if (!knopf) { ende(); return; }
        knopf.click();
        setTimeout(function () {
          ok(window.__name === 'Alpha.md', 'Dateiname aus dem Titel: ' + window.__name);
          window.__blob.text().then(function (text) {
            ok(text === '# Alpha\n\nzwei drei vier', 'der Inhalt geht unveraendert durch: ' + JSON.stringify(text));

            head('Der Titel wird zum Dateinamen, Zeichen die kein Dateisystem mag werden ersetzt');
            waehle('Bericht / 2026');
            setTimeout(function () {
              wzBtn('Diese Seite als Markdown-Datei sichern').click();
              setTimeout(function () {
                ok(window.__name === 'Bericht - 2026.md', 'Dateiname: ' + window.__name);
                window.__blob.text().then(function (t2) {
                  ok(t2 === 'Ein Bericht', 'Inhalt kam mit: ' + JSON.stringify(t2));
                  ende();
                });
              }, 150);
            }, 150);
          });
        }, 150);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_md1.html', teil1, seiten, startpage='a')
mkcopy.PRE_SCRIPT = ''

# ---------------------------------------------------------------- Teil 2
# Im Browser: .md-Dateien werden neue Seiten, der Dateiname der Titel.
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function titel() { return all('.toc-item-title').map(function (s) { return s.textContent.trim(); }); }
      function mdFeld() { return q('input[accept*=".md"]'); }
      /* Ein Datei-Feld laesst sich nicht mit echten Dateien fuellen,
         ohne dass der Test auf echtes Lesen von der Platte wartet -
         unter virtueller Zeit ein Wettlauf. Hier werden dem Feld
         stattdessen kleine Stellvertreter untergeschoben, die sofort
         antworten; das Datei-Feld selbst bleibt echt. */
      function setzeDateien(feld, liste) {
        var kuenstlich = liste.map(function (f) {
          return { name: f.name, text: function () { return Promise.resolve(f.text); } };
        });
        Object.defineProperty(feld, 'files', { value: kuenstlich, configurable: true });
        feld.dispatchEvent(new Event('change'));
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });


      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        head('Ausgangslage');
        ok(titel().indexOf('Alpha') >= 0, 'Alpha ist da');
        ok(titel().indexOf('Notiz') < 0, 'Notiz noch nicht');

        head('Zwei Markdown-Dateien einlesen');
        q('.settings-toggle').click();
        setTimeout(function () {
          var feld = mdFeld();
          ok(!!feld, 'es gibt das Datei-Feld fuer Markdown');
          if (!feld) { ende(); return; }
          setzeDateien(feld, [
            { name: 'Notiz.md', text: '# Notiz\n\nSiehe [[Alpha]]' },
            { name: 'Alpha.md', text: 'Kopie von Alpha' }
          ]);

          setTimeout(function () {
            ok(titel().indexOf('Notiz') >= 0, 'Notiz wurde angelegt');
            ok(titel().indexOf('Alpha 2') >= 0, 'der doppelte Name wird eindeutig: ' + titel().join(', '));
            ok(titel().indexOf('Alpha') >= 0, 'die alte Alpha bleibt');
            var h = q('.hinweis');
            ok(!!h && /2/.test(h.textContent), 'Hinweis nennt die Zahl: ' + (h ? h.textContent : ''));

            head('Inhalt und Verweis landen im Speicher');
            var gespeichert = [];
            try { gespeichert = JSON.parse(localStorage.getItem('simplewiki_pages') || '[]'); } catch (e) {}
            var notiz = gespeichert.filter(function (p) { return p.title === 'Notiz'; })[0];
            ok(!!notiz, 'Notiz steht im Browserspeicher');
            ok(notiz && /\[\[Alpha\]\]/.test(notiz.content), 'der Text blieb');
            ok(notiz && (notiz.links || []).indexOf('Alpha') >= 0, 'der Verweis wurde notiert');
            ende();
          }, 300);
        }, 500);
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_md2.html', teil2, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 3
# Am Server: sichern und einlesen schreiben Tiddler.
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function titel() { return all('.toc-item-title').map(function (s) { return s.textContent.trim(); }); }
      function wzBtn(t) { return all('.werkzeug-btn').filter(function (b) { return b.getAttribute('title') === t; })[0]; }
      function setzeDateien(feld, liste) {
        var kuenstlich = liste.map(function (f) {
          return { name: f.name, text: function () { return Promise.resolve(f.text); } };
        });
        Object.defineProperty(feld, 'files', { value: kuenstlich, configurable: true });
        feld.dispatchEvent(new Event('change'));
      }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };

      setTimeout(function () {
        head('Die offene Seite am Server als Markdown sichern');
        var druck = wzBtn('Diese Seite als Markdown-Datei sichern');
        ok(!!druck, 'der Sichern-Knopf ist da');
        if (druck) druck.click();
        setTimeout(function () {
          ok(window.__name === 'Alpha.md', 'Dateiname: ' + window.__name);

          head('Eine Markdown-Datei als Seite schreiben');
          q('.settings-toggle').click();
          setTimeout(function () {
            var feld = q('input[accept*=".md"]');
            ok(!!feld, 'es gibt das Datei-Feld');
            if (feld) setzeDateien(feld, [{ name: 'Neu.md', text: '# Neu\n\nfrisch' }]);
            setTimeout(function () {
              ok(titel().indexOf('Neu') >= 0, 'Neu steht im Verzeichnis');
              ende();
            }, 400);
          }, 500);
        }, 200);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nzwei drei vier', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000',
     'toolbar': 'true'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]
wikis = {'md': Wiki('md', TIDDLER, titel='Markdown', skript=teil3)}
server, thread, port = starten(wikis)

fehler_gesamt = 0
try:
    text = bericht(dumpdom('_md1.html', budget=120000))
    text2 = bericht(dumpdom('_md2.html', budget=120000))

    def drucken(name, textx):
        print('%-22s %s' % (name, textx.split('\n')[-1] if textx else 'KEIN REPORT'))
        for z in textx.split('\n'):
            if z.startswith('FAIL'):
                print('    ' + z)
        print()

    drucken('_md1.html', text)
    drucken('_md2.html', text2)
    fehler_gesamt += zahlen(text)[1] + zahlen(text2)[1]

    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/md/' % port, None, 120000))
    drucken('_md3_server.html', text3)
    fehler_gesamt += zahlen(text3)[1]
finally:
    beenden(server)

# Die neue Seite muss als Tiddler beim Server angekommen sein.
saves = [a for a in anfragen() if a.get('op') == 'save' and a['nutzlast'].get('tiddlers')]
neu = [t for a in saves for t in a['nutzlast']['tiddlers']
       if t.get('title') == 'Neu' and 'frisch' in (t.get('text') or '')]
print('Markdown-Seite am Server: %s' % ('angekommen' if neu else 'fehlt'))
if not neu:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0] + zahlen(text3)[0], fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
