import { verticalOptions } from "./chart-utils.js";


function normalizeCount(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return 0;
    }

    return Math.max(
        0,
        Math.round(number)
    );
}


export function initMatchChart(state) {
    const canvas = document.getElementById(
        "matchChart"
    );

    if (
        !canvas ||
        typeof Chart === "undefined"
    ) {
        return;
    }

    const matched = normalizeCount(
        state.matchedSkills
    );

    const missing = normalizeCount(
        state.missingSkills
    );

    const matchLabels = [
        "Matched",
        "Missing",
    ];

    const matchData = [
        matched,
        missing,
    ];

    const matchColors = [
        "#10b981",
        "#ef4444",
    ];

    const totalSkills =
        matched + missing;

    const dynamicMax = Math.max(
        5,
        matched,
        missing
    );

    const matchBaseOptions =
        verticalOptions(
            dynamicMax,
            2
        );

    new Chart(
        canvas,
        {
            type: "bar",

            data: {
                labels: matchLabels,

                datasets: [
                    {
                        label:
                            "Job Match",

                        data:
                            matchData,

                        backgroundColor:
                            matchColors,

                        borderRadius: 8,

                        maxBarThickness: 28,
                    },
                ],
            },

            options: {
                ...matchBaseOptions,

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label(context) {
                                const count =
                                    context.parsed.y;

                                const percentage =
                                    totalSkills > 0
                                        ? Math.round(
                                            (
                                                count /
                                                totalSkills
                                            ) * 100
                                        )
                                        : 0;

                                return (
                                    `${context.label}: ` +
                                    `${count} skills ` +
                                    `(${percentage}%)`
                                );
                            },
                        },
                    },
                },

                animation: {
                    duration: 700,
                    easing:
                        "easeOutCubic",
                },

                scales: {
                    ...matchBaseOptions.scales,

                    y: {
                        ...matchBaseOptions
                            .scales.y,

                        beginAtZero: true,

                        ticks: {
                            color:
                                "#64748b",

                            precision: 0,
                        },
                    },
                },
            },
        }
    );
}