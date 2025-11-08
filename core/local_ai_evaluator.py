import subprocess, tempfile, os, json, requests

# ---------- Detect Ollama Host ----------
def get_ollama_url():
    """Detect whether Ollama is running locally or inside Docker network."""
    urls = ["http://ollama:11434/api/generate", "http://localhost:11434/api/generate"]
    for url in urls:
        try:
            r = requests.get(url.replace("/api/generate", "/api/tags"), timeout=2)
            if r.status_code == 200:
                print(f" Ollama detected at: {url}")
                return url
        except requests.exceptions.RequestException:
            continue
    print("Could not connect to Ollama. AI feedback will be unavailable.")
    return None

OLLAMA_API_URL = get_ollama_url()

# ---------- Run Code Function ----------
def run_code(code, lang, test_input):
    with tempfile.TemporaryDirectory() as tempdir:
        ext_map = {"python": "py", "java": "java", "cpp": "cpp", "c": "c"}
        ext = ext_map.get(lang.lower(), "txt")
        filepath = os.path.join(tempdir, f"code.{ext}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        compile_cmd = run_cmd = None
        if lang.lower() == "python":
            run_cmd = ["python", filepath]
        elif lang.lower() == "c":
            exe_path = os.path.join(tempdir, "a.exe")
            compile_cmd = ["gcc", filepath, "-o", exe_path]
            run_cmd = [exe_path]
        elif lang.lower() == "cpp":
            exe_path = os.path.join(tempdir, "a.exe")
            compile_cmd = ["g++", filepath, "-o", exe_path]
            run_cmd = [exe_path]
        elif lang.lower() == "java":
            class_name = "Temp"
            filepath = os.path.join(tempdir, f"{class_name}.java")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            compile_cmd = ["javac", filepath]
            run_cmd = ["java", "-cp", tempdir, class_name]

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

# ---------- AI Feedback Using Ollama ----------
def ai_feedback_ollama(code, student_output, expected_output):
    if not OLLAMA_API_URL:
        return "⚠️ Ollama is not running — no AI feedback available."

    prompt = f"""
You are a code evaluator. Analyze the student's code and output.

Code:
{code}

Student Output: {student_output}
Expected Output: {expected_output}

Please respond with:
- Logic score (1–5)
- Short explanation of correctness
- Suggested improvements if any.
"""
    try:
        res = requests.post(OLLAMA_API_URL, json={"model": "llama3", "prompt": prompt}, timeout=40)
        if res.status_code == 200:
            data = res.text.splitlines()
            response_text = ""
            for line in data:
                try:
                    j = json.loads(line)
                    if "response" in j:
                        response_text += j["response"]
                except:
                    continue
            return response_text.strip() or "(No response received)"
        else:
            return f"Ollama error: {res.text}"
    except Exception as e:
        return f"Ollama connection error: {e}"

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

        # Check logic
        is_correct = evaluate_logic(output, expected_output)
        if is_correct:
            passed_tests += 1

        # AI Feedback
        feedback = ai_feedback_ollama(code, output, expected_output)

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
