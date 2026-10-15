"""Der Warnhinweis unter file:///: sobald eine Seite bearbeitet und
gespeichert wurde, erinnert SimpleWiki daran, die Datei zu sichern.

Im Browserbetrieb liegen Aenderungen nur im Browserspeicher; die Datei
auf der Platte bleibt zurueck, bis der Mensch sie erneut sichert. Die
Warnung besteht aus zwei Zeichen:

  * einem roten, pulsierenden Punkt am Zahnrad (.datei-warn-punkt),
  * einem pulsierenden roten Rand am Knopf "Als Datei sichern"
    (.datei-warn-rand) mit einer Zeile Text darueber.

Sie verschwindet mit dem Sichern als Datei und uebersteht ein Neuladen
(localStorage simplewiki_datei_warnung). Am Server gibt es keine Datei
zu sichern - dort darf die Warnung nie erscheinen.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen
from mwsserver import Wiki, starten, beenden, leeren

seiten = [
    {"id": "1", "title": "Alpha", "content": "# Alpha\n\nText.", "links": [],
     "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Beta", "content": "# Beta", "links": [], "tags": [],
     "created": "x", "updated": "x"},
]

GEMEINSAM = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      function punkt() { return q('.datei-warn-punkt'); }
      function rand() { return q('.settings-btn.datei-warn-rand'); }
      function warnText() { var p = q('.datei-warn-hinweis'); return p ? p.textContent.trim() : ''; }
      function sichernKnopf() { return all('.settings-btn').filter(function (b) { return /Als Datei sichern|Save as file/.test(b.textContent); })[0]; }
      function bearbeiten() { return all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0]; }
      function speichern() { return all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0]; }
      function merker() { return localStorage.getItem('simplewiki_datei_warnung') || ''; }
      function banner() { var p = q('.hinweis'); return p ? p.textContent.trim() : ''; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
"""

