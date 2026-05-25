<a href="https://www.ultralytics.com/" target="_blank"><img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg" width="320" alt="Ultralytics logo"></a>

# 📚 Ultralytics Docs

## Gemini-Inspired Motion Spec

The docs theme now includes a reusable Gemini-inspired motion system implemented in:

- `docs/overrides/main.html`
- `docs/overrides/stylesheets/style.css`
- `docs/overrides/javascript/extra.js`

### Upgrade Checklist

1. Replaced the static announcement bar with a branded motion hero.
2. Added unified motion tokens for duration, easing, gradients, surfaces, and shadows.
3. Added 8 reusable animation groups:
    - loading shimmer
    - enter / appear
    - exit / disappear
    - hover lift
    - theme switch wash
    - success feedback
    - error shake
    - empty state float
4. Added runtime motion orchestration API via `window.UltBrandMotion`.
5. Added motion-safe fallbacks for `prefers-reduced-motion`.
6. Added performance event hooks for FCP, LCP, CLS, frame-ready, theme-switch, and toast events.

### Brand Motion Tokens

| Token           | Value                            |
| --------------- | -------------------------------- |
| Primary         | `#4285f4`                        |
| Secondary       | `#a142f4`                        |
| Success         | `#34a853`                        |
| Error           | `#ea4335`                        |
| Warning         | `#fbbc05`                        |
| XS duration     | `140ms`                          |
| SM duration     | `220ms`                          |
| MD duration     | `380ms`                          |
| LG duration     | `640ms`                          |
| Standard easing | `cubic-bezier(0.2, 0, 0, 1)`     |
| Emphasis easing | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| Exit easing     | `cubic-bezier(0.4, 0, 1, 1)`     |

### Runtime API

```js
window.UltBrandMotion.toast({ type: "success", title: "Saved", message: "Changes are live." });
window.UltBrandMotion.success(buttonNode, "Copied successfully.");
window.UltBrandMotion.error(formNode, "Request failed.");
window.UltBrandMotion.empty(containerNode, {
    title: "No results",
    description: "Try another keyword.",
});
window.UltBrandMotion.observe(document);
window.UltBrandMotion.track("custom-event", { source: "docs" });
```

### Performance Targets

- 60 fps for all transform/opacity-driven transitions
- first visual response target: `<=100ms`
- CLS target: `<=0.1`
- no motion-only dependency for core navigation

### Verification Matrix

- Chrome latest
- Edge latest
- Safari latest
- Firefox latest
- iOS Safari
- Android Chrome

### Suggested Manual Test Cases

1. Load the docs homepage and verify hero entrance, chips, and staged content reveal.
2. Hover links, buttons, cards, and admonitions and confirm lift-only motion.
3. Toggle light/dark palette and verify theme wash animation with no layout jump.
4. Copy a code block and verify success toast plus button feedback.
5. Trigger reduced motion in OS settings and verify all animations are effectively disabled.
6. Check Lighthouse / Performance panel for FCP, LCP, CLS, and long tasks.

