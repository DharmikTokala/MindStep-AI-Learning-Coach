import html
import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from coach_core import analyze_student_attempt
from ui_styles import (
    apply_global_styles,
    render_section_header,
    render_soft_card,
    render_highlight_banner,
)


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="AI Evaluation | MindStep",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


# =========================================================
# PAGE-SPECIFIC STYLES
# =========================================================

st.markdown(
    """
    <style>

    .eval-hero {
        border:1px solid rgba(148,163,184,0.14);
        border-radius:28px;
        padding:40px 46px;
        margin-bottom:28px;
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(139,92,246,0.22),
                transparent 34%
            ),
            radial-gradient(
                circle at 0% 100%,
                rgba(14,165,233,0.16),
                transparent 35%
            ),
            rgba(15,23,42,0.72);
    }

    .eval-badge {
        display:inline-block;
        padding:7px 13px;
        border-radius:999px;
        background:rgba(59,130,246,0.11);
        border:1px solid rgba(96,165,250,0.28);
        color:#93c5fd;
        font-size:0.8rem;
        font-weight:800;
        letter-spacing:0.05em;
        margin-bottom:18px;
    }

    .eval-title {
        color:#f8fafc;
        font-size:3rem;
        font-weight:900;
        line-height:1.08;
        letter-spacing:-0.04em;
        margin-bottom:18px;
    }

    .eval-gradient {
        background:linear-gradient(
            90deg,
            #60a5fa,
            #818cf8,
            #c084fc
        );
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        background-clip:text;
    }

    .eval-subtitle {
        color:#aebbd0;
        font-size:1.05rem;
        line-height:1.8;
        max-width:900px;
    }

    .eval-stat {
        min-height:145px;
        border:1px solid rgba(148,163,184,0.15);
        background:rgba(15,23,42,0.70);
        border-radius:20px;
        padding:22px;
        margin-bottom:10px;
    }

    .eval-stat-label {
        color:#94a3b8;
        font-size:0.78rem;
        font-weight:800;
        text-transform:uppercase;
        letter-spacing:0.08em;
        margin-bottom:10px;
    }

    .eval-stat-value {
        color:#f8fafc;
        font-size:2rem;
        font-weight:900;
        line-height:1.1;
        margin-bottom:8px;
    }

    .eval-stat-note {
        color:#7f8ea3;
        font-size:0.8rem;
        line-height:1.45;
    }

    .eval-step {
        border:1px solid rgba(148,163,184,0.14);
        background:rgba(15,23,42,0.66);
        border-radius:20px;
        padding:22px;
        min-height:190px;
    }

    .eval-step-number {
        color:#60a5fa;
        font-weight:900;
        font-size:0.78rem;
        letter-spacing:0.08em;
        margin-bottom:12px;
    }

    .eval-step-title {
        color:#f8fafc;
        font-size:1.2rem;
        font-weight:800;
        margin-bottom:10px;
    }

    .eval-step-text {
        color:#aebbd0;
        line-height:1.65;
        font-size:0.93rem;
    }

    .eval-note {
        border:1px solid rgba(148,163,184,0.14);
        background:rgba(15,23,42,0.60);
        border-radius:18px;
        padding:18px 20px;
        color:#aebbd0;
        line-height:1.65;
        font-size:0.93rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def readable_label(value):

    if not value:
        return "Unknown"

    return (
        value
        .replace("_", " ")
        .title()
    )


def render_eval_stat(
    label,
    value,
    note,
):

    card = (
        '<div class="eval-stat">'
        f'<div class="eval-stat-label">{html.escape(str(label))}</div>'
        f'<div class="eval-stat-value">{html.escape(str(value))}</div>'
        f'<div class="eval-stat-note">{html.escape(str(note))}</div>'
        '</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


def render_eval_step(
    number,
    title,
    text,
):

    card = (
        '<div class="eval-step">'
        f'<div class="eval-step-number">{html.escape(str(number))}</div>'
        f'<div class="eval-step-title">{html.escape(str(title))}</div>'
        f'<div class="eval-step-text">{html.escape(str(text))}</div>'
        '</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


# =========================================================
# HERO
# =========================================================

hero_html = (
    '<div class="eval-hero">'
    '<div class="eval-badge">🧪 MINDSTEP · MODEL EVALUATION</div>'
    '<div class="eval-title">'
    'Can the AI correctly identify '
    '<span class="eval-gradient">how a student went wrong?</span>'
    '</div>'
    '<div class="eval-subtitle">'
    'This page evaluates MindStep’s misconception detector using labeled '
    'student-response examples. It is intended for transparency, testing, '
    'and project evaluation rather than normal student use.'
    '</div>'
    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


render_highlight_banner(
    "The benchmark compares a <b>human-assigned misconception label</b> "
    "with the label predicted by the same AI system used in the learning coach."
)


# =========================================================
# PATHS
# =========================================================

DATA_PATH = Path("data") / "evaluation_cases.json"
RESULTS_PATH = Path("data") / "evaluation_results.json"


# =========================================================
# LOAD DATA
# =========================================================

if not DATA_PATH.exists():

    st.error(
        "Evaluation dataset not found."
    )

    st.code(
        str(DATA_PATH)
    )

    st.stop()


with open(
    DATA_PATH,
    "r",
    encoding="utf-8",
) as file:

    evaluation_cases = json.load(
        file
    )


# =========================================================
# STORAGE HELPERS
# =========================================================

def save_results(results):

    RESULTS_PATH.parent.mkdir(
        exist_ok=True
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_saved_results():

    if not RESULTS_PATH.exists():
        return []

    try:

        with open(
            RESULTS_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(
                file
            )

    except Exception:

        return []


# =========================================================
# EVALUATION FUNCTION
# =========================================================

def evaluate_case(
    case,
    max_retries=2,
):

    question = case.get(
        "question",
        ""
    )

    attempted_solution = case.get(
        "attempted_solution",
        ""
    )

    human_label = case.get(
        "label",
        ""
    )

    last_error = ""


    for retry_number in range(
        max_retries + 1
    ):

        try:

            prediction = analyze_student_attempt(
                question,
                attempted_solution,
            )

            predicted_label = (
                prediction
                .misconception_category
            )

            return {
                "question":
                    question,

                "attempted_solution":
                    attempted_solution,

                "human_label":
                    human_label,

                "predicted_label":
                    predicted_label,

                "correct":
                    predicted_label
                    == human_label,

                "confidence":
                    prediction.confidence,

                "diagnosis":
                    prediction.diagnosis,

                "api_failed":
                    False,

                "error_message":
                    "",
            }

        except Exception as e:

            last_error = str(e)

            if retry_number < max_retries:

                time.sleep(
                    2
                )


    return {
        "question":
            question,

        "attempted_solution":
            attempted_solution,

        "human_label":
            human_label,

        "predicted_label":
            "",

        "correct":
            False,

        "confidence":
            0,

        "diagnosis":
            "",

        "api_failed":
            True,

        "error_message":
            last_error,
    }


# =========================================================
# WHAT IS BEING TESTED
# =========================================================

render_section_header(
    "How the Evaluation Works",
    "The benchmark follows a simple three-step comparison."
)


col1, col2, col3 = st.columns(
    3
)


with col1:

    render_eval_step(
        "01 · HUMAN LABEL",
        "Known misconception",
        "Each benchmark example has a predefined misconception category such as sign error, fraction error, or conceptual misunderstanding.",
    )


with col2:

    render_eval_step(
        "02 · AI ANALYSIS",
        "Model prediction",
        "MindStep analyzes the student's question and attempted reasoning using the same misconception detector used by the main learning coach.",
    )


with col3:

    render_eval_step(
        "03 · COMPARISON",
        "Measure performance",
        "The predicted category is compared with the human label to calculate classification metrics such as accuracy and macro F1.",
    )


# =========================================================
# DATASET OVERVIEW
# =========================================================

st.divider()

render_section_header(
    "Benchmark Dataset",
    "The current labeled examples used to test the misconception detector."
)


category_counts = {}


for case in evaluation_cases:

    label = case.get(
        "label",
        "unknown"
    )

    category_counts[label] = (
        category_counts.get(
            label,
            0
        )
        + 1
    )


overview_col1, overview_col2 = st.columns(
    [1, 2]
)


with overview_col1:

    render_eval_stat(
        "Labeled Examples",
        len(evaluation_cases),
        "Total examples currently included in the benchmark dataset.",
    )

    render_eval_stat(
        "Categories",
        len(category_counts),
        "Distinct human-labeled misconception categories represented.",
    )


with overview_col2:

    category_rows = []

    for label, count in category_counts.items():

        category_rows.append(
            {
                "Category":
                    readable_label(
                        label
                    ),

                "Examples":
                    count,
            }
        )


    category_df = pd.DataFrame(
        category_rows
    )


    if not category_df.empty:

        category_df = category_df.sort_values(
            "Examples",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "Category"
            )
        )


with st.expander(
    "🔎 View benchmark examples"
):

    preview_rows = []

    for case in evaluation_cases:

        preview_rows.append(
            {
                "Question":
                    case.get(
                        "question",
                        ""
                    ),

                "Student Attempt":
                    case.get(
                        "attempted_solution",
                        ""
                    ),

                "Human Label":
                    readable_label(
                        case.get(
                            "label",
                            ""
                        )
                    ),
            }
        )


    st.dataframe(
        pd.DataFrame(
            preview_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# SESSION STATE
# =========================================================

if "evaluation_results" not in st.session_state:

    st.session_state[
        "evaluation_results"
    ] = load_saved_results()


# =========================================================
# RUN EVALUATION
# =========================================================

st.divider()

render_section_header(
    "Run the Benchmark",
    "Use the quick test while developing. Run the full benchmark when you want a broader evaluation."
)


col1, col2 = st.columns(
    2
)


with col1:

    run_quick = st.button(
        "⚡ Run Quick Test · 10 Examples",
        use_container_width=True,
    )


with col2:

    run_full = st.button(
        "🧪 Run Full Benchmark · All Examples",
        type="primary",
        use_container_width=True,
    )


st.caption(
    "The quick test only evaluates the first 10 examples in the dataset. "
    "It should not be treated as representative of the full benchmark."
)


if run_quick or run_full:

    if run_quick:

        cases_to_run = evaluation_cases[
            :10
        ]

    else:

        cases_to_run = evaluation_cases


    results = []

    progress = st.progress(
        0
    )

    status = st.empty()


    for index, case in enumerate(
        cases_to_run
    ):

        status.write(
            f"Evaluating {index + 1} of {len(cases_to_run)}..."
        )

        result = evaluate_case(
            case
        )

        results.append(
            result
        )

        save_results(
            results
        )

        progress.progress(
            (index + 1)
            / len(cases_to_run)
        )

        time.sleep(
            0.5
        )


    st.session_state[
        "evaluation_results"
    ] = results

    status.success(
        "Evaluation complete."
    )

    st.rerun()


# =========================================================
# RESULTS
# =========================================================

results = st.session_state.get(
    "evaluation_results",
    []
)


if not results:

    render_soft_card(
        "📭 No saved evaluation results yet",
        "Run the quick test first to confirm the evaluation pipeline is working."
    )

    st.stop()


successful_results = [
    result
    for result in results
    if not result.get(
        "api_failed",
        False
    )
]


api_failures = [
    result
    for result in results
    if result.get(
        "api_failed",
        False
    )
]


successful_count = len(
    successful_results
)

api_failure_count = len(
    api_failures
)


correct_count = sum(
    1
    for result in successful_results
    if result.get(
        "correct",
        False
    )
)


incorrect_count = (
    successful_count
    - correct_count
)


if successful_count > 0:

    accuracy = (
        correct_count
        / successful_count
    )

else:

    accuracy = 0


# =========================================================
# CLASSIFICATION METRICS
# =========================================================

labels = sorted(
    set(
        result[
            "human_label"
        ]
        for result in successful_results
    )
    |
    set(
        result[
            "predicted_label"
        ]
        for result in successful_results
    )
)


precision_values = []
recall_values = []
f1_values = []

per_category_rows = []


for label in labels:

    tp = sum(
        1
        for result in successful_results
        if (
            result["human_label"] == label
            and
            result["predicted_label"] == label
        )
    )

    fp = sum(
        1
        for result in successful_results
        if (
            result["human_label"] != label
            and
            result["predicted_label"] == label
        )
    )

    fn = sum(
        1
        for result in successful_results
        if (
            result["human_label"] == label
            and
            result["predicted_label"] != label
        )
    )


    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )


    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )


    f1 = (
        2
        * precision
        * recall
        / (
            precision
            + recall
        )
        if (
            precision
            + recall
        ) > 0
        else 0
    )


    precision_values.append(
        precision
    )

    recall_values.append(
        recall
    )

    f1_values.append(
        f1
    )


    per_category_rows.append(
        {
            "Category":
                readable_label(
                    label
                ),

            "Precision":
                round(
                    precision
                    * 100,
                    1
                ),

            "Recall":
                round(
                    recall
                    * 100,
                    1
                ),

            "F1":
                round(
                    f1
                    * 100,
                    1
                ),
        }
    )


macro_precision = (
    sum(
        precision_values
    )
    / len(
        precision_values
    )
    if precision_values
    else 0
)


macro_recall = (
    sum(
        recall_values
    )
    / len(
        recall_values
    )
    if recall_values
    else 0
)


macro_f1 = (
    sum(
        f1_values
    )
    / len(
        f1_values
    )
    if f1_values
    else 0
)


# =========================================================
# PERFORMANCE SUMMARY
# =========================================================

st.divider()

render_section_header(
    "Model Performance",
    "Metrics below use only examples that were successfully evaluated."
)


col1, col2, col3, col4 = st.columns(
    4
)


with col1:

    render_eval_stat(
        "Accuracy",
        f"{accuracy * 100:.1f}%",
        "Share of successful tests where AI label matched human label.",
    )


with col2:

    render_eval_stat(
        "Macro F1",
        f"{macro_f1 * 100:.1f}%",
        "Balances precision and recall while weighting each tested category equally.",
    )


with col3:

    render_eval_stat(
        "Successful Tests",
        successful_count,
        "Examples that completed without an API/system failure.",
    )


with col4:

    render_eval_stat(
        "API Failures",
        api_failure_count,
        "System failures excluded from classification accuracy.",
    )


if api_failure_count > 0:

    st.warning(
        f"{api_failure_count} example(s) could not be evaluated because of "
        f"API/system errors. They are excluded from accuracy and F1."
    )


# =========================================================
# INTERPRETATION
# =========================================================

st.divider()

render_section_header(
    "How to Read the Metrics",
    "What each result actually means."
)


col1, col2 = st.columns(
    2
)


with col1:

    render_soft_card(
        "🎯 Accuracy",
        "The percentage of successfully evaluated examples where the AI "
        "selected the same misconception label as the benchmark's human label."
    )


with col2:

    render_soft_card(
        "📊 Macro F1",
        "A combined precision-and-recall measure calculated separately for "
        "each tested category and then averaged so that categories receive equal weight."
    )


st.markdown(
    (
        '<div class="eval-note">'
        '<b>Important:</b> a high score on a small or narrow benchmark does not '
        'prove that the system will perform equally well on all real student work. '
        'The dataset size, category balance, labeling quality, and topic coverage '
        'all affect how meaningful the result is.'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# =========================================================
# PREDICTION TABLE
# =========================================================

st.divider()

render_section_header(
    "Prediction Results",
    "A case-by-case comparison between benchmark labels and AI predictions."
)


prediction_rows = []


for result in successful_results:

    prediction_rows.append(
        {
            "Question":
                result["question"],

            "Human Label":
                readable_label(
                    result["human_label"]
                ),

            "AI Prediction":
                readable_label(
                    result["predicted_label"]
                ),

            "Result":
                (
                    "✅ Correct"
                    if result["correct"]
                    else "❌ Incorrect"
                ),

            "Confidence":
                f"{result['confidence'] * 100:.0f}%",
        }
    )


if prediction_rows:

    st.dataframe(
        pd.DataFrame(
            prediction_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# CATEGORY PERFORMANCE
# =========================================================

st.divider()

render_section_header(
    "Performance by Misconception",
    "Precision, recall, and F1 for each category represented in this run."
)


if per_category_rows:

    category_performance_df = pd.DataFrame(
        per_category_rows
    )

    st.dataframe(
        category_performance_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# CONFUSION MATRIX
# =========================================================

st.divider()

render_section_header(
    "Confusion Matrix",
    "A technical view of which misconception categories are confused with each other."
)


if successful_results:

    confusion_rows = []

    for result in successful_results:

        confusion_rows.append(
            {
                "Human Label":
                    readable_label(
                        result["human_label"]
                    ),

                "AI Prediction":
                    readable_label(
                        result["predicted_label"]
                    ),
            }
        )


    confusion_df = pd.DataFrame(
        confusion_rows
    )


    confusion_matrix = pd.crosstab(
        confusion_df[
            "Human Label"
        ],
        confusion_df[
            "AI Prediction"
        ],
    )


    st.dataframe(
        confusion_matrix,
        use_container_width=True,
    )


# =========================================================
# MISCLASSIFIED EXAMPLES
# =========================================================

st.divider()

render_section_header(
    "Where the Model Got It Wrong",
    "Misclassified examples are often more useful for improving the system than correct ones."
)


mistakes = [
    result
    for result in successful_results
    if not result["correct"]
]


if not mistakes:

    st.success(
        "No model misclassifications were recorded in this evaluation run."
    )

else:

    for number, mistake in enumerate(
        mistakes,
        start=1,
    ):

        human_label = readable_label(
            mistake["human_label"]
        )

        predicted_label = readable_label(
            mistake["predicted_label"]
        )


        with st.expander(
            f"Error {number}: {human_label} → {predicted_label}"
        ):

            st.markdown(
                "**Question**"
            )

            st.write(
                mistake["question"]
            )


            st.markdown(
                "**Student Attempt**"
            )

            st.code(
                mistake["attempted_solution"],
                language="text",
            )


            col1, col2, col3 = st.columns(
                3
            )


            with col1:

                st.write(
                    f"**Human label**  \n{human_label}"
                )


            with col2:

                st.write(
                    f"**AI prediction**  \n{predicted_label}"
                )


            with col3:

                st.write(
                    f"**Confidence**  \n"
                    f"{mistake['confidence'] * 100:.0f}%"
                )


            st.markdown(
                "**AI Diagnosis**"
            )

            st.write(
                mistake["diagnosis"]
            )


# =========================================================
# API FAILURES
# =========================================================

if api_failures:

    st.divider()

    render_section_header(
        "API / System Failures",
        "These are excluded from classification metrics because the model did not return a usable prediction."
    )


    for number, failure in enumerate(
        api_failures,
        start=1,
    ):

        with st.expander(
            f"API Failure {number}"
        ):

            st.write(
                failure["question"]
            )

            st.code(
                failure["error_message"]
            )


# =========================================================
# RESEARCH SUMMARY
# =========================================================

st.divider()

render_section_header(
    "Research Summary",
    "A concise description of the current benchmark run."
)


render_soft_card(
    "📄 Current Evaluation",
    f"The misconception detector successfully evaluated "
    f"<b>{successful_count} examples</b>. "
    f"On those examples it achieved "
    f"<b>{accuracy * 100:.1f}% accuracy</b> and "
    f"<b>{macro_f1 * 100:.1f}% macro F1</b>. "
    f"<b>{api_failure_count}</b> example(s) were excluded because of API/system failures."
)


# =========================================================
# LIMITATIONS
# =========================================================

st.divider()

render_section_header(
    "Limitations",
    "What this benchmark does and does not establish."
)


render_soft_card(
    "⚠️ Prototype Evaluation",
    "The dataset is manually constructed and relatively small. "
    "Some misconception categories can overlap, and different human reviewers "
    "may reasonably assign different labels to the same student response."
)


limitations = [
    "The benchmark is not yet based on a large real-student dataset.",
    "The current dataset may not represent every Grade 11–12 or JEE mathematics topic equally.",
    "A single human label may not capture all reasonable interpretations of a student's mistake.",
    "Confidence scores are model-generated and should not be treated as calibrated probabilities.",
    "A quick 10-example run is useful for debugging but is not a strong estimate of overall performance.",
]


for limitation in limitations:

    st.write(
        f"• {limitation}"
    )


render_highlight_banner(
    "Future evaluation could use <b>real student responses</b>, "
    "<b>multiple human annotators</b>, <b>inter-rater agreement</b>, "
    "and a larger held-out benchmark covering more mathematical topics."
)


# =========================================================
# CLEAR SAVED RESULTS
# =========================================================

st.divider()

if st.button(
    "🗑️ Clear Saved Evaluation Results"
):

    st.session_state[
        "evaluation_results"
    ] = []

    if RESULTS_PATH.exists():
        RESULTS_PATH.unlink()

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    (
        '<div style="'
        'text-align:center;'
        'color:#64748b;'
        'padding:22px 0 8px 0;'
        'font-size:0.9rem;'
        '">'
        'A useful AI learning tool should be evaluated, not just demonstrated.'
        '</div>'
    ),
    unsafe_allow_html=True,
)