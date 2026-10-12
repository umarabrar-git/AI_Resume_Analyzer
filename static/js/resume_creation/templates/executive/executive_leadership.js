export function renderExecutiveLeadershipTemplate(content, escapeHtml) {
  const root = document.createElement("div");
  const fallbackEscape = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => Array.isArray(items)
    ? items.filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("")
    : "";
  const section = (key, title, html) => html
    ? '<section data-section="' + key + '"><h2>' + e(title) + "</h2>" + html + "</section>"
    : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const experience = (data.experience || []).map((item) =>
    '<article class="el-entry"><div class="el-entry-head"><h3>' + e(item.title || "") +
    '</h3><span class="el-date">' + dates(item) + '</span></div><div class="el-subtitle">' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    ((item.bullets || []).length || (item.achievements || []).length
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  ).join("");

  const education = (data.education || []).map((item) =>
    '<article class="el-entry"><div class="el-entry-head"><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><span class="el-date">' +
    dates(item) + '</span></div><div class="el-subtitle">' + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const projects = (data.projects || []).map((item) =>
    '<article class="el-entry"><div class="el-entry-head"><h3>' + e(item.name || "") +
    (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.technologies && item.technologies.length ? '<p class="el-subtitle"><strong>Tools:</strong> ' + e(item.technologies.join(", ")) + "</p>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">' + e(item.url) + "</a></p>" : "") +
    "</article>"
  ).join("");

  const skillsList = Array.isArray(data.skills) ? data.skills : Object.values(data.skills_by_category || {}).flat();
  const skills = skillsList.length
    ? '<div class="el-skills">' + skillsList.map((skill) => '<span class="el-skill">' + e(skill) + "</span>").join("") + "</div>"
    : "";

  const certifications = (data.certifications || []).map((item) =>
    '<p><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " — " + e(item.issuer) : "") +
    (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = (data.languages || []).map((item) =>
    "<p>" + e(item.language || "") + (item.proficiency ? " — " + e(item.proficiency) : "") + "</p>"
  ).join("");
  const custom = (data.custom_sections || [])
    .filter((item) => item.items && item.items.length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + e(item.id || ""), item.title || "Additional Information",
      item.items.map((entry) => '<article class="el-custom-item"><div class="el-entry-head"><h3>' +
        e(entry.title || "") + (entry.subtitle ? " · " + e(entry.subtitle) : "") +
        '</h3><span class="el-date">' + e(entry.date || "") + "</span></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>").join("")
    )).join("");

  root.innerHTML =
    '<div class="resume-template-executive-leadership"><header class="el-header">' +
    '<p class="el-kicker">Leadership Profile</p><h1>' + e(personal.full_name || "Your Name") +
    '</h1><p class="el-title">' + e(personal.professional_title || "") +
    '</p><div class="el-contact">' + contact.join("<span> · </span>") +
    '</div><div class="el-rule" aria-hidden="true"></div></header><main>' +
    section("summary", "Executive Summary", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Leadership Experience", experience) +
    section("projects", "Strategic Initiatives", projects) +
    section("education", "Education", education) +
    section("skills", "Core Competencies", skills) +
    section("certifications", "Certifications & Governance", certifications) +
    section("languages", "Languages", languages) + custom + "</main></div>";

  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const main = root.querySelector("main");
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
