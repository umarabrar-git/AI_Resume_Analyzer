export function wrapLabel(label, maxLineLength) {
    const text = String(label || "").trim();
    if (!text) return "";
    if (text.length <= maxLineLength) return text;

    if (!/\s/.test(text)) {
        const chunks = text.match(new RegExp(`.{1,${maxLineLength}}`, "g"));
        return chunks && chunks.length > 1 ? chunks : text;
    }

    const words = text.split(/\s+/);
    const lines = [];
    let current = "";

    words.forEach((word) => {
        const next = current ? `${current} ${word}` : word;
        if (next.length <= maxLineLength) {
            current = next;
        } else {
            if (current) lines.push(current);
            current = word;
        }
    });

    if (current) lines.push(current);
    return lines.length > 1 ? lines : text;
}

function xTickFont(labelCount) {
    if (labelCount <= 3) return 12;
    if (labelCount <= 5) return 11;
    return 10;
}

export function verticalOptions(maxY, labelCount) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { bottom: 10 } },
        scales: {
            x: {
                ticks: {
                    color: "#334155",
                    autoSkip: false,
                    maxRotation: 40,
                    minRotation: 0,
                    font: { size: xTickFont(labelCount) },
                    callback(value) {
                        const label = String(this.getLabelForValue(value) || "");
                        if (label.length <= 10) return label;
                        const mid = Math.ceil(label.length / 2);
                        const breakAt = label.lastIndexOf(" ", mid) > 0 ? label.lastIndexOf(" ", mid) : mid;
                        return [label.slice(0, breakAt).trim(), label.slice(breakAt).trim()];
                    },
                },
                grid: { display: false },
            },
            y: { beginAtZero: true, max: maxY, ticks: { color: "#64748b" } },
        },
    };
}
