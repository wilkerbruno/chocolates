# ============================================================
#  SPINASSI CHOCOLATES — Backend Flask completo
#  Conecta ao MySQL e expõe todas as rotas da API
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps

# ── JWT opcional (instale: pip install PyJWT) ──────────────
try:
    import jwt
    JWT_DISPONIVEL = True
except ImportError:
    JWT_DISPONIVEL = False
    print("⚠ PyJWT não instalado. Autenticação via token desativada.")

# ============================================================
#  CONFIGURAÇÕES
# ============================================================

app = Flask(__name__, static_folder='.')
CORS(app, supports_credentials=True)

# ── Banco de dados ─────────────────────────────────────────
DB_CONFIG = {
    'host':     'easypanel.pontocomdesconto.com.br',
    'port':     4066,
    'user':     'mysql',
    'password': 'a66f389982ce9a59eeaf',
    'database': 'chocolate',
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 10,
    'autocommit': True,
}

# ── JWT ────────────────────────────────────────────────────
JWT_SECRET  = os.environ.get('JWT_SECRET', 'spinassi-secret-mude-em-producao-2024')
JWT_EXPIRES = 24  # horas

# ── E-mail ─────────────────────────────────────────────────
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port':   587,
    'email':       'seu-email@gmail.com',       # ← substitua
    'senha':       'sua-senha-de-app',          # ← substitua
    'destinatario':'contato@spinassichocolates.com',
}

# ============================================================
#  HELPERS DE BANCO
# ============================================================

def get_db():
    """Abre uma nova conexão com o banco."""
    return pymysql.connect(**DB_CONFIG)


def query(sql, params=None, fetch='all'):
    """
    Executa uma query e retorna os resultados.
    fetch = 'all' | 'one' | 'none'
    Retorna (resultado, lastrowid)
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch == 'all':
                return cur.fetchall(), cur.lastrowid
            if fetch == 'one':
                return cur.fetchone(), cur.lastrowid
            return None, cur.lastrowid
    finally:
        conn.close()


def ok(data=None, msg='ok', code=200):
    resp = {'success': True, 'message': msg}
    if data is not None:
        resp['data'] = data
    return jsonify(resp), code


def err(msg='Erro interno', code=400):
    return jsonify({'success': False, 'message': msg}), code

# ============================================================
#  HELPERS DE JWT
# ============================================================

def gerar_token(usuario_id, tipo):
    if not JWT_DISPONIVEL:
        return None
    payload = {
        'sub':  usuario_id,
        'tipo': tipo,
        'exp':  datetime.utcnow() + timedelta(hours=JWT_EXPIRES),
        'iat':  datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verificar_token(token):
    if not JWT_DISPONIVEL:
        return None
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def requer_login(f):
    """Decorator: rota só acessível com token válido."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return err('Token não fornecido', 401)
        payload = verificar_token(token)
        if not payload:
            return err('Token inválido ou expirado', 401)
        request.usuario_id   = payload['sub']
        request.usuario_tipo = payload['tipo']
        return f(*args, **kwargs)
    return decorated


def requer_admin(f):
    """Decorator: rota só acessível para administradores."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return err('Token não fornecido', 401)
        payload = verificar_token(token)
        if not payload:
            return err('Token inválido ou expirado', 401)
        if payload.get('tipo') != 'admin':
            return err('Acesso restrito a administradores', 403)
        request.usuario_id   = payload['sub']
        request.usuario_tipo = payload['tipo']
        return f(*args, **kwargs)
    return decorated

# ============================================================
#  HELPERS DE E-MAIL
# ============================================================

def enviar_email(destinatario, assunto, html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From']    = EMAIL_CONFIG['email']
        msg['To']      = destinatario
        msg.attach(MIMEText(html, 'html'))
        srv = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        srv.starttls()
        srv.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['senha'])
        srv.send_message(msg)
        srv.quit()
        return True
    except Exception as e:
        print(f'[EMAIL] Erro: {e}')
        return False


def log(usuario_id, acao, descricao='', ip=None):
    try:
        query(
            "INSERT INTO log_atividades (usuario_id, acao, descricao, ip) VALUES (%s,%s,%s,%s)",
            (usuario_id, acao, descricao, ip), fetch='none'
        )
    except Exception:
        pass

# ============================================================
#  ARQUIVOS ESTÁTICOS
# ============================================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# ============================================================
#  STATUS
# ============================================================

@app.route('/api/status')
def status():
    try:
        conn = get_db()
        conn.ping(reconnect=True)
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False
    return ok({'db': db_ok, 'horario': datetime.now().strftime('%d/%m/%Y %H:%M:%S')},
              'Spinassi API online')

# ============================================================
#  AUTH — CADASTRO
# ============================================================

@app.route('/api/auth/cadastro', methods=['POST'])
def cadastro():
    d = request.get_json() or {}
    nome      = (d.get('nome')      or '').strip()
    sobrenome = (d.get('sobrenome') or '').strip()
    email     = (d.get('email')     or '').strip().lower()
    senha     = d.get('senha', '')
    telefone  = (d.get('telefone')  or '').strip() or None
    cpf       = (d.get('cpf')       or '').strip() or None
    genero    = d.get('genero') or None
    news      = 1 if d.get('aceita_news') else 0

    if not nome or not sobrenome or not email or not senha:
        return err('Preencha todos os campos obrigatórios')
    if len(senha) < 8:
        return err('A senha deve ter ao menos 8 caracteres')

    existe, _ = query("SELECT id FROM usuarios WHERE email=%s", (email,), fetch='one')
    if existe:
        return err('Este e-mail já está cadastrado')

    hash_senha = generate_password_hash(senha)
    _, novo_id = query(
        """INSERT INTO usuarios
           (nome, sobrenome, email, senha_hash, telefone, cpf, genero, aceita_news)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (nome, sobrenome, email, hash_senha, telefone, cpf, genero, news),
        fetch='none'
    )
    log(novo_id, 'cadastro', f'Novo usuário: {email}')
    token = gerar_token(novo_id, 'cliente')
    return ok({'token': token, 'tipo': 'cliente', 'nome': nome},
              'Conta criada com sucesso!', 201)

