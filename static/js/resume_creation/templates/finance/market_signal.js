export function renderMarketSignalTemplate(content, escapeHtml) {
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
    ? '<section class="ms-section" data-section="' + key + '"><h2>' + title + "</h2>" + body + "</section>" : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, url]) => {
      if (url && /^https?:\/\//i.test(String(url).trim()))
        contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });
  const skills = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="ms-skill"><strong>' + e(category) + "</strong><span>" + e(values.join(" · ")) + "</span></div>").join("")
    || (Array.isArray(data.skills) && data.skills.length ? '<div class="ms-skill"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="ms-entry"><div class="ms-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    (((item.bullets || []).length || (item.achievements || []).length)
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") + "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="ms-entry"><div class="ms-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><p>' + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</p></div><time>" + dates(item) + "</time></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") + "</article>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="ms-project"><h3>' + e(item.name || "") + (item.role ? " · " + e(item.role) : "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length ? '<p class="ms-tools">RESEARCH TOOLS / ' + e(item.technologies.join(" · ")) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") + "</article>"
  ).join("");
  const credentials = (data.certifications || []).map((item) =>
    '<div class="ms-credential"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? "<span>" + e(item.issuer) + "</span>" : "") +
    (item.issue_date ? "<time>" + e(item.issue_date) + "</time>" : "") + "</div>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    '<div class="ms-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? "<span>" + e(item.proficiency) + "</span>" : "") + "</div>"
  ).join("");
  const custom = (data.custom_sections || []).filter((item) => Array.isArray(item.items) && item.items.length)
    .map((item) => section("custom", e(item.title || "Additional Research"), item.items.map((entry) =>
      '<article class="ms-entry"><h3>' + e(entry.title || "") + (entry.subtitle ? " — " + e(entry.subtitle) : "") + "</h3>" +
      (entry.date ? "<time>" + e(entry.date) + "</time>" : "") +
      (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
      (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") + "</article>"
    ).join(""))).join("");
  const markup = '<div class="resume-template-market-signal"><header class="ms-header">' +
    '<div class="ms-topline"><span>MARKET SIGNAL / RESEARCH NOTE</span><span>INVESTMENT · EQUITY · PORTFOLIO</span></div>' +
    '<h1>' + e(personal.full_name || "Your Name") + "</h1>" +
    '<p class="ms-title">' + e(personal.professional_title || "Investment Research Professional") + "</p>" +
    '<div class="ms-contact">' + contact.join('<span aria-hidden="true">/</span>') + "</div></header>" +
    '<div class="ms-thesis"><span>INVESTMENT APPROACH</span><strong>RESEARCH WITH CONVICTION. DECISIONS WITH DISCIPLINE.</strong></div>' +
    '<div class="ms-layout"><aside class="ms-rail">' + section("skills", "Research Toolkit", skills) +
    section("certifications", "Credentials", credentials) + section("languages", "Languages", languages) +
    (data.career_objective ? section("career_objective", "Investment Focus", "<p>" + e(data.career_objective) + "</p>") : "") +
    '</aside><main class="ms-main">' +
    section("summary", "Investment Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Research & Investment Experience", experience) +
    section("projects", "Selected Research & Portfolio Work", projects) +
    section("education", "Education & Financial Studies", education) + custom + "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".ms-main");
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
