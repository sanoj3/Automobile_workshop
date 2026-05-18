from django.shortcuts import render, redirect
from .models import ServiceBooking, Complaints
from customer.models import City, Customer, Vehicle
from mechanic.models import Active_mechanic
from django.http import JsonResponse
from mechanic.views import check_mechanic_access

# Create your views here.


def get_available_mechanic(city):
    return Active_mechanic.objects.filter(
        mechanic__city = city,
        is_available = True,
        is_online = True,
        is_work_approve = True,
        is_work_reject = False
    ).order_by('?').first()

def servicebooking(request):

    customer = Customer.objects.get(user=request.user)

    city = City.objects.get(customer=customer)
    complaints = Complaints.objects.all()
    vehicles = Vehicle.objects.filter(customer=customer)

    if request.method == 'POST':

        vehicle_id = request.POST.get('vehicle')
        vehicle = Vehicle.objects.get(id=vehicle_id)
        city = city

        # Multiple selected complaints
        selected_complaints = request.POST.getlist('complaints')

        problem_description = request.POST.get('problem_description')

        mechanic = get_available_mechanic(city)

        booking = ServiceBooking.objects.create(
            customer=customer,
            vehicle=vehicle,
            city=city,
            
            problem_description=problem_description,
            mechanic=mechanic.mechanic if mechanic else None,
            status="Assigned" if mechanic else "Pending"
        )

        booking.complaints.set(selected_complaints)

        return redirect('service_booking_success')

    return render(request, 'servicebooking.html', {
        'city': city,
        'complaints': complaints,
        'vehicles' : vehicles
    })

def service_booking_success(request):
    return render(request, 'service_booking_success.html')


