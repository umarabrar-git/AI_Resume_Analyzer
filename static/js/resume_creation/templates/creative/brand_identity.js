export function renderBrandIdentityTemplate(content, escapeHtml) {
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const list = (value) => Array.isArray(value) ? value : [];
  const hidden = new Set(list(data.hidden_sections));
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const section = (key, title, body) => body
    ? '<section data-section="' + e(key) + '"><div class="bi-section-heading"><span>' +
      e(String(list(data.section_order).indexOf(key) + 1).padStart(2, "0")) +
      '</span><h2>' + e(title) + '</h2></div>' + body + '</section>' : "";
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const projects = list(data.projects).map((item, index) =>
    '<article class="bi-case"><div class="bi-case-index">CASE ' + e(String(index + 1).padStart(2, "0")) +
    '</div><div class="bi-case-body"><h3>' + e(item.name || "") + '</h3>' +
    (item.role ? '<p class="bi-role">' + e(item.role) + '</p>' : "") +
    (item.description ? '<p>' + e(item.description) + '</p>' : "") +
    (list(item.achievements).length ? '<ul>' + bullets(item.achievements) + '</ul>' : "") +
    (list(item.technologies).length ? '<p class="bi-tools">DISCIPLINES / ' + e(item.technologies.join(" · ")) + '</p>' : "") +
    (safeUrl(item.url) ? '<a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View case study ↗</a>' : "") +
    '</div></article>'
  ).join("");
  const experience = list(data.experience).map((item) =>
    '<article class="bi-entry"><div><h3>' + e(item.title || "") + '</h3><p>' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + '</p></div><span>' +
    e(item.start_date || "") + (item.start_date && (item.end_date || item.current) ? " — " : "") +
    e(item.current ? "Present" : (item.end_date || "")) + '</span>' +
    (list(item.bullets).length ? '<ul>' + bullets(item.bullets) + '</ul>' : "") + '</article>'
  ).join("");
  const education = list(data.education).map((item) =>
    '<article class="bi-entry"><div><h3>' + e(item.degree || "") + '</h3><p>' +
    e(item.institution || "") + (item.field_of_study ? " · " + e(item.field_of_study) : "") +
    '</p></div><span>' + e(item.end_date || item.start_date || "") + '</span></article>'
  ).join("");
  const skillGroups = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skills = skillGroups.length
    ? skillGroups.map(([name, values]) => '<div class="bi-skill-group"><h3>' + e(name) + '</h3><p>' +
      values.map(e).join(" / ") + '</p></div>').join("")
    : list(data.skills).map(e).join(" / ");
  const contacts = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [[ "Portfolio", personal.portfolio ], [ "Website", personal.website ], [ "LinkedIn", personal.linkedin ]].forEach(([label, value]) => {
    const url = safeUrl(value);
    if (url) contacts.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + ' ↗</a>');
  });
  const custom = list(data.custom_sections).filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + item.id, item.title || "Additional Information",
      list(item.items).map((entry) => '<article class="bi-entry"><div><h3>' + e(entry.title || "") +
      '</h3><p>' + e(entry.subtitle || entry.description || "") + '</p></div></article>').join(""))).join("");
  const html = '<div class="resume-template-brand-identity"><header class="bi-masthead">' +
    '<div class="bi-mark">B/I <span>CREATIVE PRACTICE</span></div><div class="bi-contact">' + contacts.join('<span>·</span>') +
    '</div></header><main><section class="bi-hero"><p class="bi-eyebrow">BRAND / DESIGN / DIRECTION</p><h1>' +
    e(personal.full_name || "Your Name") + '</h1><p class="bi-title">' + e(personal.professional_title || "Brand Identity Designer") +
    '</p>' + (data.summary ? '<p class="bi-summary">' + e(data.summary) + '</p>' : "") +
    '<div class="bi-color-strip" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div></section>' +
    section("projects", "Selected Identity Work", projects) + section("experience", "Practice & Experience", experience) +
    section("skills", "Design Languages & Tools", skills) + section("education", "Education", education) + custom +
    '</main><footer class="bi-footer"><span>SELECTED WORK / PROFILE</span><span>' + e(personal.location || "") + '</span></footer></div>';
  const holder = document.createElement("div");
  holder.innerHTML = html;
  holder.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const main = holder.querySelector("main");
  const order = list(data.section_order);
  if (main && order.length) {
    const children = Array.from(main.children);
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return holder.firstElementChild.outerHTML;
}
