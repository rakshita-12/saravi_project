# CodeQuestAI - Online Coding Evaluation Platform

## Overview
CodeQuestAI is a Django-based web application that provides an AI-powered coding evaluation platform. It allows students to practice coding problems and receive automated feedback, while faculty members can create and manage coding questions, test cases, and track student performance.

## Project Structure
- **Django Project**: saravi_project
- **Main App**: core
- **Database**: SQLite (development)
- **Static Files**: Served from core/static/dynamic/
- **Templates**: Located in core/templates/core/

## Key Features
- Student and Faculty authentication systems
- Question management with test cases
- Code submission and evaluation (Python, C++, Java, C)
- AI-powered feedback system (requires Ollama connection)
- Performance tracking and announcements
- Theme toggle (dark/light mode)

## Tech Stack
- Django 5.2.8
- Python 3.11
- SQLite database
- Gunicorn (production server)

## Setup Information
- **Development Server**: Runs on 0.0.0.0:5000
- **Workflow**: django-server configured for automatic startup
- **Deployment**: Configured for Replit autoscale deployment using Gunicorn

## Models
1. **Faculty** - Faculty user profiles with department info
2. **Student** - Student profiles linked to faculty
3. **Question** - Coding problems with difficulty levels and marks
4. **TestCase** - Test cases for each question
5. **Submission** - Student code submissions with results
6. **Announcement** - Faculty announcements

## Environment Configuration
- ALLOWED_HOSTS set to accept all hosts (Replit proxy compatible)
- CSRF_TRUSTED_ORIGINS configured for Replit domains
- X_FRAME_OPTIONS set to ALLOWALL for iframe compatibility

## Recent Changes
- Migrated project to Replit environment (November 8, 2025)
- Configured Django settings for Replit proxy support
- Set up workflow to run on port 5000
- Added deployment configuration with Gunicorn
- Created fresh database migrations
- Added .gitignore for Python/Django
- Populated database with sample data (faculty, students, questions, test cases, announcements)
- Fixed submission code to properly handle test cases and save scores (November 8, 2025)
- Redesigned student dashboard with card-based question grid featuring difficulty badges
- Added score/status badges for submissions in both student and faculty dashboards
- Enhanced UI with gradient badges for Easy/Medium/Hard difficulties and Pass/Partial/Fail statuses
- Implemented complete "Solve Challenge" button functionality (November 8, 2025):
  - Added endpoint to fetch question details as JSON
  - Created interactive flow: Question Card → Language Selection → Code Editor
  - Integrated real-time code submission and evaluation
  - Display live results with scores, test outcomes, and AI feedback
- Fixed AI evaluation and code submission issues (November 8, 2025):
  - AI evaluation now works with graceful degradation (shows warning when Ollama unavailable, but logic checking still works)
  - Fixed code submission by removing duplicate event listeners and correcting URL paths
  - Updated run_student_code view to return proper JSON format
  - Added safe element existence checks to prevent TypeErrors
  - Implemented code editor clearing on logout and when leaving the page
  - Fixed JavaScript scoping issues by moving handlers inside DOMContentLoaded block
- **Enhanced Hugging Face AI Integration** (November 9, 2025):
  - Integrated Hugging Face Inference API using Llama 3.1-8B-Instruct model
  - Added comprehensive logic-based code evaluation beyond simple test case matching
  - Implemented hard-coded solution detection using AI analysis
  - Added separate logic score (0-10) to evaluate algorithm quality and correctness
  - Enhanced AI prompts to detect inefficient algorithms and provide actionable feedback
  - Robust error handling with distinct status codes (success, model_loading, timeout, etc.)
  - Added regex-based parsing for AI responses with float support and validation
  - AI now receives all test cases for better context when detecting hard-coded solutions
  - Evaluation results include: test_case_score, logic_score, hard_coded_detected flag, and detailed AI feedback
  - Added `isAIErrorMessage()` filter to hide error messages from users
  - Updated student dashboard to suppress AI service errors (410, timeout, model loading, etc.)
- **Faculty Dashboard Enhancements** (November 9, 2025):
  - Updated Review Submissions page with expandable test result details
  - Added Logic Score column showing AI-assigned algorithm quality (0-10)
  - Added hard-coded solution warning badges when AI detects suspicious patterns
  - Implemented "View Details" button for each submission with clean test-by-test breakdown
  - Updated Performance Reports page with similar improvements
  - Filtered out AI error messages from faculty views (only shows meaningful feedback)
  - Color-coded test results (green for pass, red for fail) with proper styling

## AI Evaluation System
The platform uses **Hugging Face Inference API** with **Llama 3.1-8B-Instruct** for intelligent code analysis:

### Features
- **Test Case Evaluation**: Traditional output matching (score based on % of passing tests)
- **Logic Score**: AI-assigned score (0-10) evaluating algorithm correctness and quality
- **Hard-coded Detection**: AI identifies solutions that only work for specific test inputs
- **Efficiency Analysis**: Evaluates time/space complexity and suggests improvements
- **Code Quality**: Checks readability, best practices, and code structure

### Configuration
- **Model**: meta-llama/Llama-3.1-8B-Instruct
- **API Key**: Set via `HUGGINGFACE_API_KEY` environment variable (Replit Secrets)
- **Timeout**: 30 seconds per evaluation
- **Graceful Degradation**: Falls back to test-only evaluation if AI unavailable

### Partial Credit Scoring System (NEW)
The platform awards partial marks based on both test results AND logic correctness:

**Scoring Formula:**
- **Combined Score** = 50% Test Cases + 50% Logic Score
  - Test Case Score: 0-100% (percentage of passing tests)
  - Logic Score: 0-10 from AI (converted to 0-100%)
- **Fallback**: If AI unavailable, uses 100% test case score

**Examples:**
- Perfect code: 100% tests + 10/10 logic = **100% final**
- Good logic, some bugs: 40% tests + 8/10 logic = **60% final** ✓ Partial credit!
- All tests pass, poor logic: 100% tests + 4/10 logic = **70% final**
- Wrong approach: 0% tests + 3/10 logic = **15% final**

This ensures students get credit for:
- Correct algorithms with minor bugs
- Right approach but implementation errors
- Demonstrating understanding even when incomplete

### Evaluation Output
Each submission returns:
- `score`: Combined final score (0-100%) using formula above
- `test_case_score`: Raw test pass percentage (0-100%)
- `logic_score`: AI quality score (0-10) or None if AI unavailable
- `hard_coded_detected`: Boolean flag for hard-coded solutions
- `results`: Array with per-test-case feedback, AI analysis, and concerns

## Login Credentials (Test Accounts)

### Main Test Accounts
**Student Login:**
- Username: `student`
- Password: `student123`

**Faculty Login:**
- Username: `faculty`
- Password: `faculty123`

### Additional User Accounts
The following accounts exist but may need password reset:
- alice_wonder (student)
- bob_builder (student)
- charlie_brown (student)
- diana_prince (student)
- prof_smith (faculty)
- prof_johnson (faculty)

## Notes
- Database uses SQLite for development
- Static files are collected in staticfiles/ directory
- AI evaluation enhances traditional testing but doesn't replace it
