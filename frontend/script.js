const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;

const healthIndicator = document.getElementById("health-indicator");
const form = document.getElementById("generate-form");
const submitButton = document.getElementById("submit-button");
const logOutput = document.getElementById("log-output");
const resultsHelp = document.getElementById("results-help");
const resultsList = document.getElementById("results-list");

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      throw new Error("Unexpected response");
    }
    healthIndicator.textContent = "Backend is online";
    healthIndicator.className = "health health--ok";
  } catch (error) {
    console.error(error);
    healthIndicator.textContent = "Backend is offline";
    healthIndicator.className = "health health--error";
  }
}

function resetLogs() {
  logOutput.textContent = "Waiting for a job…";
  resultsHelp.style.display = "block";
  resultsList.innerHTML = "";
}

function appendLogs(entries) {
  if (!entries || entries.length === 0) {
    logOutput.textContent = "No log entries were returned.";
    return;
  }

  const content = entries
    .map(({ type, message }) => `[${type.toUpperCase()}] ${message}`)
    .join("\n");

  logOutput.textContent = content;
}

function updateResults(outputs) {
  resultsList.innerHTML = "";

  if (!outputs || outputs.length === 0) {
    resultsHelp.style.display = "block";
    return;
  }

  resultsHelp.style.display = "none";

  outputs.forEach((href) => {
    const listItem = document.createElement("li");
    const link = document.createElement("a");
    link.href = `${API_BASE}${href}`;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = href.split("/").pop();
    listItem.appendChild(link);
    resultsList.appendChild(listItem);
  });
}

function collectFormData() {
  const formData = new FormData();

  const apiKey = document.getElementById("api-key").value.trim();
  const model = document.getElementById("model").value;
  const mergeGraphs = document.getElementById("merge-graphs").checked;
  const enableCache = document.getElementById("enable-cache").checked;
  const resolution = document.getElementById("resolution").value;
  const files = document.getElementById("pdf-files").files;

  if (!apiKey) {
    throw new Error("API key is required.");
  }

  if (!files || files.length === 0) {
    throw new Error("Please select at least one PDF file.");
  }

  const configPayload = {
    api_key: apiKey,
    model,
    api: "openai",
  };

  const optionsPayload = {
    merge_document_graphs: mergeGraphs,
    optimization_on: enableCache,
    resolution_state: resolution,
  };

  formData.append("config", JSON.stringify(configPayload));
  formData.append("options", JSON.stringify(optionsPayload));

  Array.from(files).forEach((file) => {
    formData.append("files", file, file.name);
  });

  return formData;
}

async function submitJob(event) {
  event.preventDefault();

  try {
    const payload = collectFormData();
    logOutput.textContent = "Uploading documents and starting the job…";
    submitButton.disabled = true;
    submitButton.textContent = "Processing…";

    const response = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      body: payload,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    appendLogs(data.logs);
    updateResults(data.outputs);
  } catch (error) {
    logOutput.textContent = `Error: ${error.message}`;
    resultsHelp.style.display = "block";
    resultsList.innerHTML = "";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Generate Graphs";
  }
}

resetLogs();
checkHealth();
form.addEventListener("submit", submitJob);
