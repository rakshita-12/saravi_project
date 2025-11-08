from django.urls import path
from . import views

urlpatterns = [
    # ---------- Home ----------
    path('', views.home, name='home'),

    # ---------- Authentication ----------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #path('student/login/', views.student_login, name='student_login'),
    #path('faculty/login/', views.faculty_login, name='faculty_login'), 

    # ---------- Student Routes ----------
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/submit/<int:question_id>/', views.submit_code, name='submit_code'),
    path('student/run_code/', views.run_student_code, name='run_code'),

    # ---------- Faculty Routes ----------
    path('faculty/login/', views.faculty_login, name='faculty_login'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/upload-questions/', views.upload_questions, name='upload_question'),
    path('faculty/review-submissions/', views.review_submissions, name='review_submissions'),
    path('faculty/performance-reports/', views.performance_reports, name='performance_reports'),
    path('faculty/announcements/', views.announcements, name='faculty_announcements'),

    # ---------- Shared ----------
    path('announcements/', views.announcements, name='announcements'),
]