Welcome to Ultralytics Docs, your comprehensive resource for understanding and utilizing our state-of-the-art [machine learning](https://www.ultralytics.com/glossary/machine-learning-ml) tools and models, including [Ultralytics YOLO](https://docs.ultralytics.com/models/yolo26/). These documents are actively maintained and deployed to [https://docs.ultralytics.com](https://docs.ultralytics.com/) for easy access.

[![pages-build-deployment](https://github.com/ultralytics/docs/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/ultralytics/docs/actions/workflows/pages/pages-build-deployment)
[![Check Broken links](https://github.com/ultralytics/docs/actions/workflows/links.yml/badge.svg)](https://github.com/ultralytics/docs/actions/workflows/links.yml)
[![Check Domains](https://github.com/ultralytics/docs/actions/workflows/check_domains.yml/badge.svg)](https://github.com/ultralytics/docs/actions/workflows/check_domains.yml)
[![Ultralytics Actions](https://github.com/ultralytics/docs/actions/workflows/format.yml/badge.svg)](https://github.com/ultralytics/docs/actions/workflows/format.yml)

<a href="https://discord.com/invite/ultralytics"><img alt="Discord" src="https://img.shields.io/discord/1089800235347353640?logo=discord&logoColor=white&label=Discord&color=blue"></a> <a href="https://community.ultralytics.com/"><img alt="Ultralytics Forums" src="https://img.shields.io/discourse/users?server=https%3A%2F%2Fcommunity.ultralytics.com&logo=discourse&label=Forums&color=blue"></a> <a href="https://www.reddit.com/r/ultralytics/"><img alt="Ultralytics Reddit" src="https://img.shields.io/reddit/subreddit-subscribers/ultralytics?style=flat&logo=reddit&logoColor=white&label=Reddit&color=blue"></a>

## 🛠️ Installation

[![PyPI - Version](https://img.shields.io/pypi/v/ultralytics?logo=pypi&logoColor=white)](https://pypi.org/project/ultralytics/)
[![Downloads](https://static.pepy.tech/badge/ultralytics)](https://clickpy.clickhouse.com/dashboard/ultralytics)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ultralytics?logo=python&logoColor=gold)](https://pypi.org/project/ultralytics/)

To install the `ultralytics` package in developer mode, which allows you to modify the source code directly, ensure you have [Git](https://git-scm.com/) and [Python](https://www.python.org/) 3.8 or later installed on your system. Then, follow these steps:

1.  Clone the `ultralytics` repository to your local machine using Git:

    ```bash
    git clone https://github.com/ultralytics/ultralytics.git
    ```

2.  Navigate to the cloned repository's root directory:

    ```bash
    cd ultralytics
    ```

3.  Install the package in editable mode (`-e`) along with its development dependencies (`[dev]`) using [pip](https://pip.pypa.io/en/stable/):

    ```bash
    pip install -e '.[dev]'
    ```

    This command installs the `ultralytics` package such that changes to the source code are immediately reflected in your environment, ideal for development.

## 🚀 Building and Serving Locally

The `mkdocs serve` command builds and serves a local version of your [MkDocs](https://www.mkdocs.org/) documentation. This is highly useful during development and testing to preview changes.

```bash
mkdocs serve
```

- **Command Breakdown:**
    - `mkdocs`: The main MkDocs command-line interface tool.
    - `serve`: The subcommand used to build and locally serve your documentation site.
- **Note:**
    - `mkdocs serve` includes live reloading, automatically updating the preview in your browser as you save changes to the documentation files.
    - To stop the local server, simply press `CTRL+C` in your terminal.

## 🌍 Building and Serving Multi-Language

If your documentation supports multiple languages, follow these steps to build and preview all versions:

1.  Stage all new or modified language Markdown (`.md`) files using Git:

    ```bash
    git add docs/**/*.md -f
    ```

2.  Build all language versions into the `/site` directory. This script ensures that relevant root-level files are included and clears the previous build:

    ```bash
    # Clear existing /site directory to prevent conflicts
    rm -rf site

    # Build the default language site using the primary config file
    mkdocs build -f docs/mkdocs.yml

    # Loop through each language-specific config file and build its site
    for file in docs/mkdocs_*.yml; do
      echo "Building MkDocs site with $file"
      mkdocs build -f "$file"
    done
    ```

3.  To preview the complete multi-language site locally, navigate into the build output directory and start a simple [Python HTTP server](https://docs.python.org/3/library/http.server.html):
    ```bash
    cd site
    python -m http.server
    # Open http://localhost:8000 in your preferred web browser
    ```
    Access the live preview site at `http://localhost:8000`.

## 📤 Deploying Your Documentation Site

To deploy your MkDocs documentation site, choose a hosting provider and configure your deployment method. Common options include [GitHub Pages](https://pages.github.com/), GitLab Pages, or other static site hosting services.

- Configure deployment settings within your `mkdocs.yml` file.
- Use your hosting provider's recommended workflow (for example running `mkdocs build` in CI or `mkdocs gh-deploy` for GitHub Pages) to publish the generated `site/` directory.

* **GitHub Pages Deployment Example:**
  If deploying to GitHub Pages, you can use the built-in command:

    ```bash
    mkdocs gh-deploy
    ```

    After deployment, you might need to update the "Custom domain" settings in your repository's settings page if you wish to use a personalized URL.

    ![GitHub Pages Custom Domain Setting](https://cdn.jsdelivr.net/gh/ultralytics/assets@main/docs/github-pages-custom-domain-setting.avif)

- For detailed instructions on various deployment methods, consult the official [MkDocs Deploying your docs guide](https://www.mkdocs.org/user-guide/deploying-your-docs/).

## 💡 Contribute

We deeply value contributions from the open-source community to enhance Ultralytics projects. Your input helps drive innovation! Please review our [Contributing Guide](https://docs.ultralytics.com/help/contributing/) for detailed information on how to get involved. You can also share your feedback and ideas through our [Survey](https://www.ultralytics.com/survey?utm_source=github&utm_medium=social&utm_campaign=Survey). A heartfelt thank you 🙏 to all our contributors for their dedication and support!

![Ultralytics open-source contributors](https://raw.githubusercontent.com/ultralytics/assets/main/im/image-contributors.png)

We look forward to your contributions!

## 📜 License

Ultralytics Docs are available under two licensing options to accommodate different usage scenarios:

- **AGPL-3.0 License**: Ideal for students, researchers, and enthusiasts involved in academic pursuits and open collaboration. See the [LICENSE](https://github.com/ultralytics/docs/blob/main/LICENSE) file for full details. This license promotes sharing improvements back with the community.
- **Enterprise License**: Designed for commercial applications, this license allows seamless integration of Ultralytics software and [AI models](https://docs.ultralytics.com/models/) into commercial products and services. Visit [Ultralytics Licensing](https://www.ultralytics.com/license) for more information on obtaining an Enterprise License.

## ✉️ Contact

For bug reports, feature requests, and other issues related to the documentation, please use [GitHub Issues](https://github.com/ultralytics/docs/issues). For discussions, questions, and community support, join the conversation with peers and the Ultralytics team on our [Discord server](https://discord.com/invite/ultralytics)!

<br>
<div align="center">
  <a href="https://github.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-github.png" width="3%" alt="Ultralytics GitHub"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.linkedin.com/company/ultralytics/"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-linkedin.png" width="3%" alt="Ultralytics LinkedIn"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://twitter.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-twitter.png" width="3%" alt="Ultralytics Twitter"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.youtube.com/ultralytics?sub_confirmation=1"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-youtube.png" width="3%" alt="Ultralytics YouTube"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.tiktok.com/@ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-tiktok.png" width="3%" alt="Ultralytics TikTok"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://ultralytics.com/bilibili"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-bilibili.png" width="3%" alt="Ultralytics BiliBili"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://discord.com/invite/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-discord.png" width="3%" alt="Ultralytics Discord"></a>
</div>
