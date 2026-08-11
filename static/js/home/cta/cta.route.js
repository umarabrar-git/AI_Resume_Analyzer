import "./cta_pulse.js";

const ctaShell = document.querySelector("[data-cta-shell]");

if (ctaShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			ctaShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.2,
			rootMargin: "0px 0px -8% 0px"
		}
	);

	observer.observe(ctaShell);
}
