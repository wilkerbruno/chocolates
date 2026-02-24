// Produtos fixos — exibidos imediatamente enquanto a API carrega (ou se ela falhar)
const PRODUTOS_FIXOS = [
    {
        id: 1,
        nome: 'Trufa Belga Premium',
        categoria: 'Trufas',
        descricao: 'Trufas artesanais com cacau 70% e ganache de champagne',
        preco: 89.90,
        imagem: 'https://images.unsplash.com/photo-1548907040-4baa42d10919?w=600',
        badge: 'Bestseller'
    },
    {
        id: 2,
        nome: 'Barra Ouro Negro',
        categoria: 'Barras',
        descricao: 'Chocolate amargo 85% com nibs de cacau torrado',
        preco: 45.90,
        imagem: 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=600',
        badge: 'Novo'
    },
    {
        id: 3,
        nome: 'Bombons Sortidos Luxo',
        categoria: 'Bombons',
        descricao: 'Caixa com 12 bombons de sabores exclusivos',
        preco: 129.90,
        imagem: 'https://images.unsplash.com/photo-1606312619070-d48b4f0c1b2d?w=600',
        badge: 'Premium'
    },
    {
        id: 4,
        nome: 'Chocolate ao Leite Artesanal',
        categoria: 'Barras',
        descricao: 'Chocolate ao leite 45% com caramelo salgado',
        preco: 42.90,
        imagem: 'https://images.unsplash.com/photo-1511381939415-e44015466834?w=600',
        badge: ''
    },
    {
        id: 5,
        nome: 'Trufas de Pistache',
        categoria: 'Trufas',
        descricao: 'Trufas cremosas com pistache siciliano',
        preco: 95.90,
        imagem: 'https://images.unsplash.com/photo-1579372786545-d24232daf58c?w=600',
        badge: 'Exclusivo'
    },
    {
        id: 6,
        nome: 'Caixa Degustação',
        categoria: 'Kits',
        descricao: 'Kit degustação com 6 tipos de chocolates',
        preco: 159.90,
        imagem: 'https://images.unsplash.com/photo-1481391243133-f96216dcb5d2?w=600',
        badge: 'Gift'
    }
];

// Produtos — preenchido pelo banco ou pelo array fixo acima
let produtos = [];

async function carregarProdutos() {
    const grid = document.getElementById('produtosGrid');
    if (!grid) return;

    // Mostra os produtos fixos imediatamente — página nunca fica vazia
    produtos = PRODUTOS_FIXOS;
    renderProdutos();

    // Tenta substituir pelos produtos reais do banco em segundo plano
    try {
        const res = await fetch('/api/produtos?limite=6&destaque=1');
        const json = await res.json();
        let lista = json.data || [];

        // Se não houver produtos em destaque, busca os 6 mais recentes
        if (!lista.length) {
            const res2 = await fetch('/api/produtos?limite=6');
            const j2   = await res2.json();
            lista = j2.data || [];
        }

        // Só substitui se o banco retornar algo
        if (lista.length) {
            produtos = lista;
            await carregarDesejos();
            renderProdutos();
        }

        // Mostra botão "Ver mais"
        const btnVerMais = document.getElementById('btnVerMaisProdutos');
        if (btnVerMais) btnVerMais.style.display = 'inline-block';

    } catch(e) {
        // API indisponível — os produtos fixos já estão visíveis, não faz nada
    }
}


// Carrinho
let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

// Lista de desejos — IDs dos produtos favoritados pelo usuário logado
let desejosSet = new Set();

/* Carrega IDs de desejos do usuário logado */
async function carregarDesejos() {
    if (!window.SpinassiAPI?.sessao?.getToken()) return;
    try {
        const res = await window.SpinassiAPI.desejos.listar();
        desejosSet = new Set((res.data || []).map(d => d.id));
        // Atualiza ícones que já estão na tela
        document.querySelectorAll('.btn-desejo').forEach(btn => {
            const id = parseInt(btn.dataset.id);
            btn.classList.toggle('ativo', desejosSet.has(id));
            btn.title = desejosSet.has(id) ? 'Remover dos favoritos' : 'Salvar nos favoritos';
        });
    } catch (_) {}
}

