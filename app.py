from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Configurações de email (ajuste com suas credenciais)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'seu-email@gmail.com',  # Substitua pelo seu email
    'senha': 'sua-senha-app',  # Substitua pela senha de app do Gmail
    'destinatario': 'contato@chocolaterienoir.com'  # Email que receberá as mensagens
}

@app.route('/')
def index():
    """Servir página inicial"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Servir arquivos estáticos"""
    return send_from_directory('.', path)

@app.route('/api/contato', methods=['POST'])
def contato():
    """Processar formulário de contato"""
    try:
        data = request.get_json()
        
        nome = data.get('nome', '')
        email = data.get('email', '')
        telefone = data.get('telefone', '')
        mensagem = data.get('mensagem', '')
        
        # Validação básica
        if not nome or not email or not mensagem:
            return jsonify({
                'success': False,
                'message': 'Preencha todos os campos obrigatórios'
            }), 400
        
        # Enviar email
        sucesso = enviar_email_contato(nome, email, telefone, mensagem)
        
        if sucesso:
            # Salvar em arquivo de log também
            salvar_log_contato(nome, email, telefone, mensagem)
            
            return jsonify({
                'success': True,
                'message': 'Mensagem enviada com sucesso!'
            })
        else:
            # Se o email falhar, ainda salva no log
            salvar_log_contato(nome, email, telefone, mensagem)
            
            return jsonify({
                'success': True,
                'message': 'Mensagem recebida! Entraremos em contato em breve.'
            })
            
    except Exception as e:
        print(f"Erro ao processar contato: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao processar mensagem'
        }), 500

def enviar_email_contato(nome, email, telefone, mensagem):
    """Enviar email com os dados do formulário"""
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Novo Contato - Chocolaterie Noir - {nome}'
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = EMAIL_CONFIG['destinatario']
        
        # Corpo do email em HTML
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #fff8e7;">
                    <h2 style="color: #3e2723; border-bottom: 3px solid #d4af37; padding-bottom: 10px;">
                        Novo Contato - Chocolaterie Noir
                    </h2>
                    
                    <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #d4af37;">
                        <p><strong style="color: #5d4037;">Nome:</strong> {nome}</p>
                        <p><strong style="color: #5d4037;">Email:</strong> {email}</p>
                        <p><strong style="color: #5d4037;">Telefone:</strong> {telefone if telefone else 'Não informado'}</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #5d4037; margin-bottom: 10px;">Mensagem:</h3>
                        <p style="white-space: pre-wrap;">{mensagem}</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        <p>Recebido em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Anexar HTML
        part = MIMEText(html, 'html')
        msg.attach(part)
        
        # Enviar via SMTP
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['senha'])
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False

def salvar_log_contato(nome, email, telefone, mensagem):
    """Salvar contato em arquivo de log"""
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        with open('logs/contatos.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Nome: {nome}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Telefone: {telefone if telefone else 'Não informado'}\n")
            f.write(f"Mensagem:\n{mensagem}\n")
            f.write(f"{'='*80}\n")
            
    except Exception as e:
        print(f"Erro ao salvar log: {str(e)}")

@app.route('/api/pedido', methods=['POST'])
def pedido():
    """Processar pedido (opcional - pode usar WhatsApp direto)"""
    try:
        data = request.get_json()
        
        carrinho = data.get('carrinho', [])
        cliente = data.get('cliente', {})
        
        if not carrinho or not cliente:
            return jsonify({
                'success': False,
                'message': 'Dados incompletos'
            }), 400
        
        # Processar pedido (salvar em banco, enviar email, etc.)
        salvar_log_pedido(carrinho, cliente)
        
        return jsonify({
            'success': True,
            'message': 'Pedido recebido com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao processar pedido: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao processar pedido'
        }), 500

def salvar_log_pedido(carrinho, cliente):
    """Salvar pedido em arquivo de log"""
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        total = sum(item['preco'] * item['quantidade'] for item in carrinho)
        
        with open('logs/pedidos.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Cliente: {cliente.get('nome', 'N/A')}\n")
            f.write(f"Email: {cliente.get('email', 'N/A')}\n")
            f.write(f"Telefone: {cliente.get('telefone', 'N/A')}\n")
            f.write(f"\nItens:\n")
            
            for item in carrinho:
                f.write(f"  - {item['quantidade']}x {item['nome']} - R$ {item['preco']:.2f}\n")
            
            f.write(f"\nTotal: R$ {total:.2f}\n")
            f.write(f"{'='*80}\n")
            
    except Exception as e:
        print(f"Erro ao salvar log de pedido: {str(e)}")

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint de status"""
    return jsonify({
        'status': 'online',
        'message': 'Chocolaterie Noir API está funcionando!'
    })

if __name__ == '__main__':
    print("="*80)
    print("🍫 Chocolaterie Noir - Servidor Backend")
    print("="*80)
    print("\nServidor iniciado com sucesso!")
    print("\nAcesse: http://localhost:5000")
    print("\nPara parar o servidor: Ctrl+C")
    print("\n" + "="*80 + "\n")
    
    # Criar pasta de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')