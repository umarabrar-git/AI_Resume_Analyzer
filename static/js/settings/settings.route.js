const navigationItems = Array.from(
    document.querySelectorAll("[data-account-tab]")
);

const accountPanels = Array.from(
    document.querySelectorAll("[data-account-panel]")
);

const validTabs = accountPanels.map(
    (panel) => panel.dataset.accountPanel
);

function openAccountTab(tabName, updateUrl = true) {
    if (!validTabs.includes(tabName)) {
        tabName = "profile";
    }

    navigationItems.forEach((item) => {
        const active = item.dataset.accountTab === tabName;
        item.classList.toggle("is-active", active);
    });

    accountPanels.forEach((panel) => {
        const active = panel.dataset.accountPanel === tabName;
        panel.classList.toggle("is-active", active);
    });

    if (updateUrl) {
        const url = new URL(window.location.href);
        url.searchParams.set("section", tabName);
        history.pushState({ tab: tabName }, "", url);
    }
}

navigationItems.forEach((item) => {
    item.addEventListener("click", () => {
        openAccountTab(item.dataset.accountTab);
    });
});

window.addEventListener("popstate", () => {
    const params = new URLSearchParams(window.location.search);
    openAccountTab(params.get("section") || "profile", false);
});

const params = new URLSearchParams(window.location.search);
openAccountTab(params.get("section") || "profile", false);
