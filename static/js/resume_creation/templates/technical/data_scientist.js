export function renderDataScientistTemplate(content, escapeHtml) {
  const fallbackEscape = (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(Array.isArray(data.hidden_sections) ? data.hidden_sections : []);
  const list = (value) => Array.isArray(value) ? value : [];
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return start || end ? e(start) + (start && end ? " – " : "") + e(end) : "";
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, body, className = "") => body
    ? '<section class="' + e(className) + '" data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + body + "</section>"
    : "";
  const contact = [];
  [personal.email, personal.phone, personal.location].filter(Boolean).forEach((value) => contact.push(e(value)));
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio]].forEach(([label, value]) => {
    const url = safeUrl(value);
    if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const categories = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skillMarkup = categories.length
    ? categories.map(([category, values]) =>
      '<div class="ds-skill-group"><strong>' + e(category) + '</strong><ul class="ds-skill-tags">' +
      values.map((skill) => "<li>" + e(skill) + "</li>").join("") + "</ul></div>"
    ).join("")
    : list(data.skills).length
      ? '<ul class="ds-skill-tags">' + list(data.skills).map((skill) => "<li>" + e(skill) + "</li>").join("") + "</ul>"
      : "";
  const experience = list(data.experience).map((item) =>
    '<article class="ds-entry"><div class="ds-entry-heading"><div><h3>' + e(item.title || "") +
    '</h3><p class="ds-meta">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><p class="ds-date">' + dates(item) + "</p></div>" +
    (item.summary ? "<p>" + e(item.summary) + "</p>" : "") +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? "<p><strong>Impact:</strong> " + item.achievements.map((value) => e(value)).join("; ") + "</p>" : "") +
    "</article>"
  ).join("");
  const projects = list(data.projects).map((item) =>
    '<article class="ds-entry"><div class="ds-entry-heading"><div><h3>' + e(item.name || "") +
    (item.role ? ' <span class="ds-meta">· ' + e(item.role) + "</span>" : "") +
    '</h3></div><p class="ds-date">' + dates(item) + "</p></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="ds-meta"><strong>Stack:</strong> ' + item.technologies.map((value) => e(value)).join(" · ") + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<p><strong>Result:</strong> " + item.achievements.map((value) => e(value)).join("; ") + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View project</a></p>' : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="ds-entry"><div class="ds-entry-heading"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="ds-meta">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    '<p class="ds-date">' + dates(item) + "</p></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="ds-compact"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="ds-compact"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections).filter((item) =>
    list(item.items).length && !hidden.has("custom:" + item.id)
  ).map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
    list(item.items).map((entry) =>
      '<article class="ds-entry"><div class="ds-entry-heading"><h3>' + e(entry.title || "") +
      (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><p class="ds-date">' + e(entry.date || "") + "</p></div>" +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
    ).join(""), "ds-custom-section"
  )).join("");
  const summary = data.summary ? "<p>" + e(data.summary) + "</p>" : "";
  const markup =
    '<div class="resume-template-data-scientist"><header class="ds-header"><div class="ds-identity">' +
    '<p class="ds-eyebrow">DATA SCIENCE · MACHINE LEARNING · ANALYTICS</p><h1>' + e(personal.full_name || "Your Name") +
    '</h1><p class="ds-role">' + e(personal.professional_title || "") + '</p></div><div class="ds-contact">' +
    contact.join("") + "</div></header><div class=\"ds-body\"><aside class=\"ds-sidebar\">" +
    section("skills", "Technical Toolkit", skillMarkup) +
    section("certifications", "Certifications", certifications) +
    section("languages", "Languages", languages) +
    '</aside><main class="ds-main">' +
    section("summary", "Professional Summary", summary) +
    section("experience", "Experience", experience) +
    section("projects", "Selected Data Projects", projects) +
    section("education", "Education", education) + custom +
    "</main></div></div>";
  const root = document.createElement("div");
  root.innerHTML = markup;
  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  const sections = Array.from(root.querySelectorAll("[data-section]"));
  order.forEach((key) => {
    const node = sections.find((candidate) => candidate.dataset.section === key);
    if (node && node.parentElement) node.parentElement.appendChild(node);
  });
  return root.firstElementChild.outerHTML;
}
