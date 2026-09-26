// Connects the form to the FastAPI backend, then renders the AI's
// structured JSON plan as a table (instead of raw text).

const API_URL = "http://127.0.0.1:8000"; // change this to your Render URL after deploying

const form = document.getElementById("plannerForm");
const submitBtn = document.getElementById("submitBtn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("errorBox");
const statRow = document.getElementById("statRow");
const summaryText = document.getElementById("summaryText");
const planBody = document.getElementById("planBody");
const downloadBtn = document.getElementById("downloadBtn");

let currentPlan = null; // kept in memory so the download button can use it
let currentMeta = null;

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const subjects = document.getElementById("subjects").value;
  const examDate = document.getElementById("examDate").value;
  const hours = document.getElementById("hours").value;
  const syllabus = document.getElementById("syllabus").value;

  loading.classList.remove("hidden");
  result.classList.add("hidden");
  errorBox.classList.add("hidden");
  submitBtn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/generate-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subjects: subjects,
        exam_date: examDate,
        hours_per_day: Number(hours),
        syllabus: syllabus,
      }),
    });

    if (!response.ok) throw new Error("Server error: " + response.status);

    const data = await response.json();
    currentPlan = data.plan;
    currentMeta = { subjects, examDate, hours };
    renderPlan(currentPlan, currentMeta);
    result.classList.remove("hidden");
  } catch (err) {
    showError(
      "Something went wrong: " + err.message +
      ". Make sure the backend server is running (uvicorn main:app --reload)."
    );
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
  }
});

function renderPlan(plan, meta) {
  const days = plan.days || [];
  const totalHours = days.reduce((sum, d) => sum + (Number(d.hours) || 0), 0);

  statRow.innerHTML = `
    <div class="stat"><span class="num">${days.length}</span><span class="label">Days planned</span></div>
    <div class="stat"><span class="num">${totalHours}</span><span class="label">Total study hours</span></div>
    <div class="stat"><span class="num">${meta.subjects.split(",").length}</span><span class="label">Subjects</span></div>
  `;

  summaryText.textContent = plan.summary || "";

  planBody.innerHTML = days.map(d => `
    <tr>
      <td class="col-day">${d.label || ("Day " + d.day)}</td>
      <td class="col-focus">${escapeHtml(d.focus || "")}</td>
      <td class="col-topics">${escapeHtml(d.topics || "")}</td>
      <td class="col-hours">${d.hours ?? ""}</td>
    </tr>
  `).join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

downloadBtn.addEventListener("click", () => {
  if (!currentPlan) return;

  const lines = [];
  lines.push("SMART AI STUDY PLANNER");
  lines.push("Subjects: " + currentMeta.subjects);
  lines.push("Exam date: " + currentMeta.examDate);
  lines.push("");
  lines.push(currentPlan.summary || "");
  lines.push("");
  lines.push("Day\tFocus\tTopics\tHours");

  (currentPlan.days || []).forEach(d => {
    lines.push(`${d.label || "Day " + d.day}\t${d.focus || ""}\t${d.topics || ""}\t${d.hours ?? ""}`);
  });

  const blob = new Blob([lines.join("\n")], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "study-plan.txt";
  a.click();
  URL.revokeObjectURL(url);
});
