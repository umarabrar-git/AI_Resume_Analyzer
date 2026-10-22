function renderCampusLaunchTemplate(content, escapeHtml) {
  const personal = content.personal_information || {};
  const esc = typeof escapeHtml === "function" ? escapeHtml : (value) => String(value == null ? "" : value);
  const list = (items, renderItem) => (Array.isArray(items) ? items : []).map(renderItem).join("");
  const contact = [personal.email, personal.phone, personal.location].filter(Boolean).map(esc).join(" · ");
  const links = [
    [personal.linkedin, "LinkedIn"],
    [personal.github, "GitHub"],
    [personal.portfolio, "Portfolio"]
  ].filter((item) => item[0]);
  const education = list(content.education, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.degree || "") +
        (item.field_of_study ? " · " + esc(item.field_of_study) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.institution || "") +
        (item.location ? " · " + esc(item.location) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.start_date || "") +
        (item.end_date ? " – " + esc(item.end_date) : "") + '</div>' +
      (item.coursework ? '<div class="resume-item-description"><strong>Coursework:</strong> ' + esc(item.coursework) + '</div>' : "") +
      (item.academic_achievements ? '<div class="resume-item-description">' + esc(item.academic_achievements) + '</div>' : "") +
    '</article>'
  );
  const experience = list(content.experience, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.title || "") +
        (item.company ? " · " + esc(item.company) : "") + '</div>' +
      '<div class="resume-item-meta">' + esc(item.location || "") +
        (item.start_date ? " · " + esc(item.start_date) : "") +
        (item.end_date || item.current ? " – " + esc(item.current ? "Present" : item.end_date) : "") + '</div>' +
      (item.bullets && item.bullets.length ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>' : "") +
    '</article>'
  );
  const projects = list(content.projects, (item) =>
    '<article class="resume-item">' +
      '<div class="resume-item-title">' + esc(item.name || "") +
        (item.role ? " · " + esc(item.role) : "") + '</div>' +
      (item.technologies && item.technologies.length ? '<div class="resume-item-meta">' +
        list(item.technologies, (tech) => esc(tech)) + '</div>' : "") +
      (item.description ? '<div class="resume-item-description">' + esc(item.description) + '</div>' : "") +
      (item.achievements && item.achievements.length ? '<ul>' +
        list(item.achievements, (achievement) => '<li>' + esc(achievement) + '</li>') + '</ul>' : "") +
    '</article>'
  );
  const groups = content.skills_by_category || {};
  const skills = Object.keys(groups).length
    ? Object.keys(groups).map((category) =>
        '<div class="skill-group"><strong>' + esc(category) + ':</strong> ' +
        list(groups[category], (skill) => esc(skill)) + '</div>'
      ).join("")
    : (content.skills && content.skills.length
      ? '<div class="skill-group">' + list(content.skills, (skill) => esc(skill)) + '</div>'
      : "");
  const certifications = list(content.certifications, (item) =>
    '<article class="resume-item"><div class="resume-item-title">' + esc(item.name || "") + '</div>' +
    '<div class="resume-item-meta">' + esc(item.issuer || "") +
    (item.issue_date ? " · " + esc(item.issue_date) : "") + '</div></article>'
  );
  const languages = list(content.languages, (item) =>
    '<div class="resume-item-meta">' + esc(item.language || "") +
    (item.proficiency ? " · " + esc(item.proficiency) : "") + '</div>'
  );
  const customSections = list(content.custom_sections, (section) =>
    '<section><h2>' + esc(section.title || "") + '</h2>' +
      list(section.items, (item) =>
        '<article class="resume-item"><div class="resume-item-title">' + esc(item.title || "") + '</div>' +
        (item.subtitle ? '<div class="resume-item-meta">' + esc(item.subtitle) + '</div>' : "") +
        (item.date ? '<div class="resume-item-meta">' + esc(item.date) + '</div>' : "") +
        (item.description ? '<div class="resume-item-description">' + esc(item.description) + '</div>' : "") +
        (item.bullets && item.bullets.length ? '<ul>' + list(item.bullets, (bullet) => '<li>' + esc(bullet) + '</li>') + '</ul>' : "") +
        '</article>'
      ) + '</section>'
  );
  return '<div class="resume-template resume-template-campus-launch">' +
    '<header class="campus-header"><div class="campus-kicker">EARLY CAREER PROFILE</div>' +
      '<h1>' + esc(personal.full_name || "") + '</h1>' +
      (personal.professional_title ? '<p class="campus-title">' + esc(personal.professional_title) + '</p>' : "") +
      (contact ? '<p class="campus-contact">' + contact + '</p>' : "") +
      (links.length ? '<div class="campus-links">' + links.map((link) =>
        '<a href="' + esc(link[0]) + '" target="_blank" rel="noopener noreferrer">' + esc(link[1]) + '</a>'
      ).join("") + '</div>' : "") +
    '</header><div class="campus-layout"><main class="campus-main">' +
      (content.summary ? '<section><h2>Profile</h2><p>' + esc(content.summary) + '</p></section>' : "") +
      (content.career_objective ? '<section><h2>Career Objective</h2><p>' + esc(content.career_objective) + '</p></section>' : "") +
      (projects ? '<section><h2>Selected Projects</h2>' + projects + '</section>' : "") +
      (experience ? '<section><h2>Experience</h2>' + experience + '</section>' : "") +
      customSections +
    '</main><aside class="campus-sidebar">' +
      (education ? '<section><h2>Education</h2>' + education + '</section>' : "") +
      (skills ? '<section><h2>Skills</h2>' + skills + '</section>' : "") +
      (certifications ? '<section><h2>Certifications</h2>' + certifications + '</section>' : "") +
      (languages ? '<section><h2>Languages</h2>' + languages + '</section>' : "") +
    '</aside></div></div>';
}
export { renderCampusLaunchTemplate };