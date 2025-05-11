from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import UserProfile, SolutionRequest, Message, Conversation
from .forms import ProfileUpdateForm, SolutionRequestForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .forms import FeedbackForm
from .models import Feedback
from django.utils import timezone
# Add this to your imports in views.py
from .models import Feedback
from django.db.models import Count, Q, Max
from .models import Project 
from django.shortcuts import get_object_or_404
# Add at the top with other imports
from .forms import ProjectUploadForm
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
    # Add to existing imports
from .models import Quiz
from django.contrib.auth.decorators import user_passes_test
from .forms import AdminUserForm
from .models import Subscriber
from .forms import NewsletterForm
from .forms import ContactForm
from .models import ContactSubmission
from django.http import JsonResponse
from .models import ContactSubmission
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

    # views.py
from .forms import ContactForm
from .models import ContactSubmission

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Project  # Assuming Project model is created
from django.shortcuts import render

from django.http import FileResponse
import os
from django.template import Template, Context
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Quiz, QuizSubmission

from django.http import HttpResponse, FileResponse
import os



from django.template import RequestContext  # Add this import


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import PasswordResetOTP
from .forms import OTPRequestForm, OTPVerifyForm, PasswordResetForm

def send_otp(request):
    if request.method == 'POST':
        form = OTPRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate 6-digit OTP
                otp = str(random.randint(100000, 999999))
                
                # Create or update OTP
                PasswordResetOTP.objects.filter(user=user).update(is_used=True)
                PasswordResetOTP.objects.create(user=user, otp=otp)
                
                # Send email
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                request.session['reset_email'] = email
                return redirect('verify_otp')
            except User.DoesNotExist:
                form.add_error('email', 'Email not found')
    else:
        form = OTPRequestForm()
    return render(request, 'user/otp_request.html', {'form': form})



def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset')

    user = get_object_or_404(User, email=email)
    form = OTPVerifyForm()

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp']
            otp_record = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp_entered,
                is_used=False
            ).first()

            if otp_record and otp_record.is_valid():
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP')
        else:
            messages.error(request, 'Please enter a valid 6-digit OTP')

    return render(request, 'user/verify_otp.html', {'form': form})




def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset')
    
    user = get_object_or_404(User, email=email)
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_password'] == form.cleaned_data['confirm_password']:
                # Check OTP validity
                otp_record = PasswordResetOTP.objects.filter(
                    user=user,
                    is_used=False
                ).order_by('-created_at').first()
                
                if otp_record and otp_record.is_valid():
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()
                    otp_record.is_used = True
                    otp_record.save()
                    messages.success(request, 'Password reset successfully! Please login.')
                    return redirect('login')
                else:
                    messages.error(request, 'Invalid or expired OTP')
            else:
                messages.error(request, 'Passwords do not match')
    else:
        form = PasswordResetForm()
    
    return render(request, 'user/reset_password.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'user/change_password.html', {
        'form': form
    })


def quiz_submissions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    submissions = QuizSubmission.objects.filter(quiz=quiz)
    return render(request, 'user/quiz_submissions.html', {
        'quiz': quiz,
        'submissions': submissions,

    })


