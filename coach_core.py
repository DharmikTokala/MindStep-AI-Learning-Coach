import json
import os
import re
import time
from dataclasses import dataclass, field

import sympy as sp

from dotenv import load_dotenv
from google import genai

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)


# =========================================================
# ENVIRONMENT + GEMINI
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in your .env file."
    )


client = genai.Client(
    api_key=api_key
)

MODEL_NAME = "gemini-3.5-flash-lite"


# =========================================================
# MISCONCEPTION CATEGORIES
# =========================================================

MISCONCEPTION_CATEGORIES = [
    "sign_error",
    "factorization_error",
    "distribution_error",
    "equation_balancing_error",
    "fraction_error",
    "arithmetic_error",
    "exponent_rule_error",
    "algebraic_manipulation_error",

    "formula_selection_error",
    "conceptual_misunderstanding",
    "domain_restriction_error",
    "theorem_application_error",

    "trigonometry_error",
    "logarithm_error",
    "function_error",
    "limit_error",
    "derivative_error",
    "integration_error",
    "coordinate_geometry_error",
    "sequence_series_error",
    "matrix_error",
    "probability_error",
    "permutation_combination_error",

    "no_clear_error"
]


# =========================================================
# RESULT OBJECTS
# =========================================================

@dataclass
class CoachResult:

    student_is_correct: bool
    topic: str
    misconception_category: str
    confidence: float
    first_wrong_step: str
    diagnosis: str
    hint_1: str
    hint_2: str
    hint_3: str
    full_explanation: str

    subtopic: str = ""
    difficulty: str = ""
    symbolic_verification: str = ""

    step_analysis: list = field(
        default_factory=list
    )

    teaching_block: dict = field(
        default_factory=dict
    )


@dataclass
class StartHelpResult:

    topic: str
    subtopic: str
    difficulty: str

    concept: str
    recognition: str

    hint_1: str
    hint_1_math: str

    hint_2: str
    hint_2_math: str

    hint_3: str
    hint_3_math: str

    student_task: str


# =========================================================
# GEMINI OUTPUT SCHEMA — NORMAL COACH
# =========================================================

analysis_schema = {

    "type": "object",

    "properties": {

        "student_is_correct": {
            "type": "boolean"
        },

        "topic": {
            "type": "string"
        },

        "subtopic": {
            "type": "string"
        },

        "difficulty": {
            "type": "string"
        },

        "misconception_category": {
            "type": "string",
            "enum": MISCONCEPTION_CATEGORIES
        },

        "confidence": {
            "type": "number"
        },

        "first_wrong_step": {
            "type": "string"
        },

        "diagnosis": {
            "type": "string"
        },

        "hint_1": {
            "type": "string"
        },

        "hint_2": {
            "type": "string"
        },

        "hint_3": {
            "type": "string"
        },

        "full_explanation": {
            "type": "string"
        },

        "symbolic_verification": {
            "type": "string"
        },

        "step_analysis": {

            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "step_number": {
                        "type": "integer"
                    },

                    "student_step": {
                        "type": "string"
                    },

                    "status": {
                        "type": "string"
                    },

                    "explanation": {
                        "type": "string"
                    }
                },

                "required": [
                    "step_number",
                    "student_step",
                    "status",
                    "explanation"
                ]
            }
        },

        "teaching_block": {

            "type": "object",

            "properties": {

                "short_summary": {
                    "type": "string"
                },

                "steps": {

                    "type": "array",

                    "items": {

                        "type": "object",

                        "properties": {

                            "title": {
                                "type": "string"
                            },

                            "explanation": {
                                "type": "string"
                            },

                            "math": {
                                "type": "string"
                            }
                        },

                        "required": [
                            "title",
                            "explanation",
                            "math"
                        ]
                    }
                },

                "final_answer": {
                    "type": "string"
                },

                "mistake_fix": {
                    "type": "string"
                }
            },

            "required": [
                "short_summary",
                "steps",
                "final_answer",
                "mistake_fix"
            ]
        }
    },

    "required": [
        "student_is_correct",
        "topic",
        "subtopic",
        "difficulty",
        "misconception_category",
        "confidence",
        "first_wrong_step",
        "diagnosis",
        "hint_1",
        "hint_2",
        "hint_3",
        "full_explanation",
        "symbolic_verification",
        "step_analysis",
        "teaching_block"
    ]
}


