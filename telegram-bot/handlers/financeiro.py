"""
Pizzelato Telegram Bot - Handlers Financeiros
Gerencia comandos relacionados a finanças
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import config
from firebase_client import (
    get_db, get_vendas_hoje, get_vendas_periodo,
    get_despesas_mes, get_caixa_hoje, get_configuracoes
)

# ═══════════════════════════════════════════════════════
# COMANDO: /start
# ═══════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensagem inicial do bot."""
    user = update.effective_user

    # Salvar ID do admin
    if config.ADMIN_CHAT_ID is None:
        config.ADMIN_CHAT_ID = update.effective_chat.id

    bienvenida = f"""
🍕 *Bem-vindo ao Pizzelato Gestor!*

Olá, {user.first_name}! Sou seu *Gerente AI* da *Pizzelato Pizza Cone*.

🤖 *Sou seu empresário virtual!*

💰 *Financeiro*
├ /caixa - Ver saldo do caixa
├ /vendas - Resumo de vendas
├ /despesas - Suas despesas
├ /dre - Demonstrativo de resultados

📊 *Análises & AI*
├ /insights - Análise completa com IA
├ /campanha - Sugestões de campanhas
├ /relatorio - Relatório diário
├ /meta - Ver progresso da meta
├ /semana - Resumo semanal

💡 *Dicas & Fotos*
├ /dica_venda - Dicas para vender mais
├ /dica_financeira - Dicas financeiras
├ /gerar_foto - Criar imagem promocional

🍕 *Operação*
├ /cardapio - Ver cardápio
├ /pedidos - Pedidos pendentes
├ /estoque - Status do estoque

🤝 *Afiliados*
├ /afiliados - Lista de afiliados
├ /comissoes - Suas comissões

_Use os botões abaixo para navegação rápida:_
"""

    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Advisor", callback_data="ai_insights"),
            InlineKeyboardButton("🎯 Campanhas", callback_data="ai_campanha"),
        ],
        [
            InlineKeyboardButton("💰 Caixa", callback_data="fin_caixa"),
            InlineKeyboardButton("📊 Vendas", callback_data="fin_vendas"),
        ],
        [
            InlineKeyboardButton("📈 DRE", callback_data="fin_dre"),
            InlineKeyboardButton("📋 Despesas", callback_data="fin_despesas"),
        ],
        [
            InlineKeyboardButton("🍕 Cardápio", callback_data="op_cardapio"),
            InlineKeyboardButton("📦 Estoque", callback_data="op_estoque"),
        ],
        [
            InlineKeyboardButton("🤝 Afiliados", callback_data="afi_lista"),
            InlineKeyboardButton("📄 Resumo do Dia", callback_data="resumo_dia"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        bienvenida,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


# ═══════════════════════════════════════════════════════
# COMANDO: /caixa
# ═══════════════════════════════════════════════════════
async def cmd_caixa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra status do caixa."""
    vendas = get_vendas_hoje()
    caixa = get_caixa_hoje()

    if not vendas:
        msg = """
💵 *Caixa do Dia*

📅 *Data:* {data}

⚠️ Nenhuma venda registrada hoje.

_Habilite o Firebase para ver dados reais._
""".format(data=datetime.now().strftime('%d/%m/%Y'))
    else:
        total_faturamento = sum(float(v.get('total', 0)) for v in vendas)
        total_lucro = sum(float(v.get('lucro', 0)) for v in vendas)
        qtd_pedidos = len(vendas)
        ticket_medio = total_faturamento / qtd_pedidos if qtd_pedidos > 0 else 0

        msg = """
💵 *Caixa do Dia*

📅 *Data:* {data}
📍 *Status:* {"🟢 Aberto" if caixa else "🔴 Fechado"}

━━━━━━━━━━━━━━━━━━━━━━

🍕 *Vendas:*
├ Pedidos: *{pedidos}*
├ Faturamento: *R$ {fat:.2f}*
├ Lucro: *R$ {lucro:.2f}*
└ Ticket Médio: R$ {ticket:.2f}

💰 *Margem:* {margem:.1f}%

━━━━━━━━━━━━━━━━━━━━━━

_Calculando..._
""".format(
            data=datetime.now().strftime('%d/%m/%Y'),
            pedidos=qtd_pedidos,
            fat=total_faturamento,
            lucro=total_lucro,
            ticket=ticket_medio,
            margem=(total_lucro / total_faturamento * 100) if total_faturamento > 0 else 0
        )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /vendas
# ═══════════════════════════════════════════════════════
async def cmd_vendas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra resumo de vendas."""
    await update.message.reply_text("🔄 Buscando dados de vendas...")

    vendas_hoje = get_vendas_hoje()
    hoje = datetime.now()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
    fim_semana = hoje.strftime('%Y-%m-%d')

    vendas_semana = get_vendas_periodo(inicio_semana, fim_semana)

    # Vendas do dia
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas_hoje)
    luc_hoje = sum(float(v.get('lucro', 0)) for v in vendas_hoje)
    ped_hoje = len(vendas_hoje)

    # Vendas da semana
    fat_semana = sum(float(v.get('total', 0)) for v in vendas_semana)
    luc_semana = sum(float(v.get('lucro', 0)) for v in vendas_semana)
    ped_semana = len(vendas_semana)

    msg = """
🍕 *Resumo de Vendas*

━━━━━━━━━━━━━━━━━━━━━━

📅 *HOJE ({data_hoje})*
├ Pedidos: *{ped_h}*
├ Faturamento: *R$ {fat_h:.2f}*
└ Lucro: *R$ {luc_h:.2f}*

📅 *ESTA SEMANA*
├ Pedidos: *{ped_s}*
├ Faturamento: *R$ {fat_s:.2f}*
└ Lucro: *R$ {luc_s:.2f}*

━━━━━━━━━━━━━━━━━━━━━━

📊 *Média diária:* R$ {media:.2f}
🎯 *Meta diária:* R$ 200,00
""".format(
        data_hoje=hoje.strftime('%d/%m'),
        ped_h=ped_hoje,
        fat_h=fat_hoje,
        luc_h=luc_hoje,
        ped_s=ped_semana,
        fat_s=fat_semana,
        luc_s=luc_semana,
        media=fat_semana / hoje.weekday() if hoje.weekday() > 0 else fat_semana
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /despesas
# ═══════════════════════════════════════════════════════
async def cmd_despesas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra despesas do mês."""
    despesas = get_despesas_mes()

    if not despesas:
        msg = """
💸 *Despesas do Mês*

📅 *Período:* {mes}/{ano}

✅ Nenhuma despesa registrada este mês.
""".format(
            mes=datetime.now().strftime('%m'),
            ano=datetime.now().strftime('%Y')
        )
    else:
        total_despesas = sum(float(d.get('valor', 0)) for d in despesas)

        # Agrupar por categoria
        por_categoria = {}
        for d in despesas:
            cat = d.get('categoria', 'Outros')
            por_categoria[cat] = por_categoria.get(cat, 0) + float(d.get('valor', 0))

        cats_text = "\n".join([
            f"├ {cat}: *R$ {val:.2f}*"
            for cat, val in sorted(por_categoria.items(), key=lambda x: -x[1])
        ])

        msg = """
💸 *Despesas do Mês*

📅 *Período:* {mes}/{ano}
💰 *Total:* *R$ {total:.2f}*

━━━━━━━━━━━━━━━━━━━━━━

{categorias}

━━━━━━━━━━━━━━━━━━━━━━

_Use /add_despesa para registrar nova despesa_
""".format(
            mes=datetime.now().strftime('%m'),
            ano=datetime.now().strftime('%Y'),
            total=total_despesas,
            categorias=cats_text
        )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /dre
# ═══════════════════════════════════════════════════════
async def cmd_dre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demonstrativo de Resultados."""
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    fim_mes = hoje.strftime('%Y-%m-%d')

    vendas_mes = get_vendas_periodo(inicio_mes, fim_mes)
    despesas_mes = get_despesas_mes()
    config_sistema = get_configuracoes()

    # Calcular valores
    faturamento = sum(float(v.get('total', 0)) for v in vendas_mes)
    custo_produtos = sum(float(v.get('custo', 0)) for v in vendas_mes)
    taxa_app = sum(float(v.get('taxa_app', 0)) for v in vendas_mes)
    total_entregador = sum(float(v.get('entregador', 0)) for v in vendas_mes)
    marketing = sum(float(v.get('marketing', 0)) for v in vendas_mes)
    despesas_fixaso = sum(float(d.get('valor', 0)) for d in despesas_mes)

    lucro_bruto = faturamento - custo_produtos
    lucro_operacional = lucro_bruto - taxa_app - total_entregador - marketing
    lucro_liquido = lucro_operacional - despesas_fixaso

    margem = (lucro_liquido / faturamento * 100) if faturamento > 0 else 0

    msg = """
📊 *DRE - Demonstrativo de Resultados*

📅 *Período:* {mes}/{ano}
🏪 *Estabelecimento:* Pizzelato Pizza Cone

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *RECEITA BRUTA*
R$ {faturamento:>12.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 *(-) CUSTO DOS PRODUTOS*
R$ {custo:>12.2f}
margem sobre custo: {margem_custo:.1f}%

🛵 *(-) TAXA DE ENTREGA*
R$ {entregador:>12.2f}

📱 *(-) TAXA APP/CANAL*
R$ {taxa:>12.2f}

📣 *(-) MARKETING*
R$ {mkt:>12.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 *LUCRO OPERACIONAL*
R$ {lucro_op:>12.2f}
margem operacional: {margem_op:.1f}%

💸 *(-) DESPESAS FIXAS*
R$ {desp:>12.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *LUCRO LÍQUIDO*
R$ {lucro:>12.2f}
margem líquida: *{margem:.1f}%*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".format(
        mes=hoje.strftime('%m'),
        ano=hoje.strftime('%Y'),
        faturamento=faturamento,
        custo=custo_produtos,
        margem_custo=((faturamento - custo_produtos) / faturamento * 100) if faturamento > 0 else 0,
        entregador=total_entregador,
        taxa=taxa_app,
        mkt=marketing,
        lucro_op=lucro_operacional,
        margem_op=(lucro_operacional / faturamento * 100) if faturamento > 0 else 0,
        desp=despesas_fixaso,
        lucro=lucro_liquido,
        margem=margem
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /resumo
# ═══════════════════════════════════════════════════════
async def cmd_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resumo completo do dia."""
    vendas = get_vendas_hoje()
    despesas = get_despesas_mes()
    config_sistema = get_configuracoes()

    # Valores do dia
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas)
    luc_hoje = sum(float(v.get('lucro', 0)) for v in vendas)
    ped_hoje = len(vendas)
    ticket = fat_hoje / ped_hoje if ped_hoje > 0 else 0

    # Meta
    meta_mensal = float(config_sistema.get('meta_mensal', 6000))
    hoje = datetime.now()
    dias_uteis = hoje.day
    meta_dia = meta_mensal / dias_uteis if dias_uteis > 0 else 0
    progresso_meta = (fat_hoje / meta_dia * 100) if meta_dia > 0 else 0

    msg = """
📄 *Resumo do Dia*

📅 {data}
🏪 Pizzelato Pizza Cone

━━━━━━━━━━━━━━━━━━━━━━

🍕 *VENDAS*
├ Pedidos: *{ped}*
├ Faturamento: *R$ {fat:.2f}*
├ Lucro: *R$ {lucro:.2f}*
└ Ticket Médio: R$ {ticket:.2f}

💰 *MARGEM*
└ {margem:.1f}%

🎯 *META*
├ Progresso: {prog:.0f}%
├ Meta Dia: R$ {meta_dia:.2f}
└ Situação: {situacao}

━━━━━━━━━━━━━━━━━━━━━━
""".format(
        data=hoje.strftime('%d de %B de %Y'),
        ped=ped_hoje,
        fat=fat_hoje,
        lucro=luc_hoje,
        ticket=ticket,
        margem=(luc_hoje / fat_hoje * 100) if fat_hoje > 0 else 0,
        prog=progresso_meta,
        meta_dia=meta_dia,
        situacao="🟢 Dentro da meta" if progresso_meta >= 100 else "🟡 Abaixo da meta"
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /meta
# ═══════════════════════════════════════════════════════
async def cmd_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra progresso da meta mensal."""
    config_sistema = get_configuracoes()

    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    fim_mes = hoje.strftime('%Y-%m-%d')

    vendas_mes = get_vendas_periodo(inicio_mes, fim_mes)
    faturamento_mes = sum(float(v.get('total', 0)) for v in vendas_mes)
    lucro_mes = sum(float(v.get('lucro', 0)) for v in vendas_mes)

    meta_mensal = float(config_sistema.get('meta_mensal', 6000))
    progresso = (faturamento_mes / meta_mensal * 100) if meta_mensal > 0 else 0
    faltam = meta_mensal - faturamento_mes
    dias_restantes = 30 - hoje.day

    # Calcular média diária
    dias_passados = hoje.day
    media_dia = faturamento_mes / dias_passados if dias_passados > 0 else 0

    # Estimar fechamento
    projecao = media_dia * 30

    msg = """
🎯 *Acompanhamento de Meta*

📅 *Mês:* {mes}/{ano}
🏪 *Meta Mensal:* R$ {meta:.2f}

━━━━━━━━━━━━━━━━━━━━━━

📈 *REALIZADO ATÉ HOJE ({dias}° dia)*
├ Faturamento: *R$ {fat:.2f}*
├ Lucro: *R$ {lucro:.2f}*
└ Progresso: {barra} {prog:.0f}%

━━━━━━━━━━━━━━━━━━━━━━

📊 *ANÁLISE*
├ Média diária: R$ {media:.2f}
├ Projeção mês: R$ {proj:.2f}
├ Falta: R$ {falta:.2f}
└ Dias restantes: {dias_r}

━━━━━━━━━━━━━━━━━━━━━━

🎯 *SITUAÇÃO:* {situacao}
""".format(
        mes=hoje.strftime('%m'),
        ano=hoje.strftime('%Y'),
        meta=meta_mensal,
        dias=dias_passados,
        fat=faturamento_mes,
        lucro=lucro_mes,
        barra="█" * int(progresso / 5) + "░" * (20 - int(progresso / 5)),
        prog=progresso,
        media=media_dia,
        proj=projecao,
        falta=faltam if faltam > 0 else 0,
        dias_r=dias_restantes,
        situacao="🟢 Meta batida!" if progresso >= 100 else "🟡 Na trilha" if projecao >= meta_mensal else "🔴 Abaixo da meta"
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /semana
# ═══════════════════════════════════════════════════════
async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resumo semanal."""
    hoje = datetime.now()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
    fim_semana = hoje.strftime('%Y-%m-%d')

    vendas = get_vendas_periodo(inicio_semana, fim_semana)

    # Total da semana
    fat_semana = sum(float(v.get('total', 0)) for v in vendas)
    luc_semana = sum(float(v.get('lucro', 0)) for v in vendas)
    ped_semana = len(vendas)

    # Vendas por dia
    por_dia = {}
    for v in vendas:
        dia = v.get('data', '')
        por_dia[dia] = por_dia.get(dia, {'fat': 0, 'luc': 0, 'ped': 0})
        por_dia[dia]['fat'] += float(v.get('total', 0))
        por_dia[dia]['luc'] += float(v.get('lucro', 0))
        por_dia[dia]['ped'] += 1

    dias_text = "\n".join([
        f"├ {d[8:10]}/{d[5:7]}: *R$ {dados['fat']:.2f}* ({dados['ped']} pedidos)"
        for d, dados in sorted(por_dia.items())
    ])

    msg = """
📊 *Resumo Semanal*

📅 {inicio} a {fim}

━━━━━━━━━━━━━━━━━━━━━━

🍕 *TOTAL DA SEMANA*
├ Pedidos: *{ped}*
├ Faturamento: *R$ {fat:.2f}*
└ Lucro: *R$ {lucro:.2f}*

📈 *POR DIA*
{dias}

━━━━━━━━━━━━━━━━━━━━━━

📊 *MÉDIA DIÁRIA:* R$ {media:.2f}
🎯 *META DIÁRIA:* R$ 200,00
""".format(
        inicio=datetime.strptime(inicio_semana, '%Y-%m-%d').strftime('%d/%m'),
        fim=datetime.strptime(fim_semana, '%Y-%m-%d').strftime('%d/%m'),
        ped=ped_semana,
        fat=fat_semana,
        lucro=lucro_semana,
        dias=dias_text if dias_text else "├ Nenhuma venda registrada",
        media=fat_semana / (hoje.weekday() + 1)
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /ajuda
# ═══════════════════════════════════════════════════════
async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra todos os comandos disponíveis."""
    msg = """
📖 *Manual do Pizzelato Gestor*

━━━━━━━━━━━━━━━━━━━━━━

💰 *FINANCEIRO*
├ /caixa - Ver caixa do dia
├ /vendas - Resumo de vendas
├ /despesas - Ver despesas do mês
├ /dre - Demonstrativo de resultados
├ /lucro - Ver lucro detalhado

📊 *ANÁLISES*
├ /resumo - Resumo completo do dia
├ /meta - Progresso da meta mensal
├ /semana - Resumo semanal
├ /top - Produtos mais vendidos

🍕 *OPERAÇÃO*
├ /cardapio - Ver cardápio completo
├ /pedidos - Pedidos pendentes
├ /estoque - Status do estoque
├ /novo_produto - Cadastrar produto

🤝 *AFILIADOS*
├ /afiliados - Lista de afiliados
├ /comissoes - Ver comissões
├ /novo_afiliado - Cadastrar afiliado

🔧 *CONFIGURAÇÕES*
├ /alertas - Configurar alertas
├ /tono - Ajustar nível de detalhe
├ /ajuda - Este menu

━━━━━━━━━━━━━━━━━━━━━━

_Para mais ajuda, entre em contato com o admin._
"""

    await update.message.reply_text(msg, parse_mode='Markdown')
