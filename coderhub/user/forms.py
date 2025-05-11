from django import forms
from .models import UserProfile, SolutionRequest
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image as PILImage
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms
from .models import Project
from .models import Feedback
from django import forms
from .models import Project
from .models import User  # Assuming 'User' is defined in your models.py

from .models import ContactSubmission

from django import forms
from .models import PasswordResetOTP

class OTPRequestForm(forms.Form):
    email = forms.EmailField(
    label='Email',
    widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email'})
)
    
class OTPVerifyForm(forms.Form):
    otp = forms.CharField(
        label='OTP',
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP'}),
        max_length=6,
        min_length=6
    )

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )







# forms.py
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
# forms.py
class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )

class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'email': forms.EmailInput(attrs={'required': True}),
        }
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

class SolutionRequestForm(forms.ModelForm):
    error_photo = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        help_text="Upload high-quality PNG (recommended) or JPG (min 800px width)",
        label="Error Screenshot"
    )

    class Meta:
        model = SolutionRequest
        fields = ['subject', 'description', 'error_photo']
        widgets = {
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your issue in detail...',
                'rows': 4
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Enter a brief title for your issue',
                'class': 'form-control-lg'
            }),
        }
        labels = {
            'subject': 'Issue Title',
            'description': 'Detailed Description'
        }
        help_texts = {
            'subject': 'Keep it concise (50-60 characters)',
            'description': 'Include error messages, line numbers, and what you\'ve tried'
        }

    def clean_error_photo(self):
        photo = self.cleaned_data.get('error_photo')
        
        if photo:
            try:
                img = PILImage.open(photo)
                
                # Maintain original format if PNG
                if photo.content_type == 'image/png':
                    return photo  # Return original PNG without modification

                # For JPEG images, ensure quality preservation
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Prevent upscaling and maintain aspect ratio
                if img.width < 800:
                    raise ValidationError("Image width should be at least 800 pixels for readability")

                # Save with quality parameters
                img_io = io.BytesIO()
                img.save(
                    img_io,
                    format='JPEG',
                    quality=95,  # Increased from default 75
                    optimize=True,
                    subsampling=0  # Keep maximum chroma resolution
                )
                img_io.seek(0)

                return InMemoryUploadedFile(
                    img_io,
                    None,
                    photo.name,
                    'image/jpeg',
                    img_io.getbuffer().nbytes,
                    None
                )

            except Exception as e:
                raise ValidationError(f"Image processing error: {str(e)}")
        
        return photo

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) > 100:
            raise ValidationError("Subject too long (max 100 characters)")
        return subject

# user/forms.py


class ProjectUploadForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'technology', 'file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.zip'})
        }


# forms.py

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'message']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
                attrs={'class': 'd-none'}  # Hide default radio buttons
            ),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your feedback...'}),
        }