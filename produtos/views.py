from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntradaProdutoForm, ProductForm
from .models import MovimentacaoEstoque, Product


@login_required
def base_produto(request):
    """
    View de base/template inicial do módulo de produtos.
    """
    return render(request, 'produtos/base_produto.html')


@login_required
def criar_produto(request):
    """
    Cria um novo produto com código sequencial e registra o usuário.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            ultimo_produto = Product.objects.order_by('-codigo').first()
            novo_codigo = (
                str(int(ultimo_produto.code) + 1).zfill(6)
                if ultimo_produto
                else '000001'
            )
            produto = form.save(commit=False)
            produto.codigo = novo_codigo
            produto.usuario = request.user
            produto.save()
            return redirect('produtos:entrada_produto')
    else:
        ultimo_produto = Product.objects.order_by('-codigo').first()
        novo_codigo = (
            str(int(ultimo_produto.code) + 1).zfill(6) if ultimo_produto else '000001'
        )
        form = ProductForm(initial={'codigo': novo_codigo})

    return render(request, 'produtos/form_produto.html', {'form': form})


@login_required
def entrada_produto(request):
    """
    Atualiza estoque de um produto já cadastrado.
    """
    produto = None
    form = None

    if request.method == 'POST':
        if 'atualizar' in request.POST:
            codigo = request.POST.get('codigo_produto')
            produto = get_object_or_404(Product, codigo=codigo)
            form = EntradaProdutoForm(request.POST, request.FILES)

            if form.is_valid():
                produto.supplier = form.cleaned_data['fornecedor']
                produto.cost_price = form.cleaned_data['preco_custo']
                produto.ativo = form.cleaned_data['ativo']
                produto.endereco_estoque = form.cleaned_data['endereco_estoque']
                produto.quantity += form.cleaned_data['quantidade']

                if form.cleaned_data.get('imagem'):
                    produto.imagem = form.cleaned_data['imagem']

                produto.usuario = request.user
                produto.save()

                messages.success(request, 'Produto atualizado com sucesso!')
                return redirect('produtos:entrada_produto')

        else:
            busca = request.POST.get('busca', '').strip()
            if busca:
                produto = Product.objects.filter(
                    Q(codigo__icontains=busca) | Q(nome__icontains=busca)
                ).first()
                if produto:
                    form = EntradaProdutoForm(
                        initial={
                            'fornecedor': produto.supplier,
                            'preco_custo': produto.cost_price,
                            'ativo': produto.ativo,
                            'endereco_estoque': produto.endereco_estoque,
                        }
                    )
                else:
                    messages.error(request, "Produto não encontrado.")

    return render(
        request,
        'produtos/entrada_produto.html',
        {
            'form': form,
            'produto': produto,
        },
    )


@login_required
def historico_individual(request):
    """
    Exibe o histórico de movimentações de um produto específico.
    """
    query = request.GET.get('q', '').strip()
    produto = None
    movimentacoes = []

    if query:
        produto = Product.objects.filter(
            Q(nome__icontains=query) | Q(codigo__icontains=query)
        ).first()

        if produto:
            movimentacoes = MovimentacaoEstoque.objects.filter(
                produto=produto
            ).order_by('-data_movimentacao')

    return render(
        request,
        'produtos/historico_individual.html',
        {
            'produto': produto,
            'movimentacoes': movimentacoes,
            'query': query,
        },
    )


@login_required
def relatorio_inventario(request):
    """
    Gera e atualiza o relatório de inventário (estoque atual).
    """
    produtos = Product.objects.all()

    # Filtros de busca GET
    cod_de = request.GET.get('cod_de')
    cod_ate = request.GET.get('cod_ate')
    codigos = request.GET.get('codigos')

    if cod_de and cod_ate:
        produtos = produtos.filter(codigo__gte=cod_de, codigo__lte=cod_ate)

    if codigos:
        lista_codigos = [c.strip() for c in codigos.split(',') if c.strip()]
        produtos = produtos.filter(codigo__in=lista_codigos)

    # Ajuste de inventário via POST
    if request.method == 'POST':
        codigo = request.POST.get('codigo_produto')
        nova_quantidade = request.POST.get('nova_quantidade')

        if codigo and nova_quantidade:
            try:
                nova_quantidade = Decimal(nova_quantidade)
                if nova_quantidade < 0:
                    raise ValueError("Quantidade negativa")

                produto = Product.objects.get(codigo=codigo)
                quantidade_anterior = produto.quantity  # Captura o valor anterior

                if produto.quantity != nova_quantidade:
                    produto.quantity = nova_quantidade
                    produto._from_inventario_adjustment = True
                    produto.usuario = request.user
                    produto.save()

                    # Mensagem atualizada com valores antigo e novo
                    messages.success(
                        request,
                        f"Inventário de '{produto.name}' ajustado de {quantidade_anterior} para {nova_quantidade}.",
                    )
                else:
                    messages.info(
                        request,
                        f"Quantidade de '{produto.name}' já está em {nova_quantidade}. Nenhum ajuste necessário.",
                    )

                return redirect('produtos:relatorio_inventario')

            except (Product.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, f"Erro: {str(e)}")

    return render(request, 'produtos/relatorio_inventario.html', {'produtos': produtos})
