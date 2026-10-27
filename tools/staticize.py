"""Replace Webflow CMS bindings and CDN libs with static equivalents on every page."""
import sys, os, copy, re
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
PHONE, TEL = '1 (888) 844-1001', 'tel:+18888441001'
EMAIL = 'contact@ariacleaningservices.com'
ADDR = ('ARIA Commercial Cleaning Services', '11823 Slauson Ave, Santa Fe Springs, CA 90670')
SOCIAL = {0: 'https://www.facebook.com/ANBS.Services/', 2: 'https://www.instagram.com/anbs.services/',
          5: 'https://yelp.to/qTKq/fBMXKxIf8T'}  # order in the export: fb, twitter, ig, linkedin, youtube, yelp
# Subject lines from the live site; full review text comes from the Testimonials CSV.
TESTIMONIALS = [
    ('Fantastic Job!!', 'Brady F', 'Orange, CA'),
    ('The quality of ARIA Commercial Cleaning Services is excellent!', 'Craig D', 'Laguna Beach, CA'),
    ('Highly Recommend!', 'Aileen S', 'Los Angeles, CA'),
    ('Ignacio was so professional', 'Tammi M', 'Whittier, CA'),
    ('They are professionals at what they do.', 'Norma A', 'Century City, CA'),
    ('They Always Deliver What They Promise', 'Izaac M', 'West Hollywood, CA'),
    ('I Will Certainly Be Using Them Again!', 'Lujan M', 'Orange County, CA'),
]
CDN = {
    'cloudfront.net/js/jquery': 'js/vendor/jquery-3.5.1.min.js',
    'slick-carousel@1.8.1/slick/slick.min.js': 'js/vendor/slick.min.js',
    'jquery.inview.min.js': 'js/vendor/jquery.inview.min.js',
    'slick-carousel@1.8.1/slick/slick.css': 'js/vendor/slick.css',
    'slick-theme.min.css': 'js/vendor/slick-theme.css',
}

def unbind(el, text=None):
    cls = [c for c in el.get('class', []) if c != 'w-dyn-bind-empty']
    el['class'] = cls
    if text is not None:
        el.string = text

def fill(soup):
    for lst in soup.select('.w-dyn-list'):
        item = lst.select_one('.w-dyn-item')
        if item is None:
            continue
        links = item.select('a')
        cls = ' '.join(' '.join(a.get('class', [])) for a in links)
        if 'nav-link--call' in cls or 'call-now__btn' in cls:
            for a in links:
                a['href'] = TEL
            for b in item.select('.w-dyn-bind-empty'):
                unbind(b, PHONE)
        elif 'footer-link-block' in cls:
            vals = [(TEL, PHONE), ('mailto:' + EMAIL, EMAIL)]
            for a, (href, txt) in zip(links, vals):
                a['href'] = href
                for b in a.select('.w-dyn-bind-empty'):
                    unbind(b, txt)
        elif 'footer-social__link' in cls:
            for i, a in enumerate(links):
                if i in SOCIAL:
                    a['href'] = SOCIAL[i]; a['target'] = '_blank'; a['rel'] = 'noopener'
                else:
                    a.decompose()
        elif item.select_one('.address'):
            binds = item.select('.w-dyn-bind-empty')
            for b, txt in zip(binds, ADDR):
                unbind(b, txt)
        elif item.select_one('.testimonial__subject'):
            tmpl = item.extract()
            items = lst.select_one('.w-dyn-items')
            for subj, author, pos in TESTIMONIALS:
                t = copy.copy(tmpl)
                unbind(t.select_one('.testimonial__subject'), subj)
                rv = t.select_one('.testimonial__review')
                rv.decompose()
                unbind(t.select_one('.testimonial__author'), author)
                unbind(t.select_one('.testimonial__pos'), pos)
                items.append(t)
        else:
            continue  # knowledge hub, before/afters, contact icons: wait for CSVs
        for e in lst.select('.w-dyn-empty'):
            e.decompose()

def vendor(soup, prefix):
    for tag, attr in (('script', 'src'), ('link', 'href')):
        for el in soup.find_all(tag):
            v = el.get(attr) or ''
            for k, local in CDN.items():
                if k in v:
                    el[attr] = prefix + local
                    for a in ('integrity', 'crossorigin'):
                        el.attrs.pop(a, None)

for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(ROOT, dp)
        prefix = '' if rel == '.' else rel + '/'
        soup = BeautifulSoup(open(p, encoding='utf-8'), 'html.parser')
        fill(soup)
        vendor(soup, prefix)
        open(p, 'w', encoding='utf-8').write(str(soup))
