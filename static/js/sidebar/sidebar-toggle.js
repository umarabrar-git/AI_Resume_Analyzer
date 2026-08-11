export function initSidebarToggle() {
    const sidebar = document.getElementById("sidebar");
    const btn = document.getElementById("collapseBtn");
    const shell = document.querySelector(".dashboard-shell");

    if (!sidebar || !btn || !shell) {
        return;
    }

    const backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    shell.appendChild(backdrop);

    const isMobile = () => window.matchMedia("(max-width: 991px)").matches;

    const setCollapsedState = (collapsed) => {
        sidebar.classList.toggle("collapsed", collapsed);
        shell.classList.toggle("sidebar-collapsed", collapsed);
        btn.setAttribute("aria-label", collapsed ? "Expand sidebar" : "Collapse sidebar");
    };

    const openSidebar = () => {
        if (isMobile()) {
            sidebar.classList.add("is-open");
            backdrop.classList.add("is-visible");
            document.body.classList.add("sidebar-open");
        } else {
            setCollapsedState(false);
        }
    };

    const closeSidebar = () => {
        if (isMobile()) {
            sidebar.classList.remove("is-open");
            backdrop.classList.remove("is-visible");
            document.body.classList.remove("sidebar-open");
        } else {
            setCollapsedState(true);
        }
    };

    btn.addEventListener("click", () => {
        if (isMobile()) {
            if (sidebar.classList.contains("is-open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
            return;
        }

        const collapsed = sidebar.classList.toggle("collapsed");
        shell.classList.toggle("sidebar-collapsed", collapsed);
        btn.setAttribute("aria-label", collapsed ? "Expand sidebar" : "Collapse sidebar");
    });

    backdrop.addEventListener("click", closeSidebar);

    window.addEventListener("resize", () => {
        if (!isMobile()) {
            sidebar.classList.remove("is-open");
            backdrop.classList.remove("is-visible");
            document.body.classList.remove("sidebar-open");
            setCollapsedState(sidebar.classList.contains("collapsed"));
        }
    });
}
