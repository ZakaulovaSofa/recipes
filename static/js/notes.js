document.addEventListener('DOMContentLoaded', function() {
    console.log('notes.js загружен');
    
    // Инициализация модального окна удаления
    initDeleteNoteModal();
    
    // Инициализация кнопок просмотра (если нужны дополнительные функции)
    initViewNoteButtons();
});

// Модальное окно удаления заметки
function initDeleteNoteModal() {
    const deleteNoteModal = document.getElementById('delete-note-modal');
    const deleteNoteText = document.getElementById('delete-note-text');
    const deleteNoteForm = document.getElementById('delete-note-form');
    const cancelNoteDelete = document.getElementById('cancel-note-delete');
    const confirmNoteDelete = document.getElementById('confirm-note-delete');
    
    if (!deleteNoteModal) {
        console.log('Модальное окно не найдено (не страница заметок)');
        return;
    }
    
    console.log('Инициализация модального окна удаления заметок');
    
    // Все кнопки удаления заметок
    const deleteButtons = document.querySelectorAll('.note-btn-delete');
    console.log('Найдено кнопок удаления:', deleteButtons.length);
    
    // Обработчик для кнопок удаления
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const noteId = this.getAttribute('data-note-id');
            const noteTitle = this.getAttribute('data-note-title');
            
            if (deleteNoteText) {
                deleteNoteText.textContent = `Это действие нельзя отменить. Заметка «${noteTitle}» будет удалена навсегда.`;
            }
            
            if (deleteNoteForm) {
                deleteNoteForm.action = `/notes/${noteId}/delete`;
            }
            
            deleteNoteModal.classList.add('delete-modal-overlay-active');
            document.body.classList.add('modal-open');
        });
    });
    
    // Закрытие по кнопке Отмена
    if (cancelNoteDelete) {
        cancelNoteDelete.addEventListener('click', function() {
            deleteNoteModal.classList.remove('delete-modal-overlay-active');
            document.body.classList.remove('modal-open');
        });
    }
    
    // Подтверждение удаления
    if (confirmNoteDelete) {
        confirmNoteDelete.addEventListener('click', function() {
            if (deleteNoteForm) {
                deleteNoteForm.submit();
            }
        });
    }
    
    // Закрытие по клику на оверлей
    deleteNoteModal.addEventListener('click', function(e) {
        if (e.target === deleteNoteModal) {
            deleteNoteModal.classList.remove('delete-modal-overlay-active');
            document.body.classList.remove('modal-open');
        }
    });
    
    // Закрытие по клавише Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && deleteNoteModal.classList.contains('delete-modal-overlay-active')) {
            deleteNoteModal.classList.remove('delete-modal-overlay-active');
            document.body.classList.remove('modal-open');
        }
    });
}

// Кнопки просмотра заметок (если нужны)
function initViewNoteButtons() {
    const viewButtons = document.querySelectorAll('.note-btn-view');
    console.log('Найдено кнопок просмотра:', viewButtons.length);
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Просмотр заметки:', this.getAttribute('href'));
            // Здесь можно добавить дополнительную логику при просмотре
        });
    });
}