# ============================================================
#  AUTH — LOGIN
# ============================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    d     = request.get_json() or {}
    email = (d.get('email') or '').strip().lower()
    senha = d.get('senha', '')

    if not email or not senha:
        return err('Informe e-mail e senha')

    user, _ = query(
        "SELECT id, nome, sobrenome, senha_hash, tipo, ativo FROM usuarios WHERE email=%s",
        (email,), fetch='one'
    )
    if not user:
        return err('E-mail ou senha incorretos', 401)
    if not user['ativo']:
        return err('Conta desativada. Entre em contato com o suporte.', 403)
    if not check_password_hash(user['senha_hash'], senha):
        return err('E-mail ou senha incorretos', 401)

    token = gerar_token(user['id'], user['tipo'])
    log(user['id'], 'login', f'Login via API — IP: {request.remote_addr}')
    return ok({
        'token':     token,
        'tipo':      user['tipo'],
        'nome':      user['nome'],
        'sobrenome': user['sobrenome'],
    }, 'Login realizado com sucesso!')

# ============================================================
#  AUTH — RECUPERAÇÃO DE SENHA
# ============================================================

@app.route('/api/auth/recuperar-senha', methods=['POST'])
def recuperar_senha():
    d     = request.get_json() or {}
    email = (d.get('email') or '').strip().lower()
    if not email:
        return err('Informe o e-mail')

    user, _ = query("SELECT id, nome FROM usuarios WHERE email=%s AND ativo=1",
                    (email,), fetch='one')
    # Retorna ok mesmo se não existir (não expõe se o e-mail está cadastrado)
    if not user:
        return ok(msg='Se este e-mail estiver cadastrado, você receberá as instruções.')

    # Gera token seguro de 64 chars
    token = secrets.token_urlsafe(48)
    expira = datetime.now() + timedelta(hours=2)
    query(
        "INSERT INTO recuperacao_senha (usuario_id, token, expira_em) VALUES (%s,%s,%s)",
        (user['id'], token, expira), fetch='none'
    )

    link = f"https://seusite.com.br/recuperar-senha.html?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:30px;background:#fff8e7;">
        <h2 style="color:#3E2723;border-bottom:3px solid #D4AF37;padding-bottom:10px;">
            Spinassi Chocolates — Recuperação de Senha
        </h2>
        <p>Olá, <strong>{user['nome']}</strong>!</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
        <p style="margin:30px 0;">
            <a href="{link}"
               style="background:#D4AF37;color:#3E2723;padding:14px 32px;
                      text-decoration:none;font-weight:bold;font-size:16px;">
                Redefinir minha senha
            </a>
        </p>
        <p style="color:#999;font-size:12px;">
            Este link é válido por 2 horas. Se você não solicitou, ignore este e-mail.
        </p>
    </div>"""
    enviar_email(email, 'Spinassi Chocolates — Redefinição de senha', html)
    return ok(msg='Se este e-mail estiver cadastrado, você receberá as instruções.')


@app.route('/api/auth/redefinir-senha', methods=['POST'])
def redefinir_senha():
    d         = request.get_json() or {}
    token     = d.get('token', '')
    nova_senha = d.get('nova_senha', '')

    if not token or not nova_senha:
        return err('Dados incompletos')
    if len(nova_senha) < 8:
        return err('A senha deve ter ao menos 8 caracteres')

    rec, _ = query(
        """SELECT r.id, r.usuario_id FROM recuperacao_senha r
           WHERE r.token=%s AND r.usado=0 AND r.expira_em > NOW()""",
        (token,), fetch='one'
    )
    if not rec:
        return err('Link inválido ou expirado. Solicite um novo.', 400)

    hash_nova = generate_password_hash(nova_senha)
    query("UPDATE usuarios SET senha_hash=%s WHERE id=%s",
          (hash_nova, rec['usuario_id']), fetch='none')
    query("UPDATE recuperacao_senha SET usado=1 WHERE id=%s",
          (rec['id'],), fetch='none')
    log(rec['usuario_id'], 'redefinir_senha')
    return ok(msg='Senha redefinida com sucesso!')

# ============================================================
#  AUTH — PERFIL DO USUÁRIO LOGADO
# ============================================================

@app.route('/api/auth/perfil', methods=['GET'])
@requer_login
def perfil():
    user, _ = query(
        """SELECT id, nome, sobrenome, email, telefone, cpf, genero,
                  tipo, aceita_news, avatar_url, criado_em
           FROM usuarios WHERE id=%s""",
        (request.usuario_id,), fetch='one'
    )
    if not user:
        return err('Usuário não encontrado', 404)
    user['criado_em'] = str(user['criado_em'])
    return ok(user)


@app.route('/api/auth/perfil', methods=['PUT'])
@requer_login
def atualizar_perfil():
    d         = request.get_json() or {}
    nome      = (d.get('nome')      or '').strip()
    sobrenome = (d.get('sobrenome') or '').strip()
    telefone  = (d.get('telefone')  or '').strip() or None
    genero    = d.get('genero') or None
    news      = 1 if d.get('aceita_news') else 0

    if not nome or not sobrenome:
        return err('Nome e sobrenome são obrigatórios')

    query(
        """UPDATE usuarios
           SET nome=%s, sobrenome=%s, telefone=%s, genero=%s, aceita_news=%s
           WHERE id=%s""",
        (nome, sobrenome, telefone, genero, news, request.usuario_id),
        fetch='none'
    )
    return ok(msg='Perfil atualizado!')


@app.route('/api/auth/alterar-senha', methods=['POST'])
@requer_login
def alterar_senha():
    d             = request.get_json() or {}
    senha_atual   = d.get('senha_atual', '')
    nova_senha    = d.get('nova_senha', '')

    if not senha_atual or not nova_senha:
        return err('Informe a senha atual e a nova senha')
    if len(nova_senha) < 8:
        return err('A nova senha deve ter ao menos 8 caracteres')

    user, _ = query("SELECT senha_hash FROM usuarios WHERE id=%s",
                    (request.usuario_id,), fetch='one')
    if not check_password_hash(user['senha_hash'], senha_atual):
        return err('Senha atual incorreta', 401)

    query("UPDATE usuarios SET senha_hash=%s WHERE id=%s",
          (generate_password_hash(nova_senha), request.usuario_id), fetch='none')
    log(request.usuario_id, 'alterar_senha')
    return ok(msg='Senha alterada com sucesso!')

# ============================================================
#  ENDEREÇOS
# ============================================================

@app.route('/api/enderecos', methods=['GET'])
@requer_login
def listar_enderecos():
    rows, _ = query("SELECT * FROM enderecos WHERE usuario_id=%s ORDER BY padrao DESC, id",
                    (request.usuario_id,))
    return ok(rows)


@app.route('/api/enderecos', methods=['POST'])
@requer_login
def criar_endereco():
    d = request.get_json() or {}
    campos = ['cep','logradouro','numero','bairro','cidade','estado']
    for c in campos:
        if not d.get(c):
            return err(f'Campo obrigatório: {c}')

    if d.get('padrao'):
        query("UPDATE enderecos SET padrao=0 WHERE usuario_id=%s",
              (request.usuario_id,), fetch='none')

    _, eid = query(
        """INSERT INTO enderecos
           (usuario_id, apelido, cep, logradouro, numero, complemento, bairro, cidade, estado, padrao)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (request.usuario_id, d.get('apelido','Casa'),
         d['cep'], d['logradouro'], d['numero'],
         d.get('complemento'), d['bairro'], d['cidade'], d['estado'],
         1 if d.get('padrao') else 0),
        fetch='none'
    )
    return ok({'id': eid}, 'Endereço adicionado!', 201)


