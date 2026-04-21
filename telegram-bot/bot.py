"""
Pizzelato Telegram Bot - Gestor Financeiro
Bot principal que gerencia comandos e callbacks

Autor: Pizzelato Pizza Cone
Versão: 1.0.0
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

import config
from handlers import financeiro, cardapio, cozinha, afiliados, ai_advisor

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DO LOGGING
# ═══════════════════════════════════════════════════════
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# HANDLERS DE COMANDOS
# ═══════════════════════════════════════════════════════

async def cmd_lucro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando rápido para ver lucro do dia."""
    from firebase_client import get_vendas_hoje

    vendas = get_vendas_hoje()
    fat = sum(float(v.get('total', 0)) for v in vendas)
    luc = sum(float(v.get('lucro', 0)) for v in vendas)
    ped = len(vendas)
    margem = (luc / fat * 100) if fat > 0 else 0

    emoji = "🟢" if margem >= 30 else "🟡" if margem >= 20 else "🔴"

    msg = f"""
💰 *Lucro do Dia*

📅 {update.effective_date.strftime('%d/%m/%Y') if update.effective_date else 'Hoje'}

🍕 Pedidos: *{ped}*
💵 Faturamento: R$ {fat:.2f}
✅ Lucro: R$ {luc:.2f}
📊 Margem: {margem:.1f}%

{emoji} *Situação:* {"Excelente!" if margem >= 30 else "Bom" if margem >= 20 else "Atenção"}
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


async def cmd_alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurar alertas automáticos."""
    msg = """
🔔 *Configurar Alertas*

Escolha quais alertas você quer receber:

━━━━━━━━━━━━━━━━━━━━━━

🟢 *Alertas de Estoque*
Receba alertas quando ingredientes acabarem.

🟡 *Alertas de Meta*
Notificação quando estiver abaixo da meta.

🔴 *Alertas de Gastos*
Avisa quando despesas forem altas.

📊 *Resumo Diário*
Receba resumo todo dia às 22h.

━━━━━━━━━━━━━━━━━━━━━━

_Esta função será implementada em breve._
_Use /resumo para ver manualmente._
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia todos os callbacks dos botões."""
    query = update.callback_query

    if not query:
        return

    await query.answer()

    data = query.data

    try:
        # ═══ FINANCEIRO ═══

        if data == "fin_caixa":
            await financeiro.cmd_caixa(update, context)

        elif data == "fin_vendas":
            await financeiro.cmd_vendas(update, context)

        elif data == "fin_dre":
            await financeiro.cmd_dre(update, context)

        elif data == "fin_despesas":
            await financeiro.cmd_despesas(update, context)

        # ═══ CARDÁPIO ═══

        elif data == "op_cardapio":
            await cardapio.cmd_cardapio(update, context)

        elif data.startswith("cardapio_cat_"):
            await cardapio.callback_cardapio_cat(update, context)

        elif data == "cardapio_todos":
            await cardapio.cmd_cardapio(update, context)

        # ═══ COZINHA ═══

        elif data == "op_estoque":
            await cozinha.cmd_estoque(update, context)

        elif data == "pedidos_refresh":
            await cozinha.cmd_pedidos(update, context)

        elif data == "pedidos_todos":
            await cozinha.cmd_pedidos(update, context)

        elif data.startswith("pedido_"):
            await handle_pedido_callback(update, context, data)

        # ═══ AFILIADOS ═══

        elif data == "afi_lista":
            await afiliados.cmd_afiliados(update, context)

        elif data == "afi_comissoes":
            await afiliados.callback_comissoes(update, context)

        elif data == "afi_novo":
            await afiliados.cmd_novo_afiliado(update, context)

        elif data == "afi_inativos":
            await afiliados.cmd_afiliados(update, context)

        # ═══ RESUMO ═══

        elif data == "resumo_dia":
            await financeiro.cmd_resumo(update, context)

        # ═══ AI ADVISOR ═══

        elif data == "ai_insights":
            await ai_advisor.cmd_insights(update, context)

        elif data == "ai_campanha":
            await ai_advisor.cmd_campanha(update, context)

        elif data == "ai_dicas":
            await ai_advisor.cmd_dica_venda(update, context)

        elif data == "ai_foto":
            await ai_advisor.cmd_gerar_foto(update, context)

        elif data == "ai_relatorio":
            await ai_advisor.cmd_daily_report(update, context)

    except Exception as e:
        logger.error(f"Erro no callback: {e}")
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def handle_pedido_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Gerencia callbacks de pedidos."""
    from firebase_client import get_db

    query = update.callback_query
    parts = data.split('_')
    action = parts[1]
    pedido_id = '_'.join(parts[2:])

    db = get_db()
    if not db:
        await query.answer_text("⚠️ Firebase não disponível.")
        return

    status_map = {
        'preparando': 'preparando',
        'pronto': 'pronto',
        'entregue': 'entregue',
        'cancela': 'cancelado'
    }

    if action in status_map:
        try:
            db.collection('pedidos').document(pedido_id).update({
                'status': status_map[action],
                'updated_at': datetime.now().isoformat()
            })

            status_text = {
                'preparando': '👨‍🍳 Em preparo',
                'pronto': '✅ Pronto',
                'entregue': '🏠 Entregue',
                'cancelado': '❌ Cancelado'
            }

            await query.answer_text(f"✅ Pedido atualizado: {status_text[action]}")

            # Atualizar mensagem
            await cozinha.cmd_pedidos(update, context)

        except Exception as e:
            await query.answer_text(f"❌ Erro: {e}")


# ═══════════════════════════════════════════════════════
# MESSAGE HANDLER (Fallback)
# ═══════════════════════════════════════════════════════

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a comandos não reconhecidos."""
    await update.message.reply_text(
        "❓ Comando não reconhecido.\n\n"
        "Use /ajuda para ver todos os comandos disponíveis."
    )


