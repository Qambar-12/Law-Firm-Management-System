from django.urls import path
from . import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('firm_signup/', views.firm_signup, name='firm_signup'),
    path('firm_login/', views.firm_login, name='firm_login'),
    path('<str:role>_login/', views.user_login, name='user_login'),
    path('firm_dashboard/', views.firm_dashboard, name='firm_dashboard'),
    path('firm_logout/', views.firm_logout, name='firm_logout'),
    path('lawyer_dashboard/', views.lawyer_dashboard, name='lawyer_dashboard'),
    path('lawyer_logout/', views.lawyer_logout, name='lawyer_logout'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client_logout/', views.client_logout, name='client_logout'),
    path('add_lawyer/', views.add_lawyer, name='add_lawyer'),
    path('firm_view_lawyers/', views.firm_view_lawyers, name='firm_view_lawyers'),
    path('firm_delete_lawyer/<int:lawyer_id>/', views.firm_delete_lawyer, name='firm_delete_lawyer'),
    path('firm_update_lawyer/<int:lawyer_id>/', views.firm_update_lawyer, name='firm_update_lawyer'),
    path('lawyer/<int:lawyer_id>/cases/', views.firm_lawyer_cases, name='firm_lawyer_cases'),
]
