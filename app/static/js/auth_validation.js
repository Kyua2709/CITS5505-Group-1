// Handle login and register modal validation
// Reset modals on shown

document.addEventListener('DOMContentLoaded', function () {
    // RESET MODALS
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');

    if (loginModal) {
        loginModal.addEventListener('shown.bs.modal', () => {
            loginModal.querySelector('form').reset();
            const errorBox = document.getElementById('loginError');
            if (errorBox) {
                errorBox.innerHTML = '';
                errorBox.style.display = 'none';
            }
        });
    }

    if (registerModal) {
        registerModal.addEventListener('shown.bs.modal', () => {
            registerModal.querySelector('form').reset();
            const errorBox = document.getElementById('registerError');
            if (errorBox) {
                errorBox.innerHTML = '';
                errorBox.style.display = 'none';
            }
        });
    }

    // REGISTER VALIDATION
    const registerForm = registerModal?.querySelector('form');
    const registerError = document.getElementById('registerError');

    if (registerForm && registerError) {
        const passwordInput = document.getElementById('registerPassword');
        const confirmInput = document.getElementById('confirmPassword');
        const emailInput = document.getElementById('registerEmail');

        registerForm.addEventListener('submit', function (event) {
            let messages = [];
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            const confirmPassword = confirmInput.value;

            registerError.innerHTML = '';
            registerError.style.display = 'none';

            const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
            if (!emailPattern.test(email)) {
                messages.push("Please enter a valid email address.");
            }

            if (password.length < 6) {
                messages.push("Password must be at least 6 characters.");
            }

            if (password !== confirmPassword) {
                messages.push("Passwords do not match.");
            }

            if (messages.length > 0) {
                event.preventDefault();
                registerError.style.display = 'block';
                registerError.innerHTML = `
                    <div class="alert alert-danger mb-3">
                        ${messages.map(msg => `<div>${msg}</div>`).join('')}
                    </div>
                `;
            }
        });
    }

    // LOGIN VALIDATION
    const loginForm = loginModal?.querySelector('form');
    const loginError = document.getElementById('loginError');

});
