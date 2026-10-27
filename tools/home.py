"""Apply the Oct 6 huddle changes: form to top, trust bar, industries, CTA band, Ignacio video to About."""
import sys, os, glob
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
VIMEO = ('<div class="intro-video"><iframe src="https://player.vimeo.com/video/620262023?dnt=1" '
         'title="Meet ARIA Commercial Cleaning Services" loading="lazy" allow="fullscreen; picture-in-picture" '
         'allowfullscreen></iframe></div>')
ICON = lambda d: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
TRUST = [
    ('BBB Accredited Business', '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/><path d="M9 12l2 2 4-4"/>'),
    ('Certified Minority-Owned Small Business', '<circle cx="12" cy="9" r="5"/><path d="M8.5 13.5L7 21l5-2.5 5 2.5-1.5-7.5"/>'),
    ('Fully Insured: Liability &amp; Workers&#8217; Comp', '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 12l3 3 5-6"/>'),
    ('OSHA-Trained Cleaning Teams', '<path d="M4 15a8 8 0 0116 0"/><path d="M2 15h20v2H2z"/><path d="M12 7v4"/>'),
    ('70+ Years of Combined Experience', '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
]
INDUSTRIES = [
    ('Office Buildings', 'services/office-cleaning-services-in-orange-county.html',
     '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M11 21v-3h2v3"/>'),
    ('Warehouse &amp; Distribution', 'services/warehouse--distribution-cleaning-services.html',
     '<path d="M3 21V9l9-5 9 5v12"/><path d="M7 21v-8h10v8M7 17h10"/>'),
    ('Manufacturing', 'services/manufacturing-facilities-cleaning-services.html',
     '<path d="M3 21V11l5 3v-3l5 3v-3l5 3V4h3v17z"/>'),
    ('Aerospace', 'services/aerospace.html',
     '<path d="M21 15l-8-4V5a1.5 1.5 0 00-3 0v6l-8 4v2l8-2v4l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-4l8 2z"/>'),
    ('Medical Facilities', 'services/terminal-disinfectant-cleaning-methods.html',
     '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M12 8v8M8 12h8"/>'),
    ('Colleges &amp; Universities', 'contact.html',
     '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/>'),
]

def frag(html):
    return BeautifulSoup(html, 'html.parser')

def add_css(soup, prefix):
    if not soup.find('link', href=prefix + 'css/aria-updates.css'):
        soup.head.append(frag(f'<link href="{prefix}css/aria-updates.css" rel="stylesheet" type="text/css"/>'))

# --- every page: shared stylesheet
for p in glob.glob(ROOT + '/*.html') + glob.glob(ROOT + '/services/*.html'):
    s = BeautifulSoup(open(p, encoding='utf-8'), 'html.parser')
    add_css(s, '../' if '/services/' in p else '')
    open(p, 'w', encoding='utf-8').write(str(s))

# --- home
p = os.path.join(ROOT, 'index.html')
s = BeautifulSoup(open(p, encoding='utf-8'), 'html.parser')
hero = s.select_one('.hero-video')
hero['class'] = hero['class'] + ['hero--with-form']
form_col = s.select_one('.form-content__form')
form_sec = form_col.find_parent(class_='section')
body = s.select_one('.form-content__body')
job_note = body.select_one('.paragraph-2')
form_col['class'] = ['hero__form']
form_col['id'] = 'quote'
form_col.append(job_note.extract())
s.select_one('.hero__container').append(form_col.extract())
s.select_one('.hero__btns').insert(0, frag('<a class="btn-cta hero__btn hero__btn--quote" href="#quote">Get a Free Quote</a>'))

# trust bar directly under the hero
trust = ''.join(f'<li class="trust-item">{ICON(d)}<span>{t}</span></li>' for t, d in TRUST)
hero.insert_after(frag(f'<section class="trust-bar" aria-label="Why clients trust ARIA"><div class="container"><ul class="trust-list">{trust}</ul></div></section>'))

# intro copy keeps its place; the Ignacio video moves to About, the branded van photo fills the column
body.select_one('.video-wrapper').decompose()
for d in body.select('.div-block-5'):
    d.decompose()
intro = body.select_one('.rich-large-heading')
intro['class'] = [c for c in intro['class'] if c != 'mtop']
form_sec.select_one('.form-content').replace_with(frag(
    '<div class="media-content"><div class="media-content__body">' + str(intro) + '</div>'
    '<div class="media-content__media"><img class="media-content__img" src="images/ARIA-TEAM.jpg" loading="lazy" '
    'sizes="(max-width: 767px) 100vw, 45vw" srcset="images/ARIA-TEAM-p-500.jpeg 500w, images/ARIA-TEAM-p-800.jpeg 800w, '
    'images/ARIA-TEAM-p-1080.jpeg 1080w, images/ARIA-TEAM.jpg 1200w" alt="ARIA team in protective suits beside a branded ARIA van"/></div></div>'))

# industries we serve, in the same circle-and-label style as the service cards
cards = ''.join(
    f'<div class="service-item-wrap"><a class="service-item w-inline-block" href="{href}"><div class="service-item__image">'
    f'<div class="service-item__icon industry-icon">{ICON(d)}</div></div><div class="service-item__body">'
    f'<h4 class="service-item__title">{t}</h4></div></a></div>' for t, href, d in INDUSTRIES)
s.select_one('#our-services').insert_after(frag(
    '<section class="section" id="industries"><div class="container"><div class="section-titles">'
    '<h3 class="heading-std">Industries We Serve</h3>'
    '<h4 class="subheading-std">Janitorial programs built around the way your facility runs.</h4></div>'
    f'<div class="services-grid industries-grid">{cards}</div></div></section>'))

# closing call to action above the footer
s.select_one('footer').insert_before(frag(
    '<section class="cta-band"><div class="container cta-band__inner"><div><h3 class="cta-band__heading">Ready for a cleaner facility?</h3>'
    '<p class="cta-band__text">Tell us about your site and we&#8217;ll send a proposal within one business day of the survey.</p></div>'
    '<div class="cta-band__btns"><a class="btn-cta" href="#quote">Get a Free Quote</a>'
    '<a class="btn-cta btn-cta--ghost" href="tel:+18888441001">Call 1 (888) 844-1001</a></div></div></section>'))
open(p, 'w', encoding='utf-8').write(str(s))

# --- about: the Ignacio video gets its own section after the intro
p = os.path.join(ROOT, 'about.html')
s = BeautifulSoup(open(p, encoding='utf-8'), 'html.parser')
first = s.select_one('main .section') or s.select_one('main > *')
first.insert_after(frag(
    '<section class="section section--alt about-video"><div class="container"><div class="section-titles">'
    '<h3 class="heading-std">Meet ARIA</h3><h4 class="subheading-std">Watch our video and discover how Aria Commercial Cleaning '
    'Services can do things <strong>The Right Way - for Your Business</strong></h4></div>' + VIMEO + '</div></section>'))
open(p, 'w', encoding='utf-8').write(str(s))
