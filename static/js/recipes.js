document.addEventListener('DOMContentLoaded', () => {
    // INGREDIENTS
    const ingredientsContainer = document.getElementById('ingredients-container');
    const addIngredientBtn = document.getElementById('add-ingredient');

    if (ingredientsContainer && addIngredientBtn) {
        addIngredientBtn.addEventListener('click', () => {
            const ingredientRow = document.createElement('div');
            ingredientRow.classList.add('ingredient-row');
            ingredientRow.innerHTML = `
                <input type="text"
                       name="ingredient_name"
                       class="ingredient-name-input"
                       placeholder="Название"
                       required>
            
                <input type="text"
                       name="ingredient_amount"
                       class="ingredient-amount-input"
                       placeholder="Кол-во"
                       pattern="^\\\\s*\\\\d+([.,]\\\\d+)?\\\\s*$|^\\\\s*\\\\d+\\\\s*/\\\\s*\\\\d+\\\\s*$"
                       title="Введите число: например 100, 100.5, 100,5 или 1/2"
                       inputmode="decimal"
                       required>
            
                <select name="ingredient_unit"
                        class="ingredient-unit-input"
                        required>
                    <option value="" disabled selected>Ед. изм.</option>
                    <option value="г">граммы</option>
                    <option value="кг">килограммы</option>
                    <option value="л">литры</option>
                    <option value="мл">миллилитры</option>
                    <option value="ст. л.">столовые ложки</option>
                    <option value="ч. л.">чайные ложки</option>
                    <option value="стакан">стаканы</option>
                    <option value="капля">капли</option>
                    <option value="щепотка">щепотки</option>
                    <option value="шт">штуки</option>
                </select>
            
                <button type="button"
                        class="ingredient-delete-btn"
                        title="Удалить">
                    ×
                </button>
            `;
            ingredientsContainer.appendChild(ingredientRow);
        });

        ingredientsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('ingredient-delete-btn')) {
                const rows = ingredientsContainer.querySelectorAll('.ingredient-row');
                if (rows.length > 1) {
                    event.target.closest('.ingredient-row').remove();
                }
            }
        });
    }

    // STEPS
    const stepsContainer = document.getElementById('steps-container');
    const addStepBtn = document.getElementById('add-step');

    if (stepsContainer && addStepBtn) {
        addStepBtn.addEventListener('click', () => {
            const stepsCount = stepsContainer.querySelectorAll('.step-block').length + 1;
            const stepBlock = document.createElement('div');
            stepBlock.classList.add('step-block');
            stepBlock.innerHTML = `
                <div class="step-number-pill">Шаг ${stepsCount}</div>
                <div class="step-card">
                    <div class="step-image-dropzone">
                        <label class="step-image-label file-upload-dropzone">
                            <input 
                                type="file" 
                                name="step_images[]" 
                                class="step-image-input file-upload-input" 
                                accept="image/*"
                            >
                            <span class="step-image-placeholder file-upload-placeholder">
                                Загрузите фото шага
                            </span>
                            <img class="file-upload-preview" alt="Предпросмотр фото шага">
                        </label>
                    </div>
                    <textarea 
                        name="step_descriptions[]" 
                        class="step-description-textarea" 
                        placeholder="Описание шага..." 
                        rows="3" 
                        required
                    ></textarea>
                </div>
                <button type="button" class="step-delete-btn" title="Удалить шаг">×</button>
            `;
            stepsContainer.appendChild(stepBlock);
        });

        stepsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('step-delete-btn')) {
                const steps = stepsContainer.querySelectorAll('.step-block');
                if (steps.length > 1) {
                    event.target.closest('.step-block').remove();
                    updateStepNumbers();
                }
            }
        });

        function updateStepNumbers() {
            const allSteps = stepsContainer.querySelectorAll('.step-block');
            allSteps.forEach((step, index) => {
                const numberPill = step.querySelector('.step-number-pill');
                numberPill.textContent = `Шаг ${index + 1}`;
            });
        }
    }

    // DELETE RECIPE MODAL
    const deleteRecipeForm = document.getElementById('delete-recipe-form');
    const openDeleteModalBtn = document.getElementById('open-delete-modal');
    const deleteModalOverlay = document.getElementById('delete-modal-overlay');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');

    if (
        deleteRecipeForm &&
        openDeleteModalBtn &&
        deleteModalOverlay &&
        cancelDeleteBtn &&
        confirmDeleteBtn
    ) {
        openDeleteModalBtn.addEventListener('click', () => {
            deleteModalOverlay.classList.add('delete-modal-overlay-active');
        });

        cancelDeleteBtn.addEventListener('click', () => {
            deleteModalOverlay.classList.remove('delete-modal-overlay-active');
        });

        deleteModalOverlay.addEventListener('click', (event) => {
            if (event.target === deleteModalOverlay) {
                deleteModalOverlay.classList.remove('delete-modal-overlay-active');
            }
        });

        confirmDeleteBtn.addEventListener('click', () => {
            deleteRecipeForm.submit();
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                deleteModalOverlay.classList.remove('delete-modal-overlay-active');
            }
        });
    }

    const servingsControls = document.querySelectorAll('.servings-control');

    servingsControls.forEach((control) => {
        const input = control.querySelector('.servings-input');
        const minusBtn = control.querySelector('[data-action="minus"]');
        const plusBtn = control.querySelector('[data-action="plus"]');

        if (!input || !minusBtn || !plusBtn) {
            return;
        }

        minusBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value, 10) || 1;

            if (currentValue > 1) {
                input.value = currentValue - 1;
            }
        });

        plusBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value, 10) || 1;
            input.value = currentValue + 1;
        });
    });

    // FAVORITE TOGGLE VISUAL STATE
    document.addEventListener('click', (event) => {
        const favoriteButton = event.target.closest('.js-favorite-toggle');

        if (!favoriteButton) {
            return;
        }

        favoriteButton.classList.toggle('is-active');
    });
});