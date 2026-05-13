/* jshint esversion: 6, strict: global */
document.addEventListener('DOMContentLoaded', () => {
    // INGREDIENTS
    const ingredientsContainer = document.getElementById('ingredients-container');
    const addIngredientBtn = document.getElementById('add-ingredient');
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
                   required>
            <input type="text"
                   name="ingredient_unit"
                   class="ingredient-unit-input"
                   placeholder="Ед. изм."
                   required>
            <button type="button"
                    class="ingredient-delete-btn"
                    title="Удалить">
                ×
            </button>
        `;
        ingredientsContainer.appendChild(ingredientRow);
    });

    // Удаление ингредиента
    ingredientsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('ingredient-delete-btn')) {
            const rows = ingredientsContainer.querySelectorAll('.ingredient-row');
            // Оставляем минимум 1 строку
            if (rows.length > 1) {
                event.target.closest('.ingredient-row').remove();
            }
        }
    });

    // STEPS
    const stepsContainer = document.getElementById('steps-container');
    const addStepBtn = document.getElementById('add-step');

    addStepBtn.addEventListener('click', () => {
        const stepsCount = stepsContainer.querySelectorAll('.step-block').length + 1;
        const stepBlock = document.createElement('div');
        stepBlock.classList.add('step-block');
        stepBlock.innerHTML = `
            <div class="step-number-pill">
                Шаг ${stepsCount}
            </div>
            <div class="step-card">
                <div class="step-image-dropzone">
                    <label class="step-image-label">
                        <input type="file"
                               name="step_images[]"
                               class="step-image-input"
                               accept="image/*">
                        <span class="step-image-placeholder">
                            Загрузите фото шага
                        </span>
                    </label>
                </div>
                <textarea
                    name="step_descriptions[]"
                    class="step-description-textarea"
                    placeholder="Описание шага..."
                    rows="3"
                    required>
                </textarea>
            </div>
            <button type="button"
                    class="step-delete-btn"
                    title="Удалить шаг">
                ×
            </button>
        `;
        stepsContainer.appendChild(stepBlock);
    });

    // Удаление шага
    stepsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('step-delete-btn')) {
            const steps = stepsContainer.querySelectorAll('.step-block');
            // Минимум 1 шаг
            if (steps.length > 1) {
                event.target.closest('.step-block').remove();
                updateStepNumbers();
            }
        }
    });

    // Обновление номеров шагов
    function updateStepNumbers() {
        const allSteps = stepsContainer.querySelectorAll('.step-block');
        allSteps.forEach((step, index) => {
            const numberPill = step.querySelector('.step-number-pill');
            numberPill.textContent = `Шаг ${index + 1}`;
        });
    }
});