# =========================================================
# GEMINI OUTPUT SCHEMA — START HELP
# =========================================================

start_help_schema = {

    "type": "object",

    "properties": {

        "topic": {
            "type": "string"
        },

        "subtopic": {
            "type": "string"
        },

        "difficulty": {
            "type": "string"
        },

        "concept": {
            "type": "string"
        },

        "recognition": {
            "type": "string"
        },

        "hint_1": {
            "type": "string"
        },

        "hint_1_math": {
            "type": "string"
        },

        "hint_2": {
            "type": "string"
        },

        "hint_2_math": {
            "type": "string"
        },

        "hint_3": {
            "type": "string"
        },

        "hint_3_math": {
            "type": "string"
        },

        "student_task": {
            "type": "string"
        }
    },

    "required": [
        "topic",
        "subtopic",
        "difficulty",
        "concept",
        "recognition",
        "hint_1",
        "hint_1_math",
        "hint_2",
        "hint_2_math",
        "hint_3",
        "hint_3_math",
        "student_task"
    ]
}


# =========================================================
# NORMALIZE MATH
# =========================================================

def normalize_math_text(
    text: str
) -> str:

    text = text.strip()

    replacements = {
        "×": "*",
        "·": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "π": "pi",
        "²": "^2",
        "³": "^3",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    text = re.sub(
        r"^\s*(step\s*\d+\s*[:.)-]?\s*)",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^\s*(therefore|thus|hence|so)\s*[:,]?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# =========================================================
# PARSE EXPRESSION
# =========================================================

def safe_parse_expression(
    expression: str
):

    expression = normalize_math_text(
        expression
    )

    if len(expression) > 200:
        return None

    try:

        return parse_expr(
            expression,
            local_dict=LOCAL_DICT,
            transformations=TRANSFORMATIONS,
            evaluate=True
        )

    except Exception:

        return None


# =========================================================
# SYMPY SETUP
# =========================================================

TRANSFORMATIONS = (
    standard_transformations
    +
    (
        implicit_multiplication_application,
        convert_xor,
    )
)


x, y, z, a, b, c, t, n, m = sp.symbols(
    "x y z a b c t n m"
)


LOCAL_DICT = {
    "x": x,
    "y": y,
    "z": z,
    "a": a,
    "b": b,
    "c": c,
    "t": t,
    "n": n,
    "m": m,

    "pi": sp.pi,
    "e": sp.E,
    "E": sp.E,

    "sqrt": sp.sqrt,

    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sec": sp.sec,
    "csc": sp.csc,
    "cot": sp.cot,

    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,

    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
}


# =========================================================
# PARSE EQUATION
# =========================================================

def parse_equation(
    line: str
):

    line = normalize_math_text(
        line
    )

    if (
        "<=" in line
        or
        ">=" in line
        or
        "!=" in line
    ):
        return None

    if line.count("=") != 1:
        return None

    left_text, right_text = line.split(
        "=",
        1
    )

    left = safe_parse_expression(
        left_text
    )

    right = safe_parse_expression(
        right_text
    )

    if (
        left is None
        or
        right is None
    ):
        return None

    return (
        left,
        right
    )


# =========================================================
# EQUATION EQUIVALENCE
# =========================================================

def equations_equivalent(
    equation_one,
    equation_two
):

    try:

        left1, right1 = equation_one
        left2, right2 = equation_two

        expr1 = sp.simplify(
            left1 - right1
        )

        expr2 = sp.simplify(
            left2 - right2
        )

        symbols = list(
            expr1.free_symbols
            |
            expr2.free_symbols
        )

        if not symbols:

            value1 = (
                sp.simplify(expr1)
                == 0
            )

            value2 = (
                sp.simplify(expr2)
                == 0
            )

            return (
                value1
                ==
                value2
            )

        if len(symbols) == 1:

            variable = symbols[0]

            try:

                solution1 = sp.solveset(
                    expr1,
                    variable,
                    domain=sp.S.Reals
                )

                solution2 = sp.solveset(
                    expr2,
                    variable,
                    domain=sp.S.Reals
                )

                if solution1 == solution2:
                    return True

            except Exception:
                pass

        if (
            expr1 != 0
            and
            expr2 != 0
        ):

            ratio = sp.simplify(
                expr1 / expr2
            )

            if (
                not ratio.free_symbols
                and
                ratio != 0
            ):
                return True

        return False

    except Exception:

        return None


# =========================================================
# EXPRESSION EQUIVALENCE
# =========================================================

def expressions_equivalent(
    expression_one,
    expression_two
):

    try:

        difference = sp.simplify(
            expression_one
            -
            expression_two
        )

        return difference == 0

    except Exception:

        return None


# =========================================================
# EXTRACT STEPS
# =========================================================

def extract_math_steps(
    attempted_solution: str
):

    raw_lines = (
        attempted_solution
        .replace(
            ";",
            "\n"
        )
        .splitlines()
    )

    steps = []

    for line in raw_lines:

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^\s*[-•]\s*",
            "",
            line
        )

        steps.append(
            line
        )

    return steps


# =========================================================
# SYMBOLIC STEP ANALYSIS
# =========================================================

def analyze_symbolic_steps(
    attempted_solution: str
):

    steps = extract_math_steps(
        attempted_solution
    )

    report = []

    previous_equation = None
    previous_expression = None

    for index, step in enumerate(
        steps,
        start=1
    ):

        equation = parse_equation(
            step
        )

        expression = None

        if equation is None:

            expression = safe_parse_expression(
                step
            )

        if equation is not None:

            status = "starting equation"

            detail = (
                "Parsed successfully as an equation."
            )

            if previous_equation is not None:

                equivalent = equations_equivalent(
                    previous_equation,
                    equation
                )

                if equivalent is True:

                    status = (
                        "symbolically equivalent"
                    )

                    detail = (
                        "This equation appears equivalent "
                        "to the previous equation."
                    )

                elif equivalent is False:

                    status = (
                        "possibly invalid transition"
                    )

                    detail = (
                        "This equation does not appear "
                        "equivalent to the previous equation."
                    )

                else:

                    status = (
                        "could not verify"
                    )

                    detail = (
                        "The symbolic engine could not "
                        "confidently verify this transition."
                    )

            report.append(
                {
                    "step_number": index,
                    "student_step": step,
                    "symbolic_status": status,
                    "symbolic_detail": detail,
                }
            )

            previous_equation = equation
            previous_expression = None

            continue

        if expression is not None:

            status = "parsed expression"

            detail = (
                "Parsed successfully as a mathematical expression."
            )

            if previous_expression is not None:

                equivalent = expressions_equivalent(
                    previous_expression,
                    expression
                )

                if equivalent is True:

                    status = (
                        "symbolically equivalent"
                    )

                    detail = (
                        "This expression is equivalent "
                        "to the previous expression."
                    )

                elif equivalent is False:

                    status = (
                        "possibly invalid transition"
                    )

                    detail = (
                        "This expression is not equivalent "
                        "to the previous expression."
                    )

            report.append(
                {
                    "step_number": index,
                    "student_step": step,
                    "symbolic_status": status,
                    "symbolic_detail": detail,
                }
            )

            previous_expression = expression
            previous_equation = None

            continue

        report.append(
            {
                "step_number": index,
                "student_step": step,
                "symbolic_status": "not parsed",
                "symbolic_detail": (
                    "This line may contain natural language "
                    "or notation that the symbolic engine "
                    "cannot directly verify."
                ),
            }
        )

    return report


# =========================================================
# CREATE SYMBOLIC REPORT
# =========================================================

def create_symbolic_report(
    attempted_solution: str
):

    analysis = analyze_symbolic_steps(
        attempted_solution
    )

    if not analysis:

        return (
            "No usable symbolic steps were detected."
        )

    report_lines = []

    for item in analysis:

        report_lines.append(
            (
                f"Step {item['step_number']}: "
                f"{item['student_step']}\n"
                f"SymPy status: "
                f"{item['symbolic_status']}\n"
                f"Detail: "
                f"{item['symbolic_detail']}"
            )
        )

    return "\n\n".join(
        report_lines
    )


# =========================================================
# GEMINI RETRY HELPER
# =========================================================

def generate_gemini_response(
    prompt: str,
    response_schema: dict
):

    max_retries = 4

    last_error = None

    for retry_index in range(
        max_retries
    ):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type":
                        "application/json",

                    "response_schema":
                        response_schema,
                },
            )

            return response

        except Exception as e:

            last_error = e

            error_text = str(e)

            temporary_error = (
                "429" in error_text
                or
                "503" in error_text
                or
                "504" in error_text
                or
                "RESOURCE_EXHAUSTED" in error_text
                or
                "UNAVAILABLE" in error_text
                or
                "DEADLINE_EXCEEDED" in error_text
                or
                "deadline expired" in error_text.lower()
                or
                "high demand" in error_text.lower()
                or
                "rate limit" in error_text.lower()
                or
                "temporarily unavailable" in error_text.lower()
            )

            if not temporary_error:
                raise

            if retry_index >= max_retries - 1:
                break

            wait_seconds = (
                2
                *
                (
                    retry_index
                    + 1
                )
            )

            time.sleep(
                wait_seconds
            )

    if last_error is not None:
        raise last_error

    raise RuntimeError(
        "Gemini did not return a response."
    )


