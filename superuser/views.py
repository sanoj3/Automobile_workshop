from django.shortcuts import render, redirect, get_object_or_404
from .models import Superadmin
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password

from mechanic.models import Mechanic, StockManagement, Active_mechanic
from customer.models import Customer, Vehicle

def check_superuser_access(request):
    super_user_id = request.session.get('super_user_id')

    if not super_user_id:
        return None
    try:
        superuser = Superadmin.objects.get(id=super_user_id)
        return superuser
    except Superadmin.DoesNotExist:
        return None

def login_superuser(request):

    if request.session.get("super_user_id"):
        return redirect("home_page_superuser")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("login_superuser")

        try:
            super_user = Superadmin.objects.get(username=username)

            if not check_password(password, super_user.password):
                messages.error(request, "Invalid credentials.")
                return redirect("login_superuser")

            request.session["super_user_id"] = super_user.id
           

            messages.success(request, "Login successfully.")
            return redirect("home_page_superuser")

        except Superadmin.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect("login_superuser")

    return render(request, "login_superuser.html")


def logout_view_superuser(request):
    if 'super_user_id' in request.session:
        del request.session['super_user_id']
    return redirect('login_superuser')


def home_page_superuser(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')

    return render(request, 'home_admin.html', {
        'superuser': superuser
    })


def all_mechanic_applications(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanics = Mechanic.objects.filter(is_valid=False, is_reject=False)

    return render(request, 'all_mechanic_application.html',{
        'mechanics':mechanics
    })

def mechanic_application(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'mechanic_application.html',{
        'mechanic':mechanic
    })

def approve_mechanic(request,id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    mechanic.is_valid = True
    mechanic.save()
    messages.success(request, 'Application Successfully Approved.')
    return redirect('all_mechanic_applications')

def reject_mechanic(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)
    mechanic.is_reject = True
    mechanic.save()
    messages.success(request, 'Application Successfully Rejected!')
    return redirect('all_mechanic_applications')
    
def all_customer_detail(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    customers = Customer.objects.select_related('user','city')

    return render(request, 'all_customer_details.html',{
        'customers':customers
    })


def customer_detail(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    customer = get_object_or_404(Customer, id=id)
    vehicle = Vehicle.objects.filter(customer=customer)

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'vehicle': vehicle
    })

def all_mechanic_details(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_valid=True)

    return render(request, 'all_mechanic_details.html',{
        'mechanic':mechanic
    })

def mechanic_deatail(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)
    vehicle_parts = StockManagement.objects.filter(mechanic=mechanic)

    return render(request, 'mechanic_detail.html',{
        'mechanic': mechanic,
        'vehicle_parts': vehicle_parts
    })

def rejected_mechanics(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_reject=True)

    return render(request, 'rejected_mechanics.html',{
        'mechanic': mechanic
    })

def view_rejected_mechanic(request,id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'view_rejected_mechanic.html', {
        'mechanic': mechanic
    })

def profile_page_superuser(request):
    superuser =  check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    return render(request, 'profile_superuser.html', {
        'superuser' : superuser
    })

def profile_page_edit_superuser(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    if request.method == 'POST':
        superuser.email = request.POST.get('email')
        superuser.number = request.POST.get('number')


        if Superadmin.objects.filter(email=superuser.email).exclude(id=superuser.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile_superuser', id=superuser.id)


        if Superadmin.objects.filter(number=superuser.number).exclude(id=superuser.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('edit_profile_superuser', id=superuser.id)

        if request.FILES.get('profile_pic'):
            superuser.profile_pic = request.FILES.get('profile_pic')

        superuser.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_page_superuser')

    return render(request, 'edit_profile_superuser.html', {'superuser': superuser})


def profile_superuser_change_password(request):
    superuser= check_superuser_access(request)

    if not superuser:
        return redirect('login_superuser')
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(old_password, superuser.password):
            messages.error(request, 'Old password is incorrected')

        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")

        elif old_password == new_password:
            messages.error(request, 'Use different password.')
        
        else:
            superuser.password = make_password(new_password)
            superuser.save()

            messages.success(request, 'Password changed successfully.')
            return redirect('login_superuser')
    
    return render(request, 'profile_superuser_change_password.html')

def available_mechanic(request):
    superuser= check_superuser_access(request)

    if not superuser:
        return redirect('login_superuser')
    
    mechanics_status = Active_mechanic.objects.filter(
        is_online = True,
        is_available = True
    )
    return render(request, 'available_mechanic.html', {
        'mechanics_status': mechanics_status,

    })

def available_online(request):
    superuser= check_superuser_access(request)

    if not superuser:
        return redirect('login_superuser')
    
    mechanics_status = Active_mechanic.objects.filter(
        is_online = True
    )
    return render(request, 'available_online.html', {
        'mechanics_status' : mechanics_status
    })