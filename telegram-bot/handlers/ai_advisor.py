"""
Pizzelato Telegram Bot - AI Advisor Module
Advisor with AI insights, tips, and campaign suggestions
"""

import os
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from firebase_client import (
    get_vendas_hoje, get_vendas_periodo, get_despesas_mes,
    get_produtos, get_configuracoes
)


# ═══════════════════════════════════════════════════════
# AI INSIGHTS & TIPS
# ═══════════════════════════════════════════════════════

async def cmd_insights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate AI-powered business insights."""

    vendas_hoje = get_vendas_hoje()
    hoje = datetime.now()

    # Dados do dia
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas_hoje)
    ped_hoje = len(vendas_hoje)
    ticket_medio = fat_hoje / ped_hoje if ped_hoje > 0 else 0

    # Dados da semana
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
    vendas_semana = get_vendas_periodo(inicio_semana, hoje.strftime('%Y-%m-%d'))
    fat_semana = sum(float(v.get('total', 0)) for v in vendas_semana)

    # Dados do mês
    inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    vendas_mes = get_vendas_periodo(inicio_mes, hoje.strftime('%Y-%m-%d'))
    fat_mes = sum(float(v.get('total', 0)) for v in vendas_mes)
    luc_mes = sum(float(v.get('lucro', 0)) for v in vendas_mes)

    # Meta
    config = get_configuracoes()
    meta_mensal = float(config.get('meta_mensal', 6000))
    progresso = (fat_mes / meta_mensal * 100) if meta_mensal > 0 else 0

    # Análise de ticket médio
    ticket_status = "🟢" if ticket_medio >= 30 else "🟡" if ticket_medio >= 20 else "🔴"
    ticket_dica = ""

    if ticket_medio < 20:
        ticket_dica = """
🔺 *COMO AUMENTAR TICKET MÉDIO:*

1. *Combo com desconto:*
   Pizza + Bebida com 10% OFF

2. *Upsell no pedido:*
   "Quer adicionar uma cobertura extra?"

3. *Frete grátis acima de X:*
   Incentive pedidos maiores

4. *Produtos premium:*
   Destaque os mais rentáveis
"""
    elif ticket_medio >= 30:
        ticket_dica = """
✅ *TICKET MÉDIO EXCELENTE!*
Continue com a estratégia atual.
"""

    # Análise de margem
    margem = (luc_mes / fat_mes * 100) if fat_mes > 0 else 0
    margem_status = "🟢" if margem >= 30 else "🟡" if margem >= 20 else "🔴"

    msg = f"""
🤖 *Pizzelato AI Advisor*

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ANÁLISE DO DIA*
├ Vendas hoje: R$ {fat_hoje:.2f}
├ Pedidos: {ped_hoje}
└ Ticket médio: R$ {ticket_medio:.2f} {ticket_status}

📅 *ESTA SEMANA*
└ Faturamento: R$ {fat_semana:.2f}

📆 *ESTE MÊS*
├ Faturamento: R$ {fat_mes:.2f}
├ Lucro: R$ {luc_mes:.2f}
├ Margem: {margem:.1f}% {margem_status}
└ Meta: {progresso:.0f}% {"✅" if progresso >= 100 else "⏳"}

━━━━━━━━━━━━━━━━━━━━━━━━━
{ticket_dica}
━━━━━━━━━━━━━━━━━━━━━━━━━

