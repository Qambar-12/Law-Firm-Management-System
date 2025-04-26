// script.js

document.addEventListener("DOMContentLoaded", function () {
    // Sidebar toggle for mobile
    const toggleBtn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("d-none");
        });
    }

    // Flip card animation
    const flipCards = document.querySelectorAll(".flip-card");
    flipCards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.querySelector(".flip-card-inner").style.transform = "rotateY(180deg)";
        });
        card.addEventListener("mouseleave", () => {
            card.querySelector(".flip-card-inner").style.transform = "rotateY(0deg)";
        });
    });
});
