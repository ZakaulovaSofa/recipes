document.addEventListener('DOMContentLoaded', function() {
    const addTagBtn = document.getElementById('addTagBtn');
    const tagsList = document.getElementById('tagsList');
    const newTagInput = document.getElementById('newTagInput');

    if (!addTagBtn || !tagsList || !newTagInput) return;

    // Функция для добавления нового тега из инпута страницы
    addTagBtn.addEventListener('click', function() {
        const tagName = newTagInput.value;
        
        if (!tagName || tagName.trim() === '') return;

        const cleanTagName = tagName.trim().toLowerCase();

        // Создаем контейнер для компонента тега
        const tagWrapper = document.createElement('div');
        tagWrapper.className = 'chef-edit-tag-item';
        
        // Генерируем структуру HTML-компонента
        tagWrapper.innerHTML = `
            <span class="chef-edit-tag-pill">${cleanTagName}</span>
            <input type="hidden" name="tags[]" value="${cleanTagName}">
            <button type="button" class="chef-edit-tag-remove" aria-label="Удалить тег">×</button>
        `;

        tagsList.appendChild(tagWrapper);
        
        // Очищаем инпут для ввода следующего тега
        newTagInput.value = '';
    });

    // Позволяем добавлять тег по нажатию клавиши Enter внутри инпута
    newTagInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Защита от случайной отправки всей формы
            addTagBtn.click();
        }
    });

    // Делегирование события для удаления тегов по клику на крестик
    tagsList.addEventListener('click', function(e) {
        if (e.target.classList.contains('chef-edit-tag-remove')) {
            const tagItem = e.target.closest('.chef-edit-tag-item');
            if (tagItem) {
                tagItem.remove();
            }
        }
    });
});
