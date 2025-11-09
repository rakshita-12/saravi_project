from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
import csv
import json

from .models import Student, Faculty, Question, Submission, Announcement
from .local_ai_evaluator import evaluate_submission  # Your AI evaluator script


# ---------- Home ----------
def home(request):
    return render(request, 'core/home.html')


# ---------- Login ----------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if hasattr(user, 'student'):
                return redirect('student_dashboard')
            elif hasattr(user, 'faculty'):
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "User profile not found.")
                logout(request)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'core/login.html')


def student_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'student'):
            login(request, user)
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid student credentials")

    return render(request, 'core/student_login.html')


def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'faculty'):
            login(request, user)
            return redirect("faculty_dashboard")
        else:
            messages.error(request, "Invalid faculty credentials")

    return render(request, "core/faculty_login.html")


# ---------- Logout ----------
def logout_view(request):
    """Single logout for both student and faculty"""
    logout(request)
    return render(request, 'core/logout.html')  # Show confirmation page


# ---------- Student Dashboard ----------
@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('logout')

    faculty = student.faculty
    questions = Question.objects.filter(faculty=faculty) if faculty else []
    submissions = Submission.objects.filter(student=student)

    # Language icons
    languages = {
        "Python": "🐍",
        "C++": "💻",
        "Java": "☕",
        "C": "⚙️",
    }

    context = {
        "student": student,
        "faculty": faculty,
        "questions": questions,
        "submissions": submissions,
        "languages": languages,
    }

    return render(request, 'core/student_dashboard.html', context)


@login_required
def run_student_code(request):
    if request.method == "POST":
        data = request.POST
        code = data.get("code")
        lang = data.get("language")
        test_input = data.get("input", "")
        expected_output = data.get("expected", "")
        
        test_cases = [{"input": test_input, "expected": expected_output}]

        report = evaluate_submission(code, lang, test_cases)
        
        # Format response for the run button
        result = report.get('results', [{}])[0] if report.get('results') else {}
        
        return JsonResponse({
            "score": report.get('score', 0),
            "test_case_score": report.get('test_case_score', 0),
            "logic_score": report.get('logic_score'),
            "is_correct": result.get('is_correct', False),
            "output": result.get('output', ''),
            "error": result.get('error', ''),
            "ai_feedback": result.get('ai_feedback', 'No AI feedback available')
        })
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def get_question_details(request, question_id):
    """Return question details as JSON for the code editor"""
    try:
        student = request.user.student
        question = get_object_or_404(Question, id=question_id)
        
        # Get first test case as example
        test_case = question.test_cases.first()
        
        data = {
            "id": question.id,
            "title": question.title,
            "description": question.description,
            "difficulty": question.difficulty,
            "marks": question.marks,
            "constraints": question.constraints or "No specific constraints",
            "example_input": test_case.input_data if test_case else "",
            "example_output": test_case.expected_output if test_case else ""
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student profile not found"}, status=400)


@login_required
def submit_code(request, question_id):
    if request.method == "POST":
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student profile not found"}, status=400)

        question = get_object_or_404(Question, id=question_id)
        data = json.loads(request.body)
        code = data.get("code")
        lang = data.get("language")

        test_cases_list = [
            {"input": tc.input_data, "expected": tc.expected_output}
            for tc in question.test_cases.all()
        ]

        report = evaluate_submission(code, lang, test_cases_list)

        Submission.objects.create(
            student=student,
            question=question,
            code=code,
            language=lang,
            result=report,
            score=report.get('score', 0)
        )

        return JsonResponse({
            "message": "Submission evaluated!",
            "result": report
        }, safe=False)


# ---------- Faculty Dashboard ----------
@login_required
def faculty_dashboard(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('logout')

    questions = Question.objects.filter(faculty=faculty)
    announcements = Announcement.objects.filter(faculty=faculty)

    return render(request, 'core/faculty_dashboard.html', {
        "faculty": faculty,
        "questions": questions,
        "announcements": announcements
    })


@login_required
def announcements(request):
    try:
        faculty = request.user.faculty
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('logout')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if title and description:
            Announcement.objects.create(
                faculty=faculty,
                title=title,
                description=description
            )
            return redirect("announcements")

    all_announcements = Announcement.objects.filter(faculty=faculty).order_by("-created_at")
    return render(request, "core/announcements.html", {"announcements": all_announcements})


@login_required
def performance_reports(request):
    submissions = Submission.objects.select_related('student__user', 'question').order_by('-submitted_at')
    return render(request, 'core/performance_reports.html', {"submissions": submissions})


@login_required
def download_performance_csv(request):
    submissions = Submission.objects.select_related('student__user', 'question').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="performance_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Question', 'Score', 'Result', 'Submitted At'])
    for sub in submissions:
        writer.writerow([sub.student.user.username, sub.question.title, sub.score, sub.result, sub.submitted_at])

    return response


@login_required
def review_submissions(request):
    submissions = Submission.objects.filter(
        question__faculty=request.user.faculty
    ).select_related('student', 'question').order_by('-submitted_at')

    return render(request, 'core/review_submissions.html', {'submissions': submissions})


@login_required
def upload_questions(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('logout')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        difficulty = request.POST.get("difficulty")

        if title and description and difficulty:
            Question.objects.create(
                title=title,
                description=description,
                difficulty=difficulty,
                faculty=faculty
            )
            return redirect('faculty_dashboard')
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'core/upload_questions.html')
