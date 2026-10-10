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

// After sharing, the server sends us back to #share-<id>: reopen that share panel.
const openPanel = location.hash.startsWith("#share-") && document.getElementById(location.hash.slice(1));
if (openPanel && openPanel.showPopover) {
  openPanel.showPopover();
  history.replaceState(null, "", location.pathname + location.search);
}
