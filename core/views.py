# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Skill, Booking, Category, Notification
from .forms import LoginForm, SkillForm  # Add SkillForm import here
from .forms import BookingForm
from .models import Skill, Booking, Review, Notification
from .forms import ReviewForm
from .forms import SignUpForm
def home(request):
    featured_skills = (
        Skill.objects.filter(is_available=True)
        .select_related('sharer', 'category')
        .prefetch_related('booking_set__review')
        .order_by('-created_at')[:6]
    )
    
    context = {
        'featured_skills': featured_skills,
        'categories': Category.objects.all()[:3]
    }
    return render(request, 'home.html', context)

@login_required
def learner_dashboard(request):
    bookings = Booking.objects.filter(
        learner=request.user
    ).select_related(
        'skill', 
        'skill__sharer'
    ).prefetch_related(
        'review'
    ).order_by('-booking_date', '-booking_time')
    
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'notifications': notifications,
    }
    return render(request, 'learner_dashboard.html', context)

@login_required
def sharer_dashboard(request):
    skills = Skill.objects.filter(
        sharer=request.user
    ).select_related('category').order_by('-created_at')
    
    bookings = Booking.objects.filter(
        skill__sharer=request.user
    ).select_related('skill', 'learner').order_by('-booking_date', '-booking_time')
    
    context = {
        'skills': skills,
        'bookings': bookings,
    }
    return render(request, 'sharer_dashboard.html', context)

@login_required
def skill_management(request):
    if request.user.role != 'SKILL_SHARER':
        messages.error(request, 'Only skill sharers can access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.sharer = request.user
            skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('sharer_dashboard')
    else:
        form = SkillForm()
    
    skills = Skill.objects.filter(sharer=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'skills': skills
    }
    return render(request, 'skill_management.html', context)

@login_required
def browse_skills(request):
    categories = Category.objects.all()
    skills = Skill.objects.filter(
        is_available=True
    ).select_related('sharer', 'category')
    
    category_id = request.GET.get('category')
    if category_id:
        skills = skills.filter(category_id=category_id)
    
    context = {
        'categories': categories,
        'skills': skills,
    }
    return render(request, 'browse_skills.html', context)

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    if user.role == 'LEARNER':
                        return redirect('learner_dashboard')
                    else:
                        return redirect('sharer_dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def book_session(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, is_available=True)
    
    if skill.sharer == request.user:
        messages.error(request, "You cannot book your own skill session.")
        return redirect('browse_skills')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.learner = request.user
            booking.skill = skill
            booking.status = 'PENDING'
            booking.save()
            
            messages.success(request, "Booking request sent successfully!")
            return redirect('learner_dashboard')
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'skill': skill
    }
    return render(request, 'book_session.html', context)

@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, skill__sharer=request.user)
    
    if request.method == 'POST':
        booking.status = 'CONFIRMED'
        booking.save()
        messages.success(request, "Booking confirmed successfully!")
        return redirect('sharer_dashboard')
        
    return redirect('sharer_dashboard')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, skill__sharer=request.user)
    
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, "Booking declined.")
        return redirect('sharer_dashboard')
        
    return redirect('sharer_dashboard')

@login_required
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, sharer=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully!')
            return redirect('skill_management')
    else:
        form = SkillForm(instance=skill)
    
    context = {
        'form': form,
        'skill': skill,
        'is_edit': True
    }
    return render(request, 'edit_skill.html', context)

@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, sharer=request.user)
    
    if request.method == 'POST':
        # Check if there are any active bookings
        active_bookings = Booking.objects.filter(
            skill=skill,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()
        
        if active_bookings:
            messages.error(request, 'Cannot delete skill with active bookings.')
        else:
            skill.delete()
            messages.success(request, 'Skill deleted successfully!')
        
        return redirect('skill_management')
    
    context = {
        'skill': skill
    }
    return render(request, 'delete_skill_confirm.html', context)

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, learner=request.user)
    
    if booking.status != 'COMPLETED':
        messages.error(request, "You can only review completed sessions.")
        return redirect('learner_dashboard')
    
    if hasattr(booking, 'review'):
        messages.error(request, "You have already reviewed this session.")
        return redirect('learner_dashboard')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            
            # Create notification for skill sharer using trigger
            # Notification will be created by the trigger
            
            messages.success(request, "Thank you for your review!")
            return redirect('learner_dashboard')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'booking': booking
    }
    return render(request, 'submit_review.html', context)

@login_required
def mark_booking_completed(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, learner=request.user)
    
    if request.method == 'POST':
        if booking.status != 'CONFIRMED':
            messages.error(request, "Only confirmed bookings can be marked as completed.")
            return redirect('learner_dashboard')
            
        booking.status = 'COMPLETED'
        booking.save()
        messages.success(request, "Session marked as completed. You can now leave a review!")
        return redirect('learner_dashboard')
        
    return redirect('learner_dashboard')
@login_required
def toggle_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = not notification.is_read
    notification.save()
    return redirect('learner_dashboard')

@login_required
def learner_dashboard(request):
    show_all = request.GET.get('show_all', False)
    
    bookings = Booking.objects.filter(
        learner=request.user
    ).select_related(
        'skill', 
        'skill__sharer'
    ).prefetch_related(
        'review'
    ).order_by('-booking_date', '-booking_time')
    
    notifications = Notification.objects.filter(user=request.user)
    if not show_all:
        notifications = notifications.filter(is_read=False)
    notifications = notifications.order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'notifications': notifications,
        'show_all': show_all,
    }
    return render(request, 'learner_dashboard.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            if user.role == 'LEARNER':
                return redirect('learner_dashboard')
            else:
                return redirect('sharer_dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})