
"use strict";

// ============================================
// ENTERPRISE RAG AI - COMPLETE FRONTEND
// ============================================

const API_URL = "http://127.0.0.1:8000";

const API_TIMEOUT = 15000;
const UPLOAD_TIMEOUT = 120000;
const ASK_TIMEOUT = 90000;

// DOM elements
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
const uploadButton = document.getElementById("upload-button");
const uploadStatus = document.getElementById("upload-status");

const documentsList = document.getElementById("documents-list");
const refreshButton = document.getElementById("refresh-documents");
const newChatButton = document.getElementById("new-chat-button");

const questionInput = document.getElementById("question");
const askButton = document.getElementById("ask-button");
const answerArea = document.getElementById("answer-area");

let isAsking = false;

// ============================================
// HELPERS
// ============================================

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatAnswer(value) {
    // Escape HTML first, then support basic Markdown.
    let text = escapeHTML(value);

    text = text.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    text = text.replace(/\n/g, "<br>");

    return text;
}

async function apiRequest(url, options = {}, timeout = API_TIMEOUT) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });

        const rawText = await response.text();
        let data = {};

        if (rawText) {
            try {
                data = JSON.parse(rawText);
            } catch {
                data = { message: rawText };
            }
        }

        if (!response.ok) {
            const detail =
                data.detail ||
                data.message ||
                `HTTP error ${response.status}`;

            throw new Error(detail);
        }

        return data;
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error(
                `Request timed out after ${Math.round(timeout / 1000)} seconds. ` +
                "Check whether the backend is responding."
            );
        }

        if (error instanceof TypeError) {
            throw new Error(
                "Cannot reach the backend. Check that FastAPI is running at " +
                API_URL + " and inspect the backend CMD."
            );
        }

        throw error;
    } finally {
        clearTimeout(timer);
    }
}

function showStatus(element, message, type = "info") {
    if (!element) return;

    element.textContent = message;
    element.style.color =
        type === "error" ? "#ff7777" :
        type === "success" ? "#75e0a0" :
        "#9db9ef";
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });
    });
}

// ============================================
// DOCUMENT LIST
// ============================================

async function loadDocuments() {
    if (!documentsList) return;

    documentsList.textContent = "⏳ Loading documents...";

    if (refreshButton) {
        refreshButton.disabled = true;
    }

    console.log("Fetching documents from:", `${API_URL}/documents`);

    try {
        const data = await apiRequest(
            `${API_URL}/documents`,
            {},
            API_TIMEOUT
        );

        const documents = Array.isArray(data.documents)
            ? data.documents
            : [];

        renderDocuments(documents);

        console.log("Documents loaded:", documents);
    } catch (error) {
        console.error("Document loading failed:", error);

        documentsList.replaceChildren();

        const errorBox = document.createElement("div");
        errorBox.className = "documents-loading";
        errorBox.style.color = "#ff7777";
        errorBox.textContent = `❌ ${error.message}`;

        const retryButton = document.createElement("button");
        retryButton.type = "button";
        retryButton.textContent = "Try Again";
        retryButton.addEventListener("click", loadDocuments);

        documentsList.append(errorBox, retryButton);
    } finally {
        if (refreshButton) {
            refreshButton.disabled = false;
        }
    }
}

function renderDocuments(documents) {
    documentsList.replaceChildren();

    if (!documents.length) {
        const empty = document.createElement("div");
        empty.className = "documents-loading";
        empty.textContent = "📂 No documents indexed yet.";
        documentsList.appendChild(empty);
        return;
    }

    documents.forEach((item) => {
        const card = document.createElement("div");
        card.className = "document-card";

        const icon = document.createElement("div");
        icon.className = "document-icon";
        icon.textContent = "📄";

        const info = document.createElement("div");
        info.className = "document-info";

        const title = document.createElement("strong");
        title.textContent = item.filename || "Unnamed document";

        const details = document.createElement("span");
        details.textContent =
            `${item.pages ?? 0} pages • ${item.chunks ?? 0} chunks`;

        info.append(title, details);

        const status = document.createElement("div");
        status.className = "document-status";
        status.textContent = "✓ Indexed";

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-document-button";
        deleteButton.textContent = "🗑 Delete";

        deleteButton.addEventListener("click", () => {
            deleteDocument(item.filename, deleteButton);
        });

        card.append(icon, info, status, deleteButton);
        documentsList.appendChild(card);
    });
}

