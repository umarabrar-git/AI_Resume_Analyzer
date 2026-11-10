export function renderServiceStandardTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  const data = content || {};
  const person = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const section = (key, title, body) => body && !hidden.has(key)
    ? '<section class="ss-section" data-section="' + key + '"><h2>' + title + '</h2>' + body + '</section>' : "";
  const dates = (item) => [item.start_date || "", item.current ? "Present" : (item.end_date || "")]
    .filter(Boolean).map(e).join(" – ");
  const bullets = (items) => Array.isArray(items) ? items.filter(Boolean).map((value) => "<li>" + e(value) + "</li>").join("") : "";
  const contact = [person.email, person.phone, person.location].filter(Boolean).map(e);
  [["LinkedIn", person.linkedin], ["Portfolio", person.portfolio], ["Website", person.website]].forEach(([label, url]) => {
    if (url && /^https?:\/\//i.test(String(url).trim()))
      contact.push('<a href="' + e(String(url).trim()) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
  });
  const experience = (data.experience || []).map((item) =>
    '<article class="ss-role"><div class="ss-role-head"><div><h3>' + e(item.title || "") +
    '</h3><p>' + e(item.company || "") + (item.location ? " · " + e(item.location) : "") +
    '</p></div><time>' + dates(item) + "</time></div>" +
    ((item.bullets || item.achievements || []).length ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>").join("");
  const skills = Object.entries(data.skills_by_category || {}).filter(([, values]) => Array.isArray(values) && values.length)
    .map(([name, values]) => '<div class="ss-skill"><strong>' + e(name) + '</strong><span>' + e(values.join(" · ")) + "</span></div>").join("");
  const skillList = skills || (Array.isArray(data.skills) && data.skills.length
    ? '<p class="ss-skill-list">' + e(data.skills.join(" · ")) + "</p>" : "");
  const education = (data.education || []).map((item) =>
    '<article class="ss-education"><strong>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</strong><span>' + e(item.institution || "") +
    '</span><time>' + dates(item) + "</time></article>").join("");
  const projects = (data.projects || []).map((item) =>
    '<article class="ss-role"><h3>' + e(item.name || "") + "</h3>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") + "</article>").join("");
  const certifications = (data.certifications || []).map((item) =>
    "<p><strong>" + e(item.name || "") + "</strong>" + (item.issuer ? " · " + e(item.issuer) : "") + "</p>").join("");
  const markup = '<div class="resume-template-service-standard"><header class="ss-header">' +
    '<div class="ss-eyebrow">HOSPITALITY · FOOD SERVICE · TRAVEL</div><h1>' + e(person.full_name || "Your Name") + "</h1>" +
    '<p class="ss-title">' + e(person.professional_title || "Hospitality & Guest Services Professional") + "</p>" +
    '<div class="ss-contact">' + contact.join('<span>•</span>') + "</div></header>" +
    '<div class="ss-principles"><span>GUEST FIRST</span><span>OPERATIONAL EXCELLENCE</span><span>CONSISTENT SERVICE</span></div>' +
    '<main class="ss-main">' + section("summary", "Professional Profile", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Hospitality Experience", experience) +
    section("projects", "Service Improvements & Highlights", projects) +
    section("skills", "Operational & Service Skills", skillList) +
    section("education", "Education & Training", education) +
    section("certifications", "Certifications", certifications) +
    (data.career_objective ? section("career_objective", "Career Objective", "<p>" + e(data.career_objective) + "</p>") : "") +
    "</main></div>";
  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".ss-main");
  if (main && Array.isArray(data.section_order)) {
    const nodes = Array.from(main.children);
    data.section_order.forEach((key) => {
      const node = nodes.find((item) => item.dataset.section === key);
      if (node) main.appendChild(node);
    });
  }
  return root.outerHTML;
}
