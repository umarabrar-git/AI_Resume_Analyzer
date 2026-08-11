const ctaShell = document.querySelector("[data-cta-shell]");

if (ctaShell) {
    setInterval(() => {
        ctaShell.classList.add("is-pulse");

        setTimeout(() => {
            ctaShell.classList.remove("is-pulse");
        }, 550);
    }, 2800);
}
