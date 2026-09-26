/**
 * Reports Route
 * ---------------------------------------------------------
 * Handles:
 * - Report download modal
 * - PDF / DOCX selection
 * - Report template selection
 * - Premium template state
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

    if (!elements.downloadButton) {
      return;
    }

    bindEvents();
    initializeSelections();
    updateTemplateCards();
    updateFormatCards();
  }

  /* =====================================================
       DOM Cache
       ===================================================== */

  function cacheElements() {
    elements = {
      downloadButton: document.getElementById("downloadReportBtn"),

      modal: document.getElementById("reportDownloadModal"),

      overlay: document.querySelector(
        "#reportDownloadModal .report-download-overlay",
      ),

      closeButton: document.getElementById("closeReportDownload"),

      cancelButton: document.getElementById("cancelReportDownload"),

      generateButton: document.getElementById("generateReportDownload"),

      formatInputs: document.querySelectorAll('input[name="report_format"]'),

      templateInputs: document.querySelectorAll(
        'input[name="report_template"]',
      ),

      formatCards: document.querySelectorAll(".format-card"),

      templateCards: document.querySelectorAll(".report-template-card"),
    };
  }

  /* =====================================================
       Event Binding
       ===================================================== */

  function bindEvents() {
    /* Open modal */
    elements.downloadButton?.addEventListener("click", openModal);

    /* Close modal */
    elements.closeButton?.addEventListener("click", closeModal);

    elements.cancelButton?.addEventListener("click", closeModal);

    elements.overlay?.addEventListener("click", closeModal);

    /* ESC key */
    document.addEventListener("keydown", handleKeyboard);

    /* Format selection */
    elements.formatInputs?.forEach((input) => {
      input.addEventListener("change", handleFormatChange);
    });

    /* Template selection */
    elements.templateInputs?.forEach((input) => {
      input.addEventListener("change", handleTemplateChange);
    });

    /* Generate */
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

    if (selectedFormat) {
      state.format = selectedFormat.value;
    }

    if (selectedTemplate) {
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

    if (state.isGenerating) {
      return;
    }

    elements.modal.classList.add("is-open");

    document.body.classList.add("report-modal-open");

    elements.modal.setAttribute("aria-hidden", "false");

    updateFormatCards();
    updateTemplateCards();

    requestAnimationFrame(() => {
      elements.closeButton?.focus();
    });
  }

  function closeModal() {
    if (!elements.modal) {
      return;
    }

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

    if (!Object.prototype.hasOwnProperty.call(CONFIG.exportEndpoints, value)) {
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

      card.classList.toggle("active", input.value === state.template);
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

    if (!isValidFormat(state.format)) {
      showError("Please select a valid report format.");
      return;
    }

    if (!state.template) {
      showError("Please select a report template.");
      return;
    }

    /*
     * Premium templates are currently allowed through
     * the frontend selection system.
     *
     * Actual premium-access enforcement should happen
     * on the backend when the subscription/entitlement
     * system is implemented.
     */
    const premium = isPremiumTemplate(state.template);

    try {
      setGeneratingState(true);

      const endpoint = CONFIG.exportEndpoints[state.format];

      const url = buildExportUrl(endpoint, state.template, premium);

      const response = await fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: getAcceptHeader(state.format),
        },
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response);

        throw new Error(message || "Unable to generate the report.");
      }

      const blob = await response.blob();

      if (!blob || blob.size === 0) {
        throw new Error("The generated report is empty.");
      }

      const filename = getFilenameFromResponse(
        response,
        state.format,
        state.template,
      );

      downloadBlob(blob, filename);

      showSuccess("Your report has been generated successfully.");

      /*
       * Give the success state a moment before
       * closing the modal.
       */
      window.setTimeout(() => {
        closeModal();
      }, 900);
    } catch (error) {
      console.error("Report generation failed:", error);

      showError(
        error.message || "Something went wrong while generating the report.",
      );
    } finally {
      /*
       * Do not immediately reset if the modal is
       * scheduled to close after a successful download.
       */
      window.setTimeout(() => {
        setGeneratingState(false);
      }, 500);
    }
  }

  /* =====================================================
       Export URL
       ===================================================== */

  function buildExportUrl(endpoint, template, premium) {
    const params = new URLSearchParams();

    params.set("template", template);

    /*
     * This is informational for the backend.
     * Backend must NOT trust this value for premium
     * authorization.
     */
    if (premium) {
      params.set("tier", "premium");
    }

    return `${endpoint}?${params.toString()}`;
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

      elements.generateButton.dataset.originalHtml =
        elements.generateButton.innerHTML;

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

  function getFilenameFromResponse(response, format, template) {
    const contentDisposition = response.headers.get("Content-Disposition");

    if (contentDisposition) {
      /*
       * Supports:
       * filename="example.pdf"
       * filename*=UTF-8''example.pdf
       */

      const encodedMatch = contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/i,
      );

      if (encodedMatch?.[1]) {
        return decodeURIComponent(encodedMatch[1]);
      }

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
      .toLowerCase();

    return `resume-analysis-${safeTemplate}.${extension}`;
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
      if (contentType.includes("application/json")) {
        const data = await response.json();

        return data.message || data.error || data.detail || null;
      }

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
     * Remove previous report notification.
     */
    document
      .querySelectorAll(".report-export-notification")
      .forEach((notification) => {
        notification.remove();
      });

    const notification = document.createElement("div");

    notification.className = `report-export-notification ${type}`;

    const icon =
      type === "success"
        ? "bi-check-circle-fill"
        : "bi-exclamation-circle-fill";

    notification.innerHTML = `
            <i class="bi ${icon}"></i>
            <span>${escapeHtml(message)}</span>
        `;

    document.body.appendChild(notification);

    window.setTimeout(() => {
      notification.classList.add("is-visible");
    }, 10);

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
  document.addEventListener("DOMContentLoaded", () => ReportsRoute.init());
} else {
  ReportsRoute.init();
}
