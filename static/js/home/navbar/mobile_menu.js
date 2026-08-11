const navbarShell = document.querySelector("[data-home-navbar-shell]");
const navbarToggle = document.querySelector("[data-home-navbar-toggle]");
const navbar = document.querySelector(".home-navbar");

if (navbarShell && navbarToggle) {
    navbarToggle.addEventListener("click", () => {
        const isOpen = navbarShell.classList.toggle("is-open");
        navbarToggle.setAttribute("aria-expanded", String(isOpen));
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
                if (navbarShell && navbarShell.classList.contains("is-open")) {
                    navbarShell.classList.remove("is-open");
                    if (navbarToggle) {
                        navbarToggle.setAttribute("aria-expanded", "false");
                    }
                }
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
