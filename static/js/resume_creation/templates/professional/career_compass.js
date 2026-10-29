export function renderCareerCompassTemplate(content, escapeHtml) {
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const list = (items, render) => (Array.isArray(items) ? items : []).map(render).join("");
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="cc-section" data-section="' + key + '"><div class="cc-section-heading"><span>' +
      e(title) + '</span><i aria-hidden="true"></i></div>' + body + '</section>' : "";
  const bullets = (items) => Array.isArray(items) && items.length
    ? "<ul>" + items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("") + "</ul>" : "";
  const contacts = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, rawUrl]) => {
      const url = String(rawUrl || "").trim();
      if (/^https?:\/\//i.test(url)) contacts.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skills = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="cc-skill"><strong>' + e(category) + '</strong><span>' + e(values.join(" · ")) + "</span></div>")
    .join("") || (Array.isArray(data.skills) && data.skills.length
      ? '<p class="cc-skill-flat">' + e(data.skills.join(" · ")) + "</p>" : "");
  const experience = list(data.experience, (item) =>
    '<article class="cc-timeline-item"><div class="cc-timeline-dot" aria-hidden="true"></div><div class="cc-entry-top"><div><h3>' +
    e(item.title || "") + '</h3><p class="cc-meta">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    (dates(item) ? "<time>" + dates(item) + "</time>" : "") + "</div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</article>");
  const education = list(data.education, (item) =>
    '<article class="cc-entry"><div class="cc-entry-top"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " · " + e(item.field_of_study) : "") + '</h3><p class="cc-meta">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    (dates(item) ? "<time>" + dates(item) + "</time>" : "") + "</div>" +
    (item.coursework ? '<p class="cc-detail"><strong>Relevant coursework:</strong> ' + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? '<p class="cc-detail">' + e(item.academic_achievements) + "</p>" : "") + "</article>");
  const projects = list(data.projects, (item, index) =>
    '<article class="cc-project"><span class="cc-project-index">' + String(index + 1).padStart(2, "0") +
    '</span><div><h3>' + e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="cc-tools">' + e(item.technologies.join(" · ")) + "</p>" : "") +
    bullets(item.achievements || []) + "</div></article>");
  const certifications = list(data.certifications, (item) =>
    '<div class="cc-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<time>" + e(item.issue_date) + "</time>" : "") + "</div>");
  const languages = list(data.languages, (item) =>
    '<div class="cc-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>");
  const custom = list(data.custom_sections, (item) =>
    item && Array.isArray(item.items) && item.items.length
      ? section("custom", item.title || "Additional Information", list(item.items, (entry) =>
        '<article class="cc-entry"><div class="cc-entry-top"><h3>' + e(entry.title || "") + "</h3>" +
        (entry.date ? "<time>" + e(entry.date) + "</time>" : "") + "</div>" +
        (entry.subtitle ? '<p class="cc-meta">' + e(entry.subtitle) + "</p>" : "") +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") + bullets(entry.bullets || []) + "</article>")) : "");
  return '<div class="resume-template-career-compass">' +
    '<header class="cc-header"><div class="cc-overline"><span>CAREER PROFILE</span><span>STRATEGY / EXECUTION / IMPACT</span></div>' +
    '<div class="cc-identity"><div><h1>' + e(personal.full_name || "Your Name") + '</h1><p class="cc-title">' +
    e(personal.professional_title || "Professional Title") + "</p></div><div class=\"cc-emblem\" aria-hidden=\"true\"><span></span><span></span><span></span><b>N</b></div></div>" +
    (contacts.length ? '<div class="cc-contact">' + contacts.join('<span aria-hidden="true">/</span>') + "</div>" : "") +
    '</header><div class="cc-body"><main class="cc-main">' +
    section("summary", "Professional Summary", data.summary ? '<p class="cc-summary">' + e(data.summary) + "</p>" : "") +
    section("experience", "Career Journey", experience) +
    section("projects", "Selected Achievements", projects) +
    section("education", "Education", education) + custom +
    '</main><aside class="cc-sidebar">' +
    section("career_objective", "Career Focus", data.career_objective ? '<p class="cc-focus">' + e(data.career_objective) + "</p>" : "") +
    section("skills", "Core Capabilities", skills) +
    section("certifications", "Credentials", certifications) +
    section("languages", "Languages", languages) +
    '</aside></div></div>';
}
