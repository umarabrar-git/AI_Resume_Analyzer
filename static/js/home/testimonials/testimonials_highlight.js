const testimonialCards = Array.from(document.querySelectorAll("[data-testimonial-card]"));

if (testimonialCards.length) {
    let activeIndex = 0;

    const highlightCard = (index) => {
        testimonialCards.forEach((card, currentIndex) => {
            card.classList.toggle("is-active", currentIndex === index);
        });
    };

    highlightCard(activeIndex);

    setInterval(() => {
        activeIndex = (activeIndex + 1) % testimonialCards.length;
        highlightCard(activeIndex);
    }, 2200);
}
