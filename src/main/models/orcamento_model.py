"""Modelo de orçamento para o site do fotógrafo."""
from django.db import models
from django.urls import reverse

from main.models.pacote_model import Pacote


class Orcamento(models.Model):
    """Orçamento solicitado pelo visitante."""

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("processando", "Em Processamento"),
        ("concluido", "Concluído"),
        ("cancelado", "Cancelado"),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    pacote = models.ForeignKey(
        Pacote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos",
        verbose_name="Pacote desejado",
    )
    mensagem = models.TextField(verbose_name="Mensagem", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ["-criado_em"]

    def get_absolute_url(self):
        return reverse("orcamento")

    def __str__(self):
        return f"Orçamento de {self.nome}"
