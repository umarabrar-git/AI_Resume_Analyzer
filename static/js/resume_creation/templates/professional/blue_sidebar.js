export function renderBlueSidebarTemplate(content, escapeHtml) {
  const template = document.querySelector("#resume-template-blue-sidebar");
  if (!template) return "";

  const fragment = template.content.cloneNode(true);
  const root = fragment.querySelector("[data-blue-sidebar-template]");
  const personal = content.personal_information || {};

  const setHtml = (selector, html) => {
    const node = root.querySelector(selector);
    if (node) node.innerHTML = html;
  };

  const setText = (selector, value) => {
    const node = root.querySelector(selector);
    if (node) node.textContent = value || "";
  };

  const has = (value) => Boolean(String(value || "").trim());

  setText('[data-field="sidebar-name"]', personal.full_name || "Your Name");
  setText('[data-field="sidebar-title"]', personal.professional_title || "Professional Title");
  setText('[data-field="full-name"]', personal.full_name || "Your Name");
  setText('[data-field="professional-title"]', personal.professional_title || "Professional Title");

  const photo = root.querySelector('[data-field="profile-photo"]');
  if (photo) {
    photo.innerHTML = personal.profile_photo
      ? `<img src="${escapeHtml(personal.profile_photo)}" alt="Profile photo">`
      : "<span>👤</span>";
  }

  const contact = [
    personal.email ? ["✉", personal.email] : null,
    personal.phone ? ["☎", personal.phone] : null,
    personal.location ? ["⌖", personal.location] : null,
    personal.linkedin ? ["in", `<a href="${escapeHtml(personal.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>`] : null,
    personal.github ? ["◉", `<a href="${escapeHtml(personal.github)}" target="_blank" rel="noopener">GitHub</a>`] : null,
    personal.portfolio ? ["◌", `<a href="${escapeHtml(personal.portfolio)}" target="_blank" rel="noopener">Portfolio</a>`] : null,
  ].filter(Boolean);

  setHtml(
    '[data-field="contact"]',
    contact.map(([icon, value]) => `<div class="blue-contact-item"><span class="blue-contact-icon">${icon}</span><span>${typeof value === "string" && value.startsWith("<a ") ? value : escapeHtml(value)}</span></div>`).join(""),
  );

  const categoryMap = content.skills_by_category || {};
  const skillGroups = [
    ["Programming", ["Programming Languages", "Programming"]],
    ["Data Science", ["Data Science"]],
    ["Machine Learning", ["Machine Learning"]],
    ["Frameworks & Libraries", ["Frameworks", "Libraries"]],
    ["Databases & Cloud", ["Databases", "Cloud"]],
    ["Tools & Platforms", ["Tools"]],
  ];

  const renderedGroups = skillGroups.map(([label, categories]) => {
    const skills = categories.flatMap((category) => Array.isArray(categoryMap[category]) ? categoryMap[category] : []);
    if (!skills.length) return "";
    return `<div class="blue-skill-group"><h3>${escapeHtml(label)}</h3><div class="blue-skill-tags">${skills.map((skill) => `<span class="blue-skill-tag">${escapeHtml(skill)}</span>`).join("")}</div></div>`;
  }).join("");

  setHtml('[data-field="skills"]', renderedGroups);

  setHtml(
    '[data-field="languages"]',
    (content.languages || []).filter((item) => item && (item.language || item.proficiency)).map((item) => `
      <div class="blue-language-item">
        <strong>${escapeHtml(item.language || "")}</strong>
        <span>${escapeHtml(item.proficiency || "")}</span>
      </div>
    `).join(""),
  );

  const interests = [];
  const interestSections = (content.custom_sections || []).filter((item) => String(item.title || "").toLowerCase() === "interests");
  interestSections.forEach((section) => (section.items || []).forEach((item) => {
    const value = item.title || item.description || "";
    if (has(value)) interests.push(value);
  }));

  setHtml(
    '[data-field="interests"]',
    interests.map((item) => `<div class="blue-interest-item">${escapeHtml(item)}</div>`).join(""),
  );

  const links = [
    personal.email ? escapeHtml(personal.email) : "",
    personal.phone ? escapeHtml(personal.phone) : "",
    personal.location ? escapeHtml(personal.location) : "",
    personal.linkedin ? `<a href="${escapeHtml(personal.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>` : "",
    personal.github ? `<a href="${escapeHtml(personal.github)}" target="_blank" rel="noopener">GitHub</a>` : "",
    personal.portfolio ? `<a href="${escapeHtml(personal.portfolio)}" target="_blank" rel="noopener">Portfolio</a>` : "",
  ].filter(Boolean);
  setHtml('[data-field="header-links"]', links.join("<span>•</span>"));

  setHtml('[data-field="summary"]', content.summary ? `<p class="blue-summary">${escapeHtml(content.summary)}</p>` : "");
  setHtml('[data-field="career-objective"]', content.career_objective ? `<p class="blue-objective">${escapeHtml(content.career_objective)}</p>` : "");

  const dateRange = (item) => {
    const start = item.start_date || "";
    const end = item.current ? "Present" : (item.end_date || "");
    return start || end ? `${escapeHtml(start)}${start || end ? " - " : ""}${escapeHtml(end)}` : "";
  };

  const bullets = (items) => (items || []).filter(Boolean).map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  setHtml(
    '[data-field="experience"]',
    (content.experience || []).map((item) => `
      <article class="blue-entry">
        <div class="blue-entry-head">
          <h3 class="blue-entry-title">${escapeHtml(item.title || "")}</h3>
          <span class="blue-entry-date">${dateRange(item)}</span>
        </div>
        <p class="blue-entry-subtitle">${escapeHtml(item.company || "")}${item.location ? ` · ${escapeHtml(item.location)}` : ""}</p>
        <ul class="blue-entry-bullets">${bullets([...(item.bullets || []), ...(item.achievements || [])])}</ul>
      </article>
    `).join(""),
  );

  setHtml(
    '[data-field="education"]',
    (content.education || []).map((item) => `
      <article class="blue-entry">
        <div class="blue-entry-head">
          <h3 class="blue-entry-title">${escapeHtml(item.degree || "")}${item.field_of_study ? ` in ${escapeHtml(item.field_of_study)}` : ""}</h3>
          <span class="blue-entry-date">${dateRange(item)}</span>
        </div>
        <p class="blue-entry-subtitle">${escapeHtml(item.institution || "")}${item.location ? ` · ${escapeHtml(item.location)}` : ""}</p>
        ${item.grade ? `<p class="blue-entry-description"><strong>Grade:</strong> ${escapeHtml(item.grade)}</p>` : ""}
        ${item.description ? `<p class="blue-entry-description">${escapeHtml(item.description)}</p>` : ""}
      </article>
    `).join(""),
  );

  setHtml(
    '[data-field="projects"]',
    (content.projects || []).map((item) => `
      <article class="blue-entry">
        <div class="blue-entry-head">
          <h3 class="blue-entry-title">${escapeHtml(item.name || "")}${item.role ? ` · ${escapeHtml(item.role)}` : ""}</h3>
          <span class="blue-entry-date">${dateRange(item)}</span>
        </div>
        ${Array.isArray(item.technologies) && item.technologies.length ? `<div class="blue-tech">${escapeHtml(item.technologies.join(", "))}</div>` : ""}
        ${item.description ? `<p class="blue-entry-description">${escapeHtml(item.description)}</p>` : ""}
        <ul class="blue-entry-bullets">${bullets(item.achievements)}</ul>
        ${item.github_url ? `<p class="blue-entry-description"><strong>GitHub:</strong> <a href="${escapeHtml(item.github_url)}" target="_blank" rel="noopener">${escapeHtml(item.github_url)}</a></p>` : ""}
        ${item.project_url ? `<p class="blue-entry-description"><strong>Project:</strong> <a href="${escapeHtml(item.project_url)}" target="_blank" rel="noopener">${escapeHtml(item.project_url)}</a></p>` : ""}
      </article>
    `).join(""),
  );

  setHtml(
    '[data-field="certifications"]',
    (content.certifications || []).map((item) => `
      <div class="blue-certification">
        <strong>${escapeHtml(item.name || "")}</strong>
        ${item.issuer ? ` — ${escapeHtml(item.issuer)}` : ""}
        ${item.issue_date ? ` (${escapeHtml(item.issue_date)})` : ""}
      </div>
    `).join(""),
  );

  const customSections = (content.custom_sections || []).filter((section) => {
    const title = String(section.title || "").trim().toLowerCase();
    return title !== "interests" && section.items && section.items.length;
  });

  setHtml(
    '[data-field="custom-sections"]',
    customSections.map((section) => `
      <section class="blue-custom-section">
        <div class="blue-section-heading"><span>•</span><h2>${escapeHtml(section.title || "Custom Section")}</h2></div>
        ${(section.items || []).map((item) => `
          <article class="blue-custom-item">
            <div class="blue-entry-head">
              <h3 class="blue-entry-title">${escapeHtml(item.title || "")}${item.subtitle ? ` · ${escapeHtml(item.subtitle)}` : ""}</h3>
              <span class="blue-entry-date">${escapeHtml(item.date || "")}</span>
            </div>
            ${item.description ? `<p class="blue-entry-description">${escapeHtml(item.description)}</p>` : ""}
            <ul class="blue-entry-bullets">${bullets(item.bullets)}</ul>
          </article>
        `).join("")}
      </section>
    `).join(""),
  );

  const hidden = new Set(content.hidden_sections || []);
  root.querySelectorAll("[data-section]").forEach((section) => {
    const key = section.dataset.section;
    if (hidden.has(key)) section.classList.add("is-hidden");
  });

  ["summary", "career_objective", "experience", "education", "projects", "certifications"].forEach((key) => {
    const node = root.querySelector(`[data-section="${key}"]`);
    const field = root.querySelector(`[data-field="${key === "career_objective" ? "career-objective" : key}"]`);
    if (node && field && !field.innerHTML.trim()) node.classList.add("is-hidden");
  });

  ["contact", "skills", "languages", "interests"].forEach((key) => {
    const node = root.querySelector(`[data-section="${key}"]`);
    const field = root.querySelector(`[data-field="${key}"]`);
    if (node && field && !field.innerHTML.trim()) node.classList.add("is-hidden");
  });

  return root.outerHTML;
}
