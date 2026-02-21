/* =========================================================
   sidebar.js — Spinassi Chocolates
   Sidebar dinâmica compartilhada por todas as páginas de conta.
   Admin vê seções extras; clientes comuns não têm acesso.

   Uso em cada página:
     <aside class="acc-sidebar" id="sidebarMount"></aside>
     <script src="../assets/js/sidebar.js"></script>
     <script> renderSidebar('minha-conta'); </script>
========================================================= */

(function (global) {
    'use strict';

    /* ── Ícones SVG reutilizáveis ─────────────────────────── */
    const ICONS = {
        user:     `<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>`,
        orders:   `<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>`,
        heart:    `<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>`,
        lock:     `<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>`,
        logout:   `<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>`,
        payment:  `<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>`,
        product:  `<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>`,
        finance:  `<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>`,
        star:     `<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>`,
    };

    function svg(paths) {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${paths}</svg>`;
    }

    function navItem(href, iconKey, label, activePage, pageId, badge) {
        const isActive = activePage === pageId;
        const badgeHtml = badge != null
            ? `<span class="acc-count-badge" id="badge-${pageId}" style="display:none">${badge}</span>`
            : '';
        if (href === '#scroll-senha') {
            return `<button class="acc-nav-item${isActive?' active':''}" onclick="document.querySelector('#secSenha')?.scrollIntoView({behavior:'smooth'})">
                        ${svg(ICONS[iconKey])}${label}${badgeHtml}
                    </button>`;
        }
        return `<a href="${href}" class="acc-nav-item${isActive?' active':''}">
                    ${svg(ICONS[iconKey])}${label}${badgeHtml}
                </a>`;
    }

    /* ── Renderizador principal ───────────────────────────── */
    global.renderSidebar = function (activePage) {

        /* Guarda de sessão */
        if (!SpinassiAPI.sessao.estaLogado() || SpinassiAPI.sessao.tokenExpirado()) {
            SpinassiAPI.sessao.limpar();
            window.location.href = 'index.html';
            return;
        }

        const u       = SpinassiAPI.sessao.getUsuario();
        const nome    = `${u.nome || ''} ${u.sobrenome || ''}`.trim();
        const inicial = (u.nome || '?').charAt(0).toUpperCase();
        const isAdmin = u.tipo === 'admin';

        /* ── Seção cliente ─────────────────────────────────── */
        const secCliente = `
            <span class="acc-nav-label">Minha conta</span>
            ${navItem('minha-conta.html',  'user',    'Meus Dados',        activePage, 'minha-conta')}
            ${navItem('meus-pedidos.html', 'orders',  'Meus Pedidos',      activePage, 'meus-pedidos', '')}
            ${navItem('lista-desejos.html','heart',   'Lista de Desejos',  activePage, 'lista-desejos', '')}
            <span class="acc-nav-label">Segurança</span>
            ${navItem('#scroll-senha',     'lock',    'Alterar Senha',     activePage, 'senha')}
        `;

        /* ── Seção admin (só para admins) ─────────────────── */
        const secAdmin = isAdmin ? `
            <span class="acc-nav-label acc-nav-label--admin">Administração</span>
            ${navItem('admin-produtos.html',    'product', 'Produtos',               activePage, 'admin-produtos')}
            ${navItem('gestao-financeira.html', 'finance', 'Gestão Financeira',      activePage, 'gestao-financeira')}
            ${navItem('config-pagamento.html',  'payment', 'Configurar Pagamento',   activePage, 'config-pagamento')}
        ` : '';

        /* ── Logout ────────────────────────────────────────── */
        const secLogout = `
            <span class="acc-nav-label">Sessão</span>
            <button class="acc-nav-item logout-item" onclick="fazerLogout()">
                ${svg(ICONS.logout)} Sair
            </button>
        `;

        /* ── Monta HTML completo ───────────────────────────── */
        const html = `
            <div class="acc-sidebar-user">
                <div class="acc-avatar-big" id="sidebarAvatar">${inicial}</div>
                <div class="acc-sidebar-name">${nome}</div>
                <div class="acc-sidebar-email">${u.email || ''}</div>
                ${isAdmin ? `<span class="sidebar-admin-tag">${svg(ICONS.star)} Admin</span>` : ''}
            </div>
            ${secCliente}
            ${secAdmin}
            ${secLogout}
        `;

        const mount = document.getElementById('sidebarMount');
        if (mount) mount.innerHTML = html;
    };

    /* ── Logout global ────────────────────────────────────── */
    global.fazerLogout = function () {
        SpinassiAPI.auth.logout();
        window.location.href = 'index.html';
    };

})(window);