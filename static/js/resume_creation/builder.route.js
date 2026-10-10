import { renderModernEditorialTemplate } from "./templates/professional/modern_editorial.js";
const root = document.querySelector("[data-resume-builder]");

if (!root) {
  // Not on resume builder page.
} else {
  const apiBase = "/resume-creation/api/resumes";

  const state = {
    resumes: [],
    activeResumeId: null,
    templateCatalog: [],
    saveTimer: null,
    savePromise: Promise.resolve(),
    editRevision: 0,
    isHydrating: false,
    lastAiRequest: null,
    lastAiContent: "",
    selectedExperienceIndex: 0,
    selectedProjectIndex: 0,
    versions: [],
    latestIntelligence: null,
  };

  const elements = {
    saveStatus: document.getElementById("saveStatus"),
    manualSaveBtn: document.getElementById("manualSaveBtn"),
    saveVersionBtn: document.getElementById("saveVersionBtn"),
    downloadPdfBtn: document.getElementById("downloadPdfBtn"),
    downloadDocxBtn: document.getElementById("downloadDocxBtn"),
    resumePicker: document.getElementById("resumePicker"),
    createScratchBtn: document.getElementById("createScratchBtn"),
    createFromAnalysisBtn: document.getElementById("createFromAnalysisBtn"),
    createFromProfileBtn: document.getElementById("createFromProfileBtn"),
    resumeUpload: document.getElementById("resumeUpload"),
    importResumeBtn: document.getElementById("importResumeBtn"),
    duplicateResumeBtn: document.getElementById("duplicateResumeBtn"),
    deleteResumeBtn: document.getElementById("deleteResumeBtn"),
    resumeTitle: document.getElementById("resumeTitle"),
    targetRole: document.getElementById("targetRole"),
    templateSelect: document.getElementById("templateSelect"),
    sectionOrderList: document.getElementById("sectionOrderList"),

    piFullName: document.getElementById("piFullName"),
    piProfessionalTitle: document.getElementById("piProfessionalTitle"),
    piEmail: document.getElementById("piEmail"),
    piPhone: document.getElementById("piPhone"),
    piLocation: document.getElementById("piLocation"),
    piLinkedin: document.getElementById("piLinkedin"),
    piGithub: document.getElementById("piGithub"),
    piPortfolio: document.getElementById("piPortfolio"),
    piProfilePhoto: document.getElementById("piProfilePhoto"),

    summaryInput: document.getElementById("summaryInput"),
    summaryLengthHint: document.getElementById("summaryLengthHint"),
    careerObjectiveInput: document.getElementById("careerObjectiveInput"),

    experienceList: document.getElementById("experienceList"),
    educationList: document.getElementById("educationList"),
    projectList: document.getElementById("projectList"),
    certificationList: document.getElementById("certificationList"),
    languageList: document.getElementById("languageList"),
    customSectionList: document.getElementById("customSectionList"),

    addExperienceBtn: document.getElementById("addExperienceBtn"),
    addEducationBtn: document.getElementById("addEducationBtn"),
    addProjectBtn: document.getElementById("addProjectBtn"),
    addCertificationBtn: document.getElementById("addCertificationBtn"),
    addLanguageBtn: document.getElementById("addLanguageBtn"),
    addCustomSectionBtn: document.getElementById("addCustomSectionBtn"),
    customSectionType: document.getElementById("customSectionType"),

    skillInput: document.getElementById("skillInput"),
    skillCategorySelect: document.getElementById("skillCategorySelect"),
    addSkillBtn: document.getElementById("addSkillBtn"),
    skillsList: document.getElementById("skillsList"),

    resumePreview: document.getElementById("resumePreview"),
    completenessBadge: document.getElementById("completenessBadge"),
    contentQualityBadge: document.getElementById("contentQualityBadge"),
    atsReadinessBadge: document.getElementById("atsReadinessBadge"),

    jobDescriptionInput: document.getElementById("jobDescriptionInput"),
    analyzeResumeBtn: document.getElementById("analyzeResumeBtn"),
    atsOutput: document.getElementById("atsOutput"),
    intelligenceMetrics: document.getElementById("intelligenceMetrics"),
    recommendationList: document.getElementById("recommendationList"),
    keywordGapList: document.getElementById("keywordGapList"),
    skillSuggestionList: document.getElementById("skillSuggestionList"),

    aiGenerateSummaryBtn: document.getElementById("aiGenerateSummaryBtn"),
    aiGenerateObjectiveBtn: document.getElementById("aiGenerateObjectiveBtn"),
    aiRewriteSummaryBtn: document.getElementById("aiRewriteSummaryBtn"),
    aiConciseSummaryBtn: document.getElementById("aiConciseSummaryBtn"),
    aiGenerateExperienceBulletsBtn: document.getElementById(
      "aiGenerateExperienceBulletsBtn",
    ),
    aiImproveExperienceBtn: document.getElementById("aiImproveExperienceBtn"),
    aiImproveProjectBtn: document.getElementById("aiImproveProjectBtn"),
    aiTailorResumeBtn: document.getElementById("aiTailorResumeBtn"),
    aiOutput: document.getElementById("aiOutput"),
    assistantPrompt: document.getElementById("assistantPrompt"),
    askAssistantBtn: document.getElementById("askAssistantBtn"),
    applyAiOutputBtn: document.getElementById("applyAiOutputBtn"),
    rejectAiOutputBtn: document.getElementById("rejectAiOutputBtn"),
    refreshVersionsBtn: document.getElementById("refreshVersionsBtn"),
    versionHistoryList: document.getElementById("versionHistoryList"),
  };

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": root.dataset.csrfToken,
        ...(options.headers || {}),
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      const error = new Error(data.error || "Request failed.");
      error.code = data.code || "request_failed";
      throw error;
    }
    return data;
  }

  function getActiveResume() {
    return (
      state.resumes.find((resume) => resume.id === state.activeResumeId) || null
    );
  }

  function ensureContent(content) {
    const flatSkills = Array.isArray(content.skills) ? content.skills : [];
    const categorizedSkills =
      content.skills_by_category &&
      typeof content.skills_by_category === "object"
        ? content.skills_by_category
        : flatSkills.length
          ? { Other: flatSkills }
          : {};
    const categorySkills = Object.values(categorizedSkills).flat();
    return {
      personal_information: {
        full_name: "",
        professional_title: "",
        email: "",
        phone: "",
        location: "",
        linkedin: "",
        github: "",
        portfolio: "",
        profile_photo: "",
        ...(content.personal_information || {}),
      },
      summary: content.summary || "",
      career_objective: content.career_objective || "",
      experience: Array.isArray(content.experience) ? content.experience : [],
      education: Array.isArray(content.education) ? content.education : [],
      skills: flatSkills.length ? flatSkills : categorySkills,
      skills_by_category: categorizedSkills,
      projects: Array.isArray(content.projects) ? content.projects : [],
      certifications: Array.isArray(content.certifications)
        ? content.certifications
        : [],
      languages: Array.isArray(content.languages) ? content.languages : [],
      custom_sections: Array.isArray(content.custom_sections)
        ? content.custom_sections
        : [],
      hidden_sections: Array.isArray(content.hidden_sections)
        ? content.hidden_sections
        : [],
      section_order: Array.isArray(content.section_order)
        ? content.section_order
        : [
            "personal_information",
            "summary",
            "experience",
            "education",
            "skills",
            "projects",
            "certifications",
            "languages",
          ],
    };
  }

  function updateActiveContent(mutator) {
    const resume = getActiveResume();
    if (!resume) return;
    resume.content = ensureContent(resume.content || {});
    mutator(resume.content);
    state.editRevision += 1;
    state.latestIntelligence = null;
    renderBuilder();
    queueAutosave();
  }

  function setSaveStatus(text, className = "") {
    elements.saveStatus.textContent = text;
    elements.saveStatus.className = `save-status ${className}`.trim();
  }

  function syncTemplateChoices(template) {
    root.querySelectorAll("[data-template-choice]").forEach((choice) => {
      const selected = choice.dataset.templateChoice === template;
      choice.classList.toggle("is-selected", selected);
      choice.setAttribute("aria-pressed", String(selected));
    });
  }

  function renderTemplateAvailability() {
    const catalog = state.templateCatalog || [];
    const previous = elements.templateSelect.value;
    elements.templateSelect.replaceChildren();
    catalog.forEach((template) => {
      const option = document.createElement("option");
      option.value = template.id;
      option.textContent = `${template.label}${template.available ? "" : " (Pro)"}`;
      option.disabled = !template.available;
      elements.templateSelect.append(option);
    });
    if (
      catalog.some((template) => template.id === previous && template.available)
    ) {
      elements.templateSelect.value = previous;
    }

    root.querySelectorAll("[data-template-choice]").forEach((choice) => {
      const template = catalog.find(
        (item) => item.id === choice.dataset.templateChoice,
      );
      if (!template) return;
      choice.disabled = !template.available;
      choice.setAttribute("aria-disabled", String(!template.available));
      const title = choice.querySelector("strong");
      const subtitle = choice.querySelector("small");
      if (title) title.textContent = template.label;
      if (subtitle)
        subtitle.textContent = template.available
          ? template.layout
          : "Pro template";
    });
  }

  function computeLocalCompleteness(content) {
    const personal = content.personal_information || {};
    const checks = [
      Boolean(personal.full_name),
      Boolean(personal.email),
      Boolean(personal.phone),
      Boolean(content.summary),
      Boolean(content.experience && content.experience.length),
      Boolean(content.education && content.education.length),
      Boolean(content.skills && content.skills.length),
      Boolean(content.projects && content.projects.length),
    ];
    const score = Math.round(
      (checks.filter(Boolean).length / checks.length) * 100,
    );
    return score;
  }

  async function loadResumes() {
    setSaveStatus("Loading...", "is-loading");
    const data = await apiRequest(apiBase);
    state.resumes = Array.isArray(data.resumes) ? data.resumes : [];
    state.templateCatalog = Array.isArray(data.templates) ? data.templates : [];

    if (state.resumes.length === 0) {
      await createResume("scratch");
      return;
    }

    if (
      !state.activeResumeId ||
      !state.resumes.some((resume) => resume.id === state.activeResumeId)
    ) {
      state.activeResumeId = state.resumes[0].id;
    }

    setSaveStatus("Ready");
    renderBuilder();
    await loadVersions();
  }

  async function loadVersions() {
    const resume = getActiveResume();
    if (!resume) {
      state.versions = [];
      renderVersions();
      return;
    }

    try {
      const data = await apiRequest(`${apiBase}/${resume.id}/versions`);
      state.versions = Array.isArray(data.versions) ? data.versions : [];
      renderVersions();
    } catch (error) {
      state.versions = [];
      elements.versionHistoryList.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
    }
  }

  async function saveVersion() {
    const resume = getActiveResume();
    if (!resume) return;
    const note =
      window.prompt("Version note (optional):", "Manual milestone save") || "";

    setSaveStatus("Saving version...", "is-loading");
    await apiRequest(`${apiBase}/${resume.id}/versions`, {
      method: "POST",
      body: JSON.stringify({ note }),
    });
    setSaveStatus("Version saved", "is-success");
    await loadVersions();
  }

  async function restoreVersion(versionId) {
    const resume = getActiveResume();
    if (!resume) return;

    if (
      !window.confirm("Restore this version? Current draft will be replaced.")
    ) {
      return;
    }

    setSaveStatus("Restoring version...", "is-loading");
    const data = await apiRequest(
      `${apiBase}/${resume.id}/versions/${versionId}/restore`,
      {
        method: "POST",
      },
    );
    const index = state.resumes.findIndex((item) => item.id === resume.id);
    if (index >= 0) {
      state.resumes[index] = data.resume;
    }
    setSaveStatus("Version restored", "is-success");
    renderBuilder();
    await loadVersions();
  }

  function downloadExport(format) {
    const resume = getActiveResume();
    if (!resume) return;
    window.location.href = `${apiBase}/${resume.id}/export/${format}`;
  }

  async function createResume(creationMethod) {
    setSaveStatus("Creating...", "is-loading");
    const titles = {
      analysis: "Resume From Analysis",
      profile: "Resume from Profile",
      scratch: "Untitled Resume",
    };
    const payload = {
      creation_method: creationMethod,
      title: titles[creationMethod] || "Untitled Resume",
      target_role: elements.targetRole.value || "",
    };
    const data = await apiRequest(apiBase, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    state.resumes.unshift(data.resume);
    state.activeResumeId = data.resume.id;
    setSaveStatus("Created", "is-success");
    renderBuilder();
  }

  async function importUploadedResume() {
    const file = elements.resumeUpload.files[0];
    if (!file) {
      setSaveStatus("Choose a PDF or DOCX", "is-error");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);
    setSaveStatus("Extracting resume...", "is-loading");

    try {
      const response = await fetch(`${apiBase}/import`, {
        method: "POST",
        headers: { "X-CSRF-Token": root.dataset.csrfToken },
        body: formData,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.success === false) {
        throw new Error(data.error || "Unable to import this resume.");
      }

      state.resumes.unshift(data.resume);
      state.activeResumeId = data.resume.id;
      elements.resumeUpload.value = "";
      setSaveStatus("Imported", "is-success");
      renderBuilder();
      await loadVersions();
    } catch (error) {
      setSaveStatus(error.message || "Import failed", "is-error");
    }
  }

  async function duplicateActiveResume() {
    const resume = getActiveResume();
    if (!resume) return;
    setSaveStatus("Duplicating...", "is-loading");
    const data = await apiRequest(`${apiBase}/${resume.id}/duplicate`, {
      method: "POST",
    });
    state.resumes.unshift(data.resume);
    state.activeResumeId = data.resume.id;
    setSaveStatus("Duplicated", "is-success");
    renderBuilder();
  }

  async function deleteActiveResume() {
    const resume = getActiveResume();
    if (!resume) return;
    if (!window.confirm("Delete this resume? This action cannot be undone.")) {
      return;
    }

    setSaveStatus("Deleting...", "is-loading");
    await apiRequest(`${apiBase}/${resume.id}`, { method: "DELETE" });
    state.resumes = state.resumes.filter((item) => item.id !== resume.id);

    if (state.resumes.length === 0) {
      state.activeResumeId = null;
      await createResume("scratch");
      return;
    }

    state.activeResumeId = state.resumes[0].id;
    setSaveStatus("Deleted", "is-success");
    renderBuilder();
  }

  function saveActiveResume({ autosave }) {
    const resume = getActiveResume();
    if (!resume) return Promise.resolve();
    const resumeId = resume.id;
    const saveRevision = state.editRevision;
    const payload = {
      title: elements.resumeTitle.value,
      target_role: elements.targetRole.value,
      template: elements.templateSelect.value,
      content: JSON.parse(JSON.stringify(ensureContent(resume.content || {}))),
      autosave,
    };

    const saveRequest = async () => {
      setSaveStatus(
        autosave ? "Saving..." : "Saving manually...",
        "is-loading",
      );
      try {
        const currentResume = state.resumes.find(
          (item) => item.id === resumeId,
        );
        if (currentResume && currentResume.updated_at) {
          payload.base_updated_at = currentResume.updated_at;
        }
        const data = await apiRequest(`${apiBase}/${resumeId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
        const index = state.resumes.findIndex((item) => item.id === resumeId);
        if (index >= 0) {
          if (saveRevision === state.editRevision) {
            state.resumes[index] = data.resume;
          } else {
            state.resumes[index].updated_at = data.resume.updated_at;
          }
        }
        if (state.activeResumeId === resumeId) {
          if (saveRevision === state.editRevision)
            setSaveStatus("Saved", "is-success");
          else setSaveStatus("Changes pending...");
        }
        return data;
      } catch (error) {
        if (
          state.activeResumeId === resumeId &&
          saveRevision === state.editRevision
        ) {
          setSaveStatus(
            error.code === "stale_update"
              ? "Conflict: reload before saving"
              : "Save failed",
            "is-error",
          );
        }
        throw error;
      }
    };

    const queuedRequest = state.savePromise.catch(() => {}).then(saveRequest);
    state.savePromise = queuedRequest;
    return queuedRequest;
  }

  function queueAutosave() {
    if (state.isHydrating) {
      return;
    }

    setSaveStatus("Changes pending...");
    window.clearTimeout(state.saveTimer);
    state.saveTimer = window.setTimeout(async () => {
      try {
        await saveActiveResume({ autosave: true });
      } catch (error) {
        console.error(error);
      }
    }, 1200);
  }

  async function runAtsAnalysis() {
    const resume = getActiveResume();
    if (!resume) return;

    elements.atsOutput.innerHTML = "<p>Analyzing...</p>";
    elements.intelligenceMetrics.innerHTML = "";
    elements.recommendationList.innerHTML = "";
    elements.keywordGapList.innerHTML = "";
    elements.skillSuggestionList.innerHTML = "";

    try {
      const data = await apiRequest(`${apiBase}/${resume.id}/analyze`, {
        method: "POST",
        body: JSON.stringify({
          job_description: elements.jobDescriptionInput.value,
        }),
      });

      const ats = data.ats || {};
      const intelligence = data.intelligence || {};
      state.latestIntelligence = intelligence;
      const breakdown = ats.breakdown || {};
      const match = data.match || {};

      const readiness = Number(intelligence.readiness_score || 0);
      const semantic = Number(
        intelligence.semantic_score || match.semantic_score || 0,
      );
      const candidateMatch = Number(
        intelligence.candidate_match_score || match.candidate_match_score || 0,
      );
      const highPriority = Number(intelligence.high_priority_count || 0);
      elements.atsReadinessBadge.textContent = `ATS readiness: ${readiness.toFixed(0)}%`;

      elements.intelligenceMetrics.innerHTML = `
                <span class="metric-pill"><strong>Readiness</strong> ${escapeHtml(readiness.toFixed(1))}%</span>
                <span class="metric-pill"><strong>Semantic</strong> ${escapeHtml(semantic.toFixed(1))}%</span>
                <span class="metric-pill"><strong>Candidate Match</strong> ${escapeHtml(candidateMatch.toFixed(1))}%</span>
                <span class="metric-pill is-alert"><strong>High Priority</strong> ${escapeHtml(String(highPriority))}</span>
            `;

      elements.atsOutput.innerHTML = `
                <p><strong>ATS Score:</strong> ${escapeHtml(ats.ats_score || 0)} (${escapeHtml(ats.rating || "")})</p>
                <p><strong>Structure:</strong> ${escapeHtml(breakdown.structure || 0)} | <strong>Content:</strong> ${escapeHtml(breakdown.content || 0)}</p>
                <p><strong>Keywords:</strong> ${escapeHtml(breakdown.keywords || 0)} | <strong>Contact:</strong> ${escapeHtml(breakdown.contact || 0)} | <strong>Readability:</strong> ${escapeHtml(breakdown.readability || 0)}</p>
            `;

      const recommendations = Array.isArray(data.recommendations)
        ? data.recommendations
        : [];
      if (!recommendations.length) {
        elements.recommendationList.innerHTML =
          "<span class='empty-note'>No priority issues detected. Keep refining for role targeting.</span>";
      } else {
        elements.recommendationList.innerHTML = recommendations
          .map((item) => {
            const action = String(item.action || "");
            const priority = String(item.priority || "low");
            return `
                        <article class="recommendation-item priority-${escapeHtml(priority)}">
                            <div class="recommendation-head">
                                <strong>${escapeHtml(item.title || "Recommendation")}</strong>
                                <span class="priority-badge">${escapeHtml(priority.toUpperCase())}</span>
                            </div>
                            <p>${escapeHtml(item.detail || item.message || "")}</p>
                            ${action ? `<button type="button" class="btn btn-sm btn-outline-dark" data-action="run-intelligence-action" data-intelligence-action="${escapeHtml(action)}">Run Action</button>` : ""}
                        </article>
                    `;
          })
          .join("");
      }

      const keywordGaps =
        intelligence.diagnostics &&
        Array.isArray(intelligence.diagnostics.missing_keywords)
          ? intelligence.diagnostics.missing_keywords
          : [];
      if (!keywordGaps.length) {
        elements.keywordGapList.innerHTML =
          "<span class='empty-note'>No major keyword gaps found for this JD.</span>";
      } else {
        elements.keywordGapList.innerHTML = keywordGaps
          .map(
            (keyword) => `
                    <button type="button" class="skill-chip suggestion-chip" data-action="add-suggested-skill" data-skill="${escapeHtml(keyword)}">+ ${escapeHtml(keyword)}</button>
                `,
          )
          .join("");
      }

      const suggestions = Array.isArray(data.skill_suggestions)
        ? data.skill_suggestions
        : [];
      if (!suggestions.length) {
        elements.skillSuggestionList.innerHTML =
          "<span class='empty-note'>No additional suggested skills from this JD.</span>";
      } else {
        elements.skillSuggestionList.innerHTML = suggestions
          .map(
            (item) => `
                    <button type="button" class="skill-chip suggestion-chip" data-suggested-skill="${escapeHtml(item.name)}">
                        + ${escapeHtml(item.name)}
                    </button>
                `,
          )
          .join("");
      }
    } catch (error) {
      state.latestIntelligence = null;
      elements.atsOutput.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
    }
  }

  function runIntelligenceAction(action) {
    const intent = String(action || "")
      .trim()
      .toLowerCase();
    if (!intent) return;

    if (intent === "ai_rewrite_summary") {
      runAiOperation("rewrite_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
      return;
    }

    if (intent === "ai_tailor_resume") {
      runAiOperation("tailor_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
      return;
    }

    if (intent === "add_experience_bullets" || intent === "quantify_bullets") {
      runAiOperation("improve_experience", {
        apply_to: "experience",
        source_type: "experience",
        source_index: state.selectedExperienceIndex,
      });
    }
  }

  async function runAiOperation(operation, extra = {}) {
    const resume = getActiveResume();
    if (!resume) return;

    elements.aiOutput.value = "Generating...";
    elements.applyAiOutputBtn.disabled = true;

    const payload = {
      operation,
      target_role: elements.targetRole.value,
      job_description: elements.jobDescriptionInput.value,
      ...extra,
    };

    try {
      const data = await apiRequest(`${apiBase}/${resume.id}/generate`, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      elements.aiOutput.value = data.content || "";
      state.lastAiContent = data.content || "";

      state.lastAiRequest = {
        ...payload,
        apply_to: extra.apply_to || "",
        source_type: extra.source_type || "",
        source_index: extra.source_index,
      };

      const canApply = [
        "summary",
        "career_objective",
        "experience",
        "project",
      ].includes(state.lastAiRequest.apply_to);
      elements.applyAiOutputBtn.disabled = !canApply;

      if (Array.isArray(data.warnings) && data.warnings.length) {
        elements.aiOutput.value += `\n\nWarnings:\n- ${data.warnings.join("\n- ")}`;
      }
    } catch (error) {
      elements.aiOutput.value = `Error: ${error.message}`;
    }
  }

  async function runResumeAgent() {
    const resume = getActiveResume();
    const message = elements.assistantPrompt.value.trim();
    if (!resume || !message) {
      elements.aiOutput.value = "Enter a question for the Resume Agent.";
      return;
    }

    elements.askAssistantBtn.disabled = true;
    elements.applyAiOutputBtn.disabled = true;
    state.lastAiRequest = null;
    elements.aiOutput.value = "Reviewing the current resume...";
    try {
      const data = await apiRequest(`${apiBase}/${resume.id}/assistant`, {
        method: "POST",
        body: JSON.stringify({
          message,
          job_description: elements.jobDescriptionInput.value,
        }),
      });
      const response = data.response || {};
      elements.aiOutput.value =
        response.content || "The agent returned no suggestions.";
      if (Array.isArray(response.warnings) && response.warnings.length) {
        elements.aiOutput.value += `\n\nNotes:\n- ${response.warnings.join("\n- ")}`;
      }
    } catch (error) {
      elements.aiOutput.value = `Error: ${error.message}`;
    } finally {
      elements.askAssistantBtn.disabled = false;
    }
  }

  function rejectAiOutput() {
    state.lastAiRequest = null;
    state.lastAiContent = "";
    elements.aiOutput.value = "Suggestion rejected.";
    elements.applyAiOutputBtn.disabled = true;
  }

  async function applyLastAiOutput() {
    const resume = getActiveResume();
    if (!resume || !state.lastAiRequest) return;

    const payload = {
      ...state.lastAiRequest,
      apply: true,
      generated_content: state.lastAiContent,
    };

    try {
      const data = await apiRequest(`${apiBase}/${resume.id}/generate`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const index = state.resumes.findIndex((item) => item.id === resume.id);
      if (index >= 0) {
        state.resumes[index] = data.resume;
      }
      state.latestIntelligence = null;
      setSaveStatus("AI changes applied", "is-success");
      renderBuilder();
    } catch (error) {
      setSaveStatus("Apply failed", "is-error");
      elements.aiOutput.value = `Error: ${error.message}`;
    }
  }

  function moveItem(list, index, direction) {
    const target = index + direction;
    if (target < 0 || target >= list.length) {
      return;
    }
    [list[index], list[target]] = [list[target], list[index]];
  }

  function bindStaticEvents() {
    elements.resumePicker.addEventListener("change", () => {
      state.activeResumeId = Number(elements.resumePicker.value);
      renderBuilder();
      loadVersions().catch((error) => console.error(error));
    });

    elements.createScratchBtn.addEventListener("click", async () => {
      try {
        await createResume("scratch");
      } catch (error) {
        setSaveStatus("Create failed", "is-error");
      }
    });

    elements.createFromAnalysisBtn.addEventListener("click", async () => {
      try {
        await createResume("analysis");
      } catch (error) {
        setSaveStatus("Create failed", "is-error");
      }
    });

    elements.createFromProfileBtn.addEventListener("click", async () => {
      try {
        await createResume("profile");
      } catch (error) {
        setSaveStatus("Profile import failed", "is-error");
      }
    });

    elements.importResumeBtn.addEventListener("click", importUploadedResume);

    elements.duplicateResumeBtn.addEventListener("click", async () => {
      try {
        await duplicateActiveResume();
      } catch (error) {
        setSaveStatus("Duplicate failed", "is-error");
      }
    });

    elements.deleteResumeBtn.addEventListener("click", async () => {
      try {
        await deleteActiveResume();
      } catch (error) {
        setSaveStatus("Delete failed", "is-error");
      }
    });

    elements.manualSaveBtn.addEventListener("click", async () => {
      try {
        await saveActiveResume({ autosave: false });
        await loadVersions();
      } catch (error) {
        console.error(error);
      }
    });

    elements.saveVersionBtn.addEventListener("click", async () => {
      try {
        await saveVersion();
      } catch (error) {
        setSaveStatus("Version save failed", "is-error");
      }
    });

    elements.downloadPdfBtn.addEventListener("click", () =>
      downloadExport("pdf"),
    );
    elements.downloadDocxBtn.addEventListener("click", () =>
      downloadExport("docx"),
    );

    root.querySelectorAll(".resume-builder-steps .step").forEach((step) => {
      step.addEventListener("click", (event) => {
        const targetId = step.getAttribute("href")?.replace("#", "");
        if (targetId) {
          const target = document.getElementById(targetId);
          if (target) {
            event.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }
        root.querySelectorAll(".resume-builder-steps .step").forEach((item) => {
          item.classList.remove("active");
          item.removeAttribute("aria-current");
        });
        step.classList.add("active");
        step.setAttribute("aria-current", "step");
      });
    });

    elements.refreshVersionsBtn.addEventListener("click", () => {
      loadVersions().catch((error) => {
        setSaveStatus("Version refresh failed", "is-error");
        console.error(error);
      });
    });

    [
      elements.resumeTitle,
      elements.targetRole,
      elements.piFullName,
      elements.piProfessionalTitle,
      elements.piEmail,
      elements.piPhone,
      elements.piLocation,
      elements.piLinkedin,
      elements.piGithub,
      elements.piPortfolio,
      elements.piProfilePhoto,
      elements.summaryInput,
      elements.careerObjectiveInput,
    ].forEach((input) => {
      input.addEventListener("input", () => {
        if (state.isHydrating) return;
        updateActiveContent((content) => {
          content.personal_information.full_name = elements.piFullName.value;
          content.personal_information.professional_title =
            elements.piProfessionalTitle.value;
          content.personal_information.email = elements.piEmail.value;
          content.personal_information.phone = elements.piPhone.value;
          content.personal_information.location = elements.piLocation.value;
          content.personal_information.linkedin = elements.piLinkedin.value;
          content.personal_information.github = elements.piGithub.value;
          content.personal_information.portfolio = elements.piPortfolio.value;
          content.personal_information.profile_photo =
            elements.piProfilePhoto.value;
          content.summary = elements.summaryInput.value;
          content.career_objective = elements.careerObjectiveInput.value;
        });
      });
    });

    elements.templateSelect.addEventListener("change", () => {
      const resume = getActiveResume();
      if (!resume) return;
      resume.template = elements.templateSelect.value;
      state.editRevision += 1;
      syncTemplateChoices(resume.template);
      renderPreview(ensureContent(resume.content || {}), resume.template);
      queueAutosave();
    });

    root.querySelectorAll("[data-template-choice]").forEach((choice) => {
      choice.addEventListener("click", () => {
        elements.templateSelect.value = choice.dataset.templateChoice;
        elements.templateSelect.dispatchEvent(
          new Event("change", { bubbles: true }),
        );
      });
    });

    elements.addSkillBtn.addEventListener("click", () => {
      const value = elements.skillInput.value.trim();
      if (!value) return;
      updateActiveContent((content) => {
        const existing = new Set(
          (content.skills || []).map((item) => item.toLowerCase()),
        );
        if (!existing.has(value.toLowerCase())) {
          const category = elements.skillCategorySelect.value || "Other";
          content.skills_by_category[category] ||= [];
          content.skills_by_category[category].push(value);
          content.skills = Object.values(content.skills_by_category).flat();
        }
      });
      elements.skillInput.value = "";
    });

    elements.addExperienceBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        content.experience.push({
          title: "",
          company: "",
          location: "",
          start_date: "",
          end_date: "",
          current: false,
          bullets: [],
          achievements: [],
        });
        state.selectedExperienceIndex = content.experience.length - 1;
      });
    });

    elements.addEducationBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        content.education.push({
          degree: "",
          field_of_study: "",
          institution: "",
          location: "",
          start_date: "",
          end_date: "",
          grade: "",
          description: "",
        });
      });
    });

    elements.addProjectBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        content.projects.push({
          name: "",
          role: "",
          description: "",
          technologies: [],
          project_url: "",
          github_url: "",
          start_date: "",
          end_date: "",
        });
        state.selectedProjectIndex = content.projects.length - 1;
      });
    });

    elements.addCertificationBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        content.certifications.push({
          name: "",
          issuer: "",
          issue_date: "",
          expiration_date: "",
          credential_id: "",
          credential_url: "",
        });
      });
    });

    elements.addLanguageBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        content.languages.push({ language: "", proficiency: "" });
      });
    });

    elements.addCustomSectionBtn.addEventListener("click", () => {
      updateActiveContent((content) => {
        const id = `custom-${Date.now()}`;
        content.custom_sections.push({
          id,
          title:
            elements.customSectionType.value === "custom"
              ? "New Custom Section"
              : elements.customSectionType.value,
          items: [],
        });
        content.section_order.push(`custom:${id}`);
      });
    });

    elements.analyzeResumeBtn.addEventListener("click", runAtsAnalysis);

    elements.aiGenerateSummaryBtn.addEventListener("click", () => {
      runAiOperation("generate_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
    });

    elements.aiGenerateObjectiveBtn.addEventListener("click", () => {
      runAiOperation("generate_objective", {
        apply_to: "career_objective",
        source_type: "summary",
      });
    });

    elements.askAssistantBtn.addEventListener("click", runResumeAgent);

    elements.aiRewriteSummaryBtn.addEventListener("click", () => {
      runAiOperation("rewrite_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
    });

    elements.aiConciseSummaryBtn.addEventListener("click", () => {
      runAiOperation("concise_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
    });

    elements.aiImproveExperienceBtn.addEventListener("click", () => {
      runAiOperation("improve_experience", {
        apply_to: "experience",
        source_type: "experience",
        source_index: state.selectedExperienceIndex,
      });
    });

    elements.aiGenerateExperienceBulletsBtn.addEventListener("click", () => {
      runAiOperation("generate_experience_bullets", {
        apply_to: "experience",
        source_type: "experience",
        source_index: state.selectedExperienceIndex,
      });
    });

    elements.aiImproveProjectBtn.addEventListener("click", () => {
      runAiOperation("project_improve", {
        apply_to: "project",
        source_type: "project",
        source_index: state.selectedProjectIndex,
      });
    });

    elements.aiTailorResumeBtn.addEventListener("click", () => {
      runAiOperation("tailor_summary", {
        apply_to: "summary",
        source_type: "summary",
      });
    });

    elements.applyAiOutputBtn.addEventListener("click", applyLastAiOutput);
    elements.rejectAiOutputBtn.addEventListener("click", rejectAiOutput);

    root.addEventListener("click", (event) => {
      const action = event.target.closest("[data-action]");
      if (!action) return;

      const resume = getActiveResume();
      if (!resume) return;
      const content = ensureContent(resume.content || {});

      const section = action.dataset.section;
      const index = Number(action.dataset.index);
      const direction = Number(action.dataset.direction || 0);
      const customIndex = Number(action.dataset.customIndex);
      const itemIndex = Number(action.dataset.itemIndex);

      updateActiveContent((draft) => {
        if (
          action.dataset.action === "remove-item" &&
          Array.isArray(draft[section])
        ) {
          draft[section].splice(index, 1);
        }

        if (
          action.dataset.action === "move-item" &&
          Array.isArray(draft[section])
        ) {
          moveItem(draft[section], index, direction);
        }

        if (action.dataset.action === "select-experience") {
          state.selectedExperienceIndex = index;
        }

        if (action.dataset.action === "select-project") {
          state.selectedProjectIndex = index;
        }

        if (action.dataset.action === "remove-skill") {
          let remainingIndex = index;
          for (const [category, skills] of Object.entries(
            draft.skills_by_category,
          )) {
            if (remainingIndex < skills.length) {
              skills.splice(remainingIndex, 1);
              if (!skills.length) delete draft.skills_by_category[category];
              break;
            }
            remainingIndex -= skills.length;
          }
          draft.skills = Object.values(draft.skills_by_category).flat();
        }

        if (action.dataset.action === "move-skill") {
          moveItem(draft.skills, index, direction);
        }

        if (action.dataset.action === "move-section") {
          moveItem(draft.section_order, index, direction);
        }

        if (action.dataset.action === "toggle-section") {
          const sectionKey = action.dataset.sectionKey;
          const hidden = new Set(draft.hidden_sections || []);
          if (hidden.has(sectionKey)) hidden.delete(sectionKey);
          else hidden.add(sectionKey);
          draft.hidden_sections = [...hidden];
        }

        if (action.dataset.action === "add-custom-item") {
          const sectionEntry = draft.custom_sections[index];
          if (sectionEntry) {
            sectionEntry.items.push({
              title: "",
              subtitle: "",
              date: "",
              description: "",
              bullets: [],
            });
          }
        }

        if (action.dataset.action === "remove-custom-section") {
          const sectionEntry = draft.custom_sections[index];
          if (sectionEntry) {
            draft.custom_sections.splice(index, 1);
            draft.section_order = draft.section_order.filter(
              (key) => key !== `custom:${sectionEntry.id}`,
            );
          }
        }

        if (action.dataset.action === "remove-custom-item") {
          const sectionEntry = draft.custom_sections[customIndex];
          if (sectionEntry && Array.isArray(sectionEntry.items)) {
            sectionEntry.items.splice(itemIndex, 1);
          }
        }

        if (action.dataset.action === "add-suggested-skill") {
          const skill = action.dataset.skill || "";
          if (skill) {
            const existing = new Set(
              (draft.skills || []).map((item) => item.toLowerCase()),
            );
            if (!existing.has(skill.toLowerCase())) {
              draft.skills_by_category.Other ||= [];
              draft.skills_by_category.Other.push(skill);
              draft.skills = Object.values(draft.skills_by_category).flat();
            }
          }
        }

        if (action.dataset.action === "restore-version") {
          const versionId = Number(action.dataset.versionId);
          if (versionId) {
            restoreVersion(versionId).catch((error) => {
              setSaveStatus("Version restore failed", "is-error");
              console.error(error);
            });
          }
        }

        if (action.dataset.action === "run-intelligence-action") {
          runIntelligenceAction(action.dataset.intelligenceAction || "");
        }
      });
    });

    root.addEventListener("input", (event) => {
      const field = event.target.closest("[data-field]");
      if (!field) return;

      const section = field.dataset.section;
      const index = Number(field.dataset.index);
      const key = field.dataset.field;
      const customIndex = Number(field.dataset.customIndex);
      const itemIndex = Number(field.dataset.itemIndex);

      updateActiveContent((content) => {
        if (section === "experience" && content.experience[index]) {
          if (key === "bullets" || key === "achievements") {
            content.experience[index][key] = event.target.value
              .split("\n")
              .map((line) => line.trim())
              .filter(Boolean);
          } else if (key === "current") {
            content.experience[index][key] = Boolean(event.target.checked);
          } else {
            content.experience[index][key] = event.target.value;
          }
        }

        if (section === "education" && content.education[index]) {
          content.education[index][key] = event.target.value;
        }

        if (section === "projects" && content.projects[index]) {
          if (key === "technologies") {
            content.projects[index][key] = event.target.value
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean);
          } else if (key === "achievements") {
            content.projects[index][key] = event.target.value
              .split("\n")
              .map((line) => line.trim())
              .filter(Boolean);
          } else {
            content.projects[index][key] = event.target.value;
          }
        }

        if (section === "certifications" && content.certifications[index]) {
          content.certifications[index][key] = event.target.value;
        }

        if (section === "languages" && content.languages[index]) {
          content.languages[index][key] = event.target.value;
        }

        if (section === "custom_sections" && content.custom_sections[index]) {
          content.custom_sections[index][key] = event.target.value;
        }

        if (
          section === "custom_section_item" &&
          content.custom_sections[customIndex]
        ) {
          const item = content.custom_sections[customIndex].items[itemIndex];
          if (!item) return;
          if (key === "bullets") {
            item[key] = event.target.value
              .split("\n")
              .map((line) => line.trim())
              .filter(Boolean);
          } else {
            item[key] = event.target.value;
          }
        }
      });
    });
  }

  function renderPicker() {
    elements.resumePicker.innerHTML = state.resumes
      .map(
        (resume) =>
          `<option value="${resume.id}">${escapeHtml(resume.title)} (${escapeHtml(resume.template)})</option>`,
      )
      .join("");
    elements.resumePicker.value = String(state.activeResumeId || "");
  }

  function renderVersions() {
    if (!state.versions.length) {
      elements.versionHistoryList.innerHTML =
        "<span class='empty-note'>No saved versions yet.</span>";
      return;
    }

    elements.versionHistoryList.innerHTML = state.versions
      .map(
        (version) => `
            <div class="version-item">
                <div>
                    <strong>${escapeHtml(version.action || "version")}</strong>
                    <div class="version-meta">${escapeHtml(version.note || "No note")}</div>
                    <div class="version-meta">${escapeHtml(version.created_at || "")}</div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-primary" data-action="restore-version" data-version-id="${version.id}">Restore</button>
            </div>
        `,
      )
      .join("");
  }

  function renderSectionOrder(content) {
    const labels = {
      personal_information: "Personal Information",
      summary: "Summary",
      career_objective: "Career Objective",
      experience: "Experience",
      education: "Education",
      skills: "Skills",
      projects: "Projects",
      certifications: "Certifications",
      languages: "Languages",
    };

    elements.sectionOrderList.innerHTML = content.section_order
      .map((key, index) => {
        const custom = key.startsWith("custom:")
          ? content.custom_sections.find((item) => `custom:${item.id}` === key)
              ?.title || "Custom Section"
          : labels[key] || key;
        return `
                <li>
                    <span>${escapeHtml(custom)}</span>
                    <div>
                      ${key === "personal_information" ? "" : `<button type="button" class="btn btn-sm btn-light" data-action="toggle-section" data-section-key="${escapeHtml(key)}">${(content.hidden_sections || []).includes(key) ? "Show" : "Hide"}</button>`}
                        <button type="button" class="btn btn-sm btn-light" data-action="move-section" data-index="${index}" data-direction="-1">↑</button>
                        <button type="button" class="btn btn-sm btn-light" data-action="move-section" data-index="${index}" data-direction="1">↓</button>
                    </div>
                </li>
            `;
      })
      .join("");
  }

  function renderSkills(content) {
    let skillIndex = 0;
    elements.skillsList.innerHTML = Object.entries(
      content.skills_by_category || {},
    )
      .map(
        ([category, skills]) => `
        <div class="skills-category-group">
          <strong>${escapeHtml(category)}</strong>
          <div class="chip-list">
            ${(skills || [])
              .map((skill) => {
                const currentIndex = skillIndex++;
                return `<span class="skill-chip">${escapeHtml(skill)}<button type="button" aria-label="Remove ${escapeHtml(skill)}" data-action="remove-skill" data-index="${currentIndex}">×</button></span>`;
              })
              .join("")}
          </div>
        </div>
      `,
      )
      .join("");
  }

  function renderExperience(content) {
    elements.experienceList.innerHTML = content.experience
      .map(
        (item, index) => `
            <div class="entry-card ${index === state.selectedExperienceIndex ? "is-selected" : ""}">
                <div class="entry-card-actions">
                    <button type="button" class="btn btn-sm btn-light" data-action="select-experience" data-section="experience" data-index="${index}">Use for AI</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="experience" data-index="${index}" data-direction="-1">↑</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="experience" data-index="${index}" data-direction="1">↓</button>
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-item" data-section="experience" data-index="${index}">Delete</button>
                </div>
                <input class="form-control" placeholder="Job Title" value="${escapeHtml(item.title || "")}" data-section="experience" data-index="${index}" data-field="title">
                <input class="form-control mt-2" placeholder="Company" value="${escapeHtml(item.company || "")}" data-section="experience" data-index="${index}" data-field="company">
                <input class="form-control mt-2" placeholder="Location" value="${escapeHtml(item.location || "")}" data-section="experience" data-index="${index}" data-field="location">
                <div class="row g-2 mt-1">
                    <div class="col"><input class="form-control" placeholder="Start Date" value="${escapeHtml(item.start_date || "")}" data-section="experience" data-index="${index}" data-field="start_date"></div>
                    <div class="col"><input class="form-control" placeholder="End Date" value="${escapeHtml(item.end_date || "")}" data-section="experience" data-index="${index}" data-field="end_date"></div>
                </div>
                <label class="form-check mt-2">
                    <input class="form-check-input" type="checkbox" ${item.current ? "checked" : ""} data-section="experience" data-index="${index}" data-field="current">
                    <span class="form-check-label">Currently Working Here</span>
                </label>
                <textarea class="form-control mt-2" rows="4" placeholder="One bullet per line" data-section="experience" data-index="${index}" data-field="bullets">${escapeHtml((item.bullets || []).join("\n"))}</textarea>
                <textarea class="form-control mt-2" rows="3" placeholder="Achievements (one per line; actual evidence only)" data-section="experience" data-index="${index}" data-field="achievements">${escapeHtml((item.achievements || []).join("\n"))}</textarea>
            </div>
        `,
      )
      .join("");
  }

  function renderEducation(content) {
    elements.educationList.innerHTML = content.education
      .map(
        (item, index) => `
                <div class="entry-card">
                <div class="entry-card-actions">
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="education" data-index="${index}" data-direction="-1">↑</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="education" data-index="${index}" data-direction="1">↓</button>
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-item" data-section="education" data-index="${index}">Delete</button>
                </div>
                <input class="form-control" placeholder="Degree" value="${escapeHtml(item.degree || "")}" data-section="education" data-index="${index}" data-field="degree">
                <input class="form-control mt-2" placeholder="Field of Study" value="${escapeHtml(item.field_of_study || "")}" data-section="education" data-index="${index}" data-field="field_of_study">
                <input class="form-control mt-2" placeholder="Institution" value="${escapeHtml(item.institution || "")}" data-section="education" data-index="${index}" data-field="institution">
                <input class="form-control mt-2" placeholder="Location" value="${escapeHtml(item.location || "")}" data-section="education" data-index="${index}" data-field="location">
                <div class="row g-2 mt-1">
                    <div class="col"><input class="form-control" placeholder="Start Date" value="${escapeHtml(item.start_date || "")}" data-section="education" data-index="${index}" data-field="start_date"></div>
                    <div class="col"><input class="form-control" placeholder="Graduation Date" value="${escapeHtml(item.end_date || "")}" data-section="education" data-index="${index}" data-field="end_date"></div>
                </div>
                <input class="form-control mt-2" placeholder="Grade or GPA (optional)" value="${escapeHtml(item.grade || "")}" data-section="education" data-index="${index}" data-field="grade">
                <input class="form-control mt-2" placeholder="Relevant coursework (optional)" value="${escapeHtml(item.coursework || "")}" data-section="education" data-index="${index}" data-field="coursework">
                <textarea class="form-control mt-2" rows="2" placeholder="Academic achievements (optional)" data-section="education" data-index="${index}" data-field="academic_achievements">${escapeHtml(item.academic_achievements || "")}</textarea>
                <textarea class="form-control mt-2" rows="3" placeholder="Description (optional)" data-section="education" data-index="${index}" data-field="description">${escapeHtml(item.description || "")}</textarea>
            </div>
        `,
      )
      .join("");
  }

  function renderProjects(content) {
    elements.projectList.innerHTML = content.projects
      .map(
        (item, index) => `
                <div class="entry-card ${index === state.selectedProjectIndex ? "is-selected" : ""}">
                <div class="entry-card-actions">
                  <button type="button" class="btn btn-sm btn-light" data-action="select-project" data-section="projects" data-index="${index}">Use for AI</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="projects" data-index="${index}" data-direction="-1">↑</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="projects" data-index="${index}" data-direction="1">↓</button>
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-item" data-section="projects" data-index="${index}">Delete</button>
                </div>
                <input class="form-control" placeholder="Project Name" value="${escapeHtml(item.name || "")}" data-section="projects" data-index="${index}" data-field="name">
                <input class="form-control mt-2" placeholder="Role" value="${escapeHtml(item.role || "")}" data-section="projects" data-index="${index}" data-field="role">
                <textarea class="form-control mt-2" rows="3" placeholder="Project Description" data-section="projects" data-index="${index}" data-field="description">${escapeHtml(item.description || "")}</textarea>
                <textarea class="form-control mt-2" rows="2" placeholder="Achievements / results (evidence only)" data-section="projects" data-index="${index}" data-field="achievements">${escapeHtml((item.achievements || []).join("\n"))}</textarea>
                <input class="form-control mt-2" placeholder="Technologies (comma separated)" value="${escapeHtml((item.technologies || []).join(", "))}" data-section="projects" data-index="${index}" data-field="technologies">
                <input class="form-control mt-2" placeholder="Project URL" value="${escapeHtml(item.project_url || "")}" data-section="projects" data-index="${index}" data-field="project_url">
                <input class="form-control mt-2" placeholder="GitHub URL" value="${escapeHtml(item.github_url || "")}" data-section="projects" data-index="${index}" data-field="github_url">
            </div>
        `,
      )
      .join("");
  }

  function renderCertifications(content) {
    elements.certificationList.innerHTML = content.certifications
      .map(
        (item, index) => `
            <div class="entry-card">
                <div class="entry-card-actions">
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="certifications" data-index="${index}" data-direction="-1">↑</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="certifications" data-index="${index}" data-direction="1">↓</button>
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-item" data-section="certifications" data-index="${index}">Delete</button>
                </div>
                <input class="form-control" placeholder="Certification Name" value="${escapeHtml(item.name || "")}" data-section="certifications" data-index="${index}" data-field="name">
                <input class="form-control mt-2" placeholder="Issuing Organization" value="${escapeHtml(item.issuer || "")}" data-section="certifications" data-index="${index}" data-field="issuer">
                <input class="form-control mt-2" placeholder="Issue Date" value="${escapeHtml(item.issue_date || "")}" data-section="certifications" data-index="${index}" data-field="issue_date">
                <input class="form-control mt-2" placeholder="Expiration Date" value="${escapeHtml(item.expiration_date || "")}" data-section="certifications" data-index="${index}" data-field="expiration_date">
                <input class="form-control mt-2" placeholder="Credential ID" value="${escapeHtml(item.credential_id || "")}" data-section="certifications" data-index="${index}" data-field="credential_id">
                <input class="form-control mt-2" placeholder="Credential URL" value="${escapeHtml(item.credential_url || "")}" data-section="certifications" data-index="${index}" data-field="credential_url">
            </div>
        `,
      )
      .join("");
  }

  function renderLanguages(content) {
    const options = [
      "",
      "basic",
      "conversational",
      "professional",
      "fluent",
      "native",
    ];
    elements.languageList.innerHTML = content.languages
      .map(
        (item, index) => `
            <div class="entry-card">
                <div class="entry-card-actions">
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="languages" data-index="${index}" data-direction="-1">↑</button>
                    <button type="button" class="btn btn-sm btn-light" data-action="move-item" data-section="languages" data-index="${index}" data-direction="1">↓</button>
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-item" data-section="languages" data-index="${index}">Delete</button>
                </div>
                <input class="form-control" placeholder="Language" value="${escapeHtml(item.language || "")}" data-section="languages" data-index="${index}" data-field="language">
                <select class="form-select mt-2" data-section="languages" data-index="${index}" data-field="proficiency">
                    ${options.map((option) => `<option value="${option}" ${option === (item.proficiency || "") ? "selected" : ""}>${option || "Select proficiency"}</option>`).join("")}
                </select>
            </div>
        `,
      )
      .join("");
  }

  function renderCustomSections(content) {
    elements.customSectionList.innerHTML = content.custom_sections
      .map(
        (section, index) => `
            <div class="entry-card">
                <div class="entry-card-actions">
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-custom-section" data-index="${index}">Delete Section</button>
                </div>
                <input class="form-control" placeholder="Section Title" value="${escapeHtml(section.title || "")}" data-section="custom_sections" data-index="${index}" data-field="title">
                <button type="button" class="btn btn-sm btn-outline-primary mt-2" data-action="add-custom-item" data-index="${index}">Add Entry</button>
                ${(section.items || [])
                  .map(
                    (item, itemIndex) => `
                    <div class="entry-card mt-2">
                        <div class="entry-card-actions">
                            <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove-custom-item" data-custom-index="${index}" data-item-index="${itemIndex}">Delete Entry</button>
                        </div>
                        <input class="form-control" placeholder="Title" value="${escapeHtml(item.title || "")}" data-section="custom_section_item" data-custom-index="${index}" data-item-index="${itemIndex}" data-field="title">
                        <input class="form-control mt-2" placeholder="Subtitle" value="${escapeHtml(item.subtitle || "")}" data-section="custom_section_item" data-custom-index="${index}" data-item-index="${itemIndex}" data-field="subtitle">
                        <input class="form-control mt-2" placeholder="Date" value="${escapeHtml(item.date || "")}" data-section="custom_section_item" data-custom-index="${index}" data-item-index="${itemIndex}" data-field="date">
                        <textarea class="form-control mt-2" rows="2" placeholder="Description" data-section="custom_section_item" data-custom-index="${index}" data-item-index="${itemIndex}" data-field="description">${escapeHtml(item.description || "")}</textarea>
                        <textarea class="form-control mt-2" rows="2" placeholder="Bullets (one per line)" data-section="custom_section_item" data-custom-index="${index}" data-item-index="${itemIndex}" data-field="bullets">${escapeHtml((item.bullets || []).join("\n"))}</textarea>
                    </div>
                `,
                  )
                  .join("")}
            </div>
        `,
      )
      .join("");
  }

  function renderPreview(content, template) {
    const personal = content.personal_information || {};
    const sections = [];
    const modernSidebarSections = [];
    const modernMainSections = [];

    sections.push(`
            <div class="preview-header">
                <h1>${escapeHtml(personal.full_name || "Your Name")}</h1>
                ${personal.profile_photo ? `<img class="preview-photo" src="${escapeHtml(personal.profile_photo)}" alt="Profile photo">` : ""}
                <p>${escapeHtml(personal.professional_title || "Professional Title")}</p>
                <p>
                    ${escapeHtml(personal.email || "")}
                    ${personal.phone ? ` | ${escapeHtml(personal.phone)}` : ""}
                    ${personal.location ? ` | ${escapeHtml(personal.location)}` : ""}
                </p>
                <p>
                    ${personal.linkedin ? `<a href="${escapeHtml(personal.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>` : ""}
                    ${personal.github ? ` | <a href="${escapeHtml(personal.github)}" target="_blank" rel="noopener">GitHub</a>` : ""}
                    ${personal.portfolio ? ` | <a href="${escapeHtml(personal.portfolio)}" target="_blank" rel="noopener">Portfolio</a>` : ""}
                </p>
            </div>
        `);

    function renderListSection(title, body) {
      if (!body || !body.length) return "";
      return `<section class="preview-section"><h3>${escapeHtml(title)}</h3>${body.join("")}</section>`;
    }

    const order = content.section_order || [];
    const orderMap = {
      summary: () =>
        content.summary
          ? `<section class="preview-section"><h3>Summary</h3><p>${escapeHtml(content.summary)}</p></section>`
          : "",
      career_objective: () =>
        content.career_objective
          ? `<section class="preview-section"><h3>Career Objective</h3><p>${escapeHtml(content.career_objective)}</p></section>`
          : "",
      experience: () =>
        renderListSection(
          "Experience",
          content.experience.map(
            (item) => `
                <article class="preview-item">
                    <div class="preview-item-head"><strong>${escapeHtml(item.title || "")}</strong> - ${escapeHtml(item.company || "")}</div>
                    <div class="preview-date">${escapeHtml(item.start_date || "")} - ${escapeHtml(item.current ? "Present" : item.end_date || "")}</div>
                    <ul>${[...(item.bullets || []), ...(item.achievements || [])].map((bullet) => `<li>${escapeHtml(bullet)}</li>`).join("")}</ul>
                </article>
            `,
          ),
        ),
      education: () =>
        renderListSection(
          "Education",
          content.education.map(
            (item) => `
                <article class="preview-item">
                    <div class="preview-item-head"><strong>${escapeHtml(item.degree || "")}</strong> ${item.field_of_study ? `in ${escapeHtml(item.field_of_study)}` : ""}</div>
                    <div>${escapeHtml(item.institution || "")} ${item.location ? `, ${escapeHtml(item.location)}` : ""}</div>
                    ${item.coursework ? `<p>Relevant coursework: ${escapeHtml(item.coursework)}</p>` : ""}
                    ${item.academic_achievements ? `<p>${escapeHtml(item.academic_achievements)}</p>` : ""}
                </article>
            `,
          ),
        ),
      skills: () =>
        content.skills.length
          ? `<section class="preview-section"><h3>Skills</h3>${Object.entries(
              content.skills_by_category || {},
            )
              .map(
                ([category, skills]) =>
                  `<p><strong>${escapeHtml(category)}:</strong> ${escapeHtml(skills.join(", "))}</p>`,
              )
              .join("")}</section>`
          : "",
      projects: () =>
        renderListSection(
          "Projects",
          content.projects.map(
            (item) => `
                <article class="preview-item">
                    <div class="preview-item-head"><strong>${escapeHtml(item.name || "")}</strong> ${item.role ? `- ${escapeHtml(item.role)}` : ""}</div>
                    <p>${escapeHtml(item.description || "")}</p>
                    <p>${escapeHtml((item.technologies || []).join(", "))}</p>
                    ${(item.achievements || []).map((achievement) => `<p>${escapeHtml(achievement)}</p>`).join("")}
                </article>
            `,
          ),
        ),
      certifications: () =>
        renderListSection(
          "Certifications",
          content.certifications.map(
            (item) => `
                <article class="preview-item">
                    <strong>${escapeHtml(item.name || "")}</strong>
                    <div>${escapeHtml(item.issuer || "")}</div>
                </article>
            `,
          ),
        ),
      languages: () =>
        renderListSection(
          "Languages",
          content.languages.map(
            (item) => `
                <article class="preview-item">${escapeHtml(item.language || "")} ${item.proficiency ? `- ${escapeHtml(item.proficiency)}` : ""}</article>
            `,
          ),
        ),
    };

    const hiddenSections = new Set(content.hidden_sections || []);
    order.forEach((key) => {
      if (hiddenSections.has(key)) return;
      if (orderMap[key]) {
        const html = orderMap[key]();
        if (html) {
          sections.push(html);
          const sidebarSection = [
            "skills",
            "education",
            "certifications",
            "languages",
          ].includes(key);
          (sidebarSection ? modernSidebarSections : modernMainSections).push(
            html,
          );
        }
        return;
      }

      if (key.startsWith("custom:")) {
        const section = content.custom_sections.find(
          (item) => `custom:${item.id}` === key,
        );
        if (!section) return;
        const body = (section.items || []).map(
          (item) => `
                    <article class="preview-item">
                        <div class="preview-item-head"><strong>${escapeHtml(item.title || "")}</strong> ${item.subtitle ? `- ${escapeHtml(item.subtitle)}` : ""}</div>
                        <div>${escapeHtml(item.date || "")}</div>
                        <p>${escapeHtml(item.description || "")}</p>
                        <ul>${(item.bullets || []).map((bullet) => `<li>${escapeHtml(bullet)}</li>`).join("")}</ul>
                    </article>
                `,
        );
        const html = renderListSection(section.title || "Custom Section", body);
        sections.push(html);
        modernMainSections.push(html);
      }
    });

    elements.resumePreview.className = `resume-preview template-${escapeHtml(template || "classic")}`;
    if (template === "modern_editorial") {
      elements.resumePreview.innerHTML = renderModernEditorialTemplate(content, escapeHtml);
      return;
    }
    if (template === "modern") {
      const contactItems = [
        personal.email ? `<p>${escapeHtml(personal.email)}</p>` : "",
        personal.phone ? `<p>${escapeHtml(personal.phone)}</p>` : "",
        personal.location ? `<p>${escapeHtml(personal.location)}</p>` : "",
        personal.linkedin
          ? `<p><a href="${escapeHtml(personal.linkedin)}" target="_blank" rel="noopener">LinkedIn</a></p>`
          : "",
        personal.github
          ? `<p><a href="${escapeHtml(personal.github)}" target="_blank" rel="noopener">GitHub</a></p>`
          : "",
        personal.portfolio
          ? `<p><a href="${escapeHtml(personal.portfolio)}" target="_blank" rel="noopener">Portfolio</a></p>`
          : "",
      ]
        .filter(Boolean)
        .join("");
      elements.resumePreview.innerHTML = `
        <div class="modern-resume">
          <aside class="modern-resume-sidebar">
            ${personal.profile_photo ? `<img class="preview-photo" src="${escapeHtml(personal.profile_photo)}" alt="Profile photo">` : ""}
            <section class="modern-contact"><h3>Contact</h3>${contactItems || "<p>Contact details</p>"}</section>
            ${modernSidebarSections.join("")}
          </aside>
          <div class="modern-resume-main">
            <header class="modern-resume-heading">
              <h1>${escapeHtml(personal.full_name || "Your Name")}</h1>
              <p>${escapeHtml(personal.professional_title || "Professional Title")}</p>
            </header>
            ${modernMainSections.join("")}
          </div>
        </div>
      `;
      return;
    }
    elements.resumePreview.innerHTML = sections.join("");
  }

  function renderBuilder() {
    const resume = getActiveResume();
    if (!resume) return;

    state.isHydrating = true;

    const content = ensureContent(resume.content || {});
    resume.content = content;

    renderPicker();

    elements.resumeTitle.value = resume.title || "";
    elements.targetRole.value = resume.target_role || "";
    elements.templateSelect.value = resume.template || "classic";
    renderTemplateAvailability();
    syncTemplateChoices(elements.templateSelect.value);

    elements.piFullName.value = content.personal_information.full_name || "";
    elements.piProfessionalTitle.value =
      content.personal_information.professional_title || "";
    elements.piEmail.value = content.personal_information.email || "";
    elements.piPhone.value = content.personal_information.phone || "";
    elements.piLocation.value = content.personal_information.location || "";
    elements.piLinkedin.value = content.personal_information.linkedin || "";
    elements.piGithub.value = content.personal_information.github || "";
    elements.piPortfolio.value = content.personal_information.portfolio || "";
    elements.piProfilePhoto.value =
      content.personal_information.profile_photo || "";

    elements.summaryInput.value = content.summary || "";
    elements.summaryLengthHint.textContent = `${content.summary.length} / 1200`;
    elements.careerObjectiveInput.value = content.career_objective || "";

    renderSectionOrder(content);
    renderSkills(content);
    renderExperience(content);
    renderEducation(content);
    renderProjects(content);
    renderCertifications(content);
    renderLanguages(content);
    renderCustomSections(content);
    renderPreview(content, resume.template);

    const score = Number.isFinite(resume.completeness)
      ? resume.completeness
      : computeLocalCompleteness(content);
    elements.completenessBadge.textContent = `Completeness: ${score}%`;
    const experienceBullets = content.experience.some(
      (item) => (item.bullets || []).length > 0,
    );
    const contentChecks = [
      content.summary.trim().length >= 80,
      experienceBullets,
      content.skills.length >= 3,
      content.projects.length > 0,
      Boolean(
        content.personal_information.email &&
        content.personal_information.phone,
      ),
    ];
    const contentQuality = Math.round(
      (contentChecks.filter(Boolean).length / contentChecks.length) * 100,
    );
    elements.contentQualityBadge.textContent = `Content quality: ${contentQuality}%`;
    if (!state.latestIntelligence) {
      elements.atsReadinessBadge.textContent = "ATS readiness: Not checked";
    }

    state.isHydrating = false;
    renderVersions();
  }

  (async function init() {
    bindStaticEvents();
    try {
      await loadResumes();
    } catch (error) {
      setSaveStatus("Load failed", "is-error");
      console.error(error);
    }
  })();
}
