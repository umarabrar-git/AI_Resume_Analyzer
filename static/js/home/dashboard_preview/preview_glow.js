const previewFrame = document.querySelector("[data-dashboard-preview-frame]");

if (previewFrame) {
    previewFrame.addEventListener("mouseenter", () => {
        previewFrame.classList.add("is-emphasis");
    });

    previewFrame.addEventListener("mouseleave", () => {
        previewFrame.classList.remove("is-emphasis");
    });
}
