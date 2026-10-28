/*
 * Home page slideshow: fades between the slides of [data-hero-slider] every few seconds.
 * The first slide is visible without JavaScript; this script only adds rotation and dots.
 */
(function () {
  'use strict';

  var INTERVAL_MS = 5000;

  function init(root) {
    var slides = root.querySelectorAll('.hero-slider__slide');
    var dotsBox = root.querySelector('[data-hero-dots]');
    if (slides.length < 2 || !dotsBox) { return; }

    var current = 0;
    var timer = null;
    var dots = [];

    function show(index) {
      current = (index + slides.length) % slides.length;
      for (var i = 0; i < slides.length; i++) {
        var active = i === current;
        slides[i].classList.toggle('is-active', active);
        dots[i].classList.toggle('is-active', active);
      }
    }

    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function start() { stop(); timer = setInterval(function () { show(current + 1); }, INTERVAL_MS); }

    for (var i = 0; i < slides.length; i++) {
      (function (index) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'hero-slider__dot';
        dot.setAttribute('aria-label', 'اسلاید ' + (index + 1));
        dot.addEventListener('click', function () { show(index); start(); });
        dotsBox.appendChild(dot);
        dots.push(dot);
      })(i);
    }

    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', start);
    show(0);
    start();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var roots = document.querySelectorAll('[data-hero-slider]');
    for (var i = 0; i < roots.length; i++) { init(roots[i]); }
  });
})();
