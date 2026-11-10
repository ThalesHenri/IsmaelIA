"""URLs do app main."""
from django.urls import path

from main.views.page_views import home
from main.views.orcamento_view import orcamento
from main.views.pacote_view import pacote_detalhe, pacote_lista
from main.views.postagem_view import postagem_detalhe, postagem_lista
from main.views.digitalizacao_view import scan, resultado, sessao_demo
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home, name="home"),
    path("scan/", scan, name="scan"),
    path("resultado/<str:codigo>/", resultado, name="resultado"),
    path("demo/", sessao_demo, name="sessao_demo"),
    path("pacotes/", pacote_lista, name="pacote_lista"),
    path("pacotes/<slug:slug>/", pacote_detalhe, name="pacote_detalhe"),
    path("postagens/", postagem_lista, name="postagem_lista"),
    path("postagens/<slug:slug>/", postagem_detalhe, name="postagem_detalhe"),
    path("orcamento/", orcamento, name="orcamento"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
