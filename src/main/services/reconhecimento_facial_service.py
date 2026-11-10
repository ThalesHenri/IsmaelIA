"""Reconhecimento facial com OpenCV.

Fluxo:
1. As fotos do evento ficam em uma pasta (settings.FOTOS_EVENTO_DIR).
2. Cada foto é analisada uma vez: detectamos os rostos (YuNet) e geramos um
   vetor de características para cada um (SFace). O resultado fica em cache,
   então só fotos novas ou alteradas são processadas de novo.
3. Quando o cliente tira uma selfie, geramos o vetor do rosto dele e
   comparamos com todos os rostos da pasta (similaridade de cosseno).
4. As fotos que passam do limite de similaridade são devolvidas.

Os dois modelos (.onnx) são os oficiais do OpenCV Zoo. Baixe-os com:
    python manage.py baixar_modelos_face
"""
import pickle
import threading
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings

MODELO_DETECTOR = "face_detection_yunet_2023mar.onnx"
MODELO_RECONHECEDOR = "face_recognition_sface_2021dec.onnx"

EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Fotos de câmera profissional são enormes; reduzir antes de detectar deixa a
# análise muito mais rápida sem perder rostos de tamanho normal.
LADO_MAXIMO_DETECCAO = 1600

_lock = threading.Lock()
_detector = None
_reconhecedor = None


class ModelosAusentesError(Exception):
    """Os arquivos .onnx não foram encontrados."""


class RostoNaoEncontradoError(Exception):
    """Nenhum rosto foi detectado na foto enviada pelo cliente."""


# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

def pasta_modelos() -> Path:
    return Path(settings.FACE_MODELS_DIR)


def pasta_fotos() -> Path:
    return Path(settings.FOTOS_EVENTO_DIR)


def arquivo_cache() -> Path:
    return Path(settings.FACE_CACHE_FILE)


def limite_similaridade() -> float:
    # 0.363 é o limite recomendado pelo OpenCV para o SFace (cosseno).
    return float(getattr(settings, "FACE_MATCH_THRESHOLD", 0.363))


def _carregar_modelos():
    global _detector, _reconhecedor
    if _detector is not None:
        return
    det = pasta_modelos() / MODELO_DETECTOR
    rec = pasta_modelos() / MODELO_RECONHECEDOR
    faltando = [p.name for p in (det, rec) if not p.exists()]
    if faltando:
        raise ModelosAusentesError(
            "Modelos de reconhecimento facial não encontrados: "
            + ", ".join(faltando)
            + ". Rode: python manage.py baixar_modelos_face"
        )
    _detector = cv2.FaceDetectorYN.create(str(det), "", (320, 320), 0.8, 0.3, 5000)
    _reconhecedor = cv2.FaceRecognizerSF.create(str(rec), "")


# --------------------------------------------------------------------------
# Análise de imagens
# --------------------------------------------------------------------------

def _reduzir(img):
    h, w = img.shape[:2]
    maior = max(h, w)
    if maior <= LADO_MAXIMO_DETECCAO:
        return img
    escala = LADO_MAXIMO_DETECCAO / maior
    return cv2.resize(img, (int(w * escala), int(h * escala)), interpolation=cv2.INTER_AREA)


def _extrair_rostos(img):
    """Retorna lista de (area_do_rosto, vetor_normalizado) para cada rosto."""
    img = _reduzir(img)
    h, w = img.shape[:2]
    with _lock:
        _carregar_modelos()
        _detector.setInputSize((w, h))
        _, rostos = _detector.detect(img)
        if rostos is None:
            return []
        resultado = []
        for rosto in rostos:
            alinhado = _reconhecedor.alignCrop(img, rosto)
            vetor = _reconhecedor.feature(alinhado).flatten().astype(np.float32)
            vetor /= np.linalg.norm(vetor) + 1e-9
            area = float(rosto[2] * rosto[3])
            resultado.append((area, vetor))
        return resultado


def _ler_imagem_arquivo(caminho: Path):
    # imdecode em vez de imread para aceitar caminhos com acento no Windows.
    dados = np.fromfile(str(caminho), dtype=np.uint8)
    return cv2.imdecode(dados, cv2.IMREAD_COLOR)


