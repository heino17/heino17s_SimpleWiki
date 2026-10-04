import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

mit_seite = [
  {"id":"a","title":"Alpha","content":"# Alpha\n\nInhalt","links":["Beta"],"tags":[],"created":"x","updated":"x"},
  {"id":"b","title":"Beta","content":"# Beta","links":[],"tags":[],"created":"x","updated":"x"},
]
ohne_seite = []

s1 = r"""
    <script>
    (function(){
      var log=[], fails=0;
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      function out(){var p=document.getElementById('report'); if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);} p.textContent=log.join('\n');}
      function ok(c,m){if(!c)fails++;log.push((c?'OK   ':'FAIL ')+m);out();}
      function btn(re){return all('.footer .btn').filter(function(b){return re.test(b.textContent);})[0];}
      window.addEventListener('error',function(e){ok(false,'JS-Fehler: '+e.message);});

      setTimeout(function(){
        ok(!q('.empty-state'),'kein Leer-Zustand trotz vorhandener Seite');
        ok(!!q('.preview h1'),'Inhalt wird angezeigt');
        ok(!!q('.menu-badge'),'Verweise werden am Knopf gezaehlt');
        ok(!q('.outgoing'),'kein Verweisabschnitt mehr in der Seite');

        all('.footer .btn').filter(function(b){return /Bearbeiten/.test(b.textContent);})[0].click();
        setTimeout(function(){
          ok(!q('.empty-state'),'kein Leer-Zustand beim Bearbeiten');
          ok(!!q('.md-host .toastui-editor-defaultUI'),'Editor verdeckt nicht: Editor sichtbar');
          var h=q('.empty-state');
          ok(!h || getComputedStyle(h).display==='none', 'Leer-Zustand wirklich ausgeblendet');
          ok(!q('.outgoing'),'Verlinkt-Abschnitte im Editor ausgeblendet');
          btn(/Abbrechen/).click();
          setTimeout(function(){
            ok(!q('.empty-state'),'nach Abbrechen wieder nur der Inhalt');
            log.push(''); log.push('>>> '+(fails?fails+' FEHLGESCHLAGEN':'ALLE '+log.filter(function(l){return /^OK|^FAIL/.test(l);}).length+' BESTANDEN'));
            out();
          },700);
        },2600);
      },3000);
    })();
    </script>
"""


s2 = r"""
    <script>
    (function(){
      var log=[];
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      setTimeout(function(){
        log.push('Leer-Zustand sichtbar: '+!!q('.empty-state'));
        log.push('Text: '+(q('.empty-state h2')?q('.empty-state h2').textContent.trim():'-'));
        log.push('Fussleiste-Knoepfe: '+all('.footer .btn').length);
        log.push('Inhaltsverzeichnis: '+all('.toc-item-title').map(function(e){return e.textContent.trim();}).join('|'));
        var p=document.createElement('pre'); p.id='report'; p.textContent=log.join('\n'); document.body.appendChild(p);
      },3000);
    })();
    </script>
"""

pruefe(
    build('_leer1.html', s1, mit_seite, theme='light', lang='de', startpage='a'),
    build('_leer2.html', s2, ohne_seite, theme='light', lang='de', startpage='')
)
