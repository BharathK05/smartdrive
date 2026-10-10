// SmartDrive page behaviour: upload (picker + drag-and-drop), toasts, copy link, share panel.

const MAX_UPLOAD = 10 * 1024 * 1024;
const AI_TYPES = /\.(jpe?g|png|pdf|txt|md|csv)$/i;

function showToast(message, kind) {
  const toast = document.createElement("div");
  toast.className = `toast ${kind || ""}`;
  toast.setAttribute("role", kind === "error" ? "alert" : "status");
  toast.innerHTML = '<span></span><button class="icon-btn" type="button" aria-label="Dismiss">' +
    '<span class="icon" aria-hidden="true">close</span></button>';
  toast.firstElementChild.textContent = message;
  document.querySelector(".toasts")?.append(toast);
  wireToast(toast);
}

function wireToast(toast) {
  const close = () => toast.remove();
  toast.querySelector("button").addEventListener("click", close);
  setTimeout(close, toast.classList.contains("error") ? 9000 : 5000);
}
document.querySelectorAll(".toast").forEach(wireToast);

// Upload: choosing or dropping a file submits it straight away.
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
if (uploadForm && fileInput) {
  const panel = document.getElementById("upload-panel");
  const overlay = document.getElementById("drop-overlay");

  const startUpload = (file) => {
    if (!file) return;
    if (file.size > MAX_UPLOAD) {
      showToast(`${file.name} is too big. The limit is 10 MB.`, "error");
      fileInput.value = "";
      return;
    }
    document.getElementById("upload-name").textContent = file.name;
    document.getElementById("upload-sub").textContent =
      AI_TYPES.test(file.name) ? "Uploading and tagging with AI…" : "Uploading…";
    panel.hidden = false;
    uploadForm.submit();
  };
  fileInput.addEventListener("change", () => startUpload(fileInput.files[0]));

  const hasFiles = (event) => event.dataTransfer && event.dataTransfer.types.includes("Files");
  let dragDepth = 0;
  window.addEventListener("dragenter", (event) => {
    if (!hasFiles(event)) return;
    event.preventDefault();
    dragDepth += 1;
    overlay.hidden = false;
  });
  window.addEventListener("dragover", (event) => { if (hasFiles(event)) event.preventDefault(); });
  window.addEventListener("dragleave", () => {
    dragDepth -= 1;
    if (dragDepth <= 0) { dragDepth = 0; overlay.hidden = true; }
  });
  window.addEventListener("drop", (event) => {
    if (!hasFiles(event)) return;
    event.preventDefault();
    dragDepth = 0;
    overlay.hidden = true;
    fileInput.files = event.dataTransfer.files;
    startUpload(fileInput.files[0]);
  });
}

// Forms that need a confirmation (delete) or a busy label (sign in).
document.addEventListener("submit", (event) => {
  const form = event.target;
  if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
    event.preventDefault();
    return;
  }
  const button = form.querySelector("button[type=submit], button:not([type])");
  if (form.dataset.busy && button) {
    button.disabled = true;
    button.textContent = form.dataset.busy;
  }
});

// Copy a public link. navigator.clipboard needs HTTPS, so fall back to selecting the text.
document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) return;
  const field = document.getElementById(button.dataset.copy);
  try {
    await navigator.clipboard.writeText(field.value);
  } catch {
    field.select();
    document.execCommand("copy");
  }
  showToast("Link copied");
});

// File preview, like Google Drive: click a file name to view it, arrows move between files.
const viewer = document.getElementById("viewer");
if (viewer) {
  const rows = [...document.querySelectorAll("tr[data-file]")];
  const stage = viewer.querySelector(".viewer-stage");
  const tagBar = viewer.querySelector(".viewer-tags");
  const TEXT_LIMIT = 200000;
  let current = 0;

  const make = (tag, props) => Object.assign(document.createElement(tag), props);
  const typeIcon = (row) => row.querySelector(".type-icon").cloneNode(true);

  const noPreview = (row, message) => {
    const card = document.getElementById("no-preview").content.firstElementChild.cloneNode(true);
    card.querySelector(".no-preview-icon").append(typeIcon(row));
    if (message) card.querySelector("p").textContent = message;
    card.querySelector("a").href = row.dataset.download;
    return card;
  };

  const show = (index) => {
    current = (index + rows.length) % rows.length;
    const row = rows[current];
    const { name, kind, view, download } = row.dataset;
    const stillShowing = () => rows[current] === row && viewer.open;

    viewer.querySelector(".viewer-name").textContent = name;
    viewer.querySelector(".viewer-icon").replaceChildren(typeIcon(row));
    viewer.querySelector(".viewer-download").href = download;
    const tags = JSON.parse(row.dataset.tags || "[]");
    tagBar.hidden = tags.length === 0;
    tagBar.querySelector(".tags").replaceChildren(...tags.map((t) => make("span", { className: "tag", textContent: t })));

    if (kind === "image") {
      const img = make("img", { src: view, alt: name });
      img.onerror = () => stillShowing() && stage.replaceChildren(noPreview(row, "This image couldn’t be shown. Download it instead."));
      stage.replaceChildren(img);
    } else if (kind === "pdf") {
      stage.replaceChildren(make("iframe", { src: view, title: name }));
    } else if (kind === "text") {
      const pre = make("pre", { textContent: "Loading…" });
      stage.replaceChildren(pre);
      fetch(view)
        .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
        .then((text) => {
          if (!stillShowing()) return;
          pre.textContent = text.length > TEXT_LIMIT
            ? `${text.slice(0, TEXT_LIMIT)}\n\n… Download the file to see the rest.`
            : text || "(This file is empty.)";
        })
        .catch(() => stillShowing() && stage.replaceChildren(noPreview(row, "This file couldn’t be loaded. Download it instead.")));
    } else {
      stage.replaceChildren(noPreview(row));
    }
  };

  viewer.querySelectorAll(".viewer-nav").forEach((button) => {
    button.hidden = rows.length < 2;
    button.addEventListener("click", () => show(current + Number(button.dataset.step)));
  });
  viewer.querySelector("[data-close]").addEventListener("click", () => viewer.close());
  viewer.addEventListener("close", () => stage.replaceChildren());
  stage.addEventListener("click", (event) => { if (event.target === stage) viewer.close(); });
  viewer.addEventListener("keydown", (event) => {
    if (rows.length < 2) return;
    if (event.key === "ArrowLeft") show(current - 1);
    if (event.key === "ArrowRight") show(current + 1);
  });

  // Plain click opens the preview; Ctrl/Cmd/Shift-click keeps the normal download link.
  document.addEventListener("click", (event) => {
    const link = event.target.closest(".file-link");
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    viewer.showModal();
    show(rows.indexOf(link.closest("tr")));
  });
}

// After sharing, the server sends us back to #share-<id>: reopen that share panel.
const openPanel = location.hash.startsWith("#share-") && document.getElementById(location.hash.slice(1));
if (openPanel && openPanel.showPopover) {
  openPanel.showPopover();
  history.replaceState(null, "", location.pathname + location.search);
}
