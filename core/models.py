# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

class User(AbstractUser):
    ROLES = (
        ('LEARNER', 'Learner'),
        ('SKILL_SHARER', 'Skill Sharer'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    bio = models.TextField(blank=True)
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sharer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    @property
    def reviews(self):
        return Review.objects.filter(booking__skill=self)
    
    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else 0
    
    @property
    def review_count(self):
        return self.reviews.count()

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_learner')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    # New fields for skill swapping - made nullable
    swap_skill_name = models.CharField(max_length=200, null=True, blank=True)
    swap_skill_description = models.TextField(null=True, blank=True)
    swap_skill_duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True)
    swap_skill_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='swap_bookings',
        null=True,
        blank=True
    )
    
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)