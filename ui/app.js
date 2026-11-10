"use strict";

const YOUTUBE = /^https?:\/\/(?:www\.|m\.|music\.)?(?:youtube\.com\/(?:watch\?|shorts\/|live\/|clip\/)|youtu\.be\/)/i;
const ACTIVE = new Set(["downloading", "converting", "sending"]);

const LANGS = ["en", "it", "es"];
const THEMES = ["dark", "light", "system"];
const LANG_KEY = "lang";
const THEME_KEY = "theme";
const ZOOM_KEY = "zoom";
const WELCOME_KEY = "welcome_seen";
const MIN_ZOOM = 0.8;
const MAX_ZOOM = 1.5;
const ZOOM_STEP = 0.1;
const LOCALES = { it: "it-IT", en: "en-GB", es: "es-ES" };

const STRINGS = window.UI_STRINGS || { en: {} };
const GUIDES = window.GUIDE_STEPS || { en: [] };

function readStorage(key) {
  try {
    return localStorage.getItem(key) || "";
  } catch (error) {
    return "";
  }
}

function downloadDetails(job) {
  const template = state.settings.download_details || "🎵 {title}\n⏱ Duration: {duration}\n📦 Size: {size}";
  return template
    .replaceAll("{title}", job.title || job.url || "")
    .replaceAll("{duration}", formatDuration(job.duration))
    .replaceAll("{size}", formatSize(job.size_mb));
}

function writeStorage(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    /* a locked-down profile still gets the language for this session */
  }
}

function dismissStartupSplash() {
  const splash = document.getElementById("startup-splash");
  if (!splash) return;
  splash.classList.add("is-hidden");
  writeStorage(WELCOME_KEY, "1");
  window.setTimeout(() => splash.remove(), 260);
}

function setupStartupSplash() {
  const splash = document.getElementById("startup-splash");
  if (!splash || readStorage(WELCOME_KEY) === "1") {
    splash?.remove();
    return;
  }
  splash.addEventListener("click", dismissStartupSplash, { once: true });
  window.setTimeout(dismissStartupSplash, 1500);
}

function applyZoom(value) {
  const zoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Number(value) || 1));
  document.documentElement.style.setProperty("--app-zoom", zoom);
  writeStorage(ZOOM_KEY, String(zoom));
  const zoomValue = document.getElementById("zoom-value");
  if (zoomValue) zoomValue.textContent = `${Math.round(zoom * 100)}%`;
  const zoomOut = document.getElementById("zoom-out");
  const zoomIn = document.getElementById("zoom-in");
  if (zoomOut) zoomOut.disabled = zoom <= MIN_ZOOM;
  if (zoomIn) zoomIn.disabled = zoom >= MAX_ZOOM;
}

function changeZoom(delta) {
  const current = Number(getComputedStyle(document.documentElement).getPropertyValue("--app-zoom")) || 1;
  applyZoom(Math.round((current + delta) * 10) / 10);
}

function setupTextareaResizing() {
  document.addEventListener("pointerdown", (event) => {
    const edge = event.target.closest(".textarea-resize__edge");
    if (!edge) return;
    const textarea = edge.parentElement?.querySelector("textarea");
    if (!textarea) return;
    event.preventDefault();
    const startY = event.clientY;
    const startHeight = textarea.getBoundingClientRect().height;
    const onMove = (moveEvent) => {
      textarea.style.height = `${Math.max(62, startHeight + moveEvent.clientY - startY)}px`;
    };
    const onUp = () => {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
    };
    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp, { once: true });
  });
}

function setupTextContextMenu() {
  const menu = document.createElement("dialog");
  menu.className = "text-context-menu";
  menu.setAttribute("role", "menu");
  menu.innerHTML = `
    <button type="button" data-command="emoji" role="menuitem">Emoji <span>Win+. </span></button>
    <button type="button" data-command="undo" role="menuitem">Undo <span>Ctrl+Z</span></button>
    <button type="button" data-command="redo" role="menuitem">Redo <span>Ctrl+Shift+Z</span></button>
    <div class="text-context-menu__separator"></div>
    <button type="button" data-command="cut" role="menuitem">Cut <span>Ctrl+X</span></button>
    <button type="button" data-command="copy" role="menuitem">Copy <span>Ctrl+C</span></button>
    <button type="button" data-command="paste" role="menuitem">Paste <span>Ctrl+V</span></button>
    <button type="button" data-command="select-all" role="menuitem">Select all <span>Ctrl+A</span></button>
  `;
  document.body.append(menu);

  let activeField = null;
  let selectedTextValue = "";
  const isTextField = (target) => {
    if (target instanceof HTMLTextAreaElement || target.isContentEditable) return true;
    if (!(target instanceof HTMLInputElement)) return false;
    return !["button", "checkbox", "color", "file", "hidden", "radio", "range", "reset", "submit"].includes(
      target.type,
    );
  };
  const getTextField = (target) => {
    if (target instanceof Element) {
      const field = target.closest("input, textarea, [contenteditable='true']");
      return field && isTextField(field) ? field : null;
    }
    return null;
  };
  const hideMenu = () => {
    if (menu.open) menu.close();
  };

  const updateMenuState = () => {
    const hasSelection = Boolean(selectedTextValue);
    menu.querySelector('[data-command="undo"]').disabled = !activeField;
    menu.querySelector('[data-command="redo"]').disabled = !activeField;
    menu.querySelector('[data-command="cut"]').disabled =
      !activeField || !hasSelection;
    menu.querySelector('[data-command="copy"]').disabled = !hasSelection;
    menu.querySelector('[data-command="paste"]').disabled = !activeField;
  };

  document.addEventListener("contextmenu", (event) => {
    const field = getTextField(event.target);
    const pageSelection = window.getSelection()?.toString() || "";
    if (!field && !pageSelection) return;
    event.preventDefault();
    activeField = field;
    selectedTextValue = field ? selectedText(field) : pageSelection;
    updateMenuState();
    if (menu.open) menu.close();
    menu.style.position = "fixed";
    menu.showModal();
    menu.style.left = `${Math.max(8, Math.min(event.clientX, window.innerWidth - menu.offsetWidth - 8))}px`;
    menu.style.top = `${Math.max(8, Math.min(event.clientY, window.innerHeight - menu.offsetHeight - 8))}px`;
  });

  menu.addEventListener("click", async (event) => {
    if (event.target === menu) {
      hideMenu();
      return;
    }
    const button = event.target.closest("button");
    if (!button || button.disabled || !activeField) return;
    const command = button.dataset.command;
    if (command === "emoji") {
      toast("Use Win+. to open the Windows emoji picker.");
    } else if (command === "paste") {
      try {
        const text = await readClipboard();
        if (!text) {
          toast(t("clipboard.empty"));
          hideMenu();
          return;
        }
        const start = activeField.selectionStart ?? activeField.value.length;
        const end = activeField.selectionEnd ?? start;
        activeField.setRangeText(text, start, end, "end");
        activeField.dispatchEvent(new Event("input", { bubbles: true }));
      } catch (error) {
        toast(error.message || t("clipboard.failed"));
      }
    } else if (command === "copy" || command === "cut") {
      const text = activeField ? selectedText(activeField) : selectedTextValue;
      if (text) {
        try {
          await copyText(text);
          if (command === "cut" && activeField) deleteSelectedText(activeField);
        } catch (error) {
          toast(error.message || t("clipboard.failed"));
        }
      }
    } else {
      document.execCommand(command === "select-all" ? "selectAll" : command);
    }
    hideMenu();
    if (activeField) activeField.focus();
  });

  document.addEventListener("pointerdown", (event) => {
    if (menu.open && !menu.contains(event.target)) hideMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") hideMenu();
  });
}

