"""
================================================================
  SPINASSI CHOCOLATES — Criador do banco de dados
  Executa este arquivo UMA VEZ para criar todas as tabelas
  e inserir os dados iniciais.

  Uso:
      pip install pymysql cryptography werkzeug
      python criar_banco.py
================================================================
"""

import sys
import pymysql
from datetime import datetime

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    print("❌  Instale as dependências primeiro:")
    print("    pip install pymysql cryptography werkzeug")
    sys.exit(1)

# ── Configuração da conexão ──────────────────────────────────
DB = {
    "host":     "easypanel.pontocomdesconto.com.br",
    "port":     4066,
    "user":     "mysql",
    "password": "a66f389982ce9a59eeaf",
    "database": "chocolate",
    "charset":  "utf8mb4",
    "connect_timeout": 15,
}

# ── Credenciais do administrador padrão ─────────────────────
ADMIN_NOME      = "Administrador"
ADMIN_SOBRENOME = "Spinassi"
ADMIN_EMAIL     = "admin@spinassichocolates.com"
ADMIN_SENHA     = "Admin@Spinassi2024"   # ← TROQUE APÓS O 1º LOGIN


# ================================================================
#  DEFINIÇÃO DAS TABELAS (ordem respeita as FK)
# ================================================================

TABELAS = {}

# ── 01. Usuários ─────────────────────────────────────────────
TABELAS["usuarios"] = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    nome          VARCHAR(80)      NOT NULL,
    sobrenome     VARCHAR(80)      NOT NULL,
    email         VARCHAR(150)     NOT NULL,
    senha_hash    VARCHAR(512)     NOT NULL,
    telefone      VARCHAR(20)      DEFAULT NULL,
    cpf           VARCHAR(14)      DEFAULT NULL,
    genero        ENUM('M','F','NB','ND') DEFAULT NULL,
    tipo          ENUM('admin','cliente') NOT NULL DEFAULT 'cliente',
    ativo         TINYINT(1)       NOT NULL DEFAULT 1,
    aceita_news   TINYINT(1)       NOT NULL DEFAULT 0,
    avatar_url    VARCHAR(500)     DEFAULT NULL,
    criado_em     DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_email (email),
    UNIQUE KEY uq_cpf   (cpf),
    INDEX idx_tipo  (tipo),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 02. Recuperação de senha ─────────────────────────────────