// ============================================
// DELETE DOCUMENT
// Assumes DELETE /documents/{filename}
// ============================================

async function deleteDocument(filename, button) {
    if (!filename) return;

    if (!confirm(`Delete "${filename}" from the knowledge base?`)) {
        return;
    }

    button.disabled = true;

    try {
        await apiRequest(
            `${API_URL}/documents/${encodeURIComponent(filename)}`,
            { method: "DELETE" },
            API_TIMEOUT
        );

        await loadDocuments();
    } catch (error) {
        console.error("Delete failed:", error);
        alert(`Could not delete document:\n${error.message}`);
        button.disabled = false;
    }
}

// ============================================
// SELECT PDF
// ============================================

if (fileInput) {
    fileInput.addEventListener("change", () => {
        const file = fileInput.files?.[0];

        if (fileName) {
            fileName.textContent = file
                ? file.name
                : "No file selected";
        }

        if (file && !file.name.toLowerCase().endsWith(".pdf")) {
            showStatus(
                uploadStatus,
                "Please choose a PDF file.",
                "error"
            );

            fileInput.value = "";

            if (fileName) {
                fileName.textContent = "No file selected";
            }
        } else {
            showStatus(uploadStatus, "");
        }
    });
}

// ============================================
// UPLOAD AND INDEX PDF
// Assumes POST /upload with multipart field "file"
// ============================================

