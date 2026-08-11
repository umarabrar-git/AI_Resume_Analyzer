import "./pricing_toggle.js";

const pricingShell = document.querySelector(
    "[data-pricing-shell]"
);

if (pricingShell) {
    const observer = new IntersectionObserver(
        (entries, currentObserver) => {
            const isVisible = entries.some(
                (entry) => entry.isIntersecting
            );

            if (!isVisible) {
                return;
            }

            pricingShell.classList.add("is-visible");

            currentObserver.disconnect();
        },
        {
            threshold: 0.2,
            rootMargin: "0px 0px -8% 0px"
        }
    );

    observer.observe(pricingShell);
}