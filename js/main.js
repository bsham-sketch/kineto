/* ==========================================================================
   KINETO INDIA — interactions
   Vanilla, no dependencies. Everything degrades to readable static HTML.
   ========================================================================== */

(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------------
     1. Reveal on scroll
     IntersectionObserver, threshold 0.15, slightly inset at the bottom.
     One-shot: once a block has arrived, it stays.
     ------------------------------------------------------------------ */

  function initReveal() {
    var blocks = document.querySelectorAll(".reveal");

    if (!("IntersectionObserver" in window) || reduceMotion) {
      blocks.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    blocks.forEach(function (el) {
      var delay = el.getAttribute("data-delay");
      if (delay) el.style.transitionDelay = delay + "ms";
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -5% 0px" }
    );

    blocks.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------------------
     2. Mega menu
     ------------------------------------------------------------------ */

  function initMenu() {
    var burger = document.querySelector("[data-menu-toggle]");
    var menu = document.getElementById("menu");
    if (!burger || !menu) return;

    function setOpen(open) {
      document.body.classList.toggle("menu-open", open);
      document.body.classList.toggle("is-locked", open);
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      menu.setAttribute("aria-hidden", String(!open));
    }

    setOpen(false);

    burger.addEventListener("click", function () {
      setOpen(!document.body.classList.contains("menu-open"));
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("menu-open")) {
        setOpen(false);
        burger.focus();
      }
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setOpen(false); });
    });

    /* Per-item colour wash behind the menu */
    var washes = menu.querySelectorAll(".menu__wash");

    menu.querySelectorAll("[data-wash]").forEach(function (link) {
      function paint(num) {
        washes.forEach(function (w) {
          w.classList.toggle("is-on", num !== null && w.getAttribute("data-wash") === num);
        });
      }
      link.addEventListener("mouseenter", function () { paint(link.getAttribute("data-wash")); });
      link.addEventListener("focus", function () { paint(link.getAttribute("data-wash")); });
      link.addEventListener("mouseleave", function () { paint(null); });
      link.addEventListener("blur", function () { paint(null); });
    });
  }

  /* ------------------------------------------------------------------
     3. Scroll progress rail
     ------------------------------------------------------------------ */

  function initRail() {
    var fill = document.querySelector("[data-rail-fill]");
    if (!fill) return;

    var ticking = false;

    function update() {
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var progress = scrollable > 0 ? window.scrollY / scrollable : 0;
      fill.style.transform = "scaleY(" + progress + ")";
      ticking = false;
    }

    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    update();
  }

  /* ------------------------------------------------------------------
     4. Solve selector (home, section 04)
     ------------------------------------------------------------------ */

  function initSelector() {
    var root = document.querySelector("[data-selector]");
    if (!root) return;

    var buttons = root.querySelectorAll("[data-selector-btn]");
    var panels = root.querySelectorAll("[data-selector-panel]");

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var key = btn.getAttribute("data-selector-btn");

        buttons.forEach(function (b) {
          b.setAttribute("aria-selected", String(b === btn));
        });

        panels.forEach(function (panel) {
          var match = panel.getAttribute("data-selector-panel") === key;
          panel.hidden = !match;
          if (match && !reduceMotion) {
            /* restart the entry animation */
            panel.style.animation = "none";
            void panel.offsetWidth;
            panel.style.animation = "";
          }
        });
      });
    });
  }

  /* ------------------------------------------------------------------
     5. Universe list → crossfading image (home, section 05)
     ------------------------------------------------------------------ */

  function initUniverse() {
    var root = document.querySelector("[data-universe]");
    if (!root) return;

    var rows = root.querySelectorAll("[data-universe-row]");
    var shots = root.querySelectorAll("[data-universe-shot]");

    rows.forEach(function (row) {
      function show() {
        var num = row.getAttribute("data-universe-row");
        shots.forEach(function (shot) {
          shot.classList.toggle("is-on", shot.getAttribute("data-universe-shot") === num);
        });
      }
      row.addEventListener("mouseenter", show);
      row.addEventListener("focus", show, true);
    });
  }

  /* ------------------------------------------------------------------
     6. Solar savings calculator
     Same arithmetic as the original:
       units  = bill / 8
       kW     = max(1, round(units / 120 * 10) / 10)
       cost   = kW * 55,000
       saving = bill * 12 * (home ? 0.85 : 0.90)
       payback = cost / saving
     ------------------------------------------------------------------ */

  function initCalculator() {
    var root = document.querySelector("[data-calc]");
    if (!root) return;

    var slider = root.querySelector("[data-calc-bill]");
    var billOut = root.querySelector("[data-calc-billout]");
    var sizeOut = root.querySelector("[data-calc-size]");
    var saveOut = root.querySelector("[data-calc-saving]");
    var costOut = root.querySelector("[data-calc-cost]");
    var backOut = root.querySelector("[data-calc-payback]");
    var modes = root.querySelectorAll("[data-calc-mode]");

    var mode = "home";

    function inr(n) { return n.toLocaleString("en-IN"); }

    function render() {
      var bill = Number(slider.value);
      var units = bill / 8;
      var kw = Math.max(1, Math.round((units / 120) * 10) / 10);
      var cost = Math.round(kw * 55000);
      var saving = Math.round(bill * 12 * (mode === "home" ? 0.85 : 0.9));
      var payback = Math.round((cost / saving) * 10) / 10;

      billOut.textContent = "₹" + inr(bill);
      sizeOut.textContent = kw + " kW";
      saveOut.textContent = "₹" + inr(saving);
      costOut.textContent = "₹" + inr(cost);
      backOut.textContent = "~" + payback + " years";
    }

    slider.addEventListener("input", render);

    modes.forEach(function (btn) {
      btn.addEventListener("click", function () {
        mode = btn.getAttribute("data-calc-mode");
        modes.forEach(function (b) {
          b.setAttribute("aria-pressed", String(b === btn));
        });
        render();
      });
    });

    render();
  }

  /* ------------------------------------------------------------------
     7. Catalogue filter + search + sort
     ------------------------------------------------------------------ */

  function initCatalogue() {
    var root = document.querySelector("[data-catalogue]");
    if (!root) return;

    var cards = root.querySelectorAll("[data-catalogue-card]");
    var groups = root.querySelectorAll("[data-catalogue-group]");
    var searchInput = root.querySelector("[data-catalogue-search]");
    var sortSelect = root.querySelector("[data-catalogue-sort]");
    var resultCount = root.querySelector("[data-catalogue-results]");
    var drawer = root.querySelector("[data-catalogue-sidebar]");
    var drawerToggle = root.querySelector("[data-catalogue-drawer-toggle]");
    var chipWrap = root.querySelector("[data-catalogue-chips]");
    var empty = root.querySelector("[data-catalogue-empty]");
    var filterButtons = root.querySelectorAll("[data-catalogue-filter]");
    var clearButtons = root.querySelectorAll("[data-catalogue-clear]");

    var state = {
      search: "",
      sort: "name",
      filters: { category: [], series: [], wattage: [], colour: [] }
    };

    function setDrawer(open) {
      if (!drawer || !drawerToggle) return;
      drawer.classList.toggle("is-open", open);
      drawerToggle.setAttribute("aria-expanded", String(open));
    }

    function parseWattage(value) {
      var num = Number((value || "0").toString().match(/\d+(?:\.\d+)?/));
      return Number.isFinite(num) ? num : 0;
    }

    function activeFilters() {
      var all = [];
      Object.keys(state.filters).forEach(function (group) {
        state.filters[group].forEach(function (value) {
          all.push({ group: group, value: value });
        });
      });
      return all;
    }

    function updateChips() {
      if (!chipWrap) return;
      chipWrap.innerHTML = "";
      activeFilters().forEach(function (chip) {
        var button = document.createElement("button");
        button.type = "button";
        button.className = "catalogue__chip";
        button.textContent = chip.value + " ×";
        button.setAttribute("data-chip-group", chip.group);
        button.setAttribute("data-chip-value", chip.value);
        button.addEventListener("click", function () {
          state.filters[chip.group] = state.filters[chip.group].filter(function (item) {
            return item !== chip.value;
          });
          filterButtons.forEach(function (item) {
            if (item.getAttribute("data-catalogue-filter") === chip.group && item.getAttribute("data-filter-value") === chip.value) {
              item.setAttribute("aria-pressed", "false");
            }
          });
          render();
        });
        chipWrap.appendChild(button);
      });
    }

    function syncFilterButtons() {
      filterButtons.forEach(function (button) {
        var group = button.getAttribute("data-catalogue-filter");
        var value = button.getAttribute("data-filter-value");
        var active = state.filters[group] && state.filters[group].indexOf(value) !== -1;
        button.setAttribute("aria-pressed", String(active));
      });
    }

    function matchesCard(card) {
      var text = (card.getAttribute("data-search") || "") + " " + (card.getAttribute("data-name") || "") + " " + (card.getAttribute("data-series") || "");
      if (state.search && text.toLowerCase().indexOf(state.search) === -1) return false;

      if (state.filters.category.length && state.filters.category.indexOf(card.getAttribute("data-category")) === -1) return false;
      if (state.filters.series.length && state.filters.series.indexOf(card.getAttribute("data-series")) === -1) return false;
      if (state.filters.colour.length && state.filters.colour.indexOf(card.getAttribute("data-colour")) === -1) return false;

      if (state.filters.wattage.length) {
        var watt = parseWattage(card.getAttribute("data-wattage"));
        var match = state.filters.wattage.some(function (range) {
          if (range === "0-5") return watt <= 5;
          if (range === "5-10") return watt > 5 && watt <= 10;
          if (range === "10-25") return watt > 10 && watt <= 25;
          if (range === "25+") return watt > 25;
          return false;
        });
        if (!match) return false;
      }

      return true;
    }

    function sortCards(group) {
      if (!sortSelect) return;
      var grid = group.querySelector(".catalogue__grid");
      if (!grid) return;

      var items = Array.prototype.slice.call(grid.querySelectorAll("[data-catalogue-card]"));
      items.sort(function (a, b) {
        var valueA = a.getAttribute("data-name") || "";
        var valueB = b.getAttribute("data-name") || "";
        if (state.sort === "wattage-asc" || state.sort === "wattage-desc") {
          var wattA = parseWattage(a.getAttribute("data-wattage"));
          var wattB = parseWattage(b.getAttribute("data-wattage"));
          return state.sort === "wattage-asc" ? wattA - wattB : wattB - wattA;
        }
        return valueA.localeCompare(valueB);
      });

      items.forEach(function (item) {
        grid.appendChild(item);
      });
    }

    function render() {
      var visibleCount = 0;

      cards.forEach(function (card) {
        var match = matchesCard(card);
        card.hidden = !match;
        if (match) visibleCount += 1;
      });

      groups.forEach(function (group) {
        var visible = Array.prototype.slice.call(group.querySelectorAll("[data-catalogue-card]")).some(function (card) {
          return !card.hidden;
        });
        group.hidden = !visible;
        if (visible) sortCards(group);
      });

      if (resultCount) {
        resultCount.textContent = visibleCount + " products";
      }
      if (empty) {
        empty.hidden = visibleCount !== 0;
      }
      syncFilterButtons();
      updateChips();
    }

    if (searchInput) {
      searchInput.addEventListener("input", function () {
        state.search = searchInput.value.trim().toLowerCase();
        render();
      });
    }

    if (sortSelect) {
      sortSelect.addEventListener("change", function () {
        state.sort = sortSelect.value;
        render();
      });
    }

    filterButtons.forEach(function (button) {
      var group = button.getAttribute("data-catalogue-filter");
      var value = button.getAttribute("data-filter-value");
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", function () {
        var arr = state.filters[group] ? state.filters[group].slice() : [];
        var index = arr.indexOf(value);
        if (index === -1) {
          arr.push(value);
        } else {
          arr.splice(index, 1);
        }
        state.filters[group] = arr;
        button.setAttribute("aria-pressed", String(index === -1));
        render();
      });
    });

    if (drawerToggle) {
      drawerToggle.addEventListener("click", function () {
        var open = drawer && drawer.classList.contains("is-open");
        setDrawer(!open);
      });
    }

    clearButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        state.filters = { category: [], series: [], wattage: [], colour: [] };
        filterButtons.forEach(function (item) {
          item.setAttribute("aria-pressed", "false");
        });
        if (searchInput) searchInput.value = "";
        state.search = "";
        render();
      });
    });

    render();
  }

  /* ------------------------------------------------------------------
     8. Footer year
     ------------------------------------------------------------------ */

  function initYear() {
    document.querySelectorAll("[data-year]").forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* ------------------------------------------------------------------ */

  function boot() {
    initReveal();
    initMenu();
    initRail();
    initSelector();
    initUniverse();
    initCalculator();
    initCatalogue();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
