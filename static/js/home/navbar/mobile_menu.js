const navbarShell = document.querySelector("[data-home-navbar-shell]");
const navbarToggle = document.querySelector("[data-home-navbar-toggle]");
const navbar = document.querySelector(".home-navbar");

const isMobileNavbar = () => {
  return window.matchMedia("(hover: none) and (pointer: coarse)").matches;
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

  window.addEventListener("resize", () => {
    if (!isMobileNavbar()) {
      closeMobileMenu();
    }
  });
}

// Scroll behavior - hide navbar menu on scroll down, show on scroll up
let lastScrollPosition = 0;
let isScrollingDown = false;

if (navbar) {
  window.addEventListener("scroll", () => {
    const currentScrollPosition = window.scrollY;

    if (currentScrollPosition > lastScrollPosition) {
      if (!isScrollingDown) {
        isScrollingDown = true;
        navbar.classList.add("navbar-hidden");
        closeMobileMenu();
      }
    } else {
      if (isScrollingDown) {
        isScrollingDown = false;
        navbar.classList.remove("navbar-hidden");
      }
    }

    lastScrollPosition = currentScrollPosition;
  });
}
