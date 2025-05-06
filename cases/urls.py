from django.urls import path
from . import views
urlpatterns = [    
    path('add_case/', views.add_case, name='add_case'),
    path('firm_view_case/', views.firm_view_case, name='firm_view_case'),
    path('case/delete/<int:case_id>/', views.firm_delete_case, name='firm_delete_case'),
    path('firm_update_case/<int:case_id>/', views.firm_update_case, name='firm_update_case'),
    path('view_doc/<int:case_id>/', views.view_doc, name='view_doc'),
]