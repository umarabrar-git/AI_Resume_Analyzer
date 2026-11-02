export function renderModelCardTemplate(content, escapeHtml) {
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
    return start || end ? e(start) + (start && end ? " — " : "") + e(end) : "";
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, body) => body
    ? '<section data-section="' + e(key) + '"><div class="mc-section-heading"><span>' +
      e(String(list(data.section_order).indexOf(key) + 1).padStart(2, "0")) +
      '</span><h2>' + e(title) + "</h2></div>" + body + "</section>" : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => { const url = safeUrl(value); if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>"); });
  const skills = Array.isArray(data.skills) ? data.skills : Object.values(data.skills_by_category || {}).flat();
  const groups = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skillMarkup = groups.length
    ? groups.map(([name, values]) => '<div class="mc-skill-group"><h3>' + e(name) + '</h3><div class="mc-tags">' +
      values.map((value) => '<span>' + e(value) + "</span>").join("") + "</div></div>").join("")
    : '<div class="mc-tags">' + skills.map((value) => "<span>" + e(value) + "</span>").join("") + "</div>";
  const experience = list(data.experience).map((item) =>
    '<article class="mc-entry"><div class="mc-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="mc-muted">' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length ? '<div class="mc-impact"><b>PRODUCTION IMPACT</b><ul>' + bullets(item.achievements) + "</ul></div>" : "") +
    "</article>").join("");
  const projects = list(data.projects).map((item) =>
    '<article class="mc-project"><div class="mc-entry-head"><div><h3>' + e(item.name || "") +
    '</h3><p class="mc-muted">' + e(item.role || "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="mc-stack"><b>STACK</b> ' + e(item.technologies.join(" / ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (safeUrl(item.url) ? '<a class="mc-project-link" href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">Explore project ↗</a>' : "") +
    "</article>").join("");
  const education = list(data.education).map((item) =>
    '<article class="mc-entry"><div class="mc-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " · " + e(item.field_of_study) : "") + '</h3><p class="mc-muted">' +
    e(item.institution || "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.coursework ? "<p>" + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>").join("");
  const certifications = list(data.certifications).map((item) =>
    '<p class="mc-credential"><b>' + e(item.name || "") + "</b>" +
    (item.issuer ? " · " + e(item.issuer) : "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>").join("");
  const languages = list(data.languages).map((item) =>
    '<p class="mc-credential"><b>' + e(item.language || "") + "</b>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>").join("");
  const custom = list(data.custom_sections).filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Work",
      list(item.items).map((entry) => '<article class="mc-entry"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + "</h3>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join(""))).join("");
  const metrics = [["MODELS & PROJECTS", list(data.projects).length], ["EXPERIENCE", list(data.experience).length],
    ["TECHNICAL SKILLS", skills.length], ["CREDENTIALS", list(data.certifications).length]];
  root.innerHTML = '<div class="resume-template-model-card"><header class="mc-header"><div class="mc-identity">' +
    '<p class="mc-eyebrow"><span class="mc-pulse"></span> MACHINE LEARNING / ENGINEERING PROFILE</p><h1>' +
    e(personal.full_name || "Your Name") + '</h1><p class="mc-role">' + e(personal.professional_title || "AI / ML Engineer") +
    '</p><div class="mc-contact">' + contact.join('<span class="mc-dot">/</span>') + '</div></div>' +
    '<div class="mc-monogram" aria-hidden="true">ML<span>_</span></div></header>' +
    '<div class="mc-metrics">' + metrics.map(([label, value]) => '<div><strong>' + e(value) + '</strong><span>' + e(label) + "</span></div>").join("") +
    '</div><main>' + section("summary", "Engineering Thesis", data.summary ? '<p class="mc-summary">' + e(data.summary) + "</p>" : "") +
    section("projects", "Model Portfolio & Applied Systems", projects) +
    section("experience", "Professional Experience", experience) +
    section("skills", "Technical Stack & Methods", skillMarkup) +
    section("education", "Education & Research Foundation", education) +
    section("certifications", "Credentials & Responsible AI", certifications) +
    section("languages", "Languages", languages) + custom + "</main><footer class=\"mc-footer\">BUILD · VALIDATE · DEPLOY · MONITOR</footer></div>";
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
