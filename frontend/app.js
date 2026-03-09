/* Aura Governance Platform — Frontend Logic */

const API = "";

// ─── Navigation ───────────────────────────────────────────────
document.querySelectorAll(".nav-link").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("page-" + btn.dataset.page).classList.add("active");

    // Lazy-load data when switching tabs
    if (btn.dataset.page === "catalogo") loadProjects();
    if (btn.dataset.page === "entrega") loadTools();
    if (btn.dataset.page === "relatorio") loadDashboard();
  });
});

// ─── Catálogo ─────────────────────────────────────────────────
async function loadProjects() {
  const search = document.getElementById("search-input").value.trim();
  const source = document.getElementById("source-filter").value;
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (source) params.set("initiative", source);

  const container = document.getElementById("projects-list");
  container.innerHTML = '<p class="text-gray-500 text-sm">Carregando...</p>';

  try {
    const res = await fetch(API + "/api/projects?" + params.toString());
    if (!res.ok) throw new Error("Erro ao carregar projetos");
    const projects = await res.json();

    if (projects.length === 0) {
      container.innerHTML = '<p class="text-gray-500 text-sm">Nenhum projeto encontrado.</p>';
      return;
    }

    container.innerHTML = projects.map((p) => `
      <div class="pulso-card pulso-card-hover p-4 cursor-pointer" onclick="showProject(${p.id})">
        <div class="flex items-start justify-between mb-2">
          <span class="font-semibold text-sm" style="color:#1f2937">${esc(p.title)}</span>
          <span class="text-xs px-2.5 py-0.5 rounded-full font-medium ml-3 flex-shrink-0 ${statusColor(p.status)}">${esc(p.status)}</span>
        </div>
        <p class="text-sm line-clamp-2 mb-3" style="color:#6b7280">${esc(p.description)}</p>
        <div class="flex flex-wrap gap-3 text-xs" style="color:#9ca3af">
          <span class="flex items-center gap-1">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/><path d="M6 3.5v2.5l1.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            ${esc(p.initiative)}
          </span>
          ${p.owner ? `<span>${esc(p.owner)}</span>` : ""}
          ${p.cost ? `<span style="color:#ca8a04">💰 ${esc(p.cost)}</span>` : ""}
          ${p.projected_return ? `<span style="color:#16a34a">📈 ${esc(p.projected_return)}</span>` : ""}
        </div>
      </div>
    `).join("");
  } catch (e) {
    container.innerHTML = '<p class="text-red-500 text-sm">Erro ao carregar projetos.</p>';
  }
}

async function showProject(id) {
  try {
    const res = await fetch(API + "/api/projects/" + id);
    if (!res.ok) throw new Error();
    const p = await res.json();

    document.getElementById("detail-name").textContent = p.title;
    document.getElementById("detail-body").innerHTML = `
      <div class="space-y-2">
        <p><span class="font-semibold" style="color:#374151">Descrição:</span> <span style="color:#4b5563">${esc(p.description)}</span></p>
        <p><span class="font-semibold" style="color:#374151">Área:</span> <span style="color:#4b5563">${esc(p.area)}</span></p>
        <p><span class="font-semibold" style="color:#374151">Iniciativa:</span> <span style="color:#4b5563">${esc(p.initiative)}</span></p>
        <p class="flex items-center gap-2"><span class="font-semibold" style="color:#374151">Status:</span> <span class="text-xs px-2.5 py-0.5 rounded-full font-medium ${statusColor(p.status)}">${esc(p.status)}</span></p>
        ${p.owner ? `<p><span class="font-semibold" style="color:#374151">Proprietário:</span> <span style="color:#4b5563">${esc(p.owner)}</span></p>` : ""}
        ${p.cost ? `<p><span class="font-semibold" style="color:#374151">Custo (cloud):</span> <span style="color:#ca8a04">${esc(p.cost)}</span></p>` : ""}
        ${p.projected_return ? `<p><span class="font-semibold" style="color:#374151">Retorno projetado:</span> <span style="color:#16a34a">${esc(p.projected_return)}</span></p>` : ""}
        <p class="text-xs pt-2" style="color:#9ca3af;border-top:1px solid #f3f4f6">Criado: ${esc(p.created_at)} | Atualizado: ${esc(p.updated_at)}</p>
      </div>
    `;
    document.getElementById("project-detail").classList.remove("hidden");
  } catch (e) {
    alert("Erro ao carregar detalhes do projeto.");
  }
}

document.getElementById("btn-close-detail").addEventListener("click", () => {
  document.getElementById("project-detail").classList.add("hidden");
});

