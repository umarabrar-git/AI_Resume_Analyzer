let spotlightInterval = null;


// ======================================================
// REMOVE CURRENT SPOTLIGHT
// ======================================================

function clearSpotlight(aiCards) {
    aiCards.forEach((card) => {
        card.classList.remove("is-spotlight");
    });
}


// ======================================================
// STOP CURRENT ANIMATION
// ======================================================

function stopSpotlight() {
    if (spotlightInterval !== null) {
        clearInterval(spotlightInterval);
        spotlightInterval = null;
    }
}


// ======================================================
// START SPOTLIGHT ANIMATION
// ======================================================

function startSpotlight() {
    // Stop old interval before starting a new one
    stopSpotlight();

    // Cards are selected again because Product Showcase
    // dynamically creates new cards
    const aiCards = Array.from(
        document.querySelectorAll("[data-ai-card]")
    );

    if (!aiCards.length) {
        return;
    }

    let activeIndex = 0;


    function highlightCard(index) {
        aiCards.forEach((card, currentIndex) => {
            card.classList.toggle(
                "is-spotlight",
                currentIndex === index
            );
        });
    }


    // Highlight first card immediately
    highlightCard(activeIndex);


    // No interval needed if only one card exists
    if (aiCards.length === 1) {
        return;
    }


    spotlightInterval = setInterval(() => {
        activeIndex =
            (activeIndex + 1) % aiCards.length;

        highlightCard(activeIndex);
    }, 1800);
}


// ======================================================
// WATCH DYNAMIC CAPABILITY CARDS
// ======================================================

const capabilitiesContainer = document.querySelector(
    "[data-ai-capabilities]"
);


if (capabilitiesContainer) {
    const observer = new MutationObserver(() => {
        startSpotlight();
    });


    observer.observe(capabilitiesContainer, {
        childList: true
    });


    // Supports cards that may already exist on page load
    startSpotlight();
}


// ======================================================
// STOP ANIMATION WHEN SHOWCASE CLOSES
// ======================================================

const showcase = document.querySelector(
    "[data-product-showcase]"
);


if (showcase) {
    const showcaseObserver = new MutationObserver(() => {
        if (showcase.hidden) {
            stopSpotlight();

            const currentCards = Array.from(
                document.querySelectorAll("[data-ai-card]")
            );

            clearSpotlight(currentCards);
        }
    });


    showcaseObserver.observe(showcase, {
        attributes: true,
        attributeFilter: ["hidden"]
    });
}