document.addEventListener("DOMContentLoaded", () => {

const API_URL = "http://127.0.0.1:8000";

const pdfFiles = document.getElementById("pdfFiles");
const uploadBtn = document.getElementById("uploadBtn");
const processBtn = document.getElementById("processBtn");
const askBtn = document.getElementById("askBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");

const uploadStatus = document.getElementById("uploadStatus");
const processStatus = document.getElementById("processStatus");

const question = document.getElementById("question");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

const pdfCount = document.getElementById("pdfCount");
const chunkCount = document.getElementById("chunkCount");

const loadingModal = document.getElementById("loadingModal");
const toast = document.getElementById("toast");
const progressFill = document.getElementById("progressFill");

let chatHistory = [];

function showLoading(message = "Processing...") {

    if (!loadingModal) return;

    loadingModal.style.display = "flex";

    const text = loadingModal.querySelector("p");

    if (text) {

        text.innerHTML = message;

    }

}

function hideLoading() {

    if (!loadingModal) return;

    loadingModal.style.display = "none";

}

function showToast(message, color = "#2563eb") {

    if (!toast) {

        alert(message);

        return;

    }

    toast.innerHTML = message;

    toast.style.background = color;

    toast.style.display = "block";

    setTimeout(() => {

        toast.style.display = "none";

    }, 3000);

}

function formatSize(bytes) {

    if (bytes < 1024) {

        return bytes + " B";

    }

    if (bytes < 1024 * 1024) {

        return (bytes / 1024).toFixed(2) + " KB";

    }

    return (bytes / (1024 * 1024)).toFixed(2) + " MB";

}

if (pdfFiles) {

    pdfFiles.addEventListener("change", () => {

        if (pdfFiles.files.length === 0) {

            uploadStatus.innerHTML = "";

            return;

        }

        let html = "<strong>Selected Files</strong><br><br>";

        for (const file of pdfFiles.files) {

            html += `
            📄 ${file.name}
            (${formatSize(file.size)})
            <br>
            `;

        }

        uploadStatus.innerHTML = html;

        showToast(`${pdfFiles.files.length} PDF Selected`);

    });

}

if (uploadBtn) {

    uploadBtn.addEventListener("click", uploadPDFs);

}
async function uploadPDFs() {

    if (!pdfFiles || pdfFiles.files.length === 0) {

        showToast("Please select PDF files", "#ef4444");

        return;

    }

    uploadBtn.disabled = true;

    showLoading("Uploading PDF Documents...");

    const formData = new FormData();

    for (const file of pdfFiles.files) {

        formData.append("files", file);

    }

    try {

        const response = await fetch(API_URL + "/upload/", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (data.status !== "success") {

            hideLoading();

            uploadBtn.disabled = false;

            uploadStatus.innerHTML = "Upload Failed";

            showToast("Upload Failed", "#ef4444");

            return;

        }

        uploadStatus.innerHTML = "✅ Upload Successful";

        pdfCount.innerHTML = data.uploaded_files.length;

        showToast("Upload Successful", "#22c55e");

        await processDocuments();

    }

    catch (err) {

        hideLoading();

        uploadBtn.disabled = false;

        uploadStatus.innerHTML = "Upload Failed";

        console.log(err);

        showToast("Backend Not Running", "#ef4444");

    }

}

async function processDocuments() {

    processStatus.innerHTML = "Processing Documents...";

    showLoading("Extracting Text...");

    if (progressFill) {

        progressFill.style.width = "0%";

    }

    let progress = 0;

    const timer = setInterval(() => {

        progress += 2;

        if (progress <= 90 && progressFill) {

            progressFill.style.width = progress + "%";

        }

    }, 120);

    try {

        const response = await fetch(API_URL + "/process/", {

            method: "POST"

        });

        clearInterval(timer);

        const data = await response.json();

        if (progressFill) {

            progressFill.style.width = "100%";

        }

        processStatus.innerHTML = "✅ Documents Processed";

        chunkCount.innerHTML = data.chunks;

        pdfCount.innerHTML = data.documents;

        showToast("Documents Ready", "#22c55e");

        showLoading("Generating Executive Summary...");

        await generateSummary();

        hideLoading();

        uploadBtn.disabled = false;

    }

    catch (err) {

        clearInterval(timer);

        hideLoading();

        uploadBtn.disabled = false;

        processStatus.innerHTML = "Processing Failed";

        console.log(err);

        showToast("Processing Failed", "#ef4444");

    }

}

async function generateSummary() {

    answer.innerHTML = `
    <div class="welcome-box">
        <div class="loader"></div>
        <h2>Generating Executive Summary...</h2>
    </div>
    `;

    sources.innerHTML = "";

    try {

        const response = await fetch(API_URL + "/chat/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: "Generate a complete executive summary of all uploaded PDF documents."

            })

        });

        const data = await response.json();

        displayAnswer(data.answer);

        displaySources(data.sources);

        chatHistory.push({

            question: "Executive Summary",

            answer: data.answer

        });

        showToast("Summary Generated", "#22c55e");

    }

    catch (err) {

        console.log(err);

        answer.innerHTML = "<h2>Unable to Generate Summary</h2>";

    }

}
if (askBtn) {

    askBtn.addEventListener("click", askAI);

}