def ler_imagem_bytes(dados: bytes):
    img = cv2.imdecode(np.frombuffer(dados, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Arquivo enviado não é uma imagem válida.")
    return img


# --------------------------------------------------------------------------
# Índice da pasta de fotos (com cache)
# --------------------------------------------------------------------------

def listar_fotos_pasta():
    pasta = pasta_fotos()
    if not pasta.exists():
        return []
    return sorted(
        p for p in pasta.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSOES_IMAGEM
    )


def _carregar_cache():
    try:
        with open(arquivo_cache(), "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return {}


def _salvar_cache(cache):
    destino = arquivo_cache()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".tmp")
    with open(temporario, "wb") as f:
        pickle.dump(cache, f)
    temporario.replace(destino)


def indexar_pasta(progresso=None):
    """Analisa fotos novas/alteradas e devolve {nome_relativo: matriz_de_vetores}."""
    pasta = pasta_fotos()
    cache = _carregar_cache()
    novo_cache = {}
    alterou = False

    for caminho in listar_fotos_pasta():
        nome = caminho.relative_to(pasta).as_posix()
        stat = caminho.stat()
        assinatura = (stat.st_mtime_ns, stat.st_size)
        item = cache.get(nome)
        if item and item["assinatura"] == assinatura:
            novo_cache[nome] = item
            continue

        img = _ler_imagem_arquivo(caminho)
        vetores = [v for _, v in _extrair_rostos(img)] if img is not None else []
        novo_cache[nome] = {
            "assinatura": assinatura,
            "vetores": np.array(vetores, dtype=np.float32).reshape(-1, 128),
        }
        alterou = True
        if progresso:
            progresso(nome, len(vetores))

    if alterou or set(novo_cache) != set(cache):
        _salvar_cache(novo_cache)

    return {nome: item["vetores"] for nome, item in novo_cache.items()}


# --------------------------------------------------------------------------
# Busca
# --------------------------------------------------------------------------

def buscar_fotos_por_rosto(img_selfie):
    """Retorna a lista de fotos (nome relativo) em que o rosto da selfie aparece,
    da mais parecida para a menos parecida."""
    rostos = _extrair_rostos(img_selfie)
    if not rostos:
        raise RostoNaoEncontradoError(
            "Não encontramos um rosto na foto. Tente com mais luz e olhando para a câmera."
        )
    # Se aparecer mais de uma pessoa na selfie, usamos o maior rosto.
    _, vetor_cliente = max(rostos, key=lambda r: r[0])

    limite = limite_similaridade()
    encontrados = []
    for nome, vetores in indexar_pasta().items():
        if len(vetores) == 0:
            continue
        similaridade = float(np.max(vetores @ vetor_cliente))
        if similaridade >= limite:
            encontrados.append((similaridade, nome))

    encontrados.sort(reverse=True)
    return [nome for _, nome in encontrados]


# --------------------------------------------------------------------------
# Prévia protegida
# --------------------------------------------------------------------------

def caminho_foto_seguro(nome_relativo: str) -> Path:
    """Resolve o nome dentro da pasta de fotos, bloqueando '../'."""
    pasta = pasta_fotos().resolve()
    caminho = (pasta / nome_relativo).resolve()
    if pasta not in caminho.parents or not caminho.is_file():
        raise FileNotFoundError(nome_relativo)
    return caminho


def gerar_previa(nome_relativo: str, largura_max: int = 900, texto: str = "AMOSTRA") -> bytes:
    """Gera um JPEG reduzido com marca d'água para mostrar antes do pagamento."""
    img = _ler_imagem_arquivo(caminho_foto_seguro(nome_relativo))
    if img is None:
        raise FileNotFoundError(nome_relativo)

    h, w = img.shape[:2]
    if w > largura_max:
        img = cv2.resize(img, (largura_max, int(h * largura_max / w)), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]

    camada = img.copy()
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    escala = w / 500
    espessura = max(2, int(escala * 2))
    (tw, th), _ = cv2.getTextSize(texto, fonte, escala, espessura)
    passo_x, passo_y = tw + int(w * 0.15), th + int(h * 0.12)
    for linha, y in enumerate(range(th, h + th, passo_y)):
        deslocamento = (passo_x // 2) * (linha % 2)
        for x in range(-deslocamento, w, passo_x):
            cv2.putText(camada, texto, (x, y), fonte, escala, (255, 255, 255), espessura, cv2.LINE_AA)
    img = cv2.addWeighted(camada, 0.35, img, 0.65, 0)

    ok, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ok:
        raise ValueError("Falha ao gerar a prévia.")
    return buffer.tobytes()