# ═══════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """ Trata erros não esperados """
    logger.error(f"Erro não tratado: {context.error}")


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    """Função principal que inicia o bot."""

    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║     🍕 PIZZELATO GESTOR BOT 🍕                   ║
    ║                                                  ║
    ║     Gestor Financeiro Telegram                  ║
    ║     para Pizzelato Pizza Cone                    ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)

    # Criar aplicação
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # ═══ COMANDOS PRINCIPAIS ═══
    application.add_handler(CommandHandler("start", financeiro.cmd_start))
    application.add_handler(CommandHandler("ajuda", financeiro.cmd_ajuda))

    # ═══ FINANCEIRO ═══
    application.add_handler(CommandHandler("caixa", financeiro.cmd_caixa))
    application.add_handler(CommandHandler("vendas", financeiro.cmd_vendas))
    application.add_handler(CommandHandler("despesas", financeiro.cmd_despesas))
    application.add_handler(CommandHandler("dre", financeiro.cmd_dre))
    application.add_handler(CommandHandler("resumo", financeiro.cmd_resumo))
    application.add_handler(CommandHandler("meta", financeiro.cmd_meta))
    application.add_handler(CommandHandler("semana", financeiro.cmd_semana))
    application.add_handler(CommandHandler("lucro", cmd_lucro))

    # ═══ CARDÁPIO ═══
    application.add_handler(CommandHandler("cardapio", cardapio.cmd_cardapio))
    application.add_handler(CommandHandler("produto", cardapio.cmd_produto))
    application.add_handler(CommandHandler("top", cardapio.cmd_top))
    application.add_handler(CommandHandler("novo_produto", cardapio.cmd_novo_produto))

    # ═══ COZINHA ═══
    application.add_handler(CommandHandler("pedidos", cozinha.cmd_pedidos))
    application.add_handler(CommandHandler("pedido", cozinha.cmd_pedido_detalhe))
    application.add_handler(CommandHandler("estoque", cozinha.cmd_estoque))
    application.add_handler(CommandHandler("alerta_estoque", cozinha.cmd_alerta_estoque))
    application.add_handler(CommandHandler("cozinha_status", cozinha.cmd_cozinha_status))

    # ═══ AFILIADOS ═══
    application.add_handler(CommandHandler("afiliados", afiliados.cmd_afiliados))
    application.add_handler(CommandHandler("comissoes", afiliados.cmd_comissoes))
    application.add_handler(CommandHandler("novo_afiliado", afiliados.cmd_novo_afiliado))
    application.add_handler(CommandHandler("afiliado", afiliados.cmd_afiliado_detalhe))

    # ═══ AI ADVISOR ═══
    application.add_handler(CommandHandler("insights", ai_advisor.cmd_insights))
    application.add_handler(CommandHandler("campanha", ai_advisor.cmd_campanha))
    application.add_handler(CommandHandler("dica_venda", ai_advisor.cmd_dica_venda))
    application.add_handler(CommandHandler("dica_financeira", ai_advisor.cmd_dica_financeira))
    application.add_handler(CommandHandler("gerar_foto", ai_advisor.cmd_gerar_foto))
    application.add_handler(CommandHandler("relatorio", ai_advisor.cmd_daily_report))

    # ═══ CONFIG ═══
    application.add_handler(CommandHandler("alertas", cmd_alertas))

    # ═══ CALLBACKS ═══
    application.add_handler(CallbackQueryHandler(callback_handler))

    # ═══ FALLBACK ═══
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # ═══ ERROR HANDLER ═══
    application.add_error_handler(error_handler)

    # Iniciar bot
    print("🤖 Bot iniciado! Aguardando mensagens...")
    print("📱 Abra o Telegram e inicie uma conversa com @Pizzelato_gestor_bot")
    print()

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
