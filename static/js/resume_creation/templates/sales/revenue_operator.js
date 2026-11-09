export function renderRevenueOperatorTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const person = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="ro-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>' : "";
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const list = (items) => Array.isArray(items) ? items.filter(Boolean).map((v) => "<li>" + e(v) + "</li>").join("") : "";
  const contact = [person.email, person.phone, person.location].filter(Boolean).map(e);
  [[ "LinkedIn", person.linkedin ], [ "Portfolio", person.portfolio ], [ "Website", person.website ]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url).trim()))
      contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const experience = (data.experience || []).map((item) =>
    '<article class="ro-entry"><div class="ro-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    ((item.bullets || item.achievements || []).length ? "<ul>" + list([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>").join("");
  const skills = Object.entries(data.skills_by_category || {}).filter(([, values]) => Array.isArray(values) && values.length)
    .map(([name, values]) => '<div class="ro-skill"><strong>' + e(name) + '</strong><span>' + e(values.join(" · ")) + "</span></div>").join("")
    || (data.skills || []).length ? '<div class="ro-skill"><span>' + e((data.skills || []).join(" · ")) + "</span></div>" : "";
  const education = (data.education || []).map((item) =>
    '<article class="ro-entry"><h3>' + e(item.degree || "") + (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><p>' + e(item.institution || "") + '</p><time>' + dates(item) + "</time></article>").join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="ro-entry"><h3>' + e(item.name || "") + '</h3>' +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + list(item.achievements) + "</ul>" : "") + "</article>").join("");
  const credentials = (data.certifications || []).map((item) => '<p><strong>' + e(item.name || "") + '</strong>' +
    (item.issuer ? " · " + e(item.issuer) : "") + "</p>").join("");
  const markup = '<div class="resume-template-revenue-operator"><header class="ro-header">' +
    '<div class="ro-kicker">SALES / REVENUE OPERATIONS</div><h1>' + e(person.full_name || "Your Name") + '</h1>' +
    '<p class="ro-title">' + e(person.professional_title || "Sales & Business Development Professional") + '</p>' +
    '<div class="ro-contact">' + contact.join('<span>/</span>') + '</div></header>' +
    '<div class="ro-proof"><div><strong>PIPELINE</strong><span>Build qualified opportunity flow</span></div>' +
    '<div><strong>CONVERSION</strong><span>Move deals with buyer insight</span></div>' +
    '<div><strong>RETENTION</strong><span>Grow durable customer value</span></div></div>' +
    '<main class="ro-main">' + section("summary", "Revenue Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Sales & Commercial Experience", experience) +
    section("projects", "Selected Wins & Initiatives", projects) +
    section("skills", "Sales Toolkit", skills) +
    section("education", "Education", education) +
    section("certifications", "Certifications", credentials) +
    (data.career_objective ? section("career_objective", "Career Focus", "<p>" + e(data.career_objective) + "</p>") : "") +
    "</main></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".ro-main");
  if (main && Array.isArray(data.section_order)) {
    const nodes = Array.from(main.children);
    data.section_order.forEach((key) => { const node = nodes.find((item) => item.dataset.section === key); if (node) main.appendChild(node); });
  }
  return root.outerHTML;
}
