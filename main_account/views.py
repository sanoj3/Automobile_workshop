from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings

import random
from datetime import timedelta
import secrets

from .models import PasswordResetOTP, MechanicPasswordOTP
from mechanic.models import Mechanic

from mechanic.views import check_mechanic_access

# Create your views here.



#::::::::::::::::::::::Forgot Password Customer::::::::::::::::::::::
# def forgot_password(request):
#     if request.user.is_authenticated:
#         return redirect("home")

#     if request.method == "POST":

#         email = request.POST.get("email")

#         try:
#             user = User.objects.get(email=email)
#             otp = str(random.randint(100000,999999))
#             PasswordResetOTP.objects.filter(user=user).delete()
#             PasswordResetOTP.objects.create(user=user, otp=otp)

#             # Professional email
#             subject = "Fixigo - Password Reset OTP"

#             message = f"""
#             Dear {user.first_name if user.first_name else "Customer"},

#             We received a request to reset the password for your Fixigo account.

#             ========================================
#                     PASSWORD RESET OTP
#                         {otp}
#             ========================================

#             This OTP is valid for 10 minutes.

#             For your security:
#             • Never share this OTP with anyone.
#             • Our team will never ask for your OTP.
#             • If you did not request a password reset, please ignore this email. Your account remains secure.

#             Thank you for choosing Fixigo.

#             Best Regards,

#             Team Fixigo
#             Your Trusted Automobile Service Partner
#             """

#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[email],
#                 fail_silently=False,
#             )

#             request.session["reset_user"] = user.id

#             return redirect("verify_otp")

#         except User.DoesNotExist:
#             return render(request,"forgot_password.html",{
#                 "error":"Email not found"
#             })

#     return render(request,"forgot_password.html")
import logging
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import PasswordResetOTP, Fixigo

logger = logging.getLogger(__name__)


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            return render(request, "forgot_password.html", {
                "error": "Please enter your email address."
            })

        try:
            user = User.objects.get(email=email)

            # Check if user requested OTP within the last 60 seconds
            latest_otp = (
                PasswordResetOTP.objects
                .filter(user=user)
                .order_by("-created_at")
                .first()
            )

            if latest_otp:
                elapsed = (timezone.now() - latest_otp.created_at).total_seconds()

                if elapsed < 60:
                    remaining = int(60 - elapsed)

                    return render(request, "forgot_password.html", {
                        "error": f"Please wait {remaining} seconds before requesting another OTP."
                    })

            # Delete any previous OTP
            PasswordResetOTP.objects.filter(user=user).delete()

            # Generate secure OTP
            otp = str(secrets.randbelow(900000) + 100000)

            # Save OTP (valid for 10 minutes)
            PasswordResetOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=timezone.now() + timezone.timedelta(minutes=10)
            )

            # Default FixiGo details
            fixigo_data = {
                "email_customer": "support@fixigo.com",
                "number_customer": "+91 98765 43210",
                "address": "123 Workshop Street, Automobile City",
            }

            fixigo = Fixigo.objects.first()

            if fixigo:
                fixigo_data = {
                    "email_customer": fixigo.email_customer,
                    "number_customer": fixigo.number_customer,
                    "address": fixigo.address,
                }

            # Email Context
            context = {
                "first_name": user.first_name or user.username,
                "email": user.email,
                "otp": otp,
                "validity_minutes": 10,
                "fixigo": fixigo_data,
                "year": timezone.now().year,
                "timestamp": timezone.localtime().strftime("%d %B %Y, %I:%M %p"),
            }

            html_message = render_to_string(
                "email_otp_customer.html",
                context
            )

            plain_message = strip_tags(html_message)

            send_mail(
                subject="FixiGo - Password Reset OTP",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            # Store user info in session
            request.session["reset_user"] = user.id
            request.session["reset_email"] = user.email

            messages.success(
                request,
                f"An OTP has been sent to {user.email}. Please check your inbox."
            )

            logger.info("Password reset OTP sent to %s", user.email)

            return redirect("verify_otp")

        except User.DoesNotExist:
            logger.warning("Password reset requested for unknown email: %s", email)

            return render(request, "forgot_password.html", {
                "error": "No account found with this email address."
            })

        except Exception as e:
            logger.exception("Forgot password error: %s", e)

            return render(request, "forgot_password.html", {
                "error": "Unable to send OTP. Please try again later."
            })

    return render(request, "forgot_password.html")

#::::::::::::::::::::::Verify OTP Customer::::::::::::::::::::::
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    user_id = request.session.get("reset_user")
    if not user_id:
        return redirect("forgot_password")

    if request.method == "POST":

        entered = request.POST.get("otp")
        otp_obj = PasswordResetOTP.objects.filter(user_id=user_id).first()

        if otp_obj:

            if otp_obj.expires_at and timezone.now() > otp_obj.expires_at:

                otp_obj.delete()

                return render(request,"verify_otp.html",{
                    "error":"OTP Expired"
                })

            if otp_obj.otp == entered:

                request.session["otp_verified"] = True

                return redirect("reset_password")

        return render(request,"verify_otp.html",{
            "error":"Invalid OTP"
        })

    return render(request,"verify_otp.html")



#::::::::::::::::::::::Resent OTP Customer::::::::::::::::::::::
def resend_otp(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    user_id = request.session.get("reset_user")

    if not user_id:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': 'Session expired. Please try again.'
            }, status=400)
        return redirect("forgot_password")

    otp_obj = PasswordResetOTP.objects.filter(user_id=user_id).first()

    # Allow resend only after 60 seconds
    if otp_obj:
        elapsed = timezone.now() - otp_obj.created_at

        if elapsed < timedelta(seconds=60):
            remaining = 60 - int(elapsed.total_seconds())
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': f'Please wait {remaining} seconds before requesting another OTP.'
                }, status=400)
            
            messages.error(
                request,
                f"Please wait {remaining} seconds before requesting another OTP."
            )
            return redirect("verify_otp")

        otp_obj.delete()

    otp = str(secrets.randbelow(900000) + 100000)

    PasswordResetOTP.objects.create(
        user_id=user_id,
        otp=otp
    )

    user = User.objects.get(id=user_id)

    send_mail(
        "Password Reset OTP",
        f"Your new OTP is {otp}",
        None,
        [user.email],
        fail_silently=False,
    )

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': 'A new OTP has been sent to your registered email.'
        })
    
    messages.success(request, "A new OTP has been sent to your registered email.")
    return redirect("verify_otp")



#::::::::::::::::::::::Reset Password Customer::::::::::::::::::::::
def reset_password(request):
    if request.user.is_authenticated:
        return redirect("home")

    if not request.session.get("otp_verified"):
        return redirect("forgot_password")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:

            return render(request,"reset_password.html",{
                "error":"Passwords do not match"
            })

        user = User.objects.get(id=request.session["reset_user"])
        user.set_password(password)
        user.save()
        PasswordResetOTP.objects.filter(user=user).delete()
        request.session.flush()
        return redirect("login")

    return render(request,"reset_password.html")



#::::::::::::::::::::::Forgot Password Mechanic::::::::::::::::::::::
def forgot_password_mechanic(request):
    mech = check_mechanic_access(request)
    if not mech is None:
        return redirect("home_mechanic")

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            mechanic = Mechanic.objects.get(email=email)
            otp = str(secrets.randbelow(900000) + 100000)
            MechanicPasswordOTP.objects.filter(mechanic=mechanic).delete()
            MechanicPasswordOTP.objects.create(mechanic=mechanic, otp=otp)


            subject = "Fixigo - Mechanic Password Reset OTP"

            message = f"""
            Dear {mechanic.name},

            We received a request to reset the password for your Fixigo Mechanic account.

            ========================================
                    PASSWORD RESET OTP
                        {otp}
            ========================================

            This OTP is valid for 10 minutes and can be used only once.

            For your security:
            • Never share this OTP with anyone.
            • The Fixigo team will never ask for your OTP.
            • If you did not request a password reset, please ignore this email. Your account will remain secure.

            If you continue to experience issues accessing your account, please contact the Fixigo Support Team.

            Thank you for being a valued member of the Fixigo Mechanic Network.

            Best Regards,

            Team Fixigo
            Your Trusted Automobile Service Partner
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[mechanic.email],
                fail_silently=False,
            )

            request.session["mechanic_reset_id"] = mechanic.id

            return redirect("verify_otp_mechanic")

        except Mechanic.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect("forgot_password_mechanic")

    return render(request, "forgot_password_mechanic.html")



#::::::::::::::::::::::Verify OTP Mechanic::::::::::::::::::::::
def verify_otp_mechanic(request):
    mech = check_mechanic_access(request)
    if not mech is None:
        return redirect("home_mechanic")

    mechanic_id = request.session.get("mechanic_reset_id")

    if not mechanic_id:
        return redirect("forgot_password_mechanic")

    if request.method == "POST":

        otp = request.POST.get("otp")
        obj = MechanicPasswordOTP.objects.filter(
            mechanic_id=mechanic_id
        ).first()

        if not obj:
            messages.error(request, "OTP not found.")
            return redirect("verify_otp_mechanic")

        if obj.is_expired():
            obj.delete()
            messages.error(request, "OTP expired.")
            return redirect("verify_otp_mechanic")

        if obj.otp != otp:
            messages.error(request, "Invalid OTP.")
            return redirect("verify_otp_mechanic")

        request.session["otp_verified"] = True

        return redirect("reset_password_mechanic")

    return render(request, "verify_otp_mechanic.html")




#::::::::::::::::::::::Resend OTP Mechanic::::::::::::::::::::::
def resend_otp_mechanic(request):
    mech = check_mechanic_access(request)
    if not mech is None:
        return redirect("home_mechanic")

    mechanic_id = request.session.get("mechanic_reset_id")

    if not mechanic_id:
        return JsonResponse({
            "success": False,
            "error": "Session expired."
        })

    mechanic = Mechanic.objects.get(id=mechanic_id)

    old = MechanicPasswordOTP.objects.filter(
        mechanic=mechanic
    ).first()

    if old:

        diff = timezone.now() - old.created_at

        if diff < timedelta(seconds=60):

            return JsonResponse({
                "success": False,
                "error": f"Please wait {60-int(diff.total_seconds())} seconds."
            })

        old.delete()

    otp = str(secrets.randbelow(900000) + 100000)

    MechanicPasswordOTP.objects.create(
        mechanic=mechanic,
        otp=otp
    )

    send_mail(
        "Mechanic Password Reset OTP",
        f"Your new OTP is {otp}",
        None,
        [mechanic.email],
        fail_silently=False
    )

    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully."
    })





#::::::::::::::::::::::Reset Password Mechanic::::::::::::::::::::::
def reset_password_mechanic(request):
    mech = check_mechanic_access(request)
    if not mech is None:
        return redirect("home_mechanic")

    if not request.session.get("otp_verified"):
        return redirect("forgot_password_mechanic")

    mechanic = Mechanic.objects.get(
        id=request.session["mechanic_reset_id"]
    )

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password_mechanic")

        mechanic.password = make_password(password)
        mechanic.save()

        MechanicPasswordOTP.objects.filter(
            mechanic=mechanic
        ).delete()

        request.session.flush()

        messages.success(request, "Password changed successfully.")

        return redirect("login_mechanic")

    return render(request, "reset_password_mechanic.html")