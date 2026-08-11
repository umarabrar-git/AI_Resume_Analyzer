import { verticalOptions } from "./chart-utils.js";


function normalizeScore(value) {
    let score = Number(value);

    if (!Number.isFinite(score)) {
        return 0;
    }

    // Support normalized semantic scores: 0.87 -> 87
    if (score > 0 && score <= 1) {
        score *= 100;
    }

    return Math.round(
        Math.min(
            100,
            Math.max(0, score)
        )
    );
}


function buildSkillData(state) {
    const labels = Array.isArray(
        state.skillLabels
    )
        ? state.skillLabels.slice(0, 5)
        : [];

    const scores = Array.isArray(
        state.skillScores
    )
        ? state.skillScores.slice(0, 5)
        : [];

    /*
     * Do NOT invent skill strengths.
     *
     * If the AI/NLP layer has no confidence/strength score,
     * the chart receives 0 rather than generating fake data.
     */
    const values = labels.map(
        (_, index) =>
            normalizeScore(
                scores[index]
            )
    );

    return {
        labels,
        values,
    };
}


function findStrongestSkill(
    labels,
    values
) {
    if (
        !labels.length ||
        !values.length
    ) {
        return null;
    }

    let strongestIndex = 0;

    for (
        let index = 1;
        index < values.length;
        index++
    ) {
        if (
            values[index] >
            values[strongestIndex]
        ) {
            strongestIndex = index;
        }
    }

    return {
        name:
            labels[strongestIndex],

        score:
            values[strongestIndex],
    };
}


function updateSkillsInsight(
    skillData
) {
    const element =
        document.getElementById(
            "skillsInsight"
        );

    if (!element) {
        return;
    }

    if (!skillData.labels.length) {
        element.textContent =
            "AI Insight No skills were detected in the resume.";

        return;
    }

    const strongest =
        findStrongestSkill(
            skillData.labels,
            skillData.values
        );

    if (
        strongest &&
        strongest.score > 0
    ) {
        element.textContent =
            `AI Insight ${strongest.name} has the highest ` +
            `detected strength at ${strongest.score}%.`;

        return;
    }

    /*
     * Skills were detected but the analysis engine did not
     * provide evidence-based strength scores.
     */
    element.textContent =
        `AI Insight ${skillData.labels.length} key skills ` +
        `were detected. Strength scoring is not available yet.`;
}


export function initSkillsChart(state) {
    const canvas =
        document.getElementById(
            "skillsChart"
        );

    if (
        !canvas ||
        typeof Chart === "undefined"
    ) {
        return;
    }

    const skillData =
        buildSkillData(state);

    if (!skillData.labels.length) {
        updateSkillsInsight(
            skillData
        );

        return;
    }

    new Chart(
        canvas,
        {
            type: "bar",

            data: {
                labels:
                    skillData.labels,

                datasets: [
                    {
                        label:
                            "Skill Strength",

                        data:
                            skillData.values,

                        backgroundColor: [
                            "#7c3aed",
                            "#8b5cf6",
                            "#a78bfa",
                            "#c4b5fd",
                            "#ddd6fe",
                        ],

                        borderRadius: 8,

                        maxBarThickness: 24,
                    },
                ],
            },

            options: {
                ...verticalOptions(
                    100,
                    skillData.labels.length
                ),

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            title(items) {
                                const index =
                                    items?.[0]
                                        ?.dataIndex ?? 0;

                                return (
                                    skillData
                                        .labels[index]
                                    || ""
                                );
                            },

                            label(context) {
                                const index =
                                    context.dataIndex;

                                const skill =
                                    skillData
                                        .labels[index]
                                    || "";

                                const score =
                                    context.parsed.y;

                                if (score <= 0) {
                                    return (
                                        `${skill}: ` +
                                        "strength not scored"
                                    );
                                }

                                return (
                                    `${skill}: ` +
                                    `${score}%`
                                );
                            },
                        },
                    },
                },

                animation: {
                    duration: 800,
                    easing:
                        "easeOutQuart",
                },
            },
        }
    );

    updateSkillsInsight(
        skillData
    );
}