#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs-html"
PANDOC_FROM = "gfm+raw_html+smart"
CSS_PATH = PurePosixPath("assets/style.css")

STYLE_CSS = """\
:root {
  color-scheme: light;
  --bg: #f5f0e8;
  --panel: rgba(255, 252, 247, 0.94);
  --panel-strong: #fffefb;
  --line: rgba(62, 44, 31, 0.14);
  --ink: #2d2118;
  --muted: #6a5747;
  --accent: #a24616;
  --accent-soft: rgba(162, 70, 22, 0.12);
  --code-bg: #f2ede4;
  --shadow: 0 18px 40px rgba(71, 45, 27, 0.08);
  --radius: 18px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: "Roboto", "Helvetica Neue", Arial, sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(162, 70, 22, 0.08), transparent 28rem),
    linear-gradient(180deg, #faf5ef 0%, #f0e7db 100%);
  line-height: 1.65;
}

a {
  color: var(--accent);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.12em;
}

a:hover {
  text-decoration-thickness: 2px;
}

img {
  max-width: 100%;
  height: auto;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

code,
pre,
kbd,
samp {
  font-family: "SFMono-Regular", Menlo, Consolas, Monaco, monospace;
}

kbd {
  display: inline-block;
  padding: 0.08rem 0.36rem;
  border: 1px solid var(--line);
  border-bottom-width: 2px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.66);
  font-size: 0.82em;
  color: var(--ink);
}

code {
  background: var(--code-bg);
  border-radius: 6px;
  padding: 0.1rem 0.32rem;
  font-size: 0.92em;
}

pre {
  background: #201913;
  color: #f8f4ef;
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  height: auto;
  margin: 0.95rem 0;
  padding: 0.72rem 0.9rem;
  border-radius: 14px;
  overflow-x: auto;
  white-space: pre;
  line-height: 1.45;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.code-block {
  position: relative;
  width: 100%;
  margin: 0.95rem 0;
}

.code-block > pre {
  margin: 0;
}

.copy-code-button {
  position: absolute;
  top: -0.6rem;
  right: 0.78rem;
  z-index: 2;
  padding: 0.34rem 0.62rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 999px;
  background: rgba(35, 26, 19, 0.92);
  color: #f8f4ef;
  font: inherit;
  font-size: 0.78rem;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(20, 14, 10, 0.18);
  transition: background-color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
}

.copy-code-button:hover {
  background: rgba(59, 42, 30, 0.96);
  transform: translateY(-1px);
}

.copy-code-button:focus-visible {
  outline: 2px solid rgba(162, 70, 22, 0.42);
  outline-offset: 2px;
}

.copy-code-button[data-state="copied"] {
  background: rgba(41, 102, 69, 0.96);
}

.copy-code-button[data-state="error"] {
  background: rgba(133, 46, 46, 0.96);
}

pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  display: block;
}

div.sourceCode {
  margin: 0.95rem 0;
  width: 100%;
}

div.sourceCode > pre {
  margin: 0;
  width: 100%;
}

blockquote {
  margin: 1.4rem 0;
  padding: 0.1rem 1rem;
  border-left: 4px solid rgba(162, 70, 22, 0.4);
  background: rgba(255, 255, 255, 0.45);
  border-radius: 0 12px 12px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.4rem 0;
  background: var(--panel-strong);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 10px 24px rgba(66, 45, 30, 0.06);
}

th,
td {
  border: 1px solid var(--line);
  padding: 0.7rem 0.85rem;
  vertical-align: top;
}

th {
  background: rgba(162, 70, 22, 0.08);
  text-align: left;
}

.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(16rem, 20rem) minmax(0, 1fr);
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 1.4rem 1.2rem;
  border-right: 1px solid var(--line);
  background: rgba(249, 243, 235, 0.92);
  backdrop-filter: blur(14px);
}

.sidebar-title {
  margin: 0;
  font-size: 1.2rem;
  font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
}

.sidebar-subtitle {
  margin: 0.45rem 0 1.2rem;
  color: var(--muted);
  font-size: 0.95rem;
}

.search-block {
  margin: 0 0 1rem;
}

.search-label {
  display: block;
  margin-bottom: 0.45rem;
  color: var(--muted);
  font-size: 0.83rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.search-input {
  width: 100%;
  padding: 0.72rem 0.84rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.82);
  color: var(--ink);
  font: inherit;
  outline: 0;
  transition: border-color 140ms ease, box-shadow 140ms ease, background-color 140ms ease;
}

.search-input:focus {
  border-color: rgba(162, 70, 22, 0.42);
  box-shadow: 0 0 0 3px rgba(162, 70, 22, 0.12);
  background: rgba(255, 255, 255, 0.95);
}

.search-hint {
  margin: 0.45rem 0 0;
  color: var(--muted);
  font-size: 0.84rem;
}

.search-panel {
  margin-top: 0.7rem;
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.search-status {
  margin: 0;
  padding: 0.68rem 0.84rem;
  color: var(--muted);
  font-size: 0.9rem;
  border-bottom: 1px solid var(--line);
}

.search-status:empty {
  display: none;
}

.search-results {
  max-height: 18rem;
  overflow-y: auto;
}

.search-result {
  display: block;
  padding: 0.78rem 0.84rem;
  text-decoration: none;
  color: var(--ink);
  border-top: 1px solid var(--line);
}

.search-result:first-child {
  border-top: 0;
}

.search-result:hover {
  background: rgba(162, 70, 22, 0.08);
}

.search-result-title {
  display: block;
  margin-bottom: 0.18rem;
  color: var(--accent);
  font-weight: 700;
}

.search-result-meta {
  display: block;
  margin-bottom: 0.24rem;
  color: var(--muted);
  font-size: 0.82rem;
}

.search-result-snippet {
  display: block;
  color: var(--ink);
  font-size: 0.92rem;
  line-height: 1.45;
}

.search-empty {
  padding: 0.84rem;
  color: var(--muted);
  font-size: 0.92rem;
}

.nav-list,
.index-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-list li + li {
  margin-top: 0.35rem;
}

.nav-link {
  display: block;
  padding: 0.52rem 0.65rem;
  border-radius: 10px;
  color: var(--ink);
  text-decoration: none;
  transition: background-color 140ms ease, transform 140ms ease;
}

.nav-link:hover {
  background: rgba(162, 70, 22, 0.08);
  transform: translateX(1px);
}

.nav-link.current {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
}

.main {
  min-width: 0;
  padding: 1.6rem;
}

.page-card,
.index-hero {
  max-width: 72rem;
  margin: 0 auto;
  background: var(--panel);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 24px;
  box-shadow: var(--shadow);
}

.page-head,
.index-head {
  padding: 1.6rem 1.8rem 1rem;
  border-bottom: 1px solid var(--line);
}

.eyebrow {
  display: inline-flex;
  gap: 0.45rem;
  align-items: center;
  margin-bottom: 0.65rem;
  color: var(--muted);
  font-size: 0.92rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.page-title,
.index-title {
  margin: 0;
  font-size: clamp(1.9rem, 3vw, 2.8rem);
  line-height: 1.08;
  font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
}

.page-meta,
.index-meta {
  margin: 0.55rem 0 0;
  color: var(--muted);
}

.page-body {
  padding: 1.5rem 1.8rem 2rem;
  overflow-wrap: anywhere;
}

.page-body h1,
.page-body h2,
.page-body h3,
.page-body h4,
.page-body h5,
.page-body h6 {
  scroll-margin-top: 1rem;
  line-height: 1.18;
}

.page-body hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 2rem 0;
}

.index-body {
  padding: 1.3rem 1.8rem 2rem;
}

.index-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}

.index-link {
  display: block;
  height: 100%;
  padding: 1rem 1.05rem;
  text-decoration: none;
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.85), rgba(250, 243, 235, 0.85));
  transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
}

.index-link:hover {
  transform: translateY(-2px);
  border-color: rgba(162, 70, 22, 0.32);
  box-shadow: 0 14px 30px rgba(68, 44, 24, 0.08);
}

.index-link strong {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--accent);
}

.index-link small {
  color: var(--muted);
}

.footer-note {
  margin-top: 1.4rem;
  color: var(--muted);
  font-size: 0.94rem;
}

@media (max-width: 960px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .main {
    padding: 1rem;
  }

  .page-head,
  .page-body,
  .index-head,
  .index-body {
    padding-left: 1.1rem;
    padding-right: 1.1rem;
  }
}
"""

