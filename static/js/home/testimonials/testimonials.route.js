import "./testimonials_highlight.js";

const testimonialsShell = document.querySelector("[data-testimonials-shell]");

if (testimonialsShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			testimonialsShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.2,
			rootMargin: "0px 0px -8% 0px"
		}
	);

	observer.observe(testimonialsShell);
}
