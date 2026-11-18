export function renderTerritoryStrategistTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const person = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="ts-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>' : "";
  const bullets = (items) => Array.isArray(items) ? items.filter(Boolean).map((value) => "<li>" + e(value) + "</li>").join("") : "";
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")].filter(Boolean).map(e).join(" – ");
  const contact = [person.email, person.phone, person.location].filter(Boolean).map(e);
  [["LinkedIn", person.linkedin], ["Portfolio", person.portfolio], ["Website", person.website]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url).trim())) contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const experience = (data.experience || []).map((item) =>
    '<article class="ts-role"><div class="ts-role-head"><div><h3>' + e(item.title || "") + '</h3><p>' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + '</p></div><time>' + dates(item) + "</time></div>" +
    ((item.bullets || item.achievements || []).length ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") + "</article>").join("");
  const skills = Object.entries(data.skills_by_category || {}).filter(([, values]) => Array.isArray(values) && values.length)
    .map(([name, values]) => '<div class="ts-skill"><strong>' + e(name) + '</strong><span>' + e(values.join(" · ")) + "</span></div>").join("");
  const fallbackSkills = Array.isArray(data.skills) && data.skills.length ? '<div class="ts-skill"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "";
  const education = (data.education || []).map((item) => '<article class="ts-education"><strong>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</strong><span>' + e(item.institution || "") + '</span><time>' + dates(item) + "</time></article>").join("");
  const projects = (data.projects || []).map((item) => '<article class="ts-project"><h3>' + e(item.name || "") +
    (item.role ? " / " + e(item.role) : "") + "</h3>" + (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") + "</article>").join("");
  const credentials = (data.certifications || []).map((item) => '<div class="ts-credential"><strong>' + e(item.name || "") + '</strong><span>' + e(item.issuer || "") + "</span></div>").join("");
  const languages = (data.languages || []).map((item) => '<div class="ts-language"><strong>' + e(item.language || "") + '</strong><span>' + e(item.proficiency || "") + "</span></div>").join("");
  const markup = '<div class="resume-template-territory-strategist"><header class="ts-header">' +
    '<div class="ts-kicker"><span>SALES STRATEGY / TERRITORY DEVELOPMENT</span><span>PLAN WITH PRECISION. GROW WITH PURPOSE.</span></div>' +
    '<h1>' + e(person.full_name || "Your Name") + '</h1><p class="ts-title">' + e(person.professional_title || "Territory & Strategic Sales Leader") +
    '</p><div class="ts-contact">' + contact.join('<span>•</span>') + "</div></header>" +
    '<div class="ts-principles"><div><strong>01 / MAP</strong><span>Market opportunity</span></div><div><strong>02 / PRIORITIZE</strong><span>Pipeline discipline</span></div><div><strong>03 / DELIVER</strong><span>Durable revenue</span></div></div>' +
    '<div class="ts-layout"><aside class="ts-sidebar">' + section("skills", "Territory Toolkit", skills || fallbackSkills) +
    section("certifications", "Sales Credentials", credentials) + section("languages", "Markets & Languages", languages) +
    (data.career_objective ? section("career_objective", "Commercial Focus", "<p>" + e(data.career_objective) + "</p>") : "") +
    '</aside><main class="ts-main">' + section("summary", "Commercial Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Territory & Revenue Experience", experience) + section("projects", "Market Expansion Initiatives", projects) +
    section("education", "Education", education) +
    (Array.isArray(data.custom_sections) ? data.custom_sections.map((item, index) => section("custom_" + index, e(item.title || "Additional Experience"),
      (item.items || []).map((entry) => "<p>" + e(entry.description || entry.title || "") + "</p>").join(""))).join("") : "") +
    "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".ts-main");
  if (main && Array.isArray(data.section_order)) {
    const nodes = Array.from(main.children);
    data.section_order.forEach((key) => { const node = nodes.find((item) => item.dataset.section === key); if (node) main.appendChild(node); });
  }
  return root.outerHTML;
}