SEARCH_SCRIPT = """\
(function () {
  const input = document.getElementById("docs-search-input");
  const panel = document.getElementById("docs-search-panel");
  const status = document.getElementById("docs-search-status");
  const results = document.getElementById("docs-search-results");
  const dataNode = document.getElementById("docs-search-data");

  if (!input || !panel || !status || !results || !dataNode) {
    return;
  }

  let items = [];
  try {
    items = JSON.parse(dataNode.textContent || "[]");
  } catch (error) {
    console.error("No se pudo cargar el índice de búsqueda", error);
    return;
  }

  const normalize = (value) =>
    (value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\\u0300-\\u036f]/g, "")
      .replace(/\\s+/g, " ")
      .trim();

  const escapeHtml = (value) =>
    String(value).replace(/[&<>"']/g, (char) => (
      {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[char]
    ));

  const indexed = items.map((item) => ({
    ...item,
    _title: normalize(item.title),
    _file: normalize(item.file),
    _search: normalize([item.title, item.file, item.text].join(" "))
  }));

  const setCopyState = (button, state, label) => {
    button.dataset.state = state;
    button.textContent = label;
    window.clearTimeout(button._copyTimer);
    button._copyTimer = window.setTimeout(() => {
      button.dataset.state = "";
      button.textContent = "Copiar";
    }, 1600);
  };

  const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        console.warn("Fallo al copiar con Clipboard API; uso fallback", error);
      }
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-9999px";
    textarea.style.left = "-9999px";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();

    let copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (error) {
      console.warn("Fallo al copiar con execCommand", error);
    }

    textarea.remove();
    return copied;
  };

  const attachCopyButtons = () => {
    document.querySelectorAll(".page-body pre").forEach((pre) => {
      let wrapper = pre.parentElement;

      if (wrapper && wrapper.classList.contains("sourceCode")) {
        wrapper.classList.add("code-block");
      } else if (wrapper && wrapper.classList.contains("code-block")) {
        // already wrapped
      } else {
        const generated = document.createElement("div");
        generated.className = "code-block";
        pre.parentNode.insertBefore(generated, pre);
        generated.appendChild(pre);
        wrapper = generated;
      }

      if (!wrapper || wrapper.querySelector(".copy-code-button")) {
        return;
      }

      const button = document.createElement("button");
      button.type = "button";
      button.className = "copy-code-button";
      button.textContent = "Copiar";
      button.setAttribute("aria-label", "Copiar código al portapapeles");

      button.addEventListener("click", async () => {
        const raw = pre.innerText || pre.textContent || "";
        const text = raw.replace(/\\r?\\n$/, "");
        const copied = await copyText(text);
        setCopyState(button, copied ? "copied" : "error", copied ? "Copiado" : "Error");
      });

      wrapper.appendChild(button);
    });
  };

  const clearResults = () => {
    panel.hidden = true;
    status.textContent = "";
    results.innerHTML = "";
  };

  const render = (matches) => {
    if (!matches.length) {
      panel.hidden = false;
      status.textContent = "Sin resultados";
      results.innerHTML = '<div class="search-empty">No se encontraron coincidencias.</div>';
      return;
    }

    panel.hidden = false;
    status.textContent = `${matches.length} resultado${matches.length === 1 ? "" : "s"} · Enter abre el primero`;
    results.innerHTML = matches
      .map(
        (item) => `
          <a class="search-result" href="${escapeHtml(item.href)}">
            <span class="search-result-title">${escapeHtml(item.title)}</span>
            <span class="search-result-meta">${escapeHtml(item.file)}</span>
            <span class="search-result-snippet">${escapeHtml(item.summary)}</span>
          </a>
        `
      )
      .join("");
  };

  const search = () => {
    const query = normalize(input.value);
    if (!query) {
      clearResults();
      return;
    }

    const tokens = query.split(" ").filter(Boolean);
    const matches = indexed
      .map((item) => {
        for (const token of tokens) {
          if (!item._search.includes(token)) {
            return null;
          }
        }

        let score = 0;
        if (item._title.includes(query)) {
          score += 120;
        }
        if (item._file.includes(query)) {
          score += 70;
        }
        if (item._search.includes(query)) {
          score += 40;
        }

        for (const token of tokens) {
          if (item._title.includes(token)) {
            score += 18;
          }
          if (item._file.includes(token)) {
            score += 10;
          }
          if (item._search.includes(token)) {
            score += 4;
          }
        }

        return { ...item, _score: score };
      })
      .filter(Boolean)
      .sort((left, right) => right._score - left._score || left.title.localeCompare(right.title, "es"))
      .slice(0, 10);

    render(matches);
  };

  input.addEventListener("input", search);
  input.addEventListener("focus", search);

  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      input.value = "";
      clearResults();
      input.blur();
      return;
    }

    if (event.key === "Enter") {
      const first = results.querySelector(".search-result");
      if (first) {
        window.location.href = first.getAttribute("href");
      }
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.metaKey || event.ctrlKey || event.altKey) {
      return;
    }

    if (document.activeElement === input) {
      return;
    }

    event.preventDefault();
    input.focus();
    input.select();
  });

  attachCopyButtons();
})();
"""