/* Alterna favorito */
async function toggleDesejo(id, btn) {
    if (!window.SpinassiAPI?.sessao?.getToken()) {
        showNotification('Faça login para salvar favoritos!', 'error');
        return;
    }
    const ativo = desejosSet.has(id);
    // Feedback visual imediato
    btn.classList.toggle('ativo', !ativo);
    try {
        if (ativo) {
            await window.SpinassiAPI.desejos.remover(id);
            desejosSet.delete(id);
            showNotification('Removido dos favoritos.');
        } else {
            await window.SpinassiAPI.desejos.adicionar(id);
            desejosSet.add(id);
            showNotification('Salvo nos favoritos! ❤️');
        }
        btn.title = desejosSet.has(id) ? 'Remover dos favoritos' : 'Salvar nos favoritos';
    } catch (e) {
        // Reverte o visual se falhar
        btn.classList.toggle('ativo', ativo);
        showNotification('Erro ao atualizar favoritos.', 'error');
    }
}

// Inicializar página
document.addEventListener('DOMContentLoaded', () => {
    carregarProdutos();
    setupEventListeners();
    setupScrollEffects();
    updateCartCount();
});

// Retrocompatibilidade com páginas que ainda usam template.js
window.addEventListener('templateCarregado', () => {
    setupEventListeners();
    setupScrollEffects();
    updateCartCount();
});


