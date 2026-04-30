# 💳 Chatbot de Cartão de Crédito - MVP Acadêmico

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-orange.svg)](https://sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Acadêmico-yellow.svg)]()

## 📋 Sobre o Projeto

Este é um **MVP (Produto Mínimo Viável) acadêmico** desenvolvido como parte de um projeto educacional. Trata-se de um chatbot fictício para atendimento ao cliente de cartão de crédito, demonstrando conceitos de autenticação, processamento de linguagem natural e integração com banco de dados.

> ⚠️ **IMPORTANTE: Este é um projeto educacional e fictício.** Todos os dados processados são para fins de demonstração. Não utilize dados reais ou sensíveis neste sistema.

## 🎯 Objetivo Acadêmico

Demonstrar os seguintes conceitos em desenvolvimento web:
- Sistema de autenticação e gerenciamento de sessões
- Integração com banco de dados SQLite
- Processamento de linguagem natural básico
- API RESTful para comunicação cliente-servidor
- Interface responsiva com HTML/CSS/JavaScript

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| **Python 3.x** | Linguagem principal |
| **Flask** | Framework web |
| **SQLite3** | Banco de dados local |
| **HTML5/CSS3** | Interface do usuário |
| **JavaScript** | Interatividade do chatbot |
| **CSV/JSON** | Armazenamento de conhecimento |

## 📁 Estrutura do Projeto

Chatbot/
├── chatbot.py # Aplicação principal
├── perguntas.csv # Base de conhecimento (perguntas)
├── respostas.json # Base de conhecimento (respostas)
├── .gitignore # Arquivos ignorados pelo Git
├── README.md # Documentação do projeto
├── templates/
│ ├── cadastro.html # Página de cadastro
│ ├── login.html # Página de login
│ └── chatbot.html # Interface do chatbot
└── static/
└── style.css # Estilos da aplicação


## ✨ Funcionalidades

### 🔐 Autenticação
- Cadastro completo de usuários
- Login com email e senha (criptografada com SHA256)
- Gerenciamento de sessões

### 💳 Dados do Cartão (Fictícios)
- Cadastro de informações de cartão de crédito
- Consulta de limite disponível
- Verificação de fatura atual
- Status e vencimento da fatura

### 🤖 Assistente Virtual
Responde perguntas sobre:
- **Fatura**: valor, vencimento, pagamento, parcelamento
- **Extrato**: compras recentes, lançamentos
- **Limite**: disponível, aumento, emergencial
- **Cartão**: bloqueio, segurança, internacional

## 🚀 Como Executar

### Pré-requisitos
pip install flask

Execução:
python chatbot.py

Acesso:
Acesse no navegador: http://localhost:5000

📚 Base de Conhecimento

Arquivo perguntas.csv
Define as perguntas que o chatbot reconhece, organizadas por categoria:
    Fatura (80+ perguntas)
    Extrato (70+ perguntas)
    Limite (70+ perguntas)
    Cartão (50+ perguntas)
    Cumprimentos (30+ perguntas)

Arquivo respostas.json
Define as respostas padrão para cada categoria.

## 🗺️ Rotas da API

**GET /** - Página inicial (sem autenticação)

**GET /cadastro** - Formulário de cadastro (sem autenticação)

**POST /cadastrar** - Processa cadastro (sem autenticação)

**GET /login** - Página de login (sem autenticação)

**POST /login** - Processa login (sem autenticação)

**GET /chatbot** - Interface do chatbot (requer autenticação)

**POST /api/chat** - API do chatbot (requer autenticação)

**GET /logout** - Encerra sessão (requer autenticação)

---

## 📊 Banco de Dados

### Tabela: usuarios

Campos:
- id (INTEGER) - Chave primária
- nome (TEXT) - Nome completo
- cpf (TEXT) - Único
- email (TEXT) - Único
- telefone (TEXT) - Telefone
- senha (TEXT) - Hash SHA256
- created_at (TIMESTAMP) - Data de criação

### Tabela: clientes

Campos:
- id (INTEGER) - Chave primária
- nome (TEXT) - Nome
- cpf (TEXT) - Único
- email (TEXT) - Email
- telefone (TEXT) - Telefone
- numero_cartao (TEXT) - Número fictício
- limite_cartao (TEXT) - Limite de crédito
- valor_fatura (TEXT) - Valor da fatura
- vencimento_fatura (TEXT) - Data de vencimento
- status_fatura (TEXT) - Status atual

---

## 🎨 Interface

- Design responsivo (mobile-first)
- Gradientes e sombras para UI moderna
- Animações de transição
- Atalhos rápidos para perguntas comuns
- Indicadores visuais de status

---

## 🧠 Lógica do Chatbot

**1. Reconhecimento de intenções**
- Identifica palavras-chave específicas
- Busca correspondência no CSV
- Fallback para respostas genéricas

**2. Dados personalizados**
- Busca informações do usuário logado
- Retorna dados específicos do cadastro

**3. Hierarquia de respostas**
- Dados pessoais (prioridade máxima)
- Correspondência CSV/JSON
- Palavras-chave de saudação
- Resposta padrão

---

## 📝 Exemplos de Uso

### Comandos que o chatbot reconhece:

- "Qual é o valor da minha fatura?"
- "Quero ver meu extrato"
- "meu limite"
- "meu cartão"
- "quando vence minha fatura?"
- "Como faço para pagar a fatura?"

### Respostas esperadas:

O chatbot retornará informações personalizadas baseadas no cadastro do usuário ou respostas genéricas da base de conhecimento.

---

## 🔒 Segurança (Para fins acadêmicos)

- Senhas criptografadas com SHA256
- Proteção contra SQL Injection (usando parâmetros)
- Sessões gerenciadas pelo Flask
- Decorador @login_requerido para rotas protegidas

### ⚠️ Para produção real, recomenda-se:

- Utilizar bcrypt ou Argon2 para senhas
- Implementar HTTPS obrigatório
- Usar variáveis de ambiente para chaves secretas
- Adicionar rate limiting
- Implementar logs de segurança

---

## 📈 Possíveis Melhorias Futuras

- [ ] Integração com IA/NLP avançado (NLTK, spaCy)
- [ ] API para dados reais de cartão
- [ ] Dashboards e análises de gastos
- [ ] Envio de notificações por e-mail/SMS
- [ ] Histórico de conversas do usuário
- [ ] Modo escuro
- [ ] Exportação de conversas em PDF
- [ ] Chatbot com reconhecimento de voz
- [ ] Suporte a múltiplos idiomas

---

## 👨‍🎓 Contexto Acadêmico

Este projeto foi desenvolvido para demonstrar:

- Desenvolvimento Web Full Stack
- Integração Frontend-Backend
- Gerenciamento de Estado e Sessões
- Arquitetura MVC
- Boas práticas de organização de código
- Documentação de projetos

---

## 🤝 Contribuições

Este é um projeto acadêmico, mas sugestões são bem-vindas:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

Este é um projeto educacional de código aberto para fins acadêmicos.

---

**Desenvolvido para fins educacionais** | © MVP Acadêmico - Chatbot de Cartão de Crédito
