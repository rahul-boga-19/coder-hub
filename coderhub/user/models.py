from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

 # Ensure this line is present

# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

from django.utils import timezone
from datetime import datetime



from django.db import models
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class PasswordResetOTP(models.Model):  # ✅ This is your custom model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 900


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='quizzes/')
    created_at = models.DateTimeField(auto_now_add=True)
    total_marks = models.IntegerField(default=30)

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    passed = models.BooleanField(default=False)  # Add this field
    submitted_at = models.DateTimeField(auto_now_add=True)





# models.py
class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"



# models.py
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    technology = models.CharField(max_length=255)
    file = models.FileField(upload_to="projects/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


    class Meta:
        db_table="Projects"






class SolutionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    error_photo = models.ImageField(upload_to='error_photos/')  # Original image only
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"Request by {self.user.username}"

class Conversation(models.Model):
    solution_request = models.ForeignKey(SolutionRequest, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Convo about {self.solution_request.subject}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)  # Add this
    losses = models.PositiveIntegerField(default=0)  # Add this
    # ... other fields

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"



# models.py
# models.py
class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)