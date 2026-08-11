const pricingToggle = document.querySelector("[data-pricing-toggle]");
const priceNodes = Array.from(document.querySelectorAll(".pricing-card__price"));

if (pricingToggle && priceNodes.length) {
    const buttons = Array.from(pricingToggle.querySelectorAll("[data-billing]"));

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const selectedMode = button.dataset.billing;

            buttons.forEach((item) => {
                item.classList.toggle("is-active", item === button);
            });

            priceNodes.forEach((node) => {
                const monthly = node.getAttribute("data-monthly") || "";
                const yearly = node.getAttribute("data-yearly") || "";
                node.textContent = selectedMode === "yearly" ? yearly : monthly;
            });
        });
    });
}
