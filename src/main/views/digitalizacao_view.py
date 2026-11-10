"""Views para escaneamento facial e galeria de fotos do evento."""
import qrcode
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings

from main.models.digitalizacao_model import (
    EventoDigitalizacao,
    FotoEvento,
    SessaoDigitalizacao,
)


def scan(request):
    """Tela de escaneamento (mock). Busca o primeiro evento ativo."""
    evento = EventoDigitalizacao.objects.filter(ativo=True).first()
    return render(request, "main/scan.html", {"evento": evento})


def resultado(request, codigo):
    """Tela de resultado: prévia com marca d'água e QR code genérico."""
    evento = EventoDigitalizacao.objects.filter(ativo=True).first()
    if not evento:
        evento = EventoDigitalizacao.objects.create(
            nome="Evento Exemplo",
            slug="evento-exemplo",
            data="2026-10-27",
            local="São Paulo, SP",
        )
    sessao, _ = SessaoDigitalizacao.objects.get_or_create(
        codigo=codigo,
        defaults={
            "evento": evento,
            "nome_cliente": "Cliente",
            "total_fotos_encontradas": 4,
            "valor_total": 150.00,
        },
    )
    fotos = FotoEvento.objects.filter(evento=sessao.evento)[: sessao.total_fotos_encontradas]

    # QR code genérico (apenas para demonstração ao cliente)
    qr_data = "https://pagamento.ismaelpessoa.com.br/checkout"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    import base64
    qr_b64 = base64.b64encode(buffer.read()).decode("utf-8")

    return render(
        request,
        "main/resultado.html",
        {
            "sessao": sessao,
            "fotos": fotos,
            "qr_b64": qr_b64,
        },
    )


def sessao_demo(request):
    """Cria/retorna uma sessão de demonstração para mostrar ao cliente."""
    evento = EventoDigitalizacao.objects.filter(ativo=True).first()
    if not evento:
        evento = EventoDigitalizacao.objects.create(
            nome="Evento Exemplo",
            slug="evento-exemplo",
            data="2026-10-27",
            local="São Paulo, SP",
        )
    sessao, _ = SessaoDigitalizacao.objects.get_or_create(
        codigo="DEMO",
        defaults={
            "evento": evento,
            "nome_cliente": "Cliente Demo",
            "total_fotos_encontradas": 4,
            "valor_total": 150.00,
        },
    )
    return redirect("resultado", codigo=sessao.codigo)
