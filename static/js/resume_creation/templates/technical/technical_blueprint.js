export function renderTechnicalBlueprintTemplate(content, escapeHtml) {
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(Array.isArray(data.hidden_sections) ? data.hidden_sections : []);
  const list = (value) => Array.isArray(value) ? value : [];
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return start || end ? e(start) + (start && end ? " – " : "") + e(end) : "";
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, body) => body
    ? '<section data-section="' + e(key) + '"><h2><span class="tb-marker">/</span> ' + e(title) + "</h2>" + body + "</section>"
    : "";
  const contact = [];
  [personal.email, personal.phone, personal.location].filter(Boolean).forEach((value) => {
    contact.push('<span class="tb-contact-item">' + e(value) + "</span>");
  });
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a class="tb-contact-item" href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const categories = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skillMarkup = categories.length
    ? categories.map(([category, values]) =>
      '<div class="tb-skill-group"><h3>' + e(category) + '</h3><ul class="tb-tags">' +
      values.map((value) => "<li>" + e(value) + "</li>").join("") + "</ul></div>"
    ).join("")
    : list(data.skills).length
      ? '<ul class="tb-tags">' + list(data.skills).map((value) => "<li>" + e(value) + "</li>").join("") + "</ul>"
      : "";
  const experience = list(data.experience).map((item) =>
    '<article class="tb-entry"><div class="tb-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="tb-meta">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><p class="tb-date">' + dates(item) + "</p></div>" +
    (item.summary ? "<p>" + e(item.summary) + "</p>" : "") +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<p class="tb-result"><strong>Result:</strong> ' + item.achievements.map((value) => e(value)).join("; ") + "</p>" : "") +
    "</article>"
  ).join("");
  const projects = list(data.projects).map((item) =>
    '<article class="tb-entry tb-project"><div class="tb-entry-head"><div><h3>' + e(item.name || "") +
    (item.role ? ' <span class="tb-meta">· ' + e(item.role) + "</span>" : "") + "</h3></div>" +
    '<p class="tb-date">' + dates(item) + "</p></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="tb-meta"><strong>Stack:</strong> ' + item.technologies.map((value) => e(value)).join(" / ") + "</p>" : "") +
    (item.achievements && item.achievements.length ? '<p class="tb-result"><strong>Outcome:</strong> ' + item.achievements.map((value) => e(value)).join("; ") + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">Open project ↗</a></p>' : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="tb-entry"><div class="tb-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><p class="tb-meta">' + e(item.institution || "") + (item.location ? " · " + e(item.location) : "") +
    "</p></div><p class=\"tb-date\">" + dates(item) + "</p></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="tb-compact"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="tb-compact"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections).filter((item) =>
    list(item.items).length && !hidden.has("custom:" + item.id)
  ).map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
    list(item.items).map((entry) =>
      '<article class="tb-entry"><div class="tb-entry-head"><h3>' + e(entry.title || "") +
      (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><p class="tb-date">' + e(entry.date || "") + "</p></div>" +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
    ).join("")
  )).join("");
  const summary = data.summary ? "<p>" + e(data.summary) + "</p>" : "";
  const markup =
    '<div class="resume-template-technical-blueprint">' +
      '<header class="tb-header"><div class="tb-topline"><span>ENGINEERING / SYSTEMS / DELIVERY</span><span class="tb-code">CV_03</span></div>' +
      '<div class="tb-identity"><div><h1>' + e(personal.full_name || "Your Name") + '</h1><p class="tb-role">' +
      e(personal.professional_title || "") + '</p></div><div class="tb-contact">' + contact.join("") + '</div></div>' +
      '<div class="tb-header-rule"><span></span><small>BUILD · MEASURE · IMPROVE</small></div></header>' +
      '<div class="tb-content"><main class="tb-main">' +
      section("summary", "Profile", summary) +
      section("experience", "Engineering Experience", experience) +
      section("projects", "Selected Builds", projects) +
      section("education", "Education", education) + custom +
      '</main><aside class="tb-sidebar">' +
      section("skills", "Skill Matrix", skillMarkup) +
      section("certifications", "Credentials", certifications) +
      section("languages", "Languages", languages) +
      '<div class="tb-sidebar-note"><span>SYS.STATUS</span><strong>READY TO BUILD</strong></div>' +
      '</aside></div></div>';
  const root = document.createElement("div");
  root.innerHTML = markup;
  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  [root.querySelector(".tb-main"), root.querySelector(".tb-sidebar")].forEach((container) => {
    if (!container || !order.length) return;
    const children = Array.from(container.querySelectorAll(":scope > [data-section]"));
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) container.appendChild(node);
    });
  });
  return root.firstElementChild.outerHTML;
}
