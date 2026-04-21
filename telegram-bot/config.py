"""
Pizzelato Telegram Bot - Configurações
Gestor Financeiro da Pizzelato Pizza Cone
"""
import os

# ═══════════════════════════════════════════════════════
# TOKEN DO TELEGRAM BOT
# ═══════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8586185192:AAEN2tR4lHNXpZJEqbqLnCZAd8D-huwsrxY"

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES DO BOT
# ═══════════════════════════════════════════════════════
BOT_NAME = "Pizzelato Gestor"
ADMIN_CHAT_ID = None  # Será definido automaticamente quando o admin iniciar o bot

# ═══════════════════════════════════════════════════════
# CATEGORIAS DE DESPESAS
# ═══════════════════════════════════════════════════════
CATEGORIAS_DESPESAS = [
    "🛒 Ingredientes",
    "💡 Energia",
    "💧 Água",
    "📦 Embalagens",
    "🛵 Entregador",
    "👨‍🍳 Salários",
    "📱 Marketing",
    "🔧 Manutenção",
    "📄 Impostos",
    "🏠 Aluguel",
    "📦 Revenda",
    "📋 Outros"
]

# ═══════════════════════════════════════════════════════
# CANAIS DE VENDA
# ═══════════════════════════════════════════════════════
CANAIS_VENDA = [
    "App (Compre Sem Fila)",
    "WhatsApp",
    "Instagram",
    "Balcão",
    "Múltiplos"
]

# ═══════════════════════════════════════════════════════
# FORMAS DE PAGAMENTO
# ═══════════════════════════════════════════════════════
FORMAS_PAGAMENTO = [
    "PIX",
    "Dinheiro",
    "Débito",
    "Crédito"
]

# ═══════════════════════════════════════════════════════
# CATEGORIAS DE PRODUTOS
# ═══════════════════════════════════════════════════════
CATEGORIAS_PRODUTOS = [
    "✨ Assinatura",
    "⭐ Premium",
    "🍕 Tradicional",
    "🍫 Doce",
    "🥤 Bebida",
    "➕ Extra"
]

# ═══════════════════════════════════════════════════════
# EMOJIS E CORES
# ═══════════════════════════════════════════════════════
EMOJI_SUCESSO = "✅"
EMOJI_ERRO = "❌"
EMOJI_ALERTA = "⚠️"
EMOJI_DINHEIRO = "💰"
EMOJI_CAIXA = "💵"
EMOJI_VENDA = "🍕"
EMOJI_ESTOQUE = "📦"
EMOJI_CLIENTE = "👥"
EMOJI_CAMPAINHA = "📣"
EMOJI_RELATORIO = "📊"
EMOJI_FOGUETE = "🚀"

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES FIREBASE
# ═══════════════════════════════════════════════════════
# Para usar, você precisa das credenciais do Firebase
# Cole o conteúdo JSON no Railway/Render como variável de ambiente
# FIREBASE_CREDENTIALS_JSON

def get_firebase_credentials():
    """Obtém credenciais do Firebase de variável de ambiente."""
    import json
    creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON', '{}')
    try:
        return json.loads(creds_json)
    except:
        return None
