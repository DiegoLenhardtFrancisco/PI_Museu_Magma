# **Guia de Migração para a Nova API v1.0**

**Versão:** 1.0.0
**Data:** 10 de Setembro de 2025

#### **Sumário**
- [**Guia de Migração para a Nova API v1.0**](#guia-de-migração-para-a-nova-api-v10)
      - [**Sumário**](#sumário)
    - [**1. Visão Geral: O Que Mudou?**](#1-visão-geral-o-que-mudou)
    - [**2. Ferramentas Essenciais**](#2-ferramentas-essenciais)
    - [**3. Documentação Interativa (Swagger UI) - Sua Fonte da Verdade**](#3-documentação-interativa-swagger-ui---sua-fonte-da-verdade)
    - [**4. Fluxo de Autenticação com JWT (Passo a Passo)**](#4-fluxo-de-autenticação-com-jwt-passo-a-passo)
      - [**a) Como Fazer Login e Obter os Tokens**](#a-como-fazer-login-e-obter-os-tokens)
      - [**b) Onde Guardar os Tokens?**](#b-onde-guardar-os-tokens)
      - [**c) Como Usar o `access` Token**](#c-como-usar-o-access-token)
      - [**d) Como Renovar o `access` Token**](#d-como-renovar-o-access-token)
    - [**5. Mapeamento de Endpoints (De / Para)**](#5-mapeamento-de-endpoints-de--para)
    - [**6. Tratamento de Erros Padronizado**](#6-tratamento-de-erros-padronizado)
    - [**7. Exemplos Práticos**](#7-exemplos-práticos)
      - [**Exemplo 1: Criar um Novo Produto**](#exemplo-1-criar-um-novo-produto)
      - [**Exemplo 2: Criar um Cliente e depois uma Venda para ele**](#exemplo-2-criar-um-cliente-e-depois-uma-venda-para-ele)
    - [**8. Dúvidas Frequentes (FAQ)**](#8-dúvidas-frequentes-faq)


-----

### **1. Visão Geral: O Que Mudou?**

Estamos a fazer a transição de uma aplicação "monolítica" (onde o frontend e o backend estavam acoplados) para uma arquitetura moderna com um **backend de API REST** e um **frontend desacoplado**.

  * **Antes:** O servidor Django renderizava as páginas HTML diretamente.
  * **Agora:** O servidor Django (backend) apenas fornece dados em formato JSON. O frontend (aplicação em React, Vue, Angular, etc.) consome esses dados e é responsável por toda a lógica de apresentação.

Isso significa que o frontend agora será responsável por todas as chamadas de rede para buscar, criar, editar e excluir dados.

### **2. Ferramentas Essenciais**

Para interagir e testar os endpoints da API durante o desenvolvimento, recomendamos o uso de um cliente de API. Estas ferramentas permitem que você envie requisições para a API e veja as respostas de forma fácil.

  * [**Postman**](https://www.postman.com/downloads/): Uma ferramenta completa e muito popular para testes de API.
  * [**Insomnia**](https://insomnia.rest/download): Uma alternativa mais leve e com uma interface limpa.

### **3. Documentação Interativa (Swagger UI) - Sua Fonte da Verdade**

A documentação completa, interativa e sempre atualizada da nossa API está disponível no Swagger UI. **Este deve ser seu primeiro ponto de consulta.**

  * **URL da Documentação:** [http://127.0.0.1:8000/api/v1/docs/](https://www.google.com/search?q=http://127.0.0.1:8000/api/v1/docs/)

Lá você pode:

  * ✅ Ver todos os endpoints disponíveis, agrupados por categoria.
  * ✅ Consultar os detalhes de cada endpoint: método HTTP, URL, parâmetros.
  * ✅ Ver os formatos de dados (JSON) para envio e resposta.
  * ✅ **Executar e testar as requisições diretamente no navegador\!**

### **4. Fluxo de Autenticação com JWT (Passo a Passo)**

Abandonámos a autenticação baseada em sessão. Agora, usamos **JSON Web Tokens (JWT)**.

#### **a) Como Fazer Login e Obter os Tokens**

Envie o `username` e `password` do usuário para o endpoint `/token/`.

  * **Endpoint:** `POST /api/v1/token/`
  * **Exemplo de Requisição (JavaScript `fetch`):**
    ```javascript
    const response = await fetch('http://127.0.0.1:8000/api/v1/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'seller_username',
        password: 'user_password'
      })
    });

    if (response.ok) {
      const tokens = await response.json();
      console.log('Access Token:', tokens.access);
      console.log('Refresh Token:', tokens.refresh);
      // Agora, guarde estes tokens!
    } else {
      console.error('Falha no login!');
    }
    ```

#### **b) Onde Guardar os Tokens?**

Após o login, você precisa de guardar os tokens `access` e `refresh` no frontend.

  * **`localStorage`:** Persiste os dados mesmo após fechar o navegador. Bom para funcionalidades como "Lembrar de mim".
  * **`sessionStorage`:** Os dados são apagados quando a aba do navegador é fechada.
  * **Estado da Aplicação (Vuex, Redux, Pinia, etc.):** Se você usa uma biblioteca de gestão de estado, guarde os tokens lá.

#### **c) Como Usar o `access` Token**

Em cada requisição para um endpoint protegido, você deve enviar o `access` token no cabeçalho `Authorization`.

  * **Header:** `Authorization: Bearer <seu_access_token>`
  * **Exemplo (JavaScript `fetch`):**
    ```javascript
    const accessToken = localStorage.getItem('accessToken'); // Exemplo

    const response = await fetch('http://127.0.0.1:8000/api/v1/products/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    ```

#### **d) Como Renovar o `access` Token**

O `access` token tem vida curta. Quando ele expirar, a API retornará um erro `401 Unauthorized`. Nesse momento, use o `refresh` token para obter um novo `access` token sem que o usuário precise de fazer login novamente.

  * **Endpoint:** `POST /api/v1/token/refresh/`
  * **Corpo da Requisição:** `{ "refresh": "<seu_refresh_token>" }`

### **5. Mapeamento de Endpoints (De / Para)**

A tabela abaixo mapeia as funcionalidades principais para os novos endpoints da API.

| Funcionalidade | Endpoint da Nova API | Método HTTP | Permissões | Notas |
| :--- | :--- | :--- | :--- | :--- |
| **Login de Usuário** | `/api/v1/token/` | `POST` | Todos | Substitui o antigo formulário de login. |
| **Logout de Usuário** | - | - | Frontend | O logout agora é gerido no frontend (apagar os tokens). |
| **Listar Produtos** | `/api/v1/products/` | `GET` | Autenticado | Retorna lista paginada de produtos. |
| **Criar Produto** | `/api/v1/products/` | `POST` | Admin/Estoquista | Enviar os dados do produto no corpo da requisição. |
| **Ver Detalhes do Produto** | `/api/v1/products/{id}/` | `GET` | Autenticado | |
| **Atualizar Produto** | `/api/v1/products/{id}/` | `PUT` / `PATCH` | Admin/Estoquista | |
| **Excluir Produto** | `/api/v1/products/{id}/` | `DELETE` | Admin/Estoquista | |
| **Listar Mov. de Estoque** | `/api/v1/stock-movements/` | `GET` | Autenticado | Endpoint de histórico. Pode ser filtrado por produto. |
| **Listar Vendas** | `/api/v1/sales/` | `GET` | Vendedor/Admin | Vendedores veem apenas as suas vendas. Admins veem todas. |
| **Criar uma Venda** | `/api/v1/sales/` | `POST` | Vendedor/Admin | O corpo da requisição deve incluir `items_to_create`. |
| **Gerir Clientes** | `/api/v1/customers/` | `GET`, `POST`, `PUT`, `DELETE` | Autenticado | CRUD completo para clientes. |


### **6. Tratamento de Erros Padronizado**

A nova API usa um formato padronizado para respostas de erro, facilitando o tratamento no frontend.

**Exemplo de Erro de Validação (400 Bad Request):**

```json
{
  "errors": {
    "status_code": 400,
    "detail": {
      "cost_price": [
        "Ensure this value is greater than or equal to 0."
      ]
    },
    "code": "invalid"
  }
}
```

**Exemplo de Erro de Permissão (403 Forbidden):**

```json
{
  "errors": {
    "status_code": 403,
    "detail": "You do not have permission to perform this action.",
    "code": "permission_denied"
  }
}
```

### **7. Exemplos Práticos**

#### **Exemplo 1: Criar um Novo Produto**

Um usuário **Estoquista** quer criar um novo produto.

1.  **Montar o Payload:** O frontend coleta os dados do formulário.
    ```javascript
    const productData = {
        name: "Cristal de Quartzo",
        cost_price: "75.50",
        profit_margin: "100.00",
        quantity: "15",
        unit_of_measure: "UNIT",
        category: "MINERAL"
    };
    ```
2.  **Fazer a Requisição:** Envia os dados com o token de autenticação.
    ```javascript
    const response = await fetch('/api/v1/products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(productData)
    });
    ```
3.  **Tratar a Resposta:** Se a resposta for `201 Created`, o produto foi criado com sucesso. Se for `403 Forbidden`, o usuário não tem permissão.

#### **Exemplo 2: Criar um Cliente e depois uma Venda para ele**

Este exemplo mostra como encadear requisições.

1.  **Primeiro, crie o cliente:**

    ```javascript
    // POST para /api/v1/customers/ com os dados do cliente
    // e o header de autorização.
    const customerResponse = await fetch('/api/v1/customers/', { /* ... */ });
    const newCustomer = await customerResponse.json();
    const customerId = newCustomer.id; // Guarde o ID do novo cliente!
    ```

2.  **Depois, crie a venda usando o ID do cliente:**

    ```javascript
    const saleData = {
        customer: customerId, // Use o ID retornado pela primeira requisição
        payment_method: 'DEBIT',
        items_to_create: [
            { "product_id": 1, "quantity": "1.00" }
        ]
    };

    // POST para /api/v1/sales/ com os dados da venda.
    const saleResponse = await fetch('/api/v1/sales/', { /* ... */ });
    ```

### **8. Dúvidas Frequentes (FAQ)**

  * **P: O que é "Bearer" no cabeçalho `Authorization`?**

      * **R:** É o "esquema" ou tipo de token. Apenas significa "quem quer que possua este token (`Bearer`) está autorizado". É um padrão que deve ser seguido.

  * **P: Como sei qual `id` usar em URLs como `/api/v1/products/{id}/`?**

      * **R:** O `id` é o identificador único do objeto no banco de dados. Geralmente, você obtém este `id` ao listar os itens (ex: uma `GET` em `/api/v1/products/` retornará uma lista de produtos, cada um com seu `id`).

  * **P: O que significam os erros 401, 403 e 404?**

      * **R:** `401 Unauthorized`: Você não está autenticado ou o seu token expirou. Tente fazer login ou renovar o token.
      * **R:** `403 Forbidden`: Você está autenticado, mas o seu tipo de usuário (`SELLER`, `STOCKCLERK`) não tem permissão para realizar essa ação específica.
      * **R:** `404 Not Found`: O recurso que você tentou aceder (ex: um produto com um `id` que não existe) não foi encontrado.

  * **P: Preciso de enviar todos os campos de um objeto ao atualizar com `PATCH`?**

      * **R:** Não. O método `PATCH` é para atualizações parciais. Envie apenas os campos que você deseja alterar. Para `PUT`, você precisa de enviar o objeto completo.