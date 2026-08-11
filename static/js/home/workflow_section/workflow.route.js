import "./step_highlight.js";

const workflowShell = document.querySelector(
    "[data-workflow-shell]"
);

if (workflowShell) {
    const observer = new IntersectionObserver(
        (entries, currentObserver) => {
            const isVisible = entries.some(
                (entry) => entry.isIntersecting
            );

            if (!isVisible) {
                return;
            }

            workflowShell.classList.add("is-visible");

            currentObserver.disconnect();
        },
        {
            threshold: 0.2,
            rootMargin: "0px 0px -8% 0px"
        }
    );

    observer.observe(workflowShell);
}