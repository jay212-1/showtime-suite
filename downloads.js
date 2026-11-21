// Download buttons from the newest GitHub release of each app. The visitor's
// system gets the big button; the others are listed next to it. Without
// JavaScript or when GitHub cannot be reached, the button leads to the
// release page.
(function () {
  "use strict";
  var NAMES = { macos: "macOS", windows: "Windows", linux: "Linux" };
  function system() {
    var p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
    var ua = navigator.userAgent || "";
    // Phones and tablets cannot run the apps: no system is preferred there.
    if (/Android|iPhone|iPad|Mobile/i.test(ua) || navigator.maxTouchPoints > 1 && /Mac/i.test(p)) return "";
    if (/Mac/i.test(p + ua)) return "macos";
    if (/Win/i.test(p + ua)) return "windows";
    if (/Linux|X11/i.test(p + ua)) return "linux";
    return "";
  }
  function find(assets, rule) {
    for (var i = 0; i < assets.length; i++) {
      var n = assets[i].name;
      if ((!rule.prefix || n.indexOf(rule.prefix) === 0) &&
          (!rule.match || n.indexOf(rule.match) === 0) &&
          n.slice(-rule.suffix.length) === rule.suffix) return assets[i];
    }
    return null;
  }
  function mb(bytes) { return (bytes / 1048576).toFixed(bytes < 10485760 ? 1 : 0) + " MB"; }
  function link(cls, href, text) {
    var a = document.createElement("a");
    a.className = cls;
    a.href = href;
    a.textContent = text;
    return a;
  }
  var cache = {};
  function latest(repo) {
    if (!cache[repo]) {
      cache[repo] = fetch("https://api.github.com/repos/" + repo + "/releases/latest", {
        headers: { Accept: "application/vnd.github+json" }
      }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    }
    return cache[repo];
  }
  var mine = system();
  document.querySelectorAll(".downloads").forEach(function (box) {
    var repo = box.dataset.releases;
    var rules = JSON.parse(box.dataset.rules || "{}");
    var extra = box.dataset.extra ? JSON.parse(box.dataset.extra) : [];
    latest(repo).then(function (rel) {
      var page = rel.html_url;
      var assets = rel.assets || [];
      var order = ["macos", "windows", "linux"].filter(function (s) { return rules[s]; });
      order.sort(function (a, b) { return (b === mine) - (a === mine); });
      box.textContent = "";
      var row = document.createElement("div");
      row.className = "row";
      var missing = [];
      order.forEach(function (s, i) {
        var a = find(assets, rules[s]);
        if (!a) { missing.push(NAMES[s]); return; }
        var big = s === mine || (i === 0 && !mine);
        var el = link(big ? "btn main" : "btn", a.browser_download_url,
          (big ? "Download for " : "") + NAMES[s]);
        el.title = a.name + " · " + mb(a.size);
        row.appendChild(el);
      });
      if (row.firstChild && !row.querySelector(".main")) row.firstChild.className = "btn main";
      box.appendChild(row);
      var ver = document.createElement("p");
      ver.className = "ver";
      ver.textContent = "Version " + String(rel.tag_name || "").replace(/^v/, "");
      ver.appendChild(document.createTextNode(" · "));
      ver.appendChild(link("", page, "release notes"));
      if (missing.length) {
        ver.appendChild(document.createTextNode(" · " + missing.join(" and ") + " follow" + (missing.length === 1 ? "s" : "") + " shortly"));
      }
      box.appendChild(ver);
      if (extra.length) {
        var more = document.createElement("div");
        more.className = "row extra";
        extra.forEach(function (x) {
          var a = find(assets, x);
          if (a) {
            var el = link("btn small", a.browser_download_url, x.label);
            el.title = a.name + " · " + mb(a.size);
            more.appendChild(el);
          }
        });
        if (more.children.length) box.appendChild(more);
      }
    }).catch(function () { /* keep the plain link to the release page */ });
  });
})();
