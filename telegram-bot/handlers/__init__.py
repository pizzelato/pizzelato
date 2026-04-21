# handlers/__init__.py
"""
Pizzelato Telegram Bot - Módulo de Handlers
Exporta todos os handlers para uso no bot principal
"""

from handlers import financeiro, cardapio, cozinha, afiliados, ai_advisor

__all__ = ['financeiro', 'cardapio', 'cozinha', 'afiliados', 'ai_advisor']