*Quer dicas específicas? Use:*
├ /campanha - Ver sugestões de campanha
├ /dica_venda - Dicas de vendas
├ /dica_financeira - Dicas financeiras
└ /gerar_foto - Criar imagem promocional
"""

    keyboard = [
        [
            InlineKeyboardButton("🎯 Campanhas", callback_data="ai_campanha"),
            InlineKeyboardButton("💡 Dicas", callback_data="ai_dicas"),
        ],
        [
            InlineKeyboardButton("📸 Gerar Foto", callback_data="ai_foto"),
            InlineKeyboardButton("📊 Relatório", callback_data="ai_relatorio"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def cmd_campanha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sugestões de campanhas promocionais."""

    vendas_hoje = get_vendas_hoje()
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas_hoje)
    ped_hoje = len(vendas_hoje)

    # Análise baseada no dia/hora
    hora = datetime.now().hour

    # Determinar melhor campanha
    if ped_hoje < 5:
        sugestao = """
🎉 *CAMPANHA SUGERIDA:*

*Para Dias Lentos (menos de 5 pedidos)*

📱 *名称:* "Quinta de Quebrada!"
🎁 *Oferta:* 15% OFF em toda encomenda
⏰ *Validade:* Só quinta-feira
📢 *Divulgue:* Stories + Grupo de WhatsApp

💡 *Por que funciona:*
- Transforma dia lento em oportunidade
- Cria urgência com dia específico
- Aumenta engajamento
"""
    elif hora >= 18 and hora <= 21:
        sugestao = """
🌙 *CAMPANHA SUGERIDA:*

*Para Horário de Pico (18h-21h)*

📱 *名称:* "Happy Hour Pizzelato!"
🎁 *Oferta:* 10% OFF das 18h às 21h
⏰ *Validade:* Todos os dias
📢 *Divulgue:* Placa na porta + stories

💡 *Por que funciona:*
- Captura cliente no momento da decisão
- Aumenta volume no pico
- Posiciona marca como "opção do dia"
"""
    else:
        sugestao = """
📱 *CAMPANHA SUGERIDA:*

*Para Dias Normais*

📱 *名称:* "Combo da Família"
🎁 *Oferta:* 20% OFF no combo:
- 2 Pizzas Tradicional
- 1 Pizza Doce
- 2 Bebidas

⏰ *Validade:* Fim de semana

💡 *Por que funciona:*
- Ticket médio alto
- Perfeito para família
- Fim de semana = mais vendas
"""

    msg = f"""
🎯 *Sugestões de Campanhas*

━━━━━━━━━━━━━━━━━━━━━━━━━

{sugestao}

━━━━━━━━━━━━━━━━━━━━━━━━━

*Outras opções:*
├ /gerar_foto - Criar arte da campanha
├ /campanha_feriado - Campanhas especiais
└ /campanha_afiliado - Para seus afiliados
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


async def cmd_dica_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dicas práticas para aumentar vendas."""

    msg = """
💡 *DICAS DE VENDAS*

━━━━━━━━━━━━━━━━━━━━━━━━━

🔺 *AUMENTAR TICKET MÉDIO:*

1. *Técnica do "E"*
   "Quer adicionar uma cobertura extra por R$ 5?"

2. *Combo Visual*
   Mostre foto do combo + preço economia

3. *Frete Grátis Condicional*
   "Acima de R$ 80, frete grátis!"

━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *MELHORAR ATENDIMENTO:*

1. *Tempo de Resposta*
   Responda pedidos em até 5 min

2. *Follow-up*
   "Gostou do pedido? Volte sempre!"

3. *Personalização*
   Lembre o nome do cliente fiel

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *CONVERTER MAIS:*

1. *Escassez*
   "Só mais 5 encomendas hoje!"

2. *Urgência*
   "Promo acaba em 2 horas"

3. *Social Proof*
   "100 clientes satisfeitos!"

━━━━━━━━━━━━━━━━━━━━━━━━━

*Quer ver mais dicas específicas?*
├ /dica_financeira - Dicas de lucratividade
└ /gerar_foto - Criar imagem promocional
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


async def cmd_dica_financeira(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dicas para melhorar finances."""

    msg = """
💰 *DICAS FINANCEIRAS*

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *AUMENTAR LUCRO:*

1. *Corte Custos Operacionais*
   - renegociar luz/aluguel
   - comprar ingredientes no atacado

2. *Aumentar Margem*
   - suba preços 5% gradualmente
   - foco em produtos premium

3. *Reduzir Perdas*
   - controle de estoque diário
   - evitar desperdício

━━━━━━━━━━━━━━━━━━━━━━━━━

💵 *GERENCIAR CAIXA:*

1. *Reserva de Emergência*
   Guarde 10% do lucro

2. *Pagamento Antecipado*
   Pague fornecedores à vista = desconto

3. *Separe Finances*
   - Conta empresa vs pessoal

━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *MÉTRICAS IMPORTANTES:*

├ Margem ideal: 30%+
├ Ticket médio meta: R$ 35+
├ Custo ingrediente: < 25% do preço
└ Gasto fixo: < 40% da receita

━━━━━━━━━━━━━━━━━━━━━━━━━

*Use /dre para ver sua margem atual!*
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


async def cmd_gerar_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera imagem promocional."""

    msg = """
📸 *Gerador de Fotos*

━━━━━━━━━━━━━━━━━━━━━━━━━

Crie imagens promocionais para:

🎉 *Tipos de imagem:*

1. *Post de Instagram*
   - Produto do dia
   - Bastidores

2. *Stories*
   - Promoção flash
   - Novo sabor

3. *Banner WhatsApp*
   - Campanha ativa
   - Anúncio especial

━━━━━━━━━━━━━━━━━━━━━━━━━

*Para gerar, digite:*

/foto_produto [nome do produto]
Ex: /foto_produto Pizza Pepperoni

/foto_promocao [nome da campanha]
Ex: /foto_promocao Quinta de Quebrada

/foto_cardapio [categoria]
Ex: /foto_cardapio Tradicional
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


async def cmd_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Relatório diário automático."""

    vendas_hoje = get_vendas_hoje()
    despesas = get_despesas_mes()
    config = get_configuracoes()

    # Calcular métricas
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas_hoje)
    luc_hoje = sum(float(v.get('lucro', 0)) for v in vendas_hoje)
    ped_hoje = len(vendas_hoje)
    ticket = fat_hoje / ped_hoje if ped_hoje > 0 else 0

    # Meta
    meta_dia = float(config.get('meta_dia', 200))
    progresso = (fat_hoje / meta_dia * 100) if meta_dia > 0 else 0

    # Despesas hoje (estimativa)
    desp_mes = sum(float(d.get('valor', 0)) for d in despesas)
    desp_dia = desp_mes / 30

    # Lucro real
    lucro_real = luc_hoje - desp_dia

    # Status
    if progresso >= 100:
        status = "🟢 META BATIDA!"
        emoji = "🎉"
    elif progresso >= 75:
        status = "🟡 NO CAMINHO CERTO"
        emoji = "👍"
    else:
        status = "🔴 PRECISAMENTE ACELERAR"
        emoji = "⚡"

    msg = f"""
📊 *RELATÓRIO DIÁRIO*

━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji} *{datetime.now().strftime('%d/%m/%Y')}*

🍕 *VENDAS*
├ Pedidos: {ped_hoje}
├ Faturamento: R$ {fat_hoje:.2f}
├ Lucro bruto: R$ {luc_hoje:.2f}
└ Ticket médio: R$ {ticket:.2f}

💰 *FINANCEIRO*
├ Lucro real: R$ {lucro_real:.2f}
├ Desp. estimadas: R$ {desp_dia:.2f}
└ Lucro líquido: R$ {lucro_real:.2f}

🎯 *META DO DIA*
├ Meta: R$ {meta_dia:.2f}
├ Realizado: R$ {fat_hoje:.2f}
└ Progresso: {progresso:.0f}%

*Situação:* {status}

━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *DICA DO DIA:*
{get_dica_aleatoria()}

━━━━━━━━━━━━━━━━━━━━━━━━━

*Use /insights para análise completa!*
"""

    await update.message.reply_text(msg, parse_mode='Markdown')


def get_dica_aleatoria():
    """Retorna uma dica aleatória."""
    dicas = [
        "Envie uma foto do produto mais vendido no stories!",
        "Que tal um post sobre a história da Pizzelato?",
        "Checklist: Estoque de pepperoni está ok?",
        "Lembre seus afiliados da campanha ativa!",
        "Que tal oferecer upgrade para tamanho família?",
        "Faça um vídeo rápido do preparo! Engaja muito!",
        "交叉销售: Ofereça bebida com a pizza hoje.",
        "Ofertar覆盘子覆盆子? Tentaupsell!",
    ]
    return dicas[datetime.now().minute % len(dicas)]


# ═══════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════

async def callback_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI module callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "ai_campanha":
        await cmd_campanha(update, context)
    elif data == "ai_dicas":
        await cmd_dica_venda(update, context)
    elif data == "ai_foto":
        await cmd_gerar_foto(update, context)
    elif data == "ai_relatorio":
        await cmd_daily_report(update, context)