def admin_quizzes(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        quiz_file = request.FILES.get('quiz_file')
        Quiz.objects.create(title=title, file=quiz_file)
        return redirect('admin_quizzes')
    profile = get_user_profile(request.user) # Get profile
    quizzes = Quiz.objects.all()
    return render(request, 'user/admin_quizzes.html', {'quizzes': quizzes,'profile':profile})


from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, "You need to login to take the quiz")
        return redirect('login')
    
    # Check previous submissions
    previous_submission = QuizSubmission.objects.filter(
        user=request.user, 
        quiz=quiz
    ).order_by('-submitted_at').first()

    # Submission validation logic
    if previous_submission:
        if previous_submission.passed:
            messages.error(request, "You've already passed this quiz and cannot take it again.")
            return redirect('quiz')
        else:
            # Calculate if 15 days have passed since last attempt
            retake_date = previous_submission.submitted_at + timedelta(days=15)
            if timezone.now() < retake_date:
                messages.error(request, 
                    f"You can retake this quiz after {retake_date.strftime('%Y-%m-%d')}. "
                    "Minimum 15 days required between failed attempts.")
                return redirect('quiz')

    # Handle quiz submission
    if request.method == 'POST':
        score = calculate_score(request.POST)
        passed = score >= 22  # Passing threshold

        # Create new submission
        QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            passed=passed
        )

        # Update user profile stats
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if passed:
            profile.wins += 1
            messages.success(request, "Congratulations! You've passed the quiz!")
        else:
            profile.losses += 1
            messages.warning(request, "Quiz attempt failed. You can try again after 15 days.")
        profile.save()

        return render(request, 'user/quiz_result.html', {
            'score': score,
            'passed': passed,
            'show_reward': passed,
            'quiz': quiz,
            'retake_date': timezone.now() + timedelta(days=15) if not passed else None
        })

    # Handle GET request - show quiz
    try:
        with open(quiz.file.path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        messages.error(request, "Quiz file not found")
        return redirect('quiz')

    template = Template(template_content)
    context = RequestContext(request, {
        'quiz': quiz,
        'terms_conditions': True,  # Flag to show terms in template
        'last_attempt': previous_submission.submitted_at if previous_submission else None,
        'retake_available': previous_submission and (timezone.now() >= retake_date) if previous_submission else False
    })
    
    rendered_content = template.render(context)
    return HttpResponse(rendered_content)



      
ANSWER_KEY = {
    'q1': 'b',
    'q2': 'a',
    'q3': 'a',
    'q4': 'a',
    'q5': 'b',
    'q6': 'b',
    'q7': 'b',
    'q8': 'a',
    'q9': 'b',
    'q10': 'c',
    'q11': 'b',
    'q12': 'a',
    'q13': 'a',
    'q14': 'a',
    'q15': 'a',
    'q16': 'a',
    'q17': 'c',
    'q18': 'b',
    'q19': 'b',
    'q20': 'a',
    'q21': 'a',
    'q22': 'a',
    'q23': 'a',
    'q24': 'b',
    'q25': 'b',
    'q26': 'a',
    'q27': 'a',
    'q28': 'a',
    'q29': 'a',
    'q30': 'a',
}

def calculate_score(user_answers):
    score = 0
    for question, correct_answer in ANSWER_KEY.items():
        if user_answers.get(question) == correct_answer:
            score += 1
    return score

def project_page(request):
    return render(request, 'project.html')  # Ensure 'project.html' exists in templates
# views.py (project_list view)
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'user/project.html', {'projects': projects})  # Adjusted path



@login_required
def upload_project(request):
    if request.method == "POST":
        form = ProjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, "Project uploaded successfully!")
            return redirect("projects")  # Updated to match the URL pattern name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectUploadForm()
    
    return render(request, "user/upload_project.html", {"form": form})



