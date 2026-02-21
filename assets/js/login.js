/* =========================================================
   login.js — Spinassi Chocolates
   Dropdown de login no header com autenticação real via API.

   Dependência: assets/js/api.js  (deve ser carregado antes)
========================================================= */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        const btn      = document.getElementById('loginBtn');
        const dropdown = document.getElementById('loginDropdown');
        const backdrop = document.getElementById('loginBackdrop');

        if (!btn || !dropdown) return;

        /* ---------------------------------------------------
           ABRIR / FECHAR
        --------------------------------------------------- */
        function openLogin() {
            dropdown.classList.add('open');
            backdrop.classList.add('active');
            btn.classList.add('active');
            btn.setAttribute('aria-expanded', 'true');
            setTimeout(() => {
                const first = dropdown.querySelector('input:not([type="hidden"])');
                if (first) first.focus();
            }, 260);
        }

        function closeLogin() {
            dropdown.classList.remove('open');
            backdrop.classList.remove('active');
            btn.classList.remove('active');
            btn.setAttribute('aria-expanded', 'false');
        }

        window.closeLogin = closeLogin;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.contains('open') ? closeLogin() : openLogin();
        });

        backdrop.addEventListener('click', closeLogin);
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLogin(); });
        dropdown.addEventListener('click', (e) => e.stopPropagation());

        /* ---------------------------------------------------
           TOGGLE VISIBILIDADE DA SENHA
        --------------------------------------------------- */
        window.togglePassword = function () {
            const passInput = document.getElementById('loginPassword');
            const eyeIcon   = document.getElementById('eyeIcon');
            if (!passInput || !eyeIcon) return;
            const isPass = passInput.type === 'password';
            passInput.type = isPass ? 'text' : 'password';
            eyeIcon.innerHTML = isPass
                ? `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                   <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                   <line x1="1" y1="1" x2="23" y2="23"/>`
                : `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                   <circle cx="12" cy="12" r="3"/>`;
        };

        /* ---------------------------------------------------
           HELPERS DE UI
        --------------------------------------------------- */
        function setAlert(msg, tipo) {
            const form = document.getElementById('loginForm');
            if (!form) return;
            let el = form.querySelector('.login-alert');
            if (!el) {
                el = document.createElement('div');
                form.insertBefore(el, form.firstChild);
            }
            el.className = `login-alert ${tipo}`;
            el.textContent = msg;
        }

        function clearAlert() {
            const el = document.querySelector('#loginForm .login-alert');
            if (el) el.remove();
        }

        function setLoading(loading) {
            const submitBtn = document.querySelector('.btn-login-submit');
            if (!submitBtn) return;
            submitBtn.disabled = loading;
            submitBtn.textContent = loading ? 'Entrando…' : 'Entrar';
        }

        /* ---------------------------------------------------
           SUBMIT — LOGIN REAL COM A API
        --------------------------------------------------- */
        window.submitLogin = async function (e) {
            e.preventDefault();
            clearAlert();

            const email = (document.getElementById('loginEmail')?.value || '').trim().toLowerCase();
            const senha = document.getElementById('loginPassword')?.value || '';

            if (!email || !senha) {
                setAlert('Preencha e-mail e senha.', 'error');
                return;
            }

            setLoading(true);

            try {
                await SpinassiAPI.auth.login(email, senha);
                const usuario = SpinassiAPI.sessao.getUsuario();
                onLoginSuccess(usuario);
            } catch (err) {
                setLoading(false);
                setAlert(err.message || 'Erro ao fazer login. Tente novamente.', 'error');
            }
        };

        /* ---------------------------------------------------
           PÓS-LOGIN — atualiza botão e dropdown
        --------------------------------------------------- */
        function onLoginSuccess(usuario) {
            const nome        = usuario.nome  || usuario.email.split('@')[0];
            const inicial     = nome.charAt(0).toUpperCase();
            const email       = usuario.email;
            const tipo        = usuario.tipo;

            /* Atualiza botão do header */
            btn.innerHTML = `
                <span class="user-avatar">${inicial}</span>
                <span class="login-btn-label">${nome}</span>
            `;
            btn.classList.add('logged-in');

            /* Item exclusivo para admin */
            const itemAdmin = tipo === 'admin'
                ? `<a href="admin-produtos.html" class="logged-menu-item logged-menu-item--admin">
                       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                           <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                       </svg>
                       Painel Admin
                   </a>`
                : '';

            /* Monta menu pós-login */
            const inner = dropdown.querySelector('.login-dropdown-inner');
            if (!inner) return;
            inner.innerHTML = `
                <div class="login-dropdown-header">
                    <h3>Olá, ${nome}!</h3>
                    <p>${email}</p>
                </div>
                <nav class="logged-menu visible">
                    ${itemAdmin}
                    <a href="minha-conta.html" class="logged-menu-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                        </svg>
                        Minha Conta
                    </a>
                    <a href="meus-pedidos.html" class="logged-menu-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                        </svg>
                        Meus Pedidos
                    </a>
                    <a href="lista-desejos.html" class="logged-menu-item">
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

            setTimeout(closeLogin, 350);
        }

        /* ---------------------------------------------------
           LOGOUT
        --------------------------------------------------- */
        window.logoutUser = function () {
            SpinassiAPI.auth.logout();
            closeLogin();

            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
                <span class="login-btn-label">Entrar</span>
            `;
            btn.classList.remove('logged-in');
            renderFormLogin();
        };

        /* ---------------------------------------------------
           RENDERIZA O FORMULÁRIO (chamado no logout/restore)
        --------------------------------------------------- */
        function renderFormLogin() {
            const inner = dropdown.querySelector('.login-dropdown-inner');
            if (!inner) return;
            inner.innerHTML = `
                <div class="login-dropdown-header">
                    <h3>Bem-vindo</h3>
                    <p>Acesse sua conta Spinassi</p>
                </div>
                <form class="login-form" id="loginForm" onsubmit="submitLogin(event)">
                    <div class="login-field">
                        <input type="email" id="loginEmail" placeholder=" "
                               autocomplete="email" required>
                        <label for="loginEmail">E-mail</label>
                    </div>
                    <div class="login-field login-field--password">
                        <input type="password" id="loginPassword" placeholder=" "
                               autocomplete="current-password" required>
                        <label for="loginPassword">Senha</label>
                        <button type="button" class="toggle-password"
                                onclick="togglePassword()" aria-label="Mostrar senha">
                            <svg id="eyeIcon" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="2">
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

        /* ---------------------------------------------------
           RESTAURA SESSÃO AO RECARREGAR A PÁGINA
        --------------------------------------------------- */
        if (SpinassiAPI.sessao.estaLogado() && !SpinassiAPI.sessao.tokenExpirado()) {
            const u = SpinassiAPI.sessao.getUsuario();
            if (u) onLoginSuccess(u);
        } else {
            SpinassiAPI.sessao.limpar(); // remove sessão expirada
        }

    } // fim init()

    /* -------------------------------------------------------
       CSS extra para item admin
    ------------------------------------------------------- */
    const s = document.createElement('style');
    s.textContent = `
        .logged-menu-item--admin {
            background: linear-gradient(90deg,rgba(212,175,55,.14),rgba(212,175,55,.04));
            border-left: 3px solid #D4AF37;
            font-weight: 600;
        }
        .logged-menu-item--admin svg { color: #D4AF37 !important; }
    `;
    document.head.appendChild(s);

})();