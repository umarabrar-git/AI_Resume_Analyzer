export function renderBoardroomBriefTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function"
    ? escapeHtml
    : (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[char]);
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(data.hidden_sections || []);
  const list = (items, renderItem) => (Array.isArray(items) ? items : []).map(renderItem).join("");
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return e(start) + (start && end ? " – " : "") + e(end);
  };
  const bullets = (items) => list(items, (item) => item ? "<li>" + e(item) + "</li>" : "");
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const section = (key, title, html) => html && !hidden.has(key)
    ? '<section data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + html + "</section>"
    : "";
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(e);
  [["LinkedIn", personal.linkedin], ["GitHub", personal.github], ["Portfolio", personal.portfolio], ["Website", personal.website]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const experience = list(data.experience, (item) =>
    '<article class="bb-entry"><div class="bb-entry-head"><h3>' + e(item.title || "") +
    '</h3><span class="bb-date">' + dates(item) + '</span></div><div class="bb-meta">' +
    e(item.company || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.bullets && item.bullets.length || item.achievements && item.achievements.length
      ? "<ul>" + bullets([...(item.bullets || []), ...(item.achievements || [])]) + "</ul>" : "") +
    "</article>"
  );
  const education = list(data.education, (item) =>
    '<article class="bb-entry"><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") + '</h3><div class="bb-meta">' +
    e(item.institution || "") + (item.location ? " · " + e(item.location) : "") + "</div>" +
    (item.start_date || item.end_date ? '<div class="bb-date">' + dates(item) + "</div>" : "") +
    (item.coursework ? "<p><strong>Coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") + "</article>"
  );
  const projects = list(data.projects, (item) =>
    '<article class="bb-entry"><div class="bb-entry-head"><h3>' + e(item.name || "") +
    (item.role ? " · " + e(item.role) : "") + "</h3></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.achievements && item.achievements.length ? "<ul>" + bullets(item.achievements) + "</ul>" : "") +
    (item.technologies && item.technologies.length ? '<div class="bb-meta">TOOLS / ' + e(item.technologies.join(" · ")) + "</div>" : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View project</a></p>' : "") +
    "</article>"
  );
  const skillsData = data.skills_by_category && Object.keys(data.skills_by_category).length
    ? Object.entries(data.skills_by_category).map(([category, values]) =>
        '<div class="bb-skill-group"><h3>' + e(category) + "</h3><div>" +
        list(values, (skill) => '<span class="bb-skill">' + e(skill) + "</span>") + "</div></div>"
      ).join("")
    : (Array.isArray(data.skills) && data.skills.length
      ? '<div class="bb-skill-cloud">' + list(data.skills, (skill) => '<span class="bb-skill">' + e(skill) + "</span>") + "</div>"
      : "");
  const certifications = list(data.certifications, (item) =>
    '<article class="bb-entry"><h3>' + e(item.name || "") + "</h3><div class="bb-meta">" +
    e(item.issuer || "") + (item.issue_date ? " · " + e(item.issue_date) : "") + "</div></article>"
  );
  const languages = list(data.languages, (item) =>
    '<p class="bb-language"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? '<span>' + e(item.proficiency) + "</span>" : "") + "</p>"
  );
  const custom = list(data.custom_sections, (item) => {
    if (!item || !Array.isArray(item.items) || !item.items.length || hidden.has("custom:" + item.id)) return "";
    return section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items, (entry) =>
        '<article class="bb-entry"><div class="bb-entry-head"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><span class="bb-date">' +
        e(entry.date || "") + "</span></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>"
      )
    );
  });

  const markup =
    '<div class="resume-template-boardroom-brief"><header class="bb-header">' +
    '<div class="bb-brand"><span class="bb-mark">BB</span><span>STRATEGY / GOVERNANCE / LEADERSHIP</span></div>' +
    '<h1>' + e(personal.full_name || "Your Name") + "</h1>" +
    (personal.professional_title ? '<p class="bb-title">' + e(personal.professional_title) + "</p>" : "") +
    (contact.length ? '<div class="bb-contact">' + contact.join("<span> · </span>") + "</div>" : "") +
    '<div class="bb-header-rule" aria-hidden="true"></div></header><div class="bb-layout"><main class="bb-main">' +
    section("summary", "Leadership Thesis", data.summary ? "<p>" + e(data.summary) + "</p>" : "") +
    section("experience", "Strategic Leadership", experience) +
    section("projects", "Strategic Mandates & Outcomes", projects) + custom +
    '</main><aside class="bb-rail">' +
    section("skills", "Board-Level Capabilities", skillsData) +
    section("education", "Education", education) +
    section("certifications", "Governance & Credentials", certifications) +
    section("languages", "Languages", languages) +
    "</aside></div></div>";

  const wrapper = document.createElement("div");
  wrapper.innerHTML = markup;
  const root = wrapper.firstElementChild;
  const main = root.querySelector(".bb-main");
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
