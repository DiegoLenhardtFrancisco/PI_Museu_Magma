# CONTRIBUTING.md



## Nosso Workflow de Desenvolvimento

Todo desenvolvimento de novas funcionalidades ou correções de bugs deve seguir este fluxo:

### Passo 1: Pegar uma Tarefa (Issue)

1. Vá até a aba **Issues**.
2. Encontre uma tarefa disponível.
3. **Atribua a si mesmo** para indicar que está trabalhando nela.

### Passo 2: Preparar o Ambiente Local

```bash
git checkout develop
git pull origin develop
```

### Passo 3: Criar a Branch da Tarefa

**Padrão de nomes:** `tipo/id-da-issue-descricao-curta`
Exemplos:

* `feature/12-adicionar-login`
* `fix/7-corrigir-bug-layout`
* `style/18-melhorar-layout-login`
* `docs/5-atualizar-readme`

```bash
git checkout -b style/18-melhorar-layout-login
```

### Passo 4: Fazer Alterações e Commits

* Faça commits pequenos e com mensagens claras.
* Use o padrão de commits convencionais e vincule a issue: `Closes #18`.

```bash
git add .
git commit -m "style(login): Adjusts form alignment and colors" -m "Improves visual hierarchy on the login page. Closes #18"
```

### Passo 5: Enviar a Branch para o GitHub

```bash
git push -u origin style/18-melhorar-layout-login
```

### Passo 6: Abrir um Pull Request (PR)

1. Crie o PR apontando para a branch `develop`.
2. Dê um título claro e descreva as mudanças.
3. Adicione revisores.

### Passo 7: Revisão e Merge

* Revisores farão comentários e podem solicitar ajustes.
* Após aprovação, o merge é feito na `develop`.
* Delete sua branch local e remota para manter o repositório limpo.


---

### Padrões de Qualidade de Código

Para garantir a consistência, a legibilidade e a qualidade do código em todo o projeto, utilizamos um conjunto de ferramentas de formatação e linting. É um requisito que todo código submetido ao repositório esteja de acordo com estas regras, que são aplicadas automaticamente.

#### Ferramentas Utilizadas

  * **Black**: Para formatação automática de código.
  * **isort**: Para ordenação automática de imports.
  * **Flake8**: Para análise estática (linting) e verificação de erros lógicos e de estilo.
  * **pre-commit**: Para automatizar a execução dessas ferramentas antes de cada commit.

-----

#### 1\. Formatação com `black` e `isort`

Nós eliminamos debates sobre estilo de código ao adotar formatadores automáticos. Eles garantem que todo o código tenha uma aparência uniforme.

  * **`black`**: É o formatador de código intransigente. Ele reformata os arquivos para seguir um padrão estrito.
  * **`isort`**: Organiza os imports alfabeticamente e os separa em seções padronizadas.

As regras específicas para ambos estão definidas no arquivo `pyproject.toml`.

**Como rodar manualmente:**

```bash
# Com o ambiente virtual ativado
# Primeiro, organize os imports
isort .

# Depois, formate o restante do código
black .
```

-----

#### 2\. Análise de Qualidade com `Flake8`

Utilizamos o **`flake8`** para análise estática do código. Ele nos ajuda a encontrar erros lógicos, código não utilizado e a garantir que seguimos as convenções da PEP 8.

**Como verificar o código localmente:**

```bash
# Com o ambiente virtual ativado
flake8 .
```

As regras de configuração, como os arquivos a serem ignorados, estão definidas na seção `[flake8]` do arquivo `setup.cfg`.

-----

#### 3\. Automação com `pre-commit`

Para facilitar a vida de todos, configuramos o **`pre-commit`** para rodar `black`, `isort` e `flake8` automaticamente toda vez que você faz um commit.

Se alguma ferramenta modificar seus arquivos, o commit será interrompido. Basta você adicionar (`git add .`) os arquivos modificados e tentar fazer o commit novamente. Isso garante que apenas código limpo e padronizado chegue ao repositório.

**Como instalar (apenas uma vez):**

```bash
# Com o ambiente virtual ativado
pre-commit install
```

Depois disso, o processo é totalmente automático a cada `git commit`.