@app.route('/api/enderecos/<int:eid>', methods=['DELETE'])
@requer_login
def deletar_endereco(eid):
    query("DELETE FROM enderecos WHERE id=%s AND usuario_id=%s",
          (eid, request.usuario_id), fetch='none')
    return ok(msg='Endereço removido.')

# ============================================================
#  CATEGORIAS
# ============================================================

@app.route('/api/categorias', methods=['GET'])
def listar_categorias():
    rows, _ = query("SELECT * FROM categorias WHERE ativa=1 ORDER BY ordem, nome")
    return ok(rows)

# ============================================================
#  PRODUTOS (público)
# ============================================================

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    categoria = request.args.get('categoria')
    busca     = request.args.get('q', '')
    destaque  = request.args.get('destaque')
    limite    = min(int(request.args.get('limite', 100)), 200)
    offset    = int(request.args.get('offset', 0))

    where  = ['p.ativo = 1']
    params = []

    if categoria:
        where.append('c.slug = %s')
        params.append(categoria)
    if busca:
        where.append('(p.nome LIKE %s OR p.descricao_curta LIKE %s)')
        params += [f'%{busca}%', f'%{busca}%']
    if destaque:
        where.append('p.destaque = 1')

    sql = f"""
        SELECT p.*, c.nome AS categoria_nome, c.slug AS categoria_slug
        FROM produtos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        WHERE {' AND '.join(where)}
        ORDER BY p.destaque DESC, p.id
        LIMIT %s OFFSET %s
    """
    params += [limite, offset]
    rows, _ = query(sql, params)
    # Converte Decimal para float
    for r in (rows or []):
        r['preco'] = float(r['preco'])
        if r.get('preco_promocional'):
            r['preco_promocional'] = float(r['preco_promocional'])
    return ok(rows)


