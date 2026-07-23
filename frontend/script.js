document.addEventListener("DOMContentLoaded", () => {

const API_URL = "http://127.0.0.1:8000";

// DOM ELEMENTS
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
const processingTime = document.getElementById("processingTime");
const modelName = document.getElementById("modelName");

const uploadedFiles =
document.getElementById("uploadedFiles");

const loadingModal =
document.getElementById("loadingModal");

const toast =
document.getElementById("toast");

const progressFill =
document.getElementById("progressFill");

const heroUploadBtn =
document.getElementById("heroUploadBtn");

let chatHistory = [];

// =====================================================
// HERO BUTTON
// =====================================================

if(heroUploadBtn){

    heroUploadBtn.addEventListener("click",()=>{

        pdfFiles.click();

    });

}

// =====================================================
// LOADING
// =====================================================

function showLoading(message = "Processing...") {

    if (!loadingModal) return;

    loadingModal.style.display = "flex";

    // Update loading message
    const text = loadingModal.querySelector(".loading-message");

    if (text) {
        text.innerHTML = message;
    }

    // Animate progress bar
    const bar = loadingModal.querySelector(".progress-bar");

    if (bar) {

        // Reset
        bar.style.transition = "none";
        bar.style.width = "0%";

        // Force browser repaint
        bar.offsetWidth;

        // Animate to 100%
        bar.style.transition = "width 8s linear";
        bar.style.width = "100%";
    }

}

function hideLoading() {

    if (!loadingModal) return;

    // Reset progress bar
    const bar = loadingModal.querySelector(".progress-bar");

    if (bar) {
        bar.style.transition = "none";
        bar.style.width = "0%";
    }

    loadingModal.style.display = "none";

}

// =====================================================
// TOAST
// =====================================================

function showToast(message,color="#2563eb"){

    if(!toast){

        alert(message);

        return;

    }

    toast.innerHTML=message;

    toast.style.background=color;

    toast.style.display="block";

    setTimeout(()=>{

        toast.style.display="none";

    },3000);

}

// =====================================================
// FILE SIZE
// =====================================================

function formatSize(bytes){

    if(bytes<1024){

        return bytes+" B";

    }

    if(bytes<1024*1024){

        return (bytes/1024).toFixed(2)+" KB";

    }

    return (bytes/(1024*1024)).toFixed(2)+" MB";

}

// =====================================================
// FILE SELECT
// =====================================================

if(pdfFiles){

pdfFiles.addEventListener("change",()=>{

    if(pdfFiles.files.length===0){

        uploadStatus.innerHTML="";

        return;

    }

    let html="<strong>Selected Files</strong><br><br>";

    for(const file of pdfFiles.files){

        html+=`
        📄 ${file.name}
        (${formatSize(file.size)})
        <br>
        `;

    }

    uploadStatus.innerHTML=html;

    showToast(`${pdfFiles.files.length} PDF Selected`);

});

}

// =====================================================
// UPLOAD
// =====================================================

if(uploadBtn){

uploadBtn.addEventListener("click",uploadPDFs);

}

async function uploadPDFs(){

    if(!pdfFiles || pdfFiles.files.length===0){

        showToast("Please select PDF files","#ef4444");

        return;

    }

    uploadBtn.disabled=true;

    showLoading("Uploading PDF Documents...");

    const formData=new FormData();

    for(const file of pdfFiles.files){

        formData.append("files",file);

    }

    try{

        const response=await fetch(API_URL+"/upload/",{

            method:"POST",

            body:formData

        });

        if(!response.ok){
            throw new Error("Backend Error");
        }

        const data=await response.json();

        if(data.status!=="success"){

            hideLoading();

            uploadBtn.disabled=false;

            uploadStatus.innerHTML="Upload Failed";

            showToast("Upload Failed","#ef4444");

            return;

        }

        uploadStatus.innerHTML="✅ Upload Successful";

        if(uploadedFiles){

            uploadedFiles.innerHTML="";

            data.uploaded_files.forEach(file=>{

                uploadedFiles.innerHTML+=`

                <div class="source-card">

                    📄 ${file}

                </div>

                `;

            });

        }

        if(pdfCount){

            pdfCount.textContent=data.uploaded_files.length;

        }

        showToast("Upload Successful","#22c55e");

        await processDocuments();
        pdfFiles.value="";

    }

    catch(err){

        console.log(err);

        hideLoading();

        uploadBtn.disabled=false;

        uploadStatus.innerHTML="Upload Failed";

        showToast("Upload Maximum 5 PDFs","#ef4444");

    }

}

// =====================================================
// PROCESS DOCUMENTS
// =====================================================

async function processDocuments(){
    if(processStatus){
        processStatus.innerHTML="Processing Documents...";
    }

    showLoading("Extracting Text...");

    if(progressFill){

        progressFill.style.width="0%";

    }

    let progress=0;

    const timer=setInterval(()=>{

        progress+=2;

        if(progress<=90 && progressFill){

            progressFill.style.width=progress+"%";

        }

    },120);

    try{

        const response=await fetch(API_URL+"/process/",{

            method:"POST"

        });

        clearInterval(timer);

        const data=await response.json();

        console.log("PROCESS RESPONSE:",data);

        if(progressFill){

            progressFill.style.width="100%";

        }
        if(processStatus){
            processStatus.innerHTML="✅ Documents Processed";
        }

        if(chunkCount){

            chunkCount.textContent=data.chunks;

        }

        if(processingTime){

            processingTime.textContent=
            data.processing_time
            ? data.processing_time.toFixed(2)+" s"
            : "--";

        }

        if(modelName){

            modelName.textContent=
            data.model || "llama3.2:3b";

        }

        if(pdfCount){

            pdfCount.textContent=data.documents;

        }

        showToast("Documents Ready","#22c55e");

        showLoading("Generating Executive Summary...");

        await generateSummary();

        hideLoading();

        uploadBtn.disabled=false;

    }

    catch(err){

        clearInterval(timer);

        console.log(err);

        hideLoading();

        uploadBtn.disabled=false;
        if(processStatus){
            processStatus.innerHTML="Processing Failed";
        }

        showToast("Processing Failed","#ef4444");

    }

}

// =====================================================
// PART 2 STARTS FROM HERE
// =====================================================

// =====================================================
// GENERATE EXECUTIVE SUMMARY
// =====================================================

async function generateSummary() {
    console.log("generateSummary() called");

    // Show loading in AI Response
    answer.innerHTML = `
    <div class="ai-response">
        <div class="loader"></div>
        <h2>Generating Executive Summary...</h2>
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

                question: "Generate a complete executive summary of all uploaded PDF documents."

            })

        });

        const data = await response.json();

        console.log("SUMMARY RESPONSE:", data);

        // -------------------------------
        // Display in AI Response panel
        // -------------------------------
        console.log("Answer:", data.answer);
        console.log("Summary:", data.summary);
        const summary = data.summary || data.answer;
        displayAnswer(summary);
        const summaryBox = document.getElementById("summaryBox");
        if (summaryBox) {
            summaryBox.innerHTML = `
            <div class="answer-text">
            ${marked.parse(summary)}
        </div>
        `;
    }

        
        

        // -------------------------------
        // Display retrieved sources
        // -------------------------------
        displaySources(data.sources);

        scrollToAnswer();

        // -------------------------------
        // Save in chat history
        // -------------------------------
        chatHistory.push({

            question: "Executive Summary",

            answer: data.answer

        });

        updateHistory();

        showToast("Executive Summary Generated", "#22c55e");

    }

    catch (err) {

        console.log(err);

        answer.innerHTML = `
        <div class="ai-response">
            <h2 style="color:red">
                Unable to Generate Executive Summary
            </h2>
        </div>
        `;

        // Also update Executive Summary box
        const summaryBox = document.getElementById("summaryBox");

        if (summaryBox) {

            summaryBox.innerHTML = `
                <div class="welcome-box">
                    <h3>Summary Generation Failed</h3>
                    <p>Please try uploading the documents again.</p>
                </div>
            `;

        }

        showToast("Summary Generation Failed", "#ef4444");

    }

}

// =====================================================
// ASK BUTTON
// =====================================================

if (askBtn) {

    askBtn.addEventListener("click", askAI);

}

// =====================================================
// ENTER KEY
// =====================================================

if (question) {

    question.addEventListener("keydown", (e) => {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            askAI();

        }

    });

}

// =====================================================
// ASK AI
// =====================================================

async function askAI() {

    const q = question.value.trim();

    if (q === "") {

        showToast("Please enter a question", "#ef4444");

        return;

    }

    askBtn.disabled = true;

    answer.innerHTML = `
    <div class="ai-response">

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

        console.log("CHAT RESPONSE:", data);
        console.log("SOURCES:", data.sources);

        askBtn.disabled = false;

        if (data.status !== "success") {

            answer.innerHTML = `
            <div class="welcome-box">

                <h2 style="color:red">

                    ${data.answer}

                </h2>

            </div>
            `;

            showToast("Answer Not Found", "#ef4444");

            return;

        }

        displayAnswer(data.answer);

        displaySources(data.sources);
        scrollToAnswer();

        chatHistory.push({

            question: q,

            answer: data.answer

        });

        updateHistory();

        showToast("Answer Generated", "#22c55e");

    }

    catch (err) {
        console.log(err);
        askBtn.disabled = false;
        answer.innerHTML = `
        <div class="ai-response">

            <h2 style="color:red">

                Unable to connect to backend

            </h2>

            <p>

                Please check whether FastAPI is running.

            </p>

        </div>
        `;

        showToast("Backend Connection Failed", "#ef4444");

    }

}

// =====================================================
// PART 3 STARTS FROM HERE
// =====================================================
// =====================================================
// DISPLAY AI ANSWER
// =====================================================

function displayAnswer(text) {

    if (!text || !text.trim()) {

        answer.innerHTML = `
        <div class="ai-response">
            <h2>No Answer Found</h2>
        </div>`;
        return;
    }

    // Normalize line endings
    text = text.replace(/\r\n/g, "\n");

    // Remove multiple blank lines
    text = text.replace(/\n{3,}/g, "\n\n");

    // Remove blank line between heading and list
    text = text.replace(/(#{1,6}[^\n]*)\n+\-/g, "$1\n-");

    // Remove blank line between two headings
    text = text.replace(/(#{1,6}[^\n]*)\n+(#{1,6})/g, "$1\n$2");

    // Render markdown
    let html = marked.parse(text);

    // Remove empty paragraphs generated by marked
    html = html.replace(/<p>\s*<\/p>/g, "");

    // Remove paragraph containing only &nbsp;
    html = html.replace(/<p>(&nbsp;|\s)*<\/p>/g, "");

    answer.innerHTML = `
    <div class="answer-text">
        ${html}
    </div>`;
}
// =====================================================
// RECENT QUESTIONS
// =====================================================

function updateHistory() {

    const history = document.getElementById("chatHistory");

    if (!history) return;

    history.innerHTML = "";

    if (chatHistory.length === 0) {

        history.innerHTML = `

        <div class="source-card">

            No Recent Questions

        </div>

        `;

        return;

    }

    [...chatHistory]

        .reverse()

        .forEach(chat => {

            history.innerHTML += `

            <div class="source-card">

                <strong>Question</strong>

                <hr>

                ${chat.question}

            </div>

            `;

        });

}

// =====================================================
// DISPLAY SOURCES
// =====================================================

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

    list.forEach(item => {

        const score = item.score || 0;
        const percent = (score * 100).toFixed(1);

        let color = "#ef4444";
        if(score >= 0.80){
        color="#22c55e";
        }
        else if(score >=0.50){

        color="#f59e0b";
        }

        const div = document.createElement("div");

        div.className = "source-card";

        div.innerHTML = `
        <h4>📄 ${item.source || "Unknown PDF"}</h4>
        <p><strong>Page:</strong> ${item.page ?? "-"}</p>
        <p><strong>Chunk:</strong> ${item.chunk || item.chunk_id || "-"}</p>
        <p>
        <strong>Confidence:</strong>
        <span style="color:${color};font-weight:bold;">
         ${percent}%
        </span>
        </p>
        <hr>
        <div class="source-preview">
        ${item.preview || item.text || "No Preview Available"}
        </div>
        `;
        

        sources.appendChild(div);

    });

}

// =====================================================
// PART 4 STARTS HERE
// =====================================================
// =====================================================
// COPY ANSWER
// =====================================================

if (copyBtn) {

    copyBtn.addEventListener("click", copyAnswer);

}

function copyAnswer() {

    const textElement = answer.querySelector(".answer-text");

    if (!textElement) {

        showToast("Nothing to Copy", "#ef4444");

        return;

    }

    const text = textElement.innerText.trim();

    navigator.clipboard.writeText(text)
     .then(()=>{
    showToast("Copied Successfully","#22c55e");
    })
    .catch(()=>{

     showToast("Copy Failed","#ef4444");

    });

}

// =====================================================
// DOWNLOAD ANSWER
// =====================================================

if (downloadBtn) {

    downloadBtn.addEventListener("click", downloadAnswer);

}

function downloadAnswer() {

    const textElement = answer.querySelector(".answer-text");

    if (!textElement) {

        showToast("Nothing to Download", "#ef4444");

        return;

    }

    const text = textElement.innerText;

    const blob = new Blob([text], {

        type: "text/plain"

    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "AI_Report.txt";

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);

    showToast("Report Downloaded", "#22c55e");

}

// =====================================================
// CLEAR CHAT
// =====================================================

if (clearBtn) {

    clearBtn.addEventListener("click", clearAll);

}

function clearAll() {

    if (question) {

        question.value = "";

    }

    if (answer) {

        answer.innerHTML = `

        <div class="welcome-box">

            <h2>AI Research Assistant</h2>

            <p>

                Upload PDF documents and ask questions.

            </p>

        </div>

        `;

    }

    if (sources) {

        sources.innerHTML = "";

    }

    chatHistory = [];

    updateHistory();

    showToast("Workspace Cleared", "#2563eb");

}

// =====================================================
// AUTO SCROLL
// =====================================================

function scrollToAnswer() {

    answer.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}

// =====================================================
// ONLINE STATUS
// =====================================================

window.addEventListener("online", () => {

    showToast("Internet Connected", "#22c55e");

});

window.addEventListener("offline", () => {

    showToast("Internet Disconnected", "#ef4444");

});

// =====================================================
// SHORTCUTS
// =====================================================

document.addEventListener("keydown", (e) => {

    // Ctrl + Enter → Ask AI

    if (e.ctrlKey && e.key === "Enter") {

        e.preventDefault();

        askAI();

    }
    if (e.key === "Escape") {

        clearAll();

    }

});

// =====================================================
// WELCOME SCREEN
// =====================================================

if (answer) {

    answer.innerHTML = `

    <div class="welcome-box">

        <h1>🤖 AI Research Assistant</h1>

        <br>

        <p>

            Upload one or more PDF documents to begin.

        </p>

        <br>

        <ul style="text-align:left;display:inline-block;line-height:2;">

            <li>📄 Multi PDF Upload</li>

            <li>🔍 Hybrid Search (BM25 + ChromaDB)</li>

            <li>🧠 AI Question Answering</li>

            <li>📝 Executive Summary</li>

            <li>📌 Source Citation</li>

            <li>📥 Download AI Report</li>

        </ul>

    </div>

    `;

}
updateHistory();

// =====================================================
// END OF SCRIPT
// =====================================================

});