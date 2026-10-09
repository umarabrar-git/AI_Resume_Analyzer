export function renderGlobalProfessionalTemplate(content, escapeHtml) {
  const root = document.createElement("div");
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const p = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return start || end ? e(start) + (start && end ? " – " : "") + e(end) : "";
  };
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const section = (key, html, title) => html
    ? '<section data-section="' + key + '"><h2>' + title + "</h2>" + html + "</section>"
    : "";

  const contact = [p.email, p.phone, p.location].filter(Boolean).map(e);
  [["LinkedIn", p.linkedin], ["Portfolio", p.portfolio], ["Website", p.website], ["GitHub", p.github]]
    .forEach(([label, url]) => {
      if (url) contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) =>
        '<div class="gp-skill-group"><strong>' + e(category) + "</strong>" + e(values.join(", ")) + "</div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
        ? '<div class="gp-skill-group">' + e(data.skills.join(", ")) + "</div>"
        : "");

  const experience = (data.experience || []).map((item) =>
    '<article class="gp-entry"><div class="gp-entry-head"><h3 class="gp-entry-title">' +
    e(item.title || "") + '</h3><span class="gp-entry-date">' + dates(item) +
    '</span></div><div class="gp-entry-subtitle">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets && item.bullets.length) || (item.achievements && item.achievements.length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");

  const education = (data.education || []).map((item) =>
    '<article class="gp-entry"><div class="gp-entry-head"><h3 class="gp-entry-title">' +
    e(item.degree || "") + (item.field_of_study ? " in " + e(item.field_of_study) : "") +
    '</h3><span class="gp-entry-date">' + dates(item) + '</span></div><div class="gp-entry-subtitle">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = (data.projects || []).map((item) =>
    '<article class="gp-entry"><div class="gp-entry-head"><h3 class="gp-entry-title">' +
    e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.technologies && item.technologies.length
      ? '<div class="gp-tech"><strong>Tools / Methods:</strong> ' + e(item.technologies.join(", ")) + "</div>" : "") +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.url ? '<p><a href="' + e(item.url) + '" target="_blank" rel="noopener noreferrer">' + e(item.url) + "</a></p>" : "") +
    "</article>"
  ).join("");

  const certifications = (data.certifications || []).map((item) =>
    '<div class="gp-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " — " + e(item.issuer) : "") +
    (item.issue_date ? " (" + e(item.issue_date) + ")" : "") + "</div>"
  ).join("");

  const languages = (data.languages || []).map((item) =>
    "<span>" + e(item.language || "") + (item.proficiency ? " (" + e(item.proficiency) + ")" : "") + "</span>"
  ).join("");

  const customSections = (data.custom_sections || []).filter((item) => item.items && item.items.length).map((custom) =>
    '<section class="gp-custom"><h2>' + e(custom.title || "Additional Information") + "</h2>" +
    custom.items.map((item) =>
      '<article class="gp-entry"><div class="gp-entry-head"><h3 class="gp-entry-title">' +
      e(item.title || "") + (item.subtitle ? " · " + e(item.subtitle) : "") +
      '</h3><span class="gp-entry-date">' + e(item.date || "") + "</span></div>" +
      (item.description ? "<p>" + e(item.description) + "</p>" : "") +
      (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
      "</article>"
    ).join("") + "</section>"
  ).join("");

  root.innerHTML =
    '<div class="resume-template-global-professional"><header class="gp-header"><h1>' +
    e(p.full_name || "Your Name") + "</h1><p>" + e(p.professional_title || "Professional") +
    "</p><div>" + contact.join("<span>•</span>") + "</div></header><main>" +
    section("summary", data.summary ? '<p class="gp-summary">' + e(data.summary) + "</p>" : "", "Professional Summary") +
    section("skills", skills ? '<div class="gp-skills">' + skills + "</div>" : "", "Core Competencies") +
    section("experience", experience, "Professional Experience") +
    section("education", education, "Education") +
    section("projects", projects, "Selected Projects") +
    section("certifications", certifications, "Certifications & Training") +
    section("languages", languages ? '<div class="gp-languages">' + languages + "</div>" : "", "Languages") +
    section("career_objective", data.career_objective ? '<p class="gp-objective">' + e(data.career_objective) + "</p>" : "", "Career Objective") +
    customSections + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    const body = node.innerHTML.replace(/<h2[^>]*>.*?<\/h2>/, "").trim();
    if (hidden.has(node.dataset.section) || !body) node.classList.add("is-hidden");
  });
  return root.firstElementChild.outerHTML;
}
window.renderGlobalProfessionalTemplate = renderGlobalProfessionalTemplate;