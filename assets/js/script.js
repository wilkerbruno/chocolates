// Dados dos produtos
const produtos = [
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

// Carrinho
let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

// Inicializar página
document.addEventListener('DOMContentLoaded', () => {
    renderProdutos();
    updateCartCount();
    setupEventListeners();
    setupScrollEffects();
});

// Renderizar produtos
function renderProdutos() {
    const grid = document.getElementById('produtosGrid');
    grid.innerHTML = produtos.map(produto => `
        <div class="produto-card" data-id="${produto.id}">
            <div class="produto-image">
                <img src="${produto.imagem}" alt="${produto.nome}">
                ${produto.badge ? `<span class="produto-badge">${produto.badge}</span>` : ''}
            </div>
            <div class="produto-info">
                <div class="produto-categoria">${produto.categoria}</div>
                <h3 class="produto-nome">${produto.nome}</h3>
                <p class="produto-descricao">${produto.descricao}</p>
                <div class="produto-footer">
                    <span class="produto-preco">R$ ${produto.preco.toFixed(2).replace('.', ',')}</span>
                    <button class="btn-add-cart" onclick="addToCart(${produto.id})">
                        Adicionar
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
    document.getElementById('cartCount').textContent = count;
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
function setupEventListeners() {
    // Cart modal
    document.getElementById('cartBtn').addEventListener('click', () => {
        document.getElementById('cartModal').classList.add('active');
        renderCart();
    });
    
    document.getElementById('closeCart').addEventListener('click', () => {
        document.getElementById('cartModal').classList.remove('active');
    });
    
    document.getElementById('cartModal').addEventListener('click', (e) => {
        if (e.target.id === 'cartModal') {
            document.getElementById('cartModal').classList.remove('active');
        }
    });
    
    // Checkout
    document.getElementById('checkoutBtn').addEventListener('click', () => {
        if (carrinho.length === 0) {
            showNotification('Adicione produtos ao carrinho primeiro!', 'error');
            return;
        }
        
        const mensagem = criarMensagemPedido();
        const whatsappUrl = `https://wa.me/5583999999999?text=${encodeURIComponent(mensagem)}`;
        window.open(whatsappUrl, '_blank');
    });
    
    // Formulário de contato
    document.getElementById('contatoForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/contato', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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
    
    // Navegação suave
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Atualizar active link
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                if (this.classList.contains('nav-link')) {
                    this.classList.add('active');
                }
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