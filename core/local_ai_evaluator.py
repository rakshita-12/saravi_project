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
            compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if compile_result.returncode != 0:
                return {"output": compile_result.stderr.strip(), "error": "Compilation Error"}

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

# ---------- AI Code Logic Analyzer Using Hugging Face ----------
def analyze_code_logic(code, language, student_output, expected_output, test_input, all_test_cases=None):
    """
    Intelligent code analysis that evaluates:
    - Algorithm correctness and logic
    - Code efficiency and complexity
    - Hard-coded solutions detection
    - Best practices and code quality
    """
    if not HUGGINGFACE_API_KEY:
        return {
            "feedback": "✓ Output-based evaluation complete. Enable AI for detailed logic analysis.",
            "logic_score": None,
            "concerns": [],
            "status": "no_api_key"
        }
    
    # Build comprehensive analysis prompt with multiple test cases context
    test_context = ""
    if all_test_cases and len(all_test_cases) > 1:
        test_context = f"\nALL TEST CASES (for context):\n"
        for i, tc in enumerate(all_test_cases[:3], 1):  # Show up to 3 test cases
            test_context += f"Test {i}: Input='{tc['input']}' → Expected='{tc['expected']}'\n"
    
    prompt = f"""You are a code evaluation expert. Your job is to award PARTIAL CREDIT based on logic correctness, not just test case results.

CODE:
```{language}
{code}
```

CURRENT TEST CASE:
Input: {test_input}
Expected Output: {expected_output}
Student Output: {student_output}
{test_context}

SCORING PHILOSOPHY - AWARD PARTIAL CREDIT FOR:
- **Correct approach** even with minor bugs (7-8/10)
- **Right algorithm** but implementation errors (6-7/10)  
- **Logical steps toward solution** even if incomplete (4-6/10)
- **Understanding the problem** but wrong approach (2-4/10)
- **No understanding** or completely wrong (0-2/10)

EVALUATION CRITERIA:
1. **Algorithm Logic**: Does the student understand the problem? Is their approach sound? Give credit for correct logical steps even if execution fails.
2. **Partial Correctness**: If the output is wrong, did they get close? Did they demonstrate understanding of key concepts?
3. **Hard-coding Detection**: Only penalize if they're cheating with hard-coded values. Don't penalize for using constants appropriately.
4. **Code Quality**: Readable code shows understanding - factor this into the score.

IMPORTANT: Even if test cases fail, award 5-8/10 if the logic and approach are fundamentally correct.

RESPONSE FORMAT:
Start with "LOGIC_SCORE: X/10" where X is 0-10, then explain:
- What logical steps they got RIGHT (be generous)
- Where they went wrong (if applicable)
- If hard-coded: state "HARD-CODED SOLUTION DETECTED"

Example 1: "LOGIC_SCORE: 7/10. The student correctly identified this as a sorting problem and attempted bubble sort. Logic is sound but has an off-by-one error in the loop. The approach is right, just needs debugging."

Example 2: "LOGIC_SCORE: 9/10. Perfect implementation of binary search with correct edge case handling. Code is clean and efficient."
"""

    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
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
                
                # Parse logic score from response using robust regex
                logic_score = None
                concerns = []
                
                if feedback_text:
                    # Extract logic score with regex (handles int, float, variations)
                    score_match = re.search(r'LOGIC[_\s]*SCORE[:\s]*([0-9]+(?:\.[0-9]+)?)\s*/\s*10', feedback_text, re.IGNORECASE)
                    if score_match:
                        try:
                            score_value = float(score_match.group(1))
                            # Clamp between 0-10 and round to 1 decimal
                            logic_score = max(0, min(10, round(score_value, 1)))
                        except (ValueError, IndexError):
                            logic_score = None
                    
                    # Detect concerns with normalized lowercase matching
                    feedback_lower = feedback_text.lower()
                    
                    # Hard-coded detection (multiple keywords)
                    hard_coded_keywords = ['hard-coded', 'hardcoded', 'hard coded', 'directly return', 'directly print']
                    if any(keyword in feedback_lower for keyword in hard_coded_keywords):
                        concerns.append("hard_coded")
                    
                    # Efficiency concerns
                    efficiency_keywords = ['inefficient', 'can be improved', 'optimize', 'better complexity']
                    if any(keyword in feedback_lower for keyword in efficiency_keywords):
                        concerns.append("efficiency")
                    
                    return {
                        "feedback": feedback_text,
                        "logic_score": logic_score,
                        "concerns": concerns,
                        "status": "success"
                    }
                    
            return {
                "feedback": "AI analysis returned empty response.",
                "logic_score": None,
                "concerns": [],
                "status": "empty_response"
            }
        elif response.status_code == 503:
            return {
                "feedback": "AI model loading. Try again in a moment.",
                "logic_score": None,
                "concerns": [],
                "status": "model_loading"
            }
        elif response.status_code >= 400 and response.status_code < 500:
            return {
                "feedback": f"AI service error (client): {response.status_code}",
                "logic_score": None,
                "concerns": [],
                "status": f"client_error_{response.status_code}"
            }
        else:
            return {
                "feedback": f"AI service unavailable (status {response.status_code})",
                "logic_score": None,
                "concerns": [],
                "status": f"server_error_{response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "feedback": "AI analysis timed out after 30 seconds.",
            "logic_score": None,
            "concerns": [],
            "status": "timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "feedback": f"Network error during AI analysis: {type(e).__name__}",
            "logic_score": None,
            "concerns": [],
            "status": "network_error"
        }
    except Exception as e:
        return {
            "feedback": f"Unexpected error during AI analysis: {type(e).__name__}",
            "logic_score": None,
            "concerns": [],
            "status": "unexpected_error"
        }

