import json
import os
import subprocess
import sys

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

from ui_styles import (
    apply_global_styles,
    render_section_header,
    render_highlight_banner,
    render_soft_card,
)


# =========================================================
# PAGE SETUP
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="Chapter Learning",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


# =========================================================
# GEMINI SETUP
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Gemini API key not found. Please check your .env file."
    )
    st.stop()

client = genai.Client(
    api_key=api_key
)

MODEL_NAME = "gemini-3.5-flash-lite"


# =========================================================
# HERO
# =========================================================

chapter_hero = (
    '<div class="hero-card">'
    '<div class="hero-badge">📚 AI Chapter Learning</div>'

    '<div class="hero-title">'
    'Turn a chapter into a '
    '<span class="gradient-text">personal learning experience</span>.'
    '</div>'

    '<div class="hero-subtitle">'
    'Upload your study material, discover the important concepts, '
    'learn them step by step, practise with AI-generated questions, '
    'and turn difficult ideas into visual lessons.'
    '</div>'

    '<div class="hero-pills">'
    '<div class="hero-pill">📄 Upload a chapter</div>'
    '<div class="hero-pill">🧠 Find key concepts</div>'
    '<div class="hero-pill">💡 Learn step by step</div>'
    '<div class="hero-pill">🎯 Practise</div>'
    '<div class="hero-pill">🎬 Create visual lessons</div>'
    '</div>'

    '</div>'
)

st.markdown(
    chapter_hero,
    unsafe_allow_html=True
)

render_highlight_banner(
    "Upload a chapter and let the AI turn it into concepts, explanations, "
    "practice questions, and visual learning material."
)


# =========================================================
# SCHEMAS
# =========================================================

chapter_schema = {
    "type": "object",
    "properties": {
        "chapter_title": {
            "type": "string"
        },
        "chapter_summary": {
            "type": "string"
        },
        "what_you_will_learn": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "important_for_jee": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "jee_importance": {
                        "type": "string"
                    },
                    "formulas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "latex": {
                                    "type": "string"
                                },
                                "meaning": {
                                    "type": "string"
                                },
                                "variables": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                            "required": [
                                "latex",
                                "meaning",
                                "variables"
                            ]
                        }
                    },
                    "subconcepts": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "id",
                    "name",
                    "explanation",
                    "jee_importance",
                    "formulas",
                    "subconcepts"
                ]
            }
        }
    },
    "required": [
        "chapter_title",
        "chapter_summary",
        "what_you_will_learn",
        "important_for_jee",
        "concepts"
    ]
}


lesson_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "intuition": {
            "type": "string"
        },
        "step_by_step": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "why_formula_works": {
            "type": "string"
        },
        "worked_example": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string"
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "answer": {
                    "type": "string"
                }
            },
            "required": [
                "question",
                "steps",
                "answer"
            ]
        },
        "common_mistake": {
            "type": "string"
        },
        "jee_trap": {
            "type": "string"
        },
        "quick_check": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string"
                },
                "options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "correct_answer": {
                    "type": "string"
                },
                "explanation": {
                    "type": "string"
                }
            },
            "required": [
                "question",
                "options",
                "correct_answer",
                "explanation"
            ]
        }
    },
    "required": [
        "title",
        "intuition",
        "step_by_step",
        "why_formula_works",
        "worked_example",
        "common_mistake",
        "jee_trap",
        "quick_check"
    ]
}


practice_schema = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string"
        },
        "options": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "correct_answer": {
            "type": "string"
        },
        "explanation": {
            "type": "string"
        },
        "difficulty": {
            "type": "string"
        },
        "skill_tested": {
            "type": "string"
        }
    },
    "required": [
        "question",
        "options",
        "correct_answer",
        "explanation",
        "difficulty",
        "skill_tested"
    ]
}


storyboard_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "learning_goal": {
            "type": "string"
        },
        "estimated_duration_seconds": {
            "type": "integer"
        },
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_number": {
                        "type": "integer"
                    },
                    "scene_title": {
                        "type": "string"
                    },
                    "visual": {
                        "type": "string"
                    },
                    "animation": {
                        "type": "string"
                    },
                    "narration": {
                        "type": "string"
                    },
                    "formula_latex": {
                        "type": "string"
                    },
                    "student_focus": {
                        "type": "string"
                    },
                    "duration_seconds": {
                        "type": "integer"
                    }
                },
                "required": [
                    "scene_number",
                    "scene_title",
                    "visual",
                    "animation",
                    "narration",
                    "formula_latex",
                    "student_focus",
                    "duration_seconds"
                ]
            }
        }
    },
    "required": [
        "title",
        "learning_goal",
        "estimated_duration_seconds",
        "scenes"
    ]
}


