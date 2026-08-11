const workflowSteps = Array.from(document.querySelectorAll("[data-workflow-step]"));

if (workflowSteps.length) {
    let activeIndex = 0;

    const activate = (index) => {
        workflowSteps.forEach((step, i) => {
            step.classList.toggle("is-active", i === index);
        });
    };

    activate(activeIndex);

    setInterval(() => {
        activeIndex = (activeIndex + 1) % workflowSteps.length;
        activate(activeIndex);
    }, 1700);
}
