const QUESTIONS = ["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"];

const $ = (sel) => document.querySelector(sel);

function setLoading(show) {
  $("#loading").classList.toggle("hidden", !show);
}

function showError(msg) {
  const el = $("#error");
  el.textContent = msg;
  el.classList.toggle("hidden", !msg);
}

function renderAnswerBlock(containerId, partKey, data, flags = {}) {
  const container = $(containerId);
  const parts = [
    { title: "Part-I", key: "part1" },
    { title: "Part-II", key: "part2" },
  ];
  container.innerHTML = parts
    .map(({ title, key }) => {
      const part = data[key] || {};
      const partFlags = data[`${key}_flags`] || flags[key] || {};
      const chips = QUESTIONS.map((q) => {
        const ans = part[q] ?? "-";
        const flag = partFlags[q];
        const extra = flag ? ` title="${flag}"` : "";
        return `<span class="q-chip"${extra}>${q}:${ans || "-"}</span>`;
      }).join("");
      return `<div class="answer-block"><h4>${title}</h4><div class="answer-row">${chips}</div></div>`;
    })
    .join("");
}

function statusClass(status) {
  return `status-${status}`;
}

function statusIcon(status) {
  return { correct: "OK", incorrect: "X", unattempted: "-", invalid: "!" }[status] || "?";
}

function renderResults(data) {
  const { answer_key, student_info, student_answers, grade_report } = data;

  $("#student-info").innerHTML = `
    <div class="info-item"><label>Name</label><span>${student_info.name}</span></div>
    <div class="info-item"><label>Registration #</label><span>${student_info.reg_no}</span></div>
    <div class="info-item"><label>Quiz</label><span>${answer_key.quiz_identifier}</span></div>
    <div class="info-item"><label>Set</label><span>${answer_key.set_identifier}</span></div>
  `;

  $("#set-badge").textContent = `Set ${answer_key.set_identifier}`;
  renderAnswerBlock("#answer-key", null, answer_key);
  renderAnswerBlock("#student-answers", null, student_answers);

  const gr = grade_report;
  $("#score-display").textContent = `${gr.total_marks} / ${gr.max_marks} (${gr.percentage}%) — Grade ${gr.letter_grade}`;
  $("#stats-row").innerHTML = `
    <span>Correct: <strong>${gr.correct}</strong></span>
    <span>Incorrect: <strong>${gr.incorrect}</strong></span>
    <span>Unattempted: <strong>${gr.unattempted}</strong></span>
    <span>Invalid: <strong>${gr.invalid}</strong></span>
  `;

  const tbody = $("#breakdown-table tbody");
  tbody.innerHTML = gr.per_question
    .map(
      (q) => `
    <tr>
      <td>${q.part}</td>
      <td>${q.question_id}</td>
      <td>${q.student_answer || "—"}</td>
      <td>${q.correct_answer}</td>
      <td class="${statusClass(q.status)}">${statusIcon(q.status)} ${q.status}${q.flag ? ` (${q.flag})` : ""}</td>
    </tr>`
    )
    .join("");

  $("#results").classList.remove("hidden");
  $("#batch-results").classList.add("hidden");
}

// Tabs
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const id = tab.dataset.tab;
    document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
    $(`#panel-${id}`).classList.remove("hidden");
    showError("");
  });
});

// Single file
let singleFile = null;
const fileSingle = $("#file-single");
const btnScan = $("#btn-scan");

fileSingle.addEventListener("change", () => {
  singleFile = fileSingle.files[0] || null;
  btnScan.disabled = !singleFile;
});

setupDrop($("#drop-single"), fileSingle, (f) => {
  singleFile = f;
  btnScan.disabled = !singleFile;
});

btnScan.addEventListener("click", async () => {
  if (!singleFile) return;
  showError("");
  $("#results").classList.add("hidden");
  setLoading(true);
  btnScan.disabled = true;

  const form = new FormData();
  form.append("file", singleFile);

  try {
    const res = await fetch("/api/scan", { method: "POST", body: form });
    const json = await res.json();
    if (!json.success) throw new Error(json.error || "Scan failed");
    renderResults(json.data);
  } catch (e) {
    showError(e.message);
  } finally {
    setLoading(false);
    btnScan.disabled = !singleFile;
  }
});

// Batch
let batchFiles = [];
const fileBatch = $("#file-batch");
const btnBatch = $("#btn-batch");

fileBatch.addEventListener("change", () => {
  batchFiles = [...fileBatch.files];
  btnBatch.disabled = batchFiles.length === 0;
});

setupDrop($("#drop-batch"), fileBatch, (files) => {
  batchFiles = Array.isArray(files) ? files : [files];
  btnBatch.disabled = batchFiles.length === 0;
});

btnBatch.addEventListener("click", async () => {
  if (!batchFiles.length) return;
  showError("");
  setLoading(true);
  btnBatch.disabled = true;

  const form = new FormData();
  batchFiles.forEach((f) => form.append("files", f));

  try {
    const res = await fetch("/api/batch", { method: "POST", body: form });
    const json = await res.json();
    if (!json.success) throw new Error(json.error || (json.errors && json.errors[0]?.error) || "Batch failed");

    $("#batch-summary").textContent = `Processed ${json.processed} sheet(s).${json.errors?.length ? ` ${json.errors.length} error(s).` : ""}`;
    $("#batch-download").href = json.download;
    $("#batch-results").classList.remove("hidden");
    $("#results").classList.add("hidden");
  } catch (e) {
    showError(e.message);
  } finally {
    setLoading(false);
    btnBatch.disabled = batchFiles.length === 0;
  }
});

function setupDrop(dropEl, inputEl, onFiles) {
  ["dragenter", "dragover"].forEach((ev) => {
    dropEl.addEventListener(ev, (e) => {
      e.preventDefault();
      dropEl.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach((ev) => {
    dropEl.addEventListener(ev, (e) => {
      e.preventDefault();
      dropEl.classList.remove("dragover");
    });
  });
  dropEl.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length) {
      if (inputEl.multiple) onFiles([...files]);
      else onFiles(files[0]);
    }
  });
}
