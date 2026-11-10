"""Serviço de pacotes de serviços."""
from main.models.pacote_model import Pacote


def listar_pacotes():
    """Retorna todos os pacotes ordenados por nome."""
    return Pacote.objects.all().order_by("nome")


def obter_pacote_por_slug(slug):
    """Retorna um pacote pelo slug ou levanta exceção se não encontrar."""
    return Pacote.objects.get(slug=slug)


def obter_pacotes_destaque():
    """Retorna apenas os pacotes marcados como destaque."""
    return Pacote.objects.filter(destaque=True)
