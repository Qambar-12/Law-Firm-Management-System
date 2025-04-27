from django.urls import path
from . import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('firm_signup/', views.firm_signup, name='firm_signup'),
    path('firm_login/', views.firm_login, name='firm_login'),
    path('firm_dashboard/', views.firm_dashboard, name='firm_dashboard'),
    path('firm_logout/', views.firm_logout, name='firm_logout'),
    path('add_lawyer/', views.add_lawyer, name='add_lawyer'),
    path('firm_view_lawyers/', views.firm_view_lawyers, name='firm_view_lawyers'),
    path('firm_delete_lawyer/<int:lawyer_id>/', views.firm_delete_lawyer, name='firm_delete_lawyer'),
    path('firm_update_lawyer/<int:lawyer_id>/', views.firm_update_lawyer, name='firm_update_lawyer'),
    path('add_case/', views.add_case, name='add_case'),
    path('firm_view_case/', views.firm_view_cases, name='firm_view_case'),
]
