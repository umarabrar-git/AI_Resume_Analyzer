const trustedSlider = document.querySelector("[data-trusted-slider]");
const trustedTrack = document.querySelector("[data-trusted-track]");

if (trustedSlider && trustedTrack) {
    let rafId = null;
    let offset = 0;
    const speed = 0.35;
    const mobileBreakpoint = 992;

    const shouldAnimate = () => {
        const hasDesktopWidth = window.innerWidth >= mobileBreakpoint;
        const hasOverflow = trustedTrack.scrollWidth > trustedSlider.clientWidth + 8;
        return hasDesktopWidth && hasOverflow;
    };

    const tick = () => {
        if (!shouldAnimate()) {
            offset = 0;
            trustedTrack.style.transform = "translateX(0)";
            rafId = null;
            return;
        }

        const maxOffset = Math.max(trustedTrack.scrollWidth - trustedSlider.clientWidth, 0);
        offset += speed;

        if (offset > maxOffset) {
            offset = 0;
        }

        trustedTrack.style.transform = `translateX(${-offset}px)`;
        rafId = requestAnimationFrame(tick);
    };

    const resetTrack = () => {
        offset = 0;
        trustedTrack.style.transform = "translateX(0)";

        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }

        if (shouldAnimate()) {
            rafId = requestAnimationFrame(tick);
        }
    };

    trustedSlider.addEventListener("mouseenter", () => {
        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    });

    trustedSlider.addEventListener("mouseleave", () => {
        if (!rafId && shouldAnimate()) {
            rafId = requestAnimationFrame(tick);
        }
    });

    window.addEventListener("resize", resetTrack);

    if (shouldAnimate()) {
        rafId = requestAnimationFrame(tick);
    }
}