@app.route('/api/produtos/<int:pid>', methods=['GET'])
def detalhe_produto(pid):
    prod, _ = query(
        """SELECT p.*, c.nome AS categoria_nome
           FROM produtos p
           LEFT JOIN categorias c ON c.id = p.categoria_id
           WHERE p.id=%s AND p.ativo=1""",
        (pid,), fetch='one'
    )
    if not prod:
        return err('Produto não encontrado', 404)
    prod['preco'] = float(prod['preco'])
    if prod.get('preco_promocional'):
        prod['preco_promocional'] = float(prod['preco_promocional'])

    imagens, _ = query("SELECT * FROM produto_imagens WHERE produto_id=%s ORDER BY ordem", (pid,))
    prod['imagens'] = imagens

    avaliacoes, _ = query(
        """SELECT a.*, u.nome AS nome_usuario
           FROM avaliacoes a
           LEFT JOIN usuarios u ON u.id = a.usuario_id
           WHERE a.produto_id=%s AND a.aprovada=1
           ORDER BY a.criado_em DESC""",
        (pid,)
    )
    for av in (avaliacoes or []):
        av['criado_em'] = str(av['criado_em'])
    prod['avaliacoes'] = avaliacoes

    prod['criado_em']     = str(prod['criado_em'])
    prod['atualizado_em'] = str(prod['atualizado_em'])
    return ok(prod)

# ============================================================
#  AVALIAÇÕES
# ============================================================

@app.route('/api/produtos/<int:pid>/avaliacoes', methods=['POST'])
def criar_avaliacao(pid):
    d          = request.get_json() or {}
    nota       = d.get('nota')
    comentario = d.get('comentario', '').strip()
    nome       = d.get('nome', '').strip() or None

    # Usuário logado (token opcional aqui)
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = verificar_token(token) if token else None
    uid = payload['sub'] if payload else None

    if not nota or int(nota) not in range(1, 6):
        return err('Nota inválida (1 a 5)')

    prod, _ = query("SELECT id FROM produtos WHERE id=%s AND ativo=1", (pid,), fetch='one')
    if not prod:
        return err('Produto não encontrado', 404)

    query(
        """INSERT INTO avaliacoes (produto_id, usuario_id, nome, nota, comentario)
           VALUES (%s,%s,%s,%s,%s)""",
        (pid, uid, nome, nota, comentario), fetch='none'
    )
    return ok(msg='Avaliação enviada! Será publicada após revisão.', code=201)

# ============================================================
#  LISTA DE DESEJOS
# ============================================================

@app.route('/api/desejos', methods=['GET'])
@requer_login
def listar_desejos():
    rows, _ = query(
        """SELECT p.id, p.nome, p.preco, p.imagem_principal, p.badge, p.slug
           FROM lista_desejos ld
           JOIN produtos p ON p.id = ld.produto_id
           WHERE ld.usuario_id=%s AND p.ativo=1
           ORDER BY ld.criado_em DESC""",
        (request.usuario_id,)
    )
    for r in (rows or []):
        r['preco'] = float(r['preco'])
    return ok(rows)


@app.route('/api/desejos/<int:pid>', methods=['POST'])
@requer_login
def adicionar_desejo(pid):
    query(
        "INSERT IGNORE INTO lista_desejos (usuario_id, produto_id) VALUES (%s,%s)",
        (request.usuario_id, pid), fetch='none'
    )
    return ok(msg='Produto adicionado à lista de desejos.')


@app.route('/api/desejos/<int:pid>', methods=['DELETE'])
@requer_login
def remover_desejo(pid):
    query(
        "DELETE FROM lista_desejos WHERE usuario_id=%s AND produto_id=%s",
        (request.usuario_id, pid), fetch='none'
    )
    return ok(msg='Produto removido da lista de desejos.')

# ============================================================
#  CUPONS — validar
# ============================================================

@app.route('/api/cupons/validar', methods=['POST'])
def validar_cupom():
    d       = request.get_json() or {}
    codigo  = (d.get('codigo') or '').strip().upper()
    total   = float(d.get('total', 0))

    if not codigo:
        return err('Informe o código do cupom')

    cupom, _ = query(
        """SELECT * FROM cupons
           WHERE codigo=%s AND ativo=1
             AND (valido_de IS NULL OR valido_de <= NOW())
             AND (valido_ate IS NULL OR valido_ate >= NOW())
             AND (limite_uso IS NULL OR total_usado < limite_uso)""",
        (codigo,), fetch='one'
    )
    if not cupom:
        return err('Cupom inválido ou expirado')

    minimo = float(cupom['valor_minimo_pedido'] or 0)
    if total < minimo:
        return err(f'Pedido mínimo para este cupom: R$ {minimo:.2f}')

    valor_cupom = float(cupom['valor'])
    if cupom['tipo'] == 'percentual':
        desconto = round(total * valor_cupom / 100, 2)
    else:
        desconto = min(valor_cupom, total)

    return ok({
        'id':       cupom['id'],
        'codigo':   cupom['codigo'],
        'tipo':     cupom['tipo'],
        'valor':    valor_cupom,
        'desconto': desconto,
    }, f'Cupom aplicado! Desconto de R$ {desconto:.2f}')