if (uploadButton) {
    uploadButton.addEventListener("click", async () => {
        const file = fileInput?.files?.[0];

        if (!file) {
            showStatus(
                uploadStatus,
                "Please select a PDF first.",
                "error"
            );
            return;
        }

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            showStatus(uploadStatus, "Only PDF files are supported.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadButton.disabled = true;
        uploadButton.textContent = "Uploading...";

        showStatus(
            uploadStatus,
            "⏳ Uploading and indexing your PDF..."
        );

        try {
            const result = await apiRequest(
                `${API_URL}/upload`,
                {
                    method: "POST",
                    body: formData
                },
                UPLOAD_TIMEOUT
            );

            showStatus(
                uploadStatus,
                result.message || "✅ PDF uploaded and indexed successfully.",
                "success"
            );

            fileInput.value = "";

            if (fileName) {
                fileName.textContent = "No file selected";
            }

            await loadDocuments();
        } catch (error) {
            console.error("Upload failed:", error);

            showStatus(
                uploadStatus,
                `❌ ${error.message}`,
                "error"
            );
        } finally {
            uploadButton.disabled = false;
            uploadButton.textContent = "⬆ Upload & Index";
        }
    });
}

// ============================================
// CHAT MESSAGE RENDERING
// ============================================

function addUserMessage(text) {
    const message = document.createElement("div");
    message.className = "chat-message user-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "👤";

    const content = document.createElement("div");
    content.className = "message-content";

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "You";

    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = text;

    content.append(label, body);
    message.append(avatar, content);
    answerArea.appendChild(message);

    scrollToBottom();
}

function addLoadingMessage() {
    const message = document.createElement("div");
    message.className = "chat-message ai-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "🤖";

    const content = document.createElement("div");
    content.className = "message-content";

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "AI Assistant";

    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = "🔎 Searching your documents...";

    content.append(label, body);
    message.append(avatar, content);
    answerArea.appendChild(message);

    scrollToBottom();
    return message;
}

function addAIMessage(data) {
    const message = document.createElement("div");
    message.className = "chat-message ai-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "🤖";

    const content = document.createElement("div");
    content.className = "message-content";

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "AI Assistant";

    const body = document.createElement("div");
    body.className = "message-text ai-answer";

    const answer =
        data.answer ??
        data.response ??
        data.result ??
        data.message ??
        "The backend returned no answer.";

    body.innerHTML = formatAnswer(answer);

    content.append(label, body);

    const sources =
        data.sources ??
        data.source ??
        data.references ??
        [];

    if (Array.isArray(sources) && sources.length > 0) {
        const sourcesSection = document.createElement("div");
        sourcesSection.className = "sources-section";

        const sourcesTitle = document.createElement("div");
        sourcesTitle.className = "sources-title";
        sourcesTitle.textContent = "📚 Sources";

        const sourcesList = document.createElement("div");
        sourcesList.className = "sources-list";

        const uniqueSources = new Set();

        sources.forEach((source) => {
            const filename =
                typeof source === "string"
                    ? source
                    : source.source ||
                      source.filename ||
                      source.document ||
                      "Document";

            const page =
                typeof source === "string"
                    ? null
                    : source.page ??
                      source.page_number ??
                      source.pageNumber ??
                      null;

            const key = `${filename}|${page ?? ""}`;

            if (uniqueSources.has(key)) return;
            uniqueSources.add(key);

            const row = document.createElement("div");
            row.className = "source-item";

            row.textContent =
                `📄 ${filename}` +
                (page !== null ? ` — Page ${page}` : "");

            sourcesList.appendChild(row);
        });

        sourcesSection.append(sourcesTitle, sourcesList);
        content.appendChild(sourcesSection);
    }

    message.append(avatar, content);
    answerArea.appendChild(message);

    scrollToBottom();
}

function addErrorMessage(error) {
    const message = document.createElement("div");
    message.className = "chat-message ai-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "⚠️";

    const content = document.createElement("div");
    content.className = "message-content";

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "Request failed";

    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = error;

    content.append(label, body);
    message.append(avatar, content);
    answerArea.appendChild(message);

    scrollToBottom();
}

// ============================================
// ASK QUESTION
// Assumes POST /ask with JSON {"question": "..."}
// ============================================

async function askQuestion() {
    if (isAsking) return;

    const question = questionInput.value.trim();

    if (!question) {
        questionInput.focus();
        return;
    }

    isAsking = true;
    askButton.disabled = true;
    askButton.textContent = "Thinking...";

    addUserMessage(question);
    questionInput.value = "";

    const loadingMessage = addLoadingMessage();

    try {
        const data = await apiRequest(
            `${API_URL}/ask`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            },
            ASK_TIMEOUT
        );

        loadingMessage.remove();
        addAIMessage(data);
    } catch (error) {
        console.error("Question failed:", error);

        loadingMessage.remove();
        addErrorMessage(error.message);
    } finally {
        isAsking = false;
        askButton.disabled = false;
        askButton.textContent = "Ask";
        questionInput.focus();
    }
}

if (askButton) {
    askButton.addEventListener("click", askQuestion);
}

if (questionInput) {
    questionInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            askQuestion();
        }
    });
}

// ============================================
// NEW CHAT
// ============================================

if (newChatButton) {
    newChatButton.addEventListener("click", () => {
        answerArea.replaceChildren();
        questionInput.value = "";
        questionInput.focus();
    });
}

// ============================================
// REFRESH DOCUMENTS
// ============================================

if (refreshButton) {
    refreshButton.addEventListener("click", loadDocuments);
}

// ============================================
// EXAMPLE QUESTIONS
// ============================================

document.querySelectorAll(".example-questions button").forEach((button) => {
    button.addEventListener("click", () => {
        questionInput.value = button.textContent.trim();
        questionInput.focus();
    });
});

// ============================================
// STARTUP
// ============================================

console.log("Enterprise RAG AI frontend initialized.");
loadDocuments();