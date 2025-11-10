import subprocess, tempfile, os, json, requests, re

# ---------- Hugging Face API Configuration ----------
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
# Using Llama 3.1 (released July 2024) - improved performance over 3.0
HUGGINGFACE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HUGGINGFACE_API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"

if HUGGINGFACE_API_KEY:
    print("✓ Hugging Face AI enabled for intelligent code analysis")
else:
    print("⚠ Hugging Face API key not found. AI feedback will be limited.")

# ---------- Language Detection Function ----------
def detect_language_from_code(code):
    """
    Detect the likely programming language from code patterns.
    Returns the detected language or None if uncertain.
    """
    if not code or not code.strip():
        return None
    
    code_clean = code.strip()
    
    # Java detection - very specific patterns
    java_patterns = [
        r'\bpublic\s+class\s+\w+',
        r'\bpublic\s+static\s+void\s+main',
        r'\bSystem\.out\.print',
        r'\bprivate\s+\w+\s+\w+\s*\(',
        r'\bimport\s+java\.',
    ]
    if any(re.search(pattern, code_clean) for pattern in java_patterns):
        return 'java'
    
    # C++ detection - specific to C++
    cpp_patterns = [
        r'#include\s*<iostream>',
        r'\bstd::cout\b',
        r'\bstd::cin\b',
        r'\bstd::string\b',
        r'\busing\s+namespace\s+std',
    ]
    if any(re.search(pattern, code_clean) for pattern in cpp_patterns):
        return 'cpp'
    
    # C detection (must check after C++ since C++ includes C headers)
    c_patterns = [
        r'#include\s*<stdio\.h>',
        r'\bprintf\s*\(',
        r'\bscanf\s*\(',
        r'#include\s*<stdlib\.h>',
        r'#include\s*<string\.h>',
    ]
    if any(re.search(pattern, code_clean) for pattern in c_patterns):
        return 'c'
    
    # Python detection
    python_patterns = [
        r'\bdef\s+\w+\s*\(',
        r'\bimport\s+\w+',
        r'\bfrom\s+\w+\s+import',
        r'\bprint\s*\(',
        r'\bif\s+__name__\s*==\s*["\']__main__["\']',
        r':\s*$',  # Colon at end of line (common in Python)
    ]
    python_score = sum(1 for pattern in python_patterns if re.search(pattern, code_clean, re.MULTILINE))
    
    # If multiple Python patterns match, likely Python
    if python_score >= 2:
        return 'python'
    
    # Check for single Python-specific pattern
    if re.search(r'\bdef\s+\w+\s*\(', code_clean) or re.search(r'\bprint\s*\(', code_clean):
        return 'python'
    
    return None

def validate_language_match(code, selected_language):
    """
    Validate if the submitted code matches the selected language.
    Returns (is_valid, error_message)
    Only flags CLEAR mismatches (e.g., Java syntax in Python selection)
    """
    if not code or not code.strip():
        return True, None  # Empty code will fail anyway
    
    # Normalize selected language
    selected_normalized = selected_language.lower().replace("+", "p").replace(" ", "")
    if selected_normalized == "c++":
        selected_normalized = "cpp"
    
    # Detect the actual language from code
    detected = detect_language_from_code(code)
    
    # If we can't detect with confidence, allow it (benefit of doubt)
    if detected is None:
        return True, None
    
    # Normalize detected language for comparison
    detected_normalized = detected.lower()
    
    # Special case: C and C++ can be similar, don't be too strict
    # Allow C code to run as C++ (C is subset of C++)
    if selected_normalized == "cpp" and detected_normalized == "c":
        return True, None  # C code can compile as C++
    
    # Check if they match
    if detected_normalized != selected_normalized:
        language_names = {
            'python': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C'
        }
        selected_name = language_names.get(selected_normalized, selected_language)
        detected_name = language_names.get(detected_normalized, detected)
        
        error_msg = f"Language mismatch: You selected {selected_name} but submitted {detected_name} code. Please select the correct language or rewrite your code in {selected_name}."
        return False, error_msg
    
    return True, None

