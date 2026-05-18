from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_superuser, name='login_superuser'),
    path('home/', views.home_page_superuser, name='home_page_superuser'),
    path('mechanic-applications/', views.all_mechanic_applications, name='all_mechanic_applications'),
    path('application/<int:id>/', views.mechanic_application, name='mechanic_application'),
    path('approve-mechanic/<int:id>/', views.approve_mechanic, name='approve_mechanic'),
    path('reject-mechanic/<int:id>/', views.reject_mechanic, name='reject_mechanic'),
    path('customers-list/', views.all_customer_detail, name='all_customer_detail'),
    path('customer/<int:id>/', views.customer_detail, name='customer_detail'),
    path('mechanics-list/', views.all_mechanic_details, name='all_mechanic_details'),
    path('mechanic/<int:id>/', views.mechanic_deatail, name='mechanic_deatail'),
    path('rejected-mechanic/', views.rejected_mechanics, name='rejected_mechanics'),
    path('rejected-mechanic/<int:id>/', views.view_rejected_mechanic, name='view_rejected_mechanic'),
    path('logout/', views.logout_view_superuser, name='logout_view_superuser'),
    path('profile/', views.profile_page_superuser, name='profile_page_superuser'),
    path('edit-profile/<int:id>/', views.profile_page_edit_superuser, name='edit_profile_superuser'),
    path('change-password/', views.profile_superuser_change_password, name='profile_superuser_change_password'),
    path('avalable-mechanic/', views.available_mechanic, name='available_mechanic'),
    path('online-mechanic/', views.available_online, name='available_online'),
]