@dataclass
class Page:
    src: Path
    title: str
    html_name: str
    fragment: str
    plain_text: str
    summary: str
    anchors: dict[str, str] = field(default_factory=dict)
    local_targets: list[str] = field(default_factory=list)


def run_pandoc(path: Path, to: str) -> str:
    result = subprocess.run(
        ["pandoc", "--from", PANDOC_FROM, "--to", to, "--wrap=none", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def iter_nodes(node: object) -> Iterable[dict]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from iter_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_nodes(item)


def inline_text(node: dict) -> str:
    kind = node.get("t")
    content = node.get("c")

    if kind == "Str":
        return content
    if kind in {"Space", "SoftBreak", "LineBreak"}:
        return " "
    if kind == "Code":
        return content[1]
    if kind == "Math":
        return content[1]
    if kind == "RawInline":
        return content[1]
    if kind in {"Emph", "Strong", "Strikeout", "Superscript", "Subscript", "SmallCaps", "Underline"}:
        return stringify_inlines(content)
    if kind == "Quoted":
        return stringify_inlines(content[1])
    if kind == "Cite":
        return stringify_inlines(content[1])
    if kind == "Span":
        return stringify_inlines(content[1])
    if kind == "Link":
        return stringify_inlines(content[1])
    if kind == "Image":
        return stringify_inlines(content[1])
    return ""


def stringify_inlines(nodes: list[dict]) -> str:
    text = "".join(inline_text(node) for node in nodes)
    return re.sub(r"\s+", " ", text).strip()


def normalize_fragment(value: str) -> str:
    return re.sub(r"\s+", " ", unquote(value).strip())


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def summarize_text(title: str, plain_text: str, limit: int = 220) -> str:
    summary = normalize_text(plain_text)
    if summary.startswith(title):
        summary = summary[len(title):].lstrip(" :-\n\t")
    if not summary:
        summary = title
    if len(summary) <= limit:
        return summary
    clipped = summary[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{clipped or summary[:limit]}…"


def heading_aliases(text: str, identifier: str) -> set[str]:
    aliases: set[str] = set()

    def add(value: str) -> None:
        value = normalize_fragment(value)
        if value:
            aliases.add(value)
            aliases.add(value.lower())

    add(identifier)
    add(text)
    add(text.replace(" ", "-"))

    match = re.match(r"^((?:\d+[.\-、]?\s*)+)(.+)$", text)
    if match:
        prefix = match.group(1)
        remainder = match.group(2).strip()
        compact = re.sub(r"\D+", "", prefix)
        add(remainder)
        add(remainder.replace(" ", "-"))
        if compact:
            add(f"{compact}-{remainder}")
            add(f"{compact}-{remainder.replace(' ', '-')}")

    return aliases


def normalize_output_path(raw_path: str) -> str:
    decoded = unquote(raw_path)
    absolute = Path(decoded)
    if absolute.is_absolute():
        for base in (ROOT, ROOT.parent):
            try:
                return PurePosixPath(absolute.resolve().relative_to(base.resolve()).as_posix()).as_posix()
            except ValueError:
                continue

    parts = [part for part in PurePosixPath(decoded).parts if part not in {"", ".", "..", "/"}]
    if parts and parts[0] == "docs":
        parts = parts[1:]
    if not parts:
        return PurePosixPath(decoded).name
    return PurePosixPath(*parts).as_posix()


def is_external(url: str) -> bool:
    lowered = url.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:"))


def rewrite_fragment(fragment: str, anchors: dict[str, str]) -> str:
    if not fragment:
        return fragment

    normalized = normalize_fragment(fragment)
    return anchors.get(normalized) or anchors.get(normalized.lower()) or normalized


def rewrite_url(url: str, current_page: Page, pages_by_md: dict[str, Page]) -> str:
    if not url or is_external(url):
        return url

    split = urlsplit(url)
    raw_path = split.path
    fragment = split.fragment

    if not raw_path:
        if fragment:
            return f"#{rewrite_fragment(fragment, current_page.anchors)}"
        return url

    decoded_path = unquote(raw_path)
    suffix = PurePosixPath(decoded_path).suffix.lower()

    if suffix == ".md":
        target_name = PurePosixPath(decoded_path).name
        target_page = pages_by_md.get(target_name)
        target_html = target_page.html_name if target_page else PurePosixPath(decoded_path).with_suffix(".html").name
        if fragment:
            target_anchors = target_page.anchors if target_page else {}
            return f"{target_html}#{rewrite_fragment(fragment, target_anchors)}"
        return target_html

    rewritten = normalize_output_path(decoded_path)
    if fragment:
        return f"{rewritten}#{fragment}"
    return rewritten


class LinkRewriter(HTMLParser):
    def __init__(self, current_page: Page, pages_by_md: dict[str, Page]) -> None:
        super().__init__(convert_charrefs=False)
        self.current_page = current_page
        self.pages_by_md = pages_by_md
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self._render_tag(tag, attrs, closed=False))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self._render_tag(tag, attrs, closed=True))

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def unknown_decl(self, data: str) -> None:
        self.parts.append(f"<![{data}]>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}>")

    def _render_tag(self, tag: str, attrs: list[tuple[str, str | None]], closed: bool) -> str:
        rendered: list[str] = []
        for key, value in attrs:
            if value is None:
                rendered.append(key)
                continue
            if key in {"href", "src"}:
                value = rewrite_url(value, self.current_page, self.pages_by_md)
            rendered.append(f'{key}="{escape(value, quote=True)}"')

        suffix = " />" if closed else ">"
        attr_blob = f" {' '.join(rendered)}" if rendered else ""
        return f"<{tag}{attr_blob}{suffix}"

    def html(self) -> str:
        return "".join(self.parts)


class HtmlScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.ids: set[str] = set()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._consume(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._consume(attrs)

    def _consume(self, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value is None:
                continue
            if key == "id":
                self.ids.add(unquote(value))
            elif key in {"href", "src"}:
                self.refs.append(value)


def collect_page(path: Path) -> Page:
    ast = json.loads(run_pandoc(path, "json"))
    fragment = run_pandoc(path, "html5")
    plain_text = normalize_text(run_pandoc(path, "plain"))

    headers: list[tuple[int, str, str]] = []
    local_targets: list[str] = []

    for node in iter_nodes(ast):
        kind = node.get("t")
        if kind == "Header":
            level = node["c"][0]
            identifier = node["c"][1][0]
            text = stringify_inlines(node["c"][2])
            headers.append((level, text, identifier))
        elif kind in {"Link", "Image"}:
            target = node["c"][2][0]
            local_targets.append(target)

    title = next((text for level, text, _ in headers if level == 1), None)
    if title is None and headers:
        title = headers[0][1]
    if title is None:
        title = path.stem

    anchors: dict[str, str] = {}
    for _, text, identifier in headers:
        for alias in heading_aliases(text, identifier):
            anchors.setdefault(alias, identifier)

    return Page(
        src=path,
        title=title,
        html_name=f"{path.stem}.html",
        fragment=fragment,
        plain_text=plain_text,
        summary=summarize_text(title, plain_text),
        anchors=anchors,
        local_targets=local_targets,
    )


def build_search_payload(pages: list[Page]) -> str:
    payload = [
        {
            "title": page.title,
            "file": page.src.name,
            "href": page.html_name,
            "summary": page.summary,
            "text": page.plain_text,
        }
        for page in pages
    ]
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def build_nav(current_html: str | None, pages: list[Page]) -> str:
    items = []
    for page in pages:
        current = " current" if page.html_name == current_html else ""
        items.append(
            f'<li><a class="nav-link{current}" href="{escape(page.html_name)}">{escape(page.title)}</a></li>'
        )
    return "\n".join(items)


def wrap_page(
    title: str,
    subtitle: str,
    nav: str,
    body: str,
    current_html: str | None,
    search_payload: str,
) -> str:
    current_marker = escape(current_html or "index.html")
    return f"""<!DOCTYPE html>
<html lang="und">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="{CSS_PATH.as_posix()}" />
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <p class="sidebar-title"><a href="index.html">docs-html</a></p>
      <p class="sidebar-subtitle">HTML estático generado desde {escape(ROOT.name)}</p>
      <div class="search-block" role="search">
        <label class="search-label" for="docs-search-input">Buscar</label>
        <input id="docs-search-input" class="search-input" type="search" placeholder="Tema, archivo o comando" autocomplete="off" spellcheck="false" />
        <p class="search-hint">Pulsa <kbd>/</kbd> para buscar y <kbd>Esc</kbd> para limpiar.</p>
        <div id="docs-search-panel" class="search-panel" hidden>
          <p id="docs-search-status" class="search-status"></p>
          <div id="docs-search-results" class="search-results"></div>
        </div>
      </div>
      <nav>
        <ul class="nav-list">
          <li><a class="nav-link{" current" if current_marker == "index.html" else ""}" href="index.html">Inicio</a></li>
          {nav}
        </ul>
      </nav>
    </aside>
    <main class="main">
      <article class="page-card">
        <header class="page-head">
          <div class="eyebrow">Archivo · {escape(subtitle)}</div>
          <h1 class="page-title">{escape(title)}</h1>
          <p class="page-meta">Versión HTML navegable con recursos locales copiados y enlaces internos corregidos.</p>
        </header>
        <div class="page-body">
{body}
        </div>
      </article>
    </main>
  </div>
  <script id="docs-search-data" type="application/json">{search_payload}</script>
  <script>
{SEARCH_SCRIPT}
  </script>
</body>
</html>
"""


def build_index(pages: list[Page], search_payload: str) -> str:
    nav = build_nav(None, pages)
    cards = "\n".join(
        f'<li><a class="index-link" href="{escape(page.html_name)}"><strong>{escape(page.title)}</strong><small>{escape(page.src.name)}</small></a></li>'
        for page in pages
    )
    body = f"""
<section class="index-hero">
  <header class="index-head">
    <div class="eyebrow">Índice</div>
    <h1 class="index-title">Documentación HTML</h1>
    <p class="index-meta">{len(pages)} páginas convertidas desde Markdown con <code>pandoc</code>.</p>
  </header>
  <div class="index-body">
    <ul class="index-list">
      {cards}
    </ul>
    <p class="footer-note">Los recursos locales enlazados desde la documentación también se copiaron a este árbol de salida para que el sitio pueda abrirse directamente con <code>index.html</code>.</p>
  </div>
</section>
""".strip()
    return wrap_page("docs-html", f"{len(pages)} documentos", nav, body, None, search_payload)


def resolve_source_target(page: Page, target: str) -> Path | None:
    if not target or is_external(target):
        return None

    split = urlsplit(target)
    raw_path = unquote(split.path)
    if not raw_path:
        return None

    candidate = Path(raw_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (page.src.parent / Path(*PurePosixPath(raw_path).parts)).resolve()
    return resolved if resolved.exists() else None


def copy_extra_assets(pages: list[Page]) -> None:
    for directory in ("images", "docker"):
        source_dir = ROOT / directory
        if source_dir.exists():
            shutil.copytree(source_dir, OUT / directory, dirs_exist_ok=True)

    copied: set[Path] = set()
    for page in pages:
        for target in page.local_targets:
            split = urlsplit(target)
            raw_path = unquote(split.path)
            if not raw_path or is_external(target) or PurePosixPath(raw_path).suffix.lower() == ".md":
                continue

            source_path = resolve_source_target(page, target)
            if source_path is None or source_path in copied:
                continue

            relative_out = normalize_output_path(raw_path)
            destination = OUT / Path(*PurePosixPath(relative_out).parts)
            if destination.resolve() == source_path.resolve():
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination)
            copied.add(source_path)


def validate_output() -> None:
    ids_by_file: dict[Path, set[str]] = {}
    refs_by_file: dict[Path, list[str]] = {}

    for html_file in sorted(OUT.glob("*.html")):
        scanner = HtmlScanner()
        scanner.feed(html_file.read_text(encoding="utf-8"))
        ids_by_file[html_file.resolve()] = scanner.ids
        refs_by_file[html_file.resolve()] = scanner.refs

    errors: list[str] = []
    for html_file, refs in refs_by_file.items():
        for ref in refs:
            if not ref or is_external(ref):
                continue

            split = urlsplit(ref)
            path = unquote(split.path)
            fragment = unquote(split.fragment)

            target_path = html_file if not path else (html_file.parent / Path(*PurePosixPath(path).parts)).resolve()
            if not target_path.exists():
                errors.append(f"{html_file.name}: missing target {ref}")
                continue

            if fragment and target_path.suffix.lower() == ".html":
                if fragment not in ids_by_file.get(target_path, set()):
                    errors.append(f"{html_file.name}: missing anchor {ref}")

    if errors:
        details = "\n".join(errors[:30])
        suffix = "\n..." if len(errors) > 30 else ""
        raise SystemExit(f"Validation failed with {len(errors)} issue(s):\n{details}{suffix}")


def main() -> int:
    pages = [collect_page(path) for path in sorted(ROOT.glob("*.md"), key=lambda item: item.name.casefold())]
    pages_by_md = {page.src.name: page for page in pages}
    search_payload = build_search_payload(pages)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / CSS_PATH.parent).mkdir(parents=True, exist_ok=True)
    (OUT / CSS_PATH).write_text(STYLE_CSS, encoding="utf-8")

    copy_extra_assets(pages)
    for page in pages:
        nav = build_nav(page.html_name, pages)
        rewriter = LinkRewriter(page, pages_by_md)
        rewriter.feed(page.fragment)
        wrapped = wrap_page(page.title, page.src.name, nav, rewriter.html(), page.html_name, search_payload)
        (OUT / page.html_name).write_text(wrapped, encoding="utf-8")

    (OUT / "index.html").write_text(build_index(pages, search_payload), encoding="utf-8")
    validate_output()

    print(f"Generated {len(pages)} HTML pages in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
