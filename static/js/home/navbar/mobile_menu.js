const navbarShell = document.querySelector("[data-home-navbar-shell]");

const navbarToggle = document.querySelector("[data-home-navbar-toggle]");

const MOBILE_BREAKPOINT = 900;

const isMobileNavbar = () => {
  return window.innerWidth <= MOBILE_BREAKPOINT;
};

const closeMobileMenu = () => {
  if (!navbarShell || !navbarToggle) {
    return;
  }

  navbarShell.classList.remove("is-open");

  navbarToggle.setAttribute("aria-expanded", "false");
};

if (navbarShell && navbarToggle) {
  navbarToggle.addEventListener("click", () => {
    if (!isMobileNavbar()) {
      return;
    }

    const isOpen = navbarShell.classList.toggle("is-open");

    navbarToggle.setAttribute("aria-expanded", String(isOpen));
  });

  /* Close menu when resizing to desktop */
  window.addEventListener("resize", () => {
    if (!isMobileNavbar()) {
      closeMobileMenu();
    }
  });
}
