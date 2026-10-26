export function renderCapitalBriefTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("") : "";
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="cb-section" data-section="' + key + '"><h2>' + title + "</h2>" + body + "</section>" : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, url]) => {
      if (url && /^https?:\/\//i.test(String(url).trim()))
        contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skills = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="cb-skill"><strong>' + e(category) + "</strong><span>" + e(values.join(" · ")) + "</span></div>").join("")
    || (Array.isArray(data.skills) && data.skills.length ? '<div class="cb-skill"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="cb-entry"><div class="cb-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    (((item.bullets || []).length || (item.achievements || []).length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") + "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="cb-entry"><div class="cb-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p>' + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") + "</article>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="cb-project"><div><h3>' + e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="cb-tools">TOOLS / ' + e(item.technologies.join(" · ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") + "</div></article>"
  ).join("");
  const certifications = (data.certifications || []).map((item) =>
    '<div class="cb-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<time>" + e(item.issue_date) + "</time>" : "") + "</div>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="cb-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>"
  ).join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => section("custom", e(item.title || "Additional Information"), item.items.map((entry) =>
      '<article class="cb-entry"><h3>' + e(entry.title || "") + (entry.subtitle ? " — " + e(entry.subtitle) : "") + "</h3>" +
      (entry.date ? "<time>" + e(entry.date) + "</time>" : "") +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
    ).join(""))).join("");
  const markup = '<div class="resume-template-capital-brief"><header class="cb-header">' +
    '<div class="cb-topline"><span>CAPITAL BRIEF</span><span>FINANCE / STRATEGY / PERFORMANCE</span></div>' +
    '<h1>' + e(personal.full_name || "Your Name") + "</h1>" +
    '<p class="cb-title">' + e(personal.professional_title || "Finance & Strategy Professional") + "</p>" +
    '<div class="cb-contact">' + contact.join('<span aria-hidden="true">/</span>') + "</div></header>" +
    '<div class="cb-metrics" aria-label="Professional focus"><div><strong>01</strong><span>ANALYZE</span></div>' +
    '<div><strong>02</strong><span>OPTIMIZE</span></div><div><strong>03</strong><span>DELIVER</span></div></div>' +
    '<div class="cb-layout"><aside class="cb-rail">' + section("skills", "Capabilities", skills) +
    section("certifications", "Credentials", certifications) + section("languages", "Languages", languages) +
    (data.career_objective ? section("career_objective", "Career Focus", "<p>" + e(data.career_objective) + "</p>") : "") +
    "</aside><main class="cb-main">" +
    section("summary", "Executive Summary", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Experience", experience) + section("projects", "Selected Analysis & Projects", projects) +
    section("education", "Education", education) + custom + "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".cb-main");
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return root.outerHTML;
}
