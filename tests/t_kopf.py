import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe

seiten = [
    {"id": "1", "title": "Alpha", "content": "# Alpha\n\nText", "links": ["Beta"], "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Beta", "content": "# Beta", "links": ["Alpha"], "tags": [], "created": "x", "updated": "x"},
]

# ---------------------------------------------------------------- Teil 1
# Der Knopf im Kopf: vorhanden, beschriftet, schaltet den Fluss um
script1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      function knopf() { return q('.kopf-fluss'); }
      function ende() {
        log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Knopf im Kopf');
        ok(!!knopf(), 'Knopf vorhanden');
        ok(knopf() && /🌊/.test(knopf().textContent), 'mit Fluss-Symbol: ' + (knopf() ? knopf().textContent.trim() : '-'));
        ok(knopf() && /Fluss|River/.test(knopf().textContent), 'mit Text');
        ok(knopf() && knopf().closest('.header') !== null, 'er sitzt im Kopf');
        ok(knopf() && knopf().getAttribute('aria-pressed') === 'false', 'nicht gedrueckt: ' + (knopf() ? knopf().getAttribute('aria-pressed') : '-'));
        ok(knopf() && /öffnen|open/i.test(knopf().getAttribute('title')), 'Hinweis: ' + (knopf() ? knopf().getAttribute('title') : '-'));

        head('Neue Seite im Kopf');
        var neu = q('.kopf-neu');
        ok(!!neu, 'Knopf vorhanden');
        ok(neu && neu.closest('.header') !== null, 'er sitzt im Kopf');
        ok(neu && /➕/.test(neu.textContent), 'mit seinem Zeichen: ' + (neu ? neu.textContent.trim() : '-'));
        ok(neu && /Neue Seite|New Page/.test(neu.getAttribute('title')),
           'und einem Hinweis darauf: ' + (neu ? neu.getAttribute('title') : '-'));
        ok(neu && /Neue Seite|New Page/.test(neu.getAttribute('aria-label')), 'auch fuer Vorlese-Programme');
        /* Dicht links neben dem Verzeichnis. Ohne diese Nachbarschaft
           stand der Knopf allein beim Suchfeld: .menu-toggle trug
           "margin-left: auto" und schob den Leerraum vor sich her. */
        ok(neu && neu.nextElementSibling === q('.menu-toggle'),
           'unmittelbar links vom Verzeichnis-Knopf');
        ok(neu && Math.abs(neu.getBoundingClientRect().right + 12 -
           q('.menu-toggle').getBoundingClientRect().left) <= 1,
           'im selben Abstand wie die anderen: ' +
           Math.round(neu.getBoundingClientRect().right) + ' -> ' +
           Math.round(q('.menu-toggle').getBoundingClientRect().left));
        ok(neu && neu.closest('.kopf-werkzeuge') !== null,
           'die Knoepfe des Kopfs haengen an einer Gruppe');
        ok(!q('.toc-footer .new-page-btn'), 'im Verzeichnis steht er nicht mehr');
        /* Wie die anderen Schreibknoepfe verschwindet er, wer nicht
           schreiben darf - das prueft t_anmeldung.py am echten Server. */

        head('Reihenfolge der Knoepfe im Kopf');
        var reihenfolge = all('.header .btn, .header button').map(function (b) {
          if (b.className.indexOf('kopf-neu') >= 0) return 'neu';
          if (b.className.indexOf('menu-toggle') >= 0) return 'toc';
          if (b.className.indexOf('kopf-fluss') >= 0) return 'fluss';
          if (b.className.indexOf('refs-toggle') >= 0) return 'refs';
          if (b.className.indexOf('settings-toggle') >= 0) return 'settings';
          if (b.className.indexOf('theme-toggle') >= 0) return 'thema';
          return '?';
        }).join(' ');
        ok(reihenfolge === 'neu toc fluss refs settings thema', 'Reihenfolge: ' + reihenfolge);

        head('Einmal druecken: Fluss');
        knopf().click();
        setTimeout(function () {
          ok(!!q('.fluss'), 'Fluss erscheint');
          ok(q('.content-title') === null, 'Seitenansicht ist weg');
          ok(knopf().getAttribute('aria-pressed') === 'true', 'Knopf ist gedrueckt');
          ok(/schlie|close/i.test(knopf().getAttribute('title')), 'Hinweis wechselt: ' + knopf().getAttribute('title'));
          ok(all('.fluss-eintrag').length === 2, 'beide Seiten im Fluss: ' + all('.fluss-eintrag').length);

          head('Nochmal druecken: zurueck zur Seite');
          knopf().click();
          setTimeout(function () {
            ok(!q('.fluss'), 'Fluss ist zu');
            ok(!!q('.content-title'), 'Seitenansicht ist da: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
            ok(knopf().getAttribute('aria-pressed') === 'false', 'Knopf wieder aus');
            ok(!!q('.footer .btn'), 'Fussleiste bedienbar');
            ende();
          }, 700);
        }, 700);
      }, 1500);
    })();
    </script>
