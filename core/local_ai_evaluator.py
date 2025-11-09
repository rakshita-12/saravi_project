import subprocess, tempfile, os, json, requests

# ---------- Hugging Face API Configuration ----------
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

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
def analyze_code_logic(code, language, student_output, expected_output, test_input):
    """
    Intelligent code analysis that evaluates:
    - Algorithm correctness and logic
    - Code efficiency and complexity
    - Hard-coded solutions detection
    - Best practices and code quality
    """
    if not HUGGINGFACE_API_KEY:
        return "✓ Output-based evaluation complete. Enable AI for detailed logic analysis."
    
    # Build comprehensive analysis prompt
    prompt = f"""Analyze this {language} code submission for a coding problem:

CODE:
{code}

TEST CASE:
Input: {test_input}
Expected Output: {expected_output}
Student Output: {student_output}

Evaluate the code on these criteria:
1. **Algorithm Logic**: Is the approach correct? Does it solve the problem properly?
2. **Hard-coding Detection**: Is the solution hard-coded or does it work for all valid inputs?
3. **Code Efficiency**: What's the time/space complexity? Can it be improved?
4. **Code Quality**: Is it readable, well-structured, and following best practices?

Provide a concise analysis (2-3 sentences) focusing on logic correctness and any concerns."""

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
                feedback = result[0].get("generated_text", "").strip()
                return feedback if feedback else "Code logic analysis unavailable."
            return "Code logic analysis unavailable."
        elif response.status_code == 503:
            return "AI model loading. Analysis will be available shortly."
        else:
            return f"Logic evaluation complete (AI service busy)."
            
    except requests.exceptions.Timeout:
        return "Logic evaluation complete (AI timeout)."
    except Exception as e:
        return f"Logic evaluation complete."

# ---------- Evaluate a Submission ----------
def evaluate_submission(code, language, test_cases):
    results = []
    total_tests = len(test_cases)
    passed_tests = 0

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
        feedback = analyze_code_logic(
            code=code,
            language=language,
            student_output=output,
            expected_output=expected_output,
            test_input=input_data
        )

        results.append({
            "input": input_data,
            "expected": expected_output,
            "output": output,
            "error": error,
            "is_correct": is_correct,
            "ai_feedback": feedback
        })

    score = round((passed_tests / total_tests) * 100, 2)
    return {"score": score, "results": results}

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
