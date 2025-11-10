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
2. **Group** - Faculty-created groups for organizing students
3. **Student** - Student profiles linked to faculty and optionally to a group
4. **Question** - Coding problems with difficulty levels and marks
5. **TestCase** - Test cases for each question
6. **Submission** - Student code submissions with results
7. **Announcement** - Faculty announcements

## Environment Configuration
- ALLOWED_HOSTS set to accept all hosts (Replit proxy compatible)
- CSRF_TRUSTED_ORIGINS configured for Replit domains
- X_FRAME_OPTIONS set to ALLOWALL for iframe compatibility

## Recent Changes
- **Group Management & Student Assignment** (November 10, 2025):
  - Implemented complete group management system for faculty
  - Added Group model with faculty ownership and unique constraint
  - Faculty can create groups from dashboard with real-time UI updates
  - Added student assignment interface to assign students to groups
  - Backend views with proper security: faculty can only manage their own groups/students
  - Student-to-group assignment with dropdown selection and live refresh
  - Groups display shows student count and member list
  - Data migration properly preserved existing student group data
  - Admin interface registered for Group model with student count display
  - All endpoints secured with @login_required and faculty ownership validation
  - CSRF protection implemented in all AJAX requests
  - Input validation for group names (max 100 characters, required field)
- **Java Class Name Fix** (November 10, 2025):
  - Fixed Java compilation to automatically detect and use the correct class name
  - System now extracts class name from code (e.g., `public class TwoSum` → saves as `TwoSum.java`)
  - Resolves "class X is public, should be declared in a file named X.java" errors
  - Works with both public and package-private classes
- **Improved Error Messages** (November 10, 2025):
  - Compilation errors now show detailed compiler output
  - Students can see exact line numbers, error types, and helpful messages
  - Better debugging experience for Java, C++, and C code
- **Compiler Installation** (November 10, 2025):
  - Installed Java compiler (GraalVM 22.3 with javac)
  - Installed C++ compiler (Clang 14 with g++/clang++)
  - All languages (Python, Java, C++, C) now fully supported
- **Language Mismatch Validation** (November 10, 2025):
  - Implemented automatic language detection for submitted code
  - When code language doesn't match the selected language, shows clear error message
  - No score or feedback given for language mismatches
  - Frontend displays "N/A" for all scores and shows warning message
  - Prevents gaming the system by submitting code in wrong language
  - Supports Python, Java, C++, and C with intelligent pattern matching
  - Automatically filters out language mismatch errors from AI feedback display
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
- **Local Heuristic Fallback System** (November 9, 2025):
  - Implemented code structure analyzer that works WITHOUT AI API
  - Analyzes code BEFORE running tests to detect algorithmic approach
  - Awards logic score (0-10) based on structural patterns: loops, conditionals, I/O, data structures
  - Enables partial credit even for syntax errors that prevent code execution
  - Verified: Code with syntax error receives 45% score (0% tests + 9/10 logic)
  - System automatically switches between AI and local heuristic based on API availability

## AI Evaluation System
The platform uses **dual-track evaluation** with both AI and local heuristic analysis:

### Evaluation Methods
1. **AI Analysis** (Hugging Face Llama 3.1-8B-Instruct) - When API key available:
   - Evaluates algorithmic approach and code quality
   - Detects hard-coded solutions and inefficient algorithms
   - Provides detailed feedback on improvements
   
2. **Local Heuristic Fallback** (No API key needed):
   - Analyzes code structure (loops, conditionals, I/O, data structures)
   - Awards logic score (0-10) based on structural patterns
   - **Works even with syntax errors** - evaluates code before running tests
   - Ensures partial credit WITHOUT requiring external API

### Partial Credit Scoring System
The platform awards partial marks based on both test results AND logic correctness:

**Scoring Formula:**
- **Combined Score** = 50% Test Cases + 50% Logic Score
  - Test Case Score: 0-100% (percentage of passing tests)
  - Logic Score: 0-10 (from AI or local heuristic, converted to 0-100%)

**Local Heuristic Scoring (when AI unavailable):**
- Base attempt: +2 points
- Has loops: +2 points
- Has conditionals: +2 points
- Adequate length (3+ lines): +2 points
- Handles I/O: +1 point
- Uses data structures: +1 point
- **Maximum: 10/10 points**

**Examples:**
- Perfect code: 100% tests + 10/10 logic = **100% final**
- Syntax error, good approach: 0% tests + 9/10 logic = **45% final** ✓ Partial credit!
- Good logic, some bugs: 40% tests + 8/10 logic = **60% final** ✓ Partial credit!
- All tests pass, poor logic: 100% tests + 4/10 logic = **70% final**
- Wrong approach: 0% tests + 3/10 logic = **15% final**

**Key Achievement:**
Students get credit for correct algorithmic approach even when code has syntax errors or bugs!

### Configuration
- **AI Model** (optional): meta-llama/Llama-3.1-8B-Instruct
- **API Key** (optional): Set via `HUGGINGFACE_API_KEY` in Replit Secrets
- **Timeout**: 30 seconds for AI analysis
- **Fallback**: Automatic switch to local heuristic if AI unavailable

### Language Validation
Before evaluating code, the system validates that the submitted code language matches the selected language:
- **Automatic Detection**: Uses pattern matching to detect Python, Java, C++, and C code
- **Language Mismatch Handling**: 
  - Returns score of 0 with no AI feedback
  - Displays clear error message explaining the mismatch
  - Shows "N/A" for all score fields in the UI
  - Prevents evaluation when code language doesn't match selection
- **Smart Detection**: Uses specific syntax patterns (e.g., `System.out.println` for Java, `def` for Python)
- **Special Cases**: C code is allowed when C++ is selected (C is subset of C++)

### Evaluation Output
Each submission returns:
- `score`: Combined final score (0-100%) using formula above
- `test_case_score`: Raw test pass percentage (0-100%)
- `logic_score`: AI quality score (0-10) or None if AI unavailable
- `hard_coded_detected`: Boolean flag for hard-coded solutions
- `results`: Array with per-test-case feedback, AI analysis, and concerns
- `status`: "language_mismatch" when code language doesn't match selection

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