# ============================================================
#  PEDIDOS
# ============================================================

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    d = request.get_json() or {}

    carrinho = d.get('carrinho', [])
    cliente  = d.get('cliente', {})
    entrega  = d.get('entrega', {})
    pagamento = d.get('forma_pagamento', 'whatsapp')
    cupom_id  = d.get('cupom_id')
    obs       = d.get('observacao', '')

    if not carrinho:
        return err('Carrinho vazio')
    if not cliente.get('nome') or not cliente.get('email'):
        return err('Dados do cliente incompletos')

    # Usuário logado?
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = verificar_token(token) if token else None
    uid = payload['sub'] if payload else None

    # Recalcula valores no servidor (nunca confie no frontend)
    subtotal = 0.0
    itens_validados = []
    for item in carrinho:
        prod, _ = query(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id=%s AND ativo=1",
            (item.get('id'),), fetch='one'
        )
        if not prod:
            return err(f'Produto #{item.get("id")} não encontrado ou inativo')
        qtd = int(item.get('quantidade', 1))
        if prod['estoque'] < qtd:
            return err(f'Estoque insuficiente para: {prod["nome"]}')
        preco = float(prod['preco'])
        subtotal += preco * qtd
        itens_validados.append({'prod': prod, 'qtd': qtd, 'preco': preco})

    # Desconto do cupom
    desconto = 0.0
    if cupom_id:
        cupom, _ = query("SELECT * FROM cupons WHERE id=%s AND ativo=1", (cupom_id,), fetch='one')
        if cupom:
            v = float(cupom['valor'])
            desconto = round(subtotal * v / 100, 2) if cupom['tipo'] == 'percentual' else min(v, subtotal)

    # Frete
    cfg_frete, _ = query(
        "SELECT valor FROM configuracoes WHERE chave='frete_padrao'", fetch='one')
    cfg_gratis, _ = query(
        "SELECT valor FROM configuracoes WHERE chave='frete_gratis_acima'", fetch='one')
    frete_padrao  = float(cfg_frete['valor']  if cfg_frete  else 15.00)
    frete_gratis  = float(cfg_gratis['valor'] if cfg_gratis else 150.00)
    frete = 0.0 if (subtotal - desconto) >= frete_gratis else frete_padrao
    total = round(subtotal - desconto + frete, 2)

    # Salva pedido
    _, ped_id = query(
        """INSERT INTO pedidos
           (usuario_id, cupom_id,
            nome_cliente, email_cliente, telefone_cliente,
            cep, logradouro, numero, complemento, bairro, cidade, estado,
            subtotal, desconto, frete, total,
            forma_pagamento, status_pagamento, status, observacao)
           VALUES
           (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (uid, cupom_id or None,
         cliente['nome'], cliente['email'], cliente.get('telefone'),
         entrega.get('cep'), entrega.get('logradouro'), entrega.get('numero'),
         entrega.get('complemento'), entrega.get('bairro'),
         entrega.get('cidade'), entrega.get('estado'),
         subtotal, desconto, frete, total,
         pagamento, 'pendente', 'aguardando_pagamento', obs),
        fetch='none'
    )

    # Salva itens e baixa estoque
    for it in itens_validados:
        query(
            """INSERT INTO pedido_itens (pedido_id, produto_id, nome, preco_unit, quantidade, subtotal)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (ped_id, it['prod']['id'], it['prod']['nome'],
             it['preco'], it['qtd'], round(it['preco'] * it['qtd'], 2)),
            fetch='none'
        )
        query("UPDATE produtos SET estoque = estoque - %s WHERE id=%s",
              (it['qtd'], it['prod']['id']), fetch='none')

    # Incrementa uso do cupom
    if cupom_id:
        query("UPDATE cupons SET total_usado = total_usado + 1 WHERE id=%s",
              (cupom_id,), fetch='none')

    if uid:
        log(uid, 'novo_pedido', f'Pedido #{ped_id} — R$ {total:.2f}')

    return ok({'pedido_id': ped_id, 'total': total}, 'Pedido realizado com sucesso!', 201)


@app.route('/api/pedidos', methods=['GET'])
@requer_login
def listar_pedidos():
    rows, _ = query(
        """SELECT id, total, status, status_pagamento, forma_pagamento,
                  criado_em, rastreamento
           FROM pedidos WHERE usuario_id=%s
           ORDER BY criado_em DESC""",
        (request.usuario_id,)
    )
    for r in (rows or []):
        r['total']     = float(r['total'])
        r['criado_em'] = str(r['criado_em'])
    return ok(rows)


