from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Vehicle, City
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.


def registration(request):
    cities = City.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        password = request.POST.get('password')


        if User.objects.filter(username=email).exists():
            messages.error(request, 'Customer Already Exists.')
            return redirect('register')
        city_obj = City.objects.get(name=city)
        if Customer.objects.filter(number=number).exists():
            messages.error(request, 'Customer Already Exists.')
            return redirect('register')
        
        try :
            if transaction.atomic():
                user = User.objects.create_user(
                    username= email,
                    email =email,
                    password = password
                )

                Customer.objects.create(
                    user = user,
                    name = name,
                    number = number,
                    address = address,
                    city = city_obj
                )
                
                messages.success(request, 'Registration Successful')
                return redirect('login')
        except Exception as e :
            messages.error(request, 'An error occurred during registration.')
            return redirect('register')
        
    return render(request, 'register.html', {'city': cities})


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successfull')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    
    return render(request, 'login.html')


@login_required
def vehicle_add(request):
    if request.method == 'POST':

        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('home')

        Vehicle.objects.create(
            customer = customer,
            vehicle_name = request.POST.get('vehicle_name'),
            vehicle_model = request.POST.get('vehicle_model'),
            vehicle_year = request.POST.get('vehicle_year'),
            vehicle_number = request.POST.get('vehicle_number')
        )
        messages.success(request, 'Vehicle added successfully.')
        return redirect('vehicle_list')
    return render(request, 'add_vehicle.html')

@login_required
def vehicle_list(request):
    vehicles = request.user.customer.vehicles.all()
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})

@login_required
def edit_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id, customer=request.user.customer)

    if request.method == 'POST':
        vehicle.vehicle_name = request.POST.get('vehicle_name')
        vehicle.vehicle_model = request.POST.get('vehicle_model')
        vehicle.vehicle_year = request.POST.get('vehicle_year')
        vehicle.vehicle_number = request.POST.get('vehicle_number')

        vehicle.save()
        messages.success(request, "Vehicle updated successfully ✅")

        return redirect('vehicle_list')

    return render(request, 'edit_vehicle.html', {'vehicle': vehicle})


@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id, customer=request.user.customer)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully 🗑️")
        return redirect('vehicle_list')

    return redirect('vehicle_list')

@login_required
def logout_page(request):
    logout(request) 
    messages.success(request, "Logged out successfully 👋")
    return redirect('login')

@login_required
def home_page(request):
    customer = request.user.customer
    vehicle = customer.vehicles.all()

    return render(request, 'home.html', {
        'customer':customer,
        'vehicles':vehicle
    })

@login_required
def profile_user(request):
    customer = request.user.customer
    vehicles = customer.vehicles.all()

    return render(request, 'profile_user.html',{
        'customer':customer,
        'vehicles': vehicles
    })


@login_required
def profile_user_edit(request,id):
    customer = get_object_or_404(
        Customer,
        id=id,
        user= request.user
    )
    if request.method == "POST":
        customer.name = request.POST.get('name')
        number = request.POST.get('number')
        customer.address = request.POST.get('address')
        email = request.POST.get('email')

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile_user', id=customer.id)

        else:
            request.user.email = email
        if Customer.objects.filter(number=number).exclude(id=customer.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('edit_profile_user', id=customer.id)
        
        if request.FILES.get('profile_pic'):
            customer.profile_pic = request.FILES.get('profile_pic')
        
        customer.save()
        request.user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile_user')
    return render(request, 'edit_profile_user.html',{
        'customer':customer
    })

@login_required
def profile_user_change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrected')

        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")

        elif old_password == new_password:
            messages.error(request, 'Use different password.')
        
        else:
            request.user.set_password(new_password)
            request.user.save()

            messages.success(request, 'Password changed successfully.')
            return redirect('login')
    
    return render(request, 'profile_user_change_password.html')



        

        
        