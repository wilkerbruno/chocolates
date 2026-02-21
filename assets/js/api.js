/* =========================================================
   api.js — Spinassi Chocolates
   Módulo central de comunicação com o backend Flask.
   Gerencia token JWT, sessão e expõe helpers de fetch.

   Inclua ANTES de login.js e outros scripts:
   <script src="assets/js/api.js"></script>
========================================================= */

(function (global) {
    'use strict';

    /* -------------------------------------------------------
       CONFIGURAÇÃO
    ------------------------------------------------------- */
    // Ajuste se o backend rodar em porta diferente
    const API_BASE = '';   // vazio = mesmo host/porta do Flask
                            // Em dev separado use 'http://localhost:5000'

    const TOKEN_KEY = 'sc_token';   // localStorage
    const USER_KEY  = 'sc_user';    // localStorage

    /* -------------------------------------------------------
       TOKEN HELPERS
    ------------------------------------------------------- */
    function salvarSessao(token, usuario) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(usuario));
    }

    function limparSessao() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    function getToken() {
        return localStorage.getItem(TOKEN_KEY) || null;
    }

    function getUsuario() {
        try {
            return JSON.parse(localStorage.getItem(USER_KEY));
        } catch (_) {
            return null;
        }
    }

    function estaLogado() {
        return !!getToken();
    }

    /* Decodifica o payload do JWT (sem verificar assinatura — só para UI) */
    function tokenExpirado() {
        const token = getToken();
        if (!token) return true;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return Date.now() / 1000 > payload.exp;
        } catch (_) {
            return true;
        }
    }

    /* -------------------------------------------------------
       FETCH HELPER
       Todas as chamadas passam por aqui.
    ------------------------------------------------------- */
    async function request(method, path, body = null, autenticado = false) {
        const headers = { 'Content-Type': 'application/json' };

        if (autenticado) {
            if (tokenExpirado()) {
                limparSessao();
                throw new Error('Sessão expirada. Faça login novamente.');
            }
            headers['Authorization'] = `Bearer ${getToken()}`;
        }

        const opts = { method, headers };
        if (body !== null) opts.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE}${path}`, opts);
        const json = await res.json().catch(() => ({ success: false, message: 'Resposta inválida do servidor.' }));

        if (!res.ok) {
            throw new Error(json.message || `Erro ${res.status}`);
        }

        return json;   // { success, message, data? }
    }

    /* Atalhos */
    const api = {
        get:    (path, auth = false)        => request('GET',    path, null, auth),
        post:   (path, body, auth = false)  => request('POST',   path, body, auth),
        put:    (path, body, auth = false)  => request('PUT',    path, body, auth),
        patch:  (path, body, auth = false)  => request('PATCH',  path, body, auth),
        delete: (path, auth = false)        => request('DELETE', path, null, auth),
    };

    /* -------------------------------------------------------
       AUTH ENDPOINTS
    ------------------------------------------------------- */
    api.auth = {
        /** Cadastra novo usuário */
        async cadastro(dados) {
            const res = await api.post('/api/auth/cadastro', dados);
            if (res.data?.token) {
                salvarSessao(res.data.token, {
                    nome:      dados.nome,
                    sobrenome: dados.sobrenome,
                    email:     dados.email,
                    tipo:      res.data.tipo || 'cliente',
                });
            }
            return res;
        },

        /** Faz login e salva sessão */
        async login(email, senha) {
            const res = await api.post('/api/auth/login', { email, senha });
            if (res.data?.token) {
                salvarSessao(res.data.token, {
                    nome:      res.data.nome,
                    sobrenome: res.data.sobrenome,
                    email,
                    tipo:      res.data.tipo,
                });
            }
            return res;
        },

        /** Solicita e-mail de recuperação de senha */
        recuperarSenha: (email) =>
            api.post('/api/auth/recuperar-senha', { email }),

        /** Redefine senha com token do e-mail */
        redefinirSenha: (token, nova_senha) =>
            api.post('/api/auth/redefinir-senha', { token, nova_senha }),

        /** Retorna dados do perfil logado */
        perfil: () => api.get('/api/auth/perfil', true),

        /** Atualiza perfil */
        atualizarPerfil: (dados) => api.put('/api/auth/perfil', dados, true),

        /** Altera senha */
        alterarSenha: (senha_atual, nova_senha) =>
            api.post('/api/auth/alterar-senha', { senha_atual, nova_senha }, true),

        /** Desloga localmente (JWT é stateless — apenas limpa localStorage) */
        logout() {
            limparSessao();
        },
    };

    /* -------------------------------------------------------
       OUTROS ENDPOINTS
    ------------------------------------------------------- */
    api.produtos = {
        listar: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return api.get(`/api/produtos${qs ? '?' + qs : ''}`);
        },
        detalhe: (id) => api.get(`/api/produtos/${id}`),
    };

    api.pedidos = {
        criar:   (dados) => api.post('/api/pedidos', dados, true),
        listar:  ()      => api.get('/api/pedidos', true),
        detalhe: (id)    => api.get(`/api/pedidos/${id}`, true),
    };

    api.desejos = {
        listar:   ()    => api.get('/api/desejos', true),
        adicionar: (id) => api.post(`/api/desejos/${id}`, {}, true),
        remover:   (id) => api.delete(`/api/desejos/${id}`, true),
    };

    api.cupons = {
        validar: (codigo, total) =>
            api.post('/api/cupons/validar', { codigo, total }),
    };

    /* -------------------------------------------------------
       HELPERS DE SESSÃO (expostos globalmente)
    ------------------------------------------------------- */
    api.sessao = {
        salvar:    salvarSessao,
        limpar:    limparSessao,
        getToken,
        getUsuario,
        estaLogado,
        tokenExpirado,
    };

    /* -------------------------------------------------------
       EXPÕE GLOBALMENTE
    ------------------------------------------------------- */
    global.SpinassiAPI = api;

})(window);