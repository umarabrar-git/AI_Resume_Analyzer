export function renderScholarsFolioTemplate(content, escapeHtml) {
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return [start, end].filter(Boolean).map(e).join(" – ");
  };
  const bullets = (items) => Array.isArray(items) && items.length
    ? "<ul>" + items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("") + "</ul>" : "";
  const section = (key, title, body, className = "") =>
    body && !hidden.has(key)
      ? '<section data-section="' + key + '" class="' + className + '"><h2>' + e(title) + "</h2>" + body + "</section>"
      : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Google Scholar", personal.google_scholar],
    ["ORCID", personal.orcid], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, rawUrl]) => {
      const url = String(rawUrl || "").trim();
      if (/^https?:\/\//i.test(url))
        contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="sf-skill-group"><strong>' + e(category) + "</strong><span>" + e(values.join(" · ")) + "</span></div>");
  const skills = skillGroups.join("") || (Array.isArray(data.skills) && data.skills.length
    ? '<div class="sf-skill-group"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="sf-entry"><div class="sf-entry-head"><div><h3>' + e(item.title || "") + "</h3>" +
    '<p class="sf-meta">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    (dates(item) ? "<time>" + dates(item) + "</time>" : "") + "</div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="sf-entry"><div class="sf-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + "</h3>" +
    '<p class="sf-meta">' + e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    (dates(item) ? "<time>" + dates(item) + "</time>" : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") + "</article>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="sf-project"><h3>' + e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="sf-tools">METHODS / ' + e(item.technologies.join(" · ")) + "</p>" : "") +
    bullets(item.achievements || []) + "</article>"
  ).join("");
  const certifications = (data.certifications || []).map((item) =>
    '<div class="sf-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<time>" + e(item.issue_date) + "</time>" : "") + "</div>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="sf-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>"
  ).join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => '<section data-section="custom" class="sf-custom"><h2>' + e(item.title || "Additional Information") + "</h2>" +
      item.items.map((entry) => '<article class="sf-entry"><div class="sf-entry-head"><h3>' + e(entry.title || "") + "</h3>" +
        (entry.date ? "<time>" + e(entry.date) + "</time>" : "") + "</div>" +
        (entry.subtitle ? '<p class="sf-meta">' + e(entry.subtitle) + "</p>" : "") +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        bullets(entry.bullets || []) + "</article>").join("") + "</section>").join("");
  const markup = '<div class="resume-template-scholars-folio"><header class="sf-header">' +
    '<p class="sf-kicker">Scholar\'s Folio · Curriculum Vitae</p><h1>' + e(personal.full_name || "Your Name") + "</h1>" +
    '<p class="sf-title">' + e(personal.professional_title || "Researcher · Educator · Scholar") + "</p>" +
    '<div class="sf-contact">' + contact.join('<span aria-hidden="true">·</span>') + "</div>" +
    '<div class="sf-motto"><span>RESEARCH</span><span>DISCOVERY</span><span>IMPACT</span></div></header>' +
    '<div class="sf-layout"><aside class="sf-rail">' +
    section("career_objective", "Research Agenda", data.career_objective ? '<p class="sf-objective">' + e(data.career_objective) + "</p>" : "") +
    section("skills", "Methods & Expertise", skills) + section("certifications", "Credentials", certifications) +
    section("languages", "Languages", languages) + "</aside><main class=\"sf-main\">" +
    section("summary", "Scholarly Profile", data.summary ? '<p class="sf-summary">' + e(data.summary) + "</p>" : "") +
    section("experience", "Research & Teaching Experience", experience) +
    section("projects", "Selected Research & Publications", projects) + section("education", "Education", education) +
    custom + "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".sf-main");
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return root.outerHTML;
}
