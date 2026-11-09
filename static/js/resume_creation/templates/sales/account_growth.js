export function renderAccountGrowthTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const person = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="ag-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>' : "";
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const bullets = (items) => Array.isArray(items) ? items.filter(Boolean).map((v) => "<li>" + e(v) + "</li>").join("") : "";
  const contact = [person.email, person.phone, person.location].filter(Boolean).map(e);
  [[ "LinkedIn", person.linkedin ], [ "Portfolio", person.portfolio ], [ "Website", person.website ]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url).trim()))
      contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const experience = (data.experience || []).map((item) =>
    '<article class="ag-role"><div class="ag-role-top"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + '</time></div>' +
    ((item.bullets || item.achievements || []).length ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>").join("");
  const skills = Object.entries(data.skills_by_category || {}).filter(([, values]) => Array.isArray(values) && values.length)
    .map(([name, values]) => '<div class="ag-skill"><strong>' + e(name) + '</strong><span>' + e(values.join(" · ")) + "</span></div>").join("");
  const fallbackSkills = Array.isArray(data.skills) && data.skills.length ? '<div class="ag-skill"><span>' + e(data.skills.join(" · ")) + "</span></div>" : "";
  const education = (data.education || []).map((item) => '<article class="ag-education"><strong>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</strong><span>' + e(item.institution || "") +
    '</span><time>' + dates(item) + "</time></article>").join("");
  const projects = (data.projects || []).map((item) => '<article class="ag-case"><h3>' + e(item.name || "") +
    (item.role ? " / " + e(item.role) : "") + "</h3>" + (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") + "</article>").join("");
  const credentials = (data.certifications || []).map((item) => '<div class="ag-credential"><strong>' + e(item.name || "") +
    '</strong><span>' + e(item.issuer || "") + "</span></div>").join("");
  const languages = (data.languages || []).map((item) => '<div class="ag-language"><strong>' + e(item.language || "") +
    '</strong><span>' + e(item.proficiency || "") + "</span></div>").join("");
  const markup = '<div class="resume-template-account-growth"><header class="ag-header">' +
    '<div class="ag-brandline"><span>CLIENT PARTNERSHIPS / CUSTOMER SUCCESS</span><span>RELATIONSHIPS THAT COMPOUND</span></div>' +
    '<h1>' + e(person.full_name || "Your Name") + '</h1><p class="ag-title">' +
    e(person.professional_title || "Strategic Accounts & Customer Success Leader") + '</p><div class="ag-contact">' +
    contact.join('<span>•</span>') + '</div></header>' +
    '<div class="ag-manifesto"><span>GROWTH PHILOSOPHY</span><strong>ALIGN VALUE. EARN TRUST. EXPAND IMPACT.</strong></div>' +
    '<div class="ag-columns"><aside class="ag-sidebar">' +
    section("skills", "Customer Growth Toolkit", skills || fallbackSkills) +
    section("certifications", "Credentials", credentials) + section("languages", "Languages", languages) +
    (data.career_objective ? section("career_objective", "Relationship Focus", "<p>" + e(data.career_objective) + "</p>") : "") +
    '</aside><main class="ag-main">' + section("summary", "Leadership Snapshot", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Strategic Account Experience", experience) +
    section("projects", "Customer Impact Stories", projects) + section("education", "Education", education) +
    "</main></div></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".ag-main");
  if (main && Array.isArray(data.section_order)) {
    const nodes = Array.from(main.children);
    data.section_order.forEach((key) => { const node = nodes.find((item) => item.dataset.section === key); if (node) main.appendChild(node); });
  }
  return root.outerHTML;
}
