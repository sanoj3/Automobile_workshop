from django.shortcuts import render, redirect, get_object_or_404
from .models import Superadmin
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password

from mechanic.models import Mechanic, StockManagement, Active_mechanic
from customer.models import Customer, Vehicle

from customer.views import username_validation, password_validation, email_validation, number_validation


#::::::::::::::::::::::Speruser Session(Check)::::::::::::::::::::::
def check_superuser_access(request):
    super_user_id = request.session.get('super_user_id')

    if not super_user_id:
        return None
    try:
        superuser = Superadmin.objects.get(id=super_user_id)
        return superuser
    except Superadmin.DoesNotExist:
        return None


#::::::::::::::::::::::Login Superuser::::::::::::::::::::::
def login_superuser(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # .............Username Validation.............
        username_error = username_validation(username)
        if username_error:
            messages.error(request, username_error)
            return redirect('login_superuser')
        
        # .............Password Validation.............
        password_error = password_validation(password)
        if password_error:
            messages.error(request, password_error)
            return redirect('login_superuser')

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


#::::::::::::::::::::::Logout Superuser::::::::::::::::::::::
def logout_view_superuser(request):
    if 'super_user_id' in request.session:
        del request.session['super_user_id']
    return redirect('login_superuser')


#::::::::::::::::::::::Home Page Superuser::::::::::::::::::::::
def home_page_superuser(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')

    return render(request, 'home_admin.html', {
        'superuser': superuser
    })


#::::::::::::::::::::::Mechanic All Application Pending Page::::::::::::::::::::::
def all_mechanic_applications(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanics = Mechanic.objects.filter(is_valid=False, is_reject=False)

    return render(request, 'all_mechanic_application.html',{
        'mechanics':mechanics
    })


#::::::::::::::::::::::View Mechanic Application::::::::::::::::::::::
def mechanic_application(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'mechanic_application.html',{
        'mechanic':mechanic
    })


#::::::::::::::::::::::Approve Mechanic(Button)::::::::::::::::::::::
def approve_mechanic(request,id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    mechanic.is_valid = True
    mechanic.save()
    messages.success(request, 'Application Successfully Approved.')
    return redirect('all_mechanic_applications')


#::::::::::::::::::::::Reject Mechanic(Button)::::::::::::::::::::::
def reject_mechanic(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)
    mechanic.is_reject = True
    mechanic.save()
    messages.success(request, 'Application Successfully Rejected!')
    return redirect('all_mechanic_applications')


#::::::::::::::::::::::All Customer List::::::::::::::::::::::   
def all_customer_detail(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    customers = Customer.objects.select_related('user','city')

    return render(request, 'all_customer_details.html',{
        'customers':customers
    })

#::::::::::::::::::::::View Customer Details::::::::::::::::::::::
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


#::::::::::::::::::::::All Mechanic List::::::::::::::::::::::
def all_mechanic_details(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_valid=True)

    return render(request, 'all_mechanic_details.html',{
        'mechanic':mechanic
    })


#::::::::::::::::::::::View Customer Details::::::::::::::::::::::
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


#::::::::::::::::::::::All Rejected Mechanic List::::::::::::::::::::::
def rejected_mechanics(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_reject=True)

    return render(request, 'rejected_mechanics.html',{
        'mechanic': mechanic
    })


#::::::::::::::::::::::Rejected Customer Details::::::::::::::::::::::
def view_rejected_mechanic(request,id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'view_rejected_mechanic.html', {
        'mechanic': mechanic
    })


#::::::::::::::::::::::Profile Page::::::::::::::::::::::
def profile_page_superuser(request):
    superuser =  check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    return render(request, 'profile_superuser.html', {
        'superuser' : superuser
    })

#::::::::::::::::::::::Edit Profile::::::::::::::::::::::
def profile_page_edit_superuser(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        number = request.POST.get('number')

        # .............Email Validation.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('edit_profile_superuser', id=superuser.id)
        
        # .............Password Validation.............
        number_error = number_validation(number)
        if number_error:
            messages.error(request, number_error)
            return redirect('edit_profile_superuser', id=superuser.id)

        # .............Duplicate Email Check.............
        if Superadmin.objects.filter(email=email).exclude(id=superuser.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile_superuser', id=superuser.id)

        # .............Duplicate Number Check.............
        if Superadmin.objects.filter(number=number).exclude(id=superuser.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('edit_profile_superuser', id=superuser.id)

        superuser.email = email
        superuser.number = number

        if request.FILES.get('profile_pic'):
            superuser.profile_pic = request.FILES.get('profile_pic')

        superuser.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_page_superuser')

    return render(request, 'edit_profile_superuser.html', {'superuser': superuser})


#::::::::::::::::::::::Change Password(Profile Page)::::::::::::::::::::::
def profile_superuser_change_password(request):
    superuser= check_superuser_access(request)

    if not superuser:
        return redirect('login_superuser')
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # .............Password Null Check.............
        if not old_password:
            messages.error(request, 'Old password is required.')
            return redirect('profile_superuser_change_password')
        
        if not new_password:
            messages.error(request, 'New password is required.')
            return redirect('profile_superuser_change_password')
        
        if not confirm_password:
            messages.error(request, 'Confirm password is required.')
            return redirect('profile_superuser_change_password')

        # .............Old Password Check.............
        if not check_password(old_password, superuser.password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile_superuser_change_password')

        # .............New and Confirm Password Check.............
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('profile_superuser_change_password')

        # .............Same Password Check.............
        if old_password == new_password:
            messages.error(request, 'Use different password.')
            return redirect('profile_superuser_change_password')
        
        # .............Password Length Check.............
        if len(new_password)<6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('profile_superuser_change_password')
  
        # .............Update Password.............
        superuser.password = make_password(new_password)
        superuser.save()

        messages.success(request, 'Password changed successfully.')
        return redirect('login_superuser')
    
    return render(request, 'profile_superuser_change_password.html')


#::::::::::::::::::::::View Mechanic Availabe For Work::::::::::::::::::::::
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


#::::::::::::::::::::::View All Online Mechanics::::::::::::::::::::::
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