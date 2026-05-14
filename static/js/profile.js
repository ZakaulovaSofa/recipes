// LOGOUT MODAL
document.addEventListener('DOMContentLoaded', () => {
    const logoutForm = document.getElementById('logout-form');
    const openLogoutModalBtn = document.getElementById('open-logout-modal');
    const logoutModalOverlay = document.getElementById('logout-modal-overlay');
    const cancelLogoutBtn = document.getElementById('cancel-logout');
    const confirmLogoutBtn = document.getElementById('confirm-logout');

    if (
        logoutForm &&
        openLogoutModalBtn &&
        logoutModalOverlay &&
        cancelLogoutBtn &&
        confirmLogoutBtn
    ) {
        openLogoutModalBtn.addEventListener('click', () => {
            logoutModalOverlay.classList.add('logout-modal-overlay-active');
        });

        cancelLogoutBtn.addEventListener('click', () => {
            logoutModalOverlay.classList.remove('logout-modal-overlay-active');
        });

        logoutModalOverlay.addEventListener('click', (event) => {
            if (event.target === logoutModalOverlay) {
                logoutModalOverlay.classList.remove('logout-modal-overlay-active');
            }
        });

        confirmLogoutBtn.addEventListener('click', () => {
            logoutForm.submit();
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                logoutModalOverlay.classList.remove('logout-modal-overlay-active');
            }
        });
    }
});