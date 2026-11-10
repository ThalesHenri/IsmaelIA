"""Analisa antecipadamente as fotos da pasta do evento.

Não é obrigatório (a primeira busca faz isso sozinha), mas rodar antes evita
que o primeiro cliente espere a análise de todas as fotos.
"""
from django.core.management.base import BaseCommand

from main.services.reconhecimento_facial_service import indexar_pasta, pasta_fotos


class Command(BaseCommand):
    help = "Detecta os rostos de todas as fotos em FOTOS_EVENTO_DIR e salva em cache."

    def handle(self, *args, **opts):
        self.stdout.write(f"Lendo fotos de {pasta_fotos()}")

        def progresso(nome, qtd):
            self.stdout.write(f"  {nome}: {qtd} rosto(s)")

        indice = indexar_pasta(progresso=progresso)
        total_rostos = sum(len(v) for v in indice.values())
        self.stdout.write(
            self.style.SUCCESS(f"{len(indice)} foto(s) indexadas, {total_rostos} rosto(s) no total.")
        )
