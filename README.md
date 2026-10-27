# ARIA Commercial Cleaning Services website

Static HTML version of ariacleaningservices.com, ported off Webflow.

- `site/` is the website. Point the host at this folder; there is no build step.
- `tools/` holds the scripts that produced `site/` from the Webflow code export (run in order: `localize.py`, `staticize.py`, `home.py`).

## Changes from the Webflow site (agreed in the Oct 6, 2026 huddle)

- Quote form moved into the homepage hero.
- Trust bar under the hero (BBB, minority-owned, insured, OSHA-trained, 70+ years).
- "Industries We Serve" section linking to the industry pages.
- Closing "Get a Free Quote / Call" band above the footer.
- Ignacio intro video moved from the homepage to About Us.
- All styles live in `site/css/aria-updates.css`, layered over the original Webflow CSS.
- Images, videos, jQuery and Slick are served locally instead of from Webflow's CDN.

## Still to do

- Testimonial review text, Knowledge Hub articles and Our Work before-and-afters: waiting on the Webflow CMS CSV exports.
- Forms: the quote and brochure forms need a submission endpoint (e.g. GoHighLevel). Webflow form handling does not work outside Webflow.
- Pages are `about.html`, `services/porter-cleaning-services.html`, etc. Enable clean URLs on the host so the old `/about` style links keep working.
