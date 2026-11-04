export function renderDiscoveryResearchTemplate(content, escapeHtml) {
  const root = document.createElement("div");
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
  const section = (key, title, html) => html
    ? '<section data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + html + "</section>" : "";
  const contact = [];
  [personal.email, personal.phone, personal.location].filter(Boolean).forEach((item) => contact.push(e(item)));
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => { const url = safeUrl(value); if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>"); });

  const skillsSource = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter((entry) => Array.isArray(entry[1]) && entry[1].length)
    : [];
  const allSkills = Array.isArray(data.skills) ? data.skills : skillsSource.flatMap((entry) => entry[1]);
  const skills = allSkills.length
    ? '<ul class="dr-skill-list">' + allSkills.map((skill) => "<li>" + e(skill) + "</li>").join("") + "</ul>" : "";
  const experience = list(data.experience).map((item) =>
    '<article class="dr-entry"><div class="dr-entry-heading"><div><h3>' + e(item.title || "") +
    '</h3><p class="dr-muted">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    '<p class="dr-date">' + dates(item) + "</p></div>" +
    (item.summary ? '<p class="dr-evidence">' + e(item.summary) + "</p>" : "") +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<p class="dr-metric"><strong>Research impact:</strong> ' + item.achievements.map((x) => e(x)).join(" · ") + "</p>" : "") +
    "</article>"
  ).join("");
  const projects = list(data.projects).map((item) =>
    '<article class="dr-project"><div class="dr-entry-heading"><div><h3>' + e(item.name || "") +
    (item.role ? ' <span class="dr-muted">· ' + e(item.role) + "</span>" : "") + "</h3></div>" +
    '<p class="dr-date">' + dates(item) + "</p></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? '<p class="dr-metric">' + item.achievements.map((x) => e(x)).join(" · ") + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="dr-muted"><strong>Methods & tools:</strong> ' + item.technologies.map((x) => e(x)).join(", ") + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View case study</a></p>' : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="dr-entry"><div class="dr-entry-heading"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="dr-muted">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    '<p class="dr-date">' + dates(item) + "</p></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="dr-compact"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="dr-compact"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections).filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items).map((entry) =>
        '<article class="dr-entry"><div class="dr-entry-heading"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><p class="dr-date">' + e(entry.date || "") + "</p></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
      ).join("")
    )).join("");

  root.innerHTML =
    '<div class="resume-template-discovery-research"><header class="dr-header"><div class="dr-kicker">PRODUCT DISCOVERY / RESEARCH</div>' +
    '<div class="dr-identity"><div><h1>' + e(personal.full_name || "Your Name") + '</h1><p class="dr-title">' +
    e(personal.professional_title || "") + '</p></div><div class="dr-contact">' + contact.join(' <span aria-hidden="true">•</span> ') +
    '</div></div><div class="dr-positioning">' + (data.summary ? e(data.summary) : "") + "</div></header><main>" +
    section("skills", "Research toolkit", skills) +
    section("experience", "Research & discovery experience", experience) +
    section("projects", "Selected studies & case work", projects) +
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
    order.forEach((key) => { const node = children.find((child) => child.dataset.section === key); if (node) main.appendChild(node); });
  }
  return root.firstElementChild.outerHTML;
}
