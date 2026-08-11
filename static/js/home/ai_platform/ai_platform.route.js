import "./capability_spotlight.js";
import "./product_showcase.js";

const aiPlatformShell = document.querySelector("[data-ai-platform-shell]");

if (aiPlatformShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			aiPlatformShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.2,
			rootMargin: "0px 0px -8% 0px"
		}
	);

	observer.observe(aiPlatformShell);
}
