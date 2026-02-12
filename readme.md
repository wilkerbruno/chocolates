# 🍫 Chocolaterie Noir - Site de Vendas Premium

Site sofisticado e moderno para venda de chocolates artesanais com design luxuoso, carrinho de compras funcional e integração com WhatsApp.

## ✨ Características

### Design & Interface
- **Design Luxuoso**: Paleta de cores chocolate premium com detalhes em dourado
- **Tipografia Elegante**: Fontes Cormorant Garamond e Montserrat para um visual sofisticado
- **Animações Suaves**: Transições e efeitos que encantam o usuário
- **Vídeo Hero**: Vídeo de chocolate na página principal para impacto visual
- **Totalmente Responsivo**: Funciona perfeitamente em desktop, tablet e mobile

### Funcionalidades
- ✅ Catálogo de produtos dinâmico com fotos e descrições
- ✅ Carrinho de compras com localStorage (persiste entre sessões)
- ✅ Adicionar, remover e alterar quantidade de produtos
- ✅ Cálculo automático de totais
- ✅ Formulário de contato com envio de email
- ✅ Botão flutuante do WhatsApp integrado ao design
- ✅ Finalização de pedido via WhatsApp
- ✅ Navegação suave entre seções
- ✅ Sistema de notificações elegante

### Tecnologias
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Comunicação**: WhatsApp Business API
- **Email**: SMTP (Gmail)

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Navegador web moderno
- Conexão com internet (para fontes e vídeo)

## 🚀 Instalação

### 1. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 2. Configurar Email (Opcional)

Edite o arquivo `app.py` e configure suas credenciais de email:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'seu-email@gmail.com',
    'senha': 'sua-senha-app',
    'destinatario': 'contato@chocolaterienoir.com'
}
```

**Para usar Gmail:**
1. Ative a verificação em duas etapas
2. Crie uma "Senha de app" em: https://myaccount.google.com/apppasswords
3. Use essa senha no lugar da sua senha normal

### 3. Configurar WhatsApp

Edite os seguintes arquivos para adicionar seu número:

**index.html** (linha 16):
```html
<a href="https://wa.me/5583999999999?text=Olá!..." class="whatsapp-float">
```

**script.js** (linha 141):
```javascript
const whatsappUrl = `https://wa.me/5583999999999?text=${encodeURIComponent(mensagem)}`;
```

Substitua `5583999999999` pelo seu número no formato internacional (código do país + DDD + número).

## ▶️ Como Executar

### Método 1: Com Backend Python (Recomendado)

```bash
python app.py
```

Acesse: http://localhost:5000

### Método 2: Apenas Frontend (Para testes)

Abra o arquivo `index.html` diretamente no navegador.

**Nota**: O formulário de contato não funcionará sem o backend.

## 📁 Estrutura do Projeto

```
chocolaterie-noir/
│
├── index.html          # Página principal
├── style.css           # Estilos CSS
├── script.js           # JavaScript do frontend
├── app.py              # Servidor backend Flask
├── requirements.txt    # Dependências Python
├── README.md          # Este arquivo
│
└── logs/              # Pasta criada automaticamente
    ├── contatos.txt   # Log de mensagens de contato
    └── pedidos.txt    # Log de pedidos
```

## 🎨 Personalização

### Alterar Produtos

Edite o array `produtos` em `script.js`:

```javascript
const produtos = [
    {
        id: 1,
        nome: 'Trufa Belga Premium',
        categoria: 'Trufas',
        descricao: 'Descrição do produto',
        preco: 89.90,
        imagem: 'URL_DA_IMAGEM',
        badge: 'Bestseller'
    },
    // ... adicione mais produtos
];
```

### Alterar Cores

Edite as variáveis CSS em `style.css`:

```css
:root {
    --chocolate-dark: #3E2723;
    --chocolate-medium: #5D4037;
    --gold: #D4AF37;
    /* ... outras cores */
}
```

### Alterar Vídeo Hero

Em `index.html`, linha 42, substitua a URL do vídeo:

```html
<source src="SUA_URL_DE_VIDEO.mp4" type="video/mp4">
```

**Fontes de vídeos gratuitos:**
- Pixabay: https://pixabay.com/videos/
- Pexels: https://www.pexels.com/videos/

### Alterar Imagens dos Produtos

Use URLs de imagens de alta qualidade. Fontes recomendadas:
- Unsplash: https://unsplash.com/
- Pexels: https://www.pexels.com/

## 📱 Funcionalidades WhatsApp

### Botão Flutuante
- Sempre visível no canto inferior direito
- Cor integrada ao design do site (marrom chocolate)
- Animação de pulso para chamar atenção

### Finalização de Pedido
- Ao clicar em "Finalizar Pedido" no carrinho
- Abre WhatsApp com mensagem formatada
- Inclui todos os produtos e total do pedido

## 📧 Sistema de Contato

O formulário envia emails e salva logs localmente em `logs/contatos.txt`.

**Campos:**
- Nome (obrigatório)
- Email (obrigatório)
- Telefone (opcional)
- Mensagem (obrigatória)

## 🛒 Carrinho de Compras

### Funcionalidades:
- Adicionar produtos
- Alterar quantidade (+ / -)
- Remover itens
- Cálculo automático de total
- Persistência com localStorage
- Modal elegante

### Persistência:
O carrinho é salvo automaticamente no navegador e permanece mesmo após fechar a página.

## 🎯 Próximos Passos (Opcional)

Para tornar o site ainda mais completo:

1. **Banco de Dados**: Integrar MySQL/PostgreSQL para produtos
2. **Painel Admin**: Interface para gerenciar produtos
3. **Pagamento Online**: Integrar Stripe, PagSeguro ou Mercado Pago
4. **Sistema de Login**: Área de clientes com histórico
5. **Blog**: Seção de receitas e notícias
6. **Cupons de Desconto**: Sistema de promoções
7. **Avaliações**: Reviews de clientes

## 🐛 Troubleshooting

### O vídeo não carrega
- Verifique sua conexão com internet
- Tente usar um vídeo local em vez de URL externa

### Formulário não envia
- Verifique se o backend está rodando
- Confirme as configurações de email no `app.py`
- Verifique o console do navegador para erros

### Carrinho não salva
- Verifique se o JavaScript está habilitado
- Limpe o cache do navegador
- Verifique o console para erros

### WhatsApp não abre
- Verifique se o número está no formato correto
- Teste o link diretamente: `https://wa.me/5583999999999`

## 📄 Licença

Este projeto é livre para uso pessoal e comercial.

## 🤝 Suporte

Para dúvidas ou sugestões, entre em contato através do formulário no site ou via WhatsApp.

---

**Desenvolvido com ❤️ e muito 🍫 por Claude**

## 🎨 Preview das Cores

- **Chocolate Escuro**: #3E2723 ████
- **Chocolate Médio**: #5D4037 ████
- **Dourado**: #D4AF37 ████
- **Creme**: #FFF8E7 ████
- **Branco**: #FFFFFF ████

---

**Dica Final**: Para melhores resultados, use imagens de alta qualidade (mínimo 800x600px) e vídeos em HD. Isso fará toda a diferença na apresentação!

Boas vendas! 🍫✨