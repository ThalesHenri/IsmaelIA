from django.contrib import admin

from .models.postagem_model import Postagem
from .models.pacote_model import Pacote
from .models.orcamento_model import Orcamento


@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    """Admin para postagens de eventos."""
    list_display = ("titulo", "data_evento", "categoria", "criado_em")
    list_filter = ("categoria", "criado_em")
    search_fields = ("titulo", "descricao")
    prepopulated_fields = {"slug": ("titulo",)}


@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    """Admin para pacotes de serviço."""
    list_display = ("nome", "preco", "destaque", "criado_em")
    list_filter = ("destaque", "criado_em")
    search_fields = ("nome", "descricao")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    """Admin para orçamentos."""
    list_display = ("nome", "email", "status", "criado_em")
    list_filter = ("status", "criado_em")
    search_fields = ("nome", "email", "mensagem")
    list_editable = ("status",)
