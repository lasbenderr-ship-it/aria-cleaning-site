"""Fill Webflow CMS sections from the Collections CSV exports and generate Knowledge Hub article pages.

usage: cms.py SITE_DIR CSV_DIR ARTICLE_TEMPLATE EXPORT_INDEX
ARTICLE_TEMPLATE is detail_knowledge-hub.html already run through localize.py and staticize.py.
EXPORT_INDEX is the untouched index.html from the Webflow export (source of the testimonial card markup).
"""
import sys, os, csv, copy, re, io
from datetime import datetime
from bs4 import BeautifulSoup

SITE, CSV_DIR, TEMPLATE, EXPORT_INDEX = sys.argv[1:5]
PREFIXED = re.compile(r'^(https?:|//|#|mailto:|tel:|data:|javascript:|/)')

def rows(name):
    with open(os.path.join(CSV_DIR, name + '.csv'), encoding='utf-8-sig') as f:
        text = f.read().replace('https://uploads-ssl.webflow.com/', 'https://cdn.prod.website-files.com/')  # legacy CDN host
    return [r for r in csv.DictReader(io.StringIO(text)) if r['Archived'] != 'true' and r['Draft'] != 'true']

def published(r):
    return datetime.strptime(r['Original Publish Date'][:24], '%a %b %d %Y %H:%M:%S')

def frag(html):
    return BeautifulSoup(html, 'html.parser')

def unbind(el, text=None):
    el['class'] = [c for c in el.get('class', []) if c != 'w-dyn-bind-empty']
    if text is not None:
        el.string = text

def drop_empty(lst):
    for e in lst.select('.w-dyn-empty'):
        e.decompose()

testimonials = rows('Testimonials')
befores = sorted(rows('Before_and_Afters'), key=lambda r: datetime.strptime(r['Created On'][:24], '%a %b %d %Y %H:%M:%S'), reverse=True)  # live site order
contact = rows('Contact_Details')[0]
articles = sorted(rows('Knowledge_Hub_Articles'), key=published, reverse=True)

# The testimonial card with its review paragraph, before staticize.py trimmed it.
tmpl_src = BeautifulSoup(open(EXPORT_INDEX, encoding='utf-8'), 'html.parser').select_one('.testimonial')

def fill_testimonials(soup):
    for items in soup.select('.testimonials.w-dyn-items'):
        tmpl = copy.copy(tmpl_src)
        for old in items.select('.testimonial'):
            old.decompose()
        for r in testimonials:
            t = copy.copy(tmpl)
            for cls, key in (('testimonial__subject', 'Subject Line'), ('testimonial__review', 'Review'),
                             ('testimonial__author', 'Author Name'), ('testimonial__pos', 'Author Location')):
                el = t.select_one('.' + cls)
                if el is not None:
                    unbind(el, r[key])
            items.append(t)
        drop_empty(items.parent)

def fill_before_afters(soup):
    items = soup.select_one('.before-afters.w-dyn-items')
    if items is None:
        return
    tmpl = items.select_one('.ba-slider-wrap').extract()
    for old in items.select('.ba-slider-wrap'):
        old.decompose()
    for r in befores:
        t = copy.copy(tmpl)
        # Webflow binds the base layer to the after shot and the draggable overlay to the before shot.
        after, before = t.select('.ba-slider__img')
        for img, key in ((before, 'Before Image'), (after, 'After Image')):
            unbind(img)
            img['src'] = r[key]
            img['alt'] = f"{r['Name']}: {key.split()[0].lower()}"
        items.append(t)
    drop_empty(items.parent)

def fill_contact(soup):
    for a in soup.select('a.icon-block'):
        heading = a.select_one('.icon-block__heading').get_text(strip=True)
        summary = a.select_one('.icon-block__summary')
        if heading == 'Telephone':
            a['href'] = 'tel:+' + re.sub(r'\D', '', contact['Phone Number'])
            unbind(summary, contact['Phone Number'])
        elif heading == 'Email':
            a['href'] = 'mailto:' + contact['Email Address']
            unbind(summary, contact['Email Address'])
    for iframe in soup.select('.collection-list-wrapper iframe'):
        iframe['src'] = contact['Google Map src']
        iframe['title'] = 'Map to ARIA Commercial Cleaning Services'
        iframe['loading'] = 'lazy'
    for lst in soup.select('.w-dyn-list'):
        if lst.select_one('a.icon-block') or lst.select_one('.collection-list-wrapper iframe') or 'collection-list-wrapper' in lst.get('class', []):
            drop_empty(lst)

