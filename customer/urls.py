
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.registration, name='register'),
    path('login/', views.user_login, name='login'),
    path('home/', views.home_page, name='home'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('add-vehicle/', views.vehicle_add, name='add_vehicle'),
    path('edit-vehicle/<int:id>/', views.edit_vehicle, name='edit_vehicle'),
    path('delete-vehicle/<int:id>/', views.delete_vehicle, name='delete_vehicle'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.profile_user, name='profile_user'),
    path('edit-profile/<int:id>/', views.profile_user_edit,name='edit_profile_user'),
    path('change-password/', views.profile_user_change_password,name='profile_user_change_password'),
    path('orders/', views.order_details, name='order_details'),
    path('orders/<int:id>/', views.order_view, name='order_view'),
    
]