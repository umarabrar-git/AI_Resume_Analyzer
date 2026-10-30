export function renderCarePathTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
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
  [["LinkedIn", personal.linkedin], ["Professional Profile", personal.professional_profile],
    ["Portfolio", personal.portfolio], ["Website", personal.website]].forEach(([label, url]) => {
      if (url) contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) => '<div class="cp-skill"><strong>' +
      e(category) + "</strong><span>" + e(values.join(", ")) + "</span></div>").join("")
    : (Array.isArray(data.skills) && data.skills.length
      ? '<div class="cp-skill"><span>' + e(data.skills.join(", ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="cp-entry"><div class="cp-entry-head"><h3>' + e(item.title || "") +
    '</h3><time>' + dates(item) + '</time></div><div class="cp-subtitle">' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets || []).length || (item.achievements || []).length
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>").join("");
  const education = (data.education || []).map((item) =>
    '<article class="cp-entry"><div class="cp-entry-head"><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><time>' +
    dates(item) + "</time></div><div class=\"cp-subtitle\">" + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant training:</strong> " + e(item.coursework) + "</p>" : "") +
    "</article>").join("");
  const certifications = (data.certifications || []).map((item) =>
    '<div class="cp-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<small>" + e(item.issue_date) + "</small>" : "") + "</div>").join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="cp-entry"><h3>' + e(item.name || "") +
    (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length
      ? '<p class="cp-tools"><strong>Tools:</strong> ' + e(item.technologies.join(", ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    "</article>").join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="cp-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>").join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => section("custom", e(item.title || "Additional Experience"),
      item.items.map((entry) => '<article class="cp-entry"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + "</h3>" +
        (entry.date ? "<time>" + e(entry.date) + "</time>" : "") +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join(""))).join("");
  return '<div class="resume-template-carepath"><header class="cp-header">' +
    '<div class="cp-brand"><span aria-hidden="true">+</span><small>CARE DELIVERY · PATIENT ADVOCACY</small></div>' +
    "<h1>" + e(personal.full_name || "Your Name") + "</h1><p>" +
    e(personal.professional_title || "Healthcare Professional") + '</p><div class="cp-contact">' +
    contact.join('<span aria-hidden="true">•</span>') + "</div></header><div class=\"cp-grid\"><aside class=\"cp-rail\">" +
    section("skills", "Clinical Competencies", skills) +
    section("certifications", "Licensure & Credentials", certifications) +
    section("languages", "Languages", languages) +
    '<div class="cp-rail-note"><strong>CARE PRINCIPLE</strong><span>Evidence-led practice. Compassionate outcomes.</span></div>' +
    '</aside><main class="cp-main">' +
    section("summary", "Professional Profile", data.summary ? '<p class="cp-summary">' + e(data.summary) + "</p>" : "") +
    section("experience", "Patient Care Experience", experience) +
    section("education", "Education & Clinical Training", education) +
    section("projects", "Quality Improvement & Research", projects) +
    section("career_objective", "Career Direction", data.career_objective ? "<p>" + e(data.career_objective) + "</p>" : "") +
    custom + "</main></div></div>";
}
