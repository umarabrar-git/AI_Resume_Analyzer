import "./preview_glow.js";

const dashboardPreviewShell = document.querySelector("[data-dashboard-preview-shell]");

if (dashboardPreviewShell) {
	const observer = new IntersectionObserver(
		(entries, currentObserver) => {
			const isVisible = entries.some((entry) => entry.isIntersecting);

			if (!isVisible) {
				return;
			}

			dashboardPreviewShell.classList.add("is-visible");
			currentObserver.disconnect();
		},
		{
			threshold: 0.2,
			rootMargin: "0px 0px -8% 0px"
		}
	);

	observer.observe(dashboardPreviewShell);
}
