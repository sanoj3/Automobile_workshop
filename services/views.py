from django.shortcuts import render, redirect
from .models import ServiceBooking, Complaints
from customer.models import City, Customer, Vehicle
from mechanic.models import Active_mechanic

# Create your views here.


def get_available_mechanic(city):
    return Active_mechanic.objects.filter(
        is_available = True,
        is_online = True,
        is_work_approve = True,
        is_work_reject = False
    ).order_by('?').first()

def servicebooking(request):

    customer = Customer.objects.get(user=request.user)

    city = City.objects.all()
    complaints = Complaints.objects.all()
    vehicles = Vehicle.objects.filter(customer=customer)

    if request.method == 'POST':

        vehicle = request.POST.get('vehicle')
        city_name = request.POST.get('city')

        # Multiple selected complaints
        selected_complaints = request.POST.getlist('complaints')

        problem_description = request.POST.get('problem_description')

        mechanic = get_available_mechanic(city_name)

        ServiceBooking.objects.create(
            customer=customer,
            vehicle=vehicle,
            city=city_name,
            complaints=", ".join(selected_complaints),
            problem_description=problem_description,
            mechanic=mechanic.mechanic if mechanic else None,
            status="Assigned" if mechanic else "Pending"
        )

        return redirect('service_booking_success')

    return render(request, 'servicebooking.html', {
        'city': city,
        'complaints': complaints,
        'vehicles' : vehicles
    })

def service_booking_success(request):
    return render(request, 'service_booking_success.html')