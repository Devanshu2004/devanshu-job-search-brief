# Builds public/index.html (the Netlify page) from the Claude page source.
# Usage: python3 tools/build_page.py <job-search-brief.html> public/index.html
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf8').read()

a = s.index("  var api=window.claude&&window.claude.use"); b = s.index("})();\n</script>")
loader = r'''  var KEY='jsb-passphrase',enc=null;
  function b64(x){var bin=atob(x),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return u}
  function stored(){try{return localStorage.getItem(KEY)||''}catch(e){return ''}}
  function remember(p){try{localStorage.setItem(KEY,p)}catch(e){}}
  function forget(){try{localStorage.removeItem(KEY)}catch(e){}}
  function decrypt(pass){
    var te=new TextEncoder();
    return crypto.subtle.importKey('raw',te.encode(pass),'PBKDF2',false,['deriveKey']).then(function(k){
      return crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(enc.salt),iterations:enc.iter,hash:'SHA-256'},k,{name:'AES-GCM',length:256},false,['decrypt'])
    }).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b64(enc.iv)},k,b64(enc.ct))
    }).then(function(buf){return JSON.parse(new TextDecoder().decode(buf))})}
  function lockScreen(msg){
    dayEl.disabled=prev.disabled=next.disabled=true;document.getElementById('actions').hidden=true;lockBtn.hidden=true;
    document.getElementById('kind').textContent='Morning brief';document.getElementById('date').textContent='Your job search, one page a day';
    document.getElementById('lead').textContent='This page is locked. Enter your passphrase to read the brief.';
    var box=el('form','empty lock'),inp=el('input'),btn=el('button','btn primary','Unlock'),err=el('p','lock-err',msg||'');
    inp.type='password';inp.id='passphrase';inp.autocomplete='current-password';inp.setAttribute('aria-label','Passphrase');inp.placeholder='Passphrase';btn.type='submit';
    add(box,el('h2',null,'Enter your passphrase'),el('p','muted','You only need to do this once on each device.'),inp,btn,err);
    box.addEventListener('submit',function(e){e.preventDefault();var p=inp.value.trim();if(!p){err.textContent='Enter the passphrase first.';return}
      btn.disabled=true;btn.textContent='Unlocking';unlock(p,true)});
    main.replaceChildren(box);inp.focus()}
  function unlock(pass,fromForm){
    decrypt(pass).then(function(data){remember(pass);lockBtn.hidden=false;
      state.briefs=arr(data&&data.briefs).filter(function(d){return d&&has(d.date)}).sort(function(a,b){return a.date<b.date?1:-1});render()
    },function(){forget();lockScreen(fromForm?'That passphrase did not unlock the brief. Check it and try again.':'')})}
  var lockBtn=document.getElementById('lock');
  lockBtn.addEventListener('click',function(){forget();state.briefs=[];lockScreen('')});
  if(!(window.crypto&&crypto.subtle)){showState('This browser cannot open the brief','Open the page over https in a current browser.')}
  else fetch('briefs.enc.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('load');return r.json()}).then(function(j){
    enc=j;var p=stored();if(p)unlock(p,false);else lockScreen('')
  },function(){showState('The brief could not be loaded','Reload the page. If it still does not load, the brief is also in this morning\'s conversation in Claude.')});
'''
s = s[:a] + loader + s[b:]

css = '''.lock{margin-top:-46px;align-items:center}
.lock input{font:inherit;width:100%;max-width:320px;min-height:46px;border:1px solid var(--line);border-radius:10px;padding:0 14px;background:var(--surface);color:var(--ink)}
.lock-err{color:var(--crit);font-size:14px;min-height:1.4em}
.linkbtn{background:none;border:0;padding:0;color:var(--brand);text-decoration:underline;cursor:pointer;font-size:14px}
[hidden]{display:none!important}
img{max-width:100%}
'''
s = s.replace('</style>', css + '</style>', 1)
old = 'Nothing is applied, sent or registered from this page.</div></footer>'
assert old in s
s = s.replace(old, 'Nothing is applied, sent or registered from this page. <button type="button" class="linkbtn" id="lock" hidden>Lock this device</button></div></footer>')

title_end = s.index('</title>') + len('</title>')
head = s[:title_end]; rest = s[title_end:]
link_end = rest.index('</style>') + len('</style>')
head += rest[:link_end]; body = rest[link_end:]
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<meta name="robots" content="noindex,nofollow">\n' + head + '\n</head>\n<body>' + body + '\n</body>\n</html>\n')
open(out, 'w', encoding='utf8').write(doc)
print('wrote', out, len(doc))
