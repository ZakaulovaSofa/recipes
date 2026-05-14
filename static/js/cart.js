/* jshint esversion: 6, strict: global */
document.addEventListener('DOMContentLoaded', () => {
    buildCartTotal();

    function buildCartTotal() {
        const totalCard = document.getElementById('cart-total-card');

        if (!totalCard) {
            return;
        }

        const ingredientRows = document.querySelectorAll('.cart-ingredient-row');
        const totals = {};

        ingredientRows.forEach((row) => {
            const name = row.dataset.name || '';
            const unit = row.dataset.unit || '';
            const amount = parseFloat(row.dataset.amount);

            if (!name || Number.isNaN(amount)) {
                return;
            }

            const key = `${name.trim().toLowerCase()}__${unit.trim().toLowerCase()}`;

            if (!totals[key]) {
                totals[key] = {
                    name: name.trim(),
                    unit: unit.trim(),
                    amount: 0
                };
            }

            totals[key].amount += amount;
        });

        totalCard.innerHTML = '';

        Object.keys(totals).forEach((key) => {
            const item = totals[key];
            const formattedAmount = formatAmount(item.amount);
            const storageKey = `cart_checked_${key}`;
            const isChecked = localStorage.getItem(storageKey) === 'true';

            const row = document.createElement('div');
            row.classList.add('total-row');

            row.innerHTML = `
                <div class="total-name-pill">${item.name}</div>
                <div class="total-amount-pill">${formattedAmount} ${item.unit}</div>

                <label class="total-checkbox-wrapper">
                    <input type="checkbox" 
                           class="total-checkbox-input"
                           data-storage-key="${storageKey}"
                           ${isChecked ? 'checked' : ''}>
                    <div class="total-checkbox" role="presentation"></div>
                </label>
            `;

            totalCard.appendChild(row);
        });

        const checkboxes = totalCard.querySelectorAll('.total-checkbox-input');

        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener('change', () => {
                const storageKey = checkbox.dataset.storageKey;

                if (!storageKey) {
                    return;
                }

                localStorage.setItem(storageKey, checkbox.checked ? 'true' : 'false');
            });
        });
    }

    function formatAmount(value) {
        if (Number.isInteger(value)) {
            return String(value);
        }

        return String(Math.round(value * 100) / 100);
    }

    // SERVINGS CONTROL
    const servingsControls = document.querySelectorAll('.servings-control');

    servingsControls.forEach((control) => {
        if (control.dataset.initialized === 'true') {
            return;
        }

        control.dataset.initialized = 'true';

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
});