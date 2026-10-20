export function renderCreativeStudioTemplate(content, escapeHtml) {
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
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
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, body) => body
    ? '<section data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + body + "</section>"
    : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map((value) => "<div>" + e(value) + "</div>");
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website], ["GitHub", personal.github]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<div><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a></div>");
    });

  const skillValues = Array.isArray(data.skills) ? data.skills
    : Object.values(data.skills_by_category || {}).flat();
  const skillGroups = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skillMarkup = skillGroups.length
    ? skillGroups.map(([name, values]) => '<h2>' + e(name) + '</h2><div class="cs-tags">' +
      values.map((skill) => '<span class="cs-tag">' + e(skill) + "</span>").join("") + "</div>").join("")
    : '<h2>Toolkit</h2><div class="cs-tags">' + skillValues.map((skill) => '<span class="cs-tag">' + e(skill) + "</span>").join("") + "</div>";

  const projects = list(data.projects).map((item, index) =>
    '<article class="cs-project"><div class="cs-project-top"><span class="cs-project-no">' +
    e(String(index + 1).padStart(2, "0")) + "</span><h3>" + e(item.name || "") +
    (item.role ? ' <span class="cs-meta">/ ' + e(item.role) + "</span>" : "") + "</h3></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.technologies && item.technologies.length ? '<p class="cs-meta">Tools: ' + e(item.technologies.join(", ")) + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">Open project ↗</a></p>' : "") +
    "</article>"
  ).join("");

  const experience = list(data.experience).map((item) =>
    '<article class="cs-entry"><div class="cs-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="cs-meta">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    "</p></div><span class=\"cs-meta\">" + dates(item) + "</span></div>" +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? "<p><strong>Impact:</strong> " + e(item.achievements.join(" · ")) + "</p>" : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="cs-entry"><div class="cs-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="cs-meta">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") +
    "</p></div><span class=\"cs-meta\">" + dates(item) + "</span></div>" +
    (item.coursework ? "<p>" + e(item.coursework) + "</p>" : "") + "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="cs-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " <span>· " + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? " <span>· " + e(item.issue_date) + "</span>" : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="cs-credential"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " <span>· " + e(item.proficiency) + "</span>" : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections)
    .filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items).map((entry) =>
        '<article class="cs-entry"><div class="cs-entry-head"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><span class="cs-meta">' +
        e(entry.date || "") + "</span></div>" + (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
      ).join("")
    )).join("");

  const html = '<div class="resume-template-creative-studio"><aside class="cs-rail"><p class="cs-label">Independent Practice</p>' +
    '<span class="cs-index" aria-hidden="true">01</span>' + skillMarkup +
    '<div class="cs-rail-meta">' + contact.join("") + '</div></aside><main class="cs-main">' +
    '<header class="cs-header"><p class="cs-kicker">Selected work / profile</p><h1>' +
    e(personal.full_name || "Your Name") + '</h1><p class="cs-title">' +
    e(personal.professional_title || "") + "</p></header>" +
    (data.summary ? '<section class="cs-summary"><p>' + e(data.summary) + "</p></section>" : "") +
    section("projects", "Selected Work", projects) + section("experience", "Experience", experience) +
    section("education", "Education", education) + section("certifications", "Credentials", certifications) +
    section("languages", "Languages", languages) + custom + "</main></div>";
  const holder = document.createElement("div");
  holder.innerHTML = html;
  holder.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const main = holder.querySelector(".cs-main");
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return holder.firstElementChild.outerHTML;
}
