/* Early boot: consent-gated culture + reading prefs (cookies + localStorage). */
(function () {
  var D = document.documentElement;
  var YEAR = 365 * 24 * 60 * 60;
  var DAY = 24 * 60 * 60;

  function getCookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/[.$?*|{}()[\]\\/+^]/g, '\\$&') + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  function setCookie(name, value, maxAge) {
    var secure = location.protocol === 'https:' ? '; Secure' : '';
    document.cookie =
      name +
      '=' +
      encodeURIComponent(value) +
      '; Path=/' +
      '; Max-Age=' +
      (maxAge | 0) +
      '; SameSite=Lax' +
      secure;
  }
  /* Expose cookie helpers early; news-tick and other UI may call before site.js */
  function delCookie(name) {
    setCookie(name, '', 0);
  }

  function consent() {
    return getCookie('haoma_consent');
  }
  function allowed() {
    return consent() === '1';
  }

  function readLS(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }
  function writeLS(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
  }
  function clearLS(key) {
    try {
      localStorage.removeItem(key);
    } catch (e) {}
  }

  function getCulture() {
    if (!allowed()) return 'base';
    return getCookie('haoma_culture') || readLS('culture') || 'base';
  }
  function setCulture(p) {
    if (!allowed()) return;
    setCookie('haoma_culture', p || 'base', YEAR);
    writeLS('culture', p || 'base');
  }

  function getPrefs() {
    if (!allowed()) return {};
    var raw = getCookie('haoma_prefs') || readLS('prefs') || '{}';
    try {
      return JSON.parse(raw) || {};
    } catch (e) {
      return {};
    }
  }
  function setPrefs(P) {
    if (!allowed()) return;
    var s = JSON.stringify(P || {});
    setCookie('haoma_prefs', s, YEAR);
    writeLS('prefs', s);
  }

  function getLast() {
    if (!allowed()) return '';
    return getCookie('haoma_last') || readLS('haoma_last') || '';
  }
  function setLast(path) {
    if (!allowed()) return;
    var p = String(path || '').split('?')[0].split('#')[0];
    if (!p || p.length > 400) return;
    setCookie('haoma_last', p, YEAR);
    writeLS('haoma_last', p);
  }

  function setConsent(on) {
    if (on) {
      setCookie('haoma_consent', '1', YEAR);
      D.dataset.consent = '1';
    } else {
      setCookie('haoma_consent', '0', 90 * DAY);
      D.dataset.consent = '0';
      delCookie('haoma_culture');
      delCookie('haoma_prefs');
      delCookie('haoma_last');
      delCookie('haoma_hide_tick');
      clearLS('culture');
      clearLS('prefs');
      clearLS('haoma_last');
      clearLS('haoma_reads');
      clearLS('haoma_saved');
      clearLS('haoma_resume');
      try { sessionStorage.removeItem('haoma_hide_news_tick'); } catch (e) {}
      if (window.haoma && typeof window.haoma.clearReads === 'function') {
        window.haoma.clearReads();
      }
      if (window.haoma && typeof window.haoma.clearStudy === 'function') {
        window.haoma.clearStudy();
      }
    }
  }

  var c = consent();
  D.dataset.consent = c || '';
  var p = 'base';
  var P = {};
  if (c === '1') {
    p = getCulture();
    P = getPrefs();
  }
  D.dataset.pick = p;
  if (!D.hasAttribute('data-fixed')) D.dataset.culture = p;
  D.style.setProperty('--read', (P.size || 1.2) + 'rem');
  D.dataset.dock = P.dock || 'start';
  D.dataset.nav = P.nav || 'shown';
  D.dataset.focus = P.focus ? '1' : '0';
  if (P.reader) {
    D.setAttribute('data-reader', '1');
    D.setAttribute('data-reader-tone', P.readerTone || 'calm');
  }

  window.haoma = {
    allowed: allowed,
    consent: consent,
    setConsent: setConsent,
    getCulture: getCulture,
    setCulture: setCulture,
    getPrefs: getPrefs,
    setPrefs: setPrefs,
    getLast: getLast,
    setLast: setLast,
    getCookie: getCookie,
    setCookie: setCookie
  };
})();
