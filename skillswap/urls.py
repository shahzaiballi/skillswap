# skillswap/urls.py
from django.contrib import admin
from django.urls import path
from core import views
from core.views import signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('learner/dashboard/', views.learner_dashboard, name='learner_dashboard'),
    path('sharer/dashboard/', views.sharer_dashboard, name='sharer_dashboard'),
    path('skills/manage/', views.skill_management, name='skill_management'),
    path('skills/browse/', views.browse_skills, name='browse_skills'),
    path('skills/book/<int:skill_id>/', views.book_session, name='book_session'),
    path('booking/<int:booking_id>/accept/', views.accept_booking, name='accept_booking'),
    path('booking/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('skills/<int:skill_id>/edit/', views.edit_skill, name='edit_skill'),
    path('skills/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),
    path('submit-review/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('mark-booking-completed/<int:booking_id>/', views.mark_booking_completed, name='mark_booking_completed'),
    path('toggle-notification/<int:notification_id>/', views.toggle_notification, name='toggle_notification'),
    path('signup/', signup, name='signup'),

    
]