from django.shortcuts import render, redirect, get_object_or_404
from .models import Superadmin
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from mechanic.models import Mechanic, StockManagement
from customer.models import Customer, Vehicle



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
    superuser_id = request.session.get('super_user_id')

    if not superuser_id:
        return redirect('login_superuser')
    
    superuser = Superadmin.objects.get(id=superuser_id)


    return render(request, 'home_admin.html', {
        'superuser': superuser
    })


def all_mechanic_applications(request):
    mechanics = Mechanic.objects.filter(is_valid=False, is_reject=False)

    return render(request, 'all_mechanic_application.html',{
        'mechanics':mechanics
    })

def mechanic_application(request, id):
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'mechanic_application.html',{
        'mechanic':mechanic
    })

def approve_mechanic(request,id):
    mechanic = get_object_or_404(Mechanic, id=id)

    mechanic.is_valid = True
    mechanic.save()
    messages.success(request, 'Application Successfully Approved.')
    return redirect('all_mechanic_applications')

def reject_mechanic(request, id):
    mechanic = get_object_or_404(Mechanic, id=id)
    mechanic.is_reject = True
    mechanic.save()
    messages.success(request, 'Application Successfully Rejected!')
    return redirect('all_mechanic_applications')
    
def all_customer_detail(request):
    customers = Customer.objects.select_related('user','city')

    return render(request, 'all_customer_details.html',{
        'customers':customers
    })


def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    vehicle = Vehicle.objects.filter(customer=customer)

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'vehicle': vehicle
    })

def all_mechanic_details(request):
    mechanic = Mechanic.objects.select_related('city').filter(is_valid=True)

    return render(request, 'all_mechanic_details.html',{
        'mechanic':mechanic
    })

def mechanic_deatail(request, id):
    mechanic = get_object_or_404(Mechanic, id=id)
    vehicle_parts = StockManagement.objects.filter(mechanic=mechanic)

    return render(request, 'mechanic_detail.html',{
        'mechanic': mechanic,
        'vehicle_parts': vehicle_parts
    })

def rejected_mechanics(request):
    mechanic = Mechanic.objects.select_related('city').filter(is_reject=True)

    return render(request, 'rejected_mechanics.html',{
        'mechanic': mechanic
    })

def view_rejected_mechanic(request,id):
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'view_rejected_mechanic.html', {
        'mechanic': mechanic
    })