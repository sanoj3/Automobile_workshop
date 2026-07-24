from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

import razorpay
from django.conf import settings

from customer.models import Customer, City, Vehicle
from .models import Complaints, ServiceBooking, MechanicRequest, Bill, Feedback
from mechanic.models import Active_mechanic

from mechanic.views import check_mechanic_access




#::::::::::::::::::::::Service Booking::::::::::::::::::::::
@login_required
def service_booking(request):
    customer = get_object_or_404(Customer, user=request.user)
    cities = City.objects.all()
    vehicles = Vehicle.objects.filter(customer=customer)
    complaints = Complaints.objects.all()

    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        city_id = request.POST.get('city')
        complaints_ids = request.POST.getlist('complaints')
        problem = request.POST.get('problem_description')
        location = request.POST.get('location')

        # .............validation.............
        if not vehicle_id or not city_id or not problem or not location:
            messages.error(request, "All fields are required")
            return redirect('service_booking')

        vehicle = Vehicle.objects.filter(id=vehicle_id, customer=customer).first()
        city = City.objects.filter(id=city_id).first()

        # .............validation.............
        if not vehicle:
            messages.error(request, "Invalid vehicle")
            return redirect('service_booking')

        if not city:
            messages.error(request, "Invalid city")
            return redirect('service_booking')

        if not complaints_ids:
            messages.error(request, "Select at least one complaint")
            return redirect('service_booking')

        # .............prevent duplicate active booking.............
        if ServiceBooking.objects.filter(customer=customer, vehicle=vehicle,
                                         status__in=["Pending", "Assigned", "Accepted"]
                                         ).exists():
            messages.error(request, "Already active booking exists")
            return redirect('service_booking')

        # .............create booking.............
        booking = ServiceBooking.objects.create(
            customer=customer,
            vehicle=vehicle,
            city=city,
            problem_description=problem,
            location=location,
            status="Pending"
        )

        booking.complaints.set(complaints_ids)

        active_mechanics = Active_mechanic.objects.filter(
            is_online=True,
            is_available=True,
            mechanic__city=city
        )

        for active in active_mechanics:
            MechanicRequest.objects.create(
                booking=booking,
                mechanic=active.mechanic
            )

        messages.success(request, "Service booked successfully")
        return redirect('booking_success',id)

    return render(request, 'service_booking.html', {
        'vehicles': vehicles,
        'cities': cities,
        'complaints': complaints
    })


#::::::::::::::::::::::Edit Booking (Mechanic Work)::::::::::::::::::::::
def edit_booking(request, id):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')

    job = get_object_or_404(
        MechanicRequest,
        id=id,
        mechanic=mechanic,
        status__in=["Accepted", "In_progress"]
    )

    booking = job.booking
    complaints = Complaints.objects.all()

    if request.method == "POST":
        problem_description = request.POST.get('problem_description')
        complaint_ids = request.POST.getlist('complaints')

        # .............validate.............
        if not problem_description:
            messages.error(request, "Problem description cannot be empty")
            return redirect('edit_booking', id=id)

        if not complaint_ids:
            messages.error(request, "Select at least one complaint")
            return redirect('edit_booking', id=id)

        # .............update booking.............
        booking.problem_description = problem_description
        booking.save()

        booking.complaints.set(complaint_ids)

        messages.success(request, "Booking updated successfully")
        return redirect('pending_job', id=id)

    return render(request, 'edit_booking.html', {
        'job': job,
        'booking': booking,
        'complaints': complaints
    })


#::::::::::::::::::::::Mechanic Request::::::::::::::::::::::
def mechanic_requests(request):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')

    requests = MechanicRequest.objects.filter(
        mechanic=mechanic,
        status='Pending'
    )

    return render(request, 'mechanic_requests.html', {
        'requests': requests
    })


#::::::::::::::::::::::Work Accept::::::::::::::::::::::
def accept_booking(request, request_id):

    mechanic = check_mechanic_access(request)
    
    if mechanic is None:
        return redirect('login_mechanic')

    mechanic_request = get_object_or_404(
        MechanicRequest,
        id=request_id,
        mechanic=mechanic
    )

    if mechanic_request.is_expired():
        mechanic_request.status = 'Expired'
        mechanic_request.save()
        messages.error(request, "Request expired")
        return redirect('home_mechanic')

    booking = mechanic_request.booking

    with transaction.atomic():

        booking = booking.__class__.objects.select_for_update().get(id=booking.id)

        if booking.mechanic:
            messages.error(request, "This work is already allocated")
            return redirect('home_mechanic')

        booking.mechanic = mechanic
        booking.status = 'Accepted'
        booking.save()

        mechanic_request.status = 'Accepted'
        mechanic_request.save()

        MechanicRequest.objects.filter(booking=booking
                                       ).exclude(mechanic=mechanic
                                                 ).update(status='Rejected')

        active = Active_mechanic.objects.filter(mechanic=mechanic).first()
        if active:
            active.is_available = False
            active.save()

    messages.success(request, "Work accepted successfully")
    return redirect('home_mechanic')