def mark_as_read(request, solution_id):
    if request.method == 'POST':
        Message.objects.filter(
            conversation__solution_request_id=solution_id,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def get_user_profile(user):
    if user.is_authenticated:
        try:
            return UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            pass
    return None


@login_required
def view_messages(request):
    conversations = Conversation.objects.filter(
        Q(solution_request__user=request.user) |
        Q(participant=request.user) 
    ).annotate(
        last_message=Max('messages__timestamp'),
        unread_count=Count('messages', filter=Q(messages__recipient=request.user) & Q(messages__is_read=False))
    ).order_by('-last_message')
    profile = get_user_profile(request.user) # Get profile


    return render(request, 'user/messages.html', {'conversations': conversations,'profile': profile})
@login_required
def delete_solution(request, solution_id):
    solution = get_object_or_404(SolutionRequest, id=solution_id)
    if solution.user != request.user:
        messages.error(request, "You don't have permission to delete this request.")
        return redirect('home')
    
    if request.method == 'POST':
        solution.delete()
        messages.success(request, "Solution request deleted successfully!")
        return redirect('profile')
    
    return render(request, 'user/confirm_delete.html', {'solution': solution})


# views.py


# In your views.py file

# from django.shortcuts import render, redirect
# from django.contrib import messages  # Import messages framework
# from .forms import FeedbackForm, NewsletterForm  # Assuming NewsletterForm is in forms.py
# from .models import Feedback, SolutionRequest, UserProfile  # Import UserProfile and SolutionRequest

# def home(request):
#     solutions = SolutionRequest.objects.all().order_by('-created_at')
#     newsletter_form = NewsletterForm()
#     feedback_form = FeedbackForm()
#     has_submitted = False
#     profile = None # Initialize profile to None

#     if request.user.is_authenticated:
#         has_submitted = Feedback.objects.filter(user=request.user).exists()
#         try:
#             # Attempt to get the user's profile
#             # Assuming a OneToOneField named 'userprofile' on your UserProfile model
#             profile = request.user.userprofile
#         except UserProfile.DoesNotExist:
#             # Handle the case where a user exists but has no profile
#             # You might want to log this or handle it differently depending on your app
#             pass # For now, we'll just let profile remain None

#     if request.method == 'POST':
#         # Handle feedback submission
#         # Check if the POST request is for feedback based on the presence of 'rating'
#         if 'rating' in request.POST:
#             if not request.user.is_authenticated:
#                 messages.warning(request, 'Please login to submit feedback')
#                 # Consider redirecting back to the home page after login attempt
#                 # You might need to store the current URL in session or a query parameter
#                 return redirect('login')

#             feedback_form = FeedbackForm(request.POST)
#             if feedback_form.is_valid():
#                 # Check if user has already submitted feedback before saving again
#                 if not Feedback.objects.filter(user=request.user).exists():
#                     feedback = feedback_form.save(commit=False)
#                     feedback.user = request.user
#                     feedback.save()
#                     messages.success(request, 'Thank you for your feedback!')
#                 else:
#                     messages.info(request, 'You have already submitted feedback.')
#                 return redirect('home') # Redirect to home after successful submission or existing feedback
#             else:
#                 # If feedback form is invalid, messages are already handled by the form in the template
#                  messages.error(request, 'There were errors in your feedback submission.') # Add a general error message

#         # Handle newsletter submission (assuming a separate submit button or field)
#         # You might need to add a check here to differentiate newsletter submission
#         # from feedback submission if both forms are on the same page and use POST.
#         # A common way is to add a hidden input or check for a specific field name.
#         # Example: if 'newsletter_email' in request.POST:
#         if 'email' in request.POST and newsletter_form.is_valid(): # Basic check for newsletter field
#              newsletter_form = NewsletterForm(request.POST)
#              if newsletter_form.is_valid():
#                  newsletter_form.save()
#                  messages.success(request, 'Thank you for subscribing to our newsletter!')
#                  return redirect('home') # Redirect to home after successful subscription
#              else:
#                  messages.error(request, 'Invalid email address for newsletter.') # Add an error message

#     context = {
#         'profile': profile,  # Pass the profile to the context
#         'solutions': solutions,
#         'newsletter_form': newsletter_form,
#         'feedback_form': feedback_form,
#         'has_submitted': has_submitted,
#     }
#     return render(request, 'user/home.html', context)


# In your views.py file

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Import your models and forms
# Change NewsletterSubscription to Subscriber here:
from .models import UserProfile, SolutionRequest, Feedback, Subscriber
from .forms import FeedbackForm, NewsletterForm

# Example Home View
def home(request):
    solutions = SolutionRequest.objects.all().order_by('-created_at')
    feedback_form = FeedbackForm()
    newsletter_form = NewsletterForm()
    has_submitted = False
    profile = None

    if request.user.is_authenticated:
        has_submitted = Feedback.objects.filter(user=request.user).exists()
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            pass

    if request.method == 'POST':
        # --- Handle Feedback Submission ---
        if 'rating' in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to submit feedback')
                return redirect('login')

            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                if not Feedback.objects.filter(user=request.user).exists():
                    feedback = feedback_form.save(commit=False)
                    feedback.user = request.user
                    feedback.save()
                    messages.success(request, 'Thank you for your feedback!')
                else:
                     messages.info(request, 'You have already submitted feedback.')

                newsletter_form = NewsletterForm()
                feedback_form = FeedbackForm()
                if request.user.is_authenticated:
                    has_submitted = Feedback.objects.filter(user=request.user).exists()

                return redirect('home')
            else:
                messages.error(request, 'There were errors in your feedback submission. Please try again.')

        # --- Handle Newsletter Submission ---
        elif 'newsletter_email' in request.POST: # Assuming your submit button name is 'newsletter_email'
             newsletter_form = NewsletterForm(request.POST)
             if newsletter_form.is_valid():
                 email = newsletter_form.cleaned_data['email']
                 try:
                     # Use the Subscriber model to create a new subscriber
                     Subscriber.objects.create(email=email)
                     messages.success(request, 'Thank you for subscribing to our newsletter!')
                 except Exception as e:
                     # Handle potential errors, e.g., duplicate email if unique=True
                     messages.error(request, f'There was an error subscribing: {e}')


                 newsletter_form = NewsletterForm()
                 feedback_form = FeedbackForm()
                 if request.user.is_authenticated:
                    has_submitted = Feedback.objects.filter(user=request.user).exists()


                 return redirect('home')
             else:
                 messages.error(request, 'Invalid email address for newsletter.')

    context = {
        'profile': profile,
        'solutions': solutions,
        'newsletter_form': newsletter_form,
        'feedback_form': feedback_form,
        'has_submitted': has_submitted,
    }
    return render(request, 'user/home.html', context)

# ... rest of your views.py

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login Successfully!!!')
                if is_admin(user):
                    return redirect('admin_panel')
                else:
                    return redirect('profile')

            else:
                messages.error(request, 'Wrong Password')
        except User.DoesNotExist:
            messages.error(request, 'Email does not exist')

    return render(request, 'user/login.html')



@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


def about(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = None

    return render(request, 'user/about.html', {
        'user': request.user,
        'profile': profile,

    })

def quiz(request):
    quizzes = Quiz.objects.all()
    enhanced_quizzes = []
    
    for quiz in quizzes:
        quiz_data = {
            'quiz': quiz,
            'submission': None,
            'can_retake': False,
        }
        
        if request.user.is_authenticated:
            # Get user's latest submission for this quiz
            submission = QuizSubmission.objects.filter(
                user=request.user,
                quiz=quiz
            ).order_by('-submitted_at').first()
            
            if submission:
                quiz_data['submission'] = submission
                if not submission.passed:
                    retake_date = submission.submitted_at + timedelta(days=15)
                    quiz_data['can_retake'] = timezone.now() >= retake_date
        
        enhanced_quizzes.append(quiz_data)
        profile = get_user_profile(request.user) 
    
    return render(request, 'user/quiz.html', {'quizzes': enhanced_quizzes,'profile':profile})
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken by another user.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered. Please login.')
            return redirect('login')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Your account has been created! You can now log in.')
        return redirect('login')

    return render(request, 'user/signup.html')

def service(request):
    profile = get_user_profile(request.user) # Get profile
    return render(request, 'user/service.html', {'profile': profile}) # Pass profile to context
@login_required
def solution(request):
    if request.method == 'POST':
        form = SolutionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            solution_request = form.save(commit=False)
            solution_request.user = request.user
            solution_request.save()
            messages.success(request, 'Your solution request has been submitted!')
            return redirect('home')
    else:
        form = SolutionRequestForm()
    
    return render(request, 'user/solution.html', {'form': form})

def project(request):
    return render(request, 'user/project.html')

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    if request.method == 'POST':
        if 'remove_image' in request.POST:
            user_profile.image.delete(save=False)
            user_profile.image = None
            user_profile.save()
            messages.success(request, 'Profile photo removed successfully!')
            return redirect('profile')
        
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'user/profile.html', {
        'user': request.user,
        'profile': user_profile,
        'form': form,
        'unread_count': unread_count
    })


@login_required
def chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        Q(id=conversation_id) &
        (Q(solution_request__user=request.user) | Q(participant=request.user))
    )

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Determine recipient
            if request.user == conversation.solution_request.user:
                recipient = conversation.participant
            else:
                recipient = conversation.solution_request.user
            
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                recipient=recipient,
                content=content
            )
            return redirect('chat', conversation_id=conversation_id)

    messages = conversation.messages.all().order_by('timestamp')
    
    # Mark received messages as read
    messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'user/chat.html', {
        'conversation': conversation,
        'messages': messages,
        'solution_request': conversation.solution_request
    })
    
 