# ---------------------------------------------------------------- Teil 1
# Bearbeiten, speichern, warnen - und mit dem Sichern aufraeumen.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + GEMEINSAM + r"""
      setTimeout(function () {
        log.push('--- Vor jeder Aenderung: keine Warnung');
        ok(!punkt(), 'kein Warnpunkt am Zahnrad');
        ok(!rand(), 'kein roter Rand am Sicherungs-Knopf');
        ok(warnText() === '', 'keine Warnzeile');
        ok(merker() === '', 'nichts im Merker');

        log.push('--- Seite bearbeiten und speichern');
        bearbeiten().click();
        setTimeout(function () {
          /* In den Text schreiben statt window.__ed zu rufen: mdEditor
             ist ein Vue-Proxy, und der Proxy reicht die Aenderung als
             "mismatched transaction" an ProseMirror weiter (siehe
             einrueckungEinrichten). Ein echter Tastendruck geht an
             ProseMirror vorbei. */
          var feld = q('.toastui-editor-contents[contenteditable=true]');
          if (feld) { feld.focus(); document.execCommand('insertText', false, 'Neu.'); }
          setTimeout(function () {
            speichern().click();
            setTimeout(function () {
              log.push('--- Jetzt steht die Warnung');
              ok(!!punkt(), 'der Warnpunkt sitzt am Zahnrad');
              ok(!!rand(), 'der Sicherungs-Knopf traegt den roten Rand');
              ok(warnText().length > 10, 'die Warnzeile ist gefuellt: [' + warnText().slice(0, 40) + '...]');
              ok(merker() === '1', 'die Warnung steht im Merker: [' + merker() + ']');
              ok((q('.settings-toggle').getAttribute('aria-label') || '').length > 0,
                 'das Zahnrad nennt den Grund im aria-label');

              log.push('--- Als Datei sichern raeumt die Warnung weg');
              sichernKnopf().click();
              setTimeout(function () {
                ok(window.__name === 'simplewiki.html', 'die Datei heisst simplewiki.html: ' + window.__name);
                ok(!punkt(), 'der Warnpunkt ist weg');
                ok(!rand(), 'der rote Rand ist weg');
                ok(warnText() === '', 'die Warnzeile ist weg');
                ok(merker() === '', 'der Merker ist leer');
                ok((banner() || '').indexOf('Speicherort') >= 0,
                   'der Banner nennt den Speicherort: [' + (banner() || '').slice(0, 60) + ']');
                ende();
              }, 400);
            }, 700);
          }, 700);
        }, 3000);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_dw1.html', teil1, seiten, startpage='1')

# ---------------------------------------------------------------- Teil 2
# Ein gemerkter Stand: die Warnung kommt beim Neuladen wieder.
mkcopy.PRE_SCRIPT = ("<script>try{localStorage.setItem('simplewiki_datei_warnung','1');}"
                     "catch(e){}</script>")

teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + GEMEINSAM + r"""
      setTimeout(function () {
        log.push('--- Warnung aus dem Merker beim Start');
        ok(!!punkt(), 'der Warnpunkt ist gleich da');
        ok(!!rand(), 'der rote Rand ist gleich da');
        ok(warnText().length > 10, 'die Warnzeile ist gleich da');

        log.push('--- Und wieder weg mit dem Sichern');
        sichernKnopf().click();
        setTimeout(function () {
          ok(!punkt(), 'der Warnpunkt ist weg');
          ok(!rand(), 'der rote Rand ist weg');
          ok(merker() === '', 'der Merker ist leer');
          ende();
        }, 400);
      }, 2000);
    })();
    </script>
"""
kopie2 = build('_dw2.html', teil2, seiten, startpage='1')

# ---------------------------------------------------------------- Teil 3
# Am Server gibt es keine Datei zu sichern: keine Warnung.
from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nText.', 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000', 'reihenfolge': '0000'},
    {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta', 'tags': '',
     'created': '20260203100500000', 'modified': '20260203100500000', 'reihenfolge': '0001'},
    {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
]

teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + GEMEINSAM + r"""
      setTimeout(function () {
        log.push('--- Am Server: bearbeiten und speichern');
        ok(!punkt(), 'am Server kein Warnpunkt beim Laden');
        bearbeiten().click();
        setTimeout(function () {
          var feld = q('.toastui-editor-contents[contenteditable=true]');
          if (feld) { feld.focus(); document.execCommand('insertText', false, 'Am Server.'); }
          setTimeout(function () {
            speichern().click();
            setTimeout(function () {
              ok(!punkt(), 'am Server kein Warnpunkt nach dem Speichern');
              ok(!rand(), 'am Server kein roter Rand');
              ok(warnText() === '', 'am Server keine Warnzeile');
              ok(merker() === '', 'am Server nichts gemerkt');
              ende();
            }, 900);
          }, 700);
        }, 3000);
      }, 2000);
    })();
    </script>
"""
def drucken(name, textx):
    print('%-22s %s' % (name, textx.split('\n')[-1] if textx else 'KEIN REPORT'))
    for z in textx.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
    print()

fehler_gesamt = 0

text1 = bericht(dumpdom('_dw1.html', budget=120000))
text2 = bericht(dumpdom('_dw2.html', budget=120000))
drucken('_dw1.html', text1)
drucken('_dw2.html', text2)
fehler_gesamt += zahlen(text1)[1] + zahlen(text2)[1]

wikis = {'warn': Wiki('warn', TIDDLER, titel='Warn-Wiki', skript=teil3)}
server, thread, port = starten(wikis)
try:
    leeren()
    text3 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/warn/' % port, None, 120000))
finally:
    beenden(server)
print('%-22s %s' % ('_dw3_server.html', text3.split('\n')[-1] if text3 else 'KEIN REPORT'))
for z in text3.split('\n'):
    if z.startswith('FAIL'):
        print('    ' + z)
print()
fehler_gesamt += zahlen(text3)[1]

print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text1)[0] + zahlen(text2)[0] + zahlen(text3)[0], fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
