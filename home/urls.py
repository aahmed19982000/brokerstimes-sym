from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    


]
