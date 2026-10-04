import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe

pages = [
    {"id": "a", "title": "Alpha", "content": "# Alpha", "links": [], "tags": [], "created": "x", "updated": "x"},
]

script = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function speicher() { return JSON.parse(localStorage.getItem('simplewiki_pages')); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        ok(!!btn(/Edit/), 'englische Oberflaeche: ' + (btn(/Edit/) ? btn(/Edit/).textContent.trim() : '-'));
        btn(/Edit/).click();
        setTimeout(function () {
          var d = btn(/Duplicate/);
          ok(!!d, 'Knopf heisst ' + (d ? d.textContent.trim() : '-'));
          ok(!!d && /^Create a copy/.test(d.title), 'Hinweis englisch: ' + (d ? d.title.slice(0, 34) + '...' : '-'));
          d.click();
          setTimeout(function () {
            ok(q('.content-title').textContent.trim() === 'Alpha (Copy)', 'Name: ' + q('.content-title').textContent.trim());
            btn(/Edit/).click();
            setTimeout(function () {
              btn(/Duplicate/).click();
              setTimeout(function () {
                ok(q('.content-title').textContent.trim() === 'Alpha (Copy 2)', 'zweite Kopie: ' + q('.content-title').textContent.trim());
                ok(speicher().length === 3, 'Seiten: ' + speicher().length);
                log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                out();
              }, 700);
            }, 2200);
          }, 900);
        }, 2200);
      }, 1200);
    })();
    </script>
"""

pruefe(
    build('_dupen.html', script, pages, lang='en')
)
