"""Modelos para digitalização facial de clientes em eventos."""
from django.db import models
from django.utils.crypto import get_random_string


class EventoDigitalizacao(models.Model):
    """Evento em que clientes podem escanear o rosto para encontrar fotos."""
    nome = models.CharField(max_length=200, verbose_name="Nome do evento")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="URL amigável")
    data = models.DateField(verbose_name="Data do evento")
    local = models.CharField(max_length=200, blank=True, verbose_name="Local")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Digitalização"
        verbose_name_plural = "Eventos de Digitalização"
        ordering = ["-data"]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class FotoEvento(models.Model):
    """Foto de um evento (arquivo original protegido)."""
    evento = models.ForeignKey(
        EventoDigitalizacao,
        on_delete=models.CASCADE,
        related_name="fotos_evento",
        verbose_name="Evento",
    )
    imagem = models.ImageField(upload_to="eventos/fotos/", verbose_name="Imagem")
    legenda = models.CharField(max_length=200, blank=True, verbose_name="Legenda")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto do Evento"
        verbose_name_plural = "Fotos do Evento"

    def __str__(self):
        return self.legenda or f"Foto {self.id}"


class SessaoDigitalizacao(models.Model):
    """Sessão de escaneamento facial de um cliente em um evento."""
    evento = models.ForeignKey(
        EventoDigitalizacao,
        on_delete=models.CASCADE,
        related_name="sessoes",
        verbose_name="Evento",
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código da sessão",
        help_text="Código curto para compartilhar com o cliente",
    )
    nome_cliente = models.CharField(max_length=100, blank=True, verbose_name="Nome do cliente")
    total_fotos_encontradas = models.PositiveIntegerField(
        default=0, verbose_name="Total de fotos encontradas"
    )
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor total",
    )
    fotos_encontradas = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Fotos encontradas",
        help_text="Arquivos da pasta de fotos do evento em que o rosto do cliente aparece",
    )
    pago = models.BooleanField(default=False, verbose_name="Pago")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sessão de Digitalização"
        verbose_name_plural = "Sessões de Digitalização"
        ordering = ["-criado_em"]

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = get_random_string(8).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.evento.nome}"
