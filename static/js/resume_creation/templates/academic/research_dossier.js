export function renderResearchDossierTemplate(content, escapeHtml) {
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return [start, end].filter(Boolean).map(e).join(" – ");
  };
  const bullets = (items) => Array.isArray(items) && items.length
    ? "<ul>" + items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("") + "</ul>" : "";
  const section = (key, title, body, cls = "") => body
    ? '<section data-section="' + key + '" class="' + cls + '"><h2>' + e(title) + "</h2>" + body + "</section>" : "";

  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Google Scholar", personal.google_scholar],
    ["ORCID", personal.orcid], ["Website", personal.website], ["Portfolio", personal.portfolio]]
    .forEach(([label, raw]) => {
      const url = safeUrl(raw);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const skills = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="rd-skill"><strong>' + e(category) + "</strong><span>" + e(values.join(", ")) + "</span></div>")
    .join("") || (Array.isArray(data.skills) && data.skills.length
      ? '<div class="rd-skill"><span>' + e(data.skills.join(", ")) + "</span></div>" : "");

  const experience = (data.experience || []).map((item) =>
    '<article class="rd-entry"><div class="rd-entry-head"><h3>' + e(item.title || "") +
    '</h3><time>' + dates(item) + "</time></div><p class=\"rd-meta\">" + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</p>" +
    bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</article>").join("");

  const education = (data.education || []).map((item) =>
    '<article class="rd-entry"><div class="rd-entry-head"><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><time>' + dates(item) +
    "</time></div><p class=\"rd-meta\">" + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</p>" +
    (item.coursework ? "<p>Coursework: " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>").join("");

  const projects = (data.projects || []).map((item, index) =>
    '<article class="rd-project"><span class="rd-project-number">' + String(index + 1).padStart(2, "0") +
    '</span><div><h3>' + e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="rd-meta">Methods: ' + e(item.technologies.join(", ")) + "</p>" : "") +
    bullets(item.achievements) +
    (safeUrl(item.url) ? '<a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">Project link ↗</a>' : "") +
    "</div></article>").join("");

  const certifications = (data.certifications || []).map((item) =>
    '<p class="rd-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? '<time>' + e(item.issue_date) + "</time>" : "") + "</p>").join("");

  const languages = (data.languages || []).map((item) =>
    '<p class="rd-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</p>").join("");

  const custom = (data.custom_sections || [])
    .filter((item) => item.items && item.items.length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + e(item.id || ""), item.title || "Additional Research",
      item.items.map((entry) => '<article class="rd-entry"><div class="rd-entry-head"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><time>' + e(entry.date || "") +
        "</time></div>" + (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        bullets(entry.bullets) + "</article>").join(""))).join("");

  const html = '<div class="resume-template-research-dossier"><header class="rd-header">' +
    '<div class="rd-header-top"><span>Research dossier / CV</span><span>' + e(personal.location || "") + "</span></div>" +
    "<h1>" + e(personal.full_name || "Your Name") + "</h1><p class=\"rd-title\">" +
    e(personal.professional_title || "") + '</p><div class="rd-contact">' + contact.join("<span> / </span>") +
    '</div><div class="rd-focus"><span>RESEARCH PROFILE</span><div>' + e(data.summary || "") +
    "</div></div></header><main class=\"rd-grid\"><div class=\"rd-primary\">" +
    section("experience", "Research & Professional Experience", experience) +
    section("projects", "Selected Research Projects", projects) +
    section("education", "Education", education) + custom +
    '</div><aside class="rd-secondary">' +
    section("skills", "Methods & Skills", skills) +
    section("career_objective", "Research Direction", data.career_objective ? "<p>" + e(data.career_objective) + "</p>" : "") +
    section("certifications", "Credentials", certifications) +
    section("languages", "Languages", languages) +
    "</aside></main></div>";

  const root = document.createElement("div");
  root.innerHTML = html;
  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const main = root.querySelector(".rd-primary");
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
window.renderResearchDossierTemplate = renderResearchDossierTemplate;
