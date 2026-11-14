(function () {
  var section = document.getElementById('ratings');
  if (!section || !window.fetch) return;

  function fmtScore(n) {
    var s = Number(n).toFixed(2);
    return s.replace(/0$/, '').replace(/\.$/, '');
  }

  function fill(key, data, scoreField) {
    var item = section.querySelector('[data-rating="' + key + '"]');
    if (!item || !data) return;
    var score = data[scoreField];
    var count = data.count;
    if (score == null || count == null) return;
    item.querySelector('[data-field="score"]').textContent = fmtScore(score);
    item.querySelector('[data-field="count"]').textContent = Number(count).toLocaleString('ja-JP');
    var stars = item.querySelector('.ratings__stars-on');
    if (stars) stars.style.width = (Math.max(0, Math.min(5, score)) / 5 * 100) + '%';
    if (data.url) item.href = data.url;
    var asof = item.querySelector('[data-field="asof"]');
    var d = data.updated || data.asof;
    if (asof && d) {
      var m = /^(\d{4})-(\d{2})/.exec(d);
      asof.textContent = m ? m[1] + '年' + String(Number(m[2])) + '月時点' : d;
    }
    item.hidden = false;
    section.hidden = false;
  }

  fetch('data/ratings.json', { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (doc) {
      if (!doc) return;
      fill('google', doc.google, 'rating');
      fill('tabelog', doc.tabelog, 'score');
    })
    .catch(function () {});
})();
