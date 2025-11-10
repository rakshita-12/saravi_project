from django.db import models
from django.contrib.auth.models import User


# ----------------------------
# Faculty and Student Profiles
# ----------------------------
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Group(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'faculty']


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.user.username


# ----------------------------
# Questions and Test Cases
# ----------------------------
class Question(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        default='Easy'
    )
    marks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    example_input = models.TextField(blank=True)
    example_output = models.TextField(blank=True)
    constraints = models.TextField(blank=True)


    def __str__(self):
        return self.title


class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"Test case for {self.question.title}"


# ----------------------------
# Submissions
# ----------------------------
class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20)
    result = models.JSONField(null=True, blank=True)  # store output, correctness, AI feedback
    score = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.question.title}"


# ----------------------------
# Announcements
# ----------------------------
class Announcement(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.faculty.user.username}"
