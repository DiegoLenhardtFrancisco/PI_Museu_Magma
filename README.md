![Logo do Museu Magma](static/img/logo.webp)

# Museu Magma - API de Gestão

![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge)

## 📌 Visão Geral

Este projeto é o backend **RESTful** para o sistema de gestão do Museu Magma. Originalmente uma aplicação monolítica, foi refatorada para uma arquitetura de microsserviços, onde este repositório serve como a API central. Ele é responsável por toda a lógica de negócio, gerenciamento de dados e autenticação, fornecendo endpoints JSON para serem consumidos por um frontend desacoplado (como React, Vue, Angular, etc.).

O sistema gerencia três pilares principais:

-   **Produtos:** Controle de inventário, categorias, preços e movimentações de estoque.
-   **Vendas:** Registro de vendas, clientes e itens de venda.
-   **Usuários:** Gerenciamento de diferentes tipos de usuários (Admin, Vendedor, Estoquista) com um sistema de permissões robusto.

## ✨ Principais Funcionalidades

A API oferece um conjunto completo de endpoints para gerenciar os recursos do museu:

-   **Autenticação:** Sistema seguro de login baseado em JWT (Access e Refresh tokens).
-   **Gerenciamento de Usuários:** CRUD completo para usuários, com permissões baseadas no tipo de usuário (`ADMIN`, `SELLER`, `STOCKCLERK`).
-   **Controle de Produtos:** Endpoints para criar, listar, atualizar e deletar produtos, com lógica para cálculo automático de preço de venda.
-   **Histórico de Estoque:** Endpoint de leitura para auditar todas as movimentações de estoque (entradas, saídas e ajustes).
-   **Gestão de Clientes:** CRUD completo para o cadastro de clientes.
-   **Registro de Vendas:** Endpoint para criar novas vendas, que automaticamente atualiza o estoque dos produtos vendidos.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído com as seguintes tecnologias e padrões:

-   **Backend:** Python 3.11+, Django, Django REST Framework.
-   **Banco de Dados:** PostgreSQL (produção), SQLite3 (desenvolvimento).
-   **Autenticação:** JSON Web Tokens (JWT) com a biblioteca `djangorestframework-simplejwt`.
-   **Documentação:** Geração automática de documentação interativa com `drf-spectacular` (Swagger UI / Redoc).
-   **Servidor de Produção:** Gunicorn.
-   **Qualidade de Código:** `Black`, `isort`, `Flake8` e `pre-commit` para garantir a padronização e a qualidade do código.

## 🚀 Instalação e Execução Local

Siga os passos abaixo para configurar e rodar o projeto no seu ambiente de desenvolvimento.

### Pré-requisitos

-   Python 3.11 ou superior
-   Git

### Passos para Instalação

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/DiegoLehardFerreira/PI_Museu_Magma.git](https://github.com/DiegoLehardFerreira/PI_Museu_Magma.git)
    cd PI_Museu_Magma
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    # Criar o ambiente
    python -m venv .venv

    # Ativar no Windows (Git Bash)
    source .venv/Scripts/activate

    # Ativar no Linux/macOS
    # source .venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto. O `.gitignore` já está configurado para ignorá-lo. Adicione as seguintes variáveis:

    ```env
    SECRET_KEY='gere_uma_chave_secreta_forte_aqui'
    DEBUG=True
    ```

5.  **Aplique as migrações do banco de dados:**

    ```bash
    python manage.py migrate
    ```

6.  **Configure os hooks de pre-commit (altamente recomendado):**
    Isso garantirá que seu código seja formatado e verificado antes de cada commit.

    ```bash
    pre-commit install
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    A API estará disponível em `http://127.0.0.1:8000`.

## 📚 Documentação da API (Swagger UI)

A melhor maneira de explorar e interagir com a API é através da nossa documentação interativa.

-   **Acesse a URL:** [**http://127.0.0.1:8000/api/v1/docs/**](http://127.0.0.1:8000/api/v1/docs/)

Nesta página, você pode:

-   Visualizar todos os endpoints disponíveis.
-   Ver os esquemas de dados (JSON) para requisições e respostas.
-   **Testar os endpoints diretamente do navegador**, incluindo o processo de autenticação.

## ✅ Executando os Testes

Para garantir a integridade e o correto funcionamento da aplicação, execute a suíte de testes automatizados:

```bash
python manage.py test
```
