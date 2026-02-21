/* =========================================================
   login.js — Spinassi Chocolates
   Lógica do dropdown de login no header
========================================================= */

(function () {
    'use strict';

    /* -------------------------------------------------------
       ELEMENTOS
    ------------------------------------------------------- */
    const btn       = document.getElementById('loginBtn');
    const dropdown  = document.getElementById('loginDropdown');
    const backdrop  = document.getElementById('loginBackdrop');
    const form      = document.getElementById('loginForm');
    const passInput = document.getElementById('loginPassword');
    const eyeIcon   = document.getElementById('eyeIcon');

    if (!btn || !dropdown) return;

    /* -------------------------------------------------------
       ABRIR / FECHAR
    ------------------------------------------------------- */
    function openLogin() {
        dropdown.classList.add('open');
        backdrop.classList.add('active');
        btn.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
        // Foca o primeiro campo após a animação
        setTimeout(() => {
            const first = dropdown.querySelector('input');
            if (first) first.focus();
        }, 260);
    }

    function closeLogin() {
        dropdown.classList.remove('open');
        backdrop.classList.remove('active');
        btn.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
    }

    function toggleLogin() {
        if (dropdown.classList.contains('open')) closeLogin();
        else openLogin();
    }

    /* Expõe closeLogin globalmente (usada no onclick do backdrop no HTML) */
    window.closeLogin = closeLogin;

    /* -------------------------------------------------------
       EVENTOS
    ------------------------------------------------------- */
    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        toggleLogin();
    });

    backdrop.addEventListener('click', closeLogin);

    // Fecha com ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeLogin();
    });

    // Impede que cliques dentro do dropdown fechem
    dropdown.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    /* -------------------------------------------------------
       TOGGLE VISIBILIDADE DE SENHA
    ------------------------------------------------------- */
    window.togglePassword = function () {
        const isPass = passInput.type === 'password';
        passInput.type = isPass ? 'text' : 'password';

        // Troca o ícone: olho aberto / olho fechado
        eyeIcon.innerHTML = isPass
            ? /* olho fechado */
              `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
               <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
               <line x1="1" y1="1" x2="23" y2="23"/>`
            : /* olho aberto */
              `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
               <circle cx="12" cy="12" r="3"/>`;
    };

    /* -------------------------------------------------------
       SUBMIT DO FORMULÁRIO (simulação)
    ------------------------------------------------------- */
    window.submitLogin = function (e) {
        e.preventDefault();

        const email    = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        // Remove alertas anteriores
        const existingAlert = form.querySelector('.login-alert');
        if (existingAlert) existingAlert.remove();

        // Validação básica
        if (!email || !password) {
            showLoginAlert('Preencha todos os campos.', 'error');
            return;
        }

        // Estado de loading no botão
        const submitBtn = form.querySelector('.btn-login-submit');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Entrando...';

        // Simulação de autenticação (substitua por fetch real)
        setTimeout(function () {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;

            // Simulação: aceita qualquer e-mail/senha preenchidos
            const firstName = email.split('@')[0];
            const displayName = firstName.charAt(0).toUpperCase() + firstName.slice(1);
            onLoginSuccess(displayName, email);
        }, 1200);
    };

    function showLoginAlert(msg, type) {
        const alert = document.createElement('div');
        alert.className = `login-alert ${type}`;
        alert.textContent = msg;
        form.insertBefore(alert, form.firstChild);
    }

    /* -------------------------------------------------------
       PÓS-LOGIN — atualiza UI do botão e dropdown
    ------------------------------------------------------- */
    function onLoginSuccess(name, email) {
        // Guarda sessão simples
        sessionStorage.setItem('sc_user', JSON.stringify({ name, email }));

        // Atualiza o botão
        btn.innerHTML = `
            <span class="user-avatar">${name.charAt(0)}</span>
            <span class="login-btn-label">${name}</span>
        `;
        btn.classList.add('logged-in');

        // Substitui o conteúdo do dropdown pelo menu pós-login
        const inner = dropdown.querySelector('.login-dropdown-inner');
        inner.innerHTML = `
            <div class="login-dropdown-header">
                <h3>Olá, ${name}!</h3>
                <p>${email}</p>
            </div>
            <nav class="logged-menu visible">
                <a href="#" class="logged-menu-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                    Minha Conta
                </a>
                <a href="#" class="logged-menu-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                    Meus Pedidos
                </a>
                <a href="#" class="logged-menu-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                    Lista de Desejos
                </a>
                <button class="logged-menu-item logout" onclick="logoutUser()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                        <polyline points="16 17 21 12 16 7"/>
                        <line x1="21" y1="12" x2="9" y2="12"/>
                    </svg>
                    Sair
                </button>
            </nav>
        `;

        // Fecha após pequeno delay para UX
        setTimeout(closeLogin, 400);
    }

    /* -------------------------------------------------------
       LOGOUT
    ------------------------------------------------------- */
    window.logoutUser = function () {
        sessionStorage.removeItem('sc_user');
        // Restaura botão original
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
            <span class="login-btn-label">Entrar</span>
        `;
        btn.classList.remove('logged-in');
        // Restaura dropdown original
        restoreLoginForm();
        closeLogin();
    };

    function restoreLoginForm() {
        const inner = dropdown.querySelector('.login-dropdown-inner');
        inner.innerHTML = `
            <div class="login-dropdown-header">
                <h3>Bem-vindo</h3>
                <p>Acesse sua conta Spinassi</p>
            </div>
            <form class="login-form" id="loginForm" onsubmit="submitLogin(event)">
                <div class="login-field">
                    <input type="email" id="loginEmail" placeholder=" " autocomplete="email" required>
                    <label for="loginEmail">E-mail</label>
                </div>
                <div class="login-field login-field--password">
                    <input type="password" id="loginPassword" placeholder=" " autocomplete="current-password" required>
                    <label for="loginPassword">Senha</label>
                    <button type="button" class="toggle-password" onclick="togglePassword()" aria-label="Mostrar senha">
                        <svg id="eyeIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                    </button>
                </div>
                <a href="recuperar-senha.html" class="forgot-link">Esqueci minha senha</a>
                <button type="submit" class="btn-login-submit">Entrar</button>
            </form>
            <div class="login-divider"><span>ou</span></div>
            <a href="cadastro.html" class="btn-register">Cadastre-se grátis</a>
            <p class="login-terms">
                Ao entrar você concorda com nossos
                <a href="#">Termos de Uso</a> e <a href="#">Privacidade</a>.
            </p>
        `;
    }

    /* -------------------------------------------------------
       RESTAURAR SESSÃO (ao recarregar a página)
    ------------------------------------------------------- */
    const saved = sessionStorage.getItem('sc_user');
    if (saved) {
        try {
            const { name, email } = JSON.parse(saved);
            onLoginSuccess(name, email);
        } catch (_) {
            sessionStorage.removeItem('sc_user');
        }
    }

})();