document.getElementById("btn-search").addEventListener("click", loadProjects);
document.getElementById("search-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadProjects();
});
document.getElementById("source-filter").addEventListener("change", loadProjects);

// ─── Executive Report ─────────────────────────────────────────
document.getElementById("btn-report").addEventListener("click", async () => {
  const body = document.getElementById("report-body");
  body.innerHTML = '<p class="text-gray-500">Gerando relatório...</p>';
  document.getElementById("report-modal").classList.remove("hidden");

  try {
    const res = await fetch(API + "/api/reports/executive");
    if (!res.ok) throw new Error();
    const r = await res.json();

    const sourceRows = Object.entries(r.by_source).map(([k, v]) => `<tr><td class="pr-4 py-1" style="color:#4b5563">${esc(k)}</td><td class="font-semibold" style="color:#166534">${v}</td></tr>`).join("");
    const statusRows = Object.entries(r.by_status).map(([k, v]) => `<tr><td class="pr-4 py-1" style="color:#4b5563">${esc(k)}</td><td class="font-semibold" style="color:#166534">${v}</td></tr>`).join("");

    body.innerHTML = `
      <p class="text-lg font-bold" style="color:#1f2937">Total de Projetos: <span style="color:#16a34a">${r.total_projects}</span></p>
      <p style="color:#6b7280">${esc(r.summary)}</p>
      <div class="grid grid-cols-2 gap-4 mt-4">
        <div class="p-3 rounded-lg" style="background:#f9fafb;border:1px solid #e5e7eb">
          <h4 class="font-semibold text-xs uppercase tracking-wide mb-2" style="color:#6b7280">Por Fonte</h4>
          <table class="text-sm w-full">${sourceRows}</table>
        </div>
        <div class="p-3 rounded-lg" style="background:#f9fafb;border:1px solid #e5e7eb">
          <h4 class="font-semibold text-xs uppercase tracking-wide mb-2" style="color:#6b7280">Por Status</h4>
          <table class="text-sm w-full">${statusRows}</table>
        </div>
      </div>
    `;
  } catch (e) {
    body.innerHTML = '<p class="text-red-500">Erro ao gerar relatório.</p>';
  }
});

document.getElementById("btn-close-report").addEventListener("click", () => {
  document.getElementById("report-modal").classList.add("hidden");
});

// ─── Wizard Chat ──────────────────────────────────────────────
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");

