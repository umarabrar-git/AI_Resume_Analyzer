export function renderFirstMileTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("") : "";
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="fm-section" data-section="' + key + '"><h2>' + title + "</h2>" + body + "</section>" : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [[ "LinkedIn", personal.linkedin ], [ "Portfolio", personal.portfolio ], [ "Website", personal.website ]]
    .forEach(([label, url]) => {
      if (url) contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skills = Array.isArray(data.skills_by_category) ? data.skills_by_category : [];
  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skillMarkup = skillGroups.length
    ? skillGroups.map(([name, values]) => '<div class="fm-skill"><strong>' + e(name) + '</strong><span>' + e(values.join(" · ")) + "</span></div>").join("")
    : (Array.isArray(data.skills) && data.skills.length
      ? '<div class="fm-skill"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="fm-entry"><div class="fm-entry-top"><div><h3>' + e(item.title || "") +
    '</h3><p class="fm-subtitle">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + '</p></div><time>' + dates(item) + "</time></div>" +
    (((item.bullets || []).length || (item.achievements || []).length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") + "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="fm-entry"><div class="fm-entry-top"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><p class="fm-subtitle">' + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + '</p></div><time>' + dates(item) + "</time></div>" +
    (item.coursework ? "<p>" + e(item.coursework) + "</p>" : "") + "</article>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="fm-project"><div class="fm-project-index">' + e(String(item.index || "PROJECT")) + '</div><div><h3>' +
    e(item.name || "") + (item.role ? " <span>· " + e(item.role) + "</span>" : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="fm-tools">' + e(item.technologies.join(" · ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    "</div></article>"
  ).join("");
  const certifications = (data.certifications || []).map((item) =>
    '<div class="fm-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<small>" + e(item.issue_date) + "</small>" : "") + "</div>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="fm-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>"
  ).join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => section("custom", e(item.title || "Additional"), item.items.map((entry) =>
      '<article class="fm-entry"><h3>' + e(entry.title || "") +
      (entry.subtitle ? " — " + e(entry.subtitle) : "") + "</h3>" +
      (entry.date ? '<p class="fm-subtitle">' + e(entry.date) + "</p>" : "") +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
      "</article>").join(""))).join("");
  return '<div class="resume-template-first-mile"><header class="fm-header">' +
    '<div class="fm-eyebrow"><span>EARLY CAREER / PORTFOLIO</span><span>01 — PROFILE</span></div>' +
    '<h1>' + e(personal.full_name || "Your Name") + '</h1><p class="fm-title">' +
    e(personal.professional_title || "Emerging Professional") + '</p><div class="fm-contact">' +
    contact.join('<span aria-hidden="true">/</span>') + '</div></header><div class="fm-body">' +
    '<aside class="fm-rail">' + section("summary", "Profile", data.summary ? '<p class="fm-summary">' + e(data.summary) + "</p>" : "") +
    section("skills", "Core Skills", skillMarkup) + section("certifications", "Certifications", certifications) +
    section("languages", "Languages", languages) +
    (data.career_objective && !hidden.has("career_objective") ? section("career_objective", "Next Direction", "<p>" + e(data.career_objective) + "</p>") : "") +
    '</aside><main class="fm-main">' + section("experience", "Experience & Involvement", experience) +
    section("projects", "Projects in Practice", projects) + section("education", "Education", education) +
    custom + "</main></div></div>";
}
