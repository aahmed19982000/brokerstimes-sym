from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_company, name='dashboard_company'),

    path('list/', views.company_list, name='company_list'),
    path('add/', views.add_company, name='add_company'),

    path('edit/<int:company_id>/', views.company_edit, name='company_edit'),
    path('delete/<int:company_id>/', views.company_delete, name='company_delete'),

    path('<int:company_id>/', views.company_details, name='company_details'),

]
