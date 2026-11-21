const esc = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));
const safe = (escapeHtml, value) => typeof escapeHtml === "function" ? escapeHtml(value) : esc(value);

export function renderPropertyPortfolioTemplate(content, escapeHtml) {
  const e = (value) => safe(escapeHtml, value);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const list = (value) => Array.isArray(value) ? value : [];
  const dateRange = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="pp-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>'
    : "";

  const experience = list(data.experience).map((item) =>
    '<article class="pp-role"><div class="pp-role-head"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dateRange(item) + '</time></div>' +
    (item.summary ? "<p>" + e(item.summary) + "</p>" : "") +
    (list(item.bullets).length ? "<ul>" + list(item.bullets).map((value) => "<li>" + e(value) + "</li>").join("") + "</ul>" : "") +
    (list(item.achievements).length ? '<p class="pp-impact"><b>Portfolio impact</b> · ' + list(item.achievements).map(e).join(" · ") + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = list(data.projects).map((item) =>
    '<article class="pp-project"><h3>' + e(item.name || "") + '</h3>' +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (list(item.technologies).length ? '<p class="pp-meta"><b>Focus</b> · ' + list(item.technologies).map(e).join(" · ") + "</p>" : "") +
    (list(item.achievements).length ? "<ul>" + list(item.achievements).map((value) => "<li>" + e(value) + "</li>").join("") + "</ul>" : "") +
    "</article>"
  ).join("");

  const skillsByCategory = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<p class="pp-skill"><b>' + e(category) + '</b><span>' + values.map(e).join(" · ") + "</span></p>")
    .join("");
  const skills = skillsByCategory || (list(data.skills).length ? "<p>" + list(data.skills).map(e).join(" · ") + "</p>" : "");
  const education = list(data.education).map((item) =>
    "<p><b>" + e(item.degree || "") + "</b> · " + e(item.institution || "") +
    " <time>" + dateRange(item) + "</time></p>"
  ).join("");
  const certifications = list(data.certifications).map((item) =>
    "<p>" + e(item.name || "") + (item.issuer ? " · " + e(item.issuer) : "") + "</p>"
  ).join("");

  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["Website", personal.website], ["Portfolio", personal.portfolio]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url))) {
      contact.push('<a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    }
  });

  const root = document.createElement("div");
  root.innerHTML =
    '<div class="resume-template-property-portfolio">' +
      '<header class="pp-header">' +
        '<div class="pp-overline"><span>REAL ESTATE / PROPERTY / ASSET STRATEGY</span><span>PROFESSIONAL PORTFOLIO</span></div>' +
        '<div class="pp-heading"><div><p class="pp-kicker">ASSETS · PLACES · PERFORMANCE</p><h1>' + e(personal.full_name || "Your Name") +
        '</h1><p class="pp-role-title">' + e(personal.professional_title || "Real Estate & Property Professional") +
        '</p></div><div class="pp-seal" aria-hidden="true"><span>RE</span><i></i><i></i></div></div>' +
        '<div class="pp-contact">' + contact.join('<span>•</span>') + "</div>" +
      "</header>" +
      '<div class="pp-thesis"><span>VALUE PROPOSITION</span><strong>' +
        e(data.summary || "Creating stronger property outcomes through disciplined asset management, informed decisions and exceptional stakeholder service.") +
      "</strong></div>" +
      '<div class="pp-layout"><aside class="pp-sidebar">' +
        section("skills", "Property Expertise", skills) +
        section("certifications", "Credentials & Tools", certifications) +
        section("education", "Education", education) +
      '</aside><main class="pp-main">' +
        section("experience", "Career & Asset Experience", experience) +
        section("projects", "Selected Property Projects", projects) +
      '</main></div>' +
      '<footer class="pp-footer"><span>PROPERTY PORTFOLIO</span><span>ASSET VALUE · OCCUPIER EXPERIENCE · LONG-TERM STEWARDSHIP</span></footer>' +
    "</div>";

  const sections = root.firstElementChild.querySelectorAll("[data-section]");
  list(data.section_order).forEach((key) => {
    const node = Array.from(sections).find((item) => item.dataset.section === key);
    if (node && node.parentElement) node.parentElement.appendChild(node);
  });
  return root.firstElementChild.outerHTML;
}
