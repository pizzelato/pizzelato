# 🍕 Pizzelato - Urban Pizza Cone

Sistema de gestão completo para a Pizzelato Pizza Cone, em Itabaiana, SE.

## 📱 Sistemas

### Sistema de Gestão Web
Acesse: **[pizzelato.github.io](https://pizzelato.github.io)** (link do GitHub Pages)

O sistema inclui:
- 💰 Dashboard financeiro
- 📊 Controle de vendas
- 📦 Gestão de estoque
- 🛵 Pedidos e entregas
- 👨‍🍳 Cozinha
- 🤝 Afiliados
- 📣 Campanhas e marketing
- 🧠 IA estratégica

### 🤖 Bot Telegram - Pizzelato Gestor

Bot de gestão financeira via Telegram.

**Acesse:** [@Pizzelato_gestor_bot](https://t.me/Pizzelato_gestor_bot)

#### Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Menu principal |
| `/caixa` | Saldo do caixa do dia |
| `/vendas` | Vendas de hoje e semana |
| `/dre` | Demonstrativo de resultados |
| `/despesas` | Despesas do mês |
| `/resumo` | Resumo completo do dia |
| `/meta` | Progresso da meta mensal |
| `/semana` | Resumo semanal |
| `/cardapio` | Ver produtos do cardápio |
| `/pedidos` | Pedidos pendentes |
| `/estoque` | Status do estoque |
| `/afiliados` | Lista de afiliados |
| `/comissoes` | Comissões do mês |
| `/ajuda` | Todos os comandos |

#### Instalação do Bot

```bash
# Entre na pasta do bot
cd telegram-bot

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
export TELEGRAM_BOT_TOKEN="seu_token_aqui"
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Execute
python bot.py
```

## 🚀 Deploy do Bot

### Railway (Recomendado)
1. Acesse [railway.app](https://railway.app)
2. Conecte este repositório
3. Configure as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `FIREBASE_CREDENTIALS_JSON`
4. Deploy automático!

## 📂 Estrutura

```
pizzelato/
├── index.html              # Sistema de gestão principal
├── cozinha.html            # Tela da cozinha
├── Pizzelato_Cardapio.html # Cardápio online
├── rastreio.html          # Rastreamento
├── telegram-bot/          # Bot Telegram
│   ├── bot.py
│   ├── config.py
│   ├── firebase_client.py
│   ├── requirements.txt
│   ├── handlers/
│   │   ├── financeiro.py
│   │   ├── cardapio.py
│   │   ├── cozinha.py
│   │   └── afiliados.py
│   └── README.md
└── README.md
```

## 🍕 Sobre a Pizzelato

Urban Pizza Cone - Itabaiana, SE

- Pizza no cone - prática e deliciosa!
- Sistema de delivery e retira
- Cardápio online com pedidos via WhatsApp
