export function renderLaunchpadTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const list = (items, render) => (Array.isArray(items) ? items : []).map(render).join("");
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="lp-section" data-section="' + key + '"><div class="lp-section-title"><span>' +
      title + '</span><i></i></div>' + body + '</section>' : "";
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const bullets = (items) => list(items, (item) => "<li>" + e(item) + "</li>");
  const contacts = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [[ "LinkedIn", personal.linkedin ], [ "GitHub", personal.github ], [ "Portfolio", personal.portfolio ], [ "Website", personal.website ]]
    .forEach(([label, url]) => {
      if (url) contacts.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([name, values]) => '<div class="lp-skill"><strong>' + e(name) +
      '</strong><span>' + e(values.join(" · ")) + '</span></div>').join("")
    : (Array.isArray(data.skills) && data.skills.length
      ? '<div class="lp-skill"><span>' + e(data.skills.join(" · ")) + '</span></div>' : "");
  const education = list(data.education, (item) =>
    '<article class="lp-entry"><div class="lp-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " · " + e(item.field_of_study) : "") + '</h3><p class="lp-meta">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + '</time></div>' +
    (item.coursework ? '<p class="lp-detail"><strong>Relevant coursework:</strong> ' + e(item.coursework) + '</p>' : "") +
    (item.academic_achievements ? '<p class="lp-detail">' + e(item.academic_achievements) + '</p>' : "") +
    '</article>');
  const projects = list(data.projects, (item, index) =>
    '<article class="lp-project"><div class="lp-project-number">' + String(index + 1).padStart(2, "0") +
    '</div><div><h3>' + e(item.name || "") + (item.role ? ' <span>· ' + e(item.role) + '</span>' : "") + '</h3>' +
    (item.description ? '<p>' + e(item.description) + '</p>' : "") +
    (item.technologies && item.technologies.length ? '<p class="lp-tools">' + e(item.technologies.join(" · ")) + '</p>' : "") +
    (item.achievements && item.achievements.length ? '<ul>' + bullets(item.achievements) + '</ul>' : "") +
    '</div></article>');
  const experience = list(data.experience, (item) =>
    '<article class="lp-entry"><div class="lp-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="lp-meta">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + '</time></div>' +
    ((item.bullets || []).length || (item.achievements || []).length
      ? '<ul>' + bullets([...(item.bullets || []), ...(item.achievements || [])]) + '</ul>' : "") +
    '</article>');
  const credentials = list(data.certifications, (item) =>
    '<div class="lp-credential"><strong>' + e(item.name || "") + '</strong>' +
    (item.issuer ? '<span>' + e(item.issuer) + '</span>' : "") +
    (item.issue_date ? '<small>' + e(item.issue_date) + '</small>' : "") + '</div>');
  const languages = list(data.languages, (item) =>
    '<div class="lp-language"><strong>' + e(item.language || "") + '</strong>' +
    (item.proficiency ? '<span>' + e(item.proficiency) + '</span>' : "") + '</div>');
  const custom = list(data.custom_sections, (item) =>
    item && Array.isArray(item.items) && item.items.length
      ? section("custom", e(item.title || "Additional"), list(item.items, (entry) =>
        '<article class="lp-entry"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3>' +
        (entry.date ? '<p class="lp-meta">' + e(entry.date) + '</p>' : "") +
        (entry.description ? '<p class="lp-detail">' + e(entry.description) + '</p>' : "") +
        (entry.bullets && entry.bullets.length ? '<ul>' + bullets(entry.bullets) + '</ul>' : "") +
        '</article>')) : "");
  return '<div class="resume-template-launchpad">' +
    '<header class="lp-header"><div class="lp-kicker"><span>STUDENT / EARLY CAREER</span><span>PROFILE 01</span></div>' +
    '<div class="lp-identity"><div><h1>' + e(personal.full_name || "Your Name") + '</h1><p class="lp-title">' +
    e(personal.professional_title || "Student & Emerging Professional") + '</p></div>' +
    '<div class="lp-marker" aria-hidden="true"><span></span><span></span><span></span></div></div>' +
    (contacts.length ? '<div class="lp-contact">' + contacts.join('<span aria-hidden="true">•</span>') + '</div>' : "") +
    '</header><div class="lp-layout"><main class="lp-main">' +
    section("summary", "Profile", data.summary ? '<p class="lp-summary">' + e(data.summary) + '</p>' : "") +
    section("education", "Education", education) +
    section("projects", "Selected Projects", projects) +
    section("experience", "Experience & Leadership", experience) + custom +
    '</main><aside class="lp-sidebar">' +
    section("skills", "Skills", skills) +
    section("certifications", "Certifications", credentials) +
    section("languages", "Languages", languages) +
    (data.career_objective && !hidden.has("career_objective")
      ? section("career_objective", "Career Direction", '<p class="lp-summary">' + e(data.career_objective) + '</p>') : "") +
    '</aside></div></div>';
}

export { renderLaunchpadTemplate };
