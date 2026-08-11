const heroSection = document.querySelector(".hero-section");

if (heroSection) {
	const revealTargets = heroSection.querySelectorAll(
		".hero-badge, .hero-heading, .hero-description, .hero-features, .hero-actions, .hero-trust, .resume-preview-card, .ats-score-card, .job-match-card, .suggestions-card, .floating-card"
	);

	revealTargets.forEach((element, index) => {
		element.classList.add("hero-reveal");

		window.setTimeout(() => {
			element.classList.add("is-visible");
		}, 80 * index);
	});
}