let currentLang = LANGS.includes(readStorage(LANG_KEY)) ? readStorage(LANG_KEY) : "en";

function t(key, values) {
  const table = STRINGS[currentLang] || STRINGS.en || {};
  let text = table[key];
  if (text == null) text = (STRINGS.en || {})[key];
  if (text == null) return key;
  if (!values) return text;
  return text.replace(/\{(\w+)\}/g, (match, name) =>
    Object.prototype.hasOwnProperty.call(values, name) ? String(values[name]) : match,
  );
}

function guideSteps() {
  return GUIDES[currentLang] || GUIDES.en || [];
}

function linkCount(count) {
  return count === 1 ? t("link.one") : t("link.many", { count });
}

const el = {
  textarea: document.getElementById("urls"),
  add: document.getElementById("add"),
  urlCount: document.getElementById("url-count"),
  jobs: document.getElementById("jobs"),
  empty: document.getElementById("empty"),
  queueCount: document.getElementById("queue-count"),
  clear: document.getElementById("clear"),
  runtime: document.getElementById("runtime"),
  runtimeText: document.getElementById("runtime-text"),
  zoomOut: document.getElementById("zoom-out"),
  zoomIn: document.getElementById("zoom-in"),
  zoomValue: document.getElementById("zoom-value"),
  footPath: document.getElementById("output-path"),
  toast: document.getElementById("toast"),
  settings: document.getElementById("settings"),
  form: document.getElementById("settings-form"),
  openSettings: document.getElementById("open-settings"),
  closeSettings: document.getElementById("close-settings"),
  cancelSettings: document.getElementById("cancel-settings"),
  token: document.getElementById("set-token"),
  chat: document.getElementById("set-chat"),
  bitrate: document.getElementById("set-bitrate"),
  output: document.getElementById("set-output"),
  downloadDetails: document.getElementById("set-download-details"),
  toggleToken: document.getElementById("toggle-token"),
  testTelegram: document.getElementById("test-telegram"),
  telegramStatus: document.getElementById("telegram-status"),
  findChat: document.getElementById("find-chat"),
  chatOptions: document.getElementById("chat-options"),
  languages: Array.from(document.querySelectorAll('input[name="set-language"]')),
  themes: Array.from(document.querySelectorAll('input[name="set-theme"]')),

  notesList: document.getElementById("notes-list"),
  notesEmpty: document.getElementById("notes-empty"),
  notesCount: document.getElementById("notes-count"),
  notesClear: document.getElementById("notes-clear"),
  noteForm: document.getElementById("note-form"),
  noteTitle: document.getElementById("note-title"),
  noteText: document.getElementById("note-text"),
  noteAdd: document.getElementById("note-add"),

  notice: document.getElementById("ytdlp-notice"),
  noticeText: document.getElementById("ytdlp-notice-text"),
  noticeDismiss: document.getElementById("ytdlp-dismiss"),
  ytdlpUpdate: document.getElementById("ytdlp-update"),
  ytdlpVersion: document.getElementById("ytdlp-version"),
  ytdlpOrigin: document.getElementById("ytdlp-origin"),
  ytdlpCheck: document.getElementById("ytdlp-check"),
  ytdlpStatus: document.getElementById("ytdlp-status"),

  guide: document.getElementById("guide"),
  guideRail: document.getElementById("guide-rail"),
  guideStep: document.getElementById("guide-step"),
  guideTitle: document.getElementById("guide-title"),
  guideBody: document.getElementById("guide-body"),
  guideClose: document.getElementById("guide-close"),
  guideSkip: document.getElementById("guide-skip"),
  guideBack: document.getElementById("guide-back"),
  guideNext: document.getElementById("guide-next"),
  openGuide: document.getElementById("open-guide"),
};

