import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saravi_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Faculty, Student, Question, TestCase, Announcement

print("Starting data population...")

# Create Faculty Users
faculty_data = [
    {'username': 'prof_smith', 'email': 'smith@university.edu', 'password': 'faculty123', 'first_name': 'John', 'last_name': 'Smith', 'department': 'Computer Science'},
    {'username': 'prof_johnson', 'email': 'johnson@university.edu', 'password': 'faculty123', 'first_name': 'Emily', 'last_name': 'Johnson', 'department': 'Software Engineering'},
]

faculties = []
for f_data in faculty_data:
    user, created = User.objects.get_or_create(
        username=f_data['username'],
        defaults={
            'email': f_data['email'],
            'first_name': f_data['first_name'],
            'last_name': f_data['last_name']
        }
    )
    if created:
        user.set_password(f_data['password'])
        user.save()
        print(f"Created faculty user: {user.username}")
    
    faculty, created = Faculty.objects.get_or_create(
        user=user,
        defaults={'department': f_data['department']}
    )
    faculties.append(faculty)
    if created:
        print(f"Created faculty profile: {faculty}")

# Create Student Users
student_data = [
    {'username': 'alice_wonder', 'email': 'alice@student.edu', 'password': 'student123', 'first_name': 'Alice', 'last_name': 'Wonder', 'group': 'Group A'},
    {'username': 'bob_builder', 'email': 'bob@student.edu', 'password': 'student123', 'first_name': 'Bob', 'last_name': 'Builder', 'group': 'Group A'},
    {'username': 'charlie_brown', 'email': 'charlie@student.edu', 'password': 'student123', 'first_name': 'Charlie', 'last_name': 'Brown', 'group': 'Group B'},
    {'username': 'diana_prince', 'email': 'diana@student.edu', 'password': 'student123', 'first_name': 'Diana', 'last_name': 'Prince', 'group': 'Group B'},
]

students = []
for s_data in student_data:
    user, created = User.objects.get_or_create(
        username=s_data['username'],
        defaults={
            'email': s_data['email'],
            'first_name': s_data['first_name'],
            'last_name': s_data['last_name']
        }
    )
    if created:
        user.set_password(s_data['password'])
        user.save()
        print(f"Created student user: {user.username}")
    
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'faculty': faculties[0],
            'group': s_data['group']
        }
    )
    students.append(student)
    if created:
        print(f"Created student profile: {student}")

# Create Questions with Test Cases
questions_data = [
    {
        'title': 'Two Sum',
        'description': 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.',
        'difficulty': 'Easy',
        'marks': 10,
        'example_input': 'nums = [2,7,11,15], target = 9',
        'example_output': '[0,1]',
        'constraints': '2 <= nums.length <= 104\n-109 <= nums[i] <= 109\n-109 <= target <= 109',
        'test_cases': [
            {'input': '2 7 11 15\n9', 'expected': '0 1'},
            {'input': '3 2 4\n6', 'expected': '1 2'},
            {'input': '3 3\n6', 'expected': '0 1'}
        ]
    },
    {
        'title': 'Reverse String',
        'description': 'Write a function that reverses a string. The input string is given as an array of characters.',
        'difficulty': 'Easy',
        'marks': 10,
        'example_input': 'hello',
        'example_output': 'olleh',
        'constraints': '1 <= s.length <= 105\ns[i] is a printable ascii character',
        'test_cases': [
            {'input': 'hello', 'expected': 'olleh'},
            {'input': 'world', 'expected': 'dlrow'},
            {'input': 'Python', 'expected': 'nohtyP'}
        ]
    },
    {
        'title': 'Fibonacci Number',
        'description': 'Calculate the nth Fibonacci number. The Fibonacci sequence is defined as F(0) = 0, F(1) = 1, and F(n) = F(n-1) + F(n-2) for n > 1.',
        'difficulty': 'Medium',
        'marks': 15,
        'example_input': '10',
        'example_output': '55',
        'constraints': '0 <= n <= 30',
        'test_cases': [
            {'input': '0', 'expected': '0'},
            {'input': '1', 'expected': '1'},
            {'input': '5', 'expected': '5'},
            {'input': '10', 'expected': '55'}
        ]
    },
    {
        'title': 'Palindrome Check',
        'description': 'Given a string, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.',
        'difficulty': 'Easy',
        'marks': 10,
        'example_input': 'A man, a plan, a canal: Panama',
        'example_output': 'true',
        'constraints': '1 <= s.length <= 2 * 105\ns consists only of printable ASCII characters',
        'test_cases': [
            {'input': 'racecar', 'expected': 'true'},
            {'input': 'hello', 'expected': 'false'},
            {'input': 'A man, a plan, a canal: Panama', 'expected': 'true'}
        ]
    },
    {
        'title': 'Maximum Subarray',
        'description': 'Given an integer array nums, find the contiguous subarray with the largest sum, and return its sum.',
        'difficulty': 'Hard',
        'marks': 20,
        'example_input': '[-2,1,-3,4,-1,2,1,-5,4]',
        'example_output': '6',
        'constraints': '1 <= nums.length <= 105\n-104 <= nums[i] <= 104',
        'test_cases': [
            {'input': '-2 1 -3 4 -1 2 1 -5 4', 'expected': '6'},
            {'input': '5 4 -1 7 8', 'expected': '23'},
            {'input': '1', 'expected': '1'}
        ]
    }
]

for q_data in questions_data:
    question, created = Question.objects.get_or_create(
        faculty=faculties[0],
        title=q_data['title'],
        defaults={
            'description': q_data['description'],
            'difficulty': q_data['difficulty'],
            'marks': q_data['marks'],
            'example_input': q_data['example_input'],
            'example_output': q_data['example_output'],
            'constraints': q_data['constraints']
        }
    )
    if created:
        print(f"Created question: {question.title}")
        
        # Create test cases for this question
        for tc_data in q_data['test_cases']:
            test_case = TestCase.objects.create(
                question=question,
                input_data=tc_data['input'],
                expected_output=tc_data['expected']
            )
            print(f"  Added test case for {question.title}")

# Create Announcements
announcements_data = [
    {
        'title': 'Welcome to CodeQuestAI!',
        'description': 'Welcome to the new semester! This platform will help you learn coding with AI-powered feedback. Practice regularly and don\'t hesitate to ask questions.'
    },
    {
        'title': 'New Assignment Posted',
        'description': 'A new set of coding problems has been posted. Please complete them by the end of this week. Focus on Two Sum and Reverse String first.'
    },
    {
        'title': 'Office Hours This Week',
        'description': 'I will be available for office hours on Wednesday from 2-4 PM and Friday from 10-12 PM. Feel free to drop by if you need help with any problems.'
    }
]

for a_data in announcements_data:
    announcement, created = Announcement.objects.get_or_create(
        faculty=faculties[0],
        title=a_data['title'],
        defaults={'description': a_data['description']}
    )
    if created:
        print(f"Created announcement: {announcement.title}")

print("\n" + "="*50)
print("Data population complete!")
print("="*50)
print("\nLogin credentials:")
print("\nFaculty:")
print("  Username: prof_smith, Password: faculty123")
print("  Username: prof_johnson, Password: faculty123")
print("\nStudents:")
print("  Username: alice_wonder, Password: student123")
print("  Username: bob_builder, Password: student123")
print("  Username: charlie_brown, Password: student123")
print("  Username: diana_prince, Password: student123")
print("="*50)
