from django.shortcuts import render, redirect, get_object_or_404
from .models import Mechanic, StockManagement
from customer.models import City
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# Create your views here.

def check_mechanic_access(request):
    mechanic_id = request.session.get('mechanic_id')

    if not mechanic_id:
        return None
    
    try:
        mechanic = Mechanic.objects.get(id=mechanic_id)

        if mechanic.is_reject:
            return 'reject'

        if not mechanic.is_valid:
            return 'not_valid'
        
        return mechanic
    
    except Mechanic.DoesNotExist:
        return None
    

def apply_mechanic(request):
    cities = City.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        certificate = request.FILES.get('certificate')  
        experience_certificate = request.FILES.get('experience_certificate')
        city_id = request.POST.get('city')
        city = City.objects.get(id=city_id)
        password = request.POST.get('password')

        required_fields = [name, email, number, certificate, city, password]
        if not all(required_fields):
            messages.error(request, 'All fields are required.')
            return redirect('apply')
        
        if Mechanic.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('apply')

        try:
            with transaction.atomic():
                Mechanic.objects.create(
                    name = name,
                    email = email,
                    number = number,
                    certificate = certificate,
                    experience_certificate = experience_certificate,
                    city = city,
                    password = make_password(password),
                    application_created_at = timezone.now()
                )
                messages.success(request, 'application submited.')
                return redirect('login_mechanic')
        
        except Exception as e :
            print(f"[DEBUG] Exception: {type(e).__name__}: {e}")
            messages.error(request, 'An error occurred during apply.')
            return redirect('apply')
    
    return render(request, 'apply.html', {'cities':cities})


def login_mechanic(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        required_fields = [email,password]

        if not all(required_fields):
            messages.error(request, 'email and password are required.')
            return redirect('login_mechanic')
        
        try:
            mechanic = Mechanic.objects.get(email=email)

            if not check_password(password, mechanic.password):
                messages.error(request, 'Invalid credentials.')
                return redirect('login_mechanic')
            
            request.session['mechanic_id'] = mechanic.id

            mechanic.last_login_date = timezone.now()
            mechanic.save()

            messages.success(request, 'Login successful.')
            return redirect('home_mechanic')
            
        except Mechanic.DoesNotExist:
            messages.error(request, 'Invalid credentials.')
            return redirect('login_mechanic')
        
    
    return render(request, 'login_mechanic.html')


def logout_view_mechanic(request):
    if 'mechanic_id' in request.session:
        del request.session['mechanic_id']
    return redirect('login_mechanic')


def home_page_mechanic(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    return render(request, 'home_mechanic.html', {
        'mechanic': mechanic
    })
 
def profile_page_mechanic(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    return render(request, 'profile_mechanic.html', {
        'mechanic': mechanic
    })

def profile_page_edit_mechanic(request, id):

    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    if request.method == 'POST':

        mechanic.email = request.POST.get('email')
        mechanic.number = request.POST.get('number')


        if Mechanic.objects.filter(email=mechanic.email).exclude(id=mechanic.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile_user', id=mechanic.id)


        if Mechanic.objects.filter(number=mechanic.number).exclude(id=mechanic.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('edit_profile_user', id=mechanic.id)

        if request.FILES.get('profile_pic'):
            mechanic.profile_pic = request.FILES.get('profile_pic')

        mechanic.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_page_mechanic')

    return render(request, 'edit_profile_mechanic.html', {'mechanic': mechanic})



def profile_mechanic_change_password(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(old_password, mechanic.password):
            messages.error(request, 'Old password is incorrected')

        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")

        elif old_password == new_password:
            messages.error(request, 'Use different password.')
        
        else:
            mechanic.password = make_password(new_password)
            mechanic.save()

            messages.success(request, 'Password changed successfully.')
            return redirect('login_mechanic')
    
    return render(request, 'profile_mechanic_change_password.html')


def vehicle_parts_list(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')
    
    stockes = StockManagement.objects.filter(mechanic=mechanic)

    return render(request, 'vehicle_parts_list.html', {
        'mechanic': mechanic,
        'stockes' : stockes
    })


def add_vehicle_parts(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')
    
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        stock_pic = request.FILES.get('stock_pic')

        required_fields = [item_name, price, quantity]

        if not all(required_fields):
            messages.error(request, 'required fields are must be entered.')
            return redirect('vehicle_parts_list')
        
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messages.error(request, 'Invalid price or quantity.')
            return redirect('vehicle_parts_list')
        
        StockManagement.objects.create(
            mechanic = mechanic,
            item_name = item_name,
            price = price,
            quantity = quantity,
            stock_pic = stock_pic
        )

        messages.success(request, 'Vehicle spare parts successfully created.')
        return redirect('vehicle_parts_list')
    
    return render(request, 'add_vehicle_parts.html')

def delete_vehicle_parts(request, id):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')
    
    parts = get_object_or_404(StockManagement, id=id, mechanic=mechanic)

    if request.method == 'POST':
        parts.delete()
        messages.success(request,'Vehicle spare part deleted successfully 🗑️')
        return redirect('vehicle_parts_list')
    
    return redirect('vehicle_parts_list')



def modify_vehicle_parts(request, id):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')
    
    parts = get_object_or_404(
        StockManagement,
        id=id,
        mechanic=mechanic
    )

    # Update Vehicle Part
    if request.method == 'POST':

        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        stock_pic = request.FILES.get('stock_pic')

        # Validation
        if not item_name or not price or not quantity:
            messages.error(request, 'All required fields must be entered.')
            return redirect('modify_vehicle_parts', id=id)

        try:
            price = float(price)
            quantity = int(quantity)

        except ValueError:
            messages.error(request, 'Invalid price or quantity.')
            return redirect('modify_vehicle_parts', id=id)

        # Update Data
        parts.item_name = item_name
        parts.price = price
        parts.quantity = quantity

        # Update Image Only If Uploaded
        if stock_pic:
            parts.stock_pic = stock_pic

        parts.save()

        messages.success(
            request,
            'Vehicle parts updated successfully ✅'
        )

        return redirect('vehicle_parts_list')

    return render(request, 'modify_vehicle_parts.html', {
        'parts': parts
    })