const state = {
  settings: {},
  jobs: [],
  notes: [],
  ytdlp: { version: "", latest: "", outdated: false, source: "", checked_at: 0, error: "" },
  rows: new Map(),
  notesSignature: "",
  toastTimer: 0,
  notesClearTimer: 0,
  guideIndex: 0,
  guideProgress: 0,
  guideAsked: false,
  settingsLoaded: false,
  prefsLoaded: false,
  refreshing: false,
  runtime: { ok: true, message: "" },
};

/* ── plumbing ─────────────────────────────────────────────────────────── */

async function api(path, body) {
  const options = body === undefined
    ? {}
    : {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      };
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || t("error.http", { status: response.status }));
  return data;
}

function toast(message) {
  el.toast.textContent = message;
  el.toast.classList.add("is-on");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => el.toast.classList.remove("is-on"), 4200);
}

function normalizeUrl(raw) {
  const text = (raw || "").trim();
  return /^https?:\/\//i.test(text) ? text : `https://${text.replace(/^\/+/, "")}`;
}

function formatDuration(seconds) {
  const total = Math.max(0, Math.round(seconds || 0));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  const pad = (value) => String(value).padStart(2, "0");
  return hours ? `${hours}:${pad(minutes)}:${pad(secs)}` : `${minutes}:${pad(secs)}`;
}

function formatSize(mb) {
  if (!mb) return "";
  return `${mb < 10 ? mb.toFixed(1) : Math.round(mb)} MB`;
}

function shortenPath(path) {
  if (!path) return t("folder");
  return path.length > 54 ? `…${path.slice(-52)}` : path;
}

/* ── language and theme ───────────────────────────────────────────────── */

function applyTheme(raw) {
  const theme = THEMES.includes(raw) ? raw : "dark";
  document.documentElement.dataset.theme = theme;
  const meta = document.querySelector('meta[name="color-scheme"]');
  if (meta) meta.content = theme === "system" ? "light dark" : theme;
  writeStorage(THEME_KEY, theme);
  for (const input of el.themes) input.checked = input.value === theme;
}

function activeTheme() {
  return document.documentElement.dataset.theme || "dark";
}

function applyLanguage(raw, { persist = true } = {}) {
  currentLang = LANGS.includes(raw) ? raw : "en";
  state.language = currentLang;
  document.documentElement.lang = currentLang;
  if (persist) writeStorage(LANG_KEY, currentLang);

  for (const node of document.querySelectorAll("[data-i18n]")) {
    node.textContent = t(node.dataset.i18n);
  }
  for (const node of document.querySelectorAll("[data-i18n-placeholder]")) {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  }
  for (const node of document.querySelectorAll("[data-i18n-aria-label]")) {
    node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel));
  }

  for (const input of el.languages) input.checked = input.value === currentLang;
  el.toggleToken.textContent =
    el.token.type === "password" ? t("settings.show") : t("settings.hide");
  if (!el.findChat.disabled) el.findChat.textContent = t("settings.chat.find");
  if (!el.ytdlpCheck.disabled) el.ytdlpCheck.textContent = t("settings.ytdlp.check");
  if (!el.ytdlpUpdate.disabled) el.ytdlpUpdate.textContent = t("notice.update");

  buildGuideRail();
  showStep(state.guideIndex);

  if (state.jobs.length || state.rows.size) {
    el.jobs.replaceChildren();
    state.rows.clear();
    renderJobs(state.jobs);
  }
  state.notesSignature = "";
  renderNotes(state.notes);
  renderYtdlp(state.ytdlp);
  setRuntime(state.runtime.ok, state.runtime.message);
  el.footPath.value = state.settings.output_dir || "";
  el.footPath.title = t("foot.open", { path: state.settings.output_dir || "" });
  if (!el.chatOptions.hidden) {
    el.chatOptions.hidden = true;
    el.chatOptions.replaceChildren();
  }
  updateComposer();
}

async function savePreference(patch) {
  try {
    const data = await api("/api/settings", patch);
    state.settings = data.settings;
  } catch (error) {
    toast(error.message);
  }
}

/* ── clipboard ────────────────────────────────────────────────────────── */

async function readClipboard() {
  /* The local server reads the real OS clipboard and is the reliable path on
     Windows (and in WebView2, where the browser API is often blocked). The
     browser API stays as a fallback for systems the server cannot read. */
  let serverText = "";
  let serverError = null;
  try {
    const data = await api("/api/clipboard/read", {});
    serverText = data.text || "";
  } catch (error) {
    serverError = error;
  }
  if (serverText && serverText.trim()) return serverText;

  try {
    if (navigator.clipboard && window.isSecureContext) {
      const browserText = await navigator.clipboard.readText();
      if (browserText && browserText.trim()) return browserText;
    }
  } catch (error) {
    /* no browser clipboard either: fall through to the error below */
  }

  if (serverError) throw serverError;
  return serverText;
}

async function pasteInto(input, button) {
  button.disabled = true;
  try {
    const text = String(await readClipboard()).trim();
    if (!text) {
      toast(t("clipboard.empty"));
      return;
    }
    input.value = text.split(/\r?\n/)[0].trim();
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.focus();
    input.select();
    toast(t("clipboard.pasted"));
  } catch (error) {
    toast(error.message || t("clipboard.failed"));
  } finally {
    button.disabled = false;
  }
}

async function copyText(text) {
  try {
    await api("/api/clipboard/write", { text });
  } catch (error) {
    if (!navigator.clipboard || !window.isSecureContext) throw error;
    await navigator.clipboard.writeText(text);
  }
  toast(t("clipboard.copied"));
}

function selectedText(field) {
  if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement) {
    return field.value.slice(field.selectionStart ?? 0, field.selectionEnd ?? 0);
  }
  const selection = window.getSelection();
  return selection ? selection.toString() : "";
}

