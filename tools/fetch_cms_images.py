"""Download CMS images still served from Webflow's CDN into images/cms/ and point the pages at them.

usage: fetch_cms_images.py SITE_DIR   (needs network access to uploads-ssl.webflow.com)
"""
import sys, os, re, urllib.request, urllib.parse

SITE = sys.argv[1]
PAT = re.compile(r'https://uploads-ssl\.webflow\.com/[0-9a-f]+/[0-9a-f]+_([^"\'\s,)<&]+)')
dest = os.path.join(SITE, 'images', 'cms')
os.makedirs(dest, exist_ok=True)
for dp, _, fs in os.walk(SITE):
    for f in fs:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        prefix = os.path.relpath(SITE, dp)
        prefix = '' if prefix == '.' else prefix + '/'
        s = open(p, encoding='utf-8').read()
        def rep(m):
            name = urllib.parse.unquote(m.group(1))
            out = os.path.join(dest, name)
            if not os.path.exists(out):
                urllib.request.urlretrieve(m.group(0), out)
            return prefix + 'images/cms/' + urllib.parse.quote(name)
        s2 = PAT.sub(rep, s)
        if s2 != s:
            open(p, 'w', encoding='utf-8').write(s2)
