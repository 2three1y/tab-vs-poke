(function () {
  var filters = document.getElementById('filters');
  var status = document.getElementById('status');
  var days = Array.prototype.slice.call(document.querySelectorAll('section.day'));
  if (!filters || !days.length) return;
  filters.hidden = false;
  var master = document.getElementById('master');
  if (master) master.hidden = false;

  function plural(n) { return n === 1 ? '1 message' : n + ' messages'; }
  function picked(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : 'all';
  }
  function dayName(sec) { return sec.querySelector('h3').textContent; }

  function apply() {
    var who = picked('speaker');
    var day = picked('day');
    var shown = 0, total = 0;
    days.forEach(function (sec) {
      var dayOk = day === 'all' || sec.getAttribute('data-day') === day;
      var n = 0, t = 0;
      sec.querySelectorAll('li.msg').forEach(function (li) {
        t++;
        var ok = dayOk && (who === 'all' || li.getAttribute('data-speaker') === who);
        li.hidden = !ok;
        if (ok) n++;
      });
      // hide a round heading whose list has nothing showing
      sec.querySelectorAll('ol.thread').forEach(function (ol) {
        var any = ol.querySelector('li.msg:not([hidden])');
        var h = ol.previousElementSibling;
        while (h && h.tagName !== 'H4') h = h.previousElementSibling;
        ol.hidden = !any;
        if (h) h.hidden = !any;
        var note = h && h.nextElementSibling;
        if (note && note.classList.contains('roundnote')) note.hidden = !any;
      });
      sec.hidden = n === 0;
      var count = sec.querySelector('.count');
      if (count) count.textContent = n === t ? plural(t) : n + ' of ' + plural(t);
      shown += n; total += t;
    });
    var parts = [];
    parts.push(who === 'all' ? 'both bots' : (who === 'tab' ? 'Tab only' : 'Poke only'));
    if (day !== 'all') {
      var sec = days.filter(function (s) { return s.getAttribute('data-day') === day; })[0];
      if (sec) parts.push(dayName(sec));
    } else {
      parts.push('all days');
    }
    status.textContent = shown === total
      ? 'Showing all ' + plural(total) + '.'
      : 'Showing ' + shown + ' of ' + plural(total) + ': ' + parts.join(', ') + '.';
  }

  filters.addEventListener('change', apply);
  document.getElementById('expand').addEventListener('click', function () {
    document.querySelectorAll('details').forEach(function (d) { d.open = true; });
    status.textContent = 'Everything expanded.';
  });
  document.getElementById('collapse').addEventListener('click', function () {
    document.querySelectorAll('details').forEach(function (d) { d.open = false; });
    status.textContent = 'Everything collapsed.';
  });
  apply();
})();
