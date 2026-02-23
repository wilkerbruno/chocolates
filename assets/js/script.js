// Produtos — carregados dinamicamente do banco de dados
let produtos = [];

async function carregarProdutos() {
    const grid = document.getElementById('produtosGrid');
    if (!grid) return;

    // Skeleton loading
    grid.innerHTML = Array(6).fill(0).map(() => `
        <div class="produto-card" style="pointer-events:none">
            <div class="produto-image" style="background:#f0ece4;height:350px;animation:shimmer 1.4s infinite linear;
                 background:linear-gradient(90deg,#f0ece4 25%,#e8e3da 50%,#f0ece4 75%);
                 background-size:600px 100%"></div>
            <div class="produto-info" style="padding:30px">
                <div style="height:12px;background:#eee;border-radius:4px;width:60%;margin-bottom:12px;
                     animation:shimmer 1.4s infinite linear;background:linear-gradient(90deg,#eee 25%,#e3e3e3 50%,#eee 75%);background-size:600px 100%"></div>
                <div style="height:20px;background:#eee;border-radius:4px;width:85%;margin-bottom:10px;
                     animation:shimmer 1.4s infinite linear;background:linear-gradient(90deg,#eee 25%,#e3e3e3 50%,#eee 75%);background-size:600px 100%"></div>
                <div style="height:14px;background:#eee;border-radius:4px;width:100%;margin-bottom:6px;
                     animation:shimmer 1.4s infinite linear;background:linear-gradient(90deg,#eee 25%,#e3e3e3 50%,#eee 75%);background-size:600px 100%"></div>
            </div>
        </div>`).join('');

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

        produtos = lista;
        await carregarDesejos(); // garante desejos antes de renderizar
        renderProdutos();

        // Mostra/esconde botão "Ver mais"
        const btnVerMais = document.getElementById('btnVerMaisProdutos');
        if (btnVerMais) btnVerMais.style.display = 'inline-block';

    } catch(e) {
        grid.innerHTML = '<p style="text-align:center;color:#888;padding:40px">Não foi possível carregar os produtos.</p>';
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
        const res = await SpinassiAPI.desejos.listar();
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
            await SpinassiAPI.desejos.remover(id);
            desejosSet.delete(id);
            showNotification('Removido dos favoritos.');
        } else {
            await SpinassiAPI.desejos.adicionar(id);
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
    updateCartCount();
    setupEventListeners();
    setupScrollEffects();
    carregarProdutos(); // busca produtos do banco + desejos
});

// Renderizar produtos
function renderProdutos() {
    const grid = document.getElementById('produtosGrid');
    grid.innerHTML = produtos.map(produto => `
        <div class="produto-card" data-id="${produto.id}">
            <div class="produto-image">
                <img src="${produto.imagem}" alt="${produto.nome}">
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
    
    // Checkout — redireciona para página de pagamento
    document.getElementById('checkoutBtn').addEventListener('click', () => {
        if (carrinho.length === 0) {
            showNotification('Adicione produtos ao carrinho primeiro!', 'error');
            return;
        }

        // Salva o carrinho (já está no localStorage) e vai para pagamento
        saveCart();

        // Fecha o modal do carrinho antes de redirecionar
        document.getElementById('cartModal').classList.remove('active');

        // Pequeno delay para o modal fechar suavemente
        setTimeout(() => {
            window.location.href = 'pagamento.html';
        }, 250);
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