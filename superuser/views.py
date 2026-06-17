from django.shortcuts import render, redirect, get_object_or_404
from .models import Superadmin
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password

from mechanic.models import Mechanic, StockManagement, Active_mechanic
from customer.models import Customer, Vehicle
from services.models import Complaints, ServiceBooking, MechanicRequest, Bill

from customer.views import username_validation, password_validation, email_validation, number_validation, name_validation


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
    if request.session.get('super_user_id'):
        return redirect('home_page_superuser')

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
        'superuser' : superuser,
        'mechanics':mechanics
    })


#::::::::::::::::::::::View Mechanic Application::::::::::::::::::::::
def mechanic_application(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'mechanic_application.html',{
        'superuser' : superuser,
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
        'superuser' : superuser,
        'customers':customers
    })

#::::::::::::::::::::::View Customer(Vehicle & Service Order) Details::::::::::::::::::::::
def customer_detail(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    customer = get_object_or_404(Customer, id=id)
    vehicle = Vehicle.objects.filter(customer=customer)
    service_order = ServiceBooking.objects.filter(customer=customer).order_by('-id')

    return render(request, 'customer_detail.html', {
        'superuser' : superuser,
        'customer': customer,
        'vehicle': vehicle,
        'service_order' : service_order
    })



#::::::::::::::::::::::View Customer Service Order Details::::::::::::::::::::::
def customer_details_service_order(request, customer_id, service_id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    customer = get_object_or_404(Customer, id=customer_id)

    service_order = get_object_or_404(
        ServiceBooking,
        id = service_id,
        customer = customer
    )

    bill = Bill.objects.filter(
        booking=service_order
    ).first()

    return render(request, 'customer_details_service_order.html', {
        'superuser' : superuser,
        'customer' : customer,
        'service_order' : service_order,
        'bill' : bill
    })


#::::::::::::::::::::::All Mechanic List::::::::::::::::::::::
def all_mechanic_details(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_valid=True)

    return render(request, 'all_mechanic_details.html',{
        'superuser' : superuser,
        'mechanic':mechanic
    })


#::::::::::::::::::::::View Mechanic Details::::::::::::::::::::::
def mechanic_deatail(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)
    vehicle_parts = StockManagement.objects.filter(mechanic=mechanic)
    service_order = ServiceBooking.objects.filter(mechanic=mechanic).order_by('-id')

    return render(request, 'mechanic_detail.html',{
        'superuser' : superuser,
        'mechanic': mechanic,
        'vehicle_parts': vehicle_parts,
        'service_order' : service_order
    })



#::::::::::::::::::::::View Mechanic Service Order Details::::::::::::::::::::::
def mechanic_details_service_order(request, mechanic_id, service_id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=mechanic_id)

    service_order = get_object_or_404(
        ServiceBooking,
        id = service_id,
        mechanic = mechanic
    )

    bill = Bill.objects.filter(
        booking=service_order
    ).first()

    return render(request, 'mechanic_details_service_order.html', {
        'superuser' : superuser,
        'mechanic' : mechanic,
        'service_order' : service_order,
        'bill' : bill
    })


#::::::::::::::::::::::All Rejected Mechanic List::::::::::::::::::::::
def rejected_mechanics(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = Mechanic.objects.select_related('city').filter(is_reject=True)

    return render(request, 'rejected_mechanics.html',{
        'superuser' : superuser,
        'mechanic': mechanic
    })


#::::::::::::::::::::::Rejected Customer Details::::::::::::::::::::::
def view_rejected_mechanic(request,id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    return render(request, 'view_rejected_mechanic.html', {
        'superuser' : superuser,
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

    if superuser is None:
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
    
    return render(request, 'profile_superuser_change_password.html',{
        'superuser' : superuser
    })


#::::::::::::::::::::::View Mechanic Availabe For Work::::::::::::::::::::::
def available_mechanic(request):
    superuser= check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanics_status = Active_mechanic.objects.filter(
        is_online = True,
        is_available = True
    )
    return render(request, 'available_mechanic.html', {
        'superuser' : superuser,
        'mechanics_status': mechanics_status,

    })


#::::::::::::::::::::::View All Online Mechanics::::::::::::::::::::::
def available_online(request):
    superuser= check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanics_status = Active_mechanic.objects.filter(
        is_online = True
    )
    return render(request, 'available_online.html', {
        'superuser' : superuser,
        'mechanics_status' : mechanics_status
    })

#::::::::::::::::::::::Complaints List::::::::::::::::::::::
def complaint_list_view(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    complaints = Complaints.objects.all()

    return render(request, 'complaint_list_view.html', {
        'superuser' : superuser,
        'complaints' : complaints
    })

#::::::::::::::::::::::Add Complaints::::::::::::::::::::::
def add_complaints(request):
    superuser = check_superuser_access(request)
    
    if superuser is None:
        return redirect('login_superuser')
    
    if request.method == 'POST':
        complaint_name = request.POST.get('complaint_name')
        basic_price = request.POST.get('basic_price')

        required_fields = [complaint_name, basic_price]
        if not all(required_fields):
            messages.error(request, 'required fields are must be entered.')
            return redirect('add_complaints')
        
        # .............Item Name Validation.............
        complaint_name_error = name_validation(complaint_name)
        if complaint_name_error:
            messages.error(request, complaint_name_error)
            return redirect('add_complaints')
        
        # .............Price Validation.............
        try:
            basic_price = float(basic_price)
        except ValueError:
            messages.error(request, 'Price must be a valid number.')
            return redirect('add_complaints')
        if basic_price<=0:
            messages.error(request, 'Price must be greater than 0')
            return redirect('add_complaints')

        # .............Data Save.............
        Complaints.objects.create(
            complaint_name = complaint_name,
            basic_service_price = basic_price
        )

        messages.success(request, 'Add complaint successfully created.')
        return redirect('complaint_list_view')
    
    return render(request, 'add_complaints.html',{
        'superuser' : superuser
    })


#::::::::::::::::::::::Delete Complaints::::::::::::::::::::::
def delete_complaints(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    complaint = get_object_or_404(Complaints, id=id)

    if request.method == 'POST':
        complaint.delete()
        messages.success(request,'Complaint deleted successfully 🗑️')
        return redirect('complaint_list_view')
    
    return redirect('complaint_list_view')


#::::::::::::::::::::::Edit Complaints::::::::::::::::::::::
def modify_complaints(request, id):
    superuser = check_superuser_access(request)
    
    if superuser is None:
        return redirect('login_superuser')
    
    complaint = get_object_or_404(Complaints, id=id)

    if request.method == 'POST':

        complaint_name = request.POST.get('complaint_name')
        basic_price = request.POST.get('basic_price')

        # .............Item Name Validation.............
        complaint_name_error = name_validation(complaint_name)
        if complaint_name_error:
            messages.error(request, complaint_name_error)
            return redirect('modify_complaints', id=id)
        
        # .............Price Validation.............
        try:
            basic_price = float(basic_price)
        except ValueError:
            messages.error(request, 'Basic price must be a valid number.')
            return redirect('modify_complaints', id=id)
        if basic_price<=0:
            messages.error(request, 'basic price must be greater than 0')
            return redirect('modify_complaints', id=id)

        # .............Udate Data.............
        complaint.complaint_name = complaint_name
        complaint.basic_service_price = basic_price

        complaint.save()

        messages.success(
            request,
            'Complaint are updated successfully ✅'
        )

        return redirect('complaint_list_view')

    return render(request, 'modify_complaints.html', {
        'superuser' : superuser,
        'complaints': complaint
    })


#::::::::::::::::::::::Suspend Mechanic Account::::::::::::::::::::::
def suspend_mechanic(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    mechanic = get_object_or_404(Mechanic, id=id)

    mechanic.account_suspend = not mechanic.account_suspend
    mechanic.save()

    if mechanic.account_suspend:
        Active_mechanic.objects.filter(mechanic=mechanic).update(
            is_online=False,
            is_available=False
        )

        messages.success(request, "Account has been suspended.")
    else:
        messages.success(request, "Account has been activated.")

    return redirect('mechanic_deatail',mechanic.id)


#::::::::::::::::::::::Service Booking Not Assign(Mechanic)::::::::::::::::::::::
def service_not_assign(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    service = ServiceBooking.objects.filter(status='Pending')

    return render(request, 'service_not_assign.html', {
        'superuser' : superuser,
        'service' : service
    })


#::::::::::::::::::::::Service Booking Not Assign(Mechanic) Details::::::::::::::::::::::
def service_not_assign_view(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    service = get_object_or_404(
        ServiceBooking,
        id=id,
        status='Pending'
    )

    mechanics = Active_mechanic.objects.filter(
        is_available = True,
        is_online = True
    )

    if request.method == "POST":
        mechanic_id = request.POST.get("mechanic")

        mechanic = get_object_or_404(Mechanic, id=mechanic_id)

        MechanicRequest.objects.filter(
            booking=service,
            mechanic=mechanic
        ).update(status='Pending')

        return redirect('service_not_assign')

    return render(request, 'service_not_assign_view.html', {
        'superuser': superuser,
        'service': service,
        'mechanics': mechanics
    })


#::::::::::::::::::::::Active Service Booking Job::::::::::::::::::::::
def active_service_booking(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    service = ServiceBooking.objects.filter(status__in=['Assigned','Accepted','In_progress'])

    active_count = service.count()

    return render(request, 'active_service.html', {
        'superuser' : superuser,
        'service' : service,
        'active_count' : active_count
    })



#::::::::::::::::::::::Active Service Booking Job Details::::::::::::::::::::::
def active_service_booking_view(request, id):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    service = get_object_or_404(
        ServiceBooking,
        id=id,
        status__in=['Assigned', 'Accepted', 'In_progress']
    )

    return render(request, 'active_service_view.html', {
        'superuser': superuser,
        'service': service
    })