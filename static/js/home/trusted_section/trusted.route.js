import "./logo_slider.js";

const trustedShell = document.querySelector("[data-trusted-shell]");

if (trustedShell) {
	const trustedLogos = Array.from(document.querySelectorAll(".trusted-section__logo"));

	trustedLogos.forEach((logo, index) => {
		logo.style.setProperty("--trusted-delay", `${index * 80}ms`);
	});

	const trustedObserver = new IntersectionObserver(
		(entries, observer) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			trustedShell.classList.add("is-visible");
			observer.disconnect();
		},
		{
			threshold: 0.25,
			rootMargin: "0px 0px -10% 0px"
		}
	);

	trustedObserver.observe(trustedShell);
}