@app.route('/api/pedidos/<int:pid>', methods=['GET'])
@requer_login
def detalhe_pedido(pid):
    ped, _ = query(
        "SELECT * FROM pedidos WHERE id=%s AND usuario_id=%s",
        (pid, request.usuario_id), fetch='one'
    )
    if not ped:
        return err('Pedido não encontrado', 404)

    itens, _ = query(
        "SELECT * FROM pedido_itens WHERE pedido_id=%s", (pid,)
    )
    for it in (itens or []):
        it['preco_unit'] = float(it['preco_unit'])
        it['subtotal']   = float(it['subtotal'])
    for k in ('subtotal','desconto','frete','total'):
        ped[k] = float(ped[k])
    ped['criado_em']     = str(ped['criado_em'])
    ped['atualizado_em'] = str(ped['atualizado_em'])
    ped['itens'] = itens
    return ok(ped)

# ============================================================
#  CONTATO (formulário)
# ============================================================

@app.route('/api/contato', methods=['POST'])
def contato():
    d        = request.get_json() or {}
    nome     = (d.get('nome')     or '').strip()
    email    = (d.get('email')    or '').strip()
    telefone = (d.get('telefone') or '').strip() or None
    mensagem = (d.get('mensagem') or '').strip()

    if not nome or not email or not mensagem:
        return err('Preencha todos os campos obrigatórios')

    query(
        "INSERT INTO contatos (nome, email, telefone, mensagem) VALUES (%s,%s,%s,%s)",
        (nome, email, telefone, mensagem), fetch='none'
    )

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;
                padding:20px;background:#fff8e7;">
        <h2 style="color:#3E2723;border-bottom:3px solid #D4AF37;padding-bottom:10px;">
            Novo Contato — Spinassi Chocolates
        </h2>
        <p><strong>Nome:</strong> {nome}</p>
        <p><strong>E-mail:</strong> {email}</p>
        <p><strong>Telefone:</strong> {telefone or 'Não informado'}</p>
        <hr style="border-color:#D4AF37;">
        <p><strong>Mensagem:</strong></p>
        <p style="white-space:pre-wrap;">{mensagem}</p>
        <p style="color:#999;font-size:12px;">
            Recebido em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
        </p>
    </div>"""
    enviar_email(EMAIL_CONFIG['destinatario'],
                 f'Novo Contato — {nome}', html)
    return ok(msg='Mensagem enviada com sucesso!')

# ============================================================
#  CONFIGURAÇÕES PÚBLICAS
# ============================================================

@app.route('/api/config', methods=['GET'])
def config_publica():
    chaves_publicas = ('nome_loja','whatsapp','email_loja',
                       'frete_gratis_acima','frete_padrao',
                       'instagram','facebook')
    rows, _ = query(
        f"SELECT chave, valor FROM configuracoes WHERE chave IN {chaves_publicas}"
    )
    return ok({r['chave']: r['valor'] for r in (rows or [])})

# ============================================================
#  ÁREA ADMIN
# ============================================================

# ── Dashboard ──────────────────────────────────────────────
@app.route('/api/admin/dashboard', methods=['GET'])
@requer_admin
def admin_dashboard():
    total_usuarios, _ = query(
        "SELECT COUNT(*) AS n FROM usuarios WHERE tipo='cliente'", fetch='one')
    total_pedidos, _ = query(
        "SELECT COUNT(*) AS n FROM pedidos", fetch='one')
    faturamento, _ = query(
        "SELECT COALESCE(SUM(total),0) AS v FROM pedidos WHERE status_pagamento='aprovado'",
        fetch='one')
    pedidos_hoje, _ = query(
        "SELECT COUNT(*) AS n FROM pedidos WHERE DATE(criado_em)=CURDATE()", fetch='one')
    contatos_nao_lidos, _ = query(
        "SELECT COUNT(*) AS n FROM contatos WHERE lida=0", fetch='one')
    avaliacoes_pendentes, _ = query(
        "SELECT COUNT(*) AS n FROM avaliacoes WHERE aprovada=0", fetch='one')
    produtos_sem_estoque, _ = query(
        "SELECT COUNT(*) AS n FROM produtos WHERE estoque=0 AND ativo=1", fetch='one')

    return ok({
        'usuarios':            total_usuarios['n'],
        'pedidos_total':       total_pedidos['n'],
        'faturamento':         float(faturamento['v']),
        'pedidos_hoje':        pedidos_hoje['n'],
        'contatos_nao_lidos':  contatos_nao_lidos['n'],
        'avaliacoes_pendentes':avaliacoes_pendentes['n'],
        'produtos_sem_estoque':produtos_sem_estoque['n'],
    })

# ── Usuários (admin) ───────────────────────────────────────
@app.route('/api/admin/usuarios', methods=['GET'])
@requer_admin
def admin_listar_usuarios():
    rows, _ = query(
        """SELECT id, nome, sobrenome, email, tipo, ativo, criado_em
           FROM usuarios ORDER BY criado_em DESC"""
    )
    for r in (rows or []):
        r['criado_em'] = str(r['criado_em'])
    return ok(rows)


@app.route('/api/admin/usuarios/<int:uid>/ativar', methods=['PATCH'])
@requer_admin
def admin_ativar_usuario(uid):
    d = request.get_json() or {}
    query("UPDATE usuarios SET ativo=%s WHERE id=%s",
          (1 if d.get('ativo') else 0, uid), fetch='none')
    return ok(msg='Status atualizado.')


@app.route('/api/admin/usuarios/<int:uid>/tipo', methods=['PATCH'])
@requer_admin
def admin_alterar_tipo(uid):
    d    = request.get_json() or {}
    tipo = d.get('tipo', 'cliente')
    if tipo not in ('admin', 'cliente'):
        return err('Tipo inválido')
    query("UPDATE usuarios SET tipo=%s WHERE id=%s", (tipo, uid), fetch='none')
    return ok(msg='Tipo de usuário atualizado.')

# ── Produtos (admin) ───────────────────────────────────────
@app.route('/api/admin/produtos', methods=['GET'])
@requer_admin
def admin_listar_produtos():
    rows, _ = query(
        """SELECT p.*, c.nome AS categoria_nome
           FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id
           ORDER BY p.id DESC"""
    )
    for r in (rows or []):
        r['preco'] = float(r['preco'])
        if r.get('preco_promocional'):
            r['preco_promocional'] = float(r['preco_promocional'])
        r['criado_em']     = str(r['criado_em'])
        r['atualizado_em'] = str(r['atualizado_em'])
    return ok(rows)


@app.route('/api/admin/produtos', methods=['POST'])
@requer_admin
def admin_criar_produto():
    d = request.get_json() or {}
    if not d.get('nome') or not d.get('preco'):
        return err('Nome e preço são obrigatórios')

    slug = d.get('slug') or d['nome'].lower().replace(' ', '-')
    _, pid = query(
        """INSERT INTO produtos
           (categoria_id, nome, slug, descricao, descricao_curta, preco,
            preco_promocional, estoque, imagem_principal, badge,
            peso_gramas, ativo, destaque)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (d.get('categoria_id'), d['nome'], slug,
         d.get('descricao'), d.get('descricao_curta'), d['preco'],
         d.get('preco_promocional'), d.get('estoque', 0),
         d.get('imagem_principal'), d.get('badge'),
         d.get('peso_gramas'), 1 if d.get('ativo', True) else 0,
         1 if d.get('destaque') else 0),
        fetch='none'
    )
    return ok({'id': pid}, 'Produto criado!', 201)


