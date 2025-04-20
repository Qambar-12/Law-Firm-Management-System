from django.urls import path
from . import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('firm/signup/', views.firm_signup, name='firm_signup'),
    path('firm/login/', views.firm_login, name='firm_login'),
   path('firm/dashboard/', views.firm_dashboard, name='firm_dashboard'),
]