# ---------- Run Code Function ----------
def run_code(code, lang, test_input):
    # Normalize language input (handle both "Python" and "python", "C++" and "cpp")
    lang_normalized = lang.lower().replace("+", "p").replace(" ", "")
    
    # Validate that language is supported
    supported_languages = ["python", "java", "cpp", "c", "c++"]
    if lang_normalized not in supported_languages and lang_normalized.replace("+", "p") not in supported_languages:
        return {
            "output": "", 
            "error": f"Unsupported language: {lang}. Supported languages are: Python, Java, C++, C"
        }
    
    # Normalize c++ to cpp
    if lang_normalized == "c++":
        lang_normalized = "cpp"
    
    with tempfile.TemporaryDirectory() as tempdir:
        ext_map = {"python": "py", "java": "java", "cpp": "cpp", "c": "c"}
        ext = ext_map.get(lang_normalized, "txt")
        filepath = os.path.join(tempdir, f"code.{ext}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        compile_cmd = run_cmd = None
        if lang_normalized == "python":
            run_cmd = ["python", filepath]
        elif lang_normalized == "c":
            exe_path = os.path.join(tempdir, "a.exe")
            compile_cmd = ["gcc", filepath, "-o", exe_path]
            run_cmd = [exe_path]
        elif lang_normalized == "cpp":
            exe_path = os.path.join(tempdir, "a.exe")
            compile_cmd = ["g++", filepath, "-o", exe_path]
            run_cmd = [exe_path]
        elif lang_normalized == "java":
            class_name = "Temp"
            filepath = os.path.join(tempdir, f"{class_name}.java")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            compile_cmd = ["javac", filepath]
            run_cmd = ["java", "-cp", tempdir, class_name]
        
        # Additional safety check
        if run_cmd is None:
            return {
                "output": "", 
                "error": f"Internal error: Unable to configure runner for language {lang}"
            }

        # Compile if needed
        if compile_cmd:
            try:
                compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
                if compile_result.returncode != 0:
                    error_details = compile_result.stderr.strip()
                    # Show the actual compiler error to help students debug
                    return {
                        "output": error_details,
                        "error": f"Compilation Error:\n{error_details}"
                    }
            except FileNotFoundError:
                compiler_name = compile_cmd[0]
                lang_name_map = {
                    'javac': 'Java',
                    'g++': 'C++',
                    'gcc': 'C'
                }
                lang_name = lang_name_map.get(compiler_name, lang)
                return {
                    "output": "",
                    "error": f"{lang_name} compiler not installed on this system. Please contact your administrator or use Python for now."
                }

        # Run the code
        try:
            proc = subprocess.run(run_cmd, input=test_input, capture_output=True, text=True, timeout=5)
            output = proc.stdout.strip()
            error = proc.stderr.strip()
        except subprocess.TimeoutExpired:
            output, error = "", "Timeout Error"
        except Exception as e:
            output, error = "", str(e)

        return {"output": output, "error": error}

# ---------- Logic Checker ----------
def evaluate_logic(student_output, expected_output):
    return student_output.strip() == expected_output.strip()

# ---------- LOCAL Fallback Logic Analyzer (NO API REQUIRED) ----------
def local_logic_analyzer(code, language, test_cases):
    """
    Simple heuristic-based logic analyzer that works WITHOUT AI API.
    Awards partial credit based on code structure and complexity.
    
    This ensures students get partial credit even when AI is unavailable!
    """
    if not code or not code.strip():
        return {
            "logic_score": 0.0,
            "feedback": "Empty or blank submission.",
            "status": "local_heuristic"
        }
    
    code_lower = code.lower()
    lines = [line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
    
    score = 0.0
    feedback_parts = []
    
    # Base score for attempting (2 points)
    score += 2.0
    feedback_parts.append("Code submitted")
    
    # Check for basic programming structures (2 points each, max 4)
    structure_score = 0
    if any(kw in code_lower for kw in ['for ', 'while ']):
        structure_score += 2
        feedback_parts.append("uses loops")
    if any(kw in code_lower for kw in ['if ', 'elif ', 'else']):
        structure_score += 2
        feedback_parts.append("uses conditionals")
    score += min(structure_score, 4)
    
    # Check for appropriate complexity (2 points)
    if len(lines) >= 3:
        score += 2
        feedback_parts.append("adequate length")
    elif len(lines) >= 1:
        score += 1
    
    # Check for input/output operations (1 point)
    if any(kw in code_lower for kw in ['input(', 'print(', 'cout', 'cin', 'scanner', 'system.out']):
        score += 1
        feedback_parts.append("handles I/O")
    
    # Check for data structures (1 point)
    if any(kw in code_lower for kw in ['list', 'array', 'dict', 'set', 'vector', 'arraylist', '[]', '{}']):
        score += 1
        feedback_parts.append("uses data structures")
    
    # Cap at 10
    score = min(score, 10.0)
    
    feedback = f"LOGIC_SCORE: {score}/10 (Local Heuristic). Code {', '.join(feedback_parts)}. Enable AI for detailed analysis."
    
    return {
        "logic_score": round(score, 1),
        "feedback": feedback,
        "status": "local_heuristic"
    }

# ---------- AI Code Approach Analyzer (UPFRONT EVALUATION) ----------
def analyze_code_approach(code, language, question_description, test_cases):
    """
    UPFRONT code analysis that evaluates algorithm and approach BEFORE running tests.
    This awards partial credit even for code with syntax errors or bugs.
    
    Evaluates:
    - Algorithm choice and correctness
    - Problem understanding
    - Logical approach
    - Code structure and readability
    """
    if not HUGGINGFACE_API_KEY:
        # Use local heuristic fallback when AI unavailable
        return local_logic_analyzer(code, language, test_cases)
    
    # Build test cases context
    test_context = "\nTEST CASES:\n"
    for i, tc in enumerate(test_cases[:3], 1):
        test_context += f"  {i}. Input: {tc['input']} → Expected: {tc['expected']}\n"
    
    prompt = f"""You are a programming instructor grading student code. Your job is to award PARTIAL CREDIT based on the ALGORITHM and APPROACH, regardless of syntax errors or bugs.

STUDENT CODE ({language}):
```{language}
{code}
```

PROBLEM CONTEXT:
{test_context}

GRADING PHILOSOPHY (AWARD GENEROUS PARTIAL CREDIT):
- **10/10**: Perfect algorithm, correct approach, clean code
- **8-9/10**: Correct algorithm with minor bugs or syntax errors
- **6-7/10**: Right approach but significant implementation issues
- **4-5/10**: Demonstrates understanding, partially correct logic
- **2-3/10**: Wrong approach but shows some problem understanding
- **0-1/10**: No understanding or blank/nonsense code

CRITICAL: Even if the code has SYNTAX ERRORS, award 6-9/10 if the algorithm and logic are correct!

EVALUATION CRITERIA:
1. **Algorithm Choice**: Did they choose an appropriate algorithm? (loops, conditionals, data structures)
2. **Problem Understanding**: Do they understand what the problem asks?
3. **Logic Flow**: Is the logical approach sound, even if buggy?
4. **Code Structure**: Is the code organized well?

SPECIAL CASES:
- Syntax errors but correct algorithm → 7-9/10
- Working code but hard-coded values → 2-4/10 + state "HARD-CODED"
- Off-by-one errors with correct logic → 7-8/10
- Wrong output but right approach → 6-8/10

RESPONSE FORMAT:
Start with "LOGIC_SCORE: X/10" where X is 0-10
Then provide 2-3 sentences explaining your score, focusing on what they got RIGHT.

Example: "LOGIC_SCORE: 8/10. The student correctly implemented a two-pointer approach which is optimal for this problem. There's a syntax error (missing colon) but the algorithm logic is sound. Once the syntax is fixed, this will work perfectly."
"""

    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                feedback_text = result[0].get("generated_text", "").strip()
                
                logic_score = None
                concerns = []
                
                if feedback_text:
                    # Extract logic score
                    score_match = re.search(r'LOGIC[_\s]*SCORE[:\s]*([0-9]+(?:\.[0-9]+)?)\s*/\s*10', feedback_text, re.IGNORECASE)
                    if score_match:
                        try:
                            score_value = float(score_match.group(1))
                            logic_score = max(0, min(10, round(score_value, 1)))
                        except (ValueError, IndexError):
                            logic_score = None
                    
                    # Detect hard-coding
                    feedback_lower = feedback_text.lower()
                    if any(kw in feedback_lower for kw in ['hard-coded', 'hardcoded', 'hard coded']):
                        concerns.append("hard_coded")
                    
                    return {
                        "feedback": feedback_text,
                        "logic_score": logic_score,
                        "concerns": concerns,
                        "status": "success"
                    }
                    
            return {
                "feedback": "AI returned empty response",
                "logic_score": None,
                "concerns": [],
                "status": "empty_response"
            }
        elif response.status_code == 503:
            # Model loading - use local fallback
            return local_logic_analyzer(code, language, test_cases)
        else:
            # Any other error - use local fallback
            return local_logic_analyzer(code, language, test_cases)
            
    except requests.exceptions.Timeout:
        # Timeout - use local fallback
        return local_logic_analyzer(code, language, test_cases)
    except Exception as e:
        # Any exception - use local fallback
        return local_logic_analyzer(code, language, test_cases)

# ---------- Evaluate a Submission ----------
def evaluate_submission(code, language, test_cases):
    """
    NEW APPROACH: Analyze code logic FIRST, then run tests
    This ensures partial credit even for code with syntax errors
    """
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    # STEP 0: Validate language match FIRST
    is_valid, error_message = validate_language_match(code, language)
    if not is_valid:
        # Language mismatch - return error with NO score
        for case in test_cases:
            results.append({
                "input": case["input"],
                "expected": case["expected"],
                "output": "",
                "error": error_message,
                "is_correct": False,
                "ai_feedback": error_message if not results else "",
                "logic_score": None,
                "concerns": ["language_mismatch"],
                "status": "language_mismatch"
            })
        
        return {
            "score": 0,
            "test_case_score": 0,
            "logic_score": None,
            "hard_coded_detected": False,
            "results": results
        }
    
    # STEP 1: Analyze code approach UPFRONT (before running anything)
    # This awards partial credit for correct algorithm even with syntax errors!
    upfront_analysis = analyze_code_approach(
        code=code,
        language=language,
        question_description="",
        test_cases=test_cases
    )
    
    overall_logic_score = upfront_analysis.get("logic_score")
    overall_feedback = upfront_analysis.get("feedback", "")
    has_hard_coded = "hard_coded" in upfront_analysis.get("concerns", [])
    
    # STEP 2: Run test cases
    for case in test_cases:
        input_data = case["input"]
        expected_output = case["expected"]

        run_result = run_code(code, language, input_data)
        output = run_result["output"]
        error = run_result.get("error", "")

        # Check if test passed
        is_correct = evaluate_logic(output, expected_output) if not error else False
        if is_correct:
            passed_tests += 1

        results.append({
            "input": input_data,
            "expected": expected_output,
            "output": output,
            "error": error,
            "is_correct": is_correct,
            "ai_feedback": overall_feedback if results == [] else "",  # Show feedback on first test only
            "logic_score": overall_logic_score if results == [] else None,
            "concerns": upfront_analysis.get("concerns", []) if results == [] else [],
            "status": upfront_analysis.get("status", "unknown")
        })

    # Calculate test case score (0-100%)
    test_case_score = round((passed_tests / total_tests) * 100, 2)
    
    # Calculate combined score for partial credit
    # 50% weight on test cases, 50% weight on logic correctness
    combined_score = test_case_score
    if overall_logic_score is not None:
        logic_percentage = overall_logic_score * 10
        combined_score = round((test_case_score * 0.5) + (logic_percentage * 0.5), 2)
    
    return {
        "score": combined_score,
        "test_case_score": test_case_score,
        "logic_score": overall_logic_score,
        "hard_coded_detected": has_hard_coded,
        "results": results
    }


# ---------- Example Execution ----------
if __name__ == "__main__":
    code = """n = int(input())\nprint(n*2)"""
    lang = "python"
    tests = [
        {"input": "2\n", "expected": "4"},
        {"input": "5\n", "expected": "10"}
    ]

    report = evaluate_submission(code, lang, tests)
    print(json.dumps(report, indent=2))