if (question) {

    question.addEventListener("keydown", (e) => {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            askAI();

        }

    });

}

async function askAI() {

    const q = question.value.trim();

    if (q === "") {

        showToast("Please enter a question", "#ef4444");

        return;

    }

    askBtn.disabled = true;

    answer.innerHTML = `
    <div class="welcome-box">
        <div class="loader"></div>
        <h2>AI is Thinking...</h2>
        <p>Please wait...</p>
    </div>
    `;

    sources.innerHTML = "";

    try {

        const response = await fetch(API_URL + "/chat/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: q

            })

        });

        const data = await response.json();

        askBtn.disabled = false;

        displayAnswer(data.answer);

        displaySources(data.sources);

        chatHistory.push({

            question: q,

            answer: data.answer

        });

        showToast("Answer Generated", "#22c55e");

    }

    catch (err) {

        askBtn.disabled = false;

        console.log(err);

        answer.innerHTML = `
        <div class="welcome-box">
            <h2 style="color:red">
                Unable to connect to backend
            </h2>
        </div>
        `;

        showToast("Backend Error", "#ef4444");

    }

}

function displayAnswer(text) {

    if (!text) {

        answer.innerHTML = "<h2>No Answer Found</h2>";

        return;

    }

    answer.innerHTML = `
    <div class="ai-response">

        <h2>🤖 AI Response</h2>

        <hr>

        <div class="answer-text">

            ${text.replace(/\n/g, "<br>")}

        </div>

    </div>
    `;

}

function displaySources(list) {

    sources.innerHTML = "";

    if (!list || list.length === 0) {

        sources.innerHTML = `
        <div class="source-card">

            No Sources Found

        </div>
        `;

        return;

    }

    list.forEach((item, index) => {

        const div = document.createElement("div");

        div.className = "source-card";

        div.innerHTML = `

        <h4>

            📄 Source ${index + 1}

        </h4>

        <p>

            ${item}

        </p>

        `;

        sources.appendChild(div);

    });

}

if (copyBtn) {

    copyBtn.addEventListener("click", copyAnswer);

}

function copyAnswer() {

    const text = answer.innerText.trim();

    if (text === "") {

        showToast("Nothing to Copy", "#ef4444");

        return;

    }

    navigator.clipboard.writeText(text);

    showToast("Answer Copied", "#22c55e");

}

if (downloadBtn) {

    downloadBtn.addEventListener("click", downloadAnswer);

}

function downloadAnswer() {

    const text = answer.innerText.trim();

    if (text === "") {

        showToast("Nothing to Download", "#ef4444");

        return;

    }

    const blob = new Blob(

        [text],

        {

            type: "text/plain"

        }

    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "AI_Research_Answer.txt";

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);

    showToast("Downloaded Successfully", "#22c55e");

}
if (clearBtn) {

    clearBtn.addEventListener("click", clearChat);

}

function clearChat() {

    if (question) {

        question.value = "";

    }

    if (answer) {

        answer.innerHTML = `
        <div class="welcome-box">

            <h2>🤖 AI Research Assistant</h2>

            <p>

                Upload one or more PDF documents.

                An executive summary will be generated automatically.

                Then ask any question related to your uploaded PDFs.

            </p>

        </div>
        `;

    }

    if (sources) {

        sources.innerHTML = `
        <div class="source-card">

            No Sources Available

        </div>
        `;

    }

    chatHistory = [];

    showToast("Chat Cleared");

}

const scrollBtn = document.getElementById("scrollTop");

if (scrollBtn) {

    window.addEventListener("scroll", () => {

        if (window.scrollY > 300) {

            scrollBtn.style.display = "block";

        }

        else {

            scrollBtn.style.display = "none";

        }

    });

    scrollBtn.addEventListener("click", () => {

        window.scrollTo({

            top: 0,

            behavior: "smooth"

        });

    });

}

window.addEventListener("online", () => {

    showToast("Internet Connected", "#22c55e");

});

window.addEventListener("offline", () => {

    showToast("Internet Disconnected", "#ef4444");

});

document.addEventListener("keydown", (e) => {

    if (e.ctrlKey && e.key === "Enter") {

        askAI();

    }

});

window.addEventListener("load", () => {

    answer.innerHTML = `
    <div class="welcome-box">

        <h2>📄 AI Research Assistant</h2>

        <p>

            Upload your PDF documents to begin.

        </p>

        <br>

        <h3>Suggested Questions</h3>

        <ul style="text-align:left;line-height:2">

            <li>Summarize all uploaded documents</li>

            <li>Compare all documents</li>

            <li>Explain the architecture</li>

            <li>What technologies are used?</li>

            <li>Generate an executive summary</li>

        </ul>

    </div>
    `;

    sources.innerHTML = `
    <div class="source-card">

        Sources will appear here after processing.

    </div>
    `;

    console.log("✅ AI Research Assistant Ready");

});

});