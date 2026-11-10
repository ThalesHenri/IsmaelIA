"""Modelo de pacote de serviço para o site do fotógrafo."""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Pacote(models.Model):
    """Pacote de serviços oferecido pelo fotógrafo."""

    nome = models.CharField(max_length=200, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    duracao = models.CharField(max_length=100, verbose_name="Duração", blank=True, null=True)
    incluindo = models.TextField(verbose_name="O que está incluído", blank=True, null=True)
    destaque = models.BooleanField(default=False, verbose_name="Destaque")
    foto = models.ImageField(upload_to="pacotes/", verbose_name="Foto", blank=True, null=True)
    slug = models.SlugField(max_length=250, unique=True, verbose_name="URL amigável")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Pacote"
        verbose_name_plural = "Pacotes"
        ordering = ["nome"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pacote_detalhe", kwargs={"slug": self.slug})

    def __str__(self):
        return self.nome
