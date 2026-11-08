export function renderLegalAssociateTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>' : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  if (personal.linkedin) contact.push('<a href="' + e(personal.linkedin) + '" target="_blank" rel="noopener noreferrer">LinkedIn</a>');
  const bullets = (items) => Array.isArray(items) ? items.filter(Boolean).map(item => '<li>' + e(item) + '</li>').join("") : "";
  const dates = item => [item.start_date || "", item.current ? "Present" : (item.end_date || "")].filter(Boolean).map(e).join(" – ");
  const experience = (data.experience || []).map(item =>
    '<article class="la-entry"><div class="la-entry-head"><h3>' + e(item.title || "") + '</h3><time>' + dates(item) + '</time></div>' +
    '<p class="la-org">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") + '</p>' +
    ((item.bullets || []).length || (item.achievements || []).length ? '<ul>' + bullets([...(item.bullets || []), ...(item.achievements || [])]) + '</ul>' : "") + '</article>'
  ).join("");
  const education = (data.education || []).map(item =>
    '<article class="la-entry"><h3>' + e(item.degree || "") + (item.field_of_study ? " · " + e(item.field_of_study) : "") + '</h3>' +
    '<p class="la-org">' + e(item.institution || "") + '</p>' +
    (item.coursework ? '<p>' + e(item.coursework) + '</p>' : "") + '</article>'
  ).join("");
  const skills = (data.skills_by_category && Object.keys(data.skills_by_category).length)
    ? Object.entries(data.skills_by_category).map(([key, values]) => '<p><strong>' + e(key) + ':</strong> ' + e((values || []).join(", ")) + '</p>').join("")
    : '<p>' + e((data.skills || []).join(" · ")) + '</p>';
  const projects = (data.projects || []).map(item => '<article class="la-entry"><h3>' + e(item.name || "") + '</h3>' +
    (item.description ? '<p>' + e(item.description) + '</p>' : "") +
    ((item.achievements || []).length ? '<ul>' + bullets(item.achievements) + '</ul>' : "") + '</article>').join("");
  const credentials = (data.certifications || []).map(item => '<li><strong>' + e(item.name || "") + '</strong>' +
    (item.issuer ? ' — ' + e(item.issuer) : "") + '</li>').join("");
  return '<div class="resume-template-legal-associate"><header class="la-header"><div class="la-kicker">LEGAL PRACTICE · COMPLIANCE · ADVOCACY</div>' +
    '<h1>' + e(personal.full_name || "Your Name") + '</h1><p class="la-title">' + e(personal.professional_title || "Legal Professional") + '</p>' +
    '<div class="la-contact">' + contact.join('<span>•</span>') + '</div></header><main class="la-body">' +
    section("summary", "Professional Summary", data.summary ? '<p>' + e(data.summary) + '</p>' : "") +
    section("experience", "Legal Experience", experience) +
    section("education", "Education & Legal Training", education) +
    section("skills", "Practice Areas & Skills", skills) +
    section("projects", "Selected Matters & Projects", projects) +
    section("certifications", "Bar Admissions & Credentials", credentials ? '<ul>' + credentials + '</ul>' : "") +
    section("career_objective", "Professional Focus", data.career_objective ? '<p>' + e(data.career_objective) + '</p>' : "") +
    '</main></div>';
}
