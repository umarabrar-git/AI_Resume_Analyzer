export function renderATSProfessionalTemplate(content, escapeHtml) {
  const root = document.createElement("div");
  const fallbackEscape = (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
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
    if (!start && !end) return "";
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, html) => html
    ? '<section data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + html + "</section>"
    : "";

  const contact = [personal.email, personal.phone, personal.location]
    .filter(Boolean)
    .map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const rawSkills = Array.isArray(data.skills)
    ? data.skills
    : Object.values(data.skills_by_category || {}).flat();
  const categories = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter((entry) => Array.isArray(entry[1]) && entry[1].length)
    : [];
  const skills = categories.length
    ? '<dl class="ap-skill-list">' + categories.map(([name, values]) =>
        '<div><dt>' + e(name) + '</dt><dd>' + values.map((skill) => e(skill)).join(", ") + "</dd></div>"
      ).join("") + "</dl>"
    : (rawSkills.length ? '<p class="ap-inline-list">' + rawSkills.map((skill) => e(skill)).join(" · ") + "</p>" : "");

  const experience = list(data.experience).map((item) =>
    '<article class="ap-entry"><div class="ap-entry-heading"><div><h3>' + e(item.title || "") +
    '</h3><p class="ap-subtitle">' + e(item.company || "") +
    (item.location ? " | " + e(item.location) : "") + "</p></div>" +
    '<p class="ap-date">' + dates(item) + "</p></div>" +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<p class="ap-highlight"><strong>Key achievements:</strong> ' + item.achievements.map((x) => e(x)).join("; ") + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = list(data.projects).map((item) =>
    '<article class="ap-entry"><div class="ap-entry-heading"><div><h3>' + e(item.name || "") +
    (item.role ? ' <span class="ap-role">| ' + e(item.role) + "</span>" : "") + "</h3></div>" +
    '<p class="ap-date">' + dates(item) + "</p></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.technologies && item.technologies.length ? '<p class="ap-subtitle"><strong>Technologies:</strong> ' + item.technologies.map((x) => e(x)).join(", ") + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">Project link</a></p>' : "") +
    "</article>"
  ).join("");

  const education = list(data.education).map((item) =>
    '<article class="ap-entry"><div class="ap-entry-heading"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="ap-subtitle">' +
    e(item.institution || "") + (item.location ? " | " + e(item.location) : "") + "</p></div>" +
    '<p class="ap-date">' + dates(item) + "</p></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const certifications = list(data.certifications).map((item) =>
    '<p class="ap-compact"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " | " + e(item.issuer) : "") +
    (item.issue_date ? " | " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="ap-compact"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " | " + e(item.proficiency) : "") + "</p>"
  ).join("");

  const custom = list(data.custom_sections)
    .filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items).map((entry) => '<article class="ap-entry"><div class="ap-entry-heading"><h3>' +
        e(entry.title || "") + (entry.subtitle ? " | " + e(entry.subtitle) : "") +
        '</h3><p class="ap-date">' + e(entry.date || "") + "</p></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join("")
    )).join("");

  root.innerHTML =
    '<div class="resume-template-ats-professional"><header class="ap-header">' +
    '<h1>' + e(personal.full_name || "Your Name") + '</h1>' +
    '<p class="ap-title">' + e(personal.professional_title || "") + '</p>' +
    '<div class="ap-contact">' + contact.join(" <span>|</span> ") + "</div></header><main>" +
    section("summary", "Professional Summary", data.summary ? '<p>' + e(data.summary) + "</p>" : "") +
    section("skills", "Core Competencies", skills) +
    section("experience", "Professional Experience", experience) +
    section("projects", "Selected Projects", projects) +
    section("education", "Education", education) +
    section("certifications", "Certifications", certifications) +
    section("languages", "Languages", languages) + custom + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const main = root.querySelector("main");
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return root.firstElementChild.outerHTML;
}