@login_required
def delete_solution(request, solution_id):
    solution = get_object_or_404(SolutionRequest, id=solution_id, user=request.user)
    
    if request.method == 'POST':
        solution.delete()
        messages.success(request, 'Solution request deleted successfully.')
        return redirect('profile_solutions')

    return render(request, 'user/confirm_delete.html', {'solution': solution})


@login_required
def start_conversation(request, solution_id):
    solution_request = get_object_or_404(SolutionRequest, id=solution_id)
    
    # Create or get conversation
    conversation, created = Conversation.objects.get_or_create(
        solution_request=solution_request,
        participant=request.user
    )
    
    return redirect('chat', conversation_id=conversation.id)



@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect('profile')
    
    return redirect('profile')

def is_admin(user):
    return user.is_authenticated and (user.email == "rahulboga62@gmail.com" or user.is_superuser)
@login_required
@user_passes_test(is_admin, login_url='home')
def admin_panel(request):
    user_count = User.objects.count()
    profile = get_user_profile(request.user) 
    context = {

        'user_count': user_count,
        'profile': profile,
        'active_users': User.objects.filter(is_active=True).count(),
        'projects_count': Project.objects.count()
    }
    return render(request, 'user/admin_panel.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('admin_panel')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'user/admin_edit_user.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.username} deleted successfully!')
        return redirect('admin_panel')
    return render(request, 'user/admin_confirm_delete.html', {'user': user})

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    profile = get_user_profile(request.user) # Get profile

    return render(request, 'user/admin_users.html', {'users': users,'profile':profile})



