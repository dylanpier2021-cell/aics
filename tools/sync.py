#!/usr/bin/env python3
"""
sync.py: propagate site.config.json into every HTML page.

This site is intentionally build-step-free: each page is real, crawlable static
HTML. But values like hours, phone, the base URL and the footer repeat on every
page, which is exactly how they drift. This script makes site.config.json the
single source of truth and rewrites the generated regions in place.

Generated regions are wrapped in markers and are OVERWRITTEN on every run:

    <!-- @shared:footer start --> ... <!-- @shared:footer end -->
    <!-- @shared:consent start --> ... <!-- @shared:consent end -->
    <!-- @shared:business-schema start --> ... <!-- @shared:business-schema end -->
    <!-- @shared:phone start --> ... <!-- @shared:phone end -->

Do not hand-edit inside those markers. Everything else in the HTML is yours.

Usage:  python3 tools/sync.py          (from the project root)
        python3 tools/sync.py --check  (fail if anything would change; for CI)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))

CHECK = "--check" in sys.argv

A = CFG["address"]
H = CFG["hours"]
SA = CFG["serviceArea"]
BASE = CFG["baseUrl"].rstrip("/")
HAS_PHONE = bool(CFG.get("phone"))


# --------------------------------------------------------------------------
# region helpers
# --------------------------------------------------------------------------
def region(name, body):
    return f"<!-- @shared:{name} start -->{body}\n<!-- @shared:{name} end -->"


def replace_region(html, name, body):
    """Replace an existing marked region; return (html, found?)."""
    pat = re.compile(
        rf"<!-- @shared:{name} start -->.*?<!-- @shared:{name} end -->", re.S
    )
    if pat.search(html):
        return pat.sub(lambda _: region(name, body), html, count=1), True
    return html, False


# --------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------
def gen_phone_line(indent="            ", icon_color="#6ee7b7"):
    """Click-to-call line, or a TODO comment while no number exists."""
    if not HAS_PHONE:
        return (
            f'\n{indent}<!-- TODO(SITE_PHONE): no business phone yet. Add "phone" +'
            f' "phoneE164" to site.config.json and run tools/sync.py to place the'
            f' click-to-call link here and everywhere else. -->'
        )
    return (
        f'\n{indent}<a href="tel:{CFG["phoneE164"]}">'
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        f'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7A2 2 0 0 1 22 16.9Z"/>'
        f'</svg> {CFG["phone"]}</a>'
    )


def gen_footer():
    towns = ", ".join(SA["towns"][:-1]) + " and " + SA["towns"][-1]
    phone_html = gen_phone_line(indent="            ")
    return f"""
  <footer class="site-footer">
    <div class="container">
      <div class="footer__grid">
        <div>
          <a class="footer__brand" href="/">
            <img src="/assets/img/logo.svg" alt="" width="40" height="40">
            <span>{CFG['dba']}</span>
          </a>
          <p>{CFG['legalName']} (DBA {CFG['dba']}). Locally owned commercial and residential cleaning for {SA['phrase']}.</p>
        </div>
        <div class="footer__col">
          <h4>Services</h4>
          <ul>
            <li><a href="/services/commercial-cleaning/">Commercial Cleaning</a></li>
            <li><a href="/services/home-cleaning/">Home Cleaning</a></li>
            <li><a href="/services/floor-cleaning-and-waxing/">Floor Cleaning &amp; Waxing</a></li>
            <li><a href="/services/window-cleaning/">Window Cleaning</a></li>
            <li><a href="/services/move-out-cleaning/">Move-Out Cleaning</a></li>
            <li><a href="/services/construction-cleaning/">Construction Cleaning</a></li>
          </ul>
        </div>
        <div class="footer__col">
          <h4>Company</h4>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about/">About Us</a></li>
            <li><a href="/services/">All Services</a></li>
            <li><a href="/contact/">Contact</a></li>
            <li><a href="/#faq">FAQs</a></li>
            <li><a href="{CFG['legalPages']['privacy']}">Privacy Policy</a></li>
            <li><a href="{CFG['legalPages']['terms']}">Terms &amp; Conditions</a></li>
          </ul>
        </div>
        <div class="footer__col">
          <h4>Get in touch</h4>
          <div class="footer__contact">
            <a href="mailto:{CFG['email']}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg> {CFG['email']}</a>{phone_html}
            <address><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 21s-7-4.4-7-10a7 7 0 0 1 14 0c0 5.6-7 10-7 10Z"/><circle cx="12" cy="11" r="2.5"/></svg> <span>{A['street']}<br>{A['city']}, {A['region']} {A['zip']}</span></address>
            <div style="display:flex;gap:11px;align-items:flex-start;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="width:18px;height:18px;color:#6ee7b7;flex:none;margin-top:3px;"><path d="M12 6v6l4 2"/><circle cx="12" cy="12" r="9"/></svg> <span>{H['displayLong']}<br>{H['closedNote']}</span></div>
          </div>
        </div>
      </div>
      <div class="footer__bottom">
        <p>&copy; <span data-year>2026</span> {CFG['legalName']} (DBA {CFG['dba']}) &middot; {A['street']}, {A['city']}, {A['region']} {A['zip']}. All rights reserved.</p>
        <p><a href="{CFG['legalPages']['privacy']}">Privacy Policy</a> &middot; <a href="{CFG['legalPages']['terms']}">Terms &amp; Conditions</a></p>
      </div>
    </div>
  </footer>"""


def gen_consent():
    """A2P 10DLC consent block. VERBIAGE IS CARRIER-REVIEWED: keep both pages
    identical and do not reword without checking compliance."""
    who = f"{CFG['legalName']} DBA {CFG['dba']}"
    return f"""
              <fieldset class="consent">
                <legend>Text message updates (optional)</legend>
                <label class="consent__item">
                  <input type="checkbox" name="sms-transactional" value="yes">
                  <span>By checking this box, I consent to receive transactional messages related to my account, orders, or services I have requested from {who}. These messages may include reminders, order confirmations, and account notifications among others. Message frequency may vary. Message &amp; Data rates may apply. Reply HELP for help or STOP to opt out.</span>
                </label>
                <label class="consent__item">
                  <input type="checkbox" name="sms-marketing" value="yes">
                  <span>By checking this box, I consent to receive marketing and promotional messages, including special offers, discounts, and new product updates, among others, from {who}. Message frequency may vary. Message &amp; Data rates may apply. Reply HELP for help or STOP to opt out.</span>
                </label>
              </fieldset>
              <p class="consent__links"><a href="{CFG['legalPages']['privacy']}">Privacy Policy</a> &middot; <a href="{CFG['legalPages']['terms']}">Terms &amp; Conditions</a></p>"""


def gen_business_schema():
    area = [{"@type": "City", "name": f"{t}, {A['region']}"} for t in SA["towns"]]
    area.append({
        "@type": "GeoCircle",
        "name": f"Within {SA['radiusMiles']} miles of {SA['hub']}",
        "geoMidpoint": {"@type": "GeoCoordinates",
                        "latitude": CFG["geo"]["lat"], "longitude": CFG["geo"]["lng"]},
        "geoRadius": str(SA["radiusMeters"]),
    })
    schema = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "ProfessionalService"],
        "@id": f"{BASE}/#business",
        "name": CFG["brand"],
        "legalName": CFG["legalName"],
        "alternateName": CFG["dba"],
        "url": f"{BASE}/",
        "email": CFG["email"],
        "image": f"{BASE}/assets/img/og-image.png",
        "logo": f"{BASE}/assets/img/logo.svg",
        "description": (
            f"Locally owned commercial and residential cleaning company serving "
            f"{SA['phrase']}. Services include commercial and office cleaning, home "
            f"cleaning, floor stripping and waxing, window cleaning, move-out cleaning "
            f"and post-construction cleaning."
        ),
        "slogan": CFG["tagline"],
        "priceRange": CFG["priceRange"],
        "currenciesAccepted": CFG["currency"],
        "founder": CFG["founder"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": A["street"], "addressLocality": A["city"],
            "addressRegion": A["region"], "postalCode": A["zip"], "addressCountry": A["country"],
        },
        "geo": {"@type": "GeoCoordinates",
                "latitude": CFG["geo"]["lat"], "longitude": CFG["geo"]["lng"]},
        "areaServed": area,
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": H["days"], "opens": H["opens"], "closes": H["closes"],
        }],
        "contactPoint": {
            "@type": "ContactPoint", "contactType": "customer service",
            "email": CFG["email"], "availableLanguage": ["English", "Spanish"],
        },
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n,
             "url": f"{BASE}/services/{s}/"}}
            for n, s in [
                ("Commercial Cleaning", "commercial-cleaning"),
                ("Home Cleaning", "home-cleaning"),
                ("Floor Cleaning and Waxing", "floor-cleaning-and-waxing"),
                ("Window Cleaning", "window-cleaning"),
                ("Move-Out Cleaning", "move-out-cleaning"),
                ("Construction Cleaning", "construction-cleaning"),
            ]
        ],
    }
    if HAS_PHONE:
        schema["telephone"] = CFG["phoneE164"]
        schema["contactPoint"]["telephone"] = CFG["phoneE164"]
    # NOTE: paymentAccepted intentionally omitted until Israel confirms methods.
    body = json.dumps(schema, indent=2, ensure_ascii=False)
    return '\n  <script type="application/ld+json">\n' + body + "\n  </script>"


# --------------------------------------------------------------------------
# per-file transforms
# --------------------------------------------------------------------------
def sync_file(p: Path):
    html = orig = p.read_text(encoding="utf-8")
    notes = []

    # 1. base URL: rewrite any other host used in canonical/og/schema
    for host in set(re.findall(r"https?://([A-Za-z0-9.\-]+)/", html)):
        if host in ("schema.org", "www.w3.org", "fonts.googleapis.com",
                    "fonts.gstatic.com", "maps.google.com", "www.google.com",
                    "images.pexels.com", "search.google.com"):
            continue
        if host != BASE.split("//")[1]:
            html = html.replace(f"https://{host}/", f"{BASE}/")
            html = html.replace(f"http://{host}/", f"{BASE}/")
            notes.append(f"baseUrl {host} -> {BASE.split('//')[1]}")

    # 2. footer
    html, found = replace_region(html, "footer", gen_footer())
    if not found:
        new, n = re.subn(r'<footer class="site-footer">.*?</footer>',
                         lambda _: region("footer", gen_footer()).strip(), html, count=1, flags=re.S)
        if n:
            html = new
            notes.append("footer wrapped+generated")
    else:
        notes.append("footer regenerated")

    # 3. hours anywhere outside the footer (contact block, service sidebars)
    html, n1 = re.subn(r"Mon&ndash;Sat:\s*[^<]*", H["displayLong"] + " ", html)
    html, n2 = re.subn(r"Mon&ndash;Sat,\s*8am&ndash;\d+pm", H["displayShort"], html)
    if n1 or n2:
        notes.append(f"hours x{n1 + n2}")

    # 4. phone regions
    html, found = replace_region(html, "phone", gen_phone_line())
    if found:
        notes.append("phone region")

    # 5. business schema (home page only)
    if p.name == "index.html" and p.parent == ROOT:
        html, found = replace_region(html, "business-schema", gen_business_schema())
        if found:
            notes.append("business schema")

    # 6. consent blocks
    html, found = replace_region(html, "consent", gen_consent())
    if found:
        notes.append("consent")

    if html != orig:
        if not CHECK:
            p.write_text(html, encoding="utf-8")
        return notes
    return []


def main():
    pages = sorted(ROOT.rglob("*.html"))
    changed = 0
    for p in pages:
        notes = sync_file(p)
        rel = p.relative_to(ROOT)
        if notes:
            changed += 1
            print(f"  {'WOULD UPDATE' if CHECK else 'updated'}  {rel}  ({', '.join(notes)})")
    print(f"\n{len(pages)} pages scanned, {changed} {'would change' if CHECK else 'updated'}.")
    if not HAS_PHONE:
        print("NOTE: site.config.json has no phone yet, so phone slots render as TODO comments.")
    if CHECK and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
