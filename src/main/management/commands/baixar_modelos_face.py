"""Baixa os modelos oficiais do OpenCV Zoo usados no reconhecimento facial."""
import hashlib
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from main.services.reconhecimento_facial_service import (
    MODELO_DETECTOR,
    MODELO_RECONHECEDOR,
    pasta_modelos,
)

BASE = "https://github.com/opencv/opencv_zoo/raw/main/models"
MODELOS = {
    MODELO_DETECTOR: (
        f"{BASE}/face_detection_yunet/{MODELO_DETECTOR}",
        "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    ),
    MODELO_RECONHECEDOR: (
        f"{BASE}/face_recognition_sface/{MODELO_RECONHECEDOR}",
        "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
    ),
}


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


class Command(BaseCommand):
    help = "Baixa os modelos YuNet (detecção) e SFace (reconhecimento) do OpenCV."

    def handle(self, *args, **opts):
        destino = pasta_modelos()
        destino.mkdir(parents=True, exist_ok=True)

        for nome, (url, sha) in MODELOS.items():
            arquivo = destino / nome
            if arquivo.exists() and _sha256(arquivo) == sha:
                self.stdout.write(f"{nome}: já está baixado.")
                continue

            self.stdout.write(f"Baixando {nome}...")
            temporario = arquivo.with_suffix(".tmp")
            try:
                urllib.request.urlretrieve(url, temporario)
            except Exception as exc:
                raise CommandError(f"Falha ao baixar {url}: {exc}") from exc

            if _sha256(temporario) != sha:
                temporario.unlink(missing_ok=True)
                raise CommandError(
                    f"{nome} veio corrompido (checksum diferente). Tente de novo."
                )
            temporario.replace(arquivo)
            self.stdout.write(self.style.SUCCESS(f"{nome}: ok"))

        self.stdout.write(self.style.SUCCESS(f"Modelos prontos em {destino}"))
