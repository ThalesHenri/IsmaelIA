"""Views de orçamento."""
from django.contrib import messages
from django.shortcuts import render, redirect

from main.services.orcamento_service import criar_orcamento


def orcamento(request):
    """Formulário de solicitação de orçamento."""
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        pacote_id = request.POST.get("pacote")
        mensagem = request.POST.get("mensagem", "").strip()

        if not nome or not email:
            messages.error(request, "Preencha pelo menos o nome e o e-mail.")
            return render(request, "main/orcamento.html")

        criar_orcamento(nome, email, telefone, pacote_id, mensagem)
        messages.success(
            request,
            "Solicitação enviada! Entraremos em contato em breve.",
        )
        return redirect("orcamento")

    return render(request, "main/orcamento.html")