function deleteSelectedText(field) {
  if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement) {
    const start = field.selectionStart ?? 0;
    const end = field.selectionEnd ?? start;
    field.setRangeText("", start, end, "start");
    field.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    document.execCommand("delete");
  }
}

document.addEventListener("copy", (event) => {
  const field = event.target instanceof Element
    ? event.target.closest("input, textarea, [contenteditable='true']")
    : null;
  const text = field ? selectedText(field) : "";
  if (!text) return;
  event.preventDefault();
  void copyText(text).catch((error) => toast(error.message || t("clipboard.failed")));
});

document.addEventListener("cut", (event) => {
  const field = event.target instanceof Element
    ? event.target.closest("input, textarea, [contenteditable='true']")
    : null;
  const text = field ? selectedText(field) : "";
  if (!text) return;
  event.preventDefault();
  void copyText(text)
    .then(() => deleteSelectedText(field))
    .catch((error) => toast(error.message || t("clipboard.failed")));
});

/* ── composer ─────────────────────────────────────────────────────────── */

function links() {
  const seen = new Set();
  for (const piece of el.textarea.value.split(/[\s,;]+/)) {
    const url = piece.trim();
    if (url) seen.add(url);
  }
  return [...seen];
}

function validLinks() {
  return links().filter((url) => YOUTUBE.test(normalizeUrl(url)));
}

function updateComposer() {
  const valid = validLinks();
  el.urlCount.textContent = linkCount(valid.length);
  el.add.disabled = valid.length === 0;
}

async function submit() {
  const urls = links();
  if (!urls.length) {
    el.textarea.focus();
    toast(t("toast.link.empty"));
    return;
  }

  el.add.disabled = true;
  try {
    const result = await api("/api/jobs", { urls });
    if (result.added) {
      el.textarea.value = "";
      const ignored = result.rejected.length;
      toast(
        ignored
          ? t("toast.ignored", { added: result.added, ignored })
          : t("toast.queued", { count: result.added }),
      );
    } else {
      toast(t("toast.invalid"));
    }
    updateComposer();
    await refresh();
  } catch (error) {
    toast(error.message);
    el.add.disabled = false;
  }
}

/* ── queue rendering ──────────────────────────────────────────────────── */

function stateLabel(job) {
  const percent = job.progress == null ? null : Math.round(job.progress);
  switch (job.status) {
    case "queued": return t("job.queued");
    case "downloading":
      return percent == null ? t("job.downloading") : t("job.downloading.pct", { percent });
    case "converting": return t("job.converting");
    case "sending": return t("job.sending");
    case "done": return t("job.done");
    case "error": return t("job.error");
    default: return job.status;
  }
}

function makeRow(id) {
  const row = document.createElement("li");
  row.className = "job";
  row.dataset.id = id;
  row.innerHTML = `
    <span class="job__mark" aria-hidden="true"></span>
    <div class="job__main">
      <p class="job__title"></p>
      <p class="job__meta"></p>
      <p class="job__details" hidden></p>
      <p class="job__note" hidden></p>
    </div>
    <div class="job__actions"></div>
    <span class="job__bar" aria-hidden="true"><i></i></span>`;
  return row;
}

function setMark(row, job) {
  const kind = ACTIVE.has(job.status)
    ? "busy"
    : job.status === "done"
      ? "done"
      : job.status === "error"
        ? "error"
        : "queued";

  const mark = row.querySelector(".job__mark");
  if (mark.dataset.kind === kind) return;
  mark.dataset.kind = kind;
  mark.replaceChildren();

  if (kind === "busy") {
    const bars = document.createElement("span");
    bars.className = "bars";
    for (let index = 0; index < 3; index += 1) bars.append(document.createElement("i"));
    mark.append(bars);
    return;
  }

  const dot = document.createElement("i");
  dot.className = kind === "done" ? "dotdone" : kind === "error" ? "doterr" : "dotdot";
  mark.append(dot);
}

function setMeta(row, job) {
  const bits = [{ text: stateLabel(job) }];
  if (job.duration) bits.push({ text: formatDuration(job.duration), mono: true });
  if (job.size_mb) bits.push({ text: formatSize(job.size_mb), mono: true });
  if (job.telegram === "sent") bits.push({ text: t("job.sent") });
  if (job.telegram === "too_big") bits.push({ text: t("job.too_big") });
  if (job.telegram === "failed") bits.push({ text: t("job.telegram_failed") });

  const key = bits.map((bit) => bit.text).join("|");
  const meta = row.querySelector(".job__meta");
  if (meta.dataset.key === key) return;
  meta.dataset.key = key;

  meta.replaceChildren();
  bits.forEach((bit, index) => {
    if (index) {
      const separator = document.createElement("span");
      separator.className = "job__sep";
      separator.textContent = "·";
      meta.append(separator);
    }
    const span = document.createElement("span");
    span.textContent = bit.text;
    if (bit.mono) span.className = "job__num";
    meta.append(span);
  });
}

function setActions(row, job) {
  const key = `${job.status}|${job.file}|${job.telegram}`;
  if (row.dataset.actions === key) return;
  row.dataset.actions = key;

  const box = row.querySelector(".job__actions");
  box.replaceChildren();

  if (job.status === "error") {
    box.append(actionButton(t("job.retry"), () => post("/api/jobs/retry", { id: job.id })));
    return;
  }
  if (job.status === "done" && job.file) {
    box.append(actionButton(t("job.open"), () => post("/api/jobs/reveal", { id: job.id })));
    box.append(actionButton(t("job.play"), () => post("/api/jobs/play", { id: job.id })));
    if (job.telegram !== "sent") {
      box.append(actionButton(t("job.send_again"), () => post("/api/jobs/send-again", { id: job.id })));
    }
    box.append(actionButton(t("job.delete"), () => post("/api/jobs/delete", { id: job.id })));
  }
}

