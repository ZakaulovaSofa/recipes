// Бургер-меню
document.addEventListener('DOMContentLoaded', function() {
    const burgerBtn = document.getElementById('burgerBtn');
    const navMenu = document.getElementById('navMenu');
    const body = document.body;
    
    if (burgerBtn && navMenu) {
        burgerBtn.addEventListener('click', function() {
            burgerBtn.classList.toggle('active');
            navMenu.classList.toggle('active');
            body.classList.toggle('menu-open');
        });
        
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                burgerBtn.classList.remove('active');
                navMenu.classList.remove('active');
                body.classList.remove('menu-open');
            });
        });
        
        body.addEventListener('click', function(e) {
            if (body.classList.contains('menu-open') && !navMenu.contains(e.target) && !burgerBtn.contains(e.target)) {
                burgerBtn.classList.remove('active');
                navMenu.classList.remove('active');
                body.classList.remove('menu-open');
            }
        });
    }
});