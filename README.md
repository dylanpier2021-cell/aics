# All Improvement Cleaning Services (AICS): Website

Static, SEO-structured marketing site for **All Improvement Cleaning Services LLC**
(Urbana, IL). Plain HTML + CSS + a tiny bit of vanilla JS. No build step, no
framework, no dependencies. Every page is a real, crawlable HTML file.

---

## Quick start

There is nothing to install or compile. To preview locally, serve the folder
(don't just double-click the files, because links are root-relative):

```bash
cd "All Improvement"
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy

Point any static host at the repo root.

- **Netlify**: drag the folder in, or connect the repo. `netlify.toml` is already
  configured (publish `.`, no build command, security + cache headers, 404 handling).
  The quote forms use **Netlify Forms** and will be captured automatically.
- **Vercel / Cloudflare Pages / GitHub Pages**: also works as-is. See "Forms" below,
  since Netlify Forms only works on Netlify.

---

## Structure

```
/                                  index.html          Home (hero, services, FAQ)
/about/                            About + values
/services/                         Services hub
/services/commercial-cleaning/     Commercial & office
/services/home-cleaning/           Home / recurring & deep
/services/floor-cleaning-and-waxing/  Strip, wax & buff
/services/window-cleaning/         Windows in & out
/services/move-out-cleaning/       Move-out / move-in
/services/construction-cleaning/   Post-construction
/contact/                          Quote form + NAP
/contact/thank-you/                Post-submit page (noindex)
/404.html                          Not found (noindex)

/assets/css/styles.css             All styling (design tokens in :root)
/assets/js/main.js                 Nav, scroll reveal, form fallback
/assets/img/                       logo.svg, favicon.svg, og-image.png
robots.txt, sitemap.xml, netlify.toml
```

---

## Before launch (do these)

1. **Set the real domain.** Everything currently uses the placeholder
   `https://www.allimprovementcleaning.com`. Find and replace it across all
   `.html` files plus `sitemap.xml` and `robots.txt`:
   ```bash
   grep -rl "allimprovementcleaning.com" . | xargs sed -i '' 's|www\.allimprovementcleaning\.com|YOURDOMAIN.com|g'
   ```
   It appears in each page's `canonical`, `og:url`, `og:image` and the JSON-LD.

2. **Add a phone number.** The site currently drives everything to email +
   the quote form, because no number was available. When there is one:
   - add a click-to-call button in the header/hero,
   - add `"telephone": "+1-217-..."` to the `LocalBusiness` JSON-LD in `index.html`,
   - there's a `TODO` comment marking the spot in `contact/index.html`.

3. **Swap the placeholder photos.** Three spots use a styled placeholder box
   (marked with an HTML comment). Drop real photos in `assets/img/` and replace
   the `.media-frame--ph` div with `<img src="..." alt="...">`:
   - homepage "Why AICS" section → team at work
   - homepage service-area section
   - about page → Israel / the team

4. **Replace the sample testimonials.** `index.html` has three clearly-marked
   placeholder reviews. Swap in real, permission-given client quotes.
   **Note:** they are deliberately *not* marked up as `Review` / `AggregateRating`
   structured data. Only add that schema once the reviews are genuine, otherwise
   it violates Google's review-snippet guidelines and risks a manual action.

5. **Verify the business address.** `301 Plum Tree, Urbana, IL 61802` is published
   in the footer, contact page and `LocalBusiness` schema. If this is a home
   address and Israel would rather not display it publicly, remove the
   `streetAddress` line and run the Google Business Profile as a
   service-area business instead.

---

## Forms

Both quote forms (`index.html` hero, `contact/index.html`) are progressive:

- **On Netlify**: `data-netlify="true"` + a hidden `form-name` field means
  submissions are captured with no backend. Check them under *Forms* in the
  Netlify dashboard, and turn on email notifications to `aics2000@gmail.com`.
- **Anywhere else**: `assets/js/main.js` intercepts the submit and opens a
  pre-filled email to `aics2000@gmail.com`, so a lead is never silently lost.
- A honeypot field (`company-website`) filters bots.

To use Formspree/Basin instead, change the `action` to their endpoint and drop
the `data-netlify` attribute.

---

## SEO notes

- **Structured data**: `LocalBusiness` + `WebSite` (home), `Service` on each of the
  6 service pages, `FAQPage` on the home page and every service page,
  `BreadcrumbList` everywhere, `AboutPage` / `ContactPage` / `CollectionPage`.
  All service pages reference the business via `@id`, so it forms one graph.
  Test with the [Rich Results Test](https://search.google.com/test/rich-results).
- **FAQ content** was drawn from real "People Also Ask" / search-intent research
  for each service (cost, frequency, what's included, insurance, access).
- Every page has a unique `<title>`, meta description, canonical, and exactly one `<h1>`.
- `sitemap.xml` lists the 10 indexable pages. Update `<lastmod>` on real edits and
  submit it in Google Search Console.
- Noindexed on purpose: `/contact/thank-you/` and `/404.html`.

### After launch
- Create/claim the **Google Business Profile** and make the NAP match this site
  exactly (name, address, hours). This matters more than anything on-page for
  local ranking.
- Submit `sitemap.xml` in Search Console and Bing Webmaster Tools.
- Get real reviews flowing to the Google profile.

---

## Editing

The whole design is driven by tokens at the top of `assets/css/styles.css`:

```css
:root {
  --brand: #0e5aa7;   /* deep blue  */
  --accent: #12b981;  /* fresh green */
  ...
}
```

Change those and the entire site re-skins. The header and footer are duplicated
across pages (normal for a static site) so if you edit nav or footer links,
update every `.html` file.
