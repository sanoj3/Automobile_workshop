from django.urls import path
from . import views

urlpatterns = [
    path('application-submitted/', views.check_mechanic_access, name='check_mechanic_access'),
    path('apply/', views.apply_mechanic, name='apply'),
    path('login/', views.login_mechanic, name='login_mechanic'),
    path('home/', views.home_page_mechanic, name='home_mechanic'),
    path('profile/', views.profile_page_mechanic, name='profile_page_mechanic'),
    path('edit-profile/<int:id>/', views.profile_page_edit_mechanic, name='profile_page_edit_mechanic'),
    path('change-password/', views.profile_mechanic_change_password, name='profile_mechanic_change_password'),
    path('logout/', views.logout_view_mechanic, name='logout_view_mechanic'),
    path('parts-list/', views.vehicle_parts_list, name='vehicle_parts_list'),
    path('add-vehicle-part/', views.add_vehicle_parts, name='add_vehicle_parts'),
    path('delete-vehicle-part/<int:id>/', views.delete_vehicle_parts, name='delete_vehicle_parts'),
    path('modify-vehicle-part/<int:id>/', views.modify_vehicle_parts, name='modify_vehicle_parts'),
    path('mechanic/toggle-status/', views.toggle_mechanic_status, name='toggle_mechanic_status'),
    path('pending-job/', views.pending_jobs_list, name='pending_jobs_list'),
    path('job/<int:id>/', views.pending_job, name='pending_job'),
    path('inprogress/<int:id>/', views.inprogress_status, name='inprogress_status'),
    path('completed-job/', views.completed_jobs_list, name='completed_jobs_list'),
    path('completed-job/<int:id>/', views.job_completed_view, name='job_completed_view'),
    path('bill-generate/<int:id>/', views.bill_generate, name='bill_generate'),
    path('complete-job/<int:id>/', views.complete_job, name='complete_job'),
    path('earnings/', views.earnings, name='earnings'),
]