const sectionToggles = document.querySelectorAll("[data-home-section-toggle]");

const controlledSections = document.querySelectorAll(
  "[data-home-controlled-section]",
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

    /* =====================================
           CLOSE ALL CONTROLLED SECTIONS
        ===================================== */

    controlledSections.forEach((section) => {
      section.hidden = true;
    });

    /* =====================================
           RESET NAVBAR BUTTONS
        ===================================== */

    sectionToggles.forEach((button) => {
      button.classList.remove("is-active");

      button.setAttribute("aria-expanded", "false");
    });

    /* =====================================
           SAME BUTTON → CLOSE
        ===================================== */

    if (isAlreadyOpen) {
      return;
    }

    /* =====================================
           OPEN SELECTED SECTION
        ===================================== */

    targetSection.hidden = false;

    toggle.classList.add("is-active");

    toggle.setAttribute("aria-expanded", "true");

    targetSection.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
});
