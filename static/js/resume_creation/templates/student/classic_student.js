function renderClassicStudentTemplate(content, escapeHtml) {
  const personal = content.personal_information || {};
  const esc = typeof escapeHtml === "function" ? escapeHtml : (value) => String(value || "");
  const contact = [
    personal.email,
    personal.phone,
    personal.location
  ].filter(Boolean).map(esc).join(" • ");

  const links = [
    ["linkedin", personal.linkedin, "LinkedIn"],
    ["github", personal.github, "GitHub"],
    ["portfolio", personal.portfolio, "Portfolio"]
  ].filter((item) => item[1]);

  const list = (items, renderer) => (items || []).map(renderer).join("");

  const education = list(content.education, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.degree || "") + (item.field_of_study ? " — " + esc(item.field_of_study) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.institution || "") + (item.location ? " • " + esc(item.location) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.start_date || "") + (item.end_date ? " – " + esc(item.end_date) : "") + '</div>' +
      (item.coursework ? '<div class="resume-item-description"><strong>Coursework:</strong> ' + esc(item.coursework) + '</div>' : '') +
      (item.academic_achievements ? '<div class="resume-item-description">' + esc(item.academic_achievements) + '</div>' : '') +
    '</article>'
  );

  const experience = list(content.experience, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.title || "") + (item.company ? " — " + esc(item.company) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.location || "") + (item.start_date ? " • " + esc(item.start_date) : "") + (item.end_date ? " – " + esc(item.end_date) : "") + '</div>' +
      (item.bullets && item.bullets.length ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>' : '') +
    '</article>'
  );

  const projects = list(content.projects, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.name || "") + (item.role ? " — " + esc(item.role) : "") + '</div>' +
      (item.technologies && item.technologies.length ? '<div class="resume-item-meta">' + list(item.technologies, (tech) => esc(tech)).join(" • ") + '</div>' : '') +
      (item.description ? '<div class="resume-item-description">' + esc(item.description) + '</div>' : '') +
      (item.achievements && item.achievements.length ? '<ul>' + list(item.achievements, (achievement) => '<li>' + esc(achievement) + '</li>') + '</ul>' : '') +
    '</article>'
  );

  const skillsByCategory = content.skills_by_category || {};
  const skillGroups = Object.keys(skillsByCategory).map((category) =>
    '<div class="skill-group"><strong>' + esc(category) + ':</strong> ' +
    list(skillsByCategory[category], (skill) => esc(skill)).join(", ") +
    '</div>'
  ).join("");

  const skills = !Object.keys(skillsByCategory).length && content.skills
    ? '<div class="skill-group">' + list(content.skills, (skill) => esc(skill)).join(", ") + '</div>'
    : skillGroups;

  const certifications = list(content.certifications, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.name || "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.issuer || "") + (item.issue_date ? " • " + esc(item.issue_date) : "") + '</div>' +
    '</article>'
  );

  const languages = list(content.languages, (item) =>
    '<span class="resume-item-meta">' + esc(item.language || "") + (item.proficiency ? " (" + esc(item.proficiency) + ")" : "") + '</span>'
  );

  const customSections = list(content.custom_sections, (section) =>
    '<section><h2>' + esc(section.title || "") + '</h2>' +
      list(section.items, (item) =>
        '<article class="resume-item">' +
          '<div class="resume-item-title">' + esc(item.title || "") + '</div>' +
          (item.subtitle ? '<div class="resume-item-meta">' + esc(item.subtitle) + '</div>' : '') +
          (item.date ? '<div class="resume-item-meta">' + esc(item.date) + '</div>' : '') +
          (item.description ? '<div class="resume-item-description">' + esc(item.description) + '</div>' : '') +
          (item.bullets && item.bullets.length ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>' : '') +
        '</article>'
      ) +
    '</section>'
  );

  return '<div class="resume-template resume-template-classic-student">' +
    '<header class="student-header">' +
      '<div class="student-identity">' +
        '<h1>' + esc(personal.full_name || "") + '</h1>' +
        (personal.professional_title ? '<p class="student-title">' + esc(personal.professional_title) + '</p>' : '') +
        (contact ? '<p class="student-contact">' + contact + '</p>' : '') +
      '</div>' +
      (links.length ? '<div class="student-links">' + links.map((link) => '<a href="' + esc(link[1]) + '" target="_blank" rel="noopener noreferrer">' + esc(link[2]) + '</a>').join("") + '</div>' : '') +
    '</header>' +
    '<main class="student-body">' +
      (content.summary ? '<section><h2>Professional Summary</h2><p>' + esc(content.summary) + '</p></section>' : '') +
      (content.career_objective ? '<section><h2>Career Objective</h2><p>' + esc(content.career_objective) + '</p></section>' : '') +
      (education ? '<section><h2>Education</h2>' + education + '</section>' : '') +
      (experience ? '<section><h2>Experience</h2>' + experience + '</section>' : '') +
      (projects ? '<section><h2>Projects</h2>' + projects + '</section>' : '') +
      (skills ? '<section><h2>Technical Skills</h2>' + skills + '</section>' : '') +
      (certifications ? '<section><h2>Certifications</h2>' + certifications + '</section>' : '') +
      (languages ? '<section><h2>Languages</h2><div class="student-links">' + languages + '</div></section>' : '') +
      customSections +
    '</main>' +
  '</div>';
}

window.renderClassicStudentTemplate = renderClassicStudentTemplate;