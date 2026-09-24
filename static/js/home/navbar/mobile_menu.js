const navbarShell = document.querySelector("[data-home-navbar-shell]");
const navbarToggle = document.querySelector("[data-home-navbar-toggle]");
const navbar = document.querySelector(".home-navbar");
const mobileBreakpoint = 900;

const isMobileNavbar = () => {
  const isTouchDevice = window.matchMedia(
    "(hover: none) and (pointer: coarse)",
  ).matches;
  return window.innerWidth < mobileBreakpoint || isTouchDevice;
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

    // Determine scroll direction
    if (currentScrollPosition > lastScrollPosition) {
      // Scrolling DOWN
      if (!isScrollingDown) {
        isScrollingDown = true;
        navbar.classList.add("navbar-hidden");
        // Close mobile menu if open
        closeMobileMenu();
      }
    } else {
      // Scrolling UP or at top
      if (isScrollingDown) {
        isScrollingDown = false;
        navbar.classList.remove("navbar-hidden");
      }
    }

    lastScrollPosition = currentScrollPosition;
  });
}
