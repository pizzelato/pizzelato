"""
Pizzelato Telegram Bot - Módulo de Conexão Firebase
Conecta com o Firebase do sistema Pizzelato
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Instância global do banco de dados
db = None

def init_firebase():
    """Inicializa conexão com Firebase Firestore."""
    global db

    if db is not None:
        return db

    try:
        # Tenta obter credenciais da variável de ambiente
        creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')

        if creds_json:
            cred_dict = json.loads(creds_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # Se não tiver credenciais, usa aplicação padrão
            # (funciona se FIREBASE_AUTH_EMULATOR estiver configurado)
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred, {
            'projectId': 'pizzelato-gestao',  # Substitua pelo seu project ID
        })

        db = firestore.client()
        print("✅ Firebase conectado com sucesso!")
        return db

    except Exception as e:
        print(f"⚠️ Firebase não disponível: {e}")
        return None


def get_db():
    """Retorna instância do banco de dados."""
    global db
    if db is None:
        return init_firebase()
    return db


# ═══════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES DE CONSULTA
# ═══════════════════════════════════════════════════════

def get_vendas_hoje():
    """Retorna vendas do dia atual."""
    from datetime import datetime
    db = get_db()
    if not db:
        return []

    try:
        hoje = datetime.now().strftime('%Y-%m-%d')
        docs = db.collection('vendas').where('data', '==', hoje).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar vendas: {e}")
        return []


def get_vendas_periodo(data_inicio, data_fim):
    """Retorna vendas de um período."""
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('vendas')\
            .where('data', '>=', data_inicio)\
            .where('data', '<=', data_fim)\
            .stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar vendas: {e}")
        return []


def get_despesas_mes():
    """Retorna despesas do mês atual."""
    from datetime import datetime
    db = get_db()
    if not db:
        return []

    try:
        ano_mes = datetime.now().strftime('%Y-%m')
        docs = db.collection('despesas').where('referencia', '==', ano_mes).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar despesas: {e}")
        return []


def get_configuracoes():
    """Retorna configurações do sistema."""
    db = get_db()
    if not db:
        return {}

    try:
        doc = db.collection('config').document('sistema').get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        print(f"Erro ao buscar config: {e}")
        return {}


def get_produtos():
    """Retorna todos os produtos do cardápio."""
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('produtos').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        return []


def get_pedidos_pendentes():
    """Retorna pedidos pendentes."""
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('pedidos').where('status', '==', 'pendente').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        return []


def get_afiliados():
    """Retorna lista de afiliados."""
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('afiliados').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar afiliados: {e}")
        return []


def get_caixa_hoje():
    """Retorna dados do caixa do dia."""
    from datetime import datetime
    db = get_db()
    if not db:
        return None

    try:
        hoje = datetime.now().strftime('%Y-%m-%d')
        doc = db.collection('caixa').document(hoje).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Erro ao buscar caixa: {e}")
        return None


def get_estoque():
    """Retorna itens do estoque."""
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('estoque').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"Erro ao buscar estoque: {e}")
        return []
