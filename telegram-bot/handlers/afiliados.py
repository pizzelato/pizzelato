"""
Pizzelato Telegram Bot - Handlers de Afiliados
Gerencia comandos relacionados a afiliados
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import config
from firebase_client import get_afiliados, get_db

# ═══════════════════════════════════════════════════════
# COMANDO: /afiliados
# ═══════════════════════════════════════════════════════
async def cmd_afiliados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra lista de afiliados."""
    afiliados = get_afiliados()

    if not afiliados:
        msg = """
🤝 *Afiliados Pizzelato*

⚠️ Nenhum afiliado cadastrado.

_Use /novo_afiliado para adicionar._
"""
    else:
        ativos = [a for a in afiliados if a.get('ativo', True)]
        inativos = [a for a in afiliados if not a.get('ativo', True)]

        msg = f"""
🤝 *Afiliados Pizzelato*

📋 Total: {len(afiliados)}
🟢 Ativos: {len(ativos)}
🔴 Inativos: {len(inativos)}

━━━━━━━━━━━━━━━━━━━━━━
"""

        for af in ativos[:15]:  # Limitar a 15
            nome = af.get('nome', 'Afiliado')
            tel = af.get('telefone', '—')
            comissao = float(af.get('comissao', 0))
            msg += f"\n👤 *{nome}*\n"
            msg += f"📱 {tel}\n"
            msg += f"💰 Comissão: {comissao}%\n"

        if len(ativos) > 15:
            msg += f"\n... e mais {len(ativos) - 15} afiliados"

    keyboard = [
        [InlineKeyboardButton("➕ Novo Afiliado", callback_data="afi_novo")],
        [InlineKeyboardButton("💰 Ver Comissões", callback_data="afi_comissoes")],
        [InlineKeyboardButton("📋 Ver Inativos", callback_data="afi_inativos")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


# ═══════════════════════════════════════════════════════
# COMANDO: /comissoes
# ═══════════════════════════════════════════════════════
async def cmd_comissoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra comissões dos afiliados."""
    db = get_db()
    if not db:
        await update.message.reply_text("⚠️ Firebase não disponível.\n\n_Calcule manualmente as comissões._")
        return

    try:
        afiliados = get_afiliados()

        # Calcular comissões por afiliado
        hoje = datetime.now()
        mes_atual = hoje.strftime('%Y-%m')
        inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
        fim_mes = hoje.strftime('%Y-%m-%d')

        # Buscar vendas do mês
        vendas = db.collection('vendas')\
            .where('data', '>=', inicio_mes)\
            .where('data', '<=', fim_mes)\
            .stream()

        # Calcular comissões
        comissoes = {}
        for doc in vendas:
            venda = doc.to_dict()
            afiliado = venda.get('afiliado', '')
            if afiliado:
                total = float(venda.get('total', 0))
                comissoes[afiliado] = comissoes.get(afiliado, 0) + total

        msg = f"""
💰 *Comissões do Mês*

📅 {hoje.strftime('%B de %Y')}

━━━━━━━━━━━━━━━━━━━━━━
"""

        total_comissoes = 0
        for af in afiliados:
            nome = af.get('nome', 'Afiliado')
            taxa = float(af.get('comissao', 0))

            if nome in comissoes:
                vendas_af = comissoes[nome]
                comissao_valor = vendas_af * (taxa / 100)
                total_comissoes += comissao_valor

                msg += f"\n👤 *{nome}*\n"
                msg += f"📦 Vendas: R$ {vendas_af:.2f}\n"
                msg += f"💰 Comissão ({taxa}%): *R$ {comissao_valor:.2f}*\n"

        if not comissoes:
            msg += "\n⚠️ Nenhuma venda vinculada a afiliados este mês."

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━

💵 *TOTAL DE COMISSÕES:* R$ {total_comissoes:.2f}
"""

        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao calcular comissões: {e}")


# ═══════════════════════════════════════════════════════
# COMANDO: /novo_afiliado
# ═══════════════════════════════════════════════════════
async def cmd_novo_afiliado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instruções para cadastrar novo afiliado."""
    msg = """
➕ *Cadastrar Novo Afiliado*

📝 *Use o formato:*
```
/novo_afiliado
Nome: [nome completo]
Telefone: [número]
Comissão: [%]
```

📱 *Exemplo:*
`/novo_afiliado Nome: João Silva Telefone: 79999998888 Comissão: 10`

💡 *Ou cadastre diretamente pelo painel web.*
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /afiliado_detalhe
# ═══════════════════════════════════════════════════════
async def cmd_afiliado_detalhe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra detalhes de um afiliado."""
    if not context.args:
        await update.message.reply_text(
            "📋 Use: /afiliado <nome>\n\nExemplo: /afiliado João Silva"
        )
        return

    nome_busca = ' '.join(context.args)
    afiliados = get_afiliados()

    # Buscar afiliado
    encontrado = None
    for af in afiliados:
        if nome_busca.lower() in af.get('nome', '').lower():
            encontrado = af
            break

    if not encontrado:
        await update.message.reply_text(f"❌ Afiliado '{nome_busca}' não encontrado.")
        return

    nome = encontrado.get('nome', 'Afiliado')
    tel = encontrado.get('telefone', '—')
    comissao = float(encontrado.get('comissao', 0))
    ativo = "🟢 Ativo" if encontrado.get('ativo', True) else "🔴 Inativo"
    criado = encontrado.get('criado_em', '—')

    # Calcular vendas do afiliado
    db = get_db()
    total_vendas = 0

    if db:
        try:
            vendas = db.collection('vendas')\
                .where('afiliado', '==', nome)\
                .stream()

            for doc in vendas:
                total_vendas += float(doc.to_dict().get('total', 0))
        except:
            pass

    comissao_total = total_vendas * (comissao / 100)

    msg = f"""
🤝 *Afiliado: {nome}*

📱 Telefone: {tel}
💰 Comissão: {comissao}%
{status}

📅 Cadastrado em: {criado}

━━━━━━━━━━━━━━━━━━━━━━

📊 *ESTATÍSTICAS*
📦 Total em vendas: R$ {total_vendas:.2f}
💵 Comissão total: R$ {comissao_total:.2f}
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# CALLBACK: Comissões
# ═══════════════════════════════════════════════════════
async def callback_comissoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para ver comissões detalhadas."""
    query = update.callback_query
    await query.answer()

    db = get_db()
    if not db:
        await query.edit_message_text("⚠️ Firebase não disponível.")
        return

    try:
        afiliados = get_afiliados()
        hoje = datetime.now()
        mes = hoje.strftime('%Y-%m')

        msg = f"💰 *Comissões - {hoje.strftime('%B %Y')}*\n\n"

        total_geral = 0
        for af in afiliados:
            if not af.get('ativo', True):
                continue

            nome = af.get('nome', 'Afiliado')
            taxa = float(af.get('comissao', 0))

            # Buscar vendas do afiliado
            vendas = list(db.collection('vendas')
                .where('afiliado', '==', nome)
                .where('data', '>=', f'{mes}-01')
                .stream())

            total_vendas = sum(float(v.to_dict().get('total', 0)) for v in vendas)
            comissao = total_vendas * (taxa / 100)
            total_geral += comissao

            msg += f"👤 *{nome}*\n"
            msg += f"   Vendas: R$ {total_vendas:.2f} ({len(vendas)} pedidos)\n"
            msg += f"   Comissão: R$ {comissao:.2f}\n\n"

        msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💵 *TOTAL A PAGAR:* R$ {total_geral:.2f}"

        await query.edit_message_text(msg, parse_mode='Markdown')

    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {e}")
