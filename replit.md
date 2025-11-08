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

## Notes
- The AI evaluator requires Ollama connection (currently unavailable message appears)
- Database uses SQLite for development
- Static files are collected in staticfiles/ directory