# ---------- Evaluate a Submission ----------
def evaluate_submission(code, language, test_cases):
    results = []
    total_tests = len(test_cases)
    passed_tests = 0

    # Collect all logic scores and concerns
    all_logic_scores = []
    has_hard_coded = False
    
    for case in test_cases:
        input_data = case["input"]
        expected_output = case["expected"]

        run_result = run_code(code, language, input_data)
        output = run_result["output"]
        error = run_result.get("error", "")

        # Check logic (output matching)
        is_correct = evaluate_logic(output, expected_output)
        if is_correct:
            passed_tests += 1

        # Intelligent AI Code Analysis (evaluates logic, not just output)
        ai_analysis = analyze_code_logic(
            code=code,
            language=language,
            student_output=output,
            expected_output=expected_output,
            test_input=input_data,
            all_test_cases=test_cases
        )
        
        # Track logic scores and concerns (only if AI analysis succeeded)
        if ai_analysis.get("status") == "success":
            if ai_analysis.get("logic_score") is not None:
                all_logic_scores.append(ai_analysis["logic_score"])
            if "hard_coded" in ai_analysis.get("concerns", []):
                has_hard_coded = True

        results.append({
            "input": input_data,
            "expected": expected_output,
            "output": output,
            "error": error,
            "is_correct": is_correct,
            "ai_feedback": ai_analysis.get("feedback", ""),
            "logic_score": ai_analysis.get("logic_score"),
            "concerns": ai_analysis.get("concerns", []),
            "status": ai_analysis.get("status", "unknown")
        })

    # Calculate test case score (0-100%)
    test_case_score = round((passed_tests / total_tests) * 100, 2)
    
    # Calculate average logic score from AI (0-10)
    avg_logic_score = None
    if all_logic_scores:
        avg_logic_score = round(sum(all_logic_scores) / len(all_logic_scores), 1)
    
    # Calculate combined score for partial credit
    # 50% weight on test cases, 50% weight on logic correctness
    combined_score = test_case_score
    if avg_logic_score is not None:
        logic_percentage = avg_logic_score * 10
        combined_score = round((test_case_score * 0.5) + (logic_percentage * 0.5), 2)
    
    return {
        "score": combined_score,
        "test_case_score": test_case_score,
        "logic_score": avg_logic_score,
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
