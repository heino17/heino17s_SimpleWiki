import sys, io, re, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, KOPIEN
import html as H

mkcopy.EXTRA_REPLACEMENTS = [('</style>', '    #report { display: none !important; }\n    </style>')]

# Absichtlich viele Seiten mit langem Inhalt: so braucht der Fluss
# mehrere Bildschirmhöhen und der Ausdruck mehrere Blätter.
lang = '# Lange Seite\n\n' + ('Ein Absatz mit genug Text, damit die Seite laenger wird als der Bildschirm. ' * 40) + '\n\n'
lang += '## Zweiter Abschnitt\n\n' + ('Noch mehr Text, damit die Seite sicher ueber die Bildschirmhoehe hinausreicht. ' * 40)
seiten = [
    {"id": "1", "title": "Anleitung", "content": lang, "links": ["Notizen"], "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Notizen", "content": "# Notizen\n\nKurze Seite.\n\nENDE-MARKER", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "3", "title": "Letzte Seite", "content": "# Letzte Seite\n\nHier steht der letzte Satz.", "links": [], "tags": [], "created": "x", "updated": "x"},
]

script = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        q('.menu-toggle').click();
        setTimeout(function () {
          all('.toc-footer .new-page-btn')[0].click();
          setTimeout(function () {
            var f = q('.fluss');
            head('Scrollen');
            ok(!!f, 'Fluss da');
            ok(window.innerHeight < 900, 'Fenster ist niedrig genug: ' + window.innerHeight + 'px');
            ok(f.scrollHeight > f.clientHeight + 10,
               'Inhalt ist hoeher als der Kasten: ' + f.scrollHeight + ' statt ' + f.clientHeight);
            var kastenHoehe = f.clientHeight;
            f.scrollTop = 400;
            setTimeout(function () {
              ok(f.scrollTop > 100, 'scrollTop greift: ' + Math.round(f.scrollTop));
              ok(f.scrollHeight > kastenHoehe * 3, 'deutlich mehr Inhalt als Bildschirm: ' + f.scrollHeight + ' statt ' + kastenHoehe);
              f.scrollTop = f.scrollHeight;
              setTimeout(function () {
                var unten = f.scrollTop + f.clientHeight;
                ok(unten >= f.scrollHeight - 2, 'Ende erreichbar: unten ' + Math.round(unten) + ' von ' + f.scrollHeight);
                var letzter = all('.fluss-eintrag')[2];
                var k = letzter.getBoundingClientRect();
                ok(k.top < window.innerHeight && k.bottom > 0, 'letzte Seite ist sichtbar erreichbar');
                var text = all('.fluss-eintrag-titel').map(function (t) { return t.textContent.trim(); }).join('|');
                ok(text === 'Anleitung|Notizen|Letzte Seite', 'alle drei da: ' + text);

                head('Neuer Fluss beginnt oben');
                f.scrollTop = 300;
                q('.menu-toggle').click();
                setTimeout(function () {
                  all('.toc-footer .new-page-btn')[0].click();
                  setTimeout(function () {
                    ok(q('.fluss').scrollTop === 0, 'Fluss startet oben: ' + q('.fluss').scrollTop);
                    log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                    out();
                  }, 700);
                }, 700);
              }, 500);
            }, 500);
          }, 900);
        }, 900);
      }, 1500);
    })();
    </script>
"""
build('_scroll1.html', script, seiten, startpage='1')

# Niedriges Fenster: nur so merkt man, ob es scrollt.
text = bericht(dumpdom('_scroll1.html', fenster='900,420', budget=90000))
print('=== Scrollen im Fluss (Fenster 900x420) ===')
print(text if text else 'KEIN REPORT')
fehler_browser = len(re.findall(r'(?m)^FAIL ', text))

# ---------------------------------------------------------------- Druck
pdf = os.path.join(KOPIEN, '_scroll_druck.pdf')
if os.path.exists(pdf):
    os.remove(pdf)
subprocess.run(['chromium', '--headless', '--disable-gpu', '--no-sandbox',
                '--virtual-time-budget=40000', '--no-pdf-header-footer',
                '--print-to-pdf=' + pdf,
                'file://' + os.path.join(KOPIEN, '_scroll1.html')],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)

print('\n=== Ausdruck als PDF ===')
fehler = 0
if os.path.exists(pdf):
    info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    bloecke = [l for l in info.split('\n') if l.startswith('Pages')]
    n = int(bloecke[0].split()[-1]) if bloecke else 0
    txt = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    alles = ' '.join(txt.split())
    print('  Seiten im PDF: %d' % n)
    if n < 2:
        print('  FEHLER: mehr als eine Seite erwartet'); fehler += 1
    else:
        print('  OK: der Inhalt laeuft ueber mehrere Blaetter')
    for erwartet in ['Anleitung', 'Notizen', 'Letzte Seite', 'ENDE-MARKER', 'Hier steht der letzte Satz']:
        da = erwartet in alles
        fehler += 0 if da else 1
        print('  %-26s %s' % (erwartet, 'ja' if da else 'NEIN (abgeschnitten!)'))
    for unerwartet in ['Neue Seite', 'Einstellungen', 'Speichern', 'Fluss – alle Seiten']:
        weg = unerwartet not in alles
        fehler += 0 if weg else 1
        print('  %-26s %s' % ('ohne ' + unerwartet, 'ok' if weg else 'NOCH DA'))
    print('\n>>> Druck ueber mehrere Seiten: ' + ('BESTANDEN' if fehler == 0 else '%d FEHLGESCHLAGEN' % fehler))
    gesamt = fehler_browser + fehler
else:
    print('   PDF wurde nicht erzeugt')
    gesamt = fehler_browser + 1

print()
print('>>> ' + ('%d FEHLGESCHLAGEN' % gesamt if gesamt else 'ALLE BESTANDEN'))
sys.exit(1 if gesamt else 0)