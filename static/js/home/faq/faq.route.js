import "./faq_toggle.js";

const faqShell = document.querySelector("[data-faq-shell]");

if (faqShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			faqShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.2,
			rootMargin: "0px 0px -8% 0px"
		}
	);

	observer.observe(faqShell);
}
