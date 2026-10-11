import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

# Ein Bild soll als Bild erscheinen - auch dann, wenn im WYSIWYG-Editor
# leere Absaetze davor stehen. Toast UI schreibt die als eigene
# "<br>"-Zeile ins Markdown; marked liest so eine Zeile als rohen
# HTML-Block, der erst an einer Leerzeile endet, und stellte die naechste
# Zeile sonst ungeparst dar. Der Test haelt beide Wege fest: die
# gerenderte Seite und die Runde durch den Editor.

IMG = ("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgH"
       "BwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTg"
       "yPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAA"
       "AAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q==")

# Genau die Form, die der Editor liefert: "1\." und "2\." escaped, dazwischen
# eine eigene <br>-Zeile, danach das Bild.
problem = "1\\. Zeile...\n\n<br>\n2\\. Zeile ![](" + IMG + ")\n"

pages = [
  {"id":"a","title":"Bild","content":problem,"links":[],"tags":[],"created":"x","updated":"x"},
]

# --- Teil 1: gerenderte Seite mit dem Editor-Markdown ---------------------
teil1 = r"""
    <script>
    (function(){
      var log=[], fails=0;
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      function out(){var p=document.getElementById('report'); if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);} p.textContent=log.join('\n');}
      function ok(c,m){if(!c)fails++;log.push((c?'OK   ':'FAIL ')+m);out();}
      function head(m){log.push('--- '+m);out();}
      window.addEventListener('error',function(e){ok(false,'JS-Fehler: '+e.message);});
      setTimeout(function(){
        var pv=q('.preview');
        head('Bild nach leeren Absaetzen aus dem Editor');
        ok(!!q('.preview img'),'Bild als <img> gerendert');
        ok(pv.textContent.indexOf('![')<0,'kein roher Markdown-Text mehr: '+pv.textContent.replace(/\s+/g,' ').trim().slice(0,60));
        ok(pv.querySelectorAll('img').length===1,'genau ein Bild: '+pv.querySelectorAll('img').length);
        ok(pv.textContent.indexOf('2. Zeile')>=0,'der Text neben dem Bild ist entescapet: '+pv.textContent.replace(/\s+/g,' ').trim().slice(0,60));
        log.push(''); log.push('>>> '+(fails?fails+' FEHLGESCHLAGEN':'ALLE '+log.filter(function(l){return /^OK|^FAIL/.test(l);}).length+' BESTANDEN'));
        out();
      },3000);
    })();
    </script>
"""

# --- Teil 2: die Runde durch den echten Editor ----------------------------
teil2 = r"""
    <script>
    (function(){
      var log=[], fails=0;
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      function out(){var p=document.getElementById('report'); if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);} p.textContent=log.join('\n');}
      function ok(c,m){if(!c)fails++;log.push((c?'OK   ':'FAIL ')+m);out();}
      function head(m){log.push('--- '+m);out();}
      function btn(re){return all('.footer .btn').filter(function(b){return re.test(b.textContent);})[0];}
      window.addEventListener('error',function(e){ok(false,'JS-Fehler: '+e.message);});
      setTimeout(function(){
        head('Bearbeiten oeffnen');
        btn(/Bearbeiten/).click();
        setTimeout(function(){
          ok(!!q('.md-host .toastui-editor-defaultUI'),'Editor ist da');
          ok(!!window.__ed,'Testhaken am Editor');
          ok(!!q('.toastui-editor-contents img'),'der Editor zeigt das Bild');
          var md = window.__ed.getMarkdown();
          head('Was der Editor als Markdown liefert');
          ok(md.indexOf('![](')>=0,'das Bild steht als Markdown im Text: '
             +JSON.stringify(md.slice(0,50)));
          head('Speichern und wieder lesen');
          btn(/Speichern/).click();
          setTimeout(function(){
            var pv=q('.preview');
            ok(!!q('.preview img'),'nach dem Speichern ist das Bild als <img> da');
            ok(pv.textContent.indexOf('![')<0,'kein roher Markdown-Text in der Anzeige');
            log.push(''); log.push('>>> '+(fails?fails+' FEHLGESCHLAGEN':'ALLE '+log.filter(function(l){return /^OK|^FAIL/.test(l);}).length+' BESTANDEN'));
            out();
          },800);
        },2600);
      },2500);
    })();
    </script>
"""

pruefe(
    build('_bild1.html', teil1, pages, theme='light', lang='de', startpage='a'),
    build('_bild2.html', teil2, pages, theme='light', lang='de', startpage='a'),
)