// Renderizar produtos
function renderProdutos() {
    const grid = document.getElementById('produtosGrid');
    grid.innerHTML = produtos.map(produto => `
        <div class="produto-card" data-id="${produto.id}">
            <div class="produto-image">
                <img src="${produto.imagem_principal || produto.imagem || ''}"
                     alt="${produto.nome}"
                     onerror="this.src='https://images.unsplash.com/photo-1548907040-4baa42d10919?w=600';this.onerror=null;">
                ${produto.badge ? `<span class="produto-badge">${produto.badge}</span>` : ''}
                <button class="btn-desejo ${desejosSet.has(produto.id) ? 'ativo' : ''}"
                        data-id="${produto.id}"
                        title="${desejosSet.has(produto.id) ? 'Remover dos favoritos' : 'Salvar nos favoritos'}"
                        onclick="toggleDesejo(${produto.id}, this); event.stopPropagation();">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06
                                 a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78
                                 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                </button>
            </div>
            <div class="produto-info">
                <div class="produto-categoria">${produto.categoria}</div>
                <h3 class="produto-nome">${produto.nome}</h3>
                <p class="produto-descricao">${produto.descricao}</p>
                <div class="produto-footer">
                    <span class="produto-preco">R$ ${produto.preco.toFixed(2).replace('.', ',')}</span>
                    <button class="btn-add-cart" onclick="addToCart(${produto.id})">
                        <span class="texto-dourado">Adicionar</span>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Adicionar ao carrinho
function addToCart(produtoId) {
    const produto = produtos.find(p => p.id === produtoId);
    const itemExistente = carrinho.find(item => item.id === produtoId);
    
    if (itemExistente) {
        itemExistente.quantidade++;
    } else {
        carrinho.push({
            ...produto,
            quantidade: 1
        });
    }
    
    saveCart();
    updateCartCount();
    showNotification('Produto adicionado ao carrinho!');
}

// Remover do carrinho
function removeFromCart(produtoId) {
    carrinho = carrinho.filter(item => item.id !== produtoId);
    saveCart();
    updateCartCount();
    renderCart();
}

// Atualizar quantidade
function updateQuantity(produtoId, delta) {
    const item = carrinho.find(item => item.id === produtoId);
    if (item) {
        item.quantidade += delta;
        if (item.quantidade <= 0) {
            removeFromCart(produtoId);
        } else {
            saveCart();
            renderCart();
        }
    }
}

// Salvar carrinho
function saveCart() {
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
}

// Atualizar contador do carrinho
function updateCartCount() {
    const count = carrinho.reduce((total, item) => total + item.quantidade, 0);
    const el = document.getElementById('cartCount');
    if (el) el.textContent = count;
}

// Renderizar carrinho
function renderCart() {
    const cartItems = document.getElementById('cartItems');
    
    if (carrinho.length === 0) {
        cartItems.innerHTML = `
            <div class="cart-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="9" cy="21" r="1"></circle>
                    <circle cx="20" cy="21" r="1"></circle>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
                <p>Seu carrinho está vazio</p>
            </div>
        `;
        document.getElementById('cartTotal').textContent = 'R$ 0,00';
        return;
    }
    
    cartItems.innerHTML = carrinho.map(item => `
        <div class="cart-item">
            <img src="${item.imagem}" alt="${item.nome}" class="cart-item-image">
            <div class="cart-item-info">
                <h4 class="cart-item-name">${item.nome}</h4>
                <p class="cart-item-price">R$ ${item.preco.toFixed(2).replace('.', ',')}</p>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">−</button>
                    <span class="cart-item-qty">${item.quantidade}</span>
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                    <button class="remove-item" onclick="removeFromCart(${item.id})">Remover</button>
                </div>
            </div>
        </div>
    `).join('');
    
    const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
    document.getElementById('cartTotal').textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
}

// Setup event listeners
// Setup event listeners
function setupEventListeners() {

    // ── Carrinho: aguarda template.js injetar o header (fetch assíncrono) ──
    function bindCart() {
        const cartBtn     = document.getElementById('cartBtn');
        const closeCart   = document.getElementById('closeCart');
        const cartModal   = document.getElementById('cartModal');
        const checkoutBtn = document.getElementById('checkoutBtn');

        if (cartBtn && cartModal) {
            cartBtn.addEventListener('click', () => {
                cartModal.classList.add('active');
                renderCart();
            });
        }
        if (closeCart && cartModal) {
            closeCart.addEventListener('click', () => cartModal.classList.remove('active'));
        }
        if (cartModal) {
            cartModal.addEventListener('click', (e) => {
                if (e.target.id === 'cartModal') cartModal.classList.remove('active');
            });
        }
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                if (carrinho.length === 0) {
                    showNotification('Adicione produtos ao carrinho primeiro!', 'error');
                    return;
                }
                saveCart();
                if (cartModal) cartModal.classList.remove('active');
                setTimeout(() => { window.location.href = 'pagamento.html'; }, 250);
            });
        }
    }

    // Tenta vincular imediatamente; se o header ainda não foi injetado,
    // aguarda o evento templateCarregado do template.js
    if (document.getElementById('cartBtn')) {
        bindCart();
    } else {
        window.addEventListener('templateCarregado', bindCart);
    }

    // ── Formulário de contato ──────────────────────────────────────────────
    const contatoForm = document.getElementById('contatoForm');
    if (contatoForm) {
        contatoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(e.target));
            try {
                const response = await fetch('/api/contato', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    showFormMessage('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
                    e.target.reset();
                } else {
                    showFormMessage('Erro ao enviar mensagem. Tente novamente.', 'error');
                }
            } catch (error) {
                showFormMessage('Erro ao enviar mensagem. Tente novamente.', 'error');
            }
        });
    }

    // ── Navegação suave ────────────────────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
                if (this.classList.contains('nav-link')) this.classList.add('active');
            }
        });
    });
}

// Criar mensagem do pedido
function criarMensagemPedido() {
    let mensagem = '*Novo Pedido - Chocolaterie Noir*\n\n';
    
    carrinho.forEach(item => {
        mensagem += `*${item.quantidade}x ${item.nome}*\n`;
        mensagem += `R$ ${(item.preco * item.quantidade).toFixed(2).replace('.', ',')}\n\n`;
    });
    
    const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
    mensagem += `*Total: R$ ${total.toFixed(2).replace('.', ',')}*`;
    
    return mensagem;
}

// Mostrar notificação
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#2ECC71' : '#E74C3C'};
        color: white;
        padding: 20px 30px;
        border-radius: 0;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Mostrar mensagem do formulário
function showFormMessage(message, type) {
    const messageEl = document.getElementById('formMessage');
    messageEl.textContent = message;
    messageEl.className = `form-message ${type}`;
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

// Efeitos de scroll
function setupScrollEffects() {
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.style.padding = '15px 0';
            header.style.background = 'rgba(62, 39, 35, 0.98)';
        } else {
            header.style.padding = '20px 0';
            header.style.background = 'linear-gradient(180deg, rgba(62, 39, 35, 0.95) 0%, rgba(62, 39, 35, 0.85) 100%)';
        }
    });
    
    // Intersection Observer para animações
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.produto-card, .stat, .detail-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Animações CSS adicionais
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);