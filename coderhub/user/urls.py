from django.urls import path
from .views import * 
from django.conf import settings
from django.conf.urls.static import static
from .views import project_page
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('feedback/', admin_feedback, name='admin_feedback'),
    path('feedback/delete/<int:feedback_id>/', admin_delete_feedback, name='admin_delete_feedback'),
    path('about/', about, name='about'),
    path('profile/solutions/', profile_solutions, name='profile_solutions'),
    path('profile/projects/', my_projects, name='my_projects'),

    path('contact/', contact, name='contact'),
    path('quiz/', quiz, name='quiz'),
    path('login/', user_login, name='login'),
    path('signup/', signup, name='signup'),
    path('service/', service, name='service'),
    path('solution/', solution, name='solution'),
    path('project/', project, name='project'),
    path('profile/', profile, name='profile'),
    path('project_list/', project_list, name='project_list'),
    path('user/<str:username>/', user_profile, name='user_profile'),
    path('admin_quizzes/', admin_quizzes, name='admin_quizzes'),
    path('quiz-submissions/<int:quiz_id>/', quiz_submissions, name='quiz_submissions'),
    path('take_quiz/<int:quiz_id>/', take_quiz, name='take_quiz'),
    path('delete_quiz/<int:quiz_id>/', delete_quiz, name='delete_quiz'),
    path('change-password/', change_password, name='change_password'),
    path('password-reset/', send_otp, name='password_reset'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),






  


    path('logout/', user_logout, name='logout'),
    path('chat/<int:conversation_id>/', chat, name='chat'),
    path('messages/',view_messages, name='view_messages'),
    path('delete-solution/<int:solution_id>/', delete_solution, name='delete_solution'),
    path('mark-read/<int:solution_id>/', mark_as_read, name='mark_as_read'),
    path('start-conversation/<int:solution_id>/', start_conversation, name='start_conversation'),
    path("upload_project/", upload_project, name="upload_project"),
    path('projects/', project_list, name='projects'),  # This shows projects list
    path('project/', project_page, name='project_page'),  
    path('upload-project/',upload_project, name='upload_project'),
    path('delete-project/<int:project_id>/', delete_project, name='delete_project'),
    path('admin-panel/', admin_panel, name='admin_panel'),
    path('users/',admin_users, name='admin_users'),
    path('admin-edit-user/<int:user_id>/', admin_edit_user, name='admin_edit_user'),
    path('admin-delete-user/<int:user_id>/',admin_delete_user, name='admin_delete_user'),
    path('subscribers/', admin_subscribers, name='admin_subscribers'),
    path('subscribers/delete/<int:subscriber_id>/', admin_delete_subscriber, name='admin_delete_subscriber'),
     path('contact-submissions/view/<int:submission_id>/', admin_view_submission, name='admin_view_submission'),
    path('contact-submissions/', admin_contact_submissions, name='admin_contact_submissions'),
    path('contact-submissions/delete/<int:submission_id>/',admin_delete_submission, name='admin_delete_submission'),


    



    
     # Added logout route
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)