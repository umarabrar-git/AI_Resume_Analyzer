const legalLinks = Array.from(
    document.querySelectorAll("[data-legal-link]")
);

const legalPanels = Array.from(
    document.querySelectorAll("[data-legal-panel]")
);

const validSections = legalPanels.map(
    (panel) => panel.dataset.legalPanel
);

const showLegalSection = (
    sectionName,
    updateHistory = true
) => {

    if (!validSections.includes(sectionName)) {
        sectionName = "terms";
    }

    legalLinks.forEach((link) => {

        const isActive =
            link.dataset.legalLink === sectionName;

        link.classList.toggle(
            "is-active",
            isActive
        );

        if (isActive) {
            link.setAttribute(
                "aria-current",
                "page"
            );
        } else {
            link.removeAttribute(
                "aria-current"
            );
        }

    });

    legalPanels.forEach((panel) => {

        const isActive =
            panel.dataset.legalPanel === sectionName;

        panel.classList.toggle(
            "is-active",
            isActive
        );

    });

    if (updateHistory) {

        history.pushState(
            { legalSection: sectionName },
            "",
            `#${sectionName}`
        );

    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

};

legalLinks.forEach((link) => {

    link.addEventListener("click", (event) => {

        event.preventDefault();

        showLegalSection(
            link.dataset.legalLink
        );

    });

});

window.addEventListener("popstate", () => {

    const section =
        window.location.hash.replace("#", "");

    showLegalSection(
        section || "terms",
        false
    );

});

const initialSection =
    window.location.hash.replace("#", "");

showLegalSection(
    validSections.includes(initialSection)
        ? initialSection
        : "terms",
    false
);