# =========================================================
# I DON'T KNOW HOW TO START
# =========================================================

def get_starting_help(
    question: str
) -> StartHelpResult:

    prompt = f"""
You are MindStep, an AI mathematics learning coach.

The student has given you a mathematics problem but says:

"I do not know how to start."

Your job is NOT to solve the entire problem immediately.

Your job is to help the student begin thinking.

============================================================
QUESTION
============================================================

{question}

============================================================
YOUR TEACHING GOAL
============================================================

Identify the topic and the key idea the student should recognize.

Then create three progressively stronger starter hints.

The hints must work like this:

HINT 1:
Give only the concept or strategy.
Do not perform the whole calculation.
Do not reveal the final answer.

HINT 2:
Show the setup or identify the important pieces.
You may provide a useful formula.
Still do not finish the whole problem.

HINT 3:
Show the first meaningful mathematical step.
Give enough guidance that the student should now be able
to continue solving the problem themselves.
Do not reveal the final result unless it is absolutely
unavoidable for a trivial one-step problem.

student_task:
Give the student one clear thing to calculate or write next.

============================================================
EXAMPLE
============================================================

Question:
Differentiate y = x^2 ln(x^2 + 1)

Possible teaching structure:

concept:
This problem combines the product rule and chain rule.

recognition:
There are two multiplied functions: x^2 and ln(x^2 + 1).

hint_1:
Treat the expression as a product of two functions.

hint_1_math:
y = uv

hint_2:
Let u = x^2 and v = ln(x^2 + 1). Find u' and v' separately.

hint_2_math:
u=x^2, v=ln(x^2+1)

hint_3:
The logarithm requires the chain rule because its input is x^2+1.

hint_3_math:
v' = 2x/(x^2+1)

student_task:
Now find u' and substitute u, v, u', and v' into the product rule.

============================================================
RULES
============================================================

1. Do not give the full solution.
2. Do not give the final answer.
3. Use clear Grade 11–12 / JEE-friendly language.
4. Keep each hint concise.
5. Mathematical text in the math fields should contain
   only the useful mathematical expression.
6. If several methods exist, choose one sensible method
   but do not imply it is the only valid method.
7. Difficulty should be a short description such as
   Easy, Moderate, Hard, or JEE Advanced-style.
"""

    response = generate_gemini_response(
        prompt,
        start_help_schema
    )

    data = json.loads(
        response.text
    )

    return StartHelpResult(

        topic=data.get(
            "topic",
            "Mathematics"
        ),

        subtopic=data.get(
            "subtopic",
            ""
        ),

        difficulty=data.get(
            "difficulty",
            ""
        ),

        concept=data.get(
            "concept",
            ""
        ),

        recognition=data.get(
            "recognition",
            ""
        ),

        hint_1=data.get(
            "hint_1",
            ""
        ),

        hint_1_math=data.get(
            "hint_1_math",
            ""
        ),

        hint_2=data.get(
            "hint_2",
            ""
        ),

        hint_2_math=data.get(
            "hint_2_math",
            ""
        ),

        hint_3=data.get(
            "hint_3",
            ""
        ),

        hint_3_math=data.get(
            "hint_3_math",
            ""
        ),

        student_task=data.get(
            "student_task",
            ""
        ),
    )


