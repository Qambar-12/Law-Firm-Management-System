from django.urls import path
from . import views

urlpatterns = [
    path('case/<int:case_id>/timelogs/', views.case_timelogs_view, name='case_timelogs'),
    path('case/<int:case_id>/start/', views.start_timer_view, name='start_timer'),
    path('case/<int:case_id>/stop/', views.stop_timer_view, name='stop_timer'),
    path('firm/case/<int:case_id>/logs/', views.case_logs_for_invoice, name='case_logs_for_invoice'),
    path('firm/case/<int:case_id>/generate_invoice/', views.generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
]
