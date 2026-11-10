"""Modelo de postagem de evento para o site do fotógrafo."""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Postagem(models.Model):
    """Postagem de foto de evento realizado pelo fotógrafo."""

    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    foto = models.ImageField(
        upload_to="postagens/",
        verbose_name="Foto do evento",
        blank=True,
        null=True,
    )
    data_evento = models.DateField(verbose_name="Data do evento", blank=True, null=True)
    categoria = models.CharField(max_length=100, verbose_name="Categoria", blank=True, null=True)
    slug = models.SlugField(max_length=250, unique=True, verbose_name="URL amigável")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Postagem"
        verbose_name_plural = "Postagens"
        ordering = ["-criado_em"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("postagem_detalhe", kwargs={"slug": self.slug})

    def __str__(self):
        return self.titulo