# views.py
@login_required
@user_passes_test(is_admin, login_url='home')
def admin_subscribers(request):
    profile = get_user_profile(request.user) # Get profile
    subscribers = Subscriber.objects.all().order_by('-date_subscribed')
    return render(request, 'user/admin_subscribers.html', {'subscribers': subscribers,'profile':profile})

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_delete_subscriber(request, subscriber_id):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    if request.method == 'POST':
        subscriber.delete()
        messages.success(request, 'Subscriber deleted successfully')
        return redirect('admin_subscribers')
    return render(request, 'user/admin_confirm_delete_subscriber.html', {'subscriber': subscriber})



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    profile = get_user_profile(request.user) # Get profile
    return render(request, 'user/contact.html', {'form': form,'profile': profile})


@login_required
@user_passes_test(is_admin, login_url='home')
def admin_view_submission(request, submission_id):
    submission = get_object_or_404(ContactSubmission, id=submission_id)
    return render(request, 'user/admin_view_submission.html', {'submission': submission})
# views.py

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_contact_submissions(request):
    profile = get_user_profile(request.user) # Get profile
    submissions = ContactSubmission.objects.all().order_by('-submitted_at')
    return render(request, 'user/admin_contact_submissions.html', {'submissions': submissions,'profile':profile})

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_delete_submission(request, submission_id):
    submission = get_object_or_404(ContactSubmission, id=submission_id)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Submission deleted successfully')
        return redirect('admin_contact_submissions')
    return render(request, 'user/admin_confirm_delete_submission.html', {'submission': submission})


def project_list(request):
    projects = Project.objects.all()
    search_query = request.GET.get('q', '')
    
    if search_query:
        projects = projects.filter(title__icontains=search_query)
    
    return render(request, 'user/project.html', {'projects': projects})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_projects = Project.objects.filter(user=user)
    
    context = {
        'profile_user': user,
        'user_projects': user_projects
    }
    return render(request, 'user/user_profile.html', context)


# Add with other imports


@login_required
@user_passes_test(is_admin, login_url='home')
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('admin_quizzes')
    return redirect('admin_quizzes')






from django.shortcuts import render

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_feedback(request):
    # Implement the logic to fetch user feedback
    feedbacks = Feedback.objects.all()  # or however you store it
    profile = get_user_profile(request.user) # Get profile
    return render(request, 'user/admin_feedback.html', {'feedbacks': feedbacks,'profile':profile})




@login_required
@user_passes_test(is_admin, login_url='home')
def admin_delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Feedback deleted successfully!')
        return redirect('admin_feedback')
    return render(request, 'user/admin_confirm_delete_feedback.html', {'feedback': feedback})


@login_required
def profile_solutions(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = get_user_profile(request.user) # Get profile
    user_solutions = SolutionRequest.objects.filter(user=request.user) # Assuming you want to list solutions

    return render(request, 'user/profile_solutions.html', {
        'profile': profile, # Pass profile to context
        'user_solutions': user_solutions # Pass user solutions
    })



@login_required
def my_projects(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = get_user_profile(request.user) # Get profile
    user_projects = Project.objects.filter(user=request.user) # Assuming you want to list projects

    return render(request, 'user/my_projects.html', {
        'profile': profile, # Pass profile to context
        'user_projects': user_projects # Pass user projects
    })