TABELAS["recuperacao_senha"] = """
CREATE TABLE IF NOT EXISTS recuperacao_senha (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED NOT NULL,
    token       VARCHAR(128) NOT NULL,
    expira_em   DATETIME     NOT NULL,
    usado       TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_token (token),
    INDEX idx_usuario (usuario_id),
    CONSTRAINT fk_rec_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 03. Endereços ────────────────────────────────────────────
TABELAS["enderecos"] = """
CREATE TABLE IF NOT EXISTS enderecos (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id    INT UNSIGNED NOT NULL,
    apelido       VARCHAR(50)  NOT NULL DEFAULT 'Casa',
    cep           VARCHAR(9)   NOT NULL,
    logradouro    VARCHAR(200) NOT NULL,
    numero        VARCHAR(20)  NOT NULL,
    complemento   VARCHAR(100) DEFAULT NULL,
    bairro        VARCHAR(100) NOT NULL,
    cidade        VARCHAR(100) NOT NULL,
    estado        CHAR(2)      NOT NULL,
    padrao        TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_usuario (usuario_id),
    CONSTRAINT fk_end_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 04. Categorias ───────────────────────────────────────────
TABELAS["categorias"] = """
CREATE TABLE IF NOT EXISTS categorias (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome        VARCHAR(80)  NOT NULL,
    slug        VARCHAR(100) NOT NULL,
    descricao   TEXT         DEFAULT NULL,
    imagem_url  VARCHAR(500) DEFAULT NULL,
    ativa       TINYINT(1)   NOT NULL DEFAULT 1,
    ordem       INT UNSIGNED NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_slug (slug),
    INDEX idx_ativa (ativa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 05. Produtos ─────────────────────────────────────────────
TABELAS["produtos"] = """
CREATE TABLE IF NOT EXISTS produtos (
    id                  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    categoria_id        INT UNSIGNED  DEFAULT NULL,
    nome                VARCHAR(150)  NOT NULL,
    slug                VARCHAR(200)  NOT NULL,
    descricao           TEXT          DEFAULT NULL,
    descricao_curta     VARCHAR(300)  DEFAULT NULL,
    preco               DECIMAL(10,2) NOT NULL,
    preco_promocional   DECIMAL(10,2) DEFAULT NULL,
    estoque             INT           NOT NULL DEFAULT 0,
    imagem_principal    VARCHAR(500)  DEFAULT NULL,
    badge               VARCHAR(50)   DEFAULT NULL,
    peso_gramas         INT UNSIGNED  DEFAULT NULL,
    ativo               TINYINT(1)    NOT NULL DEFAULT 1,
    destaque            TINYINT(1)    NOT NULL DEFAULT 0,
    criado_em           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_slug (slug),
    INDEX idx_categoria (categoria_id),
    INDEX idx_ativo     (ativo),
    INDEX idx_destaque  (destaque),
    CONSTRAINT fk_prod_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 06. Sabores / Variações dos produtos ─────────────────────
# Cada produto pode ter N sabores. Cada sabor tem seu próprio
# estoque, preço adicional opcional e peso específico.
TABELAS["produto_sabores"] = """
CREATE TABLE IF NOT EXISTS produto_sabores (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    produto_id      INT UNSIGNED  NOT NULL,
    nome            VARCHAR(100)  NOT NULL,
    descricao       VARCHAR(300)  DEFAULT NULL,
    preco_adicional DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estoque         INT           NOT NULL DEFAULT 0,
    peso_gramas     INT UNSIGNED  DEFAULT NULL,
    ativo           TINYINT(1)    NOT NULL DEFAULT 1,
    ordem           INT UNSIGNED  NOT NULL DEFAULT 0,
    criado_em       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_produto (produto_id),
    INDEX idx_ativo   (ativo),
    CONSTRAINT fk_sab_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 07. Imagens adicionais dos produtos ──────────────────────
TABELAS["produto_imagens"] = """
CREATE TABLE IF NOT EXISTS produto_imagens (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    produto_id  INT UNSIGNED NOT NULL,
    url         VARCHAR(500) NOT NULL,
    alt_text    VARCHAR(200) DEFAULT NULL,
    ordem       INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX idx_produto (produto_id),
    CONSTRAINT fk_img_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 08. Cupons de desconto ───────────────────────────────────
TABELAS["cupons"] = """
CREATE TABLE IF NOT EXISTS cupons (
    id                    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    codigo                VARCHAR(30)   NOT NULL,
    descricao             VARCHAR(200)  DEFAULT NULL,
    tipo                  ENUM('percentual','fixo') NOT NULL DEFAULT 'percentual',
    valor                 DECIMAL(10,2) NOT NULL,
    valor_minimo_pedido   DECIMAL(10,2) DEFAULT NULL,
    limite_uso            INT UNSIGNED  DEFAULT NULL,
    total_usado           INT UNSIGNED  NOT NULL DEFAULT 0,
    ativo                 TINYINT(1)    NOT NULL DEFAULT 1,
    valido_de             DATETIME      DEFAULT NULL,
    valido_ate            DATETIME      DEFAULT NULL,
    criado_em             DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_codigo (codigo),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 09. Pedidos ──────────────────────────────────────────────
TABELAS["pedidos"] = """
CREATE TABLE IF NOT EXISTS pedidos (
    id               INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    usuario_id       INT UNSIGNED    DEFAULT NULL,
    cupom_id         INT UNSIGNED    DEFAULT NULL,
    nome_cliente     VARCHAR(160)    NOT NULL,
    email_cliente    VARCHAR(150)    NOT NULL,
    telefone_cliente VARCHAR(20)     DEFAULT NULL,
    cep              VARCHAR(9)      DEFAULT NULL,
    logradouro       VARCHAR(200)    DEFAULT NULL,
    numero           VARCHAR(20)     DEFAULT NULL,
    complemento      VARCHAR(100)    DEFAULT NULL,
    bairro           VARCHAR(100)    DEFAULT NULL,
    cidade           VARCHAR(100)    DEFAULT NULL,
    estado           CHAR(2)         DEFAULT NULL,
    subtotal         DECIMAL(10,2)   NOT NULL,
    desconto         DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    frete            DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    total            DECIMAL(10,2)   NOT NULL,
    forma_pagamento  ENUM('cartao_credito','cartao_debito',
                         'pix','boleto','whatsapp')
                     NOT NULL DEFAULT 'whatsapp',
    status_pagamento ENUM('pendente','aprovado','recusado','estornado')
                     NOT NULL DEFAULT 'pendente',
    status           ENUM('aguardando_pagamento','confirmado',
                         'em_separacao','enviado','entregue','cancelado')
                     NOT NULL DEFAULT 'aguardando_pagamento',
    observacao       TEXT            DEFAULT NULL,
    rastreamento     VARCHAR(50)     DEFAULT NULL,
    criado_em        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_status  (status),
    INDEX idx_criado  (criado_em),
    CONSTRAINT fk_ped_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    CONSTRAINT fk_ped_cupom
        FOREIGN KEY (cupom_id) REFERENCES cupons(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 10. Itens dos pedidos ────────────────────────────────────
# Guarda snapshot do produto + sabor no momento da compra
TABELAS["pedido_itens"] = """
CREATE TABLE IF NOT EXISTS pedido_itens (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    pedido_id       INT UNSIGNED  NOT NULL,
    produto_id      INT UNSIGNED  DEFAULT NULL,
    sabor_id        INT UNSIGNED  DEFAULT NULL,
    nome_produto    VARCHAR(150)  NOT NULL,
    nome_sabor      VARCHAR(100)  DEFAULT NULL,
    peso_gramas     INT UNSIGNED  DEFAULT NULL,
    preco_unit      DECIMAL(10,2) NOT NULL,
    quantidade      INT UNSIGNED  NOT NULL DEFAULT 1,
    subtotal        DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_pedido  (pedido_id),
    INDEX idx_produto (produto_id),
    CONSTRAINT fk_item_pedido
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_item_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL,
    CONSTRAINT fk_item_sabor
        FOREIGN KEY (sabor_id) REFERENCES produto_sabores(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 11. Lista de desejos ─────────────────────────────────────
TABELAS["lista_desejos"] = """
CREATE TABLE IF NOT EXISTS lista_desejos (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED NOT NULL,
    produto_id  INT UNSIGNED NOT NULL,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuario_produto (usuario_id, produto_id),
    CONSTRAINT fk_wish_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_wish_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 12. Avaliações ───────────────────────────────────────────
TABELAS["avaliacoes"] = """
CREATE TABLE IF NOT EXISTS avaliacoes (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    produto_id  INT UNSIGNED NOT NULL,
    usuario_id  INT UNSIGNED DEFAULT NULL,
    nome        VARCHAR(80)  DEFAULT NULL,
    nota        TINYINT      NOT NULL,
    comentario  TEXT         DEFAULT NULL,
    aprovada    TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_produto  (produto_id),
    INDEX idx_aprovada (aprovada),
    CONSTRAINT chk_nota CHECK (nota BETWEEN 1 AND 5),
    CONSTRAINT fk_av_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
    CONSTRAINT fk_av_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 13. Contatos (formulário do site) ────────────────────────
TABELAS["contatos"] = """
CREATE TABLE IF NOT EXISTS contatos (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome        VARCHAR(120) NOT NULL,
    email       VARCHAR(150) NOT NULL,
    telefone    VARCHAR(20)  DEFAULT NULL,
    mensagem    TEXT         NOT NULL,
    lida        TINYINT(1)   NOT NULL DEFAULT 0,
    respondida  TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_lida (lida)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 14. Configurações gerais do site ─────────────────────────
TABELAS["configuracoes"] = """
CREATE TABLE IF NOT EXISTS configuracoes (
    chave     VARCHAR(80)  NOT NULL,
    valor     TEXT         DEFAULT NULL,
    descricao VARCHAR(200) DEFAULT NULL,
    PRIMARY KEY (chave)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# ── 15. Log de atividades ────────────────────────────────────
TABELAS["log_atividades", "despesas"] = """
CREATE TABLE IF NOT EXISTS log_atividades (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id  INT UNSIGNED DEFAULT NULL,
    acao        VARCHAR(100) NOT NULL,
    descricao   TEXT         DEFAULT NULL,
    ip          VARCHAR(45)  DEFAULT NULL,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_criado  (criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


TABELAS["despesas"] = """
CREATE TABLE IF NOT EXISTS despesas (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    descricao    VARCHAR(200)   NOT NULL,
    categoria    ENUM('ingredientes','embalagem','marketing','aluguel','funcionarios',
                      'equipamentos','impostos','logistica','outros')
                 NOT NULL DEFAULT 'outros',
    valor        DECIMAL(10,2)  NOT NULL,
    data_despesa DATE           NOT NULL DEFAULT (CURDATE()),
    observacao   TEXT,
    criado_em    DATETIME       DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""




TABELAS["despesas"] = """
CREATE TABLE IF NOT EXISTS despesas (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    descricao    VARCHAR(200)   NOT NULL,
    categoria    ENUM('ingredientes','embalagem','marketing','aluguel','funcionarios',
                      'equipamentos','impostos','logistica','outros')
                 NOT NULL DEFAULT 'outros',
    valor        DECIMAL(10,2)  NOT NULL,
    data_despesa DATE           NOT NULL DEFAULT (CURDATE()),
    observacao   TEXT,
    criado_em    DATETIME       DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""



# ================================================================
#  DADOS INICIAIS
# ================================================================

def inserir_dados_iniciais(cur):
    """Insere categorias, produtos, sabores, cupom e configurações."""

    # ── Admin ────────────────────────────────────────────────
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (ADMIN_EMAIL,))
    if not cur.fetchone():
        hash_senha = generate_password_hash(ADMIN_SENHA)
        cur.execute(
            """INSERT INTO usuarios
               (nome, sobrenome, email, senha_hash, tipo, ativo)
               VALUES (%s, %s, %s, %s, 'admin', 1)""",
            (ADMIN_NOME, ADMIN_SOBRENOME, ADMIN_EMAIL, hash_senha)
        )
        print("  ✔  Admin criado")
    else:
        print("  –  Admin já existe, pulando")

    # ── Categorias ───────────────────────────────────────────
    categorias = [
        ("Trufas",    "trufas",    1),
        ("Barras",    "barras",    2),
        ("Bombons",   "bombons",   3),
        ("Kits",      "kits",      4),
        ("Presentes", "presentes", 5),
    ]
    for nome, slug, ordem in categorias:
        cur.execute("SELECT id FROM categorias WHERE slug = %s", (slug,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO categorias (nome, slug, ordem) VALUES (%s, %s, %s)",
                (nome, slug, ordem)
            )
    print("  ✔  Categorias inseridas")

    # ── IDs das categorias ───────────────────────────────────
    cur.execute("SELECT id, slug FROM categorias")
    cat_map = {row["slug"]: row["id"] for row in cur.fetchall()}

    # ── Produtos ─────────────────────────────────────────────
    produtos = [
        # (cat_slug, nome, slug, descricao_curta, preco, imagem, badge, peso_g, estoque, destaque)
        ("trufas",
         "Trufa Belga Premium",
         "trufa-belga-premium",
         "Trufas artesanais com cacau 70% e ganache de champagne",
         89.90,
         "https://images.unsplash.com/photo-1548907040-4baa42d10919?w=600",
         "Bestseller", 200, 50, 1),

        ("barras",
         "Barra Ouro Negro",
         "barra-ouro-negro",
         "Chocolate amargo 85% com nibs de cacau torrado",
         45.90,
         "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=600",
         "Novo", 100, 80, 1),

        ("bombons",
         "Bombons Sortidos Luxo",
         "bombons-sortidos-luxo",
         "Caixa com 12 bombons de sabores exclusivos",
         129.90,
         "https://images.unsplash.com/photo-1606312619070-d48b4f0c1b2d?w=600",
         "Premium", 300, 40, 1),

        ("barras",
         "Chocolate ao Leite Artesanal",
         "chocolate-ao-leite-artesanal",
         "Chocolate ao leite 45% com caramelo salgado",
         42.90,
         "https://images.unsplash.com/photo-1511381939415-e44015466834?w=600",
         None, 100, 60, 0),

        ("trufas",
         "Trufas de Pistache",
         "trufas-de-pistache",
         "Trufas cremosas com pistache siciliano",
         95.90,
         "https://images.unsplash.com/photo-1579372786545-d24232daf58c?w=600",
         "Exclusivo", 200, 30, 1),

        ("kits",
         "Caixa Degustação",
         "caixa-degustacao",
         "Kit degustação com 6 tipos de chocolates",
         159.90,
         "https://images.unsplash.com/photo-1481391243133-f96216dcb5d2?w=600",
         "Gift", 500, 25, 1),
    ]

    prod_ids = {}   # slug → id
    for (cat_slug, nome, slug, desc, preco, img, badge, peso, estoque, destaque) in produtos:
        cur.execute("SELECT id FROM produtos WHERE slug = %s", (slug,))
        row = cur.fetchone()
        if row:
            prod_ids[slug] = row["id"]
            continue
        cur.execute(
            """INSERT INTO produtos
               (categoria_id, nome, slug, descricao_curta, preco,
                imagem_principal, badge, peso_gramas, estoque, ativo, destaque)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)""",
            (cat_map.get(cat_slug), nome, slug, desc, preco,
             img, badge, peso, estoque, destaque)
        )
        prod_ids[slug] = cur.lastrowid
    print("  ✔  Produtos inseridos")

    # ── Sabores por produto ──────────────────────────────────
    # (produto_slug, nome_sabor, descricao, preco_adicional, peso_g, estoque, ordem)
    sabores = [
        # Trufa Belga Premium
        ("trufa-belga-premium", "Tradicional",
         "Ganache de champagne puro", 0.00, 200, 20, 1),
        ("trufa-belga-premium", "Maracujá",
         "Ganache de champagne com maracujá fresco", 5.00, 200, 15, 2),
        ("trufa-belga-premium", "Framboesa",
         "Ganache com coulis de framboesa belga", 5.00, 200, 15, 3),
        ("trufa-belga-premium", "Café Especial",
         "Ganache com espresso extraído a frio", 5.00, 200, 10, 4),

        # Barra Ouro Negro
        ("barra-ouro-negro", "Puro 85%",
         "Amargo intenso sem adição", 0.00, 100, 30, 1),
        ("barra-ouro-negro", "Com Sal Rosa",
         "Amargo com flor de sal rosa do Himalaia", 3.00, 100, 25, 2),
        ("barra-ouro-negro", "Com Nibs de Cacau",
         "Amargo com nibs de cacau torrado e crocante", 3.00, 100, 20, 3),
        ("barra-ouro-negro", "Com Pimenta Rosa",
         "Amargo com toque de pimenta rosa moída", 5.00, 100, 10, 4),

        # Bombons Sortidos Luxo
        ("bombons-sortidos-luxo", "Coleção Clássica",
         "Brigadeiro, beijinho, caramelo e pistache", 0.00, 300, 15, 1),
        ("bombons-sortidos-luxo", "Coleção Frutas Tropicais",
         "Maracujá, manga, abacaxi e coco", 10.00, 300, 12, 2),
        ("bombons-sortidos-luxo", "Coleção Nozes",
         "Castanha, avelã, amêndoa e pistache", 15.00, 300, 10, 3),
        ("bombons-sortidos-luxo", "Coleção Premium",
         "Trufas belgas, licor e especiarias raras", 20.00, 300, 8, 4),

        # Chocolate ao Leite Artesanal
        ("chocolate-ao-leite-artesanal", "Caramelo Salgado",
         "Ao leite 45% com caramelo e sal marinho", 0.00, 100, 25, 1),
        ("chocolate-ao-leite-artesanal", "Avelã Inteira",
         "Ao leite 45% com avelãs inteiras tostadas", 4.00, 100, 20, 2),
        ("chocolate-ao-leite-artesanal", "Cookies & Cream",
         "Ao leite 45% com pedaços de biscoito recheado", 4.00, 100, 18, 3),
        ("chocolate-ao-leite-artesanal", "Morango Liofilizado",
         "Ao leite 45% com morangos liofilizados crocantes", 6.00, 100, 12, 4),

        # Trufas de Pistache
        ("trufas-de-pistache", "Pistache Puro",
         "Ganache de pistache siciliano 100%", 0.00, 200, 12, 1),
        ("trufas-de-pistache", "Pistache & Limão Siciliano",
         "Pistache com raspas de limão siciliano", 5.00, 200, 10, 2),
        ("trufas-de-pistache", "Pistache & Rosas",
         "Pistache com água de rosas turca", 8.00, 200, 8, 3),

        # Caixa Degustação
        ("caixa-degustacao", "Clássica (6 sabores)",
         "Trufa, barra, bombom, ao leite, amargo e branco", 0.00, 500, 10, 1),
        ("caixa-degustacao", "Gourmet (8 sabores)",
         "Os 6 clássicos mais pistache e champagne", 30.00, 700, 8, 2),
        ("caixa-degustacao", "Premium (12 sabores)",
         "Seleção completa com embalagem presente exclusiva", 60.00, 1000, 5, 3),
    ]

    for (prod_slug, nome_sab, desc_sab, preco_adic, peso_g, estoque_s, ordem) in sabores:
        pid = prod_ids.get(prod_slug)
        if not pid:
            continue
        cur.execute(
            "SELECT id FROM produto_sabores WHERE produto_id=%s AND nome=%s",
            (pid, nome_sab)
        )
        if cur.fetchone():
            continue
        cur.execute(
            """INSERT INTO produto_sabores
               (produto_id, nome, descricao, preco_adicional,
                peso_gramas, estoque, ativo, ordem)
               VALUES (%s,%s,%s,%s,%s,%s,1,%s)""",
            (pid, nome_sab, desc_sab, preco_adic, peso_g, estoque_s, ordem)
        )
    print("  ✔  Sabores inseridos")

    # ── Cupom de boas-vindas ─────────────────────────────────
    cur.execute("SELECT id FROM cupons WHERE codigo = 'BEM-VINDO10'")
    if not cur.fetchone():
        cur.execute(
            """INSERT INTO cupons
               (codigo, descricao, tipo, valor, valor_minimo_pedido,
                limite_uso, ativo, valido_ate)
               VALUES (%s,%s,%s,%s,%s,%s,%s, DATE_ADD(NOW(), INTERVAL 1 YEAR))""",
            ("BEM-VINDO10",
             "10% de desconto para novos clientes",
             "percentual", 10.00, 50.00, 1000, 1)
        )
        print("  ✔  Cupom BEM-VINDO10 criado")

    # ── Configurações gerais ─────────────────────────────────
    configs = [
        ("nome_loja",          "Spinassi Chocolates",          "Nome da loja"),
        ("whatsapp",           "5583999999999",                "Número WhatsApp para pedidos"),
        ("email_loja",         "contato@spinassichocolates.com","E-mail principal"),
        ("frete_gratis_acima", "150.00",                       "Valor mínimo para frete grátis (R$)"),
        ("frete_padrao",       "15.00",                        "Valor padrão do frete (R$)"),
        ("instagram",          "",                             "Link do Instagram"),
        ("facebook",           "",                             "Link do Facebook"),
        ("metodo_pagamento",   "whatsapp,pix,cartao,boleto",   "Métodos ativos"),
    ]
    for chave, valor, desc in configs:
        cur.execute(
            """INSERT INTO configuracoes (chave, valor, descricao)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE valor = VALUES(valor)""",
            (chave, valor, desc)
        )
    print("  ✔  Configurações salvas")


# ================================================================
#  EXECUÇÃO PRINCIPAL
# ================================================================

def separador(char="─", largura=60):
    print(char * largura)


def main():
    separador("═")
    print("  🍫  SPINASSI CHOCOLATES — Criador do Banco de Dados")
    separador("═")
    print(f"  Host : {DB['host']}:{DB['port']}")
    print(f"  Banco: {DB['database']}")
    separador()

    # ── Conecta ──────────────────────────────────────────────
    print("\n[1/4] Conectando ao banco de dados...")
    try:
        conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
        print("  ✔  Conexão estabelecida!")
    except pymysql.Error as e:
        print(f"  ❌  Falha na conexão: {e}")
        sys.exit(1)

    cur = conn.cursor()

    try:
        cur.execute("SET NAMES utf8mb4")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")

        # ── Cria tabelas ─────────────────────────────────────
        print(f"\n[2/4] Criando {len(TABELAS)} tabelas...")
        for nome_tab, sql in TABELAS.items():
            try:
                cur.execute(sql.strip())
                conn.commit()
                print(f"  ✔  {nome_tab}")
            except pymysql.Error as e:
                print(f"  ❌  {nome_tab}: {e}")
                raise

        # ── Insere dados iniciais ─────────────────────────────
        print("\n[3/4] Inserindo dados iniciais...")
        inserir_dados_iniciais(cur)
        conn.commit()

        # ── Reativa FK ───────────────────────────────────────
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        # ── Resumo final ─────────────────────────────────────
        print("\n[4/4] Verificando resultado...")
        separador()

        tabelas_check = [
            "usuarios", "recuperacao_senha", "enderecos",
            "categorias", "produtos", "produto_sabores",
            "produto_imagens", "cupons", "pedidos",
            "pedido_itens", "lista_desejos", "avaliacoes",
            "contatos", "configuracoes", "log_atividades", "despesas",
        ]

        for t in tabelas_check:
            cur.execute(f"SELECT COUNT(*) AS n FROM {t}")
            n = cur.fetchone()["n"]
            print(f"  {'✔' if n >= 0 else '❌'}  {t:<25} {n:>4} registro(s)")

        separador("═")
        print("\n  ✅  BANCO DE DADOS PRONTO!\n")
        print(f"  Admin : {ADMIN_EMAIL}")
        print(f"  Senha : {ADMIN_SENHA}")
        print(f"\n  ⚠   TROQUE A SENHA DO ADMIN APÓS O PRIMEIRO LOGIN!")
        separador("═")

    except Exception as e:
        conn.rollback()
        print(f"\n  ❌  Erro durante a execução: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()