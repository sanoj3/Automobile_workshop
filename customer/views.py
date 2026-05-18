from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Vehicle, City
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import re
from datetime import datetime
# Create your views here.

#..............................................................................................
#............. Main Email Validation.............
def email_validation(email):
    if not email:
        return 'Email is required.'
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern,email):
        return 'Enter a valid email address.'
    return None

#.............Main Password Validationn.............
def password_validation(password):
    if not password:
        return 'Password is required.'
    if len(password)<6:
        return 'Password must be at least 6 characters.'
    return None
    
#.............Main Name Validation.............
def name_validation(name):   
    if not name:
        return 'Name is required.'
    if len(name) < 3:
        return 'Name must be at least 3 characters.'
    if not re.match(r'^[A-Za-z]+$', name):
        return 'Name should contain only letters.'
    return None
    
#.............Main Number Validation.............
def number_validation(number):
    if not number:
        return 'Number is required.'
    if not number.isdigit():
        return 'Phone number should contain only digits.'
    if len(number) != 10:
        return 'Phone number must be 10 digits.'
    return None
 #..............................................................................................            

#.............User Registration.............
def registration(request):
    cities = City.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        password = request.POST.get('password')

        #.............Name Validation.............
        name_error = name_validation(name)
        if name_error:
            messages.error(request, name_error)
            return redirect('register')
        
        #.............Email Validation.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('register')
        
        #.............Number Validation.............
        number_error = number_validation(number)
        if number_error:
            messages.error(request, number_error)
            return redirect('register')
        
        #.............Password Validation.............
        password_error = password_validation(password)
        if password_error:
            messages.error(request, password_error)
            return redirect('register')

        #.............Existing User Check Validation.............
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Customer Already Exists.')
            return redirect('register')
        
        if Customer.objects.filter(number=number).exists():
            messages.error(request, 'Customer Already Exists.')
            return redirect('register')
        
        #.............City Object.............
        try:
            city_obj = City.objects.get(name=city)
        except City.DoesNotExist:
            messages.error(request, 'Invalid city selected.')
            return redirect('register')
        
        #.............Save Data.............
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

#.............User Login.............
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        #.............Email Validation.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('login')
        
        #.............Password Validation.............
        password_error = password_validation(password)
        if password_error:
            messages.error(request, password_error)
            return redirect('login')

        #.............User Authenticate.............
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successfull')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    
    return render(request, 'login.html')

#..............................................................................................
#.............Main Vehicle Name Validation.............
def vehicle_name_validation(vehicle_name):
    vehicle_name = vehicle_name.strip()
    if not vehicle_name:
        return 'Vehicle name is required.'
    if len(vehicle_name)<2:
        return 'Vehicle name must be at least 2 characters.'
    return None

#.............Main Vehicle Model Validation.............
def vehicle_model_validation(vehicle_model):
    if not vehicle_model:
        return 'Vehicle model is required.'
    return None

#.............Main Vehicle Year Validation.............
def vehicle_year_validation(vehicle_year):
    if not vehicle_year:
        return 'Vehicle year is required.'
    if not vehicle_year.isdigit():
        return 'Vehicle year must contain only numbers.'
    current_year = datetime.now().year
    if int(vehicle_year)<1970 or int(vehicle_year)>current_year:
        return f'Enter a valid year between 1970 and {current_year}.'
    return None

#.............Main Vehicle Number Validation.............
def vehicle_number_validation(vehicle_number):
    if not vehicle_number:
        return 'Vehicle number is required.'
    vehicle_number = vehicle_number.upper()
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
    if not re.match(pattern, vehicle_number):
        return 'Enter a valid vehicle number.'
    return None
#..............................................................................................

#.............User Vehicle Add.............
@login_required
def vehicle_add(request):
    if request.method == 'POST':
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('home')
        
        vehicle_name = request.POST.get('vehicle_name')
        vehicle_model = request.POST.get('vehicle_model')
        vehicle_year = request.POST.get('vehicle_year')
        vehicle_number = request.POST.get('vehicle_number')

        #.............Vehicle Name Validate.............
        vehicle_name_error = vehicle_name_validation(vehicle_name)
        if vehicle_name_error:
            messages.error(request, vehicle_name_error)
            return redirect('add_vehicle')
        
        #.............Vehicle Model Validate.............
        vehicle_model_error = vehicle_model_validation(vehicle_model)
        if vehicle_model_error:
            messages.error(request, vehicle_model_error)
            return redirect('add_vehicle')

        #.............Vehicle Year Validate.............
        vehicle_year_error = vehicle_year_validation(vehicle_year)
        if vehicle_year_error:
            messages.error(request, vehicle_year_error)
            return redirect('add_vehicle')
        
        #.............Vehicle Number Validate.............
        vehicle_number_error = vehicle_number_validation(vehicle_number)
        if vehicle_number_error:
            messages.error(request, vehicle_number_error)
            return redirect('add_vehicle')
        
        #.............Duplicate Vehicle Check.............
        if Vehicle.objects.filter(vehicle_number=vehicle_number).exists():
            messages.error(request, 'Vehicle already exists.')
            return redirect('add_vehicle')


        Vehicle.objects.create(
            customer = customer,
            vehicle_name = vehicle_name,
            vehicle_model = vehicle_model,
            vehicle_year = vehicle_year,
            vehicle_number = vehicle_number.upper()
        )
        messages.success(request, 'Vehicle added successfully.')
        return redirect('vehicle_list')
    return render(request, 'add_vehicle.html')

