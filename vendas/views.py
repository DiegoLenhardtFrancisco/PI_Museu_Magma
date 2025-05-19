from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from .models import Venda, ItemVenda
from produtos.models import Produto

@login_required
def venda_rapida(request):
    carrinho = request.session.get('carrinho', [])
    
    # Pesquisa de produtos
    query = request.GET.get('q', '')
    produtos = Produto.objects.filter(ativo=True, margem_lucro__isnull=False).exclude(margem_lucro=0).order_by('nome')

    if query:
        produtos = produtos.filter(  
            Q(codigo__icontains=query) | 
            Q(nome__icontains=query)
        )

    # Adicionar produto ao carrinho (corrigido)
    if 'adicionar' in request.GET:
        try:
            produto_id = request.GET['adicionar']
            produto = Produto.objects.get(id=produto_id)
            preco_venda = float(produto.preco_venda)  # Convertendo Decimal para float
            
            item_existente = next((item for item in carrinho if item['produto_id'] == str(produto_id)), None)
            
            if item_existente:
                item_existente['quantidade'] += 1
                item_existente['subtotal'] = round(item_existente['quantidade'] * preco_venda, 2)
            else:
                carrinho.append({
                    'produto_id': str(produto.id),
                    'nome': produto.nome,
                    'quantidade': 1,
                    'preco': preco_venda,
                    'subtotal': preco_venda
                })
            
            request.session['carrinho'] = carrinho
        except Produto.DoesNotExist:
            messages.error(request, 'Produto não encontrado!')
        return redirect('vendas:venda_rapida')

    # Remover item do carrinho (mantido)
    if 'remover' in request.GET:
        produto_id = request.GET['remover']
        carrinho = [item for item in carrinho if item['produto_id'] != produto_id]
        request.session['carrinho'] = carrinho
        return redirect('vendas:venda_rapida')

    # Finalizar venda (seção corrigida)
    if request.method == 'POST':
        try:
            # Converter todos os valores para Decimal
            total_bruto = sum(Decimal(str(item['subtotal'])) for item in carrinho)
            desconto = Decimal(request.POST.get('desconto', 0))
            
            # Calcular custo total
            custo_total = Decimal(0)
            for item in carrinho:
                produto = Produto.objects.get(id=item['produto_id'])
                quantidade = Decimal(str(item['quantidade']))
                custo_total += produto.preco_custo * quantidade
            
            # Calcular margem
            margem_disponivel = total_bruto - custo_total
            
            # Validações
            if desconto < 0:
                raise ValueError("Desconto não pode ser negativo")
                
            if desconto > margem_disponivel:
                messages.error(request, f'Desconto máximo permitido: R$ {margem_disponivel:.2f}')
                return redirect('vendas:venda_rapida')

            total_venda = total_bruto - desconto

            # Verificar estoque
            for item in carrinho:
                produto = Produto.objects.get(id=item['produto_id'])
                if produto.quantidade < Decimal(str(item['quantidade'])):
                    messages.error(request, f"Estoque insuficiente: {produto.nome}")
                    return redirect('vendas:venda_rapida')

            with transaction.atomic():
                # Criar venda
                venda = Venda.objects.create(
                    usuario=request.user,
                    forma_pagamento=request.POST['forma_pagamento'],
                    status='F',
                    total=total_venda,
                    desconto=desconto,
                    custo_total=custo_total,
                    cliente=None,
                )

                # Criar itens
                for item in carrinho:
                    produto = Produto.objects.get(id=item['produto_id'])
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=Decimal(str(item['quantidade'])),
                        preco_unitario=Decimal(str(item['preco'])))
                    
                    # Atualizar estoque
                    produto.quantidade -= Decimal(str(item['quantidade']))
                    produto.save()

                # Limpar carrinho
                request.session['carrinho'] = []
                messages.success(request, f'Venda concluída: R$ {total_venda:.2f}')
                return redirect('vendas:venda_rapida')

        except (Produto.DoesNotExist, InvalidOperation, ValueError) as e:
            messages.error(request, f'Erro: {str(e)}')
            return redirect('vendas:venda_rapida')

    # Cálculos para exibição (convertendo para float)
    total_bruto = float(sum(Decimal(str(item['subtotal'])) for item in carrinho))
    custo_total = float(sum(
        Produto.objects.get(id=item['produto_id']).preco_custo * Decimal(str(item['quantidade']))
        for item in carrinho
    )) if carrinho else 0.0
    margem_disponivel = total_bruto - custo_total

    return render(request, 'vendas/venda_rapida.html', {
        'produtos': produtos,
        'carrinho': carrinho,
        'total_bruto': total_bruto,
        'margem_disponivel': margem_disponivel,
        'formas_pagamento': Venda.FORMA_PAGAMENTO_CHOICES
    })