# Pizzelato Gestor Bot

## Descrição

Bot do Telegram para gestão financeira da Pizzelato Pizza Cone. Permite acompanhar vendas, despesas, estoque, pedidos, afiliados e muito mais diretamente pelo Telegram.

## Funcionalidades

### 💰 Financeiro
- `/caixa` - Ver saldo do caixa do dia
- `/vendas` - Resumo de vendas (hoje e semana)
- `/despesas` - Ver despesas do mês
- `/dre` - Demonstrativo de Resultados
- `/resumo` - Resumo completo do dia
- `/meta` - Acompanhamento da meta mensal
- `/semana` - Resumo semanal
- `/lucro` - Ver lucro do dia

### 🍕 Cardápio
- `/cardapio` - Ver cardápio completo
- `/produto [nome]` - Ver detalhes de um produto
- `/top` - Produtos mais vendidos
- `/novo_produto` - Cadastrar novo produto

### 🛵 Cozinha e Pedidos
- `/pedidos` - Ver pedidos pendentes
- `/pedido [id]` - Ver detalhes de um pedido
- `/estoque` - Status do estoque
- `/alerta_estoque` - Alertas de estoque crítico
- `/cozinha_status` - Status da cozinha

### 🤝 Afiliados
- `/afiliados` - Lista de afiliados
- `/comissoes` - Ver comissões do mês
- `/novo_afiliado` - Cadastrar novo afiliado
- `/afiliado [nome]` - Ver detalhes de um afiliado

## Requisitos

- Python 3.10+
- Conta no Telegram
- Credenciais do Firebase (do seu projeto Pizzelato)

## Instalação Local

### 1. Clone ou baixe o projeto

```bash
git clone <seu-repositorio>
cd telegram-bot
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Windows (PowerShell)
$env:TELEGRAM_BOT_TOKEN = "8586185192:AAEN2tR4lHNXpZJEqbqLnCZAd8D-huwsrxY"
$env:FIREBASE_CREDENTIALS_JSON = '{"type":"service_account",...}'

# Linux/Mac
export TELEGRAM_BOT_TOKEN="8586185192:AAEN2tR4lHNXpZJEqbqLnCZAd8D-huwsrxY"
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### 5. Execute o bot

```bash
python bot.py
```

## Configuração do Firebase

### 1. Obter as credenciais

1. Acesse o [Firebase Console](https://console.firebase.google.com)
2. Selecione seu projeto Pizzelato
3. Vá em **Configurações do Projeto** > **Contas de serviço**
4. Clique em **Gerar nova chave privada**
5. Salve o arquivo JSON

### 2. Converter para variável de ambiente

```python
# Uma linha (Linux/Mac)
cat firebase-credentials.json | tr -d '\n'

# PowerShell
(Get-Content firebase-credentials.json -Raw).Replace("`n","").Replace("`r","")
```

Copie o resultado e configure como `FIREBASE_CREDENTIALS_JSON`.

## Deploy na nuvem

### Railway (Recomendado)

1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Adicione as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `FIREBASE_CREDENTIALS_JSON`
4. Railway detectará automaticamente o Python
5. O bot estará online 24/7

### Render

1. Acesse [render.com](https://render.com)
2. Crie um novo **Web Service**
3. Conecte ao GitHub
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Adicione as variáveis de ambiente

### Heroku

1. Acesse [heroku.com](https://heroku.com)
2. Crie novo app
3. Configure Dyno como **Worker** (não Web)
4. Adicione variáveis de ambiente

## Estrutura do Projeto

```
telegram-bot/
├── bot.py              # Arquivo principal do bot
├── config.py           # Configurações e constantes
├── firebase_client.py  # Conexão com Firebase
├── requirements.txt    # Dependências Python
├── handlers/
│   ├── __init__.py
│   ├── financeiro.py   # Comandos financeiros
│   ├── cardapio.py     # Comandos de cardápio
│   ├── cozinha.py      # Comandos de cozinha
│   └── afiliados.py    # Comandos de afiliados
└── railway.json       # Configuração Railway
```

## Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Menu principal |
| `/caixa` | Ver caixa do dia |
| `/vendas` | Resumo de vendas |
| `/despesas` | Despesas do mês |
| `/dre` | Demonstrativo de resultados |
| `/resumo` | Resumo completo do dia |
| `/meta` | Progresso da meta mensal |
| `/semana` | Resumo semanal |
| `/lucro` | Lucro do dia |
| `/cardapio` | Ver cardápio |
| `/produto` | Detalhes de produto |
| `/top` | Top produtos |
| `/pedidos` | Pedidos pendentes |
| `/estoque` | Status do estoque |
| `/afiliados` | Lista de afiliados |
| `/comissoes` | Comissões do mês |
| `/ajuda` | Ver todos os comandos |

## Solução de Problemas

### Bot não responde

1. Verifique se o token está correto
2. Confirme que o bot está ativo no @BotFather
3. Verifique os logs no console

### Erro de Firebase

1. Verifique se as credenciais estão corretas
2. Confirme que o projeto existe no Firebase
3. Verifique se a variável `FIREBASE_CREDENTIALS_JSON` está formatada corretamente (JSON válido em uma linha)

### Erro de importação

```bash
pip install --upgrade -r requirements.txt
```

## Suporte

Para dúvidas ou problemas, entre em contato.

## Licença

Uso interno - Pizzelato Pizza Cone
