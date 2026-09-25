const homeNavbar = document.querySelector("#home-navbar");

if (homeNavbar) {
  /* =========================================
       SCROLLED STATE
    ========================================= */

  const syncNavbarState = () => {
    homeNavbar.classList.toggle("is-scrolled", window.scrollY > 8);
  };

  syncNavbarState();

  window.addEventListener("scroll", syncNavbarState, { passive: true });

  /* =========================================
       HIDE ON SCROLL DOWN
       SHOW ON SCROLL UP
    ========================================= */

  let lastScrollPosition = window.scrollY;

  let isScrollingDown = false;

  window.addEventListener(
    "scroll",
    () => {
      const currentScrollPosition = window.scrollY;

      /* Always show navbar at top */
      if (currentScrollPosition <= 8) {
        homeNavbar.classList.remove("navbar-hidden");

        isScrollingDown = false;

        lastScrollPosition = currentScrollPosition;

        return;
      }

      /* Scrolling DOWN */
      if (currentScrollPosition > lastScrollPosition) {
        if (!isScrollingDown) {
          isScrollingDown = true;

          homeNavbar.classList.add("navbar-hidden");
        }
      } else if (currentScrollPosition < lastScrollPosition) {

      /* Scrolling UP */
        if (isScrollingDown) {
          isScrollingDown = false;

          homeNavbar.classList.remove("navbar-hidden");
        }
      }

      lastScrollPosition = currentScrollPosition;
    },
    { passive: true },
  );
}