@app.route('/api/admin/produtos/<int:pid>', methods=['PUT'])
@requer_admin
def admin_atualizar_produto(pid):
    d = request.get_json() or {}
    query(
        """UPDATE produtos SET
           categoria_id=%s, nome=%s, descricao=%s, descricao_curta=%s,
           preco=%s, preco_promocional=%s, estoque=%s,
           imagem_principal=%s, badge=%s, peso_gramas=%s,
           ativo=%s, destaque=%s
           WHERE id=%s""",
        (d.get('categoria_id'), d.get('nome'), d.get('descricao'),
         d.get('descricao_curta'), d.get('preco'), d.get('preco_promocional'),
         d.get('estoque'), d.get('imagem_principal'), d.get('badge'),
         d.get('peso_gramas'), 1 if d.get('ativo', True) else 0,
         1 if d.get('destaque') else 0, pid),
        fetch='none'
    )
    return ok(msg='Produto atualizado!')


@app.route('/api/admin/produtos/<int:pid>', methods=['DELETE'])
@requer_admin
def admin_deletar_produto(pid):
    query("UPDATE produtos SET ativo=0 WHERE id=%s", (pid,), fetch='none')
    return ok(msg='Produto desativado.')

# ── Pedidos (admin) ────────────────────────────────────────
@app.route('/api/admin/pedidos', methods=['GET'])
@requer_admin
def admin_listar_pedidos():
    status = request.args.get('status')
    params = []
    where  = ''
    if status:
        where = 'WHERE p.status=%s'
        params.append(status)
    rows, _ = query(
        f"""SELECT p.id, p.nome_cliente, p.email_cliente, p.total,
                   p.status, p.status_pagamento, p.forma_pagamento,
                   p.criado_em, p.rastreamento
            FROM pedidos p {where}
            ORDER BY p.criado_em DESC
            LIMIT 200""",
        params
    )
    for r in (rows or []):
        r['total']     = float(r['total'])
        r['criado_em'] = str(r['criado_em'])
    return ok(rows)


@app.route('/api/admin/pedidos/<int:pid>/status', methods=['PATCH'])
@requer_admin
def admin_atualizar_status_pedido(pid):
    d              = request.get_json() or {}
    status         = d.get('status')
    status_pag     = d.get('status_pagamento')
    rastreamento   = d.get('rastreamento')

    sets, vals = [], []
    if status:
        sets.append('status=%s'); vals.append(status)
    if status_pag:
        sets.append('status_pagamento=%s'); vals.append(status_pag)
    if rastreamento is not None:
        sets.append('rastreamento=%s'); vals.append(rastreamento)

    if not sets:
        return err('Nada para atualizar')

    vals.append(pid)
    query(f"UPDATE pedidos SET {', '.join(sets)} WHERE id=%s", vals, fetch='none')
    log(request.usuario_id, 'atualizar_pedido', f'Pedido #{pid} → {status or status_pag}')
    return ok(msg='Pedido atualizado.')

