function renderTechSidebarTemplate(content, escapeHtml) {
  const personal = content.personal_information || {};
  const esc = typeof escapeHtml === "function" ? escapeHtml : (value) => String(value || "");

  const contact = [
    personal.email,
    personal.phone,
    personal.location
  ].filter(Boolean).map(esc).join(" • ");

  const list = (items, renderer) => (items || []).map(renderer).join("");

  const skillsByCategory = content.skills_by_category || {};
  const skills = Object.keys(skillsByCategory).map((category) =>
    '<div class="skill-group"><strong>' + esc(category) + '</strong>' +
    list(skillsByCategory[category], (skill) => esc(skill)).join(", ") +
    '</div>'
  ).join("");

  const fallbackSkills = !Object.keys(skillsByCategory).length && content.skills
    ? '<div class="skill-group">' + list(content.skills, (skill) => esc(skill)).join(", ") + '</div>'
    : skills;

  const languages = list(content.languages, (item) =>
    '<div class="resume-item"><div class="resume-item-title">' +
    esc(item.language || "") + '</div>' +
    (item.proficiency ? '<div class="resume-item-meta">' + esc(item.proficiency) + '</div>' : '') +
    '</div>'
  );

  const certifications = list(content.certifications, (item) =>
    '<div class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.name || "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.issuer || "") +
      (item.issue_date ? " • " + esc(item.issue_date) : "") + '</div>' +
    '</div>'
  );

  const experience = list(content.experience, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.title || "") +
      (item.company ? " — " + esc(item.company) : "") + '</div>' +
      '<div class="resume-item-meta">' +
      [item.location, item.start_date, item.end_date].filter(Boolean).map(esc).join(" • ") +
      '</div>' +
      (item.bullets && item.bullets.length
        ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>'
        : '') +
    '</article>'
  );

  const projects = list(content.projects, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.name || "") +
      (item.role ? " — " + esc(item.role) : "") + '</div>' +
      (item.technologies && item.technologies.length
        ? '<div class="resume-item-meta">' +
          item.technologies.map(esc).join(" • ") + '</div>'
        : '') +
      (item.description
        ? '<div class="resume-item-description">' + esc(item.description) + '</div>'
        : '') +
      (item.achievements && item.achievements.length
        ? '<ul>' + list(item.achievements, (achievement) => '<li>' + esc(achievement) + '</li>') + '</ul>'
        : '') +
    '</article>'
  );

  const education = list(content.education, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.degree || "") +
      (item.field_of_study ? " — " + esc(item.field_of_study) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.institution || "") +
      (item.location ? " • " + esc(item.location) : "") + '</div>' +
      '<div class="resume-item-meta">' +
      [item.start_date, item.end_date].filter(Boolean).map(esc).join(" – ") +
      '</div>' +
      (item.academic_achievements
        ? '<div class="resume-item-description">' + esc(item.academic_achievements) + '</div>'
        : '') +
    '</article>'
  );

  const customSections = list(content.custom_sections, (section) =>
    '<section><h2>' + esc(section.title || "") + '</h2>' +
      list(section.items, (item) =>
        '<article class="resume-item">' +
          '<div class="resume-item-title">' + esc(item.title || "") + '</div>' +
          (item.subtitle ? '<div class="resume-item-meta">' + esc(item.subtitle) + '</div>' : '') +
          (item.date ? '<div class="resume-item-meta">' + esc(item.date) + '</div>' : '') +
          (item.description ? '<div class="resume-item-description">' + esc(item.description) + '</div>' : '') +
          (item.bullets && item.bullets.length
            ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>'
            : '') +
        '</article>'
      ) +
    '</section>'
  );

  return '<div class="resume-template resume-template-tech">' +
    '<header class="tech-header">' +
      '<div class="tech-name">' +
        '<h1>' + esc(personal.full_name || "") + '</h1>' +
        (personal.professional_title ? '<p>' + esc(personal.professional_title) + '</p>' : '') +
      '</div>' +
      (contact ? '<div class="tech-contact">' + contact + '</div>' : '') +
    '</header>' +
    '<div class="tech-layout">' +
      '<aside class="tech-sidebar">' +
        (fallbackSkills ? '<section><h2>Skills</h2>' + fallbackSkills + '</section>' : '') +
        (languages ? '<section><h2>Languages</h2>' + languages + '</section>' : '') +
        (certifications ? '<section><h2>Certifications</h2>' + certifications + '</section>' : '') +
      '</aside>' +
      '<main class="tech-main">' +
        (content.summary ? '<section><h2>Profile</h2><p>' + esc(content.summary) + '</p></section>' : '') +
        (experience ? '<section><h2>Experience</h2>' + experience + '</section>' : '') +
        (projects ? '<section><h2>Projects</h2>' + projects + '</section>' : '') +
        (education ? '<section><h2>Education</h2>' + education + '</section>' : '') +
        customSections +
      '</main>' +
    '</div>' +
  '</div>';
}

window.renderTechSidebarTemplate = renderTechSidebarTemplate;