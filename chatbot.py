# Importação das bibliotecas necessárias
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3  # Para manipulação do banco de dados SQLite
import hashlib  # Para criptografia de senhas
import csv     # Para leitura do arquivo de perguntas
import json    # Para leitura do arquivo de respostas
from functools import wraps  # Para decoradores

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Chave secreta para sessões

# ========================================
# BLOCO: INICIALIZAÇÃO DO BANCO DE DADOS
# ========================================
def init_db():
    """
    Inicializa o banco de dados SQLite criando as tabelas necessárias
    se elas ainda não existirem
    """
    conexao = sqlite3.connect("chatbot.db")
    cursor = conexao.cursor()
    
    # Criar tabela de usuários para autenticação
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        telefone TEXT,
        senha TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Manter tabela de clientes existente para dados do cartão
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        email TEXT,
        telefone TEXT,
        numero_cartao TEXT,
        limite_cartao TEXT,
        valor_fatura TEXT,
        vencimento_fatura TEXT,
        status_fatura TEXT
    )
    """)
    
    conexao.commit()
    conexao.close()

# ========================================
# BLOCO: FUNÇÕES AUXILIARES
# ========================================
def login_requerido(f):
    """
    Decorador que exige que o usuário esteja logado para acessar a rota
    Redireciona para página de login se não estiver autenticado
    """
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcao_decorada

def criptografar_senha(senha):
    """
    Criptografa a senha usando algoritmo SHA256
    Retorna o hash da senha em formato hexadecimal
    """
    return hashlib.sha256(senha.encode()).hexdigest()

def obter_dados_cartao_usuario(user_id):
    """
    Obtém os dados do cartão de crédito do usuário logado
    Retorna dicionário com informações do cartão ou None se não encontrado
    """
    conexao = sqlite3.connect("chatbot.db")
    cursor = conexao.cursor()
    
    try:
        # Buscar dados do cartão usando o email do usuário logado
        cursor.execute("""
        SELECT numero_cartao, limite_cartao, valor_fatura, vencimento_fatura, status_fatura 
        FROM clientes 
        WHERE email = (SELECT email FROM usuarios WHERE id = ?)
        """, (user_id,))
        
        dados_cartao = cursor.fetchone()
        
        if dados_cartao:
            return {
                'numero_cartao': dados_cartao[0] or "Não informado",
                'limite_cartao': dados_cartao[1] or "Não informado",
                'valor_fatura': dados_cartao[2] or "R$ 0,00",
                'vencimento_fatura': dados_cartao[3] or "Não informado",
                'status_fatura': dados_cartao[4] or "Não informado"
            }
        else:
            return None
            
    except Exception as erro:
        print(f"Erro ao buscar dados do cartão: {erro}")
        return None
    finally:
        conexao.close()

@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('chatbot'))
    return redirect(url_for('cadastro'))

@app.route("/cadastro")
def cadastro():
    if 'user_id' in session:
        return redirect(url_for('chatbot'))
    return render_template("cadastro.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    """
    Processa o formulário de cadastro completo
    Salva dados do usuário na tabela usuarios e dados do cartão na tabela clientes
    Tudo em uma única transação para garantir consistência
    """
    # Obter dados pessoais do formulário
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    email = request.form["email"]
    telefone = request.form.get("telefone", "")
    senha = request.form["senha"]
    confirmar_senha = request.form["confirmar_senha"]
    
    # Obter dados do cartão de crédito
    numero_cartao = request.form.get("numero_cartao", "")
    limite_cartao = request.form.get("limite_cartao", "")
    valor_fatura = request.form.get("valor_fatura", "")
    vencimento_fatura = request.form.get("vencimento_fatura", "")
    status_fatura = request.form.get("status_fatura", "")

    # Validação básica dos dados pessoais
    if senha != confirmar_senha:
        flash("As senhas não coincidem!", "error")
        return redirect(url_for('cadastro'))
    
    if len(senha) < 6:
        flash("A senha deve ter pelo menos 6 caracteres!", "error")
        return redirect(url_for('cadastro'))

    # Conectar ao banco de dados para salvar usuário e cliente
    conexao = sqlite3.connect("chatbot.db")
    cursor = conexao.cursor()

    try:
        # Iniciar transação para salvar ambos os dados
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Salvar usuário na tabela de usuários
        senha_criptografada = criptografar_senha(senha)
        cursor.execute("""
        INSERT INTO usuarios (nome, cpf, email, telefone, senha)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, cpf, email, telefone, senha_criptografada))
        
        # 2. Salvar dados do cartão na tabela de clientes
        cursor.execute("""
        INSERT INTO clientes (nome, cpf, email, telefone, numero_cartao, limite_cartao, valor_fatura, vencimento_fatura, status_fatura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, email, telefone, numero_cartao, limite_cartao, valor_fatura, vencimento_fatura, status_fatura))
        
        # Confirmar transação se tudo deu certo
        conexao.commit()
        flash("Cadastro realizado com sucesso! Seus dados do cartão foram salvos. Faça login para continuar.", "success")
        return redirect(url_for('login'))
        
    except sqlite3.IntegrityError as erro:
        # Desfazer transação em caso de erro
        conexao.rollback()
        
        # Tratar erros específicos de duplicidade
        if "cpf" in str(erro):
            flash("CPF já cadastrado!", "error")
        elif "email" in str(erro):
            flash("Email já cadastrado!", "error")
        else:
            flash("Erro no cadastro. Tente novamente.", "error")
        return redirect(url_for('cadastro'))
    except Exception as erro:
        # Desfazer transação em caso de qualquer outro erro
        conexao.rollback()
        flash("Erro ao cadastrar. Tente novamente.", "error")
        return redirect(url_for('cadastro'))
    finally:
        conexao.close()

# ========================================
# BLOCO: AUTENTICAÇÃO DE USUÁRIOS
# ========================================
@app.route("/login")
def login():
    """
    Exibe página de login para usuários existentes
    Se já estiver logado, redireciona para o chatbot
    """
    if 'user_id' in session:
        return redirect(url_for('chatbot'))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def autenticar():
    """
    Processa o formulário de login
    Verifica email e senha no banco de dados e cria sessão se válido
    """
    # Obter dados do formulário
    email = request.form["email"]
    senha = request.form["senha"]
    
    # Conectar ao banco para verificar usuário
    conexao = sqlite3.connect("chatbot.db")
    cursor = conexao.cursor()
    
    # Buscar usuário pelo email
    cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conexao.close()
    
    # Verificar se usuário existe e senha está correta
    if usuario and usuario[3] == criptografar_senha(senha):
        # Criar sessão do usuário
        session['user_id'] = usuario[0]
        session['user_name'] = usuario[1]
        session['user_email'] = usuario[2]
        flash(f"Bem-vindo, {usuario[1]}!", "success")
        return redirect(url_for('chatbot'))
    else:
        flash("Email ou senha incorretos!", "error")
        return redirect(url_for('login'))

@app.route("/chatbot")
@login_requerido
def chatbot():
    """
    Exibe a página principal do chatbot
    Requer que o usuário esteja autenticado
    """
    return render_template("chatbot.html")

@app.route("/logout")
def logout():
    """
    Encerra a sessão do usuário e redireciona para login
    Limpa todos os dados da sessão
    """
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for('login'))

# ========================================
# BLOCO: CARREGAMENTO DE DADOS DO CHATBOT
# ========================================
def carregar_dados_chatbot():
    """
    Carrega as perguntas do arquivo CSV e respostas do arquivo JSON
    Organiza as perguntas por categoria para processamento eficiente
    Retorna: dicionário de perguntas por categoria e dicionário de respostas
    """
    perguntas_por_categoria = {}
    
    # Carregar perguntas do arquivo CSV
    try:
        with open('perguntas.csv', 'r', encoding='utf-8') as arquivo_csv:
            leitor_csv = csv.DictReader(arquivo_csv)
            for linha in leitor_csv:
                categoria = linha['categoria']
                frase = linha['frase']
                if categoria not in perguntas_por_categoria:
                    perguntas_por_categoria[categoria] = []
                perguntas_por_categoria[categoria].append(frase.lower())
    except FileNotFoundError:
        print("Arquivo perguntas.csv não encontrado. Usando lista vazia.")
    
    # Carregar respostas do arquivo JSON
    try:
        with open('respostas.json', 'r', encoding='utf-8') as arquivo_json:
            respostas = json.load(arquivo_json)
    except FileNotFoundError:
        print("Arquivo respostas.json não encontrado. Usando dicionário vazio.")
        respostas = {}
    
    return perguntas_por_categoria, respostas

# Carregar dados na inicialização do servidor
perguntas_por_categoria, respostas = carregar_dados_chatbot()

# ========================================
# BLOCO: API DO CHATBOT
# ========================================
@app.route("/api/chat", methods=["POST"])
@login_requerido
def api_chatbot():
    """
    API para processar mensagens do chatbot
    Recebe mensagem do usuário, encontra correspondência e retorna resposta adequada
    Requer autenticação do usuário
    """
    # Obter mensagem do usuário e normalizar
    mensagem_usuario = request.json.get("message", "").lower().strip()
    user_id = session.get('user_id')
    
    # Se mensagem vazia, retornar saudação padrão
    if not mensagem_usuario:
        return {"response": "Olá! Sou seu assistente de cartão de crédito. Como posso ajudar você?"}
    
    # ========================================
    # VERIFICAR SOLICITAÇÕES DE DADOS PESSOAIS
    # ========================================
    
    # Palavras-chave para dados pessoais do cartão
    palavras_limite = ["meu limite", "limite do meu cartão", "qual meu limite", "quanto de limite", "limite disponível"]
    palavras_fatura = ["minha fatura", "valor da fatura", "quanto devo", "valor fatura", "fatura atual"]
    palavras_vencimento = ["vencimento da fatura", "quando vence", "data vencimento", "vence minha fatura"]
    palavras_status = ["status da fatura", "minha fatura está", "situação da fatura", "fatura status"]
    palavras_cartao = ["meu cartão", "dados do cartão", "informações do cartão", "meu número"]
    
    # Obter dados do cartão do usuário logado
    dados_cartao = obter_dados_cartao_usuario(user_id) if user_id else None
    
    # Verificar solicitações específicas de dados pessoais
    if any(palavra in mensagem_usuario for palavra in palavras_limite):
        if dados_cartao and dados_cartao['limite_cartao'] != "Não informado":
            return {"response": f"Seu limite de crédito atual é: {dados_cartao['limite_cartao']}"}
        else:
            return {"response": "Não encontrei informações sobre seu limite de crédito. Verifique se seus dados do cartão foram cadastrados corretamente."}
    
    elif any(palavra in mensagem_usuario for palavra in palavras_fatura):
        if dados_cartao and dados_cartao['valor_fatura'] != "R$ 0,00" and dados_cartao['valor_fatura'] != "Não informado":
            return {"response": f"O valor atual da sua fatura é: {dados_cartao['valor_fatura']}"}
        else:
            return {"response": "Sua fatura atual está em R$ 0,00 ou não foi informada. Você pode verificar suas compras recentes no extrato."}
    
    elif any(palavra in mensagem_usuario for palavra in palavras_vencimento):
        if dados_cartao and dados_cartao['vencimento_fatura'] != "Não informado":
            return {"response": f"Sua fatura vence no dia: {dados_cartao['vencimento_fatura']}"}
        else:
            return {"response": "Não encontrei informação sobre o vencimento da sua fatura. Verifique seus dados cadastrais."}
    
    elif any(palavra in mensagem_usuario for palavra in palavras_status):
        if dados_cartao and dados_cartao['status_fatura'] != "Não informado":
            return {"response": f"O status da sua fatura é: {dados_cartao['status_fatura']}"}
        else:
            return {"response": "Não encontrei informação sobre o status da sua fatura. Entre em contato com o suporte para mais detalhes."}
    
    elif any(palavra in mensagem_usuario for palavra in palavras_cartao):
        if dados_cartao:
            resposta = f"📊 **Seus Dados do Cartão:**\n"
            resposta += f"• Limite: {dados_cartao['limite_cartao']}\n"
            resposta += f"• Fatura Atual: {dados_cartao['valor_fatura']}\n"
            resposta += f"• Vencimento: {dados_cartao['vencimento_fatura']}\n"
            resposta += f"• Status: {dados_cartao['status_fatura']}"
            return {"response": resposta}
        else:
            return {"response": "Não encontrei seus dados do cartão. Verifique se seu cadastro foi completado corretamente."}
    
    # ========================================
    # SISTEMA DE RESPOSTAS GERAIS (CSV/JSON)
    # ========================================
    
    # Variáveis para encontrar melhor correspondência
    melhor_correspondencia = None
    melhor_categoria = None
    
    # Procurar correspondência exata ou parcial nas perguntas cadastradas
    for categoria, perguntas in perguntas_por_categoria.items():
        for pergunta in perguntas:
            # Verificar correspondência exata
            if mensagem_usuario == pergunta:
                melhor_categoria = categoria
                melhor_correspondencia = pergunta
                break
            # Verificar correspondência parcial
            elif pergunta in mensagem_usuario or mensagem_usuario in pergunta:
                if melhor_correspondencia is None or len(pergunta) < len(melhor_correspondencia):
                    melhor_categoria = categoria
                    melhor_correspondencia = pergunta
    
    # Se encontrou categoria correspondente, retornar resposta do JSON
    if melhor_categoria and melhor_categoria in respostas:
        return {"response": respostas[melhor_categoria]}
    
    # Verificar se é saudação e retornar resposta apropriada
    saudacoes = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "tudo bem", "ajuda", "ajudar"]
    if any(saudacao in mensagem_usuario for saudacao in saudacoes):
        return {"response": "Olá! Sou seu assistente de cartão de crédito. Posso ajudar com faturas, extrato, limite, cartão e outros serviços. No que posso ajudar?"}
    
    # Resposta padrão para mensagens não reconhecidas (usando JSON)
    if "default" in respostas:
        return {"response": respostas["default"]}
    else:
        return {"response": "Entendi sua dúvida. Para informações mais detalhadas sobre seu cartão, sugiro verificar as opções de Fatura, Extrato, Limite ou Cartão. Posso ajudar com algo mais específico?"}

# ========================================
# BLOCO: CADASTRO DE CLIENTES (LEGADO)
# ========================================
@app.route("/cadastrar_cliente", methods=["POST"])
@login_requerido
def cadastrar_cliente():
    """
    Rota legada para cadastrar informações de cliente e cartão
    Mantida para compatibilidade com sistema existente
    Requer que usuário esteja autenticado
    """
    # Obter dados do formulário de cliente
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    email = request.form["email"]
    telefone = request.form["telefone"]
    numero_cartao = request.form["numero_cartao"]
    limite_cartao = request.form["limite_cartao"]
    valor_fatura = request.form["valor_fatura"]
    vencimento_fatura = request.form["vencimento_fatura"]
    status_fatura = request.form["status_fatura"]

    # Conectar ao banco de dados para salvar cliente
    conexao = sqlite3.connect("chatbot.db")
    cursor = conexao.cursor()

    try:
        # Inserir dados do cliente na tabela de clientes
        cursor.execute("""
        INSERT INTO clientes (nome, cpf, email, telefone, numero_cartao, limite_cartao, valor_fatura, vencimento_fatura, status_fatura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, email, telefone, numero_cartao, limite_cartao, valor_fatura, vencimento_fatura, status_fatura))

        conexao.commit()
    except Exception as erro:
        # Tratar erro de duplicidade de CPF
        return "Erro: CPF já cadastrado!"
    finally:
        conexao.close()

    # Redirecionar para página inicial após cadastro
    return redirect("/")

# ========================================
# BLOCO: INICIALIZAÇÃO DO SERVIDOR
# ========================================
if __name__ == "__main__":
    """
    Ponto de entrada principal da aplicação
    Inicializa o banco de dados e inicia o servidor Flask
    """
    print(" Iniciando servidor do Chatbot de Cartão de Crédito...")
    print(" Carregando dados de perguntas e respostas...")
    
    # Inicializar banco de dados
    init_db()
    
    print(" Servidor pronto! Acesse http://localhost:5000")
    print(" Use Ctrl+C para parar o servidor")
    
    # Iniciar servidor Flask em modo debug
    app.run(debug=True)