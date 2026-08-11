import { initAtsChart } from "./ats-chart.js";
import { initSkillsChart } from "./skills-chart.js";
import { initMatchChart } from "./match-chart.js";


function safeNumber(value, fallback = 0) {
    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
}


function safeArray(value) {
    return Array.isArray(value)
        ? value
        : [];
}


function safeObject(value) {
    return (
        value &&
        typeof value === "object" &&
        !Array.isArray(value)
    )
        ? value
        : {};
}


function readChartState() {
    return {
        // ---------------------------------
        // ATS
        // ---------------------------------

        atsScore: safeNumber(
            window.atsScore
        ),

        atsBreakdown: safeObject(
            window.atsBreakdown
        ),

        // ---------------------------------
        // Job Matching
        // ---------------------------------

        matchedSkills: safeNumber(
            window.matchedSkills
        ),

        missingSkills: safeNumber(
            window.missingSkills
        ),

        matchPercentage: safeNumber(
            window.matchPercentage
        ),

        // ---------------------------------
        // Skills
        // ---------------------------------

        skillLabels: safeArray(
            window.skillLabels
        ),

        skillScores: safeArray(
            window.skillScores
        ),
    };
}


function initCharts() {
    if (typeof Chart === "undefined") {
        return;
    }

    const state = readChartState();

    initAtsChart(state);
    initSkillsChart(state);
    initMatchChart(state);
}


document.addEventListener(
    "DOMContentLoaded",
    initCharts
);