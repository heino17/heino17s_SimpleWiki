"""Die Sprachauswahl: Die eingebauten Sprachen stehen vollstaendig im
Dropdown unter den Einstellungen, jede nennt sich selbst und jede
uebersetzt die Oberflaeche.

Die Codes kommen aus dem Austauschvertrag im Kopf von simplewiki.html;
die Namen sind Eigenbezeichnungen, keine Uebersetzungen. Geprueft wird
darum das Paar aus Code und Name und die Kopfzeile des Panels - ein
Wort, das aus der jeweiligen Uebersetzung stammt und nicht aus der
Hauptsprache.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkcopy import build
from _hilfe import pruefe

seiten = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [],
     "created": "x", "updated": "x"},
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
      function ende() {
        log.push('');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN'
          : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }

      /* Den Dialog oeffnen und die Sprache im Dropdown wechseln. */
      function sprache(code) {
        var p = q('.settings-panel');
        if (!p || !p.classList.contains('open')) { q('.settings-toggle').click(); }
        return new Promise(function (res) {
          setTimeout(function () {
            var s = q('#settings-language');
            s.value = code;
            s.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(res, 400);
          }, 400);
        });
      }

      var kopf = { de: 'Einstellungen', en: 'Settings', ru: 'Настройки',
                   es: 'Ajustes', fr: 'Réglages', ja: '設定', ko: '설정',
                   zh_CN: '设置' };
      var namen = { de: 'Deutsch', en: 'English', ru: 'Русский',
                    es: 'Español', fr: 'Français', ja: '日本語',
                    ko: '한국어', zh_CN: '简体中文' };
      var codes = ['de', 'en', 'ru', 'es', 'fr', 'ja', 'ko', 'zh_CN'];
      var i = 0;

      function weiter() {
        if (i >= codes.length) { ende(); return; }
        var c = codes[i++];
        sprache(c).then(function () {
          var h = q('.settings-panel .side-header h2');
          ok(h && h.textContent.trim() === kopf[c],
             c + ': Kopfzeile ' + (h ? JSON.stringify(h.textContent.trim()) : 'fehlt'));
          ok(localStorage.getItem('simplewiki_lang') === c,
             c + ' gemerkt: ' + localStorage.getItem('simplewiki_lang'));
          weiter();
        });
      }

      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        head('Die Auswahl');
        q('.settings-toggle').click();
        setTimeout(function () {
          var opts = all('#settings-language option');
          var got = opts.map(function (o) { return o.value; });
          ok(got.length === 8, 'acht Sprachen: ' + got.join('|'));
          ok(got[0] === 'de', 'Deutsch steht vorn: ' + got[0]);
          var fehlen = codes.filter(function (c) { return got.indexOf(c) < 0; });
          ok(fehlen.length === 0,
             'alle Codes sind da' + (fehlen.length ? ' - es fehlt: ' + fehlen.join(',') : ''));

          var gelesen = {};
          opts.forEach(function (o) { gelesen[o.value] = o.textContent.trim(); });
          var falsch = codes.filter(function (c) { return gelesen[c] !== namen[c]; });
          ok(falsch.length === 0,
             'jede Sprache nennt sich selbst' +
             (falsch.length ? ' - falsch: ' + falsch.map(function (c) { return c + '=' + gelesen[c]; }).join(' ') : ''));

          head('Jede Sprache uebersetzt die Oberflaeche');
          weiter();
        }, 700);
      }, 2500);
    })();
    </script>
"""

pruefe(build('_sprachen.html', script, seiten, theme='light', lang='de', startpage='a'))
