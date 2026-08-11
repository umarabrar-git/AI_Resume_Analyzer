const homeNavbar = document.querySelector("#home-navbar");

if (homeNavbar) {
    const syncNavbarState = () => {
        homeNavbar.classList.toggle("is-scrolled", window.scrollY > 8);
    };

    syncNavbarState();
    window.addEventListener("scroll", syncNavbarState, { passive: true });
}
