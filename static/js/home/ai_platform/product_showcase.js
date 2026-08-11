const showcase = document.querySelector("[data-product-showcase]");

const showcaseEyebrow = document.querySelector("[data-showcase-eyebrow]");
const showcaseTitle = document.querySelector("[data-showcase-title]");
const showcaseSubtitle = document.querySelector("[data-showcase-subtitle]");

const capabilitiesContainer = document.querySelector(
    "[data-ai-capabilities]"
);

const featureTriggers = Array.from(
    document.querySelectorAll("[data-feature-trigger]")
);

const featureCards = Array.from(
    document.querySelectorAll("[data-feature-card]")
);


// ======================================================
// SHOWCASE DATA
// ======================================================

const showcaseData = {

    "resume-analysis": {
        eyebrow: "AI Resume Analysis",

        title: "Understand and Improve Your Resume",

        subtitle:
            "Analyze resume structure, keywords, ATS compatibility, and improvement opportunities.",

        capabilities: [
            {
                icon: "bi-file-earmark-text",
                title: "Resume Parsing",
                desc: "Extract important resume information automatically."
            },
            {
                icon: "bi-search",
                title: "Keyword Analysis",
                desc: "Identify important keywords and missing terms."
            },
            {
                icon: "bi-check2-circle",
                title: "ATS Compatibility",
                desc: "Evaluate how effectively your resume works with ATS systems."
            },
            {
                icon: "bi-graph-up",
                title: "ATS Score",
                desc: "Receive a clear score with actionable improvement insights."
            }
        ]
    },


    "resume-creation": {
        eyebrow: "AI Resume Builder",

        title: "Build an ATS-Ready Resume with AI",

        subtitle:
            "Create professional resume content, customize your design, optimize for ATS systems, and export your resume.",

        capabilities: [
            {
                icon: "bi-pencil-square",
                title: "AI Content Writer",
                desc: "Generate professional and role-focused resume content."
            },
            {
                icon: "bi-layout-text-window",
                title: "Professional Templates",
                desc: "Choose layouts designed for clarity and ATS compatibility."
            },
            {
                icon: "bi-eye",
                title: "Live Preview",
                desc: "See resume changes instantly while building your resume."
            },
            {
                icon: "bi-stars",
                title: "ATS Optimization",
                desc: "Improve keywords, structure, and resume relevance."
            }
        ]
    },


    "job-matching": {
        eyebrow: "AI Job Matching",

        title: "Measure Your Resume Against the Job",

        subtitle:
            "Compare your resume with job descriptions and discover where you match and where you can improve.",

        capabilities: [
            {
                icon: "bi-bullseye",
                title: "Match Score",
                desc: "Measure resume relevance against a target job."
            },
            {
                icon: "bi-key",
                title: "Keyword Comparison",
                desc: "Compare important job keywords with your resume."
            },
            {
                icon: "bi-exclamation-circle",
                title: "Missing Skills",
                desc: "Discover important skills missing from your resume."
            },
            {
                icon: "bi-lightning-charge",
                title: "Improvement Actions",
                desc: "Receive clear actions to improve your job match."
            }
        ]
    },


    "career-assistant": {
        eyebrow: "AI Career Assistant",

        title: "Get Personalized Guidance for Your Career",

        subtitle:
            "Use AI-powered assistance to improve your resume, career decisions, and next professional steps.",

        capabilities: [
            {
                icon: "bi-chat-dots",
                title: "AI Conversations",
                desc: "Ask career questions and receive contextual guidance."
            },
            {
                icon: "bi-compass",
                title: "Career Direction",
                desc: "Explore practical next steps based on your goals."
            },
            {
                icon: "bi-file-text",
                title: "Resume Guidance",
                desc: "Receive suggestions for improving your resume."
            },
            {
                icon: "bi-lightbulb",
                title: "Actionable Advice",
                desc: "Turn AI recommendations into clear next actions."
            }
        ]
    },


    "smart-reports": {
        eyebrow: "Smart Reports",

        title: "Turn Resume Analysis Into Clear Insights",

        subtitle:
            "Review structured reports that explain performance, weaknesses, and recommended improvements.",

        capabilities: [
            {
                icon: "bi-file-earmark-pdf",
                title: "PDF Reports",
                desc: "Export professional resume analysis reports."
            },
            {
                icon: "bi-bar-chart",
                title: "Performance Insights",
                desc: "Understand resume performance through clear metrics."
            },
            {
                icon: "bi-list-check",
                title: "Recommendations",
                desc: "Review prioritized improvements and next actions."
            },
            {
                icon: "bi-clock-history",
                title: "Progress Tracking",
                desc: "Compare improvements across resume analysis results."
            }
        ]
    },


    "skill-gap-analysis": {
        eyebrow: "AI Skill Intelligence",

        title: "Discover the Skills You Need to Grow",

        subtitle:
            "Identify missing skills, understand development opportunities, and receive practical learning recommendations.",

        capabilities: [
            {
                icon: "bi-search",
                title: "Skill Detection",
                desc: "Identify skills currently present in your resume."
            },
            {
                icon: "bi-exclamation-diamond",
                title: "Skill Gaps",
                desc: "Discover important missing skills for target roles."
            },
            {
                icon: "bi-mortarboard",
                title: "Learning Suggestions",
                desc: "Receive practical recommendations for skill development."
            },
            {
                icon: "bi-graph-up-arrow",
                title: "Growth Opportunities",
                desc: "Understand where new skills can improve career readiness."
            }
        ]
    }
};


