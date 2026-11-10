# FotoComigo — Site do Fotógrafo

Site responsivo construído com **Django 5.2** para um fotógrafo profissional.
O site visa apresentar os pacotes de serviço, publicar fotografias de eventos
com descrições e permitir que visitantes solicitem orçamentos.

## Funcionalidades

- **Página inicial (landing)** — apresentação da proposta, cards dos pacotes em destaque e eventos recentes;
- **Seção de pacotes** — listagem de todos os pacotes com preço, duração e o que está incluído, além do detalhe de cada um;
- **Seção de eventos** — postagens com fotos de eventos, data, categoria e descrição, com tela de detalhe;
- **Solicitação de orçamento** — formulário que salva um orçamento no banco e exibe mensagens de feedback;
- **Área do admin** — cadastro de postagens, pacotes e orçamentos (Django admin).

## Estrutura do projeto

```
src/
├── manage.py
├── siteDjango/            # Configuração do projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── main/                  # Aplicativo principal
    ├── models/            # Modelos: Postagem, Pacote, Orçamento
    ├── services/          # Lógica de negócio: postagem, pacote, orçamento
    ├── views/             # Views: home, pacote, postagem, orcamento
    ├── templates/main/    # Templates HTML
    ├── static/css/        # Estilos globais
    ├── admin.py
    ├── apps.py
    ├── urls.py            # Roteamento das páginas
    ├── migrations/        # Migrations geradas
    └── tests.py
```

## Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd src

# 2. Criar um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install django

# 4. aplicar as migrations
python manage.py makemigrations
python manage.py migrate

# 5.Rodar o servidor de desenvolvimento
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

## Uso do painel administrativo

```bash
python manage.py createsuperuser
```

 Acesse `http://127.0.0.1:8000/admin/` e faça login com o usuário criado para
 cadastrar **Pacotes**, **Postagens** (fotografias de eventos) e **Orçamentos**.

## Camada de apresentação (templates)

Os templates utilizados são:

- `base.html` — layout com cabeçalho, navegação e rodapé;
- `index.html` — página inicial com hero, sobre, pacotes e eventos;
- `pacotes.html` — listagem dos pacotes;
- `pacote_detalhe.html` — detalhe de um pacote;
- `postagens.html` — listagem dos eventos;
- `postagem_detalhe.html` — detalhe de uma postagem;
- `orcamento.html` — formulário de solicitação de orçamento.

## Estrutura dos modelos

### Postagem
- `titulo` — título da postagem;
- `descricao` — descrição da fotografia do evento;
- `foto` — imagem do evento;
- `data_evento` — data do evento;
- `categoria` — categoria do evento;
- `slug` — URL amigável gerada automaticamente.

### Pacote
- `nome` — nome do pacote;
- `descricao` — descrição do pacote;
- `preco` — valor do pacote;
- `duracao` — duração do serviço;
- `incluindo` — o que está incluído;
- `destaque` — indica se o pacote está em destaque.

### Orçamento
- `nome` — nome do solicitante;
- `email` — e-mail de contato;
- `telefone` — telefone de contato;
- `pacote` — pacote desejado (opcional);
- `mensagem` — mensagem adicional;
- `status` — status do orçamento (Pendente, Em Processamento, Concluído, Cancelado).

## Licença

Este projeto é um site pessoal de demonstração.