"""
kopie1 = build('_kopf1.html', script1, seiten, startpage='1')

# ---------------------------------------------------------------- Teil 2
# Scharfes Fenster: der Text verschwindet, der Knopf bleibt bedienbar
#
# ACHTUNG, und das hat lange getrogen: Chromium nimmt kein Fenster unter
# 500 Pixeln. Ein Aufruf mit 380 liefert 500:
#
#     --window-size=320  ->  innerWidth=500
#     --window-size=380  ->  innerWidth=500
#     --window-size=412  ->  innerWidth=500
#
# Dieser Lauf hat also immer ein Fenster von 500 Pixeln geprueft und
# eines von 380 gewollt. Die Pruefung unten sagt das jetzt, statt eine
# Zahl zu behaupten, die nicht stimmt - siehe tests/README.md,
# "Headless nimmt kein Fenster unter 500 Pixeln".
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        ok(window.innerWidth <= 560, 'Fenster ist schmal: ' + window.innerWidth +
           ' - und 500 ist das schmalste, was Headless zulässt (siehe oben)');
        var k = q('.kopf-fluss');
        ok(!!k, 'Knopf da');
        ok(k && getComputedStyle(k.querySelector('.kopf-text')).display === 'none', 'Text ist ausgeblendet');
        ok(k && k.getBoundingClientRect().width > 20, 'Knopf ist noch da: ' + Math.round(k.getBoundingClientRect().width) + 'px breit');
        var kopf = q('.header').getBoundingClientRect();
        var letzte = all('.header button').pop().getBoundingClientRect();
        ok(letzte.right <= kopf.right + 1, 'alle Knoepfe passen in den Kopf: ' + Math.round(letzte.right) + ' von ' + Math.round(kopf.right));
        k.click();
        setTimeout(function () {
          ok(!!q('.fluss'), 'Fluss laesst sich auch schmal oeffnen');
          var n = log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length;
          var f = log.filter(function (l) { return /^FAIL/.test(l); }).length;
          log.push('');
          log.push('>>> ' + (f ? f + ' FEHLGESCHLAGEN' : 'ALLE ' + n + ' BESTANDEN'));
          out();
        }, 700);
      }, 1500);
    })();
    </script>
"""
kopie2 = build('_kopf2.html', script2, seiten, startpage='1')

# Beide Kopien laufen durch dieselbe Stelle: so zaehlt Teil 2 in der
# Gesamtzahl mit, und ein Fehlschlag im schmalen Fenster macht den
# Lauf rot. Teil 2 braucht ein schmales Fenster - das wird ihm hier
# mitgegeben, statt es nebenbei zu umgehen.
pruefe(kopie1, kopie2, fenster={'_kopf2.html': '380,700'})