#::::::::::::::::::::::Work Reject::::::::::::::::::::::
def reject_booking(request, request_id):

    mechanic = check_mechanic_access(request)
    
    if mechanic is None:
        return redirect('login_mechanic')

    mechanic_request = get_object_or_404(
        MechanicRequest,
        id=request_id,
        mechanic=mechanic
    )

    booking = mechanic_request.booking

    mechanic_request.status = 'Rejected'
    mechanic_request.save()


    messages.info(request, "Booking rejected")
    return redirect('home_mechanic')


#::::::::::::::::::::::Booking Success::::::::::::::::::::::
@login_required
def booking_success(request,id):
    customer = request.user.customer
    # booking = ServiceBooking.objects.filter(customer=customer).first()
    booking = get_object_or_404(
        ServiceBooking,
        id=id,
        customer=request.user.customer
    )
    return render(
        request,
        'booking_success.html',{
        'booking' : booking
        }
    )


#::::::::::::::::::::::Customer Cancel Booking::::::::::::::::::::::
@login_required
def cancel_booking_user(request, id):
    customer = get_object_or_404(
        Customer,
        user=request.user
    )

    booking = get_object_or_404(
        ServiceBooking,
        id=id,
        customer=customer
    )

    if booking.status in ["Completed", "Cancelled", "In_progress"]:

        messages.error(request, "You cannot cancel this booking.")
        return redirect('order_view', booking.id)

    if request.method == "POST":
        reason = request.POST.get("reason")

        booking.status = "Cancelled"
        booking.cancel_reason = reason
        booking.cancelled_by = "Customer"

        booking.save()

        MechanicRequest.objects.filter(
            booking=booking
        ).exclude(
            status="Completed"
        ).update(
            status="Cancelled"
        )

        if booking.mechanic:
            active_mechanic, created = Active_mechanic.objects.get_or_create(
                mechanic=booking.mechanic
            )

            active_mechanic.is_available = True
            active_mechanic.save()

        messages.success(request, "Booking cancelled successfully.")
        return redirect('home')

    return render(request, "cancel_booking.html",{
            "booking": booking
        })



#::::::::::::::::::::::Mechanic Cancel Booking::::::::::::::::::::::
def cancel_booking_mechanic(request, id):
    mechanic = check_mechanic_access(request)

    if mechanic is None:
        return redirect('login_mechanic')
    
    job = get_object_or_404(
        MechanicRequest,
        id=id,
        mechanic=mechanic
    )

    job.status = "Rejected"
    job.save()

    booking = job.booking

    active_mechanic, created = Active_mechanic.objects.get_or_create(
        mechanic=mechanic
    )

    active_mechanic.is_available = True
    active_mechanic.save()

    booking.status = "Pending"
    booking.mechanic = None
    booking.save()

    booking.rejected_mechanics.add(mechanic)

    mechanics = Active_mechanic.objects.filter(
        is_online=True,
        is_available=True,
        mechanic__city=booking.city
    ).exclude(
        mechanic__in=booking.rejected_mechanics.all()
    )

    for m in mechanics:
        MechanicRequest.objects.update_or_create(
            booking=booking,
            mechanic=m.mechanic,
            defaults={"status": "Pending"}
        )

    messages.warning(request, "Job rejected successfully.")
    return redirect('pending_jobs_list')



#::::::::::::::::::::::Payment Page::::::::::::::::::::::
def payment_page(request, id):
    bill = get_object_or_404(Bill, id=id)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    amount = int(bill.grand_total * 100)

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "bill": bill,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "payment_page.html", context)


#::::::::::::::::::::::Payment Success::::::::::::::::::::::
def payment_success(request):
    if request.method == "POST":

        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')

        bill_id = request.POST.get('bill_id')

        bill = Bill.objects.get(id=bill_id)

        bill.payment_status = "Paid"
        bill.payment_id = payment_id
        bill.save()

        booking = bill.booking
        booking.status = "Completed"
        booking.save()

        mechanic_request = MechanicRequest.objects.filter(
            booking=booking,
            mechanic=booking.mechanic
        ).first()

        if mechanic_request:
            mechanic_request.status = "Completed"
            mechanic_request.save()

        active_mechanic = Active_mechanic.objects.filter(
            mechanic=booking.mechanic
        ).first()

        if active_mechanic:
            active_mechanic.is_available = True
            active_mechanic.save()

        messages.success(request, "Payment Successful")

        return redirect('home')  


#::::::::::::::::::::::Customer Review For Mechanic::::::::::::::::::::::
@login_required
def feedback(request, order_id):
    customer = get_object_or_404(Customer,user=request.user)

    order = get_object_or_404(
        ServiceBooking,
        id=order_id,
        customer=customer
    )

    existing_feedback = Feedback.objects.filter(service=order).first()

    if existing_feedback:
        messages.warning(request, "Rating already submitted.")
        return redirect('order_view', id=order.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        message = request.POST.get("message")

        Feedback.objects.create(
            customer=customer,
            service=order,
            mechanic=order.mechanic,
            rating=rating,
            message=message
        )

        messages.success(request, "Feedback submitted successfully.")
        return redirect("order_details")

    return render(request, "feedback.html", {
        "order": order
    })