function actionButton(label, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "btnlink";
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

async function post(path, body) {
  try {
    const data = await api(path, body);
    if (data.jobs) renderJobs(data.jobs);
    await refresh();
    return data;
  } catch (error) {
    toast(error.message);
    return null;
  }
}

function patchRow(row, job) {
  row.dataset.status = job.status;

  const title = row.querySelector(".job__title");
  const label = job.title || job.url;
  if (title.textContent !== label) {
    title.textContent = label;
    title.title = label;
  }

  setMark(row, job);
  setMeta(row, job);
  setActions(row, job);

  const details = row.querySelector(".job__details");
  const detailsText = job.status === "done" ? downloadDetails(job) : "";
  details.textContent = detailsText;
  details.hidden = !detailsText;

  const note = row.querySelector(".job__note");
  const text = job.status === "error" ? job.error : job.note;
  note.textContent = text || "";
  note.hidden = !text;

  const percent = job.status === "done" ? 100 : (job.progress ?? 0);
  row.style.setProperty("--p", String(percent / 100));
}

function renderJobs(jobs) {
  const seen = new Set();

  for (const job of jobs) {
    seen.add(job.id);
    let row = state.rows.get(job.id);
    if (!row) {
      row = makeRow(job.id);
      state.rows.set(job.id, row);
      el.jobs.append(row);
      row.classList.add("is-new");
      row.addEventListener("animationend", () => row.classList.remove("is-new"), { once: true });
    }
    patchRow(row, job);
  }

  for (const [id, row] of state.rows) {
    if (!seen.has(id)) {
      row.remove();
      state.rows.delete(id);
    }
  }

  el.empty.hidden = jobs.length > 0;
  el.queueCount.textContent = String(jobs.length);
  el.clear.disabled = !jobs.some((job) => job.status === "done" || job.status === "error");
}

/* ── appunti ──────────────────────────────────────────────────────────── */

function noteDate(seconds) {
  if (!seconds) return "";
  return new Intl.DateTimeFormat(LOCALES[currentLang] || "it-IT", {
    day: "numeric",
    month: "short",
  }).format(new Date(seconds * 1000));
}

function renderNotes(notes) {
  const list = Array.isArray(notes) ? notes : [];
  const signature = list.map((note) => `${note.id}|${note.created}|${note.text}`).join("\u0000");
  if (signature === state.notesSignature) return;
  state.notesSignature = signature;

  el.notesList.replaceChildren();
  for (const note of list) {
    const item = document.createElement("li");
    item.className = "note";
    item.dataset.id = note.id;

    const content = document.createElement("div");
    content.className = "note__content";
    const title = document.createElement("p");
    title.className = "note__title";
    title.textContent = note.title || note.text;
    content.append(title);
    if (note.body) {
      const body = document.createElement("p");
      body.className = "note__text";
      body.textContent = note.body;
      content.append(body);
    }

    const date = document.createElement("span");
    date.className = "note__date";
    date.textContent = noteDate(note.created);

    const actions = document.createElement("div");
    actions.className = "note__actions";
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "btnlink";
    copy.textContent = t("notes.copy");
    copy.setAttribute("aria-label", t("notes.copy.aria", { text: note.title.slice(0, 80) }));
    copy.addEventListener("click", () => copyText(note.text));
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "btnlink";
    edit.textContent = t("notes.edit");
    edit.addEventListener("click", () => startNoteEdit(item, note));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "btnlink";
    remove.textContent = t("notes.delete");
    remove.setAttribute("aria-label", t("notes.delete.aria", { text: note.title.slice(0, 80) }));
    remove.addEventListener("click", () => deleteNote(note.id));
    actions.append(copy, edit, remove);

    item.append(content, date, actions);
    el.notesList.append(item);
  }

  el.notesEmpty.hidden = list.length > 0;
  el.notesCount.textContent = String(list.length);
  el.notesClear.disabled = list.length === 0;
  if (!list.length) resetNotesClear();
}

function startNoteEdit(item, note) {
  const content = item.querySelector(".note__content");
  content.replaceChildren();
  const title = document.createElement("input");
  title.className = "note__edit-title";
  title.value = note.title || note.text;
  title.maxLength = 240;
  const body = document.createElement("textarea");
  body.className = "note__edit-body";
  body.rows = 3;
  body.value = note.body || "";
  const actions = document.createElement("div");
  actions.className = "note__edit-actions";
  const save = document.createElement("button");
  save.type = "button";
  save.className = "btnlink";
  save.textContent = t("notes.save");
  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "btnlink";
  cancel.textContent = t("notes.cancel");
  cancel.addEventListener("click", () => renderNotes(state.notes));
  save.addEventListener("click", async () => {
    save.disabled = true;
    try {
      const data = await api("/api/notes/update", {
        id: note.id,
        title: title.value,
        body: body.value,
      });
      state.notes = data.notes;
      renderNotes(data.notes);
      toast(t("settings.saved"));
    } catch (error) {
      toast(error.message);
      save.disabled = false;
    }
  });
  actions.append(save, cancel);
  content.append(title, body, actions);
  title.focus();
}

async function addNote(event) {
  if (event) event.preventDefault();
  const title = el.noteTitle.value;
  const body = el.noteText.value;
  if (!title.trim()) {
    el.noteTitle.focus();
    return;
  }

  el.noteAdd.disabled = true;
  try {
    const data = await api("/api/notes", { title, body });
    el.noteTitle.value = "";
    el.noteText.value = "";
    renderNotes(data.notes);
    toast(
      data.added > 1
        ? t("toast.notes.added", { count: data.added })
        : t("toast.note.added"),
    );
    el.noteText.focus();
  } catch (error) {
    toast(error.message);
  } finally {
    el.noteAdd.disabled = false;
  }
}

async function deleteNote(id) {
  try {
    const data = await api("/api/notes/delete", { id });
    renderNotes(data.notes);
  } catch (error) {
    toast(error.message);
  }
}

function resetNotesClear() {
  clearTimeout(state.notesClearTimer);
  state.notesClearTimer = 0;
  el.notesClear.textContent = t("notes.clear");
  delete el.notesClear.dataset.armed;
}

async function clearNotes() {
  if (!el.notesClear.dataset.armed) {
    el.notesClear.dataset.armed = "1";
    el.notesClear.textContent = t("notes.clear.confirm");
    state.notesClearTimer = setTimeout(resetNotesClear, 3600);
    return;
  }

  resetNotesClear();
  try {
    const data = await api("/api/notes/clear", {});
    renderNotes(data.notes);
    toast(t("toast.notes.cleared"));
  } catch (error) {
    toast(error.message);
  }
}

/* ── yt-dlp ───────────────────────────────────────────────────────────── */

const DISMISS_KEY = "ytdlp-dismissed";
let dismissedUpdate = localStorage.getItem(DISMISS_KEY) || "";

function renderYtdlp(info) {
  if (!info) return;
  state.ytdlp = info;

  el.ytdlpVersion.textContent = info.version || t("ytdlp.missing");
  el.ytdlpOrigin.textContent =
    info.source === "staged" ? t("ytdlp.source.staged") :
    info.source === "bundled" ? t("ytdlp.source.bundled") :
    info.source === "installed" ? t("ytdlp.source.installed") : "";
  el.ytdlpOrigin.title = info.location || "";

  const show = Boolean(info.outdated) && dismissedUpdate !== info.latest;
  el.notice.hidden = !show;
  if (show) {
    el.noticeText.textContent = t("notice.text", {
      current: info.version || "?",
      latest: info.latest,
    });
  }

  if (info.error) {
    el.ytdlpStatus.textContent = info.error;
    el.ytdlpStatus.dataset.error = "1";
  } else if (info.checked_at) {
    el.ytdlpStatus.textContent = info.outdated
      ? t("ytdlp.status.available", { version: info.latest })
      : t("ytdlp.status.current");
    el.ytdlpStatus.dataset.error = "0";
  }
}

async function updateYtdlp() {
  el.ytdlpUpdate.disabled = true;
  el.ytdlpUpdate.textContent = t("ytdlp.updating");
  try {
    const data = await api("/api/ytdlp/update", {});
    dismissedUpdate = "";
    localStorage.removeItem(DISMISS_KEY);
    renderYtdlp(data.ytdlp);
    if (data.ytdlp.changed) {
      toast(
        data.ytdlp.applied
          ? t("ytdlp.toast.updated", { version: data.ytdlp.version })
          : t("ytdlp.toast.staged", { version: data.ytdlp.version }),
      );
    } else {
      toast(t("ytdlp.toast.already", { version: data.ytdlp.version }));
    }
    await refresh();
  } catch (error) {
    toast(error.message);
  } finally {
    el.ytdlpUpdate.disabled = false;
    el.ytdlpUpdate.textContent = t("notice.update");
  }
}

async function checkYtdlp() {
  el.ytdlpCheck.disabled = true;
  el.ytdlpCheck.textContent = t("ytdlp.checking");
  el.ytdlpStatus.textContent = "";
  try {
    const data = await api("/api/ytdlp/check", {});
    renderYtdlp(data.ytdlp);
    toast(data.ytdlp.outdated
      ? t("ytdlp.toast.available", { version: data.ytdlp.latest })
      : t("ytdlp.toast.current", { version: data.ytdlp.version }));
  } catch (error) {
    el.ytdlpStatus.dataset.error = "1";
    el.ytdlpStatus.textContent = error.message;
  } finally {
    el.ytdlpCheck.disabled = false;
    el.ytdlpCheck.textContent = t("settings.ytdlp.check");
  }
}

/* ── the walkthrough ──────────────────────────────────────────────────── */

function guideBlock(block) {
  if (block.type === "welcome") {
    const node = document.createElement("div");
    node.className = "welcome-panel";
    node.innerHTML = `
      <span class="welcome-panel__mark" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>
      <strong class="welcome-panel__name"></strong>
    `;
    node.querySelector(".welcome-panel__name").textContent = block.name;
    return node;
  }
  if (block.type === "p") {
    const node = document.createElement("p");
    node.textContent = block.text;
    return node;
  }
  if (block.type === "h") {
    const node = document.createElement("p");
    node.className = "guide__h";
    node.textContent = block.text;
    return node;
  }
  if (block.type === "note") {
    const node = document.createElement("p");
    node.className = "guide__note";
    node.textContent = block.text;
    return node;
  }
  if (block.type === "code") {
    const node = document.createElement("pre");
    node.className = "guide__code";
    node.textContent = block.text;
    return node;
  }
  if (block.type === "steps") {
    const list = document.createElement("ol");
    list.className = "guide-list";
    for (const text of block.items) {
      const item = document.createElement("li");
      item.textContent = text;
      list.append(item);
    }
    return list;
  }
  return document.createTextNode("");
}

function buildGuideRail() {
  el.guideRail.replaceChildren();
  guideSteps().forEach((step, index) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";

    const number = document.createElement("span");
    number.className = "guide__num";
    number.textContent = String(index);

    const label = document.createElement("span");
    label.textContent = step.label;

    button.append(number, label);
    button.addEventListener("click", () => showStep(index));
    item.append(button);
    el.guideRail.append(item);
  });
}

