import "./footer_year.js";

const footerShell = document.querySelector("[data-footer-shell]");

if (footerShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			footerShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.08,
			rootMargin: "0px 0px -5% 0px"
		}
	);

	observer.observe(footerShell);
}
