// Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

// Block sitemap.xml fetches triggered by Weglot's hreflang tags detected by MkDocs Material
(() => {
  const EMPTY_SITEMAP = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>`;

  const originalFetch = window.fetch;
  window.fetch = function (url, options) {
    if (typeof url === "string" && url.includes("/sitemap.xml")) {
      return Promise.resolve(
        new Response(EMPTY_SITEMAP, { status: 200, headers: { "Content-Type": "application/xml" } }),
      );
    }
    return originalFetch.apply(this, arguments);
  };

  const originalXHROpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    if (typeof url === "string" && url.includes("/sitemap.xml")) {
      this._blockRequest = true;
    }
    return originalXHROpen.apply(this, arguments);
  };

  const originalXHRSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function () {
    if (this._blockRequest) {
      Object.defineProperty(this, "status", { value: 200 });
      Object.defineProperty(this, "responseText", { value: EMPTY_SITEMAP });
      Object.defineProperty(this, "response", { value: EMPTY_SITEMAP });
      Object.defineProperty(this, "responseXML", {
        value: new DOMParser().parseFromString(EMPTY_SITEMAP, "application/xml"),
      });
      this.dispatchEvent(new Event("load"));
      return;
    }
    return originalXHRSend.apply(this, arguments);
  };
})();

// Apply theme colors based on dark/light mode
const applyTheme = (isDark) => {
  document.body.setAttribute("data-md-color-scheme", isDark ? "slate" : "default");
  document.body.setAttribute("data-md-color-primary", isDark ? "black" : "indigo");
};

// Sync widget theme with Material theme
const syncWidgetTheme = () => {
  const isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
};

// Check and apply appropriate theme based on system/user preference
const checkTheme = () => {
  const palette = JSON.parse(localStorage.getItem(".__palette") || "{}");
  if (palette.index === 0) {
    applyTheme(window.matchMedia("(prefers-color-scheme: dark)").matches);
    syncWidgetTheme();
  }
};

// Initialize theme handling on page load
document.addEventListener("DOMContentLoaded", () => {
  checkTheme();
  syncWidgetTheme();

  // Watch for system theme changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", checkTheme);

  // Watch for theme toggle changes
  document.getElementById("__palette_1")?.addEventListener("change", (e) => {
    if (e.target.checked) setTimeout(checkTheme);
  });

  // Watch for Material theme changes and sync to widget
  new MutationObserver(syncWidgetTheme).observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"],
  });
});

// Ultralytics Chat Widget ---------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const ultralyticsChat = new UltralyticsChat({
    welcome: {
      title: "Hello 👋",
      message: "Ask about YOLO, tutorials, training, export, deployment, or troubleshooting.",
      chatExamples: [
        "What's new in SAM 3?",
        "How can I get started with YOLO26?",
        "How does Enterprise Licensing work?",
      ],
      searchExamples: [
        "YOLO26 quickstart",
        "custom dataset training",
        "model export formats",
        "object detection tutorial",
        "hyperparameter tuning",
      ],
    },
  });

  const headerElement = document.querySelector(".md-header__inner");
  const searchContainer = headerElement?.querySelector(".md-header__source");

  if (headerElement && searchContainer) {
    const searchBar = document.createElement("div");
    searchBar.className = "ult-header-search";
    const hotkey = /Mac|iPod|iPhone|iPad/.test(navigator.platform) ? "⌘K" : "Ctrl+K";
    searchBar.innerHTML = `
      <button class="ult-search-button" title="Search documentation (${hotkey})" aria-label="Search documentation">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <span>Search</span>
        <span class="ult-search-hotkey" aria-hidden="true">${hotkey}</span>
      </button>
    `;
    headerElement.insertBefore(searchBar, searchContainer);

    const defaultSearchToggle = headerElement.querySelector('label[for="__search"]');
    const defaultSearchInput = document.getElementById("__search");
    const defaultSearchDialog = document.querySelector(".md-search");
    if (defaultSearchToggle) {
      defaultSearchToggle.setAttribute("aria-hidden", "true");
      defaultSearchToggle.style.display = "none";
    }
    if (defaultSearchInput) {
      defaultSearchInput.setAttribute("tabindex", "-1");
      defaultSearchInput.setAttribute("aria-hidden", "true");
    }
    if (defaultSearchDialog) defaultSearchDialog.style.display = "none";

    searchBar.querySelector(".ult-search-button").addEventListener("click", () => {
      ultralyticsChat?.toggle(true, "search");
    });
  }
});

// Fix language switcher links to preserve current page path, query string, and hash
(() => {
  function fixLanguageLinks() {
    const path = location.pathname;
    const links = document.querySelectorAll(".md-select__link[hreflang]");
    if (!links.length) return;

    // Derive language codes from the actual links (config-driven)
    const langCodes = Array.from(links)
      .map((link) => link.getAttribute("hreflang"))
      .filter(Boolean);
    const defaultLang =
      Array.from(links)
        .find((link) => link.getAttribute("href") === "/")
        ?.getAttribute("hreflang") || "en";

    // Extract base path (without leading slash and language prefix)
    let basePath = path.startsWith("/") ? path.slice(1) : path;
    for (const code of langCodes) {
      if (code === defaultLang) continue;
      const prefix = `${code}/`;
      if (basePath === code || basePath === prefix) {
        basePath = "";
        break;
      }
      if (basePath.startsWith(prefix)) {
        basePath = basePath.slice(prefix.length);
        break;
      }
    }

    // Preserve query string and hash
    const suffix = location.search + location.hash;

    // Update all language links
    links.forEach((link) => {
      const lang = link.getAttribute("hreflang");
      link.href =
        lang === defaultLang
          ? `${location.origin}/${basePath}${suffix}`
          : `${location.origin}/${lang}/${basePath}${suffix}`;
    });
  }

  // Run on load and navigation
  fixLanguageLinks();

  if (typeof document$ !== "undefined") {
    document$.subscribe(() => setTimeout(fixLanguageLinks, 50));
  }
})();

// Gemini-inspired brand motion system -------------------------------------------------------------------------------
(() => {
  const BRAND_TOKENS = {
    duration: {
      xs: 140,
      sm: 220,
      md: 380,
      lg: 640,
    },
    easing: {
      standard: "cubic-bezier(0.2, 0, 0, 1)",
      emphasis: "cubic-bezier(0.2, 0.8, 0.2, 1)",
      exit: "cubic-bezier(0.4, 0, 1, 1)",
    },
    colors: {
      primary: "#4285f4",
      secondary: "#a142f4",
      success: "#34a853",
      error: "#ea4335",
      warning: "#fbbc05",
      info: "#4fc3f7",
    },
  };

  const BRAND_PRESETS = {
    loading: { className: "brand-motion-loading" },
    enter: { className: "brand-motion-enter" },
    exit: { className: "brand-motion-exit" },
    hover: { className: "brand-motion-hover" },
    switch: { className: "brand-motion-switch" },
    success: { className: "brand-feedback--success" },
    error: { className: "brand-feedback--error" },
    empty: { className: "brand-empty-state" },
  };

  const brandMetrics = {
    bootStart: performance.now(),
    fcp: null,
    lcp: null,
    cls: 0,
    frameReady: null,
  };

  let toastLayer;
  let motionObserver;

  const emitMetric = (name, detail = {}) => {
    window.dispatchEvent(new CustomEvent("ult:brand-motion-metric", { detail: { name, ...detail } }));
  };

  const getToastLayer = () => {
    if (toastLayer?.isConnected) return toastLayer;
    toastLayer = document.createElement("div");
    toastLayer.className = "brand-toast-layer";
    document.body.appendChild(toastLayer);
    return toastLayer;
  };

  const showToast = ({ type = "success", title = "Done", message = "", timeout = 2400 } = {}) => {
    const layer = getToastLayer();
    const toast = document.createElement("div");
    toast.className = `brand-toast brand-toast--${type}`;
    toast.innerHTML = `
      <span class="brand-toast__title">${title}</span>
      <span class="brand-toast__body">${message}</span>
    `;
    layer.appendChild(toast);
    emitMetric("toast", { type, title });
    window.setTimeout(() => {
      toast.classList.add("brand-motion-exit");
      window.setTimeout(() => toast.remove(), BRAND_TOKENS.duration.sm);
    }, timeout);
    return toast;
  };

  const markFeedback = (node, type = "success") => {
    if (!node) return;
    const className = type === "error" ? BRAND_PRESETS.error.className : BRAND_PRESETS.success.className;
    node.classList.remove(BRAND_PRESETS.error.className, BRAND_PRESETS.success.className);
    node.classList.add(className);
    window.setTimeout(() => node.classList.remove(className), 1600);
  };

  const createEmptyState = (
    container,
    { title = "Nothing here yet", description = "Try changing filters or searching another topic." } = {},
  ) => {
    if (!container) return null;
    const empty = document.createElement("div");
    empty.className = BRAND_PRESETS.empty.className;
    empty.innerHTML = `<strong>${title}</strong><span>${description}</span>`;
    container.appendChild(empty);
    return empty;
  };

  const observeTargets = (root = document) => {
    const targets = root.querySelectorAll(
      ".md-content__inner > h1, .md-content__inner > h2, .md-content__inner > h3, .md-content__inner > p, .md-content__inner > ul, .md-content__inner > ol, .md-content__inner > .md-typeset__table, .md-content__inner > .highlight, .md-content__inner > .admonition, .md-content__inner > details, .md-content__inner > blockquote",
    );
    targets.forEach((node) => node.classList.add("motion-target"));

    if (motionObserver) motionObserver.disconnect();
    motionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          motionObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.14, rootMargin: "0px 0px -8% 0px" },
    );

    targets.forEach((node) => motionObserver.observe(node));
  };

  const enhanceInteractiveSurfaces = (root = document) => {
    root
      .querySelectorAll(
        ".ult-search-button, .md-typeset .md-button, .md-nav__link, .md-tabs__link, .share-button, .md-top, .md-typeset .admonition, .md-typeset details",
      )
      .forEach((node) => node.classList.add("brand-motion-hover"));
  };

  const setupThemeSwitchMotion = () => {
    document.documentElement.classList.add("brand-motion-switch");
    document.querySelectorAll('input[name="__palette"]').forEach((input) => {
      input.addEventListener("change", () => {
        document.documentElement.classList.add("is-switching");
        emitMetric("theme-switch");
        window.setTimeout(() => document.documentElement.classList.remove("is-switching"), BRAND_TOKENS.duration.md);
      });
    });
  };

  const setupCopyFeedback = (root = document) => {
    root.querySelectorAll("button[data-clipboard-target], .md-clipboard").forEach((button) => {
      if (button.dataset.brandMotionBound === "true") return;
      button.dataset.brandMotionBound = "true";
      button.addEventListener("click", () => {
        markFeedback(button, "success");
        showToast({ type: "success", title: "Copied", message: "Code snippet copied to clipboard." });
      });
    });
  };

  const setupPageExitMotion = () => {
    if (document.body.dataset.brandExitBound === "true") return;
    document.body.dataset.brandExitBound = "true";
    document.addEventListener(
      "click",
      (event) => {
        const link = event.target.closest("a[href]");
        if (!link) return;
        const href = link.getAttribute("href") || "";
        const isInternal = href.startsWith("/") || href.startsWith("#") || href.startsWith(location.origin);
        if (!isInternal || href.startsWith("#")) return;
        document.querySelector(".md-main__inner")?.classList.add("brand-motion-exit");
      },
      true,
    );
  };

  const setupSearchLoading = () => {
    const button = document.querySelector(".ult-search-button");
    if (!button || button.dataset.brandReady === "true") return;
    button.dataset.brandReady = "true";
    button.classList.add("brand-motion-loading");
    requestAnimationFrame(() => {
      requestAnimationFrame(() => button.classList.remove("brand-motion-loading"));
    });
  };

  const setupPerformanceObservers = () => {
    if (window.__ultBrandMotionPerfBound) return;
    window.__ultBrandMotionPerfBound = true;

    try {
      new PerformanceObserver((entryList) => {
        entryList.getEntries().forEach((entry) => {
          if (entry.name === "first-contentful-paint") {
            brandMetrics.fcp = entry.startTime;
            emitMetric("fcp", { value: brandMetrics.fcp });
          }
        });
      }).observe({ type: "paint", buffered: true });
    } catch {}

    try {
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        if (lastEntry) {
          brandMetrics.lcp = lastEntry.startTime;
          emitMetric("lcp", { value: brandMetrics.lcp });
        }
      }).observe({ type: "largest-contentful-paint", buffered: true });
    } catch {}

    try {
      new PerformanceObserver((entryList) => {
        entryList.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) {
            brandMetrics.cls += entry.value;
          }
        });
        emitMetric("cls", { value: brandMetrics.cls });
      }).observe({ type: "layout-shift", buffered: true });
    } catch {}
  };

  const finalizeFrameMetric = () => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        brandMetrics.frameReady = performance.now() - brandMetrics.bootStart;
        emitMetric("frame-ready", { value: brandMetrics.frameReady });
      });
    });
  };

  const initBrandMotion = () => {
    document.documentElement.classList.add("brand-motion-ready");
    observeTargets(document);
    enhanceInteractiveSurfaces(document);
    setupThemeSwitchMotion();
    setupCopyFeedback(document);
    setupPageExitMotion();
    setupSearchLoading();
    finalizeFrameMetric();
  };

  window.UltBrandMotion = {
    version: "1.0.0",
    tokens: BRAND_TOKENS,
    presets: BRAND_PRESETS,
    metrics: brandMetrics,
    observe(root = document) {
      observeTargets(root);
      enhanceInteractiveSurfaces(root);
    },
    toast: showToast,
    success(node, message = "Operation completed successfully.") {
      markFeedback(node, "success");
      return showToast({ type: "success", title: "Success", message });
    },
    error(node, message = "Something went wrong. Please try again.") {
      markFeedback(node, "error");
      return showToast({ type: "error", title: "Error", message });
    },
    empty(container, options) {
      return createEmptyState(container, options);
    },
    switch(node = document.documentElement) {
      node.classList.add("is-switching");
      window.setTimeout(() => node.classList.remove("is-switching"), BRAND_TOKENS.duration.md);
    },
    track(name, detail = {}) {
      emitMetric(name, detail);
    },
  };

  document.addEventListener("DOMContentLoaded", () => {
    setupPerformanceObservers();
    initBrandMotion();
  });

  if (typeof document$ !== "undefined") {
    document$.subscribe(() => {
      window.setTimeout(initBrandMotion, 40);
    });
  }
})();
// Gemini-inspired brand motion system -------------------------------------------------------------------------------
