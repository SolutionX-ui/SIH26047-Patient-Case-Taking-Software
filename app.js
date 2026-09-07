const titles = {
    "patient-dashboard": "My Care Dashboard",
    chat: "AI Triage",
    draft: "My Triage Draft",
    "doctor-dashboard": "Clinical Dashboard",
    queue: "Incoming Patients",
    workspace: "Review & Prescription",
    report: "Finalized Report"
};

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
        showView(control.dataset.view);
    });
});

document.querySelector(".composer").addEventListener("submit", (event) => {
    event.preventDefault();
    event.currentTarget.reset();
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