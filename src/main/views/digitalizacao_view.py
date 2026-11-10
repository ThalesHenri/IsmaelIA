"""Views para escaneamento facial e galeria de fotos do evento."""
import base64
from decimal import Decimal
from io import BytesIO

import qrcode
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_POST

from main.models.digitalizacao_model import (
    EventoDigitalizacao,
    FotoEvento,
    SessaoDigitalizacao,
)
from main.services import reconhecimento_facial_service as facial


def _evento_ativo():
    evento = EventoDigitalizacao.objects.filter(ativo=True).first()
    if not evento:
        evento = EventoDigitalizacao.objects.create(
            nome="Evento Exemplo",
            slug="evento-exemplo",
            data="2026-10-27",
            local="São Paulo, SP",
        )
    return evento


def calcular_valor(total_fotos: int) -> Decimal:
    """Valor cobrado pelas fotos encontradas.

    TODO: ligar aos preços dos pacotes. Por enquanto fica zerado e a tela
    mostra "a definir".
    """
    return Decimal("0.00")


def scan(request):
    """Tela de escaneamento: câmera ou envio de foto."""
    evento = EventoDigitalizacao.objects.filter(ativo=True).first()
    return render(request, "main/scan.html", {"evento": evento})


@require_POST
def buscar_rosto(request):
    """Recebe a selfie do cliente, procura o rosto na pasta de fotos e cria a sessão."""
    arquivo = request.FILES.get("foto")
    if not arquivo:
        return JsonResponse({"erro": "Nenhuma foto enviada."}, status=400)

    try:
        img = facial.ler_imagem_bytes(arquivo.read())
        fotos = facial.buscar_fotos_por_rosto(img)
    except facial.RostoNaoEncontradoError as exc:
        return JsonResponse({"erro": str(exc)}, status=422)
    except ValueError as exc:
        return JsonResponse({"erro": str(exc)}, status=400)
    except facial.ModelosAusentesError as exc:
        return JsonResponse({"erro": str(exc)}, status=503)

    if not fotos:
        return JsonResponse({"total": 0})

    sessao = SessaoDigitalizacao.objects.create(
        evento=_evento_ativo(),
        nome_cliente="Cliente",
        fotos_encontradas=fotos,
        total_fotos_encontradas=len(fotos),
        valor_total=calcular_valor(len(fotos)),
    )
    return JsonResponse(
        {
            "total": len(fotos),
            "codigo": sessao.codigo,
            "url": reverse("resultado", args=[sessao.codigo]),
        }
    )


def foto_previa(request, codigo, indice):
    """Entrega a prévia com marca d'água de uma foto da sessão.

    O cliente só acessa as fotos que foram encontradas para o rosto dele,
    pelo índice na lista — nunca pelo nome do arquivo.
    """
    sessao = get_object_or_404(SessaoDigitalizacao, codigo=codigo)
    if indice >= len(sessao.fotos_encontradas):
        raise Http404
    try:
        jpeg = facial.gerar_previa(sessao.fotos_encontradas[indice])
    except FileNotFoundError:
        raise Http404
    resposta = HttpResponse(jpeg, content_type="image/jpeg")
    resposta["Cache-Control"] = "private, max-age=3600"
    return resposta


def _qr_code_b64():
    # QR code genérico (apenas para demonstração ao cliente)
    qr_img = qrcode.make("https://pagamento.ismaelpessoa.com.br/checkout")
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def resultado(request, codigo):
    """Tela de resultado: prévias com marca d'água e QR code genérico."""
    sessao = SessaoDigitalizacao.objects.filter(codigo=codigo).first()
    if not sessao:
        sessao = SessaoDigitalizacao.objects.create(
            codigo=codigo,
            evento=_evento_ativo(),
            nome_cliente="Cliente",
            total_fotos_encontradas=4,
            valor_total=150.00,
        )

    if sessao.fotos_encontradas:
        previas = [
            reverse("foto_previa", args=[sessao.codigo, i])
            for i in range(len(sessao.fotos_encontradas))
        ]
    else:
        # Sessões de demonstração (sem busca real) usam a imagem padrão.
        qtd = FotoEvento.objects.filter(evento=sessao.evento)[: sessao.total_fotos_encontradas].count()
        previas = [static("img/foto-padrao.jpg")] * qtd

    return render(
        request,
        "main/resultado.html",
        {"sessao": sessao, "previas": previas, "qr_b64": _qr_code_b64()},
    )


def sessao_demo(request):
    """Cria/retorna uma sessão de demonstração para mostrar ao cliente."""
    sessao, _ = SessaoDigitalizacao.objects.get_or_create(
        codigo="DEMO",
        defaults={
            "evento": _evento_ativo(),
            "nome_cliente": "Cliente Demo",
            "total_fotos_encontradas": 4,
            "valor_total": 150.00,
        },
    )
    return redirect("resultado", codigo=sessao.codigo)
