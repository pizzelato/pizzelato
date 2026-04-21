"""
Pizzelato Telegram Bot - Handlers de Cozinha e Operação
Gerencia comandos relacionados a cozinha e pedidos
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import config
from firebase_client import get_pedidos_pendentes, get_db, get_estoque

# ═══════════════════════════════════════════════════════
# COMANDO: /pedidos
# ═══════════════════════════════════════════════════════
async def cmd_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra pedidos pendentes."""
    pedidos = get_pedidos_pendentes()

    if not pedidos:
        msg = """
🛵 *Pedidos Pendentes*

✅ Nenhum pedido pendente no momento!

_Todos os pedidos foram atendidos._
"""
    else:
        msg = f"""
🛵 *Pedidos Pendentes*

📋 *Total:* {len(pedidos)} pedido(s)

━━━━━━━━━━━━━━━━━━━━━━
"""

        # Agrupar por status
        urgente = [p for p in pedidos if p.get('urgente')]
        normais = [p for p in pedidos if not p.get('urgente')]

        if urgente:
            msg += "\n🔥 *URGENTES*\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
            for p in urgente:
                cliente = p.get('cliente', 'Cliente')
                hora = p.get('hora', '--:--')
                itens = p.get('itens', [])
                msg += f"\n⚡ Pedido #{p.get('id', '')[:8]}\n"
                msg += f"👤 {cliente}\n"
                msg += f"🕐 {hora}\n"
                msg += f"📦 {len(itens)} item(s)\n"

        if normais:
            msg += "\n📋 *NORMAIS*\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
            for p in normais[:10]:  # Limitar a 10
                cliente = p.get('cliente', 'Cliente')
                hora = p.get('hora', '--:--')
                itens = p.get('itens', [])
                msg += f"\n📦 Pedido #{p.get('id', '')[:8]}\n"
                msg += f"👤 {cliente}\n"
                msg += f"🕐 {hora}\n"
                msg += f"📦 {len(itens)} item(s)\n"

        if len(normais) > 10:
            msg += f"\n... e mais {len(normais) - 10} pedidos"

    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="pedidos_refresh")],
        [InlineKeyboardButton("📋 Ver Todos", callback_data="pedidos_todos")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


# ═══════════════════════════════════════════════════════
# COMANDO: /pedido_detalhe
# ═══════════════════════════════════════════════════════
async def cmd_pedido_detalhe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra detalhes de um pedido específico."""
    if not context.args:
        await update.message.reply_text(
            "📋 Use: /pedido <ID do pedido>\n\n_O ID aparece na mensagem do pedido (/pedidos)_"
        )
        return

    pedido_id = context.args[0]
    db = get_db()

    if not db:
        await update.message.reply_text("⚠️ Firebase não disponível.")
        return

    try:
        doc = db.collection('pedidos').document(pedido_id).get()

        if not doc.exists:
            await update.message.reply_text(f"❌ Pedido #{pedido_id} não encontrado.")
            return

        pedido = doc.to_dict()
        cliente = pedido.get('cliente', 'Cliente')
        status = pedido.get('status', 'pendente')
        hora = pedido.get('hora', '--:--')
        itens = pedido.get('itens', [])
        total = float(pedido.get('total', 0))
        pagto = pedido.get('pagamento', 'PIX')

        status_emoji = {
            'pendente': '⏳',
            'preparando': '👨‍🍳',
            'pronto': '✅',
            'entregue': '🏠',
            'cancelado': '❌'
        }

        msg = f"""
🛵 *Pedido #{pedido_id[:8]}*

📋 Status: {status_emoji.get(status, '❓')} *{status.upper()}*
👤 Cliente: *{cliente}*
🕐 Hora: {hora}
💳 Pagamento: {pagto}
💰 Total: R$ {total:.2f}

━━━━━━━━━━━━━━━━━━━━━━

📦 *ITENS:*
"""

        for i, item in enumerate(itens, 1):
            nome = item.get('nome', 'Item')
            qtd = item.get('qty', 1)
            obs = item.get('obs', '')
            msg += f"\n{i}. {nome} x{qtd}"
            if obs:
                msg += f"\n   📝 {obs}"

        # Botões de ação
        keyboard = [
            [
                InlineKeyboardButton("👨‍🍳 Preparando", callback_data=f"pedido_preparando_{pedido_id}"),
                InlineKeyboardButton("✅ Pronto", callback_data=f"pedido_pronto_{pedido_id}"),
            ],
            [
                InlineKeyboardButton("🏠 Entregue", callback_data=f"pedido_entregue_{pedido_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"pedido_cancela_{pedido_id}"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")


# ═══════════════════════════════════════════════════════
# COMANDO: /estoque
# ═══════════════════════════════════════════════════════
async def cmd_estoque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra status do estoque."""
    estoque = get_estoque()

    if not estoque:
        msg = """
📦 *Status do Estoque*

⚠️ Nenhum item no estoque.

_Use o painel web para gerenciar estoque._
"""
    else:
        # Agrupar por status
        criticos = []
        atencao = []
        ok = []

        for item in estoque:
            saldo = float(item.get('saldo', 0))
            alerta = float(item.get('alerta', 0))
            nome = item.get('nome', 'Item')

            if saldo <= 0:
                criticos.append(item)
            elif saldo <= alerta:
                atencao.append(item)
            else:
                ok.append(item)

        msg = f"""
📦 *Status do Estoque*

📋 *Total de itens:* {len(estoque)}
🟢 OK: {len(ok)}
🟡 Atenção: {len(atencao)}
🔴 Crítico: {len(criticos)}

━━━━━━━━━━━━━━━━━━━━━━
"""

        if criticos:
            msg += "\n🔴 *CRÍTICO - REABASTECER JÁ*\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
            for item in criticos:
                nome = item.get('nome', 'Item')
                saldo = float(item.get('saldo', 0))
                msg += f"⚠️ {nome}: {saldo} {item.get('unidade', 'un')}\n"

        if atencao:
            msg += "\n🟡 *ATENÇÃO - PRÓXIMO DO MÍNIMO*\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
            for item in atencao[:5]:
                nome = item.get('nome', 'Item')
                saldo = float(item.get('saldo', 0))
                alerta = float(item.get('alerta', 0))
                msg += f"⚡ {nome}: {saldo}/{alerta} {item.get('unidade', 'un')}\n"

        if criticos or atencao:
            msg += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "_Use /compras para ver sugestão de compras._"

    keyboard = [
        [InlineKeyboardButton("📦 Ver Estoque Completo", callback_data="estoque_completo")],
        [InlineKeyboardButton("🛒 Sugestão de Compras", callback_data="compras_sugestao")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


# ═══════════════════════════════════════════════════════
# COMANDO: /alerta_estoque
# ═══════════════════════════════════════════════════════
async def cmd_alerta_estoque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia alertas de estoque crítico."""
    estoque = get_estoque()
    criticos = []

    for item in estoque:
        saldo = float(item.get('saldo', 0))
        if saldo <= 0:
            criticos.append(item)

    if not criticos:
        await update.message.reply_text(
            "📦 *Alertas de Estoque*\n\n✅ Nenhum item crítico no momento!"
        )
        return

    msg = f"""
🔔 *ALERTAS DE ESTOQUE CRÍTICO*

⚠️ {len(criticos)} item(s) precisam de reposição:

━━━━━━━━━━━━━━━━━━━━━━
"""

    for item in criticos:
        nome = item.get('nome', 'Item')
        msg += f"⚠️ *{nome}*\n"

    msg += """
━━━━━━━━━━━━━━━━━━━━━━

💡 Ações sugeridas:
• /compras - Ver sugestão de compras
• /entradas - Registrar entrada de estoque
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /cozinha_status
# ═══════════════════════════════════════════════════════
async def cmd_cozinha_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra status da cozinha."""
    db = get_db()
    if not db:
        await update.message.reply_text("⚠️ Firebase não disponível.")
        return

    try:
        # Buscar pedidos por status
        preparando = db.collection('pedidos').where('status', '==', 'preparando').stream()
        pronto = db.collection('pedidos').where('status', '==', 'pronto').stream()

        preparando_list = [doc.to_dict() for doc in preparando]
        pronto_list = [doc.to_dict() for doc in pronto]

        msg = f"""
👨‍🍳 *Status da Cozinha*

📋 *Em preparo:* {len(preparando_list)}
📋 *Prontos:* {len(pronto_list)}

━━━━━━━━━━━━━━━━━━━━━━
"""

        if preparando_list:
            msg += "\n🔄 *EM PREPARO*\n"
            for p in preparando_list[:5]:
                hora = p.get('hora', '--:--')
                cliente = p.get('cliente', 'Cliente')
                msg += f"⏳ {cliente} - {hora}\n"

        if pronto_list:
            msg += "\n✅ *PRONTOS PARA ENTREGA*\n"
            for p in pronto_list[:5]:
                hora = p.get('hora', '--:--')
                cliente = p.get('cliente', 'Cliente')
                msg += f"✅ {cliente} - {hora}\n"

        msg += """
━━━━━━━━━━━━━━━━━━━━━━

_Use /pedidos para gerenciar pedidos._
"""

        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")
