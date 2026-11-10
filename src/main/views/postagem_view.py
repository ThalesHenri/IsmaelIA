"""Views de postagens de eventos."""
from django.shortcuts import render, get_object_or_404

from main.models.postagem_model import Postagem
from main.services.postagem_service import listar_postagens, obter_postagem_por_slug


def postagem_lista(request):
    """Lista todas as postagens."""
    postagens = listar_postagens()
    return render(request, "main/postagens.html", {"postagens": postagens})


def postagem_detalhe(request, slug):
    """Detalhe de uma postagem."""
    postagem = get_object_or_404(Postagem, slug=slug)
    return render(request, "main/postagem_detalhe.html", {"postagem": postagem})
