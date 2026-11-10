"""Views de paginação e página inicial do site."""
from django.shortcuts import render

from main.services.pacote_service import listar_pacotes
from main.services.postagem_service import listar_postagens


def home(request):
    """View da página inicial/landing."""
    pacotes = listar_pacotes()[:3]
    postagens = listar_postagens()[:3]
    return render(
        request,
        "main/index.html",
        {"pacotes": pacotes, "postagens": postagens},
    )
