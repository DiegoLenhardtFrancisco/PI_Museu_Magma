from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if user.tipo_usuario == 'ADMIN':
                return redirect(reverse('admin:index'))
            elif user.tipo_usuario == 'VENDEDOR':
                return redirect('vendas:venda_rapida')
            elif user.tipo_usuario == 'ESTOQUISTA':
                return redirect('produtos:base_produto')
        
        return render(request, 'usuarios/login_usuarios.html', {
            'error': 'Usuário ou senha inválidos'
        })
    
    return render(request, 'usuarios/login_usuarios.html')