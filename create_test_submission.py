import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saravi_project.settings')
django.setup()

from core.models import Student, Question, Submission

# Get a student and a question
student = Student.objects.first()
question = Question.objects.first()

# Create a test submission
if student and question:
    Submission.objects.create(
        student=student,
        question=question,
        code='def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]',
        language='Python',
        result={'score': 100, 'results': [{'is_correct': True}]},
        score=100.0
    )
    print(f"Created submission for {student.user.username} on {question.title}")
    
    # Create another with partial score
    question2 = Question.objects.all()[1]
    Submission.objects.create(
        student=student,
        question=question2,
        code='def reverse_string(s):\n    return s',
        language='Python',
        result={'score': 33.33, 'results': [{'is_correct': False}]},
        score=33.33
    )
    print(f"Created submission for {student.user.username} on {question2.title}")
    
    # Create one more from different student
    student2 = Student.objects.all()[1]
    Submission.objects.create(
        student=student2,
        question=question,
        code='def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i',
        language='Python',
        result={'score': 100, 'results': [{'is_correct': True}]},
        score=100.0
    )
    print(f"Created submission for {student2.user.username} on {question.title}")
else:
    print("No student or question found")

print("\nTest submissions created successfully!")
