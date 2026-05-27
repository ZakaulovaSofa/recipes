/* jshint esversion: 6, strict: global */
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('change', (event) => {
        const input = event.target;

        if (!input.classList.contains('file-upload-input')) {
            return;
        }

        const file = input.files && input.files[0];

        if (!file) {
            return;
        }

        const dropzone = input.closest('.file-upload-dropzone');

        if (!dropzone) {
            return;
        }

        const placeholder = dropzone.querySelector('.file-upload-placeholder');
        const preview = dropzone.querySelector('.file-upload-preview');

        dropzone.classList.add('has-file');

        if (placeholder) {
            placeholder.textContent = `Выбрано: ${file.name}`;
        }

        if (preview && file.type.startsWith('image/')) {
            const reader = new FileReader();

            reader.addEventListener('load', () => {
                preview.src = reader.result;
                preview.classList.add('is-visible');
            });

            reader.readAsDataURL(file);
        }
    });
});