export function renderDataEngineerTemplate(content, escapeHtml) {
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
    ? '<section class="de-section" data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + body + "</section>"
    : "";
  const contact = [];
  [personal.email, personal.phone, personal.location].filter(Boolean).forEach((value) => contact.push(e(value)));
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio]].forEach(([label, value]) => {
    const url = safeUrl(value);
    if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const skillGroups = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skills = skillGroups.length
    ? skillGroups.map(([name, values]) => '<div class="de-skill-group"><strong>' + e(name) + '</strong><div class="de-tags">' +
      values.map((value) => "<span>" + e(value) + "</span>").join("") + "</div></div>").join("")
    : list(data.skills).length
      ? '<div class="de-tags">' + list(data.skills).map((value) => "<span>" + e(value) + "</span>").join("") + "</div>"
      : "";
  const experience = list(data.experience).map((item) =>
    '<article class="de-entry"><div class="de-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="de-muted">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    (item.summary ? "<p>" + e(item.summary) + "</p>" : "") +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<p class="de-impact"><strong>Delivery impact:</strong> ' + item.achievements.map(e).join("; ") + "</p>" : "") +
    "</article>"
  ).join("");
  const projects = list(data.projects).map((item) =>
    '<article class="de-project"><div class="de-entry-head"><div><h3>' + e(item.name || "") +
    (item.role ? '<span class="de-muted"> · ' + e(item.role) + "</span>" : "") +
    '</h3></div><time>' + dates(item) + "</time></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="de-stack"><strong>Pipeline stack:</strong> ' + item.technologies.map(e).join(" · ") + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (safeUrl(item.url) ? '<a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View project</a>' : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="de-entry"><div class="de-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="de-muted">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="de-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="de-credential"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections).filter((item) =>
    list(item.items).length && !hidden.has("custom:" + item.id)
  ).map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
    list(item.items).map((entry) =>
      '<article class="de-entry"><div class="de-entry-head"><h3>' + e(entry.title || "") +
      (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><time>' + e(entry.date || "") + "</time></div>" +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
    ).join("")
  )).join("");
  const summary = data.summary ? "<p>" + e(data.summary) + "</p>" : "";
  const root = document.createElement("div");
  root.innerHTML =
    '<div class="resume-template-data-engineer"><header class="de-header"><div class="de-identity">' +
    '<p class="de-kicker">DATA PLATFORMS / PIPELINE ENGINEERING / RELIABLE SYSTEMS</p><h1>' + e(personal.full_name || "Your Name") +
    '</h1><p class="de-role">' + e(personal.professional_title || "") + '</p></div><div class="de-contact">' +
    contact.join("") + '</div></header><div class="de-layout"><aside class="de-sidebar">' +
    section("skills", "Engineering Stack", skills) +
    section("certifications", "Platform Credentials", certifications) +
    section("languages", "Languages", languages) +
    '<div class="de-principle"><span>ENGINEERING FOCUS</span><strong>Reliable · Observable · Scalable</strong></div></aside>' +
    '<main class="de-main">' + section("summary", "Data Engineering Profile", summary) +
    section("experience", "Pipeline & Platform Experience", experience) +
    section("projects", "Selected Data Systems", projects) +
    section("education", "Education", education) + custom + "</main></div></div>";
  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const order = list(data.section_order);
  const nodes = Array.from(root.querySelectorAll("[data-section]"));
  order.forEach((key) => {
    const node = nodes.find((candidate) => candidate.dataset.section === key);
    if (node && node.parentElement) node.parentElement.appendChild(node);
  });
  return root.firstElementChild.outerHTML;
}
