import { updateRings, updateBars } from "./gauge-utils.js";
import { animateGaugeValue } from "./gauge-animate.js";

function refreshCards() {
    updateRings();
    updateBars();
}

document.addEventListener("DOMContentLoaded", () => {
    refreshCards();
    animateGaugeValue();
});

window.addEventListener("resize", refreshCards);
