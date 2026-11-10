"""Serviço de postagens de eventos."""
from main.models.postagem_model import Postagem


def listar_postagens():
    """Retorna todas as postagens ordenadas pela data mais recente."""
    return Postagem.objects.all()


def obter_postagem_por_slug(slug):
    """Retorna uma postagem pelo slug ou levanta exceção se não encontrar."""
    return Postagem.objects.get(slug=slug)
