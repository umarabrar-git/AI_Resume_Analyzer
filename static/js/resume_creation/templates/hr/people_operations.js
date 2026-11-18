export function renderPeopleOperationsTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }[char]));
  const data = content || {};
  const person = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="po-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>'
    : "";
  const list = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const dateRange = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" — ");
  const contact = [person.email, person.phone, person.location].filter(Boolean).map(e);
  [["LinkedIn", person.linkedin], ["Portfolio", person.portfolio], ["Website", person.website]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url).trim())) {
      contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    }
  });
  const skills = Object.entries(data.skills_by_category || {})
    .filter(([, values]) => Array.isArray(values) && values.length)
    .map(([category, values]) => '<div class="po-skill"><strong>' + e(category) + '</strong><span>' + e(values.join(" · ")) + "</span></div>")
    .join("") || ((data.skills || []).length ? "<p>" + e(data.skills.join(" · ")) + "</p>" : "");
  const experience = (data.experience || []).map((item) =>
    '<article class="po-role"><div class="po-role-head"><div><h3>' + e(item.title || "") + '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") + '</p></div><time>' + dateRange(item) + "</time></div>" +
    ((item.bullets || item.achievements || []).length ? "<ul>" + list([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="po-case"><span>PEOPLE INITIATIVE / IMPACT</span><h3>' + e(item.name || "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + list(item.achievements) + "</ul>" : "") +
    "</article>"
  ).join("");
  const education = (data.education || []).map((item) =>
    '<article class="po-education"><strong>' + e(item.degree || "") + (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</strong><span>' + e(item.institution || "") + '</span><time>' + dateRange(item) + "</time></article>"
  ).join("");
  const certifications = (data.certifications || []).map((item) =>
    '<p class="po-credential"><strong>' + e(item.name || "") + "</strong><span>" + e(item.issuer || "") + "</span></p>"
  ).join("");
  const markup =
    '<div class="resume-template-people-operations">' +
      '<header class="po-header"><div class="po-kicker">PEOPLE STRATEGY / CULTURE / PERFORMANCE</div>' +
        '<h1>' + e(person.full_name || "Your Name") + '</h1>' +
        '<p class="po-title">' + e(person.professional_title || "People & Culture Professional") + '</p>' +
        '<div class="po-contact">' + contact.join("<span>•</span>") + "</div></header>" +
      '<div class="po-principles"><div><b>ATTRACT</b><span>Build strong talent pipelines</span></div>' +
        '<div><b>ENABLE</b><span>Design meaningful employee journeys</span></div>' +
        '<div><b>MEASURE</b><span>Turn people insights into action</span></div></div>' +
      '<div class="po-layout"><aside class="po-sidebar">' +
        section("skills", "People Practice", skills) +
        section("education", "Education", education) +
        section("certifications", "Credentials", certifications) +
        (data.career_objective ? section("career_objective", "People Mission", "<p>" + e(data.career_objective) + "</p>") : "") +
      '</aside><main class="po-main">' +
        section("summary", "People Strategy Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
        section("experience", "People & Culture Experience", experience) +
        section("projects", "Workforce Initiatives", projects) +
      "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root && root.querySelector(".po-main");
  if (main && Array.isArray(data.section_order)) {
    const nodes = Array.from(main.children);
    data.section_order.forEach((key) => {
      const node = nodes.find((item) => item.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return root ? root.outerHTML : "";
}
