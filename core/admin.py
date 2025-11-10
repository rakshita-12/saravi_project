from django.contrib import admin
from .models import Faculty, Student, Group, Question, TestCase, Submission, Announcement


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'department']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'faculty', 'group']
    list_filter = ['faculty', 'group']
    search_fields = ['user__username']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'faculty', 'created_at', 'student_count']
    list_filter = ['faculty', 'created_at']
    search_fields = ['name', 'faculty__user__username']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Number of Students'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'faculty', 'difficulty', 'marks', 'created_at']
    list_filter = ['difficulty', 'faculty', 'created_at']
    search_fields = ['title', 'description']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['question', 'input_data', 'expected_output']
    list_filter = ['question']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'question', 'language', 'score', 'submitted_at']
    list_filter = ['language', 'submitted_at', 'student', 'question']
    search_fields = ['student__user__username', 'question__title']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'faculty', 'created_at']
    list_filter = ['faculty', 'created_at']
    search_fields = ['title', 'description']
