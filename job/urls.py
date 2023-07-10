from django.urls import path
from . import views

urlpatterns = [
    path('create-job/',views.create_job,name='create-job'),
    path('update-job/<int:pk>/',views.update_job,name='update-job'),
    path('delete-job/<int:pk>/',views.delete_job,name='delete-job'),
    path('accept-job/<int:app_pk>/',views.accept_job,name='accept-job'),
    path('reject-job/<int:app_pk>/',views.reject_job,name='reject-job'),
    path('manage-jobs/',views.manage_jobs,name='manage-jobs'),
    path('apply-to-job/<int:pk>/', views.apply_to_job, name= 'apply-to-job'),
    path('all-applicants/<int:pk>/', views.all_applicants, name='all-applicants'), 
    path('applied-jobs/', views.applied_jobs, name='applied-jobs'),
    path('delete-application/<int:job_pk>/' , views.delete_application, name = 'delete-application')
]
