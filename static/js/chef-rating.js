function renderStars(rating, containerId, interactive = false, userRating = 0) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = (rating - fullStars) >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    // Рисуем полные звезды
    for (let i = 0; i < fullStars; i++) {
        container.appendChild(createStarIcon('full', i + 1, interactive, userRating === i + 1));
    }
    
    // Рисуем половинку (если нужна)
    if (hasHalfStar) {
        container.appendChild(createStarIcon('half', fullStars + 1, interactive, userRating === fullStars + 1));
    }
    
    // Рисуем пустые звезды
    for (let i = 0; i < emptyStars; i++) {
        const starNumber = fullStars + (hasHalfStar ? 1 : 0) + i + 1;
        container.appendChild(createStarIcon('empty', starNumber, interactive, userRating === starNumber));
    }
}

/**
 * Создает SVG иконку звезды
 */
function createStarIcon(type, value, interactive, isActive) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "24");
    svg.setAttribute("height", "24");
    
    if (interactive) {
        svg.style.cursor = "pointer";
        svg.style.transition = "transform 0.2s";
        svg.addEventListener("mouseenter", () => svg.style.transform = "scale(1.1)");
        svg.addEventListener("mouseleave", () => svg.style.transform = "scale(1)");
        svg.addEventListener("click", () => selectRating(value));
    }
    
    let path = document.createElementNS(svgNS, "path");
    
    if (type === 'full') {
        path.setAttribute("d", "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z");
        path.setAttribute("fill", "#ff3b30");
        path.setAttribute("stroke", "#ff3b30");
    } else if (type === 'half') {
        path.setAttribute("d", "M12 2 L9.19 8.63 L2 9.24 L5.46 13.97 L3.82 21 L12 17.27 L12 2 Z");
        path.setAttribute("fill", "#ff3b30");
        path.setAttribute("stroke", "#ddd");
        
        const outline = document.createElementNS(svgNS, "path");
        outline.setAttribute("d", "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z");
        outline.setAttribute("fill", "none");
        outline.setAttribute("stroke", "#ddd");
        outline.setAttribute("stroke-width", "1.5");
        svg.appendChild(outline);
        svg.appendChild(path);
        return svg;
    } else {
        path.setAttribute("d", "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#ddd");
        path.setAttribute("stroke-width", "1.5");
    }
    
    if (interactive && isActive) {
        svg.style.filter = "drop-shadow(0 0 3px rgba(255, 59, 48, 0.5))";
        path.setAttribute("stroke", "#ff3b30");
        path.setAttribute("stroke-width", "2");
    }
    
    svg.appendChild(path);
    return svg;
}

/**
 * Обработчик выбора оценки
 */
let selectedRatingValue = 0;

function selectRating(value) {
    selectedRatingValue = value;
    
    const ratingInput = document.querySelector('input[name="rating"]');
    if (ratingInput) ratingInput.value = value;
    
    const starsContainer = document.querySelector('.chef-stars-selector');
    if (starsContainer && starsContainer.id) {
        renderStars(value, starsContainer.id, true, value);
    }
    
    const hint = document.querySelector('.rating-hint');
    if (hint) {
        const text = value === 1 ? 'звезду' : (value < 5 ? 'звезды' : 'звезд');
        hint.textContent = `Вы выбрали ${value} ${text}`;
        hint.style.display = 'block';
        setTimeout(() => {
            hint.style.opacity = '0';
            setTimeout(() => hint.style.display = 'none', 300);
        }, 2000);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Отображение среднего рейтинга
    const avgRatingElement = document.getElementById('chefAvgRating');
    if (avgRatingElement) {
        const avgRating = parseFloat(avgRatingElement.dataset.rating);
        renderStars(avgRating, 'chefStarsDisplay', false, 0);
    }
    
    // Интерактивные звезды для выбора оценки
    const userRatingElement = document.getElementById('chefUserRating');
    if (userRatingElement) {
        const userRating = parseInt(userRatingElement.dataset.rating);
        renderStars(userRating || 5, 'chefStarsSelector', true, userRating || 0);
        
        if (userRating) {
            const ratingInput = document.getElementById('ratingInput');
            if (ratingInput) ratingInput.value = userRating;
        }
    }
});