def fill_article_cards(soup, href_prefix):
    items = soup.select_one('.articles-area.w-dyn-items')
    if items is None:
        return
    tmpl = items.select_one('.article-card').extract()
    for old in items.select('.article-card'):
        old.decompose()
    for r in articles:
        t = copy.copy(tmpl)
        t.select_one('a')['href'] = href_prefix + r['Slug'] + '.html'
        img = t.select_one('.article-card__img')
        unbind(img); img['src'] = r['Thumbnail']; img['alt'] = r['Name']
        unbind(t.select_one('.article-card__name'), r['Name'])
        unbind(t.select_one('.article-card__excerpt'), r['Excerpt'])
        items.append(t)
    drop_empty(items.parent)

def fill_sidebar(soup, current_slug):
    item = soup.select_one('.sidebar-article')
    if item is None:
        return
    wrap = item.find_parent(class_='w-dyn-item')
    items = wrap.parent
    tmpl = wrap.extract()
    for r in [a for a in articles if a['Slug'] != current_slug][:5]:
        t = copy.copy(tmpl)
        t.select_one('a')['href'] = r['Slug'] + '.html'
        img = t.select_one('.sidebar-article__img')
        unbind(img); img['src'] = r['Thumbnail']; img['alt'] = ''
        unbind(t.select_one('.sidebar-article__title'), r['Name'])
        items.append(t)
    drop_empty(items.parent)

def depth_fix(soup, prefix):
    for el in soup.find_all(True):
        for attr in ('href', 'src'):
            v = el.get(attr)
            if v and not PREFIXED.match(v):
                el[attr] = prefix + v
        if el.get('srcset'):
            el['srcset'] = ', '.join(p if PREFIXED.match(p.strip()) else prefix + p.strip()
                                     for p in el['srcset'].split(','))

# --- existing pages
for dp, _, fs in os.walk(SITE):
    for f in fs:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        soup = BeautifulSoup(open(p, encoding='utf-8'), 'html.parser')
        fill_testimonials(soup)
        if f == 'our-work.html':
            fill_before_afters(soup)
        if f == 'contact.html':
            fill_contact(soup)
        if f == 'knowledge-hub.html':
            fill_article_cards(soup, 'knowledge-hub/')
        open(p, 'w', encoding='utf-8').write(str(soup))

# --- article pages
os.makedirs(os.path.join(SITE, 'knowledge-hub'), exist_ok=True)
for r in articles:
    soup = BeautifulSoup(open(TEMPLATE, encoding='utf-8'), 'html.parser')
    fill_testimonials(soup)
    fill_sidebar(soup, r['Slug'])
    soup.title.string = r['Meta Title'] or r['Name']
    for sel, val in (({'name': 'description'}, r['Meta Description']), ({'property': 'og:title'}, r['Meta Title'] or r['Name']),
                     ({'property': 'og:description'}, r['Meta Description']), ({'property': 'og:image'}, r['Thumbnail'])):
        m = soup.find('meta', attrs=sel)
        if m is not None:
            m['content'] = val
    unbind(soup.select_one('.title-banner__heading'), r['Name'])
    body = soup.select_one('.rich-article')
    unbind(body)
    body.clear()
    body.append(frag(r['Article']))
    depth_fix(soup, '../')
    if not soup.find('link', href='../css/aria-updates.css'):
        soup.head.append(frag('<link href="../css/aria-updates.css" rel="stylesheet" type="text/css"/>'))
    with open(os.path.join(SITE, 'knowledge-hub', r['Slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(str(soup))
print(len(testimonials), 'testimonials,', len(befores), 'before/afters,', len(articles), 'articles')
