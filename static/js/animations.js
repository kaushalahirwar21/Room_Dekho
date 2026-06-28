// Scroll Animation for fade-in elements
document.addEventListener('DOMContentLoaded', function() {
    const fadeElements = document.querySelectorAll('.fade-slide-up');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Uncomment if you want to animate only once
                // observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(el => {
        observer.observe(el);
    });
    
    // Navbar scroll animation
    const navbar = document.querySelector('nav');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('nav-scroll');
        } else {
            navbar.classList.remove('nav-scroll');
        }
        
        // Optional: hide navbar on scroll down, show on scroll up
        // if (window.scrollY > lastScrollY && window.scrollY > 100) {
        //     navbar.style.transform = 'translateY(-100%)';
        // } else {
        //     navbar.style.transform = 'translateY(0)';
        // }
        // lastScrollY = window.scrollY;
    });
    
    // Theme toggle smooth transition
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Add transition class to body for smooth color change
            document.body.classList.add('theme-transition');
            
            // Remove transition class after animation completes
            setTimeout(() => {
                document.body.classList.remove('theme-transition');
            }, 500);
        });
    }
});