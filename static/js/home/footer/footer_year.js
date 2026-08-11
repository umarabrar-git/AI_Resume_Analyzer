const footerYearNode = document.querySelector("[data-footer-year]");

if (footerYearNode) {
    footerYearNode.textContent = String(new Date().getFullYear());
}
