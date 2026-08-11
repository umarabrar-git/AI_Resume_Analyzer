export function highlightActiveNavLink() {
    document.querySelectorAll(".nav-link").forEach((link) => {
        if (link.getAttribute("href") === window.location.pathname) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });
}
