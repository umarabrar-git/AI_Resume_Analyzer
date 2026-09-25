/* =========================================================
   DASHBOARD INTERACTIONS
   ========================================================= */

const dashboardPage = document.querySelector("[data-dashboard]");

if (dashboardPage) {
  /* =====================================================
       GLOBAL HELPERS
       ===================================================== */

  const allowedFileExtensions = [".pdf", ".doc", ".docx"];

  const allowedMimeTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ];

  const formatFileSize = (bytes) => {
    if (!bytes || bytes <= 0) {
      return "0 KB";
    }

    const kb = bytes / 1024;

    if (kb < 1024) {
      return `${kb.toFixed(1)} KB`;
    }

    const mb = kb / 1024;

    if (mb < 1024) {
      return `${mb.toFixed(1)} MB`;
    }

    const gb = mb / 1024;

    return `${gb.toFixed(1)} GB`;
  };

  const isValidResumeFile = (file) => {
    if (!file) {
      return false;
    }

    const fileName = file.name.toLowerCase();

    const hasValidExtension = allowedFileExtensions.some((extension) =>
      fileName.endsWith(extension),
    );

    const hasValidMimeType = !file.type || allowedMimeTypes.includes(file.type);

    return hasValidExtension && hasValidMimeType;
  };

  /* =====================================================
       CREATE UPLOAD MODAL
       ===================================================== */

  const createUploadModal = () => {
    const existingModal = document.getElementById("resumeUploadModal");

    if (existingModal) {
      return existingModal;
    }

    const modal = document.createElement("div");

    modal.id = "resumeUploadModal";

    modal.className = "upload-modal";

    modal.innerHTML = `

            <!-- =========================================
                 BACKDROP
                 ========================================= -->

            <div
                class="upload-modal__backdrop"
                data-upload-backdrop
            ></div>


            <!-- =========================================
                 DIALOG
                 ========================================= -->

            <div
                class="upload-modal__dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby="uploadModalTitle"
            >


                <!-- =====================================
                     HEADER
                     ===================================== -->

                <div class="upload-modal__header">

                    <div class="upload-modal__heading">

                        <h3 id="uploadModalTitle">
                            Upload Resume
                        </h3>

                        <p>
                            Upload a PDF or DOCX resume
                            and optionally add a target
                            job description.
                        </p>

                    </div>


                    <button
                        type="button"
                        class="upload-modal__close"
                        data-upload-close
                        aria-label="Close upload modal"
                    >
                        ×
                    </button>

                </div>


                <!-- =====================================
                     FORM
                     ===================================== -->

                <form
                    class="upload-modal__form"
                    action="/upload"
                    method="post"
                    enctype="multipart/form-data"
                    novalidate
                >


                    <!-- =================================
                         RESUME FIELD
                         ================================= -->

                    <div
                        class="
                            upload-modal__field
                            upload-modal__field--resume
                        "
                    >

                        <div
                            class="
                                upload-modal__label-row
                            "
                        >

                            <label
                                for="resumeUploadInput"
                            >
                                Resume file
                                <span>*</span>
                            </label>


                            <small>
                                Supported formats
                            </small>

                        </div>


                        <!-- =============================
                             DROPZONE
                             ============================= -->

                        <div
                            class="file-dropzone"
                            data-file-dropzone
                            tabindex="0"
                            role="button"
                            aria-label="Upload resume file"
                        >


                            <!-- =========================
                                 DROPZONE CONTENT
                                 ========================= -->

                            <div
                                class="
                                    file-dropzone__placeholder
                                "
                                data-file-placeholder
                            >

                                <div
                                    class="
                                        file-dropzone__icon
                                    "
                                    aria-hidden="true"
                                >
                                    ↑
                                </div>


                                <div
                                    class="
                                        file-dropzone__text
                                    "
                                >

                                    <strong
                                        data-file-name
                                    >
                                        Drag & drop your
                                        resume here
                                    </strong>


                                    <span
                                        data-file-status
                                    >
                                        or click to browse
                                        files
                                    </span>

                                </div>

                            </div>


                            <!-- =========================
                                 CHOOSE FILE
                                 ========================= -->

                            <label
                                class="
                                    file-dropzone__button
                                "
                                for="resumeUploadInput"
                            >

                                <span>
                                    Choose File
                                </span>


                                <input
                                    id="resumeUploadInput"
                                    type="file"
                                    name="resume"
                                    accept=".pdf,.doc,.docx"
                                    required
                                    data-resume-input
                                >

                            </label>


                        </div>


                        <!-- =============================
                             ERROR MESSAGE
                             ============================= -->

                        <small
                            class="
                                upload-modal__file-error
                            "
                            data-file-error
                            aria-live="polite"
                        ></small>


                    </div>


                    <!-- =================================
                         JOB DESCRIPTION
                         ================================= -->

                    <div
                        class="
                            upload-modal__field
                            upload-modal__field--job
                        "
                    >

                        <div
                            class="
                                upload-modal__label-row
                            "
                        >

                            <label
                                for="uploadJobDescription"
                            >
                                Job description
                                <em>
                                    (optional)
                                </em>
                            </label>

                        </div>


                        <textarea
                            id="uploadJobDescription"
                            name="job_description"
                            rows="5"
                            placeholder="Paste the job description here to enable job matching and skill gap analysis..."
                        ></textarea>

                    </div>


                    <!-- =================================
                         ACTION BUTTONS
                         ================================= -->

                    <div
                        class="
                            upload-modal__actions
                        "
                    >

                        <button
                            type="button"
                            class="
                                upload-modal__cancel
                            "
                            data-upload-cancel
                        >
                            Cancel
                        </button>


                        <button
                            type="submit"
                            class="
                                upload-modal__submit
                            "
                            data-upload-submit
                        >

                            <span
                                aria-hidden="true"
                            >
                                ⚙
                            </span>

                            <span>
                                Analyze Resume
                            </span>

                            <span
                                aria-hidden="true"
                            >
                                →
                            </span>

                        </button>

                    </div>


                </form>

            </div>
        `;

    document.body.appendChild(modal);

    /* =================================================
           CACHE ELEMENTS
           ================================================= */

    const form = modal.querySelector(".upload-modal__form");

    const fileInput = modal.querySelector("[data-resume-input]");

    const dropzone = modal.querySelector("[data-file-dropzone]");

    const fileName = modal.querySelector("[data-file-name]");

    const fileStatus = modal.querySelector("[data-file-status]");

    const fileError = modal.querySelector("[data-file-error]");

    const submitButton = modal.querySelector("[data-upload-submit]");

    const submitButtonText = submitButton?.querySelectorAll("span");

    /* =================================================
           CLEAR FILE ERROR
           ================================================= */

    const clearFileError = () => {
      if (fileError) {
        fileError.textContent = "";
      }

      dropzone?.classList.remove("has-error");
    };

    /* =================================================
           SHOW FILE ERROR
           ================================================= */

    const showFileError = (message) => {
      if (fileError) {
        fileError.textContent = message;
      }

      dropzone?.classList.add("has-error");
    };

    /* =================================================
           RESET FILE UI
           ================================================= */

    const resetFileUI = () => {
      if (fileName) {
        fileName.textContent = "Drag & drop your resume here";
      }

      if (fileStatus) {
        fileStatus.textContent = "or click to browse files";
      }

      dropzone?.classList.remove("has-file");

      dropzone?.classList.remove("is-dragging");

      dropzone?.classList.remove("has-error");

      clearFileError();
    };

    /* =================================================
           UPDATE FILE UI
           ================================================= */

    const updateFileUI = (file) => {
      clearFileError();

      if (!file) {
        resetFileUI();
        return;
      }

      /* ---------------------------------------------
               Validate file
               --------------------------------------------- */

      if (!isValidResumeFile(file)) {
        if (fileInput) {
          fileInput.value = "";
        }

        resetFileUI();

        showFileError("Please select a PDF, DOC or DOCX file.");

        return;
      }

      /* ---------------------------------------------
               Update filename
               --------------------------------------------- */

      if (fileName) {
        fileName.textContent = file.name;
      }

      /* ---------------------------------------------
               Update status
               --------------------------------------------- */

      if (fileStatus) {
        fileStatus.textContent = `${formatFileSize(file.size)} • Ready to analyze`;
      }

      /* ---------------------------------------------
               Active state
               --------------------------------------------- */

      dropzone?.classList.add("has-file");
    };

    /* =================================================
           ASSIGN DROPPED FILE TO INPUT
           ================================================= */

    const assignFileToInput = (file) => {
      if (!fileInput || !file) {
        return false;
      }

      try {
        const dataTransfer = new DataTransfer();

        dataTransfer.items.add(file);

        fileInput.files = dataTransfer.files;

        return true;
      } catch (error) {
        console.warn("Unable to assign dropped file:", error);

        return false;
      }
    };

    /* =================================================
           FILE INPUT CHANGE
           ================================================= */

    fileInput?.addEventListener("change", () => {
      const file = fileInput.files?.[0];

      updateFileUI(file);
    });

    /* =================================================
           DRAG OVER
           ================================================= */

    dropzone?.addEventListener("dragover", (event) => {
      event.preventDefault();

      event.stopPropagation();

      dropzone.classList.add("is-dragging");
    });

    /* =================================================
           DRAG ENTER
           ================================================= */

    dropzone?.addEventListener("dragenter", (event) => {
      event.preventDefault();

      event.stopPropagation();

      dropzone.classList.add("is-dragging");
    });

    /* =================================================
           DRAG LEAVE
           ================================================= */

    dropzone?.addEventListener("dragleave", (event) => {
      event.preventDefault();

      event.stopPropagation();

      if (!dropzone.contains(event.relatedTarget)) {
        dropzone.classList.remove("is-dragging");
      }
    });

    /* =================================================
           DROP
           ================================================= */

    dropzone?.addEventListener("drop", (event) => {
      event.preventDefault();

      event.stopPropagation();

      dropzone.classList.remove("is-dragging");

      const files = event.dataTransfer?.files;

      if (!files || files.length === 0) {
        return;
      }

      const file = files[0];

      const assigned = assignFileToInput(file);

      if (!assigned) {
        showFileError("Unable to select this file. Please use Choose File.");

        return;
      }

      updateFileUI(file);
    });

    /* =================================================
           KEYBOARD SUPPORT
           ================================================= */

    dropzone?.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();

        fileInput?.click();
      }
    });

    /* =================================================
           FORM VALIDATION
           ================================================= */

    form?.addEventListener("submit", (event) => {
      const file = fileInput?.files?.[0];

      clearFileError();

      /* -----------------------------------------
                   No file
                   ----------------------------------------- */

      if (!file) {
        event.preventDefault();

        showFileError("Please select your resume before continuing.");

        dropzone?.focus();

        return;
      }

      /* -----------------------------------------
                   Invalid file
                   ----------------------------------------- */

      if (!isValidResumeFile(file)) {
        event.preventDefault();

        showFileError("Please select a PDF, DOC or DOCX file.");

        return;
      }

      /* -----------------------------------------
                   Submit state
                   ----------------------------------------- */

      if (submitButton) {
        submitButton.disabled = true;

        submitButton.classList.add("is-loading");
      }

      if (submitButtonText?.length) {
        const textSpan = submitButtonText[submitButtonText.length - 2];

        if (textSpan) {
          textSpan.textContent = "Analyzing...";
        }
      }
    });

    /* =================================================
           RETURN MODAL
           ================================================= */

    return modal;
  };

  /* =====================================================
       OPEN UPLOAD MODAL
       ===================================================== */

  const openUploadModal = () => {
    const modal = createUploadModal();

    modal.classList.add("is-open");

    document.body.classList.add("upload-modal-open");

    const fileInput = modal.querySelector("[data-resume-input]");

    /*
     * Small delay allows browser to
     * finish rendering the modal.
     */

    requestAnimationFrame(() => {
      modal.classList.add("is-visible");
    });

    /*
     * Focus the file area.
     */

    const dropzone = modal.querySelector("[data-file-dropzone]");

    dropzone?.focus();

    /*
     * Store modal state.
     */

    modal.dataset.open = "true";
  };

  /* =====================================================
       CLOSE UPLOAD MODAL
       ===================================================== */

  const closeUploadModal = () => {
    const modal = document.getElementById("resumeUploadModal");

    if (!modal) {
      return;
    }

    modal.classList.remove("is-visible");

    modal.classList.remove("is-open");

    modal.dataset.open = "false";

    document.body.classList.remove("upload-modal-open");
  };

  /* =====================================================
       GET UPLOAD BUTTONS
       ===================================================== */

  const uploadBtns = dashboardPage.querySelectorAll('[data-action="upload"]');

  uploadBtns.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      window.location.href = "/analysis?upload=1";
    });
  });

  /* =====================================================
       MODAL EVENT DELEGATION
       ===================================================== */

  document.addEventListener("click", (event) => {
    const target = event.target;

    const modal = document.getElementById("resumeUploadModal");

    if (!modal) {
      return;
    }

    /* ---------------------------------------------
               CLOSE BUTTON
               --------------------------------------------- */

    if (target.closest("[data-upload-close]")) {
      closeUploadModal();

      return;
    }

    /* ---------------------------------------------
               CANCEL BUTTON
               --------------------------------------------- */

    if (target.closest("[data-upload-cancel]")) {
      closeUploadModal();

      return;
    }

    /* ---------------------------------------------
               BACKDROP
               --------------------------------------------- */

    if (target.closest("[data-upload-backdrop]")) {
      closeUploadModal();

      return;
    }
  });

  /* =====================================================
       ESCAPE KEY
       ===================================================== */

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    const modal = document.getElementById("resumeUploadModal");

    if (modal && modal.classList.contains("is-open")) {
      closeUploadModal();
    }
  });

  /* =====================================================
       CREATE RESUME BUTTON
       ===================================================== */

  const createBtns = dashboardPage.querySelectorAll('[data-action="create"]');

  createBtns.forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = "/resume-creation";
    });
  });

  /* =====================================================
       REPORT BUTTON
       ===================================================== */

  const reportBtns = dashboardPage.querySelectorAll('[data-action="report"]');

  reportBtns.forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = "/analysis";
    });
  });

  /* =====================================================
       MATCH BUTTON
       ===================================================== */

  const matchBtns = dashboardPage.querySelectorAll('[data-action="match"]');

  matchBtns.forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = "/assistant";
    });
  });

  /* =====================================================
       RESUME ROW ACTIONS
       ===================================================== */

  const resumeRows = dashboardPage.querySelectorAll("[data-resume-id]");

  resumeRows.forEach((row) => {
    const viewBtn = row.querySelector('[title="View"]');

    const downloadBtn = row.querySelector('[title="Download"]');

    const deleteBtn = row.querySelector('[title="Delete"]');

    /* ---------------------------------------------
           VIEW
           --------------------------------------------- */

    if (viewBtn) {
      viewBtn.addEventListener("click", (event) => {
        event.preventDefault();

        const resumeId = row.dataset.resumeId;

        console.log(`View resume ${resumeId}`);

        /*
         * TODO:
         * Navigate to resume detail page.
         */
      });
    }

    /* ---------------------------------------------
           DOWNLOAD
           --------------------------------------------- */

    if (downloadBtn) {
      downloadBtn.addEventListener("click", (event) => {
        event.preventDefault();

        const resumeId = row.dataset.resumeId;

        console.log(`Download resume ${resumeId}`);

        /*
         * TODO:
         * Implement resume download.
         */
      });
    }

    /* ---------------------------------------------
           DELETE
           --------------------------------------------- */

    if (deleteBtn) {
      deleteBtn.addEventListener("click", (event) => {
        event.preventDefault();

        const resumeId = row.dataset.resumeId;

        console.log(`Delete resume ${resumeId}`);

        /*
         * TODO:
         * Show delete confirmation modal.
         */
      });
    }
  });

  /* =====================================================
       DASHBOARD LOAD ANIMATION
       ===================================================== */

  setTimeout(() => {
    dashboardPage.style.opacity = "1";
  }, 100);

  /* =====================================================
       DEBUG MESSAGE
       ===================================================== */

  console.log("Dashboard interactions initialized successfully.");
}
