from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


import re
from datetime import datetime

from .models import Customer, Vehicle, City
from mechanic.models import Mechanic
from services.models import ServiceBooking, Bill, BookingSparePart, Feedback
from main_account.models import Fixigo



#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
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
    if not re.match(r'^[A-Za-z ]+$', name):
        return 'Name should contain only letters.'
    return None

#.............Main UserName Validation.............
def username_validation(username):   
    if not username:
        return 'Username is required.'
    if len(username) < 3:
        return 'Userame must be at least 3 characters.'
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
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::  


#::::::::::::::::::::::Main Index Page::::::::::::::::::::::
def index(request):
    customer_count = Customer.objects.count()
    mechanic_count = Mechanic.objects.count()
    completed_service_count = ServiceBooking.objects.filter(
        status= 'Completed'
        ).count()

    return render(request, 'index.html', {
        'customer_count' : customer_count,
        'mechanic_count' : mechanic_count,
        'completed_service_count' : completed_service_count
    })


#::::::::::::::::::::::User Registration::::::::::::::::::::::
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
            with transaction.atomic():
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


#::::::::::::::::::::::User Login::::::::::::::::::::::
def user_login(request):
    if request.user.is_authenticated:
        Customer.objects.get_or_create(
            user=request.user,
            defaults={
                'name': request.user.username or "Google User",
                'number': '0000000000',
                'address': 'Google Account',
                'city': City.objects.first()
            }
        )

        return redirect('home')

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
        
        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username = user_obj.username,
                password = password
            )

            if user is not None:
                login(request, user)

                Customer.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.username,
                    'number': '0000000000',
                    'address': 'Default Address',
                    'city': City.objects.first()
                    }
                )
                messages.success(request, 'Login successfull')
                return redirect('home')
            
            messages.error(request, 'Invalid email or password')
            return redirect('login')
        
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
        
    return render(request, 'login.html')

        

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
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
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


#::::::::::::::::::::::User Vehicle Add::::::::::::::::::::::
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


#::::::::::::::::::::::User All Vehicle List::::::::::::::::::::::
@login_required
def vehicle_list(request):
    vehicles = request.user.customer.vehicles.all()
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})


#::::::::::::::::::::::User Vehicle Edit::::::::::::::::::::::
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


#::::::::::::::::::::::User Vehicle Delete::::::::::::::::::::::
@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id, customer=request.user.customer)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully 🗑️")
        return redirect('vehicle_list')

    return redirect('vehicle_list')


#::::::::::::::::::::::User Logout::::::::::::::::::::::
@login_required
def logout_page(request):
    logout(request) 
    messages.success(request, "Logged out successfully 👋")
    return redirect('login')


#::::::::::::::::::::::User Home Page::::::::::::::::::::::
@login_required
def home_page(request):
    customer = request.user.customer
    vehicle = customer.vehicles.all()
    bookings = ServiceBooking.objects.filter(
        customer=customer
    ).exclude(
        status__in=['Cancelled', 'Completed']
    ).order_by('-id')

    latest_booking = bookings.first()

    mechanic_ratings = {
        item['mechanic']: item
        for item in Feedback.objects.values('mechanic').annotate(
            average=Avg('rating'),
            total_reviews=Count('id')
        )
    }

    for booking in bookings:
        if booking.mechanic_id:
            data = mechanic_ratings.get(booking.mechanic_id)

            booking.average_rating = round(
                data['average'], 1
            ) if data and data['average'] else 0

            booking.review_count = (
                data['total_reviews']
                if data else 0
            )

    return render(request, 'home.html', {
        'customer':customer,
        'vehicles':vehicle,
        'bookings': bookings,
        'latest_booking' : latest_booking
    })


#::::::::::::::::::::::User Profile Page::::::::::::::::::::::
@login_required
def profile_user(request):
    customer = request.user.customer
    vehicles = customer.vehicles.all()

    total_vehicles = Vehicle.objects.filter(customer=customer).count()
    total_orders = ServiceBooking.objects.filter(customer=customer).count()
    member_since = request.user.date_joined
    return render(request, 'profile_user.html',{
        'customer':customer,
        'vehicles': vehicles,
        'total_vehicles': total_vehicles,
        'total_orders': total_orders,
        'member_since': member_since,
    })


