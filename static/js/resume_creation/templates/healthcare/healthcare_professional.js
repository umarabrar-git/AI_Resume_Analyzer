export function renderHealthcareProfessionalTemplate(content, escapeHtml) {
  const root = document.createElement("div");
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);

  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    if (!start && !end) return "";
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const section = (key, html, title) => html
    ? '<section data-section="' + key + '"><h2>' + title + "</h2>" + html + "</section>"
    : "";

  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Professional Profile", personal.professional_profile],
    ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, url]) => {
      if (url) contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) =>
        '<div class="hp-skill-group"><strong>' + e(category) + "</strong>" + e(values.join(", ")) + "</div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
        ? '<div class="hp-skill-group">' + e(data.skills.join(", ")) + "</div>"
        : "");

  const experience = (data.experience || []).map((item) =>
    '<article class="hp-entry"><div class="hp-entry-head"><h3 class="hp-entry-title">' +
    e(item.title || "") + '</h3><span class="hp-entry-date">' + dates(item) +
    '</span></div><div class="hp-entry-subtitle">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets && item.bullets.length) || (item.achievements && item.achievements.length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");

  const education = (data.education || []).map((item) =>
    '<article class="hp-entry"><div class="hp-entry-head"><h3 class="hp-entry-title">' +
    e(item.degree || "") + (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><span class="hp-entry-date">' + dates(item) + '</span></div><div class="hp-entry-subtitle">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant training:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = (data.projects || []).map((item) =>
    '<article class="hp-entry"><div class="hp-entry-head"><h3 class="hp-entry-title">' +
    e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.technologies && item.technologies.length
      ? '<div class="hp-tech"><strong>Methods / Tools:</strong> ' + e(item.technologies.join(", ")) + "</div>" : "") +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.url ? '<p><a href="' + e(item.url) + '" target="_blank" rel="noopener noreferrer">' + e(item.url) + "</a></p>" : "") +
    "</article>"
  ).join("");

  const certifications = (data.certifications || []).map((item) =>
    '<div class="hp-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " — " + e(item.issuer) : "") +
    (item.issue_date ? " (" + e(item.issue_date) + ")" : "") +
    (item.credential_id ? " · Credential ID: " + e(item.credential_id) : "") + "</div>"
  ).join("");

  const languages = (data.languages || []).map((item) =>
    "<span>" + e(item.language || "") + (item.proficiency ? " (" + e(item.proficiency) + ")" : "") + "</span>"
  ).join("");

  const customSections = (data.custom_sections || [])
    .filter((custom) => Array.isArray(custom.items) && custom.items.length)
    .map((custom) =>
      '<section class="hp-custom"><h2>' + e(custom.title || "Additional Clinical Experience") + "</h2>" +
      custom.items.map((item) =>
        '<article class="hp-entry"><div class="hp-entry-head"><h3 class="hp-entry-title">' +
        e(item.title || "") + (item.subtitle ? " · " + e(item.subtitle) : "") +
        '</h3><span class="hp-entry-date">' + e(item.date || "") + "</span></div>" +
        (item.description ? "<p>" + e(item.description) + "</p>" : "") +
        (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
        "</article>"
      ).join("") + "</section>"
    ).join("");

  root.innerHTML =
    '<div class="resume-template-healthcare-professional"><header class="hp-header">' +
    '<div class="hp-header-mark" aria-hidden="true">+</div><div class="hp-header-main"><h1>' +
    e(personal.full_name || "Your Name") + "</h1><p>" + e(personal.professional_title || "Healthcare Professional") +
    "</p><div>" + contact.join("<span>•</span>") + "</div></div></header><main>" +
    section("summary", data.summary ? '<p class="hp-summary">' + e(data.summary) + "</p>" : "", "Professional Profile") +
    section("skills", skills ? '<div class="hp-skills">' + skills + "</div>" : "", "Clinical & Professional Competencies") +
    section("experience", experience, "Clinical & Professional Experience") +
    section("education", education, "Education & Training") +
    section("certifications", certifications, "Licensure & Certifications") +
    section("projects", projects, "Research & Selected Projects") +
    section("languages", languages ? '<div class="hp-languages">' + languages + "</div>" : "", "Languages") +
    section("career_objective", data.career_objective ? '<p class="hp-objective">' + e(data.career_objective) + "</p>" : "", "Career Objective") +
    customSections + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    const body = node.innerHTML.replace(/<h2[^>]*>.*?<\/h2>/, "").trim();
    if (hidden.has(node.dataset.section) || !body) node.classList.add("is-hidden");
  });

  return root.firstElementChild.outerHTML;
}
window.renderHealthcareProfessionalTemplate = renderHealthcareProfessionalTemplate;