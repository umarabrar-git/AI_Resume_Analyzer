const dashboardPage = document.querySelector("[data-dashboard]");

if (dashboardPage) {
    const createUploadModal = () => {
        const existingModal = document.getElementById("resumeUploadModal");
        if (existingModal) {
            return existingModal;
        }

        const modal = document.createElement("div");
        modal.id = "resumeUploadModal";
        modal.className = "upload-modal";
        modal.innerHTML = `
            <div class="upload-modal__backdrop"></div>
            <div class="upload-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="uploadModalTitle">
                <div class="upload-modal__header">
                    <div>
                        <h3 id="uploadModalTitle">Upload Resume</h3>
                        <p>Upload a PDF or DOCX resume and optionally add a target job description.</p>
                    </div>
                    <button type="button" class="upload-modal__close" aria-label="Close upload modal">×</button>
                </div>
                <form class="upload-modal__form" action="/upload" method="post" enctype="multipart/form-data">
                    <label class="upload-modal__field">
                        <span>Resume file</span>
                        <input type="file" name="resume" accept=".pdf,.doc,.docx" required>
                    </label>
                    <label class="upload-modal__field">
                        <span>Job description (optional)</span>
                        <textarea name="job_description" rows="5" placeholder="Paste the job description to improve analysis..."></textarea>
                    </label>
                    <div class="upload-modal__actions">
                        <button type="button" class="upload-modal__cancel">Cancel</button>
                        <button type="submit" class="upload-modal__submit">Analyze Resume</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
        return modal;
    };

    const openUploadModal = () => {
        const modal = createUploadModal();
        modal.classList.add("is-open");
        document.body.classList.add("upload-modal-open");
        const closeBtn = modal.querySelector(".upload-modal__close");
        closeBtn?.addEventListener("click", closeUploadModal);
        modal.querySelector(".upload-modal__cancel")?.addEventListener("click", closeUploadModal);
        modal.querySelector(".upload-modal__backdrop")?.addEventListener("click", closeUploadModal);
    };

    const closeUploadModal = () => {
        const modal = document.getElementById("resumeUploadModal");
        if (!modal) return;
        modal.classList.remove("is-open");
        document.body.classList.remove("upload-modal-open");
    };

    // Handle upload button clicks
    const uploadBtns = dashboardPage.querySelectorAll('[data-action="upload"]');
    uploadBtns.forEach(btn => {
        btn.addEventListener("click", openUploadModal);
    });

    // Handle create button clicks
    const createBtns = dashboardPage.querySelectorAll('[data-action="create"]');
    createBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            window.location.href = "/resume-creation";
        });
    });

    // Handle report button clicks
    const reportBtns = dashboardPage.querySelectorAll('[data-action="report"]');
    reportBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            window.location.href = "/analysis";
        });
    });

    // Handle match button clicks
    const matchBtns = dashboardPage.querySelectorAll('[data-action="match"]');
    matchBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            window.location.href = "/assistant";
        });
    });

    // Handle resume row actions
    const resumeRows = dashboardPage.querySelectorAll("[data-resume-id]");
    resumeRows.forEach(row => {
        const viewBtn = row.querySelector('[title="View"]');
        const downloadBtn = row.querySelector('[title="Download"]');
        const deleteBtn = row.querySelector('[title="Delete"]');

        if (viewBtn) {
            viewBtn.addEventListener("click", () => {
                const resumeId = row.dataset.resumeId;
                console.log(`View resume ${resumeId}`);
                // TODO: Navigate to resume detail page
            });
        }

        if (downloadBtn) {
            downloadBtn.addEventListener("click", () => {
                const resumeId = row.dataset.resumeId;
                console.log(`Download resume ${resumeId}`);
                // TODO: Download resume
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener("click", () => {
                const resumeId = row.dataset.resumeId;
                console.log(`Delete resume ${resumeId}`);
                // TODO: Show delete confirmation modal
            });
        }
    });

    // Add animation on load
    setTimeout(() => {
        dashboardPage.style.opacity = "1";
    }, 100);
}
