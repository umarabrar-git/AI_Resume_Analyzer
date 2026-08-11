const sectionToggles = document.querySelectorAll(
    "[data-home-section-toggle]"
);

const controlledSections = document.querySelectorAll(
    "[data-home-controlled-section]"
);

sectionToggles.forEach((toggle) => {
    toggle.addEventListener("click", (event) => {
        event.preventDefault();

        const targetId = toggle.dataset.homeSectionToggle;
        const targetSection = document.getElementById(targetId);

        if (!targetSection) {
            return;
        }

        const isAlreadyOpen = !targetSection.hidden;

        // Close all controlled sections
        controlledSections.forEach((section) => {
            section.hidden = true;
        });

        // Reset all navbar buttons
        sectionToggles.forEach((button) => {
            button.classList.remove("is-active");
            button.setAttribute("aria-expanded", "false");
        });

        // Same button clicked again -> keep everything closed
        if (isAlreadyOpen) {
            return;
        }

        // Open selected section
        targetSection.hidden = false;

        toggle.classList.add("is-active");
        toggle.setAttribute("aria-expanded", "true");

        targetSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    });
});