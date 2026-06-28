/**
 * Room Dekho - Premium Animations & Interactions
 * High-performance vanilla JS animation controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all animations
    initScrollProgress();
    initBackToTop();
    initScrollReveals();
    initButtonRipples();
    initNavbarScrollEffects();
    initCardHoverEffects();
    initFormFloatingLabels();
});

/**
 * 1. Scroll Progress Indicator
 */
function initScrollProgress() {
    const progressContainer = document.createElement('div');
    progressContainer.className = 'scroll-progress-container';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress-bar';
    progressBar.id = 'scrollProgressBar';
    
    progressContainer.appendChild(progressBar);
    document.body.insertBefore(progressContainer, document.body.firstChild);
    
    window.addEventListener('scroll', () => {
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (totalHeight > 0) {
            const progress = (window.scrollY / totalHeight) * 100;
            progressBar.style.width = `${progress}%`;
        }
    });
}

/**
 * 2. Back to Top Button
 */
function initBackToTop() {
    const btn = document.createElement('button');
    btn.className = 'back-to-top-btn';
    btn.id = 'backToTopBtn';
    btn.setAttribute('aria-label', 'Back to Top');
    btn.innerHTML = '<i data-lucide="arrow-up" style="width: 20px; height: 20px;"></i>';
    
    document.body.appendChild(btn);
    
    // Toggle visibility based on scroll position
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });
    
    // Smooth scroll to top on click
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * 3. Scroll Reveal Animations (Intersection Observer)
 */
function initScrollReveals() {
    // Add reveal classes to standard sections and components
    const sections = document.querySelectorAll('.hero-section, .categories-grid, .section-header, .property-grid, .why-grid, .testimonials-grid, .cta-banner, .why-card');
    sections.forEach((sec, idx) => {
        if (!sec.classList.contains('reveal')) {
            sec.classList.add('reveal', 'reveal-up');
        }
    });

    const revealElements = document.querySelectorAll('.reveal');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.12
    };
    
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                
                // If it's a grid, trigger staggered children animation
                if (entry.target.classList.contains('categories-grid') || 
                    entry.target.classList.contains('property-grid') || 
                    entry.target.classList.contains('why-grid') || 
                    entry.target.classList.contains('testimonials-grid')) {
                    animateGridChildren(entry.target);
                }
                
                obs.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    revealElements.forEach(el => observer.observe(el));
}

function animateGridChildren(grid) {
    const children = grid.children;
    Array.from(children).forEach((child, idx) => {
        child.style.opacity = '0';
        child.style.transform = 'translateY(20px)';
        child.style.transition = `opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${idx * 0.1}s, transform 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${idx * 0.1}s`;
        
        // Trigger reflow to apply initial state
        child.getBoundingClientRect();
        
        child.style.opacity = '1';
        child.style.transform = 'translateY(0)';
    });
}

/**
 * 4. Button Click Ripple Effect
 */
function initButtonRipples() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn');
        if (!btn) return;
        
        // Add ripple span
        const ripple = document.createElement('span');
        ripple.className = 'btn-ripple';
        
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
        
        // Remove existing ripples
        const existing = btn.querySelector('.btn-ripple');
        if (existing) existing.remove();
        
        btn.appendChild(ripple);
        
        // Clean up after animation finishes
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
}

/**
 * 5. Navbar Dynamic Scroll Effects
 */
function initNavbarScrollEffects() {
    const nav = document.querySelector('nav');
    if (!nav) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            nav.classList.add('nav-scrolled');
        } else {
            nav.classList.remove('nav-scrolled');
        }
    });
}

/**
 * 6. Card Interactive Hover Effects
 */
function initCardHoverEffects() {
    // Add custom hover tilt or glow to property cards
    document.addEventListener('mousemove', (e) => {
        const card = e.target.closest('.property-card, .why-card');
        if (!card) return;
        
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
}

/**
 * 7. Form Floating Labels and Custom Focus Indicators
 */
function initFormFloatingLabels() {
    const inputs = document.querySelectorAll('.form-control');
    
    inputs.forEach(input => {
        // Add container focus class
        input.addEventListener('focus', () => {
            const group = input.closest('.form-group');
            if (group) group.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            const group = input.closest('.form-group');
            if (group) group.classList.remove('focused');
        });
    });
}