function showStep(index) {
  const steps = guideSteps();
  const total = steps.length;
  state.guideIndex = Math.max(0, Math.min(total - 1, index));
  state.guideProgress = state.guideIndex;
  const step = steps[state.guideIndex];
  if (!step) return;

  el.guideStep.textContent = t("guide.step", {
    current: state.guideIndex,
    total,
  });
  el.guideTitle.textContent = step.title;
  el.guideBody.replaceChildren(...step.blocks.map(guideBlock));
  el.guideBody.scrollTop = 0;

  [...el.guideRail.querySelectorAll("button")].forEach((button, position) => {
    if (position === state.guideIndex) button.setAttribute("aria-current", "step");
    else button.removeAttribute("aria-current");
    if (position < state.guideProgress) button.dataset.complete = "1";
    else delete button.dataset.complete;
  });

  el.guideBack.disabled = false;
  el.guideNext.textContent =
    state.guideIndex === total - 1 ? t("guide.done") : t("guide.next");

  if (el.guide.open) el.guideTitle.focus({ preventScroll: true });
}

function openGuide(start = 0) {
  buildGuideRail();
  showStep(start);
  if (!el.guide.open) el.guide.showModal();
  el.guideTitle.focus({ preventScroll: true });
}

function closeGuide() {
  state.guideIndex = 0;
  state.guideProgress = 0;
  if (el.guide.open) el.guide.close();
  buildGuideRail();
}

