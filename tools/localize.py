import re,sys,os,urllib.parse
root=sys.argv[1]
pat=re.compile(r'https://uploads-ssl\.webflow\.com/[0-9a-f]+/[0-9a-f]+_([^"\'\s,)&]+)')
missing=set()
for dp,_,fs in os.walk(root):
  for f in fs:
    if not f.endswith(('.html','.css')): continue
    p=os.path.join(dp,f); rel=os.path.relpath(root,dp)
    pre='' if rel=='.' else rel+'/'
    if f.endswith('.css'): pre='../'
    s=open(p,encoding='utf-8').read()
    def rep(m):
      name=m.group(1); dec=urllib.parse.unquote(name)
      for d in ('videos','images'):
        if os.path.exists(os.path.join(root,d,dec)): return pre+d+'/'+name
      missing.add(name); return m.group(0)
    s2=pat.sub(rep,s)
    if s2!=s: open(p,'w',encoding='utf-8').write(s2)
print('missing:',missing)
