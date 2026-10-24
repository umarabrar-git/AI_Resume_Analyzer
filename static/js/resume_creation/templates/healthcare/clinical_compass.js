export function renderClinicalCompassTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return [start, end].filter(Boolean).map(e).join(" – ");
  };
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section data-section="' + key + '"><h2>' + title + "</h2>" + body + "</section>"
    : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, url]) => {
      if (url) contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) =>
        '<div class="cc-skill-group"><strong>' + e(category) + "</strong><span>" + e(values.join(", ")) + "</span></div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
      ? '<div class="cc-skill-group"><span>' + e(data.skills.join(", ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="cc-entry"><div class="cc-entry-head"><h3>' + e(item.title || "") +
    '</h3><span class="cc-date">' + dates(item) + '</span></div><div class="cc-subtitle">' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets || []).length || (item.achievements || []).length
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="cc-entry"><div class="cc-entry-head"><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><span class="cc-date">' +
    dates(item) + "</span></div><div class=\"cc-subtitle\">" + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant training:</strong> " + e(item.coursework) + "</p>" : "") +
    "</article>"
  ).join("");
  const certifications = (data.certifications || []).map((item) =>
    '<div class="cc-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? '<small>' + e(item.issue_date) + "</small>" : "") + "</div>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="cc-entry"><div class="cc-entry-head"><h3>' + e(item.name || "") +
    (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length
      ? '<p class="cc-methods"><strong>Methods / Tools:</strong> ' + e(item.technologies.join(", ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    "</article>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="cc-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>"
  ).join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => section("custom", e(item.title || "Additional Experience"),
      item.items.map((entry) => '<article class="cc-entry"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + "</h3>" +
        (entry.date ? '<span class="cc-date">' + e(entry.date) + "</span>" : "") +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join(""))).join("");

  return '<div class="resume-template-clinical-compass"><header class="cc-header">' +
    '<div class="cc-kicker">PATIENT CARE · CLINICAL PRACTICE</div><h1>' +
    e(personal.full_name || "Your Name") + "</h1><p>" +
    e(personal.professional_title || "Healthcare Professional") + '</p><div class="cc-contact">' +
    contact.join('<span aria-hidden="true">•</span>') + "</div></header><div class=\"cc-layout\"><aside class=\"cc-rail\">" +
    section("skills", "Clinical Skills", skills) + section("certifications", "Licensure", certifications) +
    section("languages", "Languages", languages) + '</aside><main class="cc-main">' +
    section("summary", "Clinical Profile", data.summary ? '<p class="cc-summary">' + e(data.summary) + "</p>" : "") +
    section("experience", "Clinical Experience", experience) + section("education", "Education & Training", education) +
    section("projects", "Research & Quality Improvement", projects) +
    section("career_objective", "Career Focus", data.career_objective ? "<p>" + e(data.career_objective) + "</p>" : "") +
    custom + "</main></div></div>";
}