# ── Contatos (admin) ───────────────────────────────────────
@app.route('/api/admin/contatos', methods=['GET'])
@requer_admin
def admin_listar_contatos():
    rows, _ = query("SELECT * FROM contatos ORDER BY criado_em DESC LIMIT 200")
    for r in (rows or []):
        r['criado_em'] = str(r['criado_em'])
    return ok(rows)


@app.route('/api/admin/contatos/<int:cid>/lida', methods=['PATCH'])
@requer_admin
def admin_marcar_contato(cid):
    query("UPDATE contatos SET lida=1 WHERE id=%s", (cid,), fetch='none')
    return ok(msg='Marcado como lido.')

# ── Avaliações (admin) ─────────────────────────────────────
@app.route('/api/admin/avaliacoes', methods=['GET'])
@requer_admin
def admin_listar_avaliacoes():
    rows, _ = query(
        """SELECT a.*, p.nome AS produto_nome
           FROM avaliacoes a JOIN produtos p ON p.id=a.produto_id
           ORDER BY a.criado_em DESC"""
    )
    for r in (rows or []):
        r['criado_em'] = str(r['criado_em'])
    return ok(rows)


@app.route('/api/admin/avaliacoes/<int:aid>/aprovar', methods=['PATCH'])
@requer_admin
def admin_aprovar_avaliacao(aid):
    d = request.get_json() or {}
    query("UPDATE avaliacoes SET aprovada=%s WHERE id=%s",
          (1 if d.get('aprovada') else 0, aid), fetch='none')
    return ok(msg='Avaliação atualizada.')

# ── Configurações (admin) ──────────────────────────────────
@app.route('/api/admin/config', methods=['GET'])
@requer_admin
def admin_listar_config():
    rows, _ = query("SELECT * FROM configuracoes ORDER BY chave")
    return ok({r['chave']: r['valor'] for r in (rows or [])})


@app.route('/api/admin/config', methods=['PUT'])
@requer_admin
def admin_atualizar_config():
    d = request.get_json() or {}
    for chave, valor in d.items():
        query(
            "INSERT INTO configuracoes (chave, valor) VALUES (%s,%s) "
            "ON DUPLICATE KEY UPDATE valor=%s",
            (chave, valor, valor), fetch='none'
        )
    return ok(msg='Configurações salvas.')

# ── Cupons (admin) ─────────────────────────────────────────
@app.route('/api/admin/cupons', methods=['GET'])
@requer_admin
def admin_listar_cupons():
    rows, _ = query("SELECT * FROM cupons ORDER BY criado_em DESC")
    for r in (rows or []):
        r['valor']               = float(r['valor'])
        r['valor_minimo_pedido'] = float(r['valor_minimo_pedido'] or 0)
        r['criado_em']           = str(r['criado_em'])
    return ok(rows)


@app.route('/api/admin/cupons', methods=['POST'])
@requer_admin
def admin_criar_cupom():
    d = request.get_json() or {}
    if not d.get('codigo') or not d.get('valor'):
        return err('Código e valor são obrigatórios')
    query(
        """INSERT INTO cupons
           (codigo, descricao, tipo, valor, valor_minimo_pedido,
            limite_uso, ativo, valido_de, valido_ate)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (d['codigo'].upper(), d.get('descricao'), d.get('tipo','percentual'),
         d['valor'], d.get('valor_minimo_pedido'),
         d.get('limite_uso'), 1 if d.get('ativo', True) else 0,
         d.get('valido_de'), d.get('valido_ate')),
        fetch='none'
    )
    return ok(msg='Cupom criado!', code=201)


@app.route('/api/admin/cupons/<int:cid>', methods=['DELETE'])
@requer_admin
def admin_deletar_cupom(cid):
    query("UPDATE cupons SET ativo=0 WHERE id=%s", (cid,), fetch='none')
    return ok(msg='Cupom desativado.')

# ============================================================
#  INICIALIZAÇÃO
# ============================================================

if __name__ == '__main__':
    print('=' * 60)
    print('🍫  Spinassi Chocolates — API Backend')
    print('=' * 60)
    print(f'  DB Host : {DB_CONFIG["host"]}:{DB_CONFIG["port"]}')
    print(f'  DB Name : {DB_CONFIG["database"]}')
    print(f'  JWT     : {"ativo" if JWT_DISPONIVEL else "inativo (instale PyJWT)"}')
    print('=' * 60)

    # Testa a conexão ao iniciar
    try:
        conn = get_db()
        conn.ping()
        conn.close()
        print('  ✅ Banco de dados conectado com sucesso!')
    except Exception as e:
        print(f'  ❌ Erro ao conectar ao banco: {e}')

    print(f'\n  Acesse: http://localhost:5000\n')
    print('=' * 60 + '\n')

    os.makedirs('logs', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)