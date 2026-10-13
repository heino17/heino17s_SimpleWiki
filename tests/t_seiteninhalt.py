"""Das Inhaltsverzeichnis der offenen Seite.

Ein Schalter in den Einstellungen legt ueber den Text ein Verzeichnis
seiner Ueberschriften. Die Liste kommt aus der fertigen Vorschau, nicht
aus dem Quelltext - ein Codeblock faellt damit von allein heraus. Ein
Klick springt zur Ueberschrift, sonst passiert nichts.

Teil 1 prueft das Ein- und Ausschalten im Browser samt Speicher, Teil 2
den Stand am Server (Feld am Tiddler und die Schreibanfrage).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkcopy import build
from _hilfe import dumpdom, dumpdom_url, bericht, zahlen

INHALT = ("# Titel\n\n"
          "## Erster Abschnitt\n\n"
          "Ein Text.\n\n"
          "### Unterpunkt\n\n"
          "```\n# kein Titel\n```\n\n"
          "## Zweiter Abschnitt\n")

seiten = [
    {"id": "a", "title": "Handbuch", "content": INHALT,
     "links": [], "tags": [], "created": "x", "updated": "x"},
]

KOPF = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function nav() { return q('.seiteninhalt'); }
      function namen() { return all('.seiteninhalt-liste a').map(function (a) { return a.textContent.trim(); }); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""

# ---------------------------------------------------------------- Teil 1
# Im Browser: aus, einschalten, Liste pruefen, wieder aus.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Ausgangslage: aus');
        ok(!nav(), 'kein Verzeichnis zu sehen');

        q('.settings-toggle').click();
        setTimeout(function () {
          var schalter = q('#settings-seiteninhalt');
          ok(!!schalter, 'der Schalter steht in den Einstellungen');

          head('Einschalten');
          schalter.click();
          setTimeout(function () {
            ok(!!nav(), 'jetzt steht das Verzeichnis');
            ok(namen().join('|') === 'Titel|Erster Abschnitt|Unterpunkt|Zweiter Abschnitt',
               'Ueberschriften in Reihenfolge: ' + namen().join('|'));
            ok(namen().indexOf('kein Titel') < 0, 'der Codeblock zaehlt nicht mit');
            var a0 = q('.seiteninhalt-liste a');
            var ziel = document.getElementById(a0.getAttribute('href').slice(1));
            ok(!!ziel && /^H[123]$/.test(ziel.tagName), 'das Sprungziel gibt es: ' + (ziel && ziel.tagName));
            var ebenen = all('.seiteninhalt-liste li').map(function (x) { return x.className; });
            ok(ebenen[0].indexOf('ebene-1') >= 0 && ebenen[1].indexOf('ebene-2') >= 0
               && ebenen[2].indexOf('ebene-3') >= 0, 'Ebenen: ' + ebenen.join(', '));
            ok(localStorage.getItem('simplewiki_seiteninhalt') === '1', 'im Browserspeicher an');

            head('Wieder ausschalten');
            q('#settings-seiteninhalt').click();
            setTimeout(function () {
              ok(!nav(), 'das Verzeichnis ist weg');
              ok((localStorage.getItem('simplewiki_seiteninhalt') || '') === '', 'im Speicher aus');
              ende();
            }, 250);
          }, 300);
        }, 500);
      }, 2000);
    })();
    </script>
"""
kopie1 = build('_seiteninhalt1.html', teil1, seiten, startpage='a')

# ---------------------------------------------------------------- Teil 2
# Am Server: das Feld am Tiddler schaltet ein, Ausschalten schreibt.
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOPF + r"""
      setTimeout(function () {
        head('Das Feld am Tiddler schaltet ein');
        ok(!!nav(), 'das Verzeichnis steht von Anfang an');
        ok(namen().length === 4, 'vier Ueberschriften: ' + namen().length);

        head('Ausschalten schreibt das Feld');
        q('.settings-toggle').click();
        setTimeout(function () {
          q('#settings-seiteninhalt').click();
          setTimeout(function () {
            ok(!nav(), 'das Verzeichnis ist weg');
            ende();
          }, 400);
        }, 400);
      }, 2000);
    })();
    </script>
"""

from mwsserver import Wiki, starten, beenden, anfragen, leeren

TIDDLER = [
    {'title': 'Handbuch', 'sw-id': 'sh1', 'text': INHALT, 'tags': '',
     'created': '20260203100000000', 'modified': '20260203100000000',
     'reihenfolge': '0000', 'seiteninhalt': 'true'},
    {'title': '$:/DefaultTiddlers', 'text': 'Handbuch'},
]
wikis = {'inhalt': Wiki('inhalt', TIDDLER, titel='Handbuch', skript=teil2)}
server, thread, port = starten(wikis)

fehler_gesamt = 0


def drucken(name, text):
    print('%-24s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
    print()


try:
    text = bericht(dumpdom('_seiteninhalt1.html', budget=120000))
    drucken('_seiteninhalt1.html', text)
    fehler_gesamt += zahlen(text)[1]

    leeren()
    text2 = bericht(dumpdom_url('http://127.0.0.1:%d/wiki/inhalt/' % port, None, 120000))
    drucken('_seiteninhalt2.html', text2)
    fehler_gesamt += zahlen(text2)[1]
    server2 = anfragen()
finally:
    beenden(server)

saves = [a for a in server2 if a.get('op') == 'save']
aus = [t for a in saves for t in (a['nutzlast'].get('tiddlers') or [])
       if t.get('title') == 'Handbuch' and t.get('seiteninhalt') == 'false']
print('Ausschalten als Feld am Tiddler: %s' % ('angekommen' if aus else 'fehlt'))
if not aus:
    fehler_gesamt += 1

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen'
      % (zahlen(text)[0] + zahlen(text2)[0], fehler_gesamt))

sys.exit(1 if fehler_gesamt else 0)
