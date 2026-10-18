export function renderProductImpactTemplate(content, escapeHtml) {
  const fallbackEscape = (value) =>
    String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[char]);
  const e = typeof escapeHtml === "function" ? escapeHtml : fallbackEscape;
  const data = content || {};
  const personal = data.personal_information || {};
  const hidden = new Set(Array.isArray(data.hidden_sections) ? data.hidden_sections : []);
  const list = (value) => Array.isArray(value) ? value : [];
  const safeUrl = (value) => {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? e(url) : "";
  };
  const dates = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return start || end ? e(start) + (start && end ? " – " : "") + e(end) : "";
  };
  const bullets = (items) => list(items).filter(Boolean).map((item) => "<li>" + e(item) + "</li>").join("");
  const section = (key, title, html, className = "") => html
    ? '<section class="' + e(className) + '" data-section="' + e(key) + '"><h2>' + e(title) + "</h2>" + html + "</section>"
    : "";

  const contact = [];
  [personal.email, personal.phone, personal.location].filter(Boolean)
    .forEach((value) => contact.push('<span class="pi-contact-item">' + e(value) + "</span>"));
  [["LinkedIn", personal.linkedin], ["Portfolio", personal.portfolio], ["Website", personal.website], ["GitHub", personal.github]]
    .forEach(([label, value]) => {
      const url = safeUrl(value);
      if (url) contact.push('<a class="pi-contact-item" href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>");
    });

  const groups = data.skills_by_category && typeof data.skills_by_category === "object"
    ? Object.entries(data.skills_by_category).filter(([, values]) => Array.isArray(values) && values.length)
    : [];
  const skills = groups.length
    ? groups.map(([name, values]) =>
      '<div class="pi-skill-group"><h3>' + e(name) + '</h3><ul class="pi-skill-tags">' +
      values.map((value) => "<li>" + e(value) + "</li>").join("") + "</ul></div>"
    ).join("")
    : list(data.skills).length
      ? '<ul class="pi-skill-tags">' + list(data.skills).map((value) => "<li>" + e(value) + "</li>").join("") + "</ul>"
      : "";

  const experience = list(data.experience).map((item) =>
    '<article class="pi-entry"><div class="pi-entry-head"><div><h3>' + e(item.title || "") +
    '</h3><p class="pi-meta">' + e(item.company || "") +
    (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    '<p class="pi-date">' + dates(item) + "</p></div>" +
    (item.summary ? '<p class="pi-entry-summary">' + e(item.summary) + "</p>" : "") +
    (item.bullets && item.bullets.length ? "<ul>" + bullets(item.bullets) + "</ul>" : "") +
    (item.achievements && item.achievements.length
      ? '<div class="pi-outcome"><strong>Impact</strong><p>' + item.achievements.map((value) => e(value)).join("; ") + "</p></div>"
      : "") + "</article>"
  ).join("");

  const projects = list(data.projects).map((item) =>
    '<article class="pi-entry pi-project"><div class="pi-entry-head"><div><h3>' + e(item.name || "") +
    (item.role ? ' <span class="pi-meta">· ' + e(item.role) + "</span>" : "") + "</h3></div>" +
    '<p class="pi-date">' + dates(item) + "</p></div>" +
    (item.description ? "<p>" + e(item.description) + "</p>" : "") +
    (item.technologies && item.technologies.length
      ? '<p class="pi-meta"><strong>Tools:</strong> ' + item.technologies.map((value) => e(value)).join(" · ") + "</p>"
      : "") +
    (item.achievements && item.achievements.length
      ? '<div class="pi-outcome"><strong>Outcome</strong><p>' + item.achievements.map((value) => e(value)).join("; ") + "</p></div>"
      : "") +
    (safeUrl(item.url) ? '<p><a href="' + safeUrl(item.url) + '" target="_blank" rel="noopener noreferrer">View project</a></p>' : "") +
    "</article>"
  ).join("");

  const education = list(data.education).map((item) =>
    '<article class="pi-entry"><div class="pi-entry-head"><div><h3>' + e(item.degree || "") +
    (item.field_of_study ? " — " + e(item.field_of_study) : "") +
    '</h3><p class="pi-meta">' + e(item.institution || "") +
    (item.location ? " · " + e(item.location) : "") + "</p></div>" +
    '<p class="pi-date">' + dates(item) + "</p></div>" +
    (item.coursework ? "<p><strong>Relevant coursework:</strong> " + e(item.coursework) + "</p>" : "") +
    (item.academic_achievements ? "<p>" + e(item.academic_achievements) + "</p>" : "") +
    "</article>"
  ).join("");

  const certifications = list(data.certifications).map((item) =>
    '<p class="pi-compact"><strong>' + e(item.name || "") + "</strong>" +
    (item.issuer ? " · " + e(item.issuer) : "") +
    (item.issue_date ? " · " + e(item.issue_date) : "") + "</p>"
  ).join("");
  const languages = list(data.languages).map((item) =>
    '<p class="pi-compact"><strong>' + e(item.language || "") + "</strong>" +
    (item.proficiency ? " · " + e(item.proficiency) : "") + "</p>"
  ).join("");

  const custom = list(data.custom_sections)
    .filter((item) => list(item.items).length && !hidden.has("custom:" + item.id))
    .map((item) => section("custom:" + (item.id || ""), item.title || "Additional Information",
      list(item.items).map((entry) =>
        '<article class="pi-entry"><div class="pi-entry-head"><h3>' + e(entry.title || "") +
        (entry.subtitle ? " · " + e(entry.subtitle) : "") + '</h3><p class="pi-date">' +
        e(entry.date || "") + "</p></div>" +
        (entry.description ? "<p>" + e(entry.description) + "</p>" : "") +
        (entry.bullets && entry.bullets.length ? "<ul>" + bullets(entry.bullets) + "</ul>" : "") +
        "</article>"
      ).join(""), "pi-custom-section"
    )).join("");

  const summary = data.summary ? "<p>" + e(data.summary) + "</p>" : "";
  const markup =
    '<div class="resume-template-product-impact">' +
      '<header class="pi-header">' +
        '<div class="pi-header-top"><span class="pi-kicker">PRODUCT / STRATEGY / DELIVERY</span><span class="pi-header-index">PROFILE · 02</span></div>' +
        '<div class="pi-header-grid"><div><h1>' + e(personal.full_name || "Your Name") + '</h1>' +
        '<p class="pi-title">' + e(personal.professional_title || "") + '</p></div>' +
        '<div class="pi-contact">' + contact.join("") + "</div></div>" +
        '<div class="pi-ribbon"><span>DISCOVERY</span><i></i><span>DECISIONS</span><i></i><span>OUTCOMES</span></div>' +
      '</header><div class="pi-layout">' +
        '<aside class="pi-sidebar"><p class="pi-sidebar-label">CAPABILITIES</p>' +
          section("skills", "Product Toolkit", skills) +
          section("certifications", "Certifications", certifications) +
          section("languages", "Languages", languages) +
        '</aside><main class="pi-main">' +
          section("summary", "Product Thesis", summary) +
          section("experience", "Product Impact", experience) +
          section("projects", "Launches & Experiments", projects) +
          section("education", "Education", education) + custom +
        '</main></div></div>';

  const root = document.createElement("div");
  root.innerHTML = markup;
  root.querySelectorAll("[data-section]").forEach((node) => {
    if (hidden.has(node.dataset.section) || !node.textContent.trim()) node.classList.add("is-hidden");
  });
  const order = Array.isArray(data.section_order) ? data.section_order : [];
  [root.querySelector(".pi-sidebar"), root.querySelector(".pi-main")].forEach((container) => {
    if (!container || !order.length) return;
    const children = Array.from(container.querySelectorAll(":scope > [data-section]"));
    order.forEach((key) => {
      const node = children.find((child) => child.dataset.section === key);
      if (node) container.appendChild(node);
    });
  });
  return root.firstElementChild.outerHTML;
}
