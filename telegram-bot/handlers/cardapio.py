"""
Pizzelato Telegram Bot - Handlers de Cardápio
Gerencia comandos relacionados ao cardápio
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import config
from firebase_client import get_produtos, get_db

# ═══════════════════════════════════════════════════════
# COMANDO: /cardapio
# ═══════════════════════════════════════════════════════
async def cmd_cardapio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra cardápio completo."""
    produtos = get_produtos()

    if not produtos:
        msg = """
🍕 *Cardápio Pizzelato*

⚠️ Nenhum produto cadastrado.

_Use o painel web para adicionar produtos._
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return

    # Agrupar por categoria
    por_categoria = {}
    for p in produtos:
        cat = p.get('categoria', 'Outros')
        if cat not in por_categoria:
            por_categoria[cat] = []
        por_categoria[cat].append(p)

    msg = """
🍕 *Cardápio Pizzelato*

📋 *Total de produtos:* {total}

━━━━━━━━━━━━━━━━━━━━━━
""".format(total=len(produtos))

    for cat, prods in por_categoria.items():
        msg += f"\n{cat}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        for p in prods[:10]:  # Limitar a 10 por categoria
            nome = p.get('nome', 'Sem nome')
            preco = float(p.get('preco', 0))
            ativo = "🟢" if p.get('ativo', True) else "🔴"
            msg += f"{ativo} {nome}: R$ {preco:.2f}\n"

        if len(prods) > 10:
            msg += f"_... e mais {len(prods) - 10} produtos_\n"

    keyboard = [
        [InlineKeyboardButton("📋 Ver Todos", callback_data="cardapio_todos")],
        [InlineKeyboardButton("✨ Assinatura", callback_data="cardapio_cat_Assinatura")],
        [InlineKeyboardButton("⭐ Premium", callback_data="cardapio_cat_Premium")],
        [InlineKeyboardButton("🍕 Tradicional", callback_data="cardapio_cat_Tradicional")],
        [InlineKeyboardButton("🍫 Doce", callback_data="cardapio_cat_Doce")],
        [InlineKeyboardButton("🥤 Bebida", callback_data="cardapio_cat_Bebida")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


# ═══════════════════════════════════════════════════════
# COMANDO: /produto_detalhe
# ═══════════════════════════════════════════════════════
async def cmd_produto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra detalhes de um produto específico."""
    if not context.args:
        await update.message.reply_text(
            "📋 Use: /produto <nome do produto>\n\nExemplo: /produto Pepperoni"
        )
        return

    nome_busca = ' '.join(context.args).lower()
    produtos = get_produtos()

    # Buscar produto
    encontrado = None
    for p in produtos:
        if nome_busca in p.get('nome', '').lower():
            encontrado = p
            break

    if not encontrado:
        await update.message.reply_text(
            f"❌ Produto '{nome_busca}' não encontrado.\n\n_Use /cardapio para ver a lista completa._"
        )
        return

    nome = encontrado.get('nome', 'Sem nome')
    preco = float(encontrado.get('preco', 0))
    cat = encontrado.get('categoria', 'Outros')
    custo = float(encontrado.get('custo', 0))
    lucro = preco - custo
    margem = (lucro / preco * 100) if preco > 0 else 0
    ativo = "🟢 Ativo" if encontrado.get('ativo', True) else "🔴 Inativo"

    msg = """
🍕 *{nome}*

📋 Categoria: {cat}
💰 Preço: *R$ {preco:.2f}*
📦 Custo: R$ {custo:.2f}
✅ Lucro: R$ {lucro:.2f}
📊 Margem: {margem:.1f}%
{status}
""".format(
        nome=nome,
        cat=cat,
        preco=preco,
        custo=custo,
        lucro=lucro,
        margem=margem,
        status=ativo
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# COMANDO: /top
# ═══════════════════════════════════════════════════════
async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra produtos mais vendidos."""
    db = get_db()
    if not db:
        await update.message.reply_text(
            "⚠️ Firebase não disponível.\n\n_Consigure as credenciais para ver dados reais._"
        )
        return

    try:
        # Buscar vendas e agregar
        vendas = db.collection('vendas').stream()
        produtos_vendas = {}

        for doc in vendas:
            data = doc.to_dict()
            itens = data.get('itens', [])
            for item in itens:
                nome = item.get('nome', 'Desconhecido')
                qtd = int(item.get('qty', 0))
                produtos_vendas[nome] = produtos_vendas.get(nome, 0) + qtd

        # Ordenar por quantidade
        top_produtos = sorted(produtos_vendas.items(), key=lambda x: -x[1])[:10]

        if not top_produtos:
            await update.message.reply_text(
                "📊 *Top Produtos*\n\n⚠️ Nenhuma venda registrada ainda."
            )
            return

        msg = "🏆 *Top 10 Produtos*\n\n"

        medals = ["🥇", "🥈", "🥉"]
        for i, (nome, qtd) in enumerate(top_produtos):
            medal = medals[i] if i < 3 else f"#{i+1}"
            msg += f"{medal} {nome}: *{qtd}* unidades\n"

        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao buscar dados: {e}")


# ═══════════════════════════════════════════════════════
# COMANDO: /novo_produto (para adicionar via bot)
# ═══════════════════════════════════════════════════════
async def cmd_novo_produto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia fluxo para cadastrar novo produto."""
    msg = """
➕ *Cadastrar Novo Produto*

Preencha os dados abaixo:

📝 *Formato:*
```
/novo_produto
Nome: [nome do produto]
Categoria: [categoria]
Preço: [preço]
Custo: [custo]
```

📋 *Categorias disponíveis:*
• ✨ Assinatura
• ⭐ Premium
• 🍕 Tradicional
• 🍫 Doce
• 🥤 Bebida
• ➕ Extra

📝 *Exemplo:*
`/novo_produto Nome: Cone Pepperoni Categoria: Tradicional Preço: 18.90 Custo: 5.50`
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════
# CALLBACK: Categorias do Cardápio
# ═══════════════════════════════════════════════════════
async def callback_cardapio_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra produtos de uma categoria."""
    query = update.callback_query

    # Extrair categoria do callback_data
    cat = query.data.replace('cardapio_cat_', '')
    produtos = get_produtos()

    # Filtrar por categoria
    produtos_cat = [p for p in produtos if p.get('categoria') == cat]

    if not produtos_cat:
        await query.answer_text("Nenhum produto nesta categoria.")
        return

    msg = f"🍕 *{cat}*\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n"

    for p in produtos_cat:
        nome = p.get('nome', 'Sem nome')
        preco = float(p.get('preco', 0))
        ativo = "🟢" if p.get('ativo', True) else "🔴"
        msg += f"{ativo} {nome}: R$ {preco:.2f}\n"

    msg += f"\n📋 Total: {len(produtos_cat)} produtos"

    await query.answer_text(msg, parse_mode='Markdown')