async function markGuideSeen() {
  if (state.settings.seen_guide) return;
  state.settings.seen_guide = true;
  try {
    await api("/api/settings", { seen_guide: true });
  } catch (error) {
    // Not worth a toast: the guide will simply open again next time.
  }
}

/* ── server state ─────────────────────────────────────────────────────── */

function setRuntime(ok, message) {
  state.runtime = { ok, message: message || "" };
  const text = message || (ok ? t("runtime.ok") : t("runtime.missing"));
  if (el.runtimeText.textContent !== text) el.runtimeText.textContent = text;
  el.runtime.dataset.ok = ok ? "1" : "0";
  el.runtime.title = ok
    ? t("runtime.ok.title")
    : message || t("runtime.missing.title");
}

async function refresh() {
  if (state.refreshing) return;
  state.refreshing = true;
  try {
    const data = await api("/api/state");
    state.settings = data.settings;
    state.jobs = data.jobs || [];
    state.notes = data.notes || [];
    state.settingsLoaded = true;

    if (!state.prefsLoaded) {
      applyLanguage(state.settings.language || "it");
      applyTheme(state.settings.theme || "dark");
      state.prefsLoaded = true;
    }

    setRuntime(data.ffmpeg);
    renderJobs(state.jobs);
    renderNotes(state.notes);
    renderYtdlp(data.ytdlp);
    el.footPath.value = data.settings.output_dir || "";
    el.footPath.title = t("foot.open", { path: data.settings.output_dir || "" });
  } catch (error) {
    setRuntime(false, t("runtime.offline"));
  } finally {
    state.refreshing = false;
  }
}

/* ── settings ─────────────────────────────────────────────────────────── */

function openSettings() {
  const settings = state.settings || {};
  el.token.value = settings.token || "";
  el.chat.value = settings.chat_id || "";
  el.bitrate.value = settings.bitrate || "192";
  el.output.value = settings.output_dir || "";
  el.downloadDetails.value = settings.download_details || "";
  el.telegramStatus.textContent = "";
  el.telegramStatus.dataset.error = "0";
  el.chatOptions.hidden = true;
  el.chatOptions.replaceChildren();
  el.findChat.disabled = false;
  el.findChat.textContent = t("settings.chat.find");
  el.ytdlpStatus.textContent = "";
  el.toggleToken.textContent =
    el.token.type === "password" ? t("settings.show") : t("settings.hide");
  for (const input of el.languages) input.checked = input.value === currentLang;
  for (const input of el.themes) input.checked = input.value === activeTheme();
  renderYtdlp(state.ytdlp);
  el.settings.showModal();
}

async function saveSettings(event) {
  event.preventDefault();
  const submitButton = el.form.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  try {
    const data = await api("/api/settings", {
      token: el.token.value.trim(),
      chat_id: el.chat.value.trim(),
      bitrate: el.bitrate.value,
      output_dir: el.output.value.trim(),
      download_details: el.downloadDetails.value,
      language: currentLang,
      theme: activeTheme(),
      seen_guide: Boolean(state.settings.seen_guide),
    });
    state.settings = data.settings;
    applyLanguage(data.settings.language || currentLang);
    applyTheme(data.settings.theme || activeTheme());
    el.settings.close();
    toast(t("settings.saved"));
    await refresh();
  } catch (error) {
    toast(error.message);
  } finally {
    submitButton.disabled = false;
  }
}

async function testTelegram() {
  el.telegramStatus.dataset.error = "0";
  el.telegramStatus.textContent = t("settings.testing");
  el.testTelegram.disabled = true;
  try {
    const data = await api("/api/telegram/test", {
      token: el.token.value.trim(),
      chat_id: el.chat.value.trim(),
    });
    el.telegramStatus.textContent = t("settings.connected", { bot: data.bot });
  } catch (error) {
    el.telegramStatus.dataset.error = "1";
    el.telegramStatus.textContent = error.message;
  } finally {
    el.testTelegram.disabled = false;
  }
}

function renderChatOptions(chats) {
  el.chatOptions.replaceChildren();

  const label = document.createElement("p");
  label.className = "chat-options__label";
  label.textContent =
    chats.length > 1 ? t("settings.chat.choose") : t("settings.chat.one");
  el.chatOptions.append(label);

  for (const chat of chats.slice(0, 6)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chat-option";

    const name = document.createElement("span");
    name.className = "chat-option__name";
    name.textContent = chat.name;

    const id = document.createElement("span");
    id.className = "chat-option__id";
    id.textContent = chat.id;

    button.append(name, id);
    button.addEventListener("click", () => {
      el.chat.value = chat.id;
      el.chatOptions.hidden = true;
      el.chatOptions.replaceChildren();
      toast(t("settings.chat.chosen", { name: chat.name }));
    });
    el.chatOptions.append(button);
  }

  el.chatOptions.hidden = false;
}

