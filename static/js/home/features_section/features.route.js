const featuresShell = document.querySelector(
    "[data-features-shell]"
);

if (featuresShell) {
    const observer = new IntersectionObserver(
        (entries, currentObserver) => {
            const isVisible = entries.some(
                (entry) => entry.isIntersecting
            );

            if (!isVisible) {
                return;
            }

            featuresShell.classList.add("is-visible");

            currentObserver.disconnect();
        },
        {
            threshold: 0.2,
            rootMargin: "0px 0px -8% 0px"
        }
    );

    observer.observe(featuresShell);
}