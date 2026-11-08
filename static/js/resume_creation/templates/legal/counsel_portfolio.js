export function renderCounselPortfolioTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section data-section="' + key + '"><div class="lc-section-label">COUNSEL PROFILE</div><h2>' + title + '</h2>' + body + '</section>' : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  if (personal.linkedin) contact.push('<a href="' + e(personal.linkedin) + '" target="_blank" rel="noopener noreferrer">LinkedIn</a>');
  if (personal.website) contact.push('<a href="' + e(personal.website) + '" target="_blank" rel="noopener noreferrer">Website</a>');
  const bullets = items => Array.isArray(items) ? items.filter(Boolean).map(item => '<li>' + e(item) + '</li>').join("") : "";
  const dates = item => [item.start_date || "", item.current ? "Present" : (item.end_date || "")].filter(Boolean).map(e).join(" — ");
  const experience = (data.experience || []).map(item => '<article class="lc-matter"><div class="lc-matter-top"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") + '</p></div><time>' + dates(item) + '</time></div>' +
    ((item.bullets || []).length || (item.achievements || []).length ? '<ul>' + bullets([...(item.bullets || []), ...(item.achievements || [])]) + '</ul>' : "") + '</article>').join("");
  const education = (data.education || []).map(item => '<div class="lc-credential"><strong>' + e(item.degree || "") +
    (item.field_of_study ? " · " + e(item.field_of_study) : "") + '</strong><span>' + e(item.institution || "") + '</span>' +
    (item.coursework ? '<small>' + e(item.coursework) + '</small>' : "") + '</div>').join("");
  const skills = Object.entries(data.skills_by_category || {}).map(([key, values]) =>
    '<div class="lc-skill"><strong>' + e(key) + '</strong><span>' + e((values || []).join(" · ")) + '</span></div>').join("") ||
    '<div class="lc-skill"><strong>Core Expertise</strong><span>' + e((data.skills || []).join(" · ")) + '</span></div>';
  const projects = (data.projects || []).map(item => '<article class="lc-project"><h3>' + e(item.name || "") + '</h3>' +
    (item.role ? '<small>' + e(item.role) + '</small>' : "") + (item.description ? '<p>' + e(item.description) + '</p>' : "") +
    ((item.achievements || []).length ? '<ul>' + bullets(item.achievements) + '</ul>' : "") + '</article>').join("");
  const credentials = (data.certifications || []).map(item => '<div class="lc-credential"><strong>' + e(item.name || "") + '</strong>' +
    '<span>' + e(item.issuer || "") + '</span></div>').join("");
  return '<div class="resume-template-counsel-portfolio"><header class="lc-header"><div class="lc-monogram">LC</div><div class="lc-overline">LEGAL COUNSEL · STRATEGY · GOVERNANCE</div>' +
    '<h1>' + e(personal.full_name || "Your Name") + '</h1><p>' + e(personal.professional_title || "Counsel & Legal Advisor") + '</p>' +
    '<div class="lc-contact">' + contact.join('<span>◆</span>') + '</div></header><div class="lc-layout"><aside class="lc-rail">' +
    section("skills", "Practice Expertise", skills) + section("certifications", "Admissions & Credentials", credentials) +
    section("education", "Legal Education", education) + '</aside><main class="lc-main">' +
    section("summary", "Counsel Perspective", data.summary ? '<p class="lc-summary">' + e(data.summary) + '</p>' : "") +
    section("experience", "Selected Experience & Matters", experience) +
    section("projects", "Representative Work", projects) +
    section("career_objective", "Advisory Focus", data.career_objective ? '<p>' + e(data.career_objective) + '</p>' : "") +
    '</main></div></div>';
}
