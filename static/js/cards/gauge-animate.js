export function animateGaugeValue() {
    const valueNodes = document.querySelectorAll(".gauge-value[data-target]");

    valueNodes.forEach((node) => {
        const target = parseInt(node.dataset.target || "0", 10);
        let start = null;
        const duration = 900;

        const tick = (timestamp) => {
            if (!start) start = timestamp;
            const progress = Math.min(1, (timestamp - start) / duration);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(target * eased);
            node.textContent = `${current}%`;

            if (progress < 1) {
                window.requestAnimationFrame(tick);
            } else {
                node.textContent = `${target}%`;
            }
        };

        window.requestAnimationFrame(tick);
    });
}
