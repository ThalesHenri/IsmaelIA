"""Views de pacotes de serviços."""
from django.shortcuts import render, get_object_or_404

from main.models.pacote_model import Pacote
from main.services.pacote_service import listar_pacotes, obter_pacote_por_slug


def pacote_lista(request):
    """Lista todos os pacotes."""
    pacotes = listar_pacotes()
    return render(request, "main/pacotes.html", {"pacotes": pacotes})


def pacote_detalhe(request, slug):
    """Detalhe de um pacote."""
    pacote = get_object_or_404(Pacote, slug=slug)
    return render(request, "main/pacote_detalhe.html", {"pacote": pacote})
