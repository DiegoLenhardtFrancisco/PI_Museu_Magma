from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'usuarios'  # Adicione isso para namespace

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/usuarios/login/'), name='logout'),

]