# =========================================================
# MAIN AI ANALYSIS
# =========================================================

def analyze_student_attempt(
    question: str,
    attempted_solution: str
) -> CoachResult:

    symbolic_report = create_symbolic_report(
        attempted_solution
    )

    prompt = f"""
You are an advanced AI Mathematics Learning Coach for
Grade 11, Grade 12, JEE Main, and introductory JEE Advanced mathematics.

Your main job is NOT to immediately give the answer.

Your job is to understand HOW the student reasoned,
find the FIRST meaningful mathematical error,
identify the misconception behind it,
and guide the student toward fixing it.


============================================================
QUESTION
============================================================

{question}


============================================================
STUDENT ATTEMPT
============================================================

{attempted_solution}


============================================================
SYMBOLIC ENGINE REPORT
============================================================

{symbolic_report}


The symbolic report comes from SymPy.

Use it only as supporting evidence.

Do NOT blindly trust it.

SymPy may fail to understand:

- natural-language reasoning
- calculus notation
- geometry explanations
- unusual notation
- inequalities
- trigonometric assumptions
- domain restrictions

You are responsible for the final mathematical judgment.


============================================================
CHECK WHETHER THE STUDENT IS CORRECT
============================================================

Set student_is_correct = true ONLY if the student's
latest reasoning and result are mathematically valid.

If correct:

- misconception_category must be "no_clear_error"
- first_wrong_step must be ""
- hint_1 must be ""
- hint_2 must be ""
- hint_3 must be ""


============================================================
SUPPORTED MATHEMATICS
============================================================

You can analyze:

- arithmetic
- algebra
- linear equations
- simultaneous equations
- inequalities
- quadratic equations
- polynomials
- factorization
- exponents
- logarithms
- functions
- inverse functions
- sequences and series
- binomial theorem
- permutations and combinations
- probability
- trigonometry
- trigonometric identities
- coordinate geometry
- straight lines
- circles
- conic sections
- limits
- continuity
- derivatives
- chain rule
- product rule
- quotient rule
- applications of derivatives
- indefinite integration
- definite integration
- substitution
- differential equations
- matrices
- determinants
- vectors
- 3D geometry
- other Grade 11, Grade 12 and JEE mathematics


============================================================
MISCONCEPTION CATEGORIES
============================================================

Choose EXACTLY ONE category from:

{", ".join(MISCONCEPTION_CATEGORIES)}


============================================================
STEP-BY-STEP ANALYSIS
============================================================

Break the student's attempt into meaningful steps.

For every step return:

- step_number
- student_step
- status
- explanation

status should normally be one of:

correct
incorrect
uncertain

Find the FIRST incorrect mathematical step.

Do not judge only from the final answer.

A student may have:

- a correct method but arithmetic mistake
- correct early steps and a later error
- a correct final answer from invalid reasoning
- an incomplete solution
- several errors

The first meaningful mathematical error is most important.


============================================================
HINT 1
============================================================

Do NOT reveal the final answer.

Point the student toward the part that should be checked.

Make them think.


============================================================
HINT 2
============================================================

Be more specific.

Explain the mathematical idea they need.

Still avoid completing the problem.


============================================================
HINT 3
============================================================

Give strong guidance.

You may show the key correction or setup.

Let the student finish the final reasoning where possible.


============================================================
FULL EXPLANATION
============================================================

Create the full mathematically correct solution internally.

Explain WHY each important step works.

Mention important domain restrictions or assumptions.

Use clear Grade-12-friendly language.


============================================================
TEACHING BLOCK
============================================================

This will be displayed visually to the student.

Do NOT produce one giant paragraph.

Create a clean teaching sequence.


short_summary:

Use at most 2 short sentences.

Explain the main idea.


steps:

Use 3 to 6 steps.

Each step must contain:

title:
A short descriptive title.

explanation:
At most about 2 short sentences.

math:
Only the important mathematical expression for that step.


final_answer:

Only the final mathematical result or conclusion.


mistake_fix:

Explain simply:

- what was wrong in the student's earlier reasoning
- what changed in the corrected method


============================================================
IMPORTANT RULES
============================================================

1. Accept valid alternative methods.

2. Do not invent mistakes.

3. Distinguish arithmetic mistakes from conceptual errors.

4. Do not penalize skipped trivial algebra.

5. For calculus, carefully check chain, product and quotient rules.

6. For integration, check +C, substitution and bounds.

7. For logarithms, check domains and log laws.

8. For trigonometry, check identities and general solutions.

9. Watch for extraneous solutions.

10. Consider domain restrictions for roots, logs and fractions.

11. For probability, check the sample space and assumptions.

12. If a problem is ambiguous, acknowledge that.

13. confidence must be between 0 and 1.

14. Use student-friendly language.

15. Never claim SymPy verified something it did not verify.
"""

    response = generate_gemini_response(
        prompt,
        analysis_schema
    )

    data = json.loads(
        response.text
    )

    confidence = data.get(
        "confidence",
        0
    )

    try:

        confidence = float(
            confidence
        )

    except Exception:

        confidence = 0.0

    confidence = max(
        0.0,
        min(
            1.0,
            confidence
        )
    )

    return CoachResult(

        student_is_correct=data.get(
            "student_is_correct",
            False
        ),

        topic=data.get(
            "topic",
            "Unknown"
        ),

        subtopic=data.get(
            "subtopic",
            ""
        ),

        difficulty=data.get(
            "difficulty",
            ""
        ),

        misconception_category=data.get(
            "misconception_category",
            "no_clear_error"
        ),

        confidence=confidence,

        first_wrong_step=data.get(
            "first_wrong_step",
            ""
        ),

        diagnosis=data.get(
            "diagnosis",
            ""
        ),

        hint_1=data.get(
            "hint_1",
            ""
        ),

        hint_2=data.get(
            "hint_2",
            ""
        ),

        hint_3=data.get(
            "hint_3",
            ""
        ),

        full_explanation=data.get(
            "full_explanation",
            ""
        ),

        symbolic_verification=data.get(
            "symbolic_verification",
            ""
        ),

        step_analysis=data.get(
            "step_analysis",
            []
        ),

        teaching_block=data.get(
            "teaching_block",
            {}
        ),
    )


# =========================================================
# HINT PROGRESSION
# =========================================================

def get_visible_feedback(
    result: CoachResult,
    attempt_number: int
):

    if result.student_is_correct:

        return {
            "level": "Solved",
            "hint": "",
            "show_full_explanation": False,
            "solved": True,
        }

    if attempt_number <= 1:

        return {
            "level": "Hint 1",
            "hint": result.hint_1,
            "show_full_explanation": False,
            "solved": False,
        }

    if attempt_number == 2:

        return {
            "level": "Hint 2",
            "hint": result.hint_2,
            "show_full_explanation": False,
            "solved": False,
        }

    if attempt_number == 3:

        return {
            "level": "Hint 3",
            "hint": result.hint_3,
            "show_full_explanation": False,
            "solved": False,
        }

    return {
        "level": "Full Explanation",
        "hint": result.hint_3,
        "show_full_explanation": True,
        "solved": False,
    }