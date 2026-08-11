import { verticalOptions } from "./chart-utils.js";

function clamp(value, min = 0, max = 100) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return min;
    }

    return Math.min(
        max,
        Math.max(min, number)
    );
}

function normalizeScore(value, fallback = 0) {
    if (value === null || value === undefined) {
        return fallback;
    }

    if (typeof value === "object") {
        value =
            value.percentage ??
            value.value ??
            value.score ??
            fallback;
    }

    let score = Number(value);

    if (!Number.isFinite(score)) {
        return fallback;
    }

    // Support normalized AI scores such as 0.82.
    if (score > 0 && score <= 1) {
        score *= 100;
    }

    return Math.round(
        clamp(score)
    );
}

function buildAtsBreakdown(state) {
    const ats = state.atsBreakdown || {};

    return {
        labels: [
            "Formatting",
            "Keywords",
            "Sections",
            "Readability",
            "Content",
        ],

        values: [
            normalizeScore(
                ats.formatting,
                state.atsScore
            ),

            normalizeScore(
                ats.keywords,
                state.atsScore
            ),

            normalizeScore(
                ats.sections,
                state.atsScore
            ),

            normalizeScore(
                ats.readability,
                state.atsScore
            ),

            normalizeScore(
                ats.content,
                state.atsScore
            ),
        ],
    };
}

function findWeakestFactor(labels, values) {
    if (!values.length) {
        return null;
    }

    let weakestIndex = 0;

    for (
        let index = 1;
        index < values.length;
        index++
    ) {
        if (
            values[index] <
            values[weakestIndex]
        ) {
            weakestIndex = index;
        }
    }

    return {
        label: labels[weakestIndex],
        score: values[weakestIndex],
    };
}

function updateAtsInsight(
    state,
    breakdown
) {
    const element =
        document.getElementById(
            "atsInsight"
        );

    if (!element) {
        return;
    }

    const weakest = findWeakestFactor(
        breakdown.labels,
        breakdown.values
    );

    if (!weakest) {
        element.textContent =
            "AI Insight ATS analysis is unavailable.";

        return;
    }

    const overall =
        normalizeScore(
            state.atsScore
        );

    if (overall >= 85) {
        element.textContent =
            `AI Insight Strong ATS performance at ${overall}%. ` +
            `${weakest.label} is currently the lowest scoring factor ` +
            `at ${weakest.score}%.`;
    }

    else if (overall >= 70) {
        element.textContent =
            `AI Insight Your ATS score is ${overall}%. ` +
            `Focus first on ${weakest.label}, which scored ` +
            `${weakest.score}%.`;
    }

    else {
        element.textContent =
            `AI Insight ATS score is ${overall}%. ` +
            `${weakest.label} needs the most attention ` +
            `at ${weakest.score}%.`;
    }
}

export function initAtsChart(state) {
    const canvas =
        document.getElementById(
            "atsChart"
        );

    if (
        !canvas ||
        typeof Chart === "undefined"
    ) {
        return;
    }

    const breakdown =
        buildAtsBreakdown(state);

    new Chart(
        canvas,
        {
            type: "bar",

            data: {
                labels:
                    breakdown.labels,

                datasets: [
                    {
                        label:
                            "ATS Score",

                        data:
                            breakdown.values,

                        backgroundColor: [
                            "#2563eb",
                            "#3b82f6",
                            "#60a5fa",
                            "#fb923c",
                            "#10b981",
                        ],

                        borderRadius: 8,

                        maxBarThickness: 24,
                    },
                ],
            },

            options: {
                ...verticalOptions(
                    100,
                    5
                ),

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label(context) {
                                return (
                                    `${context.label}: ` +
                                    `${context.parsed.y}%`
                                );
                            },
                        },
                    },
                },
            },
        }
    );

    updateAtsInsight(
        state,
        breakdown
    );
}