# =========================================================
# SESSION STATE
# =========================================================

if "practice_correct" not in st.session_state:
    st.session_state["practice_correct"] = 0

if "practice_total" not in st.session_state:
    st.session_state["practice_total"] = 0

if "practice_question" not in st.session_state:
    st.session_state["practice_question"] = None

if "practice_answered" not in st.session_state:
    st.session_state["practice_answered"] = False


# =========================================================
# HELPERS
# =========================================================

def split_text(
    text,
    chunk_size=8000
):
    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):
        chunks.append(
            text[
                i:
                i + chunk_size
            ]
        )

    return chunks


def reset_practice():
    st.session_state[
        "practice_correct"
    ] = 0

    st.session_state[
        "practice_total"
    ] = 0

    st.session_state[
        "practice_question"
    ] = None

    st.session_state[
        "practice_answered"
    ] = False


def render_storyboard_video(
    storyboard
):
    generated_folder = Path(
        "generated"
    )

    generated_folder.mkdir(
        exist_ok=True
    )

    storyboard_file = (
        generated_folder
        / "storyboard.json"
    )

    media_folder = (
        generated_folder
        / "media"
    )

    with open(
        storyboard_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            storyboard,
            file,
            ensure_ascii=False,
            indent=2
        )

    environment = os.environ.copy()

    environment[
        "STORYBOARD_JSON"
    ] = str(
        storyboard_file.resolve()
    )

    command = [
        sys.executable,
        "-m",
        "manim",
        "-ql",
        "--format=mp4",
        "--media_dir",
        str(
            media_folder.resolve()
        ),
        "animation_renderer.py",
        "StoryboardAnimation"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=environment,
        timeout=300
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr[-5000:]
            or
            result.stdout[-5000:]
        )

    video_files = list(
        media_folder.rglob(
            "StoryboardAnimation.mp4"
        )
    )

    if not video_files:
        raise RuntimeError(
            "Manim finished but the video file was not found."
        )

    latest_video = max(
        video_files,
        key=lambda path:
            path.stat().st_mtime
    )

    return latest_video


# =========================================================
# UPLOAD
# =========================================================

st.divider()

render_section_header(
    "Upload Your Study Material",
    "Start with a Physics chapter or notes PDF."
)

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=[
        "pdf"
    ]
)


# =========================================================
# READ PDF
# =========================================================

