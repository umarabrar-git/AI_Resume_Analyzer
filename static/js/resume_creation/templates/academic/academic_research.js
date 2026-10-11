export function renderAcademicResearchTemplate(content, escapeHtml) {
  const root = document.createElement("div");
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);

  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    if (!start && !end) return "";
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const section = (key, html, title) => html
    ? '<section data-section="' + key + '"><h2>' + e(title) + "</h2>" + html + "</section>"
    : "";

  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Google Scholar", personal.google_scholar],
    ["ORCID", personal.orcid], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, rawUrl]) => {
      const url = safeUrl(rawUrl);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) =>
        '<div class="ar-skill-group"><strong>' + e(category) + "</strong>" + e(values.join(", ")) + "</div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
        ? '<div class="ar-skill-group">' + e(data.skills.join(", ")) + "</div>"
        : "");

  const experience = (data.experience || []).map((item) =>
    '<article class="ar-entry"><div class="ar-entry-head"><h3 class="ar-entry-title">' +
    e(item.title || "") + '</h3><span class="ar-entry-date">' + dates(item) +
    '</span></div><div class="ar-entry-subtitle">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets && item.bullets.length) || (item.achievements && item.achievements.length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");

  const education = (data.education || []).map((item) =>
    '<article class="ar-entry"><div class="ar-entry-head"><h3 class="ar-entry-title">' +
    e(item.degree || "") + (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><span class="ar-entry-date">' + dates(item) + '</span></div><div class="ar-entry-subtitle">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = (data.projects || []).map((item) =>
    '<article class="ar-entry"><div class="ar-entry-head"><h3 class="ar-entry-title">' +
    e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.technologies && item.technologies.length
      ? '<div class="ar-tech"><strong>Methods & tools:</strong> ' + e(item.technologies.join(", ")) + "</div>" : "") +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">' + e(item.url) + "</a></p>" : "") +
    "</article>"
  ).join("");

  const certifications = (data.certifications || []).map((item) =>
    '<div class="ar-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " — " + e(item.issuer) : "") +
    (item.issue_date ? " (" + e(item.issue_date) + ")" : "") + "</div>"
  ).join("");

  const languages = (data.languages || []).map((item) =>
    "<span>" + e(item.language || "") +
    (item.proficiency ? " (" + e(item.proficiency) + ")" : "") + "</span>"
  ).join("");

  const customSections = (data.custom_sections || [])
    .filter((item) => item.items && item.items.length && !hidden.has("custom:" + item.id))
    .map((item) =>
      '<section class="ar-custom" data-section="custom:' + e(item.id || "") + '"><h2>' +
      e(item.title || "Additional Academic Information") + "</h2>" +
      item.items.map((entry) =>
        '<article class="ar-custom-item"><div class="ar-entry-head"><h3 class="ar-entry-title">' +
        e(entry.title || "") + (entry.subtitle ? " · " + e(entry.subtitle) : "") +
        '</h3><span class="ar-entry-date">' + e(entry.date || "") + "</span></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>"
      ).join("") + "</section>"
    ).join("");

  root.innerHTML =
    '<div class="resume-template-academic-research"><header class="ar-header">' +
    '<p class="ar-kicker">Academic Curriculum Vitae</p><h1>' + e(personal.full_name || "Your Name") +
    '</h1><p class="ar-title">' + e(personal.professional_title || "") +
    '</p><div class="ar-contact">' + contact.join("<span> · </span>") +
    '</div><div class="ar-header-rule" aria-hidden="true"></div></header><main>' +
    section("summary", data.summary ? '<p class="ar-summary">' + e(data.summary) + "</p>" : "", "Research Profile") +
    section("career_objective", data.career_objective ? '<p class="ar-objective">' + e(data.career_objective) + "</p>" : "", "Research Objective") +
    section("skills", skills ? '<div class="ar-skill-groups">' + skills + "</div>" : "", "Research & Technical Skills") +
    section("experience", experience, "Research & Professional Experience") +
    section("education", education, "Education") +
    section("projects", projects, "Selected Research & Projects") +
    section("certifications", certifications, "Certifications & Training") +
    section("languages", languages ? '<div class="ar-languages">' + languages + "</div>" : "", "Languages") +
    customSections + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    const contentNode = node.cloneNode(true);
    const heading = contentNode.querySelector("h2");
    if (heading) heading.remove();
    if (hidden.has(node.dataset.section) || !contentNode.textContent.trim()) {
      node.classList.add("is-hidden");
    }
  });

  const main = root.querySelector("main");
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const sectionNode = children.find((node) => node.dataset.section === key);
      if (sectionNode) main.appendChild(sectionNode);
    });
  }

  return root.firstElementChild.outerHTML;
}

window.renderAcademicResearchTemplate = renderAcademicResearchTemplate;
