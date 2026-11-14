/* ヤキトリネクストサークル 公式サイト 共通スクリプト
   - スマホ用ハンバーガーメニューの開閉
   - ページトップボタン
   - トップのカルーセル（CSS アニメーション）の複製処理 */
(function () {
  'use strict';

  // ハンバーガーメニュー
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('global-nav');
  if (toggle && nav) {
    var closeNav = function () {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };
    toggle.addEventListener('click', function () {
      var open = !nav.classList.contains('is-open');
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeNav);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1024) closeNav();
    });
  }

  // ページトップ
  var pagetop = document.querySelector('.pagetop');
  if (pagetop) {
    var onScroll = function () {
      pagetop.classList.toggle('is-visible', window.scrollY > 400);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    pagetop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // カルーセル: 無限ループ用にトラックの中身を複製する（CSS 側で -50% まで移動）
  var track = document.querySelector('.carousel__track');
  if (track && !track.dataset.cloned) {
    track.innerHTML += track.innerHTML;
    track.dataset.cloned = '1';
    track.querySelectorAll('img').forEach(function (img, i) {
      if (i >= track.children.length / 2) img.setAttribute('aria-hidden', 'true');
    });
  }
})();
