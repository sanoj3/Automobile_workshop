from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.http import JsonResponse

import json
from decimal import Decimal

from .models import Mechanic, StockManagement, Active_mechanic
from customer.models import City
from services.models import MechanicRequest, Bill, BookingSparePart, ServiceBooking

from customer.views import name_validation, email_validation, number_validation, password_validation



#::::::::::::::::::::::Mechanic Session Access::::::::::::::::::::::
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

#::::::::::::::::::::::Apply Mechanic::::::::::::::::::::::
def apply_mechanic(request):
    cities = City.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email','').strip()
        aadhaar = request.POST.get('aadhaar','').strip()
        number = request.POST.get('number','').strip()
        certificate = request.FILES.get('certificate')  
        experience_certificate = request.FILES.get('experience_certificate')
        city_id = request.POST.get('city')
        password = request.POST.get('password','').strip()

        # .............City Validate.............
        try:
            city = City.objects.get(id=city_id)
        
        except City.DoesNotExist:
            messages.error(request, 'Invalid city selected.')
            return redirect('apply')

        # .............Name Validate.............
        name_error = name_validation(name)
        if name_error:
            messages.error(request, name_error)
            return redirect('apply')
        
        # .............Email Validate.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('apply')
        
        # .............Number Validate.............
        number_error = number_validation(number)
        if number_error:
            messages.error(request, number_error)
            return redirect('apply')

        required_fields = [name, email, aadhaar, number, certificate, city, password]
        if not all(required_fields):
            messages.error(request, 'All fields are required.')
            return redirect('apply')

        # .............Aadhaar Validate.............
        if not aadhaar:
            messages.error(request, 'Aadhaar is required.')
            return redirect('apply')
        if not aadhaar.isdigit():
            messages.error(request, 'Aadhaar must contain only digits.')
            return redirect('apply')
        if len(aadhaar) != 12:
            messages.error(request, 'Aadhaar must be 12 digits.')
            return redirect('apply')
        
        # .............Duplicate Email Check.............
        if Mechanic.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('apply')
        
        # .............Duplicate Number Check.............
        if Mechanic.objects.filter(number=number).exists():
            messages.error(request, 'Number already exists.')
            return redirect('apply')
        
        # .............Duplicate Aadhaar Check.............
        if Mechanic.objects.filter(aadhaar=aadhaar).exists():
            messages.error(request, 'Aadhaar already exists.')
            return redirect('apply')
        
        # .............Certificate Validate.............
        if not certificate:
            messages.error(request, 'Certificate is required.')
            return redirect('apply')
        
        

        # .............Save Data.............
        try:
            with transaction.atomic():
                Mechanic.objects.create(
                    name = name,
                    email = email,
                    aadhaar=aadhaar,
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


#::::::::::::::::::::::Login Mechanic::::::::::::::::::::::
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


#::::::::::::::::::::::Logout Mechanic::::::::::::::::::::::
def logout_view_mechanic(request):
    mechanic_id = request.session.get('mechanic_id')
    if mechanic_id:
        mech = Active_mechanic.objects.filter(mechanic_id=mechanic_id).first()

        if mech:
            mech.is_online = False
            mech.is_available = False
            mech.save()
            
    if 'mechanic_id' in request.session:
        del request.session['mechanic_id']
    return redirect('login_mechanic')

#::::::::::::::::::::::Home Page Mechanic::::::::::::::::::::::
def home_page_mechanic(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    mech = Active_mechanic.objects.filter(mechanic=mechanic).first()

    requests = MechanicRequest.objects.filter(
        mechanic=mechanic,
        status='Pending'
    ).order_by('-created_at')

    return render(request, 'home_mechanic.html', {
        'mechanic': mech,
        'requests': requests
    })
 
 #::::::::::::::::::::::Profile Page Mechanic::::::::::::::::::::::
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

#::::::::::::::::::::::Edit Profile Mechanic::::::::::::::::::::::
def profile_page_edit_mechanic(request, id):

    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        number = request.POST.get('number')

        # .............Email Validation.............
        email_error = email_validation(email)
        if email_error:
            messages.error(request, email_error)
            return redirect('profile_page_edit_mechanic', id=mechanic.id)
        
        # .............Number Validation.............
        number_error = number_validation(number)
        if number_error:
            messages.error(request, number_error)
            return redirect('profile_page_edit_mechanic', id=mechanic.id)

        # .............Duplicate Email Check.............
        if Mechanic.objects.filter(email=email).exclude(id=mechanic.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('profile_page_edit_mechanic', id=mechanic.id)
        
        # .............Duplicate Number Check.............
        if Mechanic.objects.filter(number=number).exclude(id=mechanic.id).exists():
            messages.error(request, 'Number already exists.')
            return redirect('profile_page_edit_mechanic', id=mechanic.id)

        # .............Profile Pic.............
        if request.FILES.get('profile_pic'):
            mechanic.profile_pic = request.FILES.get('profile_pic')

        # .............Save Data.............
        mechanic.email = email
        mechanic.number = number

        mechanic.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_page_mechanic')

    return render(request, 'edit_profile_mechanic.html', {'mechanic': mechanic})


#::::::::::::::::::::::Change Password(Profile Page)::::::::::::::::::::::
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

        # .............Password Validations.............
        old_password_error = password_validation(old_password)
        if old_password_error:
            messages.error(request, old_password_error)
            return redirect('profile_mechanic_change_password')
        
        new_password_error = password_validation(new_password)
        if new_password_error:
            messages.error(request, new_password_error)
            return redirect('profile_mechanic_change_password')
        
        confirm_password_error = password_validation(confirm_password)
        if confirm_password_error:
            messages.error(request, confirm_password_error)
            return redirect('profile_mechanic_change_password')


        if not check_password(old_password, mechanic.password):
            messages.error(request, 'Old password is incorrected')
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        if old_password == new_password:
            messages.error(request, 'Use different password.')
        
        # .............Save Data.............
        mechanic.password = make_password(new_password)
        mechanic.save()

        messages.success(request, 'Password changed successfully.')
        return redirect('login_mechanic')
    
    return render(request, 'profile_mechanic_change_password.html')


#::::::::::::::::::::::Spareparts List::::::::::::::::::::::
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


#::::::::::::::::::::::Add Spareparts::::::::::::::::::::::
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
        
        # .............Item Name Validation.............
        item_name_error = name_validation(item_name)
        if item_name_error:
            messages.error(request, item_name_error)
            return redirect('add_vehicle_parts')
        
        # .............Price Validation.............
        try:
            price = float(price)
        except ValueError:
            messages.error(request, 'Price must be a valid number.')
            return redirect('add_vehicle_parts')
        if price<=0:
            messages.error(request, 'Price must be greater than 0')
            return redirect('add_vehicle_parts')
        
        # .............Quantity Validation.............
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, 'Quantity must be a valid integer.')
            return redirect('add_vehicle_parts')
        if quantity<=0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('add_vehicle_parts')

        # .............Data Save.............
        created_at = timezone.datetime.now()
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


#::::::::::::::::::::::Delete Spareparts::::::::::::::::::::::
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


#::::::::::::::::::::::Edit Spareparts::::::::::::::::::::::
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

    if request.method == 'POST':

        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        stock_pic = request.FILES.get('stock_pic')

        # .............Item Name Validation.............
        item_name_error = name_validation(item_name)
        if item_name_error:
            messages.error(request, item_name_error)
            return redirect('modify_vehicle_parts', id=id)
        
        # .............Price Validation.............
        try:
            price = float(price)
        except ValueError:
            messages.error(request, 'Price must be a valid number.')
            return redirect('modify_vehicle_parts', id=id)
        if price<=0:
            messages.error(request, 'Price must be greater than 0')
            return redirect('modify_vehicle_parts', id=id)
        
        # .............Quantity Validation.............
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, 'Quantity must be a valid integer.')
            return redirect('modify_vehicle_parts', id=id)
        if quantity<=0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('modify_vehicle_parts', id=id)

        # .............Udate Data.............
        parts.item_name = item_name
        parts.price = price
        parts.quantity = quantity

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


#::::::::::::::::::::::Toggle Button(Mechanic Online)::::::::::::::::::::::
def toggle_mechanic_status(request):

    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request'}, status=400)

    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    if mechanic == 'not_valid':
        return render(request, 'application_submitted.html')
    if mechanic == 'reject':
        return render(request, 'application_rejected.html')

    mech, created = Active_mechanic.objects.get_or_create(mechanic=mechanic)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    is_online = data.get("is_online")

    if isinstance(is_online, str):
        is_online = is_online.lower() == "true"

    mech.is_online = is_online
    mech.is_available = is_online
    mech.save()

    return JsonResponse({
        'status': 'online' if mech.is_online else 'offline'
    })


#::::::::::::::::::::::Pending Jobs List::::::::::::::::::::::
def pending_jobs_list(request):
    mechanic = check_mechanic_access(request)
    jobs = MechanicRequest.objects.filter(mechanic=mechanic, 
                                          status__in = ["Accepted", "In_progress"]
                                          ).exclude(booking__status="Completed"
                                                    ).exclude(booking__status="Cancelled"
                                                              ).exclude(status="Expired"
                                                                        ).order_by('-id')
    return render(request, 'pending_job_list.html', {
        'jobs': jobs,
        'mechanic': mechanic
    })


#::::::::::::::::::::::Pending Job::::::::::::::::::::::
def pending_job(request, id):
    mechanic = check_mechanic_access(request)
    job = get_object_or_404(MechanicRequest, id=id, mechanic=mechanic,
        status__in = ["Accepted", "In_progress"]
    )

    booking = job.booking

    stocks = StockManagement.objects.filter(
        mechanic=mechanic,
        quantity__gt=0
    )

    if request.method == 'POST':

        # .............Complaint Total.............
        complaint_total = Decimal('0.00')

        for complaint in booking.complaints.all():

            complaint_total += complaint.basic_sevice_price


        # .............Labour Charge.............
        labour_charge = request.POST.get('labour_charge') or 0
        labour_charge = Decimal(str(labour_charge))

        
        # .............Totals.............
        spare_parts_total = Decimal('0.00')

        extra_parts_total = Decimal('0.00')

        grand_total = Decimal('0.00')

        # .............Create Bill.............
        bill, created = Bill.objects.get_or_create(
            booking=booking,
            defaults={
                "complaint_total": complaint_total,
                "labour_charge": labour_charge,
                "payment_status": "Pending"
            }
        )

        # .............update bill already exists.............
        if not created:
            bill.complaint_total = complaint_total
            bill.labour_charge = labour_charge
            bill.save()


        # .............Used Stock Parts.............
        stock_ids = request.POST.getlist('stock_id')

        quantities = request.POST.getlist('quantity')

        for stock_id, qty in zip(stock_ids, quantities):

            if qty and int(qty) > 0:

                qty = int(qty)

                stock = StockManagement.objects.get(
                    id=stock_id,
                    mechanic=mechanic
                )

                total = stock.price * qty

                # .............Save used spare part.............
                BookingSparePart.objects.create(bill=bill, stock=stock, part_name=stock.item_name,
                                                quantity=qty, price=stock.price, total_price=total,
                                                is_extra=False)

                # .............Reduce stock quantity.............
                stock.quantity -= qty
                stock.save()
                spare_parts_total += total

        # .............Extra Spare Parts.............
        extra_names = request.POST.getlist('extra_part_name')
        extra_prices = request.POST.getlist('extra_part_price')

        for name, price in zip(extra_names, extra_prices):

            if name and price:
                price = Decimal(price)

                BookingSparePart.objects.create(bill=bill, part_name=name, quantity=1,
                                                price=price, total_price=price, is_extra=True)
                extra_parts_total += price

        # .............Final Bill Calculation.............
        grand_total = (complaint_total + spare_parts_total + extra_parts_total + labour_charge)

        # .............Update Bill.............
        bill.spare_parts_total = spare_parts_total
        bill.extra_parts_total = extra_parts_total
        bill.grand_total = grand_total
        bill.save()

        # .............Update Booking.............
        booking.labour_charge = labour_charge
        booking.total_price = grand_total
        booking.status = "Completed"
        booking.save()
        job.status = "Completed"
        job.save()
        active_mechanic, created = Active_mechanic.objects.get_or_create(mechanic=mechanic)
        active_mechanic.is_available = True
        active_mechanic.save()

        messages.success(request, f'Bill Generated Successfully ₹{grand_total}')
        return redirect('pending_jobs_list')

    return render(request, 'pending_job.html', {
        'job': job,
        'mechanic': mechanic,
        'stocks': stocks,
    })


#::::::::::::::::::::::Inprogress Status::::::::::::::::::::::
def inprogress_status(request, id):
    mechanic = check_mechanic_access(request)

    job = get_object_or_404(MechanicRequest, id=id, mechanic=mechanic, status='Accepted')
    
    job.status = 'In_progress'
    job.save()

    booking = job.booking
    booking.status = 'In_progress'
    booking.save()

    messages.success(request, 'Work is In Progress')
    return redirect('pending_job', id=job.id)


#::::::::::::::::::::::Completed Job List::::::::::::::::::::::
def completed_jobs_list(request):
    mechanic = check_mechanic_access(request)

    job = ServiceBooking.objects.filter(mechanic=mechanic, status='Completed')

    return render(request, 'completed_job_list.html', {
        'mechanic' : mechanic,
       'jobs' : job 
    })


#::::::::::::::::::::::Completed Job View::::::::::::::::::::::
def job_completed_view(request, id):
    mechanic = check_mechanic_access(request)

    job = get_object_or_404(ServiceBooking, id=id, mechanic=mechanic)

    return render(request, 'job_completed_view.html', {
        'mechanic' : mechanic,
        'jobs' : job
    })