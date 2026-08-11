import { initSidebarToggle } from "./sidebar-toggle.js";
import { highlightActiveNavLink } from "./active-link.js";

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    highlightActiveNavLink();
});