if uploaded_file is not None:

    try:
        reader = PdfReader(
            uploaded_file
        )

        extracted_text = ""

        for page in reader.pages:
            page_text = (
                page.extract_text()
            )

            if page_text:
                extracted_text += (
                    page_text
                    + "\n"
                )

        st.success(
            f"✅ PDF loaded successfully — "
            f"{len(reader.pages)} pages"
        )

    except Exception as e:
        st.error(
            "Could not read the PDF."
        )

        st.caption(
            str(e)
        )

        st.stop()


    # =====================================================
    # DOCUMENT INFO
    # =====================================================

    word_count = len(
        extracted_text.split()
    )

    character_count = len(
        extracted_text
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        st.metric(
            "Pages",
            len(reader.pages)
        )

    with col2:
        st.metric(
            "Words",
            f"{word_count:,}"
        )

    with col3:
        st.metric(
            "Characters",
            f"{character_count:,}"
        )


    with st.expander(
        "📄 View Extracted Text"
    ):
        st.text_area(
            "PDF Content",
            extracted_text,
            height=300
        )


    # =====================================================
    # ANALYZE CHAPTER
    # =====================================================

    st.divider()

    render_section_header(
        "Analyze the Chapter",
        "The AI will break the chapter into teachable concepts and identify important JEE areas."
    )

    if st.button(
        "✨ Analyze Full Chapter",
        type="primary",
        use_container_width=True
    ):

        chunks = split_text(
            extracted_text
        )

        st.info(
            f"The chapter will be analyzed in "
            f"{len(chunks)} sections."
        )

        progress_bar = st.progress(
            0
        )

        all_results = []

        for index, chunk in enumerate(
            chunks
        ):
            st.write(
                f"Analyzing section "
                f"{index + 1} of "
                f"{len(chunks)}..."
            )

            chunk_prompt = f"""
You are an expert JEE Main Physics teacher.

Read this section of a Physics chapter carefully.

Identify all important teachable concepts.

For every concept identify:

- concept name
- simple explanation
- important formulas
- important sub-concepts
- JEE Main relevance

IMPORTANT:

- Do not over-summarize.
- Capture individual concepts.
- Capture important sub-concepts.
- Preserve formulas.
- Do not invent information.
- Focus only on material actually present.

CHAPTER SECTION:

{chunk}
"""

            try:
                response = (
                    client.models.generate_content(
                        model=MODEL_NAME,
                        contents=chunk_prompt
                    )
                )

                all_results.append(
                    response.text
                )

            except Exception as e:
                st.warning(
                    f"Section {index + 1} "
                    f"could not be analyzed."
                )

                st.caption(
                    str(e)
                )

            progress_bar.progress(
                (
                    index + 1
                )
                /
                len(chunks)
            )


        combined_results = (
            "\n\n".join(
                all_results
            )
        )

        if not combined_results:
            st.error(
                "No chapter analysis was generated."
            )
            st.stop()


        with st.spinner(
            "Creating your chapter learning map..."
        ):

            final_prompt = f"""
You are an expert JEE Main Physics teacher.

Below are concept analyses from different sections
of the SAME Physics chapter.

Create one complete student-friendly chapter learning map.

Include:

- chapter title
- simple chapter summary
- what the student will learn
- most important JEE Main areas
- all important concepts in logical order

For every concept include:

- simple explanation
- JEE Main importance
- important formulas
- meaning of each formula
- explanation of variables
- related sub-concepts

FORMULA RULES:

- Use valid LaTeX.
- Do not compress formulas.
- Explain every formula.
- Explain every important symbol.

Use simple student-friendly language.

Remove duplicates but keep important concepts.

Do not invent material that is not in the chapter.

CHAPTER ANALYSIS:

{combined_results}
"""

            try:
                final_response = (
                    client.models.generate_content(
                        model=MODEL_NAME,
                        contents=final_prompt,
                        config={
                            "response_mime_type":
                                "application/json",
                            "response_schema":
                                chapter_schema
                        }
                    )
                )

                chapter_data = (
                    json.loads(
                        final_response.text
                    )
                )

                st.session_state[
                    "chapter_data"
                ] = chapter_data

                st.session_state.pop(
                    "lesson_data",
                    None
                )

                st.session_state.pop(
                    "storyboard_data",
                    None
                )

                st.session_state.pop(
                    "animation_video",
                    None
                )

                reset_practice()

                st.success(
                    "🎉 Chapter analysis completed."
                )

            except Exception as e:
                st.error(
                    "Could not create the structured chapter."
                )

                st.caption(
                    str(e)
                )


# =========================================================
# CHAPTER DISPLAY
# =========================================================

if "chapter_data" in st.session_state:

    chapter_data = st.session_state[
        "chapter_data"
    ]

    st.divider()

    render_section_header(
        chapter_data.get(
            "chapter_title",
            "Chapter Overview"
        ),
        "Your AI-generated learning map for this chapter."
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    render_soft_card(
        "📖 Chapter Summary",
        chapter_data.get(
            "chapter_summary",
            ""
        )
    )


    # =====================================================
    # LEARNING GOALS
    # =====================================================

    col1, col2 = st.columns(
        2
    )

    with col1:
        st.markdown(
            "### 🎯 What You Will Learn"
        )

        for item in chapter_data.get(
            "what_you_will_learn",
            []
        ):
            st.write(
                f"• {item}"
            )


    with col2:
        st.markdown(
            "### 🔥 Important for JEE Main"
        )

        for item in chapter_data.get(
            "important_for_jee",
            []
        ):
            st.write(
                f"• {item}"
            )


    # =====================================================
    # CONCEPTS
    # =====================================================

    concepts = chapter_data.get(
        "concepts",
        []
    )

    st.divider()

    render_section_header(
        f"Chapter Concepts ({len(concepts)})",
        "Choose a concept and learn it in depth."
    )


    for concept in concepts:
        with st.expander(
            f"{concept.get('id')}. "
            f"{concept.get('name')}"
        ):
            st.write(
                concept.get(
                    "explanation",
                    ""
                )
            )

            st.caption(
                "JEE importance: "
                + concept.get(
                    "jee_importance",
                    ""
                )
            )


    # =====================================================
    # SELECT CONCEPT
    # =====================================================

    if concepts:

        st.divider()

        render_section_header(
            "Choose a Concept",
            "Pick one concept to explore, practise, and visualize."
        )

        concept_names = [
            concept.get(
                "name",
                "Unnamed Concept"
            )
            for concept in concepts
        ]

        selected_name = st.selectbox(
            "Select a concept",
            concept_names
        )

        selected_concept = next(
            (
                concept
                for concept in concepts
                if concept.get(
                    "name"
                )
                == selected_name
            ),
            None
        )


        old_concept = (
            st.session_state.get(
                "selected_concept_name"
            )
        )

        if old_concept != selected_name:

            st.session_state[
                "selected_concept_name"
            ] = selected_name

            st.session_state.pop(
                "lesson_data",
                None
            )

            st.session_state.pop(
                "storyboard_data",
                None
            )

            st.session_state.pop(
                "animation_video",
                None
            )

            reset_practice()


        # =================================================
        # SELECTED CONCEPT
        # =================================================

        if selected_concept:

            st.divider()

            render_section_header(
                selected_concept.get(
                    "name",
                    ""
                ),
                "Understand the idea before memorizing the formula."
            )

            render_soft_card(
                "💡 Simple Explanation",
                selected_concept.get(
                    "explanation",
                    ""
                )
            )

            st.info(
                "🎯 JEE Main Importance: "
                + selected_concept.get(
                    "jee_importance",
                    ""
                )
            )


            # =============================================
            # FORMULAS
            # =============================================

            formulas = (
                selected_concept.get(
                    "formulas",
                    []
                )
            )

            if formulas:

                st.markdown(
                    "### 🧮 Important Formulas"
                )

                for number, formula in enumerate(
                    formulas,
                    start=1
                ):

                    with st.expander(
                        f"Formula {number}"
                    ):

                        latex_formula = (
                            formula.get(
                                "latex",
                                ""
                            )
                        )

                        if latex_formula:

                            try:
                                st.latex(
                                    latex_formula
                                )

                            except Exception:
                                st.write(
                                    latex_formula
                                )


                        meaning = formula.get(
                            "meaning",
                            ""
                        )

                        if meaning:
                            st.write(
                                "**What it means:**"
                            )

                            st.write(
                                meaning
                            )


                        variables = (
                            formula.get(
                                "variables",
                                []
                            )
                        )

                        if variables:
                            st.write(
                                "**Symbols:**"
                            )

                            for variable in variables:
                                st.write(
                                    f"• {variable}"
                                )


            # =============================================
            # SUBCONCEPTS
            # =============================================

            subconcepts = (
                selected_concept.get(
                    "subconcepts",
                    []
                )
            )

            if subconcepts:

                st.markdown(
                    "### 🔗 Related Ideas"
                )

                for item in subconcepts:
                    st.write(
                        f"• {item}"
                    )


            # =============================================
            # LEARN
            # =============================================

            st.divider()

            render_section_header(
                "Learn This Concept",
                "Generate a guided lesson with intuition, reasoning, examples, and common traps."
            )

            if st.button(
                "🧠 Learn This Concept",
                type="primary",
                use_container_width=True
            ):

                lesson_prompt = f"""
You are an excellent JEE Main Physics teacher.

Teach this concept to a student seeing it
for the first time.

CONCEPT:

{selected_concept.get("name")}

EXPLANATION:

{selected_concept.get("explanation")}

SUB-CONCEPTS:

{selected_concept.get("subconcepts")}

FORMULAS:

{selected_concept.get("formulas")}

Create:

1. Intuition

2. Step-by-step explanation

3. Why the formula makes sense

4. One worked JEE-style example

5. One common student mistake

6. One JEE Main trap

7. One multiple-choice quick check


WORKED EXAMPLE RULES:

- Use a clear example.
- Show solution step by step.


QUICK CHECK RULES:

- Must NOT be the same as worked example.
- Do NOT reuse same numbers.
- Test a different aspect.
- Prefer conceptual understanding.
- Use a common misconception if possible.
- Use four realistic options.
- Only one option should be correct.

Use simple language.

Do not skip reasoning.

Do not invent formulas.
"""

                with st.spinner(
                    "Creating your lesson..."
                ):

                    try:
                        lesson_response = (
                            client.models.generate_content(
                                model=MODEL_NAME,
                                contents=lesson_prompt,
                                config={
                                    "response_mime_type":
                                        "application/json",
                                    "response_schema":
                                        lesson_schema
                                }
                            )
                        )

                        lesson_data = (
                            json.loads(
                                lesson_response.text
                            )
                        )

                        st.session_state[
                            "lesson_data"
                        ] = lesson_data

                        st.session_state.pop(
                            "storyboard_data",
                            None
                        )

                        st.session_state.pop(
                            "animation_video",
                            None
                        )

                        reset_practice()

                        st.rerun()

                    except Exception as e:
                        st.error(
                            "Could not create the lesson."
                        )

                        st.caption(
                            str(e)
                        )


# =========================================================
# LESSON DISPLAY
# =========================================================

if st.session_state.get(
    "lesson_data"
):

    lesson = st.session_state[
        "lesson_data"
    ]

    st.divider()

    render_section_header(
        f"Learn: {lesson.get('title', '')}",
        "A deeper lesson designed to build understanding before memorization."
    )


    # =====================================================
    # INTUITION
    # =====================================================

    render_soft_card(
        "💡 Intuition",
        lesson.get(
            "intuition",
            ""
        )
    )


    # =====================================================
    # STEP BY STEP
    # =====================================================

    st.markdown(
        "### 🧭 Step-by-Step"
    )

    for number, step in enumerate(
        lesson.get(
            "step_by_step",
            []
        ),
        start=1
    ):
        st.write(
            f"**Step {number}:** {step}"
        )


    # =====================================================
    # WHY FORMULA WORKS
    # =====================================================

    render_soft_card(
        "🧠 Why the Formula Works",
        lesson.get(
            "why_formula_works",
            ""
        )
    )


    # =====================================================
    # WORKED EXAMPLE
    # =====================================================

    example = lesson.get(
        "worked_example",
        {}
    )

    if example:

        st.markdown(
            "### ✏️ Worked Example"
        )

        st.write(
            "**Question**"
        )

        st.write(
            example.get(
                "question",
                ""
            )
        )

        st.write(
            "**Solution**"
        )

        for number, step in enumerate(
            example.get(
                "steps",
                []
            ),
            start=1
        ):
            st.write(
                f"{number}. {step}"
            )

        st.success(
            "Answer: "
            + example.get(
                "answer",
                ""
            )
        )


    # =====================================================
    # MISTAKE + TRAP
    # =====================================================

    col1, col2 = st.columns(
        2
    )

    with col1:
        st.warning(
            "⚠️ Common Mistake\n\n"
            + lesson.get(
                "common_mistake",
                ""
            )
        )

    with col2:
        st.info(
            "🎯 JEE Trap\n\n"
            + lesson.get(
                "jee_trap",
                ""
            )
        )


    # =====================================================
    # INITIAL PRACTICE QUESTION
    # =====================================================

    if st.session_state[
        "practice_question"
    ] is None:

        st.session_state[
            "practice_question"
        ] = lesson.get(
            "quick_check"
        )

        st.session_state[
            "practice_answered"
        ] = False


    # =====================================================
    # ANIMATION STORYBOARD
    # =====================================================

    st.divider()

    render_section_header(
        "Animated Learning",
        "Turn the concept into a short visual teaching sequence."
    )

    if st.button(
        "🎬 Generate Animation Storyboard",
        use_container_width=True
    ):

        selected_name = (
            st.session_state.get(
                "selected_concept_name",
                ""
            )
        )

        storyboard_prompt = f"""
You are designing a short animated JEE Main Physics lesson.

CONCEPT:

{selected_name}

LESSON:

{json.dumps(
    lesson,
    ensure_ascii=False
)}

Create a visual storyboard for a 60 to 120 second
educational animation.

Use 5 to 8 scenes.

For every scene specify:

- scene number
- short scene title
- what appears visually
- what should move or animate
- narration
- formula in LaTeX if needed
- what student should focus on
- duration in seconds

VERY IMPORTANT:

- Do not create a talking-head lecture.
- Teach visually.
- Prefer charges, particles, arrows,
  graphs, fields, motion, geometry,
  capacitor plates and equations.
- Introduce intuition before formulas.
- Do not show too much text.
- Build the concept progressively.
- Keep the physics correct.
- Do not invent formulas.
"""

        with st.spinner(
            "Designing animation..."
        ):

            try:
                storyboard_response = (
                    client.models.generate_content(
                        model=MODEL_NAME,
                        contents=storyboard_prompt,
                        config={
                            "response_mime_type":
                                "application/json",
                            "response_schema":
                                storyboard_schema
                        }
                    )
                )

                storyboard_data = (
                    json.loads(
                        storyboard_response.text
                    )
                )

                st.session_state[
                    "storyboard_data"
                ] = storyboard_data

                st.session_state.pop(
                    "animation_video",
                    None
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "Could not create storyboard."
                )

                st.caption(
                    str(e)
                )


    # =====================================================
    # PRACTICE MODE
    # =====================================================

    st.divider()

    render_section_header(
        "Practice Mode",
        "Check whether you can apply the concept without looking back at the lesson."
    )


    correct = st.session_state[
        "practice_correct"
    ]

    total = st.session_state[
        "practice_total"
    ]

    if total > 0:
        accuracy = round(
            (
                correct
                / total
            )
            * 100
        )
    else:
        accuracy = 0


    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        st.metric(
            "Correct",
            correct
        )

    with col2:
        st.metric(
            "Questions Attempted",
            total
        )

    with col3:
        st.metric(
            "Accuracy",
            f"{accuracy}%"
        )


    if total == 0:
        st.info(
            "Answer your first question to start tracking your score."
        )

    elif accuracy >= 80:
        st.success(
            "🏆 Strong understanding"
        )

    elif accuracy >= 50:
        st.warning(
            "📈 Getting there — keep practising"
        )

    else:
        st.error(
            "🎯 This concept needs more revision"
        )


    question_data = (
        st.session_state[
            "practice_question"
        ]
    )

    if question_data:

        st.markdown(
            "### Practice Question"
        )

        difficulty = (
            question_data.get(
                "difficulty"
            )
        )

        skill_tested = (
            question_data.get(
                "skill_tested"
            )
        )

        if difficulty:
            st.caption(
                f"Difficulty: {difficulty}"
            )

        if skill_tested:
            st.caption(
                f"Skill tested: {skill_tested}"
            )


        st.write(
            question_data.get(
                "question",
                ""
            )
        )


        options = (
            question_data.get(
                "options",
                []
            )
        )

        selected_answer = st.radio(
            "Choose your answer",
            options,
            index=None,
            key="practice_radio"
        )


        if not st.session_state[
            "practice_answered"
        ]:

            if st.button(
                "✅ Check Practice Answer",
                use_container_width=True
            ):

                if selected_answer is None:
                    st.warning(
                        "Choose an answer first."
                    )

                else:
                    st.session_state[
                        "practice_total"
                    ] += 1

                    correct_answer = (
                        question_data.get(
                            "correct_answer",
                            ""
                        )
                    )

                    if (
                        selected_answer
                        ==
                        correct_answer
                    ):
                        st.session_state[
                            "practice_correct"
                        ] += 1

                        st.success(
                            "🎉 Correct!"
                        )

                    else:
                        st.error(
                            "Not quite. "
                            f"Correct answer: "
                            f"{correct_answer}"
                        )

                    st.write(
                        question_data.get(
                            "explanation",
                            ""
                        )
                    )

                    st.session_state[
                        "practice_answered"
                    ] = True


        if st.session_state[
            "practice_answered"
        ]:

            if st.button(
                "🔁 Generate Another Question",
                use_container_width=True
            ):

                selected_name = (
                    st.session_state.get(
                        "selected_concept_name",
                        ""
                    )
                )

                previous_question = (
                    question_data.get(
                        "question",
                        ""
                    )
                )

                practice_prompt = f"""
You are a JEE Main Physics question setter.

Create ONE fresh multiple-choice practice question.

CONCEPT:

{selected_name}

PREVIOUS QUESTION:

{previous_question}

Requirements:

- Do NOT repeat previous question.
- Do NOT reuse exact same numbers.
- Test a different sub-concept.
- Use four realistic options.
- Only one correct answer.
- Suitable for JEE Main.
- Prefer conceptual understanding.
- Difficulty:
  Easy, Medium, or Hard.
- Explain why correct answer is right.
"""

                with st.spinner(
                    "Generating another question..."
                ):

                    try:
                        practice_response = (
                            client.models.generate_content(
                                model=MODEL_NAME,
                                contents=practice_prompt,
                                config={
                                    "response_mime_type":
                                        "application/json",
                                    "response_schema":
                                        practice_schema
                                }
                            )
                        )

                        new_question = (
                            json.loads(
                                practice_response.text
                            )
                        )

                        st.session_state[
                            "practice_question"
                        ] = new_question

                        st.session_state[
                            "practice_answered"
                        ] = False

                        st.rerun()

                    except Exception as e:
                        st.error(
                            "Could not generate another question."
                        )

                        st.caption(
                            str(e)
                        )


    if st.button(
        "Reset Practice Score"
    ):
        reset_practice()
        st.rerun()


# =========================================================
# STORYBOARD
# =========================================================

if st.session_state.get(
    "storyboard_data"
):

    storyboard = (
        st.session_state[
            "storyboard_data"
        ]
    )

    st.divider()

    render_section_header(
        "Animation Storyboard",
        "A scene-by-scene plan for visually teaching this concept."
    )

    render_soft_card(
        "🎬 " + storyboard.get(
            "title",
            ""
        ),
        storyboard.get(
            "learning_goal",
            ""
        )
    )

    st.caption(
        "Estimated duration: "
        f"{storyboard.get('estimated_duration_seconds', 0)} seconds"
    )


    scenes = storyboard.get(
        "scenes",
        []
    )


    for scene in scenes:

        with st.expander(
            f"🎞️ Scene "
            f"{scene.get('scene_number')}: "
            f"{scene.get('scene_title')}"
        ):

            st.markdown(
                "**Visual**"
            )

            st.write(
                scene.get(
                    "visual",
                    ""
                )
            )

            st.markdown(
                "**Animation**"
            )

            st.write(
                scene.get(
                    "animation",
                    ""
                )
            )

            st.markdown(
                "**Narration**"
            )

            st.write(
                scene.get(
                    "narration",
                    ""
                )
            )


            formula = (
                scene.get(
                    "formula_latex",
                    ""
                )
            )

            if formula:
                st.markdown(
                    "**Formula**"
                )

                try:
                    st.latex(
                        formula
                    )

                except Exception:
                    st.write(
                        formula
                    )


            st.markdown(
                "**Student Focus**"
            )

            st.write(
                scene.get(
                    "student_focus",
                    ""
                )
            )

            st.caption(
                f"Duration: "
                f"{scene.get('duration_seconds', 0)} seconds"
            )


    # =====================================================
    # RENDER VIDEO
    # =====================================================

    st.divider()

    render_section_header(
        "Create the Animation",
        "Turn the storyboard into a real MP4 using Manim."
    )

    if st.button(
        "🎥 Render Animation Video",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Rendering animation..."
        ):

            try:
                video_path = (
                    render_storyboard_video(
                        storyboard
                    )
                )

                st.session_state[
                    "animation_video"
                ] = str(
                    video_path
                )

                st.success(
                    "🎉 Animation created!"
                )

            except Exception as e:
                st.error(
                    "Animation rendering failed."
                )

                st.code(
                    str(e)
                )


    video_path = (
        st.session_state.get(
            "animation_video"
        )
    )

    if video_path:

        video_file = Path(
            video_path
        )

        if video_file.exists():

            st.markdown(
                "### 🎬 Animated Lesson"
            )

            st.video(
                str(
                    video_file
                )
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
        padding:22px 0 8px 0;
        font-size:0.9rem;
    ">
        Learn the concept. Practise it. Visualize it. Master it.
    </div>
    """,
    unsafe_allow_html=True
)