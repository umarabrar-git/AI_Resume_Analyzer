export function renderInsightGridTemplate(content, escapeHtml) {
  const root = document.createElement("div");
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
    return start || end ? e(start) + (start && end ? " – " : "") + e(end) : "";
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, body) => body
    ? '<section data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + body + "</section>"
    : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skills = Array.isArray(data.skills) ? data.skills : Object.values(data.skills_by_category || {}).flat();
  const categories = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skillHtml = categories.length
    ? categories.map(([name, values]) => '<div class="ig-skill-group"><h3>' + e(name) + '</h3><div class="ig-tags">' +
      values.map((value) => '<span>' + e(value) + '</span>').join("") + "</div></div>").join("")
    : (skills.length ? '<div class="ig-tags">' + skills.map((value) => "<span>" + e(value) + "</span>").join("") + "</div>" : "");
  const experience = list(data.experience).map((item) =>
    '<article class="ig-entry"><div class="ig-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="ig-muted">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<div class="ig-proof"><strong>Measured impact</strong><ul>' + bullets(item.achievements) + "</ul></div>" : "") +
    "</article>"
  ).join("");
  const projects = list(data.projects).map((item) =>
    '<article class="ig-project"><div class="ig-entry-head"><h3>' + e(item.name || "") +
    (item.role ? " · " + e(item.role) : "") + "</h3>" +
    ((item.start_date || item.end_date) ? "<time>" + dates(item) + "</time>" : "") + "</div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.technologies && item.technologies.length ? '<p class="ig-muted"><strong>Stack:</strong> ' + e(item.technologies.join(", ")) + "</p>" : "") +
    (safeUrl(item.url) ? '<a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View project</a>' : "") +
    "</article>"
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="ig-entry"><div class="ig-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p class="ig-muted">' +
    e(item.institution || "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.coursework ? "<p><strong>Relevant study:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="ig-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="ig-credential"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = list(data.custom_sections).filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items).map((entry) => '<article class="ig-entry"><div class="ig-entry-head"><h3>' +
        e(entry.title || "") + (entry.subtitle ? " · " + e(entry.subtitle) : "") +
        "</h3><time>" + e(entry.date || "") + "</time></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join("")
    )).join("");
  const highlights = [
    ["Experience", list(data.experience).length],
    ["Analysis projects", list(data.projects).length],
    ["Skills", skills.length],
    ["Credentials", list(data.certifications).length]
  ];
  root.innerHTML = '<div class="resume-template-insight-grid"><header class="ig-header"><div>' +
    '<p class="ig-eyebrow">Analytics & Business Intelligence</p><h1>' + e(personal.full_name || "Your Name") +
    '</h1><p class="ig-role">' + e(personal.professional_title || "") + '</p><div class="ig-contact">' +
    contact.join("<span> / </span>") + '</div></div><div class="ig-monogram" aria-hidden="true">IG</div></header>' +
    '<section class="ig-highlights" aria-label="Profile highlights">' + highlights.map(([label, value], index) =>
      '<div class="ig-highlight"><span>0' + (index + 1) + " / " + e(label) + '</span><strong>' + e(value) + "</strong></div>"
    ).join("") + '</section><main>' +
    section("summary", "Analytical Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Experience & Business Impact", experience) +
    section("projects", "Data & BI Projects", projects) +
    section("skills", "Analytics Toolkit", skillHtml) +
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