// ======================================================
// CURRENT ACTIVE FEATURE
// ======================================================

let activeFeatureId = null;


// ======================================================
// RENDER CAPABILITY CARDS
// ======================================================

function renderCapabilities(capabilities) {

    if (!capabilitiesContainer) {
        return;
    }

    capabilitiesContainer.innerHTML = capabilities
        .map(
            (capability) => `

                <article
                    class="ai-capability-card"
                    data-ai-card
                >

                    <span
                        class="ai-capability-card__icon"
                        aria-hidden="true"
                    >
                        <i class="bi ${capability.icon}"></i>
                    </span>


                    <h3 class="ai-capability-card__title">
                        ${capability.title}
                    </h3>


                    <p class="ai-capability-card__desc">
                        ${capability.desc}
                    </p>

                </article>

            `
        )
        .join("");
}


// ======================================================
// RESET ALL FEATURE STATES
// ======================================================

function resetFeatureStates() {

    featureTriggers.forEach((trigger) => {

        trigger.setAttribute(
            "aria-expanded",
            "false"
        );

    });


    featureCards.forEach((card) => {

        card.classList.remove("is-active");

    });

}


// ======================================================
// CLOSE SHOWCASE
// ======================================================

function closeShowcase() {

    if (!showcase) {
        return;
    }


    showcase.hidden = true;


    resetFeatureStates();


    activeFeatureId = null;

}


// ======================================================
// OPEN SHOWCASE
// ======================================================

function openShowcase(featureId, trigger) {

    const featureData = showcaseData[featureId];


    if (!featureData) {
        return;
    }


    // ----------------------------------
    // Update left side content
    // ----------------------------------

    showcaseEyebrow.textContent =
        featureData.eyebrow;


    showcaseTitle.textContent =
        featureData.title;


    showcaseSubtitle.textContent =
        featureData.subtitle;


    // ----------------------------------
    // Render right side capabilities
    // ----------------------------------

    renderCapabilities(
        featureData.capabilities
    );


    // ----------------------------------
    // Reset previous active states
    // ----------------------------------

    resetFeatureStates();


    // ----------------------------------
    // Activate selected trigger
    // ----------------------------------

    trigger.setAttribute(
        "aria-expanded",
        "true"
    );


    const selectedCard = document.querySelector(
        `[data-feature-card="${featureId}"]`
    );


    selectedCard?.classList.add("is-active");


    // ----------------------------------
    // Show Product Showcase
    // ----------------------------------

    showcase.hidden = false;


    activeFeatureId = featureId;


    // ----------------------------------
    // Smooth scroll
    // ----------------------------------

    showcase.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}


// ======================================================
// FEATURE CLICK EVENTS
// ======================================================

if (
    showcase &&
    showcaseEyebrow &&
    showcaseTitle &&
    showcaseSubtitle &&
    capabilitiesContainer &&
    featureTriggers.length
) {

    featureTriggers.forEach((trigger) => {

        trigger.addEventListener("click", () => {

            const featureId =
                trigger.dataset.featureTrigger;


            // ----------------------------------
            // SAME FEATURE CLICKED AGAIN
            // CLOSE SHOWCASE
            // ----------------------------------

            if (activeFeatureId === featureId) {

                closeShowcase();

                return;

            }


            // ----------------------------------
            // NEW FEATURE SELECTED
            // OPEN / UPDATE SHOWCASE
            // ----------------------------------

            openShowcase(
                featureId,
                trigger
            );

        });

    });

}