document.getElementById("btn-send").addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  // User bubble
  chatMessages.innerHTML += `<div class="bubble-user p-4 max-w-[80%] ml-auto text-sm" style="color:#1f2937">${esc(text)}</div>`;
  chatInput.value = "";
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Loading indicator
  const loadingId = "loading-" + Date.now();
  chatMessages.innerHTML += `<div id="${loadingId}" class="bubble-bot p-4 max-w-[80%] text-sm" style="color:#9ca3af">Analisando...</div>`;
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch(API + "/api/wizard/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const loading = document.getElementById(loadingId);
    if (loading) loading.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg = err.detail || "Erro ao processar mensagem.";
      chatMessages.innerHTML += `<div class="bubble-bot p-4 max-w-[80%] text-sm" style="color:#dc2626">${esc(msg)}</div>`;
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return;
    }

    const data = await res.json();
    let html = `<div class="bubble-bot p-4 max-w-[80%] text-sm" style="color:#374151">`;
    html += `<p>${esc(data.answer)}</p>`;

    if (data.recommended_tool && data.recommended_tool !== "no_solution") {
      html += `<div class="mt-3 p-3 rounded-lg" style="background:#f0fdf4;border:1px solid #bbf7d0">`;
      html += `<p class="font-semibold text-xs uppercase tracking-wide mb-1" style="color:#15803d">Ferramenta recomendada</p>`;
      html += `<p class="font-medium" style="color:#166534">${esc(data.recommended_tool)}</p>`;
      if (data.justification) html += `<p class="text-xs mt-1" style="color:#16a34a">${esc(data.justification)}</p>`;
      html += `</div>`;
    }

    if (data.similar_projects && data.similar_projects.length > 0) {
      html += `<div class="mt-2 text-xs" style="color:#9ca3af">Projetos similares: ${data.similar_projects.map((p) => esc(p.title)).join(", ")}</div>`;
    }

    html += `</div>`;
    chatMessages.innerHTML += html;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (e) {
    const loading = document.getElementById(loadingId);
    if (loading) loading.remove();
    chatMessages.innerHTML += `<div class="bubble-bot p-4 max-w-[80%] text-sm" style="color:#dc2626">Erro de conexão com o servidor.</div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

// ─── Entrega ──────────────────────────────────────────────────
async function loadTools() {
  const container = document.getElementById("tools-list");
  container.innerHTML = '<p class="text-gray-500 text-sm">Carregando...</p>';

  try {
    const res = await fetch(API + "/api/delivery/tools");
    if (!res.ok) throw new Error();
    const tools = await res.json();

    if (tools.length === 0) {
      container.innerHTML = '<p class="text-gray-500 text-sm">Nenhuma ferramenta cadastrada.</p>';
      return;
    }

    container.innerHTML = tools.map((t) => `
      <div class="pulso-card pulso-card-hover p-5 cursor-pointer" onclick="showProcedure('${esc(t.tool_id)}')">
        <div class="flex items-start gap-3 mb-2">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#f0fdf4">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 2L2 6v6l7 4 7-4V6L9 2z" stroke="#16a34a" stroke-width="1.4" stroke-linejoin="round"/></svg>
          </div>
          <div>
            <h3 class="font-semibold text-sm" style="color:#1f2937">${esc(t.tool_name)}</h3>
            <p class="text-xs mt-0.5" style="color:#9ca3af">${t.steps.length} passo(s)</p>
          </div>
        </div>
        ${t.contact_info ? `<p class="text-xs mt-2" style="color:#6b7280">${esc(t.contact_info)}</p>` : ""}
      </div>
    `).join("");
  } catch (e) {
    container.innerHTML = '<p class="text-red-500 text-sm">Erro ao carregar ferramentas.</p>';
  }
}

async function showProcedure(toolId) {
  try {
    const res = await fetch(API + "/api/delivery/instructions/" + toolId);
    if (!res.ok) throw new Error();
    const p = await res.json();

    document.getElementById("procedure-name").textContent = p.tool_name;
    document.getElementById("procedure-body").innerHTML = `
      <ol class="space-y-2">
        ${p.steps.map((s, i) => `
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center" style="background:#dcfce7;color:#166534">${i + 1}</span>
            <span style="color:#374151">${esc(s)}</span>
          </li>`).join("")}
      </ol>
      ${p.documentation_path ? `<p class="mt-4 text-xs pt-3" style="border-top:1px solid #f3f4f6;color:#6b7280"><span class="font-semibold">Documentação:</span> ${esc(p.documentation_path)}</p>` : ""}
      ${p.contact_info ? `<p class="text-xs" style="color:#6b7280"><span class="font-semibold">Contato:</span> ${esc(p.contact_info)}</p>` : ""}
    `;
    document.getElementById("procedure-modal").classList.remove("hidden");
  } catch (e) {
    alert("Erro ao carregar procedimento.");
  }
}

document.getElementById("btn-close-procedure").addEventListener("click", () => {
  document.getElementById("procedure-modal").classList.add("hidden");
});

// ─── Relatório Executivo Dashboard ────────────────────────────
let dashboardFiltersPopulated = false;

async function loadDashboard() {
  const area = document.getElementById("filter-area").value;
  const initiative = document.getElementById("filter-initiative").value;
  const status = document.getElementById("filter-status").value;
  const owner = document.getElementById("filter-owner").value;

  const params = new URLSearchParams();
  if (area) params.set("area", area);
  if (initiative) params.set("initiative", initiative);
  if (status) params.set("status", status);
  if (owner) params.set("owner", owner);

  try {
    const res = await fetch(API + "/api/reports/executive-dashboard?" + params.toString());
    if (!res.ok) throw new Error("Erro ao carregar relatório");
    const data = await res.json();

    // Populate filter dropdowns on first load only
    if (!dashboardFiltersPopulated) {
      populateFilterSelect("filter-area", data.filter_options.areas, "Todas");
      populateFilterSelect("filter-initiative", data.filter_options.initiatives, "Todas");
      populateFilterSelect("filter-status", data.filter_options.statuses, "Todos");
      populateFilterSelect("filter-owner", data.filter_options.owners, "Todos");
      dashboardFiltersPopulated = true;
    }

    renderKPICards(data);
    renderCharts(data);
    renderCrossTable(data.cross_area_initiative, "cross-area-initiative", "Área", "Iniciativa");
    renderCrossTable(data.cross_area_status, "cross-area-status", "Área", "Status");
  } catch (e) {
    console.error(e);
    document.getElementById("kpi-cards").innerHTML =
      '<p class="text-red-500 text-sm col-span-full">Erro ao carregar relatório.</p>';
  }
}

function populateFilterSelect(selectId, options, defaultLabel) {
  const select = document.getElementById(selectId);
  const currentValue = select.value;
  select.innerHTML = '<option value="">' + esc(defaultLabel) + "</option>";
  options.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt;
    select.appendChild(option);
  });
  select.value = currentValue;
}

// Filter change listeners
["filter-area", "filter-initiative", "filter-status", "filter-owner"].forEach((id) => {
  document.getElementById(id).addEventListener("change", () => loadDashboard());
});

// Clear filters button
document.getElementById("btn-clear-filters").addEventListener("click", () => {
  document.getElementById("filter-area").value = "";
  document.getElementById("filter-initiative").value = "";
  document.getElementById("filter-status").value = "";
  document.getElementById("filter-owner").value = "";
  loadDashboard();
});

// Chart.js instances (module-level for destroy/re-create cycle)
let chartInitiative, chartStatus, chartArea, chartOwner;

// Status color mapping (Req 8.2)
const STATUS_COLORS = {
  active: "#16a34a",
  development: "#2563eb",
  inactive: "#6b7280",
  staging: "#ca8a04",
};

// Dark green palette for bar charts (Req 8.4)
const GREEN_PALETTE = ["#166534", "#15803d", "#16a34a", "#22c55e", "#4ade80", "#86efac", "#bbf7d0", "#dcfce7"];

function renderKPICards(data) {
  document.getElementById("kpi-total").textContent = data.total_contracts;
  document.getElementById("kpi-active").textContent = data.by_status["active"] || 0;
  document.getElementById("kpi-development").textContent = data.by_status["development"] || 0;
  document.getElementById("kpi-sec-compliance").textContent = data.compliance.sec_approval_percentage + "%";
  document.getElementById("kpi-docs-compliance").textContent = data.compliance.docs_link_percentage + "%";

  // Financial KPIs
  if (data.financial) {
    const costEl = document.getElementById("kpi-cost-coverage");
    const returnEl = document.getElementById("kpi-return-coverage");
    if (costEl) costEl.textContent = data.financial.cost_coverage_percentage + "%";
    if (returnEl) returnEl.textContent = data.financial.return_coverage_percentage + "%";
    renderFinancialTable(data.financial.cost_by_initiative, data.financial.return_by_initiative);
  }
}



function renderCharts(data) {
  // Destroy existing instances before re-creating
  if (chartInitiative) chartInitiative.destroy();
  if (chartStatus) chartStatus.destroy();
  if (chartArea) chartArea.destroy();
  if (chartOwner) chartOwner.destroy();

  // Bar chart — Contratos por Iniciativa
  const initLabels = Object.keys(data.by_initiative);
  chartInitiative = new Chart(document.getElementById("chart-initiative"), {
    type: "bar",
    data: {
      labels: initLabels,
      datasets: [{
        label: "Contratos",
        data: Object.values(data.by_initiative),
        backgroundColor: initLabels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length]),
      }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });

  // Pie chart — Contratos por Status
  const statusLabels = Object.keys(data.by_status);
  chartStatus = new Chart(document.getElementById("chart-status"), {
    type: "pie",
    data: {
      labels: statusLabels,
      datasets: [{
        data: Object.values(data.by_status),
        backgroundColor: statusLabels.map((s) => STATUS_COLORS[s] || "#166534"),
      }],
    },
    options: { responsive: true },
  });

  // Bar chart — Contratos por Área
  const areaLabels = Object.keys(data.by_area);
  chartArea = new Chart(document.getElementById("chart-area"), {
    type: "bar",
    data: {
      labels: areaLabels,
      datasets: [{
        label: "Contratos",
        data: Object.values(data.by_area),
        backgroundColor: areaLabels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length]),
      }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });

  // Horizontal bar chart — Contratos por Proprietário
  const ownerLabels = Object.keys(data.by_owner);
  chartOwner = new Chart(document.getElementById("chart-owner"), {
    type: "bar",
    data: {
      labels: ownerLabels,
      datasets: [{
        label: "Contratos",
        data: Object.values(data.by_owner),
        backgroundColor: ownerLabels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length]),
      }],
    },
    options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } } },
  });
}

function renderCrossTable(crossData, containerId, rowLabel, colLabel) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!crossData || crossData.length === 0) {
    container.innerHTML = `<p class="text-gray-400 text-sm">Sem dados disponíveis</p>`;
    return;
  }

  // Extract unique rows and columns
  const rows = [...new Set(crossData.map(d => d.row))].sort();
  const cols = [...new Set(crossData.map(d => d.col))].sort();

  // Build lookup map: { row: { col: count } }
  const lookup = {};
  for (const entry of crossData) {
    if (!lookup[entry.row]) lookup[entry.row] = {};
    lookup[entry.row][entry.col] = entry.count;
  }

  // Header row
  let html = `<table class="w-full text-sm border-collapse">`;
  html += `<thead><tr style="background:#f9fafb">`;
  html += `<th class="border px-3 py-2 text-left font-semibold" style="color:#374151;border-color:#e5e7eb">${esc(rowLabel)}</th>`;
  for (const col of cols) {
    html += `<th class="border px-3 py-2 text-center font-semibold" style="color:#374151;border-color:#e5e7eb">${esc(col)}</th>`;
  }
  html += `<th class="border px-3 py-2 text-center font-semibold" style="color:#374151;border-color:#e5e7eb">Total</th>`;
  html += `</tr></thead><tbody>`;

  // Data rows with row totals
  const colTotals = new Array(cols.length).fill(0);
  let grandTotal = 0;

  for (const row of rows) {
    html += `<tr>`;
    html += `<td class="border px-3 py-2 font-medium" style="color:#374151;border-color:#e5e7eb">${esc(row)}</td>`;
    let rowTotal = 0;
    for (let i = 0; i < cols.length; i++) {
      const val = (lookup[row] && lookup[row][cols[i]]) || 0;
      rowTotal += val;
      colTotals[i] += val;
      html += `<td class="border px-3 py-2 text-center" style="color:#4b5563;border-color:#e5e7eb">${val}</td>`;
    }
    grandTotal += rowTotal;
    html += `<td class="border px-3 py-2 text-center font-semibold" style="color:#166534;border-color:#e5e7eb">${rowTotal}</td>`;
    html += `</tr>`;
  }

  // Footer row
  html += `</tbody><tfoot><tr style="background:#f0fdf4">`;
  html += `<td class="border px-3 py-2 font-semibold" style="color:#374151;border-color:#e5e7eb">Total</td>`;
  for (const ct of colTotals) {
    html += `<td class="border px-3 py-2 text-center font-semibold" style="color:#374151;border-color:#e5e7eb">${ct}</td>`;
  }
  html += `<td class="border px-3 py-2 text-center font-bold" style="color:#166534;border-color:#e5e7eb">${grandTotal}</td>`;
  html += `</tr></tfoot></table>`;

  container.innerHTML = html;
}

function renderFinancialTable(costByInitiative, returnByInitiative) {
  const container = document.getElementById("financial-table");
  if (!container) return;

  const initiatives = [...new Set([...Object.keys(costByInitiative || {}), ...Object.keys(returnByInitiative || {})])].sort();
  if (initiatives.length === 0) {
    container.innerHTML = '<p class="text-gray-400 text-sm">Sem dados financeiros disponíveis.</p>';
    return;
  }

  let html = `<table class="w-full text-sm border-collapse">
    <thead><tr style="background:#f9fafb">
      <th class="border px-3 py-2 text-left font-semibold" style="color:#374151;border-color:#e5e7eb">Iniciativa</th>
      <th class="border px-3 py-2 text-center font-semibold" style="color:#ca8a04;border-color:#e5e7eb">Custo (cloud)</th>
      <th class="border px-3 py-2 text-center font-semibold" style="color:#16a34a;border-color:#e5e7eb">Retorno Projetado</th>
    </tr></thead><tbody>`;

  for (const init of initiatives) {
    const cost = costByInitiative?.[init] || "—";
    const ret = returnByInitiative?.[init] || "—";
    html += `<tr>
      <td class="border px-3 py-2 font-medium" style="color:#374151;border-color:#e5e7eb">${esc(init)}</td>
      <td class="border px-3 py-2 text-center" style="color:#ca8a04;border-color:#e5e7eb">${esc(cost)}</td>
      <td class="border px-3 py-2 text-center" style="color:#16a34a;border-color:#e5e7eb">${esc(ret)}</td>
    </tr>`;
  }

  html += `</tbody></table>`;
  container.innerHTML = html;
}

// ─── Helpers ──────────────────────────────────────────────────
function esc(str) {
  if (str == null) return "";
  const d = document.createElement("div");
  d.textContent = String(str);
  return d.innerHTML;
}

function statusColor(status) {
  const map = {
    active:      "badge-active",
    development: "badge-development",
    inactive:    "badge-inactive",
    staging:     "badge-staging",
  };
  return map[status] || "badge-inactive";
}


// Close modals on backdrop click
["project-detail", "report-modal", "procedure-modal"].forEach((id) => {
  document.getElementById(id).addEventListener("click", (e) => {
    if (e.target === e.currentTarget) e.currentTarget.classList.add("hidden");
  });
});

// Initial load
loadProjects();
