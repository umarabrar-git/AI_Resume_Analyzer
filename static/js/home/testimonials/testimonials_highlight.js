document.addEventListener("DOMContentLoaded", () => {
  /* =====================================================
       ELEMENTS
       ===================================================== */

  const grid = document.querySelector("[data-testimonials-grid]");

  const track = document.querySelector("[data-testimonial-track]");

  const cards = Array.from(
    document.querySelectorAll("[data-testimonial-card]"),
  );

  const previousButton = document.querySelector("[data-testimonial-prev]");

  const nextButton = document.querySelector("[data-testimonial-next]");

  const dotsContainer = document.querySelector("[data-testimonial-dots]");

  /* =====================================================
       SAFETY CHECK
       ===================================================== */

  if (!grid || !track || !cards.length) {
    return;
  }

  /* =====================================================
       VARIABLES
       ===================================================== */

  let activeIndex = 0;

  let autoSlideTimer = null;

  let resizeTimer = null;

  let touchStartX = 0;

  let touchEndX = 0;

  /* =====================================================
       RESPONSIVE VISIBLE CARDS
       ===================================================== */

  const getVisibleCards = () => {
    if (window.innerWidth <= 650) {
      return 1;
    }

    if (window.innerWidth <= 1000) {
      return 2;
    }

    return 3;
  };

  /* =====================================================
       MAX SLIDE INDEX
       ===================================================== */

  const getMaxIndex = () => {
    const visibleCards = getVisibleCards();

    return Math.max(0, cards.length - visibleCards);
  };

  /* =====================================================
       CREATE DOTS
       ===================================================== */

  const createDots = () => {
    if (!dotsContainer) {
      return;
    }

    dotsContainer.innerHTML = "";

    const totalSlides = getMaxIndex() + 1;

    for (let index = 0; index < totalSlides; index++) {
      const dot = document.createElement("button");

      dot.type = "button";

      dot.className = "testimonials-section__dot";

      dot.setAttribute("aria-label", `Go to testimonial slide ${index + 1}`);

      dot.addEventListener("click", () => {
        activeIndex = index;

        updateSlider();

        restartAutoSlide();
      });

      dotsContainer.appendChild(dot);
    }
  };

  /* =====================================================
       UPDATE DOTS
       ===================================================== */

  const updateDots = () => {
    if (!dotsContainer) {
      return;
    }

    const dots = Array.from(dotsContainer.children);

    dots.forEach((dot, index) => {
      dot.classList.toggle("is-active", index === activeIndex);
    });
  };

  /* =====================================================
       CALCULATE SLIDE DISTANCE
       ===================================================== */

  const getSlideDistance = () => {
    const firstCard = cards[0];

    if (!firstCard) {
      return 0;
    }

    const cardWidth = firstCard.getBoundingClientRect().width;

    const trackStyles = window.getComputedStyle(track);

    const gap =
      parseFloat(trackStyles.columnGap) || parseFloat(trackStyles.gap) || 0;

    return cardWidth + gap;
  };

  /* =====================================================
       UPDATE SLIDER
       ===================================================== */

  const updateSlider = () => {
    const maxIndex = getMaxIndex();

    if (activeIndex > maxIndex) {
      activeIndex = maxIndex;
    }

    const slideDistance = getSlideDistance();

    const movement = activeIndex * slideDistance;

    track.style.transform = `translate3d(-${movement}px, 0, 0)`;

    updateDots();
  };

  /* =====================================================
       NEXT SLIDE
       ===================================================== */

  const goNext = () => {
    const maxIndex = getMaxIndex();

    if (activeIndex >= maxIndex) {
      activeIndex = 0;
    } else {
      activeIndex++;
    }

    updateSlider();
  };

  /* =====================================================
       PREVIOUS SLIDE
       ===================================================== */

  const goPrevious = () => {
    const maxIndex = getMaxIndex();

    if (activeIndex <= 0) {
      activeIndex = maxIndex;
    } else {
      activeIndex--;
    }

    updateSlider();
  };

  /* =====================================================
       NEXT BUTTON
       ===================================================== */

  if (nextButton) {
    nextButton.addEventListener("click", () => {
      goNext();

      restartAutoSlide();
    });
  }

  /* =====================================================
       PREVIOUS BUTTON
       ===================================================== */

  if (previousButton) {
    previousButton.addEventListener("click", () => {
      goPrevious();

      restartAutoSlide();
    });
  }

  /* =====================================================
       START AUTO SLIDE
       ===================================================== */

  const startAutoSlide = () => {
    stopAutoSlide();

    autoSlideTimer = setInterval(() => {
      goNext();
    }, 3500);
  };

  /* =====================================================
       STOP AUTO SLIDE
       ===================================================== */

  const stopAutoSlide = () => {
    if (autoSlideTimer !== null) {
      clearInterval(autoSlideTimer);

      autoSlideTimer = null;
    }
  };

  /* =====================================================
       RESTART AUTO SLIDE
       ===================================================== */

  const restartAutoSlide = () => {
    startAutoSlide();
  };

  /* =====================================================
       PAUSE WHEN MOUSE ENTERS
       ===================================================== */

  grid.addEventListener("mouseenter", () => {
    stopAutoSlide();
  });

  /* =====================================================
       RESUME WHEN MOUSE LEAVES
       ===================================================== */

  grid.addEventListener("mouseleave", () => {
    startAutoSlide();
  });

  /* =====================================================
       TOUCH START
       ===================================================== */

  grid.addEventListener(
    "touchstart",
    (event) => {
      touchStartX = event.changedTouches[0].screenX;
    },
    {
      passive: true,
    },
  );

  /* =====================================================
       TOUCH END
       ===================================================== */

  grid.addEventListener(
    "touchend",
    (event) => {
      touchEndX = event.changedTouches[0].screenX;

      const swipeDistance = touchStartX - touchEndX;

      /*
       * Ignore very small movements
       */

      if (Math.abs(swipeDistance) < 50) {
        return;
      }

      if (swipeDistance > 0) {
        /*
         * Swipe left
         */

        goNext();
      } else {
        /*
         * Swipe right
         */

        goPrevious();
      }

      restartAutoSlide();
    },
    {
      passive: true,
    },
  );

  /* =====================================================
       KEYBOARD SUPPORT
       ===================================================== */

  document.addEventListener("keydown", (event) => {
    /*
     * Only react when carousel
     * is visible/focused area.
     */

    if (event.key === "ArrowRight") {
      goNext();

      restartAutoSlide();
    }

    if (event.key === "ArrowLeft") {
      goPrevious();

      restartAutoSlide();
    }
  });

  /* =====================================================
       WINDOW RESIZE
       ===================================================== */

  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);

    resizeTimer = setTimeout(() => {
      createDots();

      updateSlider();
    }, 150);
  });

  /* =====================================================
       INITIALIZE
       ===================================================== */

  createDots();

  updateSlider();

  startAutoSlide();
});
