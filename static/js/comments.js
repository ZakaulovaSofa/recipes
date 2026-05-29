/* jshint esversion: 6, strict: global */
document.addEventListener('DOMContentLoaded', () => {
    syncCommentEditForms();
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
        }
    });

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
})