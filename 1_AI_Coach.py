import streamlit as st

from coach_core import (
    analyze_student_attempt,
    get_visible_feedback,
    get_starting_help,
)

from storage import (
    save_attempt,
    get_all_attempts,
)

from ui_styles import (
    apply_global_styles,
    render_hero_section,
    render_feature_cards,
    render_section_header,
    render_highlight_banner,
    render_soft_card,
)


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="AI Learning Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


st.sidebar.markdown(
    (
        '<div style="'
        'padding:14px 10px 18px 10px;'
        'border-bottom:1px solid rgba(148,163,184,0.15);'
        'margin-bottom:14px;'
        '">'
        '<div style="'
        'font-size:1.35rem;'
        'font-weight:800;'
        'color:#f8fafc;'
        '">'
        '🧠 MindStep'
        '</div>'
        '<div style="'
        'font-size:0.82rem;'
        'color:#94a3b8;'
        'margin-top:4px;'
        'line-height:1.5;'
        '">'
        'AI-powered learning coach for understanding mistakes, '
        'fixing reasoning, and building mastery.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True
)

st.sidebar.caption(
    "Navigate using the pages above."
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    (
        '<div style="'
        'font-size:0.78rem;'
        'color:#64748b;'
        'line-height:1.5;'
        '">'
        'Built for Grade 11–12 / JEE-style mathematics.'
        '</div>'
    ),
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "coach_result" not in st.session_state:
    st.session_state["coach_result"] = None

if "attempt_number" not in st.session_state:
    st.session_state["attempt_number"] = 1

if "current_question" not in st.session_state:
    st.session_state["current_question"] = ""

if "student_attempt" not in st.session_state:
    st.session_state["student_attempt"] = ""

if "start_help_result" not in st.session_state:
    st.session_state["start_help_result"] = None

if "start_help_level" not in st.session_state:
    st.session_state["start_help_level"] = 1


# =========================================================
# HELPERS
# =========================================================

def readable_category(category):

    if not category:
        return "None"

    if category == "no_clear_error":
        return "No Misconception"

    return (
        category
        .replace("_", " ")
        .title()
    )


def clean_latex_math(text: str):

    if not text:
        return ""

    text = text.strip()

    if text.startswith("$$") and text.endswith("$$"):
        text = text[2:-2].strip()

    if text.startswith("\\[") and text.endswith("\\]"):
        text = text[2:-2].strip()

    if text.startswith("\\(") and text.endswith("\\)"):
        text = text[2:-2].strip()

    return text


def reset_problem():

    st.session_state["coach_result"] = None
    st.session_state["attempt_number"] = 1
    st.session_state["current_question"] = ""
    st.session_state["student_attempt"] = ""

    st.session_state["start_help_result"] = None
    st.session_state["start_help_level"] = 1

    for key in [
        "retry_box",
        "starter_attempt_box",
    ]:

        if key in st.session_state:
            del st.session_state[key]


def render_math_block(
    math_text: str
):

    if not math_text:
        return

    cleaned = clean_latex_math(
        math_text
    )

    try:

        st.latex(
            cleaned
        )

    except Exception:

        st.code(
            cleaned,
            language="text"
        )


# =========================================================
# REASONING STEP CARDS
# =========================================================

def render_reasoning_steps(result):

    steps = result.step_analysis

    if not steps:
        return

    render_section_header(
        "Your Reasoning, Step by Step",
        "The coach checks each meaningful step, not just the final answer."
    )

    first_incorrect_seen = False

    for step in steps:

        status = (
            step.get(
                "status",
                "uncertain"
            )
            .lower()
            .strip()
        )

        step_number = step.get(
            "step_number",
            ""
        )

        student_step = step.get(
            "student_step",
            ""
        )

        explanation = step.get(
            "explanation",
            ""
        )

        is_first_wrong = (
            status == "incorrect"
            and not first_incorrect_seen
        )

        if is_first_wrong:
            first_incorrect_seen = True


        if status == "correct":

            border = "rgba(34,197,94,0.35)"
            background = "rgba(22,101,52,0.10)"
            badge_background = "rgba(34,197,94,0.16)"
            badge_color = "#4ade80"

            icon = "✓"
            label = "Correct Step"

        elif status == "incorrect":

            border = "rgba(239,68,68,0.40)"
            background = "rgba(127,29,29,0.12)"
            badge_background = "rgba(239,68,68,0.16)"
            badge_color = "#f87171"

            icon = "✕"

            if is_first_wrong:
                label = "First Mistake Detected"

            else:
                label = "Incorrect Step"

        else:

            border = "rgba(96,165,250,0.28)"
            background = "rgba(30,64,175,0.08)"
            badge_background = "rgba(59,130,246,0.14)"
            badge_color = "#60a5fa"

            icon = "?"
            label = "Needs Checking"


        card_html = (
            f'<div style="'
            f'border:1px solid {border};'
            f'background:{background};'
            f'border-radius:20px;'
            f'padding:20px 22px;'
            f'margin-bottom:10px;'
            f'">'

            f'<div style="'
            f'display:flex;'
            f'align-items:center;'
            f'justify-content:space-between;'
            f'gap:12px;'
            f'margin-bottom:12px;'
            f'">'

            f'<div style="'
            f'font-size:1.15rem;'
            f'font-weight:800;'
            f'color:#f8fafc;'
            f'">'
            f'Step {step_number}'
            f'</div>'

            f'<div style="'
            f'display:inline-block;'
            f'padding:6px 11px;'
            f'border-radius:999px;'
            f'background:{badge_background};'
            f'color:{badge_color};'
            f'font-size:0.78rem;'
            f'font-weight:800;'
            f'letter-spacing:0.05em;'
            f'">'
            f'{icon} {label}'
            f'</div>'

            f'</div>'

            f'<div style="'
            f'color:#cbd5e1;'
            f'font-size:0.96rem;'
            f'line-height:1.65;'
            f'">'
            f'{explanation}'
            f'</div>'

            f'</div>'
        )

        st.markdown(
            card_html,
            unsafe_allow_html=True
        )

        if student_step:

            with st.container(
                border=True
            ):

                st.caption(
                    "Student's step"
                )

                render_math_block(
                    student_step
                )

        if is_first_wrong:

            st.error(
                "🎯 **This is the first point where the reasoning breaks.** "
                "Fix this step first — later steps may depend on it."
            )


# =========================================================
# CLEAN TEACHING WALKTHROUGH
# =========================================================

def render_solution_walkthrough(result):

    teaching = (
        result.teaching_block
        or {}
    )

    short_summary = teaching.get(
        "short_summary",
        ""
    )

    steps = teaching.get(
        "steps",
        []
    )

    final_answer = teaching.get(
        "final_answer",
        ""
    )

    mistake_fix = teaching.get(
        "mistake_fix",
        ""
    )

    if short_summary:

        render_highlight_banner(
            "🧠 <b>Big idea</b><br>"
            + short_summary
        )

    if steps:

        render_section_header(
            "Step-by-Step Explanation",
            "Follow the reasoning one idea at a time."
        )

        for index, step in enumerate(
            steps,
            start=1
        ):

            title = step.get(
                "title",
                f"Step {index}"
            )

            explanation = step.get(
                "explanation",
                ""
            )

            math_text = step.get(
                "math",
                ""
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"""
                    <div style="
                        display:inline-block;
                        padding:6px 12px;
                        margin-bottom:10px;
                        border-radius:999px;
                        background:rgba(59,130,246,0.12);
                        border:1px solid rgba(96,165,250,0.25);
                        color:#60a5fa;
                        font-size:0.78rem;
                        font-weight:800;
                        letter-spacing:0.08em;
                    ">
                        STEP {index}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"### {title}"
                )

                if explanation:

                    st.write(
                        explanation
                    )

                if math_text:

                    st.markdown(
                        "**Mathematics**"
                    )

                    render_math_block(
                        math_text
                    )

    if final_answer:

        st.markdown(
            "### ✅ Final Answer"
        )

        with st.container(
            border=True
        ):

            render_math_block(
                final_answer
            )

    if mistake_fix:

        st.markdown(
            "### 💡 What Changed?"
        )

        st.warning(
            mistake_fix
        )

    if steps:

        st.info(
            "🎯 **Takeaway:** Try to remember the reasoning pattern, "
            "not just the final formula."
        )


# =========================================================
# START HELP UI
# =========================================================

def render_start_help(
    starter
):

    st.divider()

    render_section_header(
        "Let's Get You Started",
        "You do not need to know the whole solution. Start with one idea."
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Topic",
            starter.topic
        )

    with col2:

        st.metric(
            "Subtopic",
            starter.subtopic
            or "—"
        )

    with col3:

        st.metric(
            "Difficulty",
            starter.difficulty
            or "—"
        )


    render_soft_card(
        "🧠 Concept You Need",
        starter.concept
    )


    render_soft_card(
        "👀 What to Recognize",
        starter.recognition
    )


    level = st.session_state[
        "start_help_level"
    ]


    render_section_header(
        f"Starter Hint {level}",
        "Use only as much help as you need."
    )


    if level == 1:

        hint_text = starter.hint_1
        hint_math = starter.hint_1_math

    elif level == 2:

        hint_text = starter.hint_2
        hint_math = starter.hint_2_math

    else:

        hint_text = starter.hint_3
        hint_math = starter.hint_3_math


    st.info(
        "💡 " + hint_text
    )


    if hint_math:

        with st.container(
            border=True
        ):

            st.caption(
                "Useful setup"
            )

            render_math_block(
                hint_math
            )


    if level < 3:

        if st.button(
            "💡 Give Me a Stronger Hint",
            use_container_width=True
        ):

            st.session_state[
                "start_help_level"
            ] += 1

            st.rerun()

    else:

        st.success(
            "You now have the main setup. Try continuing it yourself."
        )


    st.markdown(
        "### 🎯 Your Next Move"
    )

    st.write(
        starter.student_task
    )


    starter_attempt = st.text_area(
        "Now try solving the problem",
        placeholder=(
            "Write what you can do from here. "
            "It does not need to be perfect."
        ),
        height=190,
        key="starter_attempt_box"
    )


    if st.button(
        "🔍 Check What I Tried",
        type="primary",
        use_container_width=True
    ):

        if not starter_attempt.strip():

            st.warning(
                "Write what you can do first."
            )

        else:

            with st.spinner(
                "🧠 Checking your attempt..."
            ):

                try:

                    result = analyze_student_attempt(
                        st.session_state[
                            "current_question"
                        ],
                        starter_attempt
                    )

                    st.session_state[
                        "coach_result"
                    ] = result

                    st.session_state[
                        "attempt_number"
                    ] = 1

                    st.session_state[
                        "student_attempt"
                    ] = starter_attempt

                    st.session_state[
                        "start_help_result"
                    ] = None

                    st.session_state[
                        "start_help_level"
                    ] = 1


                    save_attempt(
                        question=
                            st.session_state[
                                "current_question"
                            ],

                        attempted_solution=
                            starter_attempt,

                        topic=
                            result.topic,

                        misconception_category=
                            result.misconception_category,

                        confidence=
                            result.confidence,

                        first_wrong_step=
                            result.first_wrong_step,

                        diagnosis=
                            result.diagnosis,

                        attempt_number=1,
                    )


                    if (
                        "starter_attempt_box"
                        in st.session_state
                    ):

                        del st.session_state[
                            "starter_attempt_box"
                        ]


                    st.rerun()

                except Exception as e:

                    st.error(
                        "The coach could not check your attempt."
                    )

                    st.code(
                        str(e)
                    )


# =========================================================
# HERO
# =========================================================

render_hero_section()

render_feature_cards()


# =========================================================
# INTRO
# =========================================================

render_section_header(
    "Try the AI Coach",
    "Enter a math problem. Try it yourself, or ask MindStep to help you begin."
)

render_highlight_banner(
    "Already tried? <b>Analyze your reasoning.</b> "
    "Completely stuck? Use <b>I Don't Know How to Start</b> "
    "and MindStep will guide you into the problem without immediately "
    "giving away the answer."
)


# =========================================================
# QUESTION INPUT
# =========================================================

render_section_header(
    "Your Math Problem",
    "Try algebra, calculus, trigonometry, logarithms, probability, matrices, "
    "coordinate geometry, and other Grade 11–12/JEE mathematics."
)


question = st.text_area(
    "Enter the math question",
    placeholder=(
        "Example: Differentiate y = (x^2 + 1)^5"
    ),
    height=110,
)


attempted_solution = st.text_area(
    "Show your attempted solution — leave this blank if you don't know how to start",
    placeholder=(
        "Example:\n"
        "dy/dx = 5(x^2 + 1)^4"
    ),
    height=190,
)


# =========================================================
# MAIN ACTION BUTTONS
# =========================================================

button_col1, button_col2 = st.columns(
    2
)


with button_col1:

    analyze_clicked = st.button(
        "✨ Analyze My Thinking",
        type="primary",
        use_container_width=True
    )


with button_col2:

    start_clicked = st.button(
        "🆘 I Don't Know How to Start",
        use_container_width=True
    )


# =========================================================
# ANALYZE STUDENT ATTEMPT
# =========================================================

if analyze_clicked:

    if not question.strip():

        st.warning(
            "Enter a math question first."
        )

    elif not attempted_solution.strip():

        st.warning(
            "Either write your attempted solution or use "
            "“I Don't Know How to Start”."
        )

    else:

        with st.spinner(
            "🧠 Checking your reasoning step by step..."
        ):

            try:

                result = analyze_student_attempt(
                    question,
                    attempted_solution
                )

                st.session_state[
                    "coach_result"
                ] = result

                st.session_state[
                    "attempt_number"
                ] = 1

                st.session_state[
                    "current_question"
                ] = question

                st.session_state[
                    "student_attempt"
                ] = attempted_solution

                st.session_state[
                    "start_help_result"
                ] = None

                st.session_state[
                    "start_help_level"
                ] = 1


                if "retry_box" in st.session_state:

                    del st.session_state[
                        "retry_box"
                    ]


                save_attempt(
                    question=question,

                    attempted_solution=
                        attempted_solution,

                    topic=
                        result.topic,

                    misconception_category=
                        result.misconception_category,

                    confidence=
                        result.confidence,

                    first_wrong_step=
                        result.first_wrong_step,

                    diagnosis=
                        result.diagnosis,

                    attempt_number=1,
                )


                st.rerun()

            except Exception as e:

                st.error(
                    "The coach could not analyze this attempt."
                )

                st.code(
                    str(e)
                )


# =========================================================
# I DON'T KNOW HOW TO START
# =========================================================

if start_clicked:

    if not question.strip():

        st.warning(
            "Enter the math question first."
        )

    else:

        with st.spinner(
            "🧭 Finding the best way to help you begin..."
        ):

            try:

                starter = get_starting_help(
                    question
                )

                st.session_state[
                    "start_help_result"
                ] = starter

                st.session_state[
                    "start_help_level"
                ] = 1

                st.session_state[
                    "current_question"
                ] = question

                st.session_state[
                    "coach_result"
                ] = None

                if (
                    "starter_attempt_box"
                    in st.session_state
                ):

                    del st.session_state[
                        "starter_attempt_box"
                    ]


                st.rerun()

            except Exception as e:

                st.error(
                    "MindStep could not create a starter hint."
                )

                st.code(
                    str(e)
                )


# =========================================================
# STARTER HELP DISPLAY
# =========================================================

starter = st.session_state.get(
    "start_help_result"
)


if (
    starter is not None
    and
    st.session_state.get(
        "coach_result"
    ) is None
):

    render_start_help(
        starter
    )


# =========================================================
# NORMAL COACH FEEDBACK
# =========================================================

result = st.session_state.get(
    "coach_result"
)


if result is not None:

    st.divider()

    render_section_header(
        "Coach Feedback",
        "Here's what the AI found in your reasoning."
    )


    attempt_number = st.session_state[
        "attempt_number"
    ]


    feedback = get_visible_feedback(
        result,
        attempt_number
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.metric(
            "Topic",
            result.topic
        )


    with col2:

        st.metric(
            "Subtopic",
            result.subtopic
            or "—"
        )


    with col3:

        st.metric(
            "Difficulty",
            result.difficulty
            or "—"
        )


    with col4:

        st.metric(
            "AI Confidence",
            f"{round(result.confidence * 100)}%"
        )


    # =====================================================
    # DIAGNOSIS
    # =====================================================

    if result.student_is_correct:

        render_soft_card(
            "✅ Reasoning Status",
            "The coach did not detect a mathematical misconception "
            "in your latest attempt."
        )

    else:

        render_soft_card(
            "🧩 Likely Misconception",
            (
                f"<b>"
                f"{readable_category(result.misconception_category)}"
                f"</b>"
                f"<br><br>"
                f"{result.diagnosis}"
            )
        )


    render_reasoning_steps(
        result
    )


    # =====================================================
    # FIRST WRONG STEP
    # =====================================================

    if (
        result.first_wrong_step
        and
        not result.student_is_correct
    ):

        st.markdown(
            "### 🎯 First Step Worth Checking"
        )

        render_math_block(
            result.first_wrong_step
        )


    # =====================================================
    # SOLVED
    # =====================================================

    if feedback[
        "solved"
    ]:

        st.success(
            "🎉 Nice recovery! Your latest reasoning is mathematically correct."
        )


        render_soft_card(
            "✅ Nice Recovery",
            "You repaired the earlier mistake. "
            "Now the coach will organize the correct method into a clean explanation."
        )


        with st.expander(
            "📚 See why your solution works",
            expanded=True
        ):

            render_solution_walkthrough(
                result
            )


        if st.button(
            "➕ Start a New Problem",
            type="primary",
            use_container_width=True
        ):

            reset_problem()

            st.rerun()


    # =====================================================
    # STILL NEEDS HELP
    # =====================================================

    else:

        st.divider()

        render_section_header(
            feedback[
                "level"
            ],
            "Use the hint to repair your reasoning before seeing the complete solution."
        )


        if feedback[
            "hint"
        ]:

            st.info(
                "💡 "
                + feedback[
                    "hint"
                ]
            )


        # =================================================
        # RETRY
        # =================================================

        if not feedback[
            "show_full_explanation"
        ]:

            render_section_header(
                "Try Again",
                "Change the part of your reasoning that the hint points toward."
            )


            retry_text = st.text_area(
                "Write your improved solution",
                placeholder=(
                    "Write your corrected reasoning here..."
                ),
                height=190,
                key="retry_box"
            )


            if st.button(
                "🔁 Check My Retry",
                type="primary",
                use_container_width=True
            ):

                if not retry_text.strip():

                    st.warning(
                        "Write your improved attempt first."
                    )

                else:

                    new_attempt_number = (
                        attempt_number
                        + 1
                    )

                    with st.spinner(
                        "🧠 Checking your new reasoning..."
                    ):

                        try:

                            new_result = (
                                analyze_student_attempt(
                                    st.session_state[
                                        "current_question"
                                    ],
                                    retry_text
                                )
                            )


                            st.session_state[
                                "coach_result"
                            ] = new_result


                            st.session_state[
                                "attempt_number"
                            ] = new_attempt_number


                            st.session_state[
                                "student_attempt"
                            ] = retry_text


                            save_attempt(
                                question=
                                    st.session_state[
                                        "current_question"
                                    ],

                                attempted_solution=
                                    retry_text,

                                topic=
                                    new_result.topic,

                                misconception_category=
                                    new_result
                                    .misconception_category,

                                confidence=
                                    new_result.confidence,

                                first_wrong_step=
                                    new_result
                                    .first_wrong_step,

                                diagnosis=
                                    new_result.diagnosis,

                                attempt_number=
                                    new_attempt_number,
                            )


                            if (
                                "retry_box"
                                in st.session_state
                            ):

                                del st.session_state[
                                    "retry_box"
                                ]


                            st.rerun()

                        except Exception as e:

                            st.error(
                                "The coach could not analyze your retry."
                            )

                            st.code(
                                str(e)
                            )


        # =================================================
        # FULL EXPLANATION
        # =================================================

        else:

            st.divider()

            render_section_header(
                "Full Explanation",
                "You've worked through several hints, so the complete reasoning is now unlocked."
            )


            render_solution_walkthrough(
                result
            )


            if st.button(
                "➕ Start a New Problem",
                type="primary",
                use_container_width=True
            ):

                reset_problem()

                st.rerun()


# =========================================================
# HISTORY
# =========================================================

st.divider()

render_section_header(
    "Recent Learning History",
    "Your recent attempts help the coach identify recurring reasoning patterns."
)


attempts = get_all_attempts()


if not attempts:

    render_soft_card(
        "🌱 Your Learning Journey Starts Here",
        "Solve a few problems and your learning history will begin appearing here."
    )

else:

    recent_attempts = attempts[
        :5
    ]


    for row in recent_attempts:

        (
            attempt_id,
            timestamp,
            saved_question,
            saved_solution,
            topic,
            misconception,
            confidence,
            first_wrong_step,
            diagnosis,
            saved_attempt_number,
        ) = row


        if misconception == "no_clear_error":

            icon = "✅"

            readable_misconception = (
                "Correct Attempt"
            )

        else:

            icon = "🧩"

            readable_misconception = (
                readable_category(
                    misconception
                )
            )


        with st.expander(
            f"{icon} {topic} — {readable_misconception}"
        ):

            col1, col2 = st.columns(
                2
            )


            with col1:

                st.write(
                    f"**Attempt:** "
                    f"{saved_attempt_number}"
                )


            with col2:

                st.write(
                    f"**AI Confidence:** "
                    f"{round(confidence * 100)}%"
                )


            st.markdown(
                "**Question**"
            )

            st.write(
                saved_question
            )


            st.markdown(
                "**Your reasoning**"
            )

            st.code(
                saved_solution,
                language="text"
            )


            st.markdown(
                "**Coach diagnosis**"
            )

            st.write(
                diagnosis
            )


            if first_wrong_step:

                st.markdown(
                    "**First step worth checking**"
                )

                st.code(
                    first_wrong_step,
                    language="text"
                )


            st.caption(
                f"Saved: {timestamp}"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        padding:24px 0 10px 0;
        font-size:0.9rem;
    ">
        Understand the mistake. Repair the reasoning. Build mastery.
    </div>
    """,
    unsafe_allow_html=True
)