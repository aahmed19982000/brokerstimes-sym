from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('my_tasks/', views.my_tasks, name='my_tasks'),
    path('tasks/update-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('update_link/<int:task_id>/', views.update_article_link, name='update_article_link'),
    path('task/<int:task_id>/details/', views.task_details, name='task_details'),
    
    



    
]
