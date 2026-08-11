export function normalizePercent(raw) {
    return Math.min(100, Math.max(0, parseFloat(String(raw || "0").replace(/[^0-9.]+/g, "")) || 0));
}

export function updateRings() {
    const rings = document.querySelectorAll(".gauge-fill");
    const r = 52;
    const circumference = 2 * Math.PI * r;

    rings.forEach((ring) => {
        const value = normalizePercent(ring.dataset.value);
        ring.style.strokeDasharray = circumference;
        ring.style.strokeDashoffset = circumference - (circumference * value) / 100;
    });
}

export function updateBars() {
    const bars = document.querySelectorAll(".progress-fill, .skill-bar-fill, .sparkline-fill");
    bars.forEach((bar) => {
        const value = normalizePercent(bar.dataset.value);
        bar.style.width = `${value}%`;
    });
}