async function findChat() {
  const token = el.token.value.trim();
  if (!token) {
    toast(t("toast.token.first"));
    el.token.focus();
    return;
  }

  el.findChat.disabled = true;
  el.findChat.textContent = t("settings.chat.searching");
  el.chatOptions.hidden = true;
  el.chatOptions.replaceChildren();

  try {
    const data = await api("/api/telegram/chats", { token });
    const chats = data.chats || [];
    if (chats.length === 1) {
      el.chat.value = chats[0].id;
      toast(t("settings.chat.found", { name: chats[0].name }));
    } else {
      renderChatOptions(chats);
    }
  } catch (error) {
    toast(error.message);
  } finally {
    el.findChat.disabled = false;
    el.findChat.textContent = t("settings.chat.find");
  }
}

/* ── init ─────────────────────────────────────────────────────────────── */

el.textarea.addEventListener("input", updateComposer);
el.add.addEventListener("click", submit);
el.textarea.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    submit();
  }
});

el.clear.addEventListener("click", async () => {
  const data = await post("/api/jobs/clear", {});
  if (data) {
    toast(
      data.removed
        ? t("toast.rows.removed", { count: data.removed })
        : t("toast.nothing.removed"),
    );
  }
});

el.footPath.addEventListener("click", async () => {
  el.footPath.select();
});

el.footPath.addEventListener("change", async () => {
  const outputDir = el.footPath.value.trim();
  if (!outputDir) return;
  const data = await api("/api/settings", { output_dir: outputDir }).catch((error) => {
    toast(error.message);
    return null;
  });
  if (data?.settings) {
    state.settings = data.settings;
    el.footPath.value = data.settings.output_dir;
    el.footPath.title = t("foot.open", { path: data.settings.output_dir });
  }
});

el.openSettings.addEventListener("click", openSettings);
el.closeSettings.addEventListener("click", () => el.settings.close());
el.cancelSettings.addEventListener("click", () => el.settings.close());
el.form.addEventListener("submit", saveSettings);
el.testTelegram.addEventListener("click", testTelegram);
el.findChat.addEventListener("click", findChat);
el.toggleToken.addEventListener("click", () => {
  const hidden = el.token.type === "password";
  el.token.type = hidden ? "text" : "password";
  el.toggleToken.textContent = hidden ? t("settings.hide") : t("settings.show");
});

for (const input of el.languages) {
  input.addEventListener("change", () => {
    if (!input.checked) return;
    applyLanguage(input.value);
    savePreference({ language: input.value });
  });
}

for (const input of el.themes) {
  input.addEventListener("change", () => {
    if (!input.checked) return;
    applyTheme(input.value);
    savePreference({ theme: input.value });
  });
}

el.noteForm.addEventListener("submit", addNote);
el.noteText.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    addNote();
  }
});
el.noteTitle.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    addNote();
  }
});
el.notesClear.addEventListener("click", clearNotes);

el.noticeDismiss.addEventListener("click", () => {
  dismissedUpdate = state.ytdlp.latest || "";
  localStorage.setItem(DISMISS_KEY, dismissedUpdate);
  el.notice.hidden = true;
});
el.ytdlpUpdate.addEventListener("click", updateYtdlp);
el.ytdlpCheck.addEventListener("click", checkYtdlp);

el.openGuide.addEventListener("click", () => openGuide(0));
el.guideClose.addEventListener("click", closeGuide);
el.guideSkip.addEventListener("click", closeGuide);
el.guideBack.addEventListener("click", () => {
  if (state.guideIndex === 0) closeGuide();
  else showStep(state.guideIndex - 1);
});
el.guideNext.addEventListener("click", () => {
  if (state.guideIndex >= guideSteps().length - 1) closeGuide();
  else showStep(state.guideIndex + 1);
});
el.guide.addEventListener("close", markGuideSeen);
el.guide.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight") {
    event.preventDefault();
    showStep(state.guideIndex + 1);
  } else if (event.key === "ArrowLeft") {
    event.preventDefault();
    showStep(state.guideIndex - 1);
  }
});
el.guide.addEventListener("click", (event) => {
  if (event.target === el.guide) closeGuide();
});

applyTheme(readStorage(THEME_KEY) || "dark");
applyLanguage(currentLang);
applyZoom(readStorage(ZOOM_KEY) || 1);
setupTextContextMenu();
setupTextareaResizing();
setupStartupSplash();
updateComposer();
refresh();
setInterval(() => {
  if (!document.hidden) refresh();
}, 1200);

document.addEventListener("keydown", (event) => {
  if (!event.ctrlKey && !event.metaKey) return;
  if (event.key === "+" || event.key === "=") {
    event.preventDefault();
    changeZoom(ZOOM_STEP);
  } else if (event.key === "-" || event.key === "_") {
    event.preventDefault();
    changeZoom(-ZOOM_STEP);
  } else if (event.key === "0") {
    event.preventDefault();
    applyZoom(1);
  }
});

el.zoomOut.addEventListener("click", () => changeZoom(-ZOOM_STEP));
el.zoomIn.addEventListener("click", () => changeZoom(ZOOM_STEP));
el.zoomValue.addEventListener("click", () => applyZoom(1));

document.addEventListener("wheel", (event) => {
  if (!event.ctrlKey && !event.metaKey) return;
  event.preventDefault();
  changeZoom(event.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP);
}, { passive: false });
