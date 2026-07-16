/* All Improvement Cleaning Services: small progressive-enhancement script.
   Everything degrades gracefully: with JS off, the nav links still work, the
   FAQ <details> still open, and the quote form still submits by email. */
(function () {
  "use strict";

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
        if (window.innerWidth <= 940 && !a.closest(".has-menu > a")) {
          nav.setAttribute("data-open", "false");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  /* ---- Sticky header shadow on scroll ----------------------------------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- Reveal-on-scroll -------------------------------------------------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---- Quote form ------------------------------------------------------- */
  /* The markup carries Netlify Forms attributes, so when this site is hosted
     on Netlify the submission is captured automatically. Everywhere else we
     fall back to opening a pre-filled email to the business. */
  var EMAIL = "aics2000@gmail.com";
  document.querySelectorAll("form[data-quote]").forEach(function (form) {
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
      var service = get("service"), message = get("message");
      var subject = "Quote request" + (service ? ": " + service : "");
      var body =
        "Name: " + name + "\n" +
        "Email: " + email + "\n" +
        "Phone: " + phone + "\n" +
        "Service: " + service + "\n\n" +
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
