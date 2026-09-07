const titles = {
    "patient-dashboard": "My Care Dashboard",
    chat: "AI Triage",
    draft: "My Triage Draft",
    "doctor-dashboard": "Clinical Dashboard",
    queue: "Incoming Patients",
    workspace: "Review & Prescription",
    report: "Finalized Report"
};

const API_BASE_URL = "http://127.0.0.1:8000";
let currentReportId = null;
const chatTranscript = [
    { role: "assistant", message: "Hello, Alex. I’m here to help prepare your visit for the doctor. To begin, how old are you?", time: "10:21 AM" },
    { role: "patient", message: "I’m 31.", time: "10:22 AM" },
    { role: "assistant", message: "Thank you. Could you describe the main symptom you’re experiencing today?", time: "10:22 AM" },
    { role: "patient", message: "I’ve had a persistent sore throat and a mild fever.", time: "10:23 AM" },
    { role: "assistant", message: "I’m sorry you’re feeling unwell. How long have these symptoms been present, and are you currently taking any medications?", time: "10:24 AM" }
];

function addMessage(message, role) {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${role}`;
    messageElement.textContent = message;
    document.querySelector(".messages").append(messageElement);
    messageElement.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function updateDraft(draft) {
    const values = document.querySelectorAll("#draft .detail-grid strong");
    values[0].textContent = draft.primary_symptoms.join(", ");
    values[1].textContent = draft.duration;
    values[2].textContent = draft.current_medications.join(", ");
    values[3].textContent = draft.allergies;
}

function updateFinalReport(report) {
    const section = report.doctor_section;
    const reportElement = document.querySelector("#report");
    reportElement.querySelector("[data-report-status]").textContent = "Finalized";
    reportElement.querySelector("[data-report-issued]").textContent = `Issued ${new Date(report.timestamps.finalized_at).toLocaleDateString()}`;
    reportElement.querySelector("[data-report-diagnosis]").textContent = section.diagnosis;

    const prescriptionBody = reportElement.querySelector("[data-report-prescriptions]");
    prescriptionBody.innerHTML = section.prescriptions.map((prescription) => `
        <tr>
            <td><b>${prescription.medication}</b></td>
            <td>${prescription.dosage}</td>
            <td>${prescription.frequency}</td>
            <td>${prescription.duration}</td>
        </tr>
    `).join("");
    reportElement.querySelector("[data-report-lifestyle]").textContent = section.lifestyle_suggestions;
    reportElement.querySelector("[data-report-follow-up]").textContent = section.follow_up_required
        ? `Follow-up recommended in ${section.follow_up_days} days. This report has been reviewed and finalized by your clinician.`
        : "No follow-up was requested. This report has been reviewed and finalized by your clinician.";
}

function showView(id) {
    document.querySelectorAll(".view").forEach((view) => {
        view.classList.toggle("active", view.id === id);
    });

    document.querySelectorAll(".nav-link").forEach((link) => {
        link.classList.toggle("active", link.dataset.view === id);
    });

    document.getElementById("page-title").textContent = titles[id];

    const isDoctorView = ["doctor-dashboard", "queue", "workspace"].includes(id);

    document.getElementById("profile-label").innerHTML = isDoctorView
        ? "Doctor view <b>PS</b>"
        : "Patient view <b>AM</b>";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

document.querySelectorAll("[data-view]").forEach((control) => {
    control.addEventListener("click", () => {
        if (control.dataset.view === "report" && !currentReportId) {
            alert("The final report will be available after the doctor finalizes your draft.");
            return;
        }
        showView(control.dataset.view);
    });
});

document.querySelector(".composer").addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = event.currentTarget.querySelector("input");
    const message = input.value.trim();

    if (!message) return;

    chatTranscript.push({ role: "patient", message, time: new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) });
    addMessage(message, "patient");
    input.value = "";

    const sendButton = event.currentTarget.querySelector("button");
    sendButton.disabled = true;
    sendButton.textContent = "Preparing…";

    try {
        const response = await fetch(`${API_BASE_URL}/api/reports/generate-draft`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ patient_id: "PT-240819", chat_transcript: chatTranscript })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || "Unable to create the draft");

        currentReportId = result.report_id;
        updateDraft(result.ai_draft);
        showView("draft");
    } catch (error) {
        addMessage(`Unable to prepare your draft: ${error.message}`, "bot");
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send ↑";
    }
});

document.getElementById("add-med").addEventListener("click", () => {
    const row = document.createElement("div");

    row.className = "med-row";

    row.innerHTML = `
    <input aria-label="Medication name" placeholder="Medication name">
    <input aria-label="Dosage" placeholder="Dosage">
    <input aria-label="Frequency" placeholder="Frequency">
    <input aria-label="Duration" placeholder="Duration">
  `;

    document.getElementById("prescriptions").append(row);
});

document.querySelector("#workspace .clinical-form .button").addEventListener("click", async (event) => {
    if (!currentReportId) {
        alert("No draft report is loaded. Create a triage draft first.");
        return;
    }

    const form = document.querySelector("#workspace .clinical-form");
    const textareas = form.querySelectorAll("textarea");
    const prescriptions = [...form.querySelectorAll(".med-row")].map((row) => {
        const fields = row.querySelectorAll("input");
        return {
            medication: fields[0].value.trim(),
            dosage: fields[1].value.trim(),
            frequency: fields[2].value.trim(),
            duration: fields[3].value.trim()
        };
    });
    const followUp = document.getElementById("follow");
    const finalizeButton = event.currentTarget;

    finalizeButton.disabled = true;
    finalizeButton.textContent = "Finalizing...";

    try {
        const response = await fetch(`${API_BASE_URL}/api/reports/${currentReportId}/finalize`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                diagnosis: textareas[0].value.trim(),
                prescriptions,
                lifestyle_suggestions: textareas[1].value.trim(),
                follow_up_required: followUp.checked,
                follow_up_days: followUp.checked ? Number(form.querySelector(".days").value) : null
            })
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || "Unable to finalize the report");
        updateFinalReport(result.report);
        showView("report");
    } catch (error) {
        alert(error.message);
    } finally {
        finalizeButton.disabled = false;
        finalizeButton.textContent = "Finalize & Send to Patient →";
    }
});