#::::::::::::::::::::::User Edit Profile::::::::::::::::::::::
@login_required
def profile_user_edit(request,id):
    customer = get_object_or_404(
        Customer,
        id=id,
        user= request.user
    )
    member_since = request.user.date_joined
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
        'customer':customer,
        'member_since' : member_since
    })


#::::::::::::::::::::::User Password Change(Profile Page)::::::::::::::::::::::
@login_required
def profile_user_change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # .............Password Null Check.............
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


#::::::::::::::::::::::Order List::::::::::::::::::::::
@login_required
def order_details(request):
    customer = request.user.customer
    order = ServiceBooking.objects.filter(customer=customer).order_by('-id')
    pending_count = order.filter(status='Pending').count()
    in_progress_count = order.filter(status='In_progress').count()
    completed_count = order.filter(status='Completed').count()

    return render(request, 'order_details_list.html', {
        'orders' : order,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
    })   


#::::::::::::::::::::::Order View::::::::::::::::::::::
@login_required
def order_view(request, id):
    customer = request.user.customer
    order = get_object_or_404(ServiceBooking, id=id, customer=customer)
    bill = Bill.objects.filter(booking=order).first()

    mechanic_rating = 0
    review_count = 0

    if order.mechanic:
        rating_data = Feedback.objects.filter(
            mechanic=order.mechanic
        ).aggregate(
            average=Avg('rating'),
            total_reviews=Count('id')
        )

        mechanic_rating = round(
            rating_data['average'], 1
        ) if rating_data['average'] else 0

        review_count = rating_data['total_reviews']

    return render(request, 'order_view.html', {
        'order': order,
        'bill': bill,
        'mechanic_rating': mechanic_rating,
        'review_count': review_count,
    })  


#::::::::::::::::::::::Chat Complaint Raise Button::::::::::::::::::::::
@login_required
@require_POST
def raise_chat_complaint(request, id):
    if not request.user.is_authenticated:
        return redirect("login")
    
    customer = request.user.customer

    booking = get_object_or_404(ServiceBooking, id=id, customer=customer)
    from chat.models import ChatRoom
    booking = get_object_or_404(
        ServiceBooking,
        id=id,
        customer=customer
    )

    room, created = ChatRoom.objects.get_or_create(
        booking=booking,
        defaults={
            "customer": booking.customer
        }
    )

    if created:
        messages.success(request, "Complaint created successfully.")
    else:
        messages.warning(request, "A complaint chat has already been created for this booking.")

    return redirect('customer_chat', room_id=room.id)
    


#::::::::::::::::::::::User About::::::::::::::::::::::
def about(request):

    customer_count = Customer.objects.count()
    mechanic_count = Mechanic.objects.count()
    complete_total_service = ServiceBooking.objects.filter(status='Completed').count()
    city_total = City.objects.count()

    return render(request,'about.html',{
        'customer_count' : customer_count,
        'mechanic_count' : mechanic_count,
        'complete_total_service' : complete_total_service,
        'city_total' : city_total
    })



#::::::::::::::::::::::Contact Us::::::::::::::::::::::
def contactus(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        fixigo = Fixigo.objects.first()

        try:
            # Context for both emails
            context = {
                'fixigo' : fixigo,
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'received_at': datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            }

            # --- Email to Admin (HTML) ---
            admin_html_content = render_to_string('emails/admin_notification.html', context)
            admin_text_content = strip_tags(admin_html_content)  # Fallback plain text

            admin_email = EmailMultiAlternatives(
                subject=f"New Contact Form - {subject}",
                body=admin_text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.EMAIL_HOST_USER],
            )
            admin_email.attach_alternative(admin_html_content, "text/html")
            admin_email.send()

            # --- Auto Reply to User (HTML) ---
            user_html_content = render_to_string('emails/auto_reply.html', context)
            user_text_content = strip_tags(user_html_content)  # Fallback plain text

            user_email = EmailMultiAlternatives(
                subject="Thank you for contacting us",
                body=user_text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            user_email.attach_alternative(user_html_content, "text/html")
            user_email.send()

            messages.success(request, "Your message has been sent successfully. We'll get back to you within 24 hours.")

        except Exception as e:
            messages.error(request, f"Failed to send email. Please try again later. Error: {e}")
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Email sending failed: {e}")

        return redirect("contactus")

    return render(request, "contactus.html")