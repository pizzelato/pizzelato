"""
Pizzelato Telegram Bot - AI Chat Module
Integração com Claude AI para conversas inteligentes
"""

import os
import anthropic
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from firebase_client import (
    get_vendas_hoje, get_vendas_periodo, get_despesas_mes,
    get_produtos, get_pedidos_pendentes, get_afiliados,
    get_estoque, get_configuracoes
)

# Cliente Anthropic
client = None

def get_claude_client():
    """Retorna cliente Claude configurado."""
    global client
    if client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            client = anthropic.Anthropic()
    return client


def get_business_context():
    """Prepara contexto do negócio para o Claude."""
    hoje = datetime.now()

    # Buscar dados
    vendas_hoje = get_vendas_hoje()
    fat_hoje = sum(float(v.get('total', 0)) for v in vendas_hoje)
    ped_hoje = len(vendas_hoje)

    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
    vendas_semana = get_vendas_periodo(inicio_semana, hoje.strftime('%Y-%m-%d'))
    fat_semana = sum(float(v.get('total', 0)) for v in vendas_semana)

    inicio_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    vendas_mes = get_vendas_periodo(inicio_mes, hoje.strftime('%Y-%m-%d'))
    fat_mes = sum(float(v.get('total', 0)) for v in vendas_mes)
    luc_mes = sum(float(v.get('lucro', 0)) for v in vendas_mes)

    despesas = get_despesas_mes()
    desp_total = sum(float(d.get('valor', 0)) for d in despesas)

    pedidos = get_pedidos_pendentes()
    estoque = get_estoque()
    afiliados = get_afiliados()

    config = get_configuracoes()
    meta_mensal = float(config.get('meta_mensal', 6000))

    return f"""
## CONTEXTO: Pizzelato Pizza Cone

### DATAS
- Hoje: {hoje.strftime('%d/%m/%Y')}
- Dia da semana: {hoje.strftime('%A')}

### VENDAS
| Período | Faturamento | Pedidos |
|---------|-------------|---------|
| Hoje | R$ {fat_hoje:.2f} | {ped_hoje} |
| Semana | R$ {fat_semana:.2f} | {len(vendas_semana)} |
| Mês | R$ {fat_mes:.2f} | {len(vendas_mes)} |

### FINANCEIRO
- Lucro do mês: R$ {luc_mes:.2f}
- Margem: {((luc_mes/fat_mes)*100) if fat_mes > 0 else 0:.1f}%
- Despesas do mês: R$ {desp_total:.2f}
- Meta mensal: R$ {meta_mensal:.2f}
- Progresso meta: {((fat_mes/meta_mensal)*100) if meta_mensal > 0 else 0:.0f}%

### OPERAÇÃO
- Pedidos pendentes: {len(pedidos)}
- Itens no estoque: {len(estoque)}
- Afiliados ativos: {len([a for a in afiliados if a.get('ativo', True)])}

### SISTEMA
- Cardápio: produtos à disposição
- Cozinha: pedidos em andamento
- Afiliados: rede de vendedores
"""


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat inteligente com o Claude."""

    if not context.args:
        await update.message.reply_text(
            "💬 *Chat com IA*\n\n"
            "Digite sua pergunta após o comando:\n"
            "`/chat Como posso aumentar meu faturamento?`\n\n"
            "Exemplos:\n"
            "├ /chat Qual minha meta para hoje?\n"
            "├ /chat Dê dicas para reduzir despesas\n"
            "├ /chat Analise meu desempenho semanal\n"
            "└ /chat O que devo fazer para vender mais?",
            parse_mode='Markdown'
        )
        return

    # Obter pergunta do usuário
    pergunta = ' '.join(context.args)

    await update.message.reply_text("🤖 Pensando...")

    # Obter cliente Claude
    claude = get_claude_client()

    if not claude:
        await update.message.reply_text(
            "⚠️ Claude não configurado.\n"
            "Adicione ANTHROPIC_API_KEY no Railway."
        )
        return

    # Preparar contexto
    contexto = get_business_context()

    try:
        # Enviar para Claude
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=f"""Você é o Gerente AI da Pizzelato Pizza Cone, uma pizza cone artesanal. Você é prestativo, analítico e focado em ajudar o dono a melhorar seu negócio.

Seu papel:
- Analisar dados financeiros e dar recomendações
- Sugerir campanhas e estratégias de vendas
- Identificar problemas e oportunidades
- Dar dicas práticas para melhorar lucratividade
- Ser direto e objetivo nas respostas

Use emojis quando apropriado para facilitar a leitura.

{contexto}

Responda sempre em português brasileiro, de forma clara e útil.""",
            messages=[
                {
                    "role": "user",
                    "content": pergunta
                }
            ]
        )

        resposta = response.content[0].text

        await update.message.reply_text(resposta, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def cmd_analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Análise completa com IA."""

    await update.message.reply_text("🔍 Analisando seu negócio...")

    claude = get_claude_client()

    if not claude:
        await update.message.reply_text(
            "⚠️ Claude não configurado.\n"
            "Adicione ANTHROPIC_API_KEY no Railway."
        )
        return

    contexto = get_business_context()

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=f"""Você é o Gerente AI da Pizzelato Pizza Cone. Analise o negócio e dê:
1. Diagnóstico rápido do dia/semana
2. 3 principais pontos de atenção
3. 3 sugestões de ação imediata
4. 1 previsão para os próximos dias

Seja direto e use emojis.""",
            messages=[
                {
                    "role": "user",
                    "content": f"Faça uma análise completa do negócio. {contexto}"
                }
            ]
        )

        resposta = response.content[0].text

        keyboard = [
            [
                InlineKeyboardButton("📋 Ver DRE", callback_data="fin_dre"),
                InlineKeyboardButton("🎯 Ver Meta", callback_data="meta"),
            ],
            [
                InlineKeyboardButton("💰 Caixa", callback_data="fin_caixa"),
                InlineKeyboardButton("🎯 Campanhas", callback_data="ai_campanha"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(resposta, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def cmd_responder_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ajuda a responder um cliente."""

    if not context.args:
        await update.message.reply_text(
            "💬 *Gerador de Respostas*\n\n"
            "Cole a mensagem do cliente:\n"
            "`/responder Gostaria de saber se entregam no centro`",
            parse_mode='Markdown'
        )
        return

    mensagem = ' '.join(context.args)

    await update.message.reply_text("✍️ Criando resposta...")

    claude = get_claude_client()

    if not claude:
        await update.message.reply_text("⚠️ Claude não configurado.")
        return

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system="""Você é atendente da Pizzelato Pizza Cone. Sua função é criar respostas profissionais e amigáveis para clientes.

Características:
- Linguagem calorosa e acolhedora
- Informações claras sobre delivery e cardápio
- Sempre sugira algo a mais (upsel)
- Finalize com chamada para ação

Crie uma resposta curta (máx 3 parágrafos).""",
            messages=[
                {
                    "role": "user",
                    "content": f"Cliente disse: {mensagem}\n\nCrie uma resposta para este cliente."
                }
            ]
        )

        resposta = response.content[0].text

        keyboard = [
            [
                InlineKeyboardButton("✏️ Criar outra", callback_data="chat_responder"),
                InlineKeyboardButton("📋 Ver cardápio", callback_data="op_cardapio"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"💬 *Sugestão de resposta:*\n\n{resposta}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def cmd_gerar_campanha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera uma campanha personalizada."""

    if not context.args:
        tipo = "promocional"
    else:
        tipo = ' '.join(context.args)

    await update.message.reply_text("🎨 Criando campanha...")

    claude = get_claude_client()

    if not claude:
        await update.message.reply_text("⚠️ Claude não configurado.")
        return

    contexto = get_business_context()

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=f"""Você é especialista em marketing para pizzarias. Crie uma campanha promocional completa.

Forneça:
1. Nome da campanha (criativo e memorável)
2. Oferta principal
3. Prazo de validade
4. Canais de divulgação (Instagram, WhatsApp, etc)
5. Estratégia de posts
6. Call-to-action

{contexto}

Seja criativo mas realista.""",
            messages=[
                {
                    "role": "user",
                    "content": f"Crie uma campanha {tipo} para esta pizzaria."
                }
            ]
        )

        resposta = response.content[0].text

        keyboard = [
            [
                InlineKeyboardButton("📸 Gerar arte", callback_data="ai_foto"),
                InlineKeyboardButton("📱 Ver modelo WhatsApp", callback_data="campanha_whatsapp"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🎯 *Campanha Gerada:*\n\n{resposta}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
