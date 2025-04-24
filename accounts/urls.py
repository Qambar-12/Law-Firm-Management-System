from django.urls import path
from . import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('firm_signup/', views.firm_signup, name='firm_signup'),
    path('firm_login/', views.firm_login, name='firm_login'),

]
