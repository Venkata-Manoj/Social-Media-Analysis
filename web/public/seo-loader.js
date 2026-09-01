/**
 * seo-loader.js — runtime SEO injector (optional, file:// safe)
 * Fetches ../web/seo.json when served via http/https and patches <head>.
 * Keeps file:// fallback intact — no error if fetch fails (CORS/file://).
 * Usage: add <script src="web/public/seo-loader.js" defer></script> to index.html
 */
(function () {
  var SEO_URLS = ['web/seo.json', '../web/seo.json', './seo.json', 'seo.json'];
  function inject(seo) {
    if (!seo || !seo.site) return;
    var s = seo.site;
    // title
    if (s.title && !document.title.includes('SocialPulse')) document.title = s.title;
    // meta description
    var md = document.querySelector('meta[name="description"]');
    if (!md) {
      md = document.createElement('meta'); md.name = 'description'; document.head.appendChild(md);
    }
    if (s.description) md.content = s.description;
    // canonical — point to current origin when deployed
    var can = document.querySelector('link[rel="canonical"]');
    if (!can) {
      can = document.createElement('link'); can.rel = 'canonical'; document.head.appendChild(can);
    }
    if (location.protocol.startsWith('http') && s.canonical) {
      try { can.href = location.origin + location.pathname.replace(/index\.html$/, ''); } catch(e) {}
    } else if (s.canonical) {
      can.href = s.canonical;
    }
    // theme-color
    var tc = document.querySelector('meta[name="theme-color"]');
    if (!tc && s.themeColor) {
      tc = document.createElement('meta'); tc.name = 'theme-color'; tc.content = s.themeColor; document.head.appendChild(tc);
    }
    // JSON-LD injection if missing
    if (seo.jsonLd && !document.querySelector('script[data-seo="jsonLd"]')) {
      var ld = document.createElement('script'); ld.type = 'application/ld+json'; ld.setAttribute('data-seo','jsonLd');
      ld.textContent = JSON.stringify(seo.jsonLd);
      document.head.appendChild(ld);
    }
  }
  function tryFetch(i) {
    if (i >= SEO_URLS.length) return;
    fetch(SEO_URLS[i], { cache: 'no-store' })
      .then(function(r){ return r.ok ? r.json() : Promise.reject(r.status); })
      .then(inject)
      .catch(function(){ tryFetch(i+1); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ tryFetch(0); });
  else tryFetch(0);
})();
