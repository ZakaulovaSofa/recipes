/* jshint esversion: 6, strict: global */
document.addEventListener('DOMContentLoaded', () => {
    syncCommentEditForms();

    let activeDeleteForm = null;

    const deleteModalOverlay = document.getElementById('comment-delete-modal-overlay');
    const cancelDeleteBtn = document.getElementById('cancel-comment-delete');
    const confirmDeleteBtn = document.getElementById('confirm-comment-delete');
    const previewText = document.getElementById('comment-delete-preview-text');

    document.addEventListener('click', (event) => {
        const editButton = event.target.closest('.comment-edit-btn');

        if (editButton) {
            const commentItem = editButton.closest('.comment-item');

            if (!commentItem) {
                return;
            }

            resetCommentTextarea(commentItem);
            commentItem.classList.add('is-editing');
            return;
        }

        const cancelButton = event.target.closest('.comment-cancel-edit-btn');

        if (cancelButton) {
            const commentItem = cancelButton.closest('.comment-item');

            if (!commentItem) {
                return;
            }

            resetCommentTextarea(commentItem);
            commentItem.classList.remove('is-editing');
            return;
        }

        const deleteButton = event.target.closest('.js-open-comment-delete-modal');

        if (deleteButton) {
            const deleteForm = deleteButton.closest('.comment-delete-form');

            if (!deleteForm || !deleteModalOverlay) {
                return;
            }

            activeDeleteForm = deleteForm;

            const commentText = deleteButton.dataset.commentText || '';

            if (previewText) {
                previewText.textContent = commentText;
            }

            deleteModalOverlay.classList.add('comment-delete-modal-overlay-active');
        }
    });

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            closeCommentDeleteModal();
        });
    }

    if (deleteModalOverlay) {
        deleteModalOverlay.addEventListener('click', (event) => {
            if (event.target === deleteModalOverlay) {
                closeCommentDeleteModal();
            }
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => {
            if (activeDeleteForm) {
                activeDeleteForm.submit();
            }
        });
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeCommentDeleteModal();
        }
    });

    function closeCommentDeleteModal() {
        if (deleteModalOverlay) {
            deleteModalOverlay.classList.remove('comment-delete-modal-overlay-active');
        }

        activeDeleteForm = null;

        if (previewText) {
            previewText.textContent = '';
        }
    }

    function syncCommentEditForms() {
        const commentItems = document.querySelectorAll('.comment-item');

        commentItems.forEach((commentItem) => {
            resetCommentTextarea(commentItem);
            commentItem.classList.remove('is-editing');
        });
    }

    function resetCommentTextarea(commentItem) {
        const textContent = commentItem.querySelector('.comment-text-content');
        const textarea = commentItem.querySelector('.comment-edit-textarea');

        if (!textContent || !textarea) {
            return;
        }

        textarea.value = textContent.textContent;
    }
});