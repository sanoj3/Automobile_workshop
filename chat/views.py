from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required

from .models import ChatRoom, ChatMessage
from customer.models import Customer
from superuser.models import Superadmin

from superuser.views import check_superuser_access



#::::::::::::::::::::::CUSTOMER CHAT DASHBOARD::::::::::::::::::::::
@login_required
def customer_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    customer = Customer.objects.get(user=request.user)

    pending_chats = ChatRoom.objects.filter(
        customer=customer,
        status='Pending'
    ).select_related(
        'booking',
        'booking__vehicle'
    ).order_by('-created_at')
    
    context = {
        'pending_chats': pending_chats,
        'user': request.user,
    }
    return render(request, 'customer_dashboard.html', context)



#::::::::::::::::::::::CUSTOMER CHAT::::::::::::::::::::::
@login_required
def customer_chat(request, room_id):
    if not request.user.is_authenticated:
        return redirect("login")
 
    customer = get_object_or_404(Customer,user=request.user)
    
    # Get chat room with related data
    room = get_object_or_404(
        ChatRoom.objects.select_related(
            "customer",
            "booking",
            "booking__vehicle",
        ),
        id=room_id,
        customer=customer
    )
    
    # Get messages
    messages = ChatMessage.objects.filter(
        room=room
    ).order_by("created_at")
    
    # Mark superuser messages as read
    ChatMessage.objects.filter(
        room=room,
        sender="superuser",
        is_read=False
    ).update(is_read=True)
    
    context = {
        "room": room,
        "message_contents": messages,
    }
    
    return render(
        request,
        "customer_chat.html",
        context
    )


#::::::::::::::::::::::CUSTOMER COMPLETE CHAT::::::::::::::::::::::
@login_required
def customer_complete_chat(request, room_id):
    if not request.user.is_authenticated:
        return redirect("login")
    
    customer = get_object_or_404(Customer,user=request.user)
    
    room = get_object_or_404(
        ChatRoom,
        id=room_id,
        customer=customer
    )
    
    # Only allow if not already completed
    if room.status != "Completed":
        room.customer_completed = True
        room.status = "Completed"
        room.completed_by = "customer"
        room.completed_at = timezone.now()
        room.save()
        
        # Add system message
        ChatMessage.objects.create(
            room=room,
            customer=customer,
            sender="customer",
            message="Customer has closed this chat",
            is_read=True
        )
    
    return redirect("customer_chat", room.id)



#::::::::::::::::::::::CUSTOMER COMPLETE CHAT HISTORY::::::::::::::::::::::
@login_required
def chat_history_customer(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    customer = Customer.objects.get(user=request.user)

    pending_chats = ChatRoom.objects.filter(
        customer=customer,
        status='Completed'
    ).select_related(
        'booking',
        'booking__vehicle'
    ).order_by('-created_at')
    
    context = {
        'pending_chats': pending_chats,
        'user': request.user,
    }
    return render(request, 'chat_history_customer.html', context)



#::::::::::::::::::::::SUPERUSER CHAT DASHBOARD::::::::::::::::::::::
def chat_dashboard(request):
    superuser = check_superuser_access(request)

    if superuser is None:
        return redirect('login_superuser')
    
    status = request.GET.get("status", "all")
    
    # Base queryset
    chat_rooms = ChatRoom.objects.select_related(
        "customer",
        "booking",
        "booking__vehicle"
    ).prefetch_related(
        Prefetch(
            "messages",
            queryset=ChatMessage.objects.order_by("-created_at")
        )
    )
    
    # Filter by status
    if status == "pending":
        chat_rooms = chat_rooms.filter(status="Pending")
    elif status == "completed":
        chat_rooms = chat_rooms.filter(status="Completed")
    
    # Annotate rooms with additional data
    for room in chat_rooms:
        # Last message
        room.last_message = room.messages.first()
        
        # Unread count for customer messages
        room.unread_count = room.messages.filter(
            sender="customer",
            is_read=False
        ).count()
        
        # Check if chat is closed (for UI)
        room.is_closed = room.status == "Completed"
    
    context = {
        "total_chats": ChatRoom.objects.count(),
        "pending_count": ChatRoom.objects.filter(
            status="Pending"
        ).count(),
        "completed_count": ChatRoom.objects.filter(
            status="Completed"
        ).count(),
        "chat_rooms": chat_rooms,
        "current_status": status,
        'superuser' : superuser
    }
    
    return render(
        request,
        "chat_dashboard.html",
        context
    )



#::::::::::::::::::::::SUPERUSER CHAT::::::::::::::::::::::
def superuser_chat(request, room_id):
    superuser = check_superuser_access(request)
    
    if superuser is None:
        return redirect('login_superuser')
    
    # Get Chat Room
    room = get_object_or_404(
        ChatRoom.objects.select_related(
            "customer",
            "booking",
            "booking__vehicle",
        ),
        id=room_id
    )
    
    # Get Messages
    messages = ChatMessage.objects.filter(
        room=room
    ).order_by("created_at")
    
    # Mark Customer Messages as Read
    ChatMessage.objects.filter(
        room=room,
        sender="customer",
        is_read=False
    ).update(is_read=True)
    
    context = {
        "room": room,
        "message_contents": messages,
        'superuser' : superuser
    }
    
    return render(
        request,
        "superuser_chat.html",
        context
    )


#::::::::::::::::::::::SUPERUSER COMPLETE CHAT::::::::::::::::::::::
def superuser_complete_chat(request, room_id):
    superuser = check_superuser_access(request)
    
    if superuser is None:
        return redirect('login_superuser')
    
    room = get_object_or_404(ChatRoom,id=room_id)
    
    superadmin = Superadmin.objects.get(id=request.session["super_user_id"])

    # Only allow if not already completed
    if room.status != "Completed":
        room.superuser_completed = True
        room.status = "Completed"
        room.completed_by = "superuser"
        room.completed_at = timezone.now()
        room.save()
        
        # Add system message
        ChatMessage.objects.create(
            room=room,
            superuser=superadmin,
            sender="superuser",
            message="Superuser has closed this chat",
            is_read=True
        )
    
    return redirect("superuser_chat", room.id)

