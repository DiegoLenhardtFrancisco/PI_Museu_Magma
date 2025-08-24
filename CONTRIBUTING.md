# CONTRIBUTING.md

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