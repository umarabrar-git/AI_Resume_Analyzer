const faqItems = Array.from(document.querySelectorAll("[data-faq-item]"));

if (faqItems.length) {
    faqItems.forEach((item) => {
        const trigger = item.querySelector("[data-faq-trigger]");
        const content = item.querySelector("[data-faq-content]");

        if (!trigger || !content) {
            return;
        }

        trigger.addEventListener("click", () => {
            const willOpen = trigger.getAttribute("aria-expanded") !== "true";

            faqItems.forEach((otherItem) => {
                const otherTrigger = otherItem.querySelector("[data-faq-trigger]");
                const otherContent = otherItem.querySelector("[data-faq-content]");

                if (!otherTrigger || !otherContent) {
                    return;
                }

                otherTrigger.setAttribute("aria-expanded", "false");
                otherContent.classList.remove("is-open");
            });

            trigger.setAttribute("aria-expanded", String(willOpen));
            content.classList.toggle("is-open", willOpen);
        });
    });
}
