/**
 * Reports Route
 * ---------------------------------------------------------
 * Handles:
 * - Report download modal
 * - PDF / DOCX selection
 * - Report template selection
 * - Premium template UI state
 * - Export request
 * - File download
 * - Loading / error states
 * - Modal accessibility
 * ---------------------------------------------------------
 */

const ReportsRoute = (() => {
  "use strict";

  /* =====================================================
       Configuration
    ===================================================== */

  const CONFIG = {
    exportEndpoints: {
      pdf: "/reports/export/pdf",
      docx: "/reports/export/docx",
    },

    defaultFormat: "pdf",

    defaultTemplate: "professional",

    premiumTemplates: ["executive", "ai_insights", "career_analytics"],
  };

  /* =====================================================
       DOM References
    ===================================================== */

  let elements = {};

  /* =====================================================
       State
    ===================================================== */

  const state = {
    format: CONFIG.defaultFormat,
    template: CONFIG.defaultTemplate,
    isGenerating: false,
  };

  /* =====================================================
       Initialization
    ===================================================== */

  function init() {
    cacheElements();

    /*
     * ReportsRoute is only initialized on pages
     * where the download button exists.
     */
    if (!elements.downloadButton) {
      return;
    }

    bindEvents();
    initializeSelections();
    updateFormatCards();
    updateTemplateCards();
  }

  /* =====================================================
       DOM Cache
    ===================================================== */

  function cacheElements() {
    elements = {
      /* Main download button */
      downloadButton: document.getElementById("downloadReportBtn"),

      /* Modal */
      modal: document.getElementById("reportDownloadModal"),

      /* Modal overlay */
      overlay: document.querySelector(
        "#reportDownloadModal .report-download-overlay",
      ),

      /* Modal controls */
      closeButton: document.getElementById("closeReportDownload"),

      cancelButton: document.getElementById("cancelReportDownload"),

      generateButton: document.getElementById("generateReportDownload"),

      /* Format inputs */
      formatInputs: document.querySelectorAll('input[name="report_format"]'),

      /* Template inputs */
      templateInputs: document.querySelectorAll(
        'input[name="report_template"]',
      ),

      /* Format cards */
      formatCards: document.querySelectorAll(".format-card"),

      /* Template cards */
      templateCards: document.querySelectorAll(".report-template-card"),
    };
  }

  /* =====================================================
       Event Binding
    ===================================================== */

  function bindEvents() {
    /* -----------------------------------------------
       Open modal
    ------------------------------------------------ */

    elements.downloadButton?.addEventListener("click", openModal);

    /* -----------------------------------------------
       Close modal
    ------------------------------------------------ */

    elements.closeButton?.addEventListener("click", closeModal);

    elements.cancelButton?.addEventListener("click", closeModal);

    elements.overlay?.addEventListener("click", closeModal);

    /* -----------------------------------------------
       Keyboard
    ------------------------------------------------ */

    document.addEventListener("keydown", handleKeyboard);

    /* -----------------------------------------------
       Format selection
    ------------------------------------------------ */

    elements.formatInputs?.forEach((input) => {
      input.addEventListener("change", handleFormatChange);
    });

    /* -----------------------------------------------
       Template selection
    ------------------------------------------------ */

    elements.templateInputs?.forEach((input) => {
      input.addEventListener("change", handleTemplateChange);
    });

    /* -----------------------------------------------
       Generate report
    ------------------------------------------------ */

    elements.generateButton?.addEventListener("click", handleGenerate);
  }

  /* =====================================================
       Initial Selection
    ===================================================== */

  function initializeSelections() {
    const selectedFormat = document.querySelector(
      'input[name="report_format"]:checked',
    );

    const selectedTemplate = document.querySelector(
      'input[name="report_template"]:checked',
    );

    if (selectedFormat && isValidFormat(selectedFormat.value)) {
      state.format = selectedFormat.value;
    }

    if (selectedTemplate?.value) {
      state.template = selectedTemplate.value;
    }
  }

  /* =====================================================
       Modal
    ===================================================== */

  function openModal() {
    if (!elements.modal) {
      return;
    }

    /*
     * Do not allow the modal to be reopened while
     * an export request is running.
     */
    if (state.isGenerating) {
      return;
    }

    elements.modal.classList.add("is-open");

    document.body.classList.add("report-modal-open");

    elements.modal.setAttribute("aria-hidden", "false");

    updateFormatCards();
    updateTemplateCards();

    /*
     * Move focus to the close button for accessibility.
     */
    requestAnimationFrame(() => {
      elements.closeButton?.focus();
    });
  }

  function closeModal() {
    if (!elements.modal) {
      return;
    }

    /*
     * Prevent closing while report generation
     * is in progress.
     */
    if (state.isGenerating) {
      return;
    }

    elements.modal.classList.remove("is-open");

    document.body.classList.remove("report-modal-open");

    elements.modal.setAttribute("aria-hidden", "true");
  }

  function handleKeyboard(event) {
    if (event.key !== "Escape") {
      return;
    }

    if (!elements.modal?.classList.contains("is-open")) {
      return;
    }

    closeModal();
  }

  /* =====================================================
       Format Selection
    ===================================================== */

  function handleFormatChange(event) {
    const value = event.target.value;

    if (!value) {
      return;
    }

    if (!isValidFormat(value)) {
      return;
    }

    state.format = value;

    updateFormatCards();
  }

  function updateFormatCards() {
    elements.formatCards?.forEach((card) => {
      const input = card.querySelector('input[name="report_format"]');

      if (!input) {
        return;
      }

      card.classList.toggle("active", input.value === state.format);
    });
  }

  /* =====================================================
       Template Selection
    ===================================================== */

  function handleTemplateChange(event) {
    const value = event.target.value;

    if (!value) {
      return;
    }

    state.template = value;

    updateTemplateCards();
  }

  function updateTemplateCards() {
    elements.templateCards?.forEach((card) => {
      const input = card.querySelector('input[name="report_template"]');

      if (!input) {
        return;
      }

      const isSelected = input.value === state.template;

      card.classList.toggle("active", isSelected);

      /*
       * Keep aria-checked synchronized for
       * custom template-card UIs.
       */
      card.setAttribute("aria-checked", String(isSelected));
    });
  }

  /* =====================================================
       Premium Template Helpers
    ===================================================== */

  function isPremiumTemplate(template) {
    return CONFIG.premiumTemplates.includes(template);
  }

  /* =====================================================
       Generate Report
    ===================================================== */

  async function handleGenerate() {
    if (state.isGenerating) {
      return;
    }

    /* -----------------------------------------------
       Validate format
    ------------------------------------------------ */

    if (!isValidFormat(state.format)) {
      showError("Please select a valid report format.");

      return;
    }

    /* -----------------------------------------------
       Validate template
    ------------------------------------------------ */

    if (!state.template) {
      showError("Please select a report template.");

      return;
    }

    /*
     * Premium information is only used by the UI.
     *
     * IMPORTANT:
     * The frontend does NOT send "premium=true"
     * or "tier=premium".
     *
     * The backend must determine whether the
     * authenticated user has access to the selected
     * premium template.
     */
    const premium = isPremiumTemplate(state.template);

    /*
     * Prevent unused-variable warnings while keeping
     * the helper available for UI logic.
     *
     * Backend authorization remains authoritative.
     */
    void premium;

    try {
      setGeneratingState(true);

      const endpoint = CONFIG.exportEndpoints[state.format];

      /* ---------------------------------------------
         Export request
         --------------------------------------------- */

      const response = await fetch(endpoint, {
        method: "POST",

        credentials: "same-origin",

        headers: {
          Accept: getAcceptHeader(state.format),

          "Content-Type": "application/json",
        },

        /*
         * Only the selected template is sent.
         *
         * Premium authorization is handled by Flask.
         */
        body: JSON.stringify({
          template: state.template,
        }),
      });

      /* ---------------------------------------------
         HTTP error
         --------------------------------------------- */

      if (!response.ok) {
        const message = await extractErrorMessage(response);

        throw new Error(message || "Unable to generate the report.");
      }

      /* ---------------------------------------------
         Convert response to Blob
         --------------------------------------------- */

      const blob = await response.blob();

      if (!blob || blob.size === 0) {
        throw new Error("The generated report is empty.");
      }

      /* ---------------------------------------------
         Get filename
         --------------------------------------------- */

      const filename = getFilenameFromResponse(
        response,
        state.format,
        state.template,
      );

      /* ---------------------------------------------
         Browser download
         --------------------------------------------- */

      downloadBlob(blob, filename);

      /* ---------------------------------------------
         Success notification
         --------------------------------------------- */

      showSuccess("Your report has been generated successfully.");

      /*
       * Close modal shortly after successful
       * download.
       */
      window.setTimeout(() => {
        closeModal();
      }, 900);
    } catch (error) {
      console.error("Report generation failed:", error);

      showError(
        error?.message || "Something went wrong while generating the report.",
      );
    } finally {
      /*
       * Small delay allows the success/error state
       * to remain visible before restoring the button.
       */
      window.setTimeout(() => {
        setGeneratingState(false);
      }, 500);
    }
  }

  /* =====================================================
       Validation
    ===================================================== */

  function isValidFormat(format) {
    return Object.prototype.hasOwnProperty.call(CONFIG.exportEndpoints, format);
  }

  /* =====================================================
       Loading State
    ===================================================== */

  function setGeneratingState(isGenerating) {
    state.isGenerating = isGenerating;

    if (!elements.generateButton) {
      return;
    }

    if (isGenerating) {
      elements.generateButton.disabled = true;

      /*
       * Save the original button HTML only once.
       */
      if (!elements.generateButton.dataset.originalHtml) {
        elements.generateButton.dataset.originalHtml =
          elements.generateButton.innerHTML;
      }

      elements.generateButton.innerHTML = `
        <span
          class="spinner-border spinner-border-sm me-2"
          role="status"
          aria-hidden="true">
        </span>
        Generating Report...
      `;

      elements.modal?.classList.add("is-generating");
    } else {
      elements.generateButton.disabled = false;

      const original = elements.generateButton.dataset.originalHtml;

      if (original) {
        elements.generateButton.innerHTML = original;

        delete elements.generateButton.dataset.originalHtml;
      }

      elements.modal?.classList.remove("is-generating");
    }
  }

  /* =====================================================
       Response Headers
    ===================================================== */

  function getAcceptHeader(format) {
    if (format === "pdf") {
      return "application/pdf";
    }

    if (format === "docx") {
      return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
    }

    return "*/*";
  }

  /* =====================================================
       Filename
    ===================================================== */

  function getFilenameFromResponse(response, format, template) {
    const contentDisposition = response.headers.get("Content-Disposition");

    if (contentDisposition) {
      /*
       * RFC 5987 / RFC 6266 style:
       *
       * filename*=UTF-8''example.pdf
       */
      const encodedMatch = contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/i,
      );

      if (encodedMatch?.[1]) {
        try {
          return decodeURIComponent(encodedMatch[1]);
        } catch (error) {
          console.warn("Could not decode filename:", error);
        }
      }

      /*
       * Standard:
       *
       * filename="example.pdf"
       */
      const normalMatch = contentDisposition.match(/filename="?([^"]+)"?/i);

      if (normalMatch?.[1]) {
        return normalMatch[1];
      }
    }

    return createFallbackFilename(format, template);
  }

  function createFallbackFilename(format, template) {
    const extension = format === "docx" ? "docx" : "pdf";

    const safeTemplate = String(template || "report")
      .replace(/[^a-z0-9-_]/gi, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "")
      .toLowerCase();

    return `resume-analysis-${safeTemplate || "report"}.${extension}`;
  }

  /* =====================================================
       File Download
    ===================================================== */

  function downloadBlob(blob, filename) {
    const objectUrl = URL.createObjectURL(blob);

    const anchor = document.createElement("a");

    anchor.href = objectUrl;

    anchor.download = filename;

    anchor.style.display = "none";

    document.body.appendChild(anchor);

    anchor.click();

    anchor.remove();

    /*
     * Give the browser time to start the download
     * before releasing the object URL.
     */
    window.setTimeout(() => {
      URL.revokeObjectURL(objectUrl);
    }, 1000);
  }

  /* =====================================================
       Error Handling
    ===================================================== */

  async function extractErrorMessage(response) {
    const contentType = response.headers.get("Content-Type") || "";

    try {
      /* ---------------------------------------------
         JSON error
         --------------------------------------------- */

      if (contentType.includes("application/json")) {
        const data = await response.json();

        return data?.message || data?.error || data?.detail || null;
      }

      /* ---------------------------------------------
         Plain text error
         --------------------------------------------- */

      const text = await response.text();

      return text?.trim() || null;
    } catch (error) {
      console.error("Could not read export error:", error);

      return null;
    }
  }

  /* =====================================================
       UI Notifications
    ===================================================== */

  function showError(message) {
    showNotification(message, "error");
  }

  function showSuccess(message) {
    showNotification(message, "success");
  }

  function showNotification(message, type) {
    /*
     * Remove previous report notifications.
     */
    document
      .querySelectorAll(".report-export-notification")
      .forEach((notification) => {
        notification.remove();
      });

    /* -----------------------------------------------
       Create notification
       ----------------------------------------------- */

    const notification = document.createElement("div");

    notification.className = `report-export-notification ${type}`;

    /* -----------------------------------------------
       Icon
       ----------------------------------------------- */

    const icon =
      type === "success"
        ? "bi-check-circle-fill"
        : "bi-exclamation-circle-fill";

    /*
     * Message is escaped before inserting it
     * into innerHTML.
     */
    notification.innerHTML = `
      <i
        class="bi ${icon}"
        aria-hidden="true">
      </i>

      <span>
        ${escapeHtml(message)}
      </span>
    `;

    /* -----------------------------------------------
       Add to document
       ----------------------------------------------- */

    document.body.appendChild(notification);

    /*
     * Trigger CSS transition.
     */
    window.setTimeout(() => {
      notification.classList.add("is-visible");
    }, 10);

    /* -----------------------------------------------
       Remove notification
       ----------------------------------------------- */

    window.setTimeout(
      () => {
        notification.classList.remove("is-visible");

        window.setTimeout(() => {
          notification.remove();
        }, 250);
      },
      type === "success" ? 3000 : 5000,
    );
  }

  /* =====================================================
       HTML Safety
    ===================================================== */

  function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = String(value ?? "");

    return div.innerHTML;
  }

  /* =====================================================
       Public API
    ===================================================== */

  return {
    init,
    openModal,
    closeModal,
  };
})();

/* =========================================================
   Bootstrap
   ========================================================= */

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    ReportsRoute.init();
  });
} else {
  ReportsRoute.init();
}
