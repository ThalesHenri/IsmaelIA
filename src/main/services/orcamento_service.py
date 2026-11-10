"""Serviço de orçamentos."""
from main.models.orcamento_model import Orcamento

#chamar script de envio de email
def criar_orcamento(nome, email, telefone, pacote_id, mensagem):
    """Cria e retorna um novo orçamento."""
    return Orcamento.objects.create(
        nome=nome,
        email=email,
        telefone=telefone,
        pacote_id=pacote_id,
        mensagem=mensagem,
    )
