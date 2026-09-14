const state = {
  agents: [],
  selectedAgent: null,
  messages: [],
  runs: [],
  activeRun: null,
  health: null,
  tab: "chat",
  eventSource: null,
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status})`);
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function initials(name) {
  return name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

function label(value) {
  return String(value || "").replaceAll("_", " ");
}

function showToast(message, error = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.toggle("error", error);
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

async function initialize() {
  try {
    const [health, agents, runs] = await Promise.all([
      api("/api/health"),
      api("/api/agents"),
      api("/api/runs"),
    ]);
    state.health = health;
    state.agents = agents;
    state.runs = runs;
    renderHealth();
    renderAgents();
    if (agents.length) await selectAgent(agents[0].id);
    if (runs.length) await selectRun(runs[0].run_id);
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderHealth() {
  const live = state.health?.openai_available;
  $("#system-signal").className = "signal ready";
  $("#system-label").textContent = "Control room ready";
  $("#system-detail").textContent = live ? `${state.health.openai_model} available` : "Deterministic mode";
  $("#live-model-toggle").disabled = !live;
  $("#live-model-toggle").title = live ? "Use the configured OpenAI model" : "OPENAI_API_KEY is not configured";
}

function renderAgents() {
  $("#agent-count").textContent = state.agents.length;
  $("#agent-list").innerHTML = state.agents.map((agent) => `
    <button class="agent-button ${state.selectedAgent?.id === agent.id ? "active" : ""}" data-agent-id="${escapeHtml(agent.id)}" title="${escapeHtml(agent.name)}">
      <span class="agent-avatar">${escapeHtml(initials(agent.name))}</span>
      <span class="agent-button-text">
        <strong>${escapeHtml(agent.name)}</strong>
        <span>${escapeHtml(label(agent.department))}</span>
      </span>
      <span class="agent-status-dot ${escapeHtml(agent.status)}"></span>
    </button>
  `).join("");
  document.querySelectorAll("[data-agent-id]").forEach((button) => {
    button.addEventListener("click", () => selectAgent(button.dataset.agentId));
  });
}

async function selectAgent(agentId) {
  state.selectedAgent = state.agents.find((agent) => agent.id === agentId);
  state.messages = await api(`/api/agents/${encodeURIComponent(agentId)}/messages`);
  renderAgents();
  renderAgentHeader();
  renderAgentInspector();
  renderMessages();
}

function renderAgentHeader() {
  const agent = state.selectedAgent;
  if (!agent) return;
  $("#workspace-title").textContent = state.tab === "chat" ? agent.name : "Controlled Workflow";
  $("#active-agent-avatar").textContent = initials(agent.name);
  $("#active-agent-name").textContent = agent.name;
  $("#active-agent-department").textContent = label(agent.department);
}

function renderAgentInspector() {
  const agent = state.selectedAgent;
  if (!agent) return;
  $("#agent-status").textContent = agent.status;
  $("#agent-mission").textContent = agent.mission;
  renderTags("#agent-owns", agent.owns);
  renderStack("#agent-skills", agent.skills);
  renderTags("#agent-tools", agent.tools);
  renderStack("#agent-restrictions", agent.prohibited_actions);
}

function renderTags(selector, items = []) {
  $(selector).innerHTML = items.map((item) => `<span>${escapeHtml(label(item))}</span>`).join("") || "<span>None</span>";
}

function renderStack(selector, items = []) {
  $(selector).innerHTML = items.map((item) => `<span>${escapeHtml(label(item))}</span>`).join("") || "<span>None</span>";
}

function renderMessages() {
  const list = $("#message-list");
  if (!state.messages.length) {
    list.innerHTML = `<div class="message-empty"><strong>${escapeHtml(state.selectedAgent.name)}</strong><span>Advisory channel ready</span></div>`;
    return;
  }
  list.innerHTML = state.messages.map((message) => `
    <article class="message ${escapeHtml(message.role)}">
      <div class="message-meta">${message.role === "user" ? "You" : escapeHtml(state.selectedAgent.name)} · ${escapeHtml(message.provider)}</div>
      <div class="message-content">${escapeHtml(message.content)}</div>
    </article>
  `).join("");
  list.scrollTop = list.scrollHeight;
}

async function sendMessage(event) {
  event.preventDefault();
  const input = $("#message-input");
  const button = $("#send-button");
  const message = input.value.trim();
  if (!message || !state.selectedAgent) return;
  input.value = "";
  button.disabled = true;
  state.messages.push({ role: "user", content: message, provider: "pending" });
  renderMessages();
  try {
    await api(`/api/agents/${encodeURIComponent(state.selectedAgent.id)}/messages`, {
      method: "POST",
      body: JSON.stringify({
        message,
        provider: $("#live-model-toggle").checked ? "openai" : "deterministic",
      }),
    });
    state.messages = await api(`/api/agents/${encodeURIComponent(state.selectedAgent.id)}/messages`);
    renderMessages();
  } catch (error) {
    state.messages = await api(`/api/agents/${encodeURIComponent(state.selectedAgent.id)}/messages`);
    renderMessages();
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    input.focus();
  }
}

function switchTab(tab) {
  state.tab = tab;
  document.querySelectorAll(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === tab));
  $("#chat-view").classList.toggle("active", tab === "chat");
  $("#workflow-view").classList.toggle("active", tab === "workflow");
  $("#agent-inspector").classList.toggle("hidden", tab !== "chat");
  $("#run-inspector").classList.toggle("hidden", tab !== "workflow");
  $("#workspace-title").textContent = tab === "chat" ? state.selectedAgent?.name || "Agent" : "Controlled Workflow";
}

async function startWorkflow() {
  const button = $("#start-workflow");
  button.disabled = true;
  try {
    const run = await api("/api/runs", {
      method: "POST",
      body: JSON.stringify({
        runtime_name: "deterministic",
        until_task: $("#workflow-target").value,
      }),
    });
    state.activeRun = run;
    state.runs = await api("/api/runs");
    renderRun();
    connectRunEvents(run.summary.run_id);
    showToast(`Run ${run.summary.run_id} started`);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

async function selectRun(runId) {
  if (!runId) return;
  state.activeRun = await api(`/api/runs/${encodeURIComponent(runId)}`);
  renderRun();
  connectRunEvents(runId);
}

function renderRun() {
  const run = state.activeRun;
  $("#run-empty").classList.toggle("hidden", Boolean(run));
  $("#run-content").classList.toggle("hidden", !run);
  if (!run) return;

  $("#run-id").textContent = run.summary.run_id;
  $("#run-phase").textContent = label(run.summary.phase);
  $("#run-select").innerHTML = state.runs.map((item) => `
    <option value="${escapeHtml(item.run_id)}" ${item.run_id === run.summary.run_id ? "selected" : ""}>${escapeHtml(item.run_id)} · ${escapeHtml(label(item.phase))}</option>
  `).join("");

  const pending = run.approvals.filter((item) => item.status === "pending");
  $("#approval-section").classList.toggle("hidden", !pending.length);
  $("#approval-count").textContent = `${pending.length} pending`;
  $("#approval-list").innerHTML = pending.map((approval) => `
    <article class="approval-item">
      <span class="approval-level">${escapeHtml(approval.required_level)}</span>
      <div class="approval-copy">
        <strong>${escapeHtml(approval.requested_action)}</strong>
        <span>${escapeHtml(approval.task_id)} · ${escapeHtml(approval.recommendation || "Human decision required")}</span>
      </div>
      <div class="approval-actions">
        <button class="approve" data-approval="${escapeHtml(approval.approval_id)}" data-decision="approved">Approve</button>
        <button class="reject" data-approval="${escapeHtml(approval.approval_id)}" data-decision="rejected">Reject</button>
      </div>
    </article>
  `).join("");
  document.querySelectorAll("[data-approval]").forEach((button) => {
    button.addEventListener("click", () => decideApproval(button.dataset.approval, button.dataset.decision));
  });

  const completed = run.graph.nodes.filter((task) => task.status === "completed").length;
  $("#task-progress").textContent = `${completed} / ${run.graph.nodes.length} completed`;
  $("#task-timeline").innerHTML = run.graph.nodes.map((task) => `
    <article class="task-item ${escapeHtml(task.status)}" data-task-id="${escapeHtml(task.task_id)}">
      <span class="task-marker"></span>
      <div class="task-copy">
        <strong>${escapeHtml(task.task_id)} · ${escapeHtml(label(task.assigned_agent))}</strong>
        <span>${escapeHtml(task.objective)}</span>
      </div>
      <span class="task-status">${escapeHtml(label(task.status))}</span>
    </article>
  `).join("");
  document.querySelectorAll("[data-task-id]").forEach((item) => {
    item.addEventListener("click", () => renderResultDetail(item.dataset.taskId));
  });

  $("#event-list").innerHTML = run.events.slice().reverse().map((event) => `
    <div class="event-item">
      <span>${escapeHtml(new Date(event.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }))}</span>
      <strong>${escapeHtml(label(event.event_type))}</strong>
    </div>
  `).join("");
  renderCanonicalState(run.committed_state);
}

function renderCanonicalState(committedState) {
  const current = committedState || {};
  $("#state-status").textContent = committedState ? "Committed" : "No commit";
  const entries = Object.entries(current);
  $("#canonical-state").innerHTML = entries.length
    ? entries.map(([key, value]) => `<div class="state-cell"><span>${escapeHtml(label(key))}</span><strong>${escapeHtml(value)}</strong></div>`).join("")
    : `<div class="state-cell"><span>Status</span><strong>Awaiting completed run</strong></div>`;
}

function renderResultDetail(taskId) {
  const result = state.activeRun?.agent_results?.[taskId];
  $("#result-detail").textContent = result ? JSON.stringify(result, null, 2) : "This task has not produced a result yet.";
}

async function decideApproval(approvalId, decision) {
  try {
    const runId = state.activeRun.summary.run_id;
    state.activeRun = await api(`/api/runs/${encodeURIComponent(runId)}/approvals/${encodeURIComponent(approvalId)}`, {
      method: "POST",
      body: JSON.stringify({ decision }),
    });
    state.runs = await api("/api/runs");
    renderRun();
    showToast(`Approval ${decision}`);
  } catch (error) {
    showToast(error.message, true);
  }
}

function connectRunEvents(runId) {
  if (state.eventSource) state.eventSource.close();
  state.eventSource = new EventSource(`/api/runs/${encodeURIComponent(runId)}/events`);
  let refreshTimer;
  const refresh = () => {
    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(async () => {
      if (state.activeRun?.summary.run_id === runId) {
        state.activeRun = await api(`/api/runs/${encodeURIComponent(runId)}`);
        renderRun();
      }
    }, 150);
  };
  ["run.created", "phase.changed", "approval.requested", "approval.decided", "task.completed", "run.completed", "run.failed"]
    .forEach((eventName) => state.eventSource.addEventListener(eventName, refresh));
}

document.addEventListener("DOMContentLoaded", () => {
  $("#message-form").addEventListener("submit", sendMessage);
  $("#start-workflow").addEventListener("click", startWorkflow);
  $("#run-select").addEventListener("change", (event) => selectRun(event.target.value));
  document.querySelectorAll(".tab-button").forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tab)));
  $("#message-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      $("#message-form").requestSubmit();
    }
  });
  initialize();
});
