/* All Improvement Cleaning Services: small progressive-enhancement script.
   Everything degrades gracefully: with JS off, the nav links still work, the
   FAQ <details> still open, the quote form still submits by email, the stats
   still show their final numbers and every reveal element is visible.
   Reveal elements are only ever hidden while this script is known to be
   running -- see the .js / .reveal-ready snippet in each page's <head>. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Mobile nav toggle ------------------------------------------------ */
  var nav = document.querySelector("[data-nav]");
  var toggle = document.querySelector("[data-nav-toggle]");
  if (nav && toggle) {
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
    });
    // close the menu after tapping a real link (not the Services parent)
    nav.querySelectorAll(".nav__links a").forEach(function (a) {
      a.addEventListener("click", function () {
        if (window.innerWidth <= 960 && !a.closest(".has-menu > a")) {
          nav.setAttribute("data-open", "false");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  /* ---- Sticky header: transparent over the hero, solid on scroll -------- */
  /* On the homepage the header carries .over-hero and stays transparent until
     the visitor scrolls past most of the full-screen hero; everywhere else it
     is solid from the top and just gains a shadow. */
  var header = document.querySelector(".site-header");
  if (header) {
    var overHero = header.classList.contains("over-hero");
    var threshold = overHero ? Math.max(120, window.innerHeight * 0.72) : 8;
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > threshold);
    };
    window.addEventListener("resize", function () {
      if (overHero) threshold = Math.max(120, window.innerHeight * 0.72);
      onScroll();
    }, { passive: true });
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- Reveal-on-scroll -------------------------------------------------- */
  /* Claim the reveals before the <head> safety net's timer fires, so it knows
     this script arrived and does not need to un-hide everything itself. */
  window.__revealActive = true;
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length && "IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---- Stat count-up ----------------------------------------------------- */
  /* Each number is <strong data-count="50" data-suffix="%">. The markup ships
     with the final value so no-JS and reduced-motion users see it immediately;
     with motion we reset to 0 and ease up to the target when it scrolls in. */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    var runCount = function (el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var suffix = el.getAttribute("data-suffix") || "";
      if (isNaN(target)) return;
      var dur = 1500, start = null;
      var step = function (ts) {
        if (start === null) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);           // easeOutCubic
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target + suffix;
      };
      requestAnimationFrame(step);
    };
    if ("IntersectionObserver" in window && !reduceMotion) {
      var co = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.textContent = "0" + (e.target.getAttribute("data-suffix") || "");
            runCount(e.target);
            co.unobserve(e.target);
          }
        });
      }, { threshold: 0.5 });
      counters.forEach(function (el) { co.observe(el); });
    }
    // else: leave the pre-rendered final values in place
  }

  /* ---- Star rating gate (/review/) --------------------------------------- */
  /* The stars are ordinary links and each one already points where it should
     go (1-3 to /feedback/, 4-5 to the Google review page), so the page still
     works with this script blocked. All we add here is the wording under the
     stars, the locked-in fill and a short beat after the tap so the visitor
     sees it register before the browser leaves the page. */
  var rating = document.querySelector("[data-rating]");
  if (rating) {
    var stars = [].slice.call(rating.querySelectorAll(".rating__star"));
    var hint = document.querySelector("[data-rating-hint]");
    var ratingStatus = document.querySelector("[data-rating-status]");
    var hintDefault = hint ? hint.innerHTML : "";
    var WORDS = ["", "Not good", "Below par", "Okay", "Great", "Excellent"];
    var locked = false;

    var setHint = function (text) { if (hint) hint.innerHTML = text; };

    stars.forEach(function (star, i) {
      var score = i + 1;
      var preview = function () { if (!locked) setHint(WORDS[score]); };
      star.addEventListener("mouseenter", preview);
      star.addEventListener("focus", preview);

      star.addEventListener("click", function (ev) {
        // let ctrl/cmd/middle clicks open in a new tab the way any link would
        if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return;
        ev.preventDefault();
        if (locked) return;
        locked = true;
        rating.classList.add("is-locked");
        stars.forEach(function (s, j) { s.classList.toggle("is-lit", j <= i); });
        setHint(WORDS[score]);
        if (ratingStatus) {
          ratingStatus.className = "form-status is-ok";
          ratingStatus.textContent = score >= 4
            ? "Thank you! Taking you to Google so you can post it..."
            : "Thank you. Taking you to a short private form so you can tell us what to fix...";
        }
        var href = star.getAttribute("href");
        setTimeout(function () { window.location.href = href; }, 700);
      });
    });

    rating.addEventListener("mouseleave", function () {
      if (!locked) setHint(hintDefault);
    });
  }

  /* ---- Feedback form: pre-select the rating carried over from /review/ ---- */
  var ratingField = document.querySelector("[data-rating-field]");
  if (ratingField) {
    var passed = (location.search.match(/[?&]rating=([1-5])(?:&|$)/) || [])[1];
    if (passed) ratingField.value = passed;
  }

  /* ---- Quote + feedback forms -------------------------------------------- */
  /* The markup carries Netlify Forms attributes, so when this site is hosted
     on Netlify the submission is captured automatically. Everywhere else we
     fall back to opening a pre-filled email to the business. A form can set
     data-subject to override the default "Quote request" subject line. */
  var EMAIL = "aicscu1@gmail.com";
  document.querySelectorAll("form[data-quote], form[data-feedback]").forEach(function (form) {
    var onNetlify = /netlify\.app$/.test(location.hostname) || location.hostname === "";
    form.addEventListener("submit", function (ev) {
      // honeypot: silently drop bots
      var hp = form.querySelector('[name="company-website"]');
      if (hp && hp.value) { ev.preventDefault(); return; }

      // Let Netlify handle it when we're actually on Netlify.
      if (form.hasAttribute("data-netlify") && onNetlify) return;

      // Otherwise build a mailto so the lead is never lost.
      ev.preventDefault();
      var get = function (n) { var f = form.querySelector('[name="' + n + '"]'); return f ? f.value.trim() : ""; };
      var name = get("name"), phone = get("phone"), email = get("email");
      var service = get("service"), message = get("message"), score = get("rating");
      var subject = form.getAttribute("data-subject") ||
        ("Quote request" + (service ? ": " + service : ""));
      var body =
        (score ? "Rating: " + score + " out of 5\n" : "") +
        "Name: " + name + "\n" +
        "Email: " + email + "\n" +
        "Phone: " + phone + "\n" +
        (service ? "Service: " + service + "\n" : "") + "\n" +
        "Details:\n" + message + "\n";
      var status = form.querySelector(".form-status");
      if (status) {
        status.className = "form-status is-ok";
        status.textContent = "Thanks, " + (name || "there") + "! Your email app is opening so you can send this to us. Prefer another way? Email " + EMAIL + ".";
      }
      window.location.href =
        "mailto:" + EMAIL +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
    });
  });

  /* ---- Footer year ------------------------------------------------------- */
  var y = document.querySelector("[data-year]");
  if (y) { y.textContent = new Date().getFullYear(); }
})();