#.............User All Vehicle List.............
@login_required
def vehicle_list(request):
    vehicles = request.user.customer.vehicles.all()
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})

#.............User Vehicle Edit.............
@login_required
def edit_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id, customer=request.user.customer)

    if request.method == 'POST':
        vehicle_name = request.POST.get('vehicle_name','').strip()
        vehicle_model = request.POST.get('vehicle_model','').strip()
        vehicle_year = request.POST.get('vehicle_year','').strip()
        vehicle_number = request.POST.get('vehicle_number','').strip().upper()

        #.............Vehicle Name Validate.............
        vehicle_name_error = vehicle_name_validation(vehicle_name)
        if vehicle_name_error:
            messages.error(request, vehicle_name_error)
            return redirect('edit_vehicle',id=id)
        
        #.............Vehicle Model Validate.............
        vehicle_model_error = vehicle_model_validation(vehicle_model)
        if vehicle_model_error:
            messages.error(request, vehicle_model_error)
            return redirect('edit_vehicle',id=id)

        #.............Vehicle Year Validate.............
        vehicle_year_error = vehicle_year_validation(vehicle_year)
        if vehicle_year_error:
            messages.error(request, vehicle_year_error)
            return redirect('edit_vehicle',id=id)
        
        #.............Vehicle Number Validate.............
        vehicle_number_error = vehicle_number_validation(vehicle_number)
        if vehicle_number_error:
            messages.error(request, vehicle_number_error)
            return redirect('edit_vehicle',id=id)
        
        vehicle.vehicle_name = vehicle_name
        vehicle.vehicle_model = vehicle_model
        vehicle.vehicle_year = vehicle_year
        vehicle.vehicle_number = vehicle_number

        vehicle.save()
        messages.success(request, "Vehicle updated successfully ✅")

        return redirect('vehicle_list')

    return render(request, 'edit_vehicle.html', {'vehicle': vehicle})


#.............User Vehicle Delete.............
@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id, customer=request.user.customer)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully 🗑️")
        return redirect('vehicle_list')

    return redirect('vehicle_list')

#.............User Logout.............
@login_required
def logout_page(request):
    logout(request) 
    messages.success(request, "Logged out successfully 👋")
    return redirect('login')

#.............User Home Page.............
@login_required
def home_page(request):
    customer = request.user.customer
    vehicle = customer.vehicles.all()

    return render(request, 'home.html', {
        'customer':customer,
        'vehicles':vehicle
    })

#.............User Profile Page.............
@login_required
def profile_user(request):
    customer = request.user.customer
    vehicles = customer.vehicles.all()

    return render(request, 'profile_user.html',{
        'customer':customer,
        'vehicles': vehicles
    })

#.............User Edit Profile.............
@login_required
def profile_user_edit(request,id):
    customer = get_object_or_404(
        Customer,
        id=id,
        user= request.user
    )
    if request.method == "POST":
        name = request.POST.get('name')
        number = request.POST.get('number')
        address = request.POST.get('address')
        email = request.POST.get('email')

        #.............Name Validation.............
        name_error = name_validation(name)
        if name_error:
            messages.error(request, name_error)
            return redirect('edit_profile_user',id=customer.id)
        
        #.............Number Validation.............
        number_error = number_validation(number)
        if number_error:
            messages.error(request, number_error)
            return redirect('edit_profile_user',id=customer.id)
        
        #.............Email Validation.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('edit_profile_user',id=customer.id)

        #.............Email Existing Check.............
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile_user', id=customer.id)

        #.............Number Existing Check............. 
        if Customer.objects.filter(number=number).exclude(id=customer.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('edit_profile_user', id=customer.id)
        
        #.............Update Data.............
        customer.name = name
        customer.number = number
        customer.address = address
        request.user.email = email

        #.............Profile Image.............
        if request.FILES.get('profile_pic'):
            customer.profile_pic = request.FILES.get('profile_pic')
        
        customer.save()
        request.user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile_user')
    return render(request, 'edit_profile_user.html',{
        'customer':customer
    })

#.............User Password Change(Profile Page).............
@login_required
def profile_user_change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # .............OLD PASSWORD CHECK.............
        if not old_password:
            messages.error(request, 'Old password is required.')
            return redirect('profile_user_change_password')
        
        if not new_password:
            messages.error(request, 'New password is required.')
            return redirect('profile_user_change_password')
        
        if not confirm_password:
            messages.error(request, 'Confirm password is required.')
            return redirect('profile_user_change_password')

        # .............Old Password Check.............
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile_user_change_password')

        # .............New and Confirm Password Check.............
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('profile_user_change_password')

        # .............Same Password Check.............
        if old_password == new_password:
            messages.error(request, 'Use different password.')
            return redirect('profile_user_change_password')
        
        # .............Password Length Check.............
        if len(new_password)<6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('profile_user_change_password')
        
        # .............Update Password.............
        request.user.set_password(new_password)
        request.user.save()

        messages.success(request, 'Password changed successfully.')
        return redirect('login')
    
    return render(request, 'profile_user_change_password.html')



        

        
        