import html

import pandas as pd
import streamlit as st

from storage import get_all_attempts
from analytics import calculate_dashboard_stats
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
    page_title="Progress Dashboard | MindStep",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


# =========================================================
# DASHBOARD-SPECIFIC STYLES
# =========================================================

st.markdown(
    """
    <style>

    .dashboard-kicker {
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

    .dashboard-hero {
        border:1px solid rgba(148,163,184,0.14);
        border-radius:28px;
        padding:40px 46px;
        margin-bottom:32px;
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

    .dashboard-title {
        color:#f8fafc;
        font-size:3.1rem;
        font-weight:900;
        line-height:1.05;
        letter-spacing:-0.04em;
        margin-bottom:18px;
    }

    .dashboard-gradient {
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

    .dashboard-subtitle {
        color:#aebbd0;
        font-size:1.08rem;
        line-height:1.8;
        max-width:850px;
    }

    .stat-card {
        min-height:155px;
        padding:22px;
        border-radius:20px;
        border:1px solid rgba(148,163,184,0.15);
        background:rgba(15,23,42,0.70);
        margin-bottom:10px;
    }

    .stat-label {
        color:#94a3b8;
        font-size:0.8rem;
        font-weight:700;
        text-transform:uppercase;
        letter-spacing:0.08em;
        margin-bottom:12px;
    }

    .stat-number {
        color:#f8fafc;
        font-size:2.15rem;
        font-weight:900;
        line-height:1;
        margin-bottom:10px;
    }

    .stat-note {
        color:#7f8ea3;
        font-size:0.82rem;
        line-height:1.45;
    }

    .insight-card {
        border:1px solid rgba(148,163,184,0.15);
        background:rgba(15,23,42,0.72);
        border-radius:22px;
        padding:24px;
        min-height:200px;
        margin-bottom:14px;
    }

    .insight-icon {
        font-size:1.55rem;
        margin-bottom:12px;
    }

    .insight-label {
        color:#60a5fa;
        font-size:0.76rem;
        font-weight:800;
        letter-spacing:0.09em;
        text-transform:uppercase;
        margin-bottom:8px;
    }

    .insight-title {
        color:#f8fafc;
        font-size:1.35rem;
        font-weight:800;
        margin-bottom:10px;
    }

    .insight-text {
        color:#aebbd0;
        font-size:0.95rem;
        line-height:1.65;
    }

    .topic-row {
        border:1px solid rgba(148,163,184,0.12);
        background:rgba(15,23,42,0.55);
        border-radius:16px;
        padding:15px 17px;
        margin-bottom:10px;
    }

    .topic-header {
        display:flex;
        justify-content:space-between;
        gap:20px;
        align-items:center;
        margin-bottom:8px;
    }

    .topic-name {
        color:#e2e8f0;
        font-weight:750;
        font-size:0.95rem;
    }

    .topic-rate {
        color:#94a3b8;
        font-size:0.82rem;
        font-weight:700;
    }

    .progress-track {
        width:100%;
        height:8px;
        background:rgba(148,163,184,0.13);
        border-radius:999px;
        overflow:hidden;
    }

    .progress-fill {
        height:100%;
        border-radius:999px;
        background:linear-gradient(
            90deg,
            #3b82f6,
            #8b5cf6
        );
    }

    .mini-rank {
        display:flex;
        align-items:center;
        gap:14px;
        border:1px solid rgba(148,163,184,0.12);
        background:rgba(15,23,42,0.55);
        border-radius:16px;
        padding:14px 16px;
        margin-bottom:10px;
    }

    .rank-number {
        width:34px;
        height:34px;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius:11px;
        background:rgba(59,130,246,0.12);
        color:#60a5fa;
        font-weight:900;
        flex-shrink:0;
    }

    .rank-title {
        color:#e2e8f0;
        font-size:0.92rem;
        font-weight:750;
    }

    .rank-subtitle {
        color:#7f8ea3;
        font-size:0.78rem;
        margin-top:2px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def readable_name(value):

    if not value:
        return "Unknown"

    if value == "no_clear_error":
        return "No Clear Error"

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def render_stat_card(
    label,
    number,
    note,
):

    card = (
        '<div class="stat-card">'
        f'<div class="stat-label">{html.escape(str(label))}</div>'
        f'<div class="stat-number">{html.escape(str(number))}</div>'
        f'<div class="stat-note">{html.escape(str(note))}</div>'
        '</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


def render_insight_card(
    icon,
    label,
    title,
    text,
):

    card = (
        '<div class="insight-card">'
        f'<div class="insight-icon">{icon}</div>'
        f'<div class="insight-label">{html.escape(str(label))}</div>'
        f'<div class="insight-title">{html.escape(str(title))}</div>'
        f'<div class="insight-text">{html.escape(str(text))}</div>'
        '</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


def render_topic_progress(
    topic,
    success_rate,
):

    success_rate = max(
        0,
        min(
            100,
            int(success_rate)
        )
    )

    card = (
        '<div class="topic-row">'
        '<div class="topic-header">'
        f'<div class="topic-name">{html.escape(str(topic))}</div>'
        f'<div class="topic-rate">{success_rate}% success</div>'
        '</div>'
        '<div class="progress-track">'
        f'<div class="progress-fill" style="width:{success_rate}%"></div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


def render_rank_item(
    rank,
    title,
    subtitle,
):

    card = (
        '<div class="mini-rank">'
        f'<div class="rank-number">{rank}</div>'
        '<div>'
        f'<div class="rank-title">{html.escape(str(title))}</div>'
        f'<div class="rank-subtitle">{html.escape(str(subtitle))}</div>'
        '</div>'
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
    '<div class="dashboard-hero">'
    '<div class="dashboard-kicker">📊 MINDSTEP · LEARNING ANALYTICS</div>'
    '<div class="dashboard-title">'
    'Turn every mistake into '
    '<span class="dashboard-gradient">progress.</span>'
    '</div>'
    '<div class="dashboard-subtitle">'
    'Your dashboard turns practice history into useful learning signals — '
    'what you understand, where your reasoning breaks, and what deserves '
    'your attention next.'
    '</div>'
    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATA
# =========================================================

attempts = get_all_attempts()

stats = calculate_dashboard_stats(
    attempts
)


# =========================================================
# EMPTY STATE
# =========================================================

if not attempts:

    render_soft_card(
        "🌱 Your dashboard is waiting for data",
        "Solve a few problems using the AI Coach first. "
        "Your success rate, misconception patterns, strong topics, "
        "and weak topics will automatically appear here."
    )

    st.stop()


# =========================================================
# MAIN VALUES
# =========================================================

total_attempts = stats.get(
    "total_attempts",
    0
)

correct_attempts = stats.get(
    "correct_attempts",
    0
)

incorrect_attempts = stats.get(
    "incorrect_attempts",
    0
)

topics_practiced = stats.get(
    "topics_practiced",
    0
)

misconception_types = stats.get(
    "misconception_types",
    0
)

misconception_counts = stats.get(
    "misconception_counts",
    {}
)

weak_topics = stats.get(
    "weak_topics",
    []
)

strong_topics = stats.get(
    "strong_topics",
    []
)

topic_error_rates = stats.get(
    "topic_error_rates",
    {}
)


if total_attempts:

    success_rate = round(
        correct_attempts
        / total_attempts
        * 100
    )

else:

    success_rate = 0


# =========================================================
# KPI CARDS
# =========================================================

render_section_header(
    "Your Progress at a Glance",
    "A quick snapshot of your recorded learning activity."
)


col1, col2, col3, col4 = st.columns(
    4
)


with col1:

    render_stat_card(
        "Attempts",
        total_attempts,
        "Problems and retries recorded by MindStep.",
    )


with col2:

    render_stat_card(
        "Success Rate",
        f"{success_rate}%",
        f"{correct_attempts} correct out of {total_attempts} stored attempts.",
    )


with col3:

    render_stat_card(
        "Topics",
        topics_practiced,
        "Different mathematical areas practiced.",
    )


with col4:

    render_stat_card(
        "Error Patterns",
        misconception_types,
        "Distinct misconception categories detected.",
    )


# =========================================================
# PERSONALIZED INSIGHTS
# =========================================================

st.divider()

render_section_header(
    "What MindStep Is Learning About You",
    "Patterns become more meaningful as your practice history grows."
)


sorted_mistakes = sorted(
    misconception_counts.items(),
    key=lambda item: item[1],
    reverse=True,
)


col1, col2 = st.columns(
    2
)


with col1:

    if sorted_mistakes:

        raw_mistake = sorted_mistakes[0][0]
        top_mistake_count = sorted_mistakes[0][1]

        render_insight_card(
            "🧩",
            "Most Frequent Pattern",
            readable_name(raw_mistake),
            (
                f"Detected {top_mistake_count} time(s). "
                "This is currently your most repeated reasoning pattern."
            ),
        )

    else:

        render_insight_card(
            "🧩",
            "Most Frequent Pattern",
            "No repeated pattern yet",
            (
                "MindStep has not detected enough repeated errors "
                "to identify a dominant misconception."
            ),
        )


with col2:

    if weak_topics:

        weakest_topic = weak_topics[0][0]

        weakest_error_rate = round(
            weak_topics[0][1]
            * 100
        )

        render_insight_card(
            "🎯",
            "Priority Topic",
            weakest_topic,
            (
                f"Recorded error rate: {weakest_error_rate}%. "
                "This is currently the strongest candidate for focused practice."
            ),
        )

    else:

        render_insight_card(
            "🎯",
            "Priority Topic",
            "More practice needed",
            (
                "There is not enough topic-level history yet "
                "to identify a clear priority."
            ),
        )


# =========================================================
# PERFORMANCE OVERVIEW
# =========================================================

st.divider()

render_section_header(
    "Overall Performance",
    "How your recorded attempts are currently split."
)


left, right = st.columns(
    [1.35, 1]
)


with left:

    progress_data = pd.DataFrame(
        {
            "Result": [
                "Correct",
                "Incorrect",
            ],
            "Attempts": [
                correct_attempts,
                incorrect_attempts,
            ],
        }
    )

    st.bar_chart(
        progress_data.set_index(
            "Result"
        )
    )


with right:

    if success_rate >= 80:

        render_insight_card(
            "🏆",
            "Current Trend",
            "Strong correction rate",
            (
                "Most of your recorded attempts are currently correct. "
                "Continue increasing problem difficulty while watching "
                "for repeated reasoning errors."
            ),
        )

    elif success_rate >= 50:

        render_insight_card(
            "📈",
            "Current Trend",
            "Building consistency",
            (
                "You are solving a meaningful share correctly, "
                "but there are still recurring reasoning patterns worth targeting."
            ),
        )

    else:

        render_insight_card(
            "🌱",
            "Current Trend",
            "Early learning stage",
            (
                "There are currently more incorrect than correct recorded attempts. "
                "Use the retry flow and focus on repairing one error pattern at a time."
            ),
        )


# =========================================================
# TOPIC MASTERY
# =========================================================

st.divider()

render_section_header(
    "Topic Mastery",
    "Success rates calculated from your stored attempts."
)


if topic_error_rates:

    ordered_topics = sorted(
        topic_error_rates.items(),
        key=lambda item: item[1],
    )

    for topic, error_rate in ordered_topics:

        topic_success_rate = round(
            (
                1
                - error_rate
            )
            * 100
        )

        render_topic_progress(
            topic,
            topic_success_rate,
        )

else:

    render_soft_card(
        "📚 Not enough topic data",
        "Practice more problems across different mathematical topics "
        "to build a clearer mastery profile."
    )


# =========================================================
# STRONG + WEAK TOPICS
# =========================================================

st.divider()

render_section_header(
    "Strengths and Priorities",
    "A clearer view of where your practice is going well and where it is not."
)


col1, col2 = st.columns(
    2
)


with col1:

    st.markdown(
        "### 💪 Stronger Topics"
    )

    if strong_topics:

        for index, (
            topic,
            error_rate,
        ) in enumerate(
            strong_topics[:5],
            start=1,
        ):

            success_percentage = round(
                (
                    1
                    - error_rate
                )
                * 100
            )

            render_rank_item(
                index,
                topic,
                f"{success_percentage}% recorded success rate",
            )

    else:

        st.info(
            "Not enough information yet to identify stronger topics."
        )


with col2:

    st.markdown(
        "### 🎯 Practice Priorities"
    )

    if weak_topics:

        for index, (
            topic,
            error_rate,
        ) in enumerate(
            weak_topics[:5],
            start=1,
        ):

            error_percentage = round(
                error_rate
                * 100
            )

            render_rank_item(
                index,
                topic,
                f"{error_percentage}% recorded error rate",
            )

    else:

        st.info(
            "No clear weak-topic pattern has been detected yet."
        )


# =========================================================
# MISCONCEPTION PATTERNS
# =========================================================

st.divider()

render_section_header(
    "Misconception Patterns",
    "The reasoning mistakes MindStep has detected most frequently."
)


misconception_rows = []


for name, count in misconception_counts.items():

    if name == "no_clear_error":
        continue

    misconception_rows.append(
        {
            "Misconception":
                readable_name(name),

            "Times Detected":
                count,
        }
    )


misconception_df = pd.DataFrame(
    misconception_rows
)


if misconception_df.empty:

    st.success(
        "No misconception pattern has been recorded yet."
    )

else:

    misconception_df = (
        misconception_df
        .sort_values(
            "Times Detected",
            ascending=False,
        )
    )

    chart_col, list_col = st.columns(
        [1.4, 1]
    )


    with chart_col:

        st.bar_chart(
            misconception_df
            .set_index(
                "Misconception"
            )
        )


    with list_col:

        for index, row in enumerate(
            misconception_df
            .head(5)
            .itertuples(),
            start=1,
        ):

            render_rank_item(
                index,
                row.Misconception,
                f"{row._2} detection(s)",
            )


# =========================================================
# RECENT LEARNING ACTIVITY
# =========================================================

st.divider()

render_section_header(
    "Recent Learning Activity",
    "Your latest attempts, results, and detected reasoning patterns."
)


recent_rows = []


for row in attempts[:12]:

    (
        attempt_id,
        timestamp,
        question,
        attempted_solution,
        topic,
        misconception,
        confidence,
        first_wrong_step,
        diagnosis,
        attempt_number,
    ) = row


    if misconception == "no_clear_error":

        result_text = "✅ Correct"
        misconception_text = "—"

    else:

        result_text = "🧩 Needs Work"

        misconception_text = (
            readable_name(
                misconception
            )
        )


    recent_rows.append(
        {
            "Time":
                timestamp,

            "Topic":
                topic,

            "Result":
                result_text,

            "Pattern":
                misconception_text,

            "Attempt":
                attempt_number,

            "Confidence":
                f"{round(confidence * 100)}%",
        }
    )


recent_df = pd.DataFrame(
    recent_rows
)


st.dataframe(
    recent_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# NEXT MOVE
# =========================================================

st.divider()

render_section_header(
    "Your Next Move",
    "A practice direction based on your current learning history."
)


if weak_topics:

    next_topic = weak_topics[0][0]

    next_error_rate = round(
        weak_topics[0][1]
        * 100
    )

    render_highlight_banner(
        f"🎯 Focus your next practice session on "
        f"<b>{html.escape(str(next_topic))}</b>. "
        f"Its current recorded error rate is "
        f"<b>{next_error_rate}%</b>. "
        f"Try 3–5 problems and pay attention to the reasoning step "
        f"where mistakes begin."
    )

else:

    render_highlight_banner(
        "✨ Keep solving problems across several topics. "
        "Once MindStep has more learning history, this section will "
        "identify a more specific practice priority."
    )


# =========================================================
# DATA NOTE
# =========================================================

st.caption(
    "Dashboard insights are based only on attempts currently stored "
    "by MindStep. Small numbers of attempts may not represent long-term mastery."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    (
        '<div style="'
        'text-align:center;'
        'color:#64748b;'
        'padding:22px 0 8px 0;'
        'font-size:0.9rem;'
        '">'
        'Practice → understand the mistake → retry → improve.'
        '</div>'
    ),
    unsafe_allow_html=True,
)