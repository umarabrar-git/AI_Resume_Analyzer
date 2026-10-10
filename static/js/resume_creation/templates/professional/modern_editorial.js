export function renderModernEditorialTemplate(content, escapeHtml) {
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
    ? '<section data-section="' + key + '"><h2><span>' + e(title.number) + "</span>" + e(title.label) + "</h2>" + html + "</section>"
    : "";

  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github],
    ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, rawUrl]) => {
      const url = safeUrl(rawUrl);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skillGroups = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length);
  const skills = skillGroups.length
    ? skillGroups.map(([category, values]) =>
        '<div class="me-skill-group"><strong>' + e(category) + "</strong><br>" + e(values.join(", ")) + "</div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
        ? '<div class="me-skill-group">' + e(data.skills.join(", ")) + "</div>"
        : "");

  const experience = (data.experience || []).map((item) =>
    '<article class="me-entry"><div class="me-entry-head"><h3 class="me-entry-title">' +
    e(item.title || "") + '</h3><span class="me-entry-date">' + dates(item) +
    '</span></div><div class="me-entry-subtitle">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets && item.bullets.length) || (item.achievements && item.achievements.length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");

  const education = (data.education || []).map((item) =>
    '<article class="me-entry"><div class="me-entry-head"><h3 class="me-entry-title">' +
    e(item.degree || "") + (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><span class="me-entry-date">' + dates(item) + '</span></div><div class="me-entry-subtitle">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = (data.projects || []).map((item) =>
    '<article class="me-entry"><div class="me-entry-head"><h3 class="me-entry-title">' +
    e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.technologies && item.technologies.length
      ? '<div class="me-tech">' + e(item.technologies.join(", ")) + "</div>" : "") +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">' + e(item.url) + "</a></p>" : "") +
    "</article>"
  ).join("");

  const certifications = (data.certifications || []).map((item) =>
    '<div class="me-cert"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " — " + e(item.issuer) : "") +
    (item.issue_date ? " (" + e(item.issue_date) + ")" : "") + "</div>"
  ).join("");

  const languages = (data.languages || []).map((item) =>
    "<span>" + e(item.language || "") +
    (item.proficiency ? " (" + e(item.proficiency) + ")" : "") + "</span>"
  ).join("");

  const customSections = (data.custom_sections || []).filter((item) => item.items && item.items.length).map((item) =>
    '<section class="me-custom"><h2><span>+</span>' + e(item.title || "Additional Information") + "</h2>" +
    item.items.map((entry) =>
      '<article class="me-custom-item"><div class="me-entry-head"><h3 class="me-entry-title">' +
      e(entry.title || "") + (entry.subtitle ? " · " + e(entry.subtitle) : "") +
      '</h3><span class="me-entry-date">' + e(entry.date || "") + "</span></div>" +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
      "</article>"
    ).join("") + "</section>"
  ).join("");

  root.innerHTML =
    '<div class="resume-template-modern-editorial"><header class="me-header">' +
    '<p class="me-eyebrow">Professional Profile</p><h1>' + e(personal.full_name || "Your Name") +
    "</h1><p class=\"me-title\">" + e(personal.professional_title || "") +
    '</p><div class="me-contact">' + contact.join("<span> · </span>") +
    '</div><div class="me-header-rule" aria-hidden="true"></div></header><main>' +
    section("summary", data.summary ? '<p class="me-summary">' + e(data.summary) + "</p>" : "", {number:"01",label:"Profile"}) +
    section("career_objective", data.career_objective ? '<p class="me-objective">' + e(data.career_objective) + "</p>" : "", {number:"02",label:"Objective"}) +
    section("skills", skills ? '<div class="me-skill-groups">' + skills + "</div>" : "", {number:"03",label:"Core Skills"}) +
    section("experience", experience, {number:"04",label:"Experience"}) +
    section("education", education, {number:"05",label:"Education"}) +
    section("projects", projects, {number:"06",label:"Selected Projects"}) +
    section("certifications", certifications, {number:"07",label:"Certifications"}) +
    section("languages", languages ? '<div class="me-languages">' + languages + "</div>" : "", {number:"08",label:"Languages"}) +
    customSections + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    const contentNode = node.cloneNode(true);
    const heading = contentNode.querySelector("h2");
    if (heading) heading.remove();
    if (hidden.has(node.dataset.section) || !contentNode.textContent.trim()) {
      node.classList.add("is-hidden");
    }
  });

  return root.firstElementChild.outerHTML;
}

window.renderModernEditorialTemplate = renderModernEditorialTemplate;