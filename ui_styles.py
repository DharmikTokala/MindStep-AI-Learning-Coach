import streamlit as st


def apply_global_styles():

    st.markdown(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* =====================================================
           GLOBAL
        ===================================================== */

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        html {
            scroll-behavior: smooth;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 12% 5%,
                    rgba(37,99,235,0.16),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 90% 4%,
                    rgba(124,58,237,0.15),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 55% 80%,
                    rgba(6,182,212,0.08),
                    transparent 28%
                ),
                linear-gradient(
                    180deg,
                    #040711 0%,
                    #080d19 45%,
                    #07101d 100%
                );

            color: #f8fafc;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }


        /* =====================================================
           SCROLLBAR
        ===================================================== */

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #060b15;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(
                #3b82f6,
                #7c3aed
            );
            border-radius: 20px;
        }


        /* =====================================================
           SIDEBAR
        ===================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    rgba(8,13,27,0.98),
                    rgba(11,18,32,0.98)
                );

            border-right:
                1px solid rgba(255,255,255,0.07);

            box-shadow:
                12px 0 40px rgba(0,0,0,0.18);
        }


        section[data-testid="stSidebar"] * {
            color: #dbeafe !important;
        }


        section[data-testid="stSidebar"] a {
            border-radius: 12px;
            transition:
                background 0.2s ease,
                transform 0.2s ease;
        }


        section[data-testid="stSidebar"] a:hover {
            background:
                rgba(59,130,246,0.10);

            transform:
                translateX(3px);
        }


        /* =====================================================
           TYPOGRAPHY
        ===================================================== */

        h1,
        h2,
        h3,
        h4 {
            color: #f8fafc !important;
            letter-spacing: -0.025em;
        }


        h1 {
            font-weight: 800 !important;
        }


        h2 {
            font-weight: 750 !important;
        }


        h3 {
            font-weight: 700 !important;
        }


        p,
        li,
        label,
        div {
            color: #d8e1ee;
        }


        /* =====================================================
           HERO
        ===================================================== */

        .hero-card {

            position: relative;
            overflow: hidden;

            background:
                linear-gradient(
                    135deg,
                    rgba(14,22,41,0.96),
                    rgba(10,17,32,0.96)
                );

            border:
                1px solid rgba(255,255,255,0.08);

            border-radius: 30px;

            padding:
                44px 48px;

            margin-bottom:
                30px;

            box-shadow:
                0 24px 70px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.04);

            backdrop-filter:
                blur(20px);
        }


        .hero-card::before {

            content: "";

            position: absolute;

            width: 340px;
            height: 340px;

            top: -140px;
            right: -90px;

            border-radius: 999px;

            background:
                radial-gradient(
                    circle,
                    rgba(99,102,241,0.34),
                    transparent 70%
                );

            animation:
                glowFloat 7s ease-in-out infinite;
        }


        .hero-card::after {

            content: "";

            position: absolute;

            width: 320px;
            height: 320px;

            bottom: -170px;
            left: -120px;

            border-radius: 999px;

            background:
                radial-gradient(
                    circle,
                    rgba(14,165,233,0.23),
                    transparent 70%
                );

            animation:
                glowFloatTwo 9s ease-in-out infinite;
        }


        @keyframes glowFloat {

            0%,
            100% {
                transform:
                    translate(0,0);
            }

            50% {
                transform:
                    translate(-20px,25px);
            }
        }


        @keyframes glowFloatTwo {

            0%,
            100% {
                transform:
                    translate(0,0);
            }

            50% {
                transform:
                    translate(25px,-15px);
            }
        }


        .hero-badge {

            display: inline-flex;

            align-items: center;

            gap: 6px;

            position: relative;

            z-index: 2;

            padding:
                8px 14px;

            border-radius:
                999px;

            background:
                rgba(59,130,246,0.12);

            border:
                1px solid rgba(96,165,250,0.27);

            color:
                #93c5fd !important;

            font-size:
                0.85rem;

            font-weight:
                700;

            letter-spacing:
                0.02em;

            margin-bottom:
                20px;
        }


        .hero-title {

            position:
                relative;

            z-index:
                2;

            font-size:
                3.45rem;

            line-height:
                1.05;

            font-weight:
                800;

            letter-spacing:
                -0.05em;

            color:
                #f8fafc;

            max-width:
                900px;

            margin-bottom:
                18px;
        }


        .hero-subtitle {

            position:
                relative;

            z-index:
                2;

            max-width:
                850px;

            font-size:
                1.08rem;

            line-height:
                1.85;

            color:
                #b8c6d9 !important;

            margin-bottom:
                26px;
        }


        .gradient-text {

            background:
                linear-gradient(
                    90deg,
                    #60a5fa,
                    #818cf8,
                    #c084fc,
                    #22d3ee
                );

            background-size:
                220% auto;

            -webkit-background-clip:
                text;

            -webkit-text-fill-color:
                transparent;

            background-clip:
                text;

            animation:
                gradientMove 6s linear infinite;
        }


        @keyframes gradientMove {

            to {
                background-position:
                    220% center;
            }
        }


        /* =====================================================
           HERO PILLS
        ===================================================== */

        .hero-pills {

            position:
                relative;

            z-index:
                2;

            display:
                flex;

            flex-wrap:
                wrap;

            gap:
                10px;

            margin-top:
                10px;
        }


        .hero-pill {

            padding:
                10px 14px;

            border-radius:
                14px;

            background:
                rgba(255,255,255,0.035);

            border:
                1px solid rgba(255,255,255,0.075);

            color:
                #dbeafe !important;

            font-size:
                0.9rem;

            font-weight:
                550;

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                background 0.2s ease;
        }


        .hero-pill:hover {

            transform:
                translateY(-2px);

            background:
                rgba(59,130,246,0.08);

            border-color:
                rgba(96,165,250,0.25);
        }


        /* =====================================================
           SECTION TITLES
        ===================================================== */

        .section-title {

            font-size:
                1.9rem;

            font-weight:
                800;

            letter-spacing:
                -0.03em;

            color:
                #f8fafc;

            margin-top:
                18px;

            margin-bottom:
                6px;
        }


        .section-subtitle {

            color:
                #8fa1b7 !important;

            font-size:
                0.98rem;

            line-height:
                1.6;

            margin-bottom:
                20px;
        }


        /* =====================================================
           FEATURE GRID
        ===================================================== */

        .feature-grid {

            display:
                grid;

            grid-template-columns:
                repeat(3, minmax(0,1fr));

            gap:
                18px;

            margin:
                18px 0 34px 0;
        }


        .feature-card {

            position:
                relative;

            overflow:
                hidden;

            min-height:
                175px;

            padding:
                24px;

            border-radius:
                22px;

            background:
                linear-gradient(
                    180deg,
                    rgba(20,31,52,0.94),
                    rgba(12,20,36,0.94)
                );

            border:
                1px solid rgba(255,255,255,0.075);

            box-shadow:
                0 12px 34px rgba(0,0,0,0.20);

            transition:
                transform 0.22s ease,
                border-color 0.22s ease,
                box-shadow 0.22s ease;
        }


        .feature-card::after {

            content: "";

            position:
                absolute;

            width:
                120px;

            height:
                120px;

            right:
                -60px;

            bottom:
                -60px;

            background:
                radial-gradient(
                    circle,
                    rgba(59,130,246,0.12),
                    transparent 70%
                );
        }


        .feature-card:hover {

            transform:
                translateY(-5px);

            border-color:
                rgba(96,165,250,0.26);

            box-shadow:
                0 18px 40px rgba(0,0,0,0.28);
        }


        .feature-step {

            color:
                #60a5fa !important;

            font-size:
                0.78rem;

            font-weight:
                800;

            text-transform:
                uppercase;

            letter-spacing:
                0.1em;

            margin-bottom:
                12px;
        }


        .feature-title {

            color:
                #f8fafc !important;

            font-size:
                1.18rem;

            font-weight:
                750;

            margin-bottom:
                10px;
        }


        .feature-desc {

            color:
                #b8c5d6 !important;

            font-size:
                0.94rem;

            line-height:
                1.65;
        }


        /* =====================================================
           SOFT CARDS
        ===================================================== */

        .soft-card {

            position:
                relative;

            overflow:
                hidden;

            background:
                linear-gradient(
                    145deg,
                    rgba(16,27,47,0.92),
                    rgba(10,18,33,0.92)
                );

            border:
                1px solid rgba(255,255,255,0.07);

            border-radius:
                22px;

            padding:
                22px 24px;

            margin-bottom:
                16px;

            box-shadow:
                0 12px 30px rgba(0,0,0,0.18);
        }


        .soft-card-title {

            color:
                #f8fafc !important;

            font-size:
                1.08rem;

            font-weight:
                750;

            margin-bottom:
                9px;
        }


        .soft-card-text {

            color:
                #bdcad9 !important;

            line-height:
                1.7;

            font-size:
                0.96rem;
        }


        /* =====================================================
           HIGHLIGHT BANNER
        ===================================================== */

        .highlight-banner {

            background:
                linear-gradient(
                    90deg,
                    rgba(37,99,235,0.16),
                    rgba(109,40,217,0.12),
                    rgba(8,145,178,0.10)
                );

            border:
                1px solid rgba(96,165,250,0.18);

            border-radius:
                18px;

            padding:
                16px 18px;

            margin:
                14px 0 22px 0;

            color:
                #dbeafe !important;

            font-size:
                0.98rem;

            line-height:
                1.65;

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.025);
        }


        /* =====================================================
           INPUTS
        ===================================================== */

        .stTextArea textarea,
        .stTextInput input {

            background:
                linear-gradient(
                    180deg,
                    rgba(12,21,38,0.95),
                    rgba(10,18,32,0.95)
                ) !important;

            color:
                #f8fafc !important;

            border:
                1px solid rgba(255,255,255,0.09) !important;

            border-radius:
                17px !important;

            padding:
                15px !important;

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.02);

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }


        .stTextArea textarea:focus,
        .stTextInput input:focus {

            border:
                1px solid rgba(96,165,250,0.60) !important;

            box-shadow:
                0 0 0 3px rgba(59,130,246,0.08) !important;
        }


        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {

            color:
                #52637a !important;
        }


        label {

            color:
                #dce6f3 !important;

            font-weight:
                650 !important;
        }


        /* =====================================================
           SELECT BOX
        ===================================================== */

        div[data-baseweb="select"] > div {

            background:
                rgba(12,21,38,0.95) !important;

            border:
                1px solid rgba(255,255,255,0.08) !important;

            border-radius:
                14px !important;
        }


        /* =====================================================
           BUTTONS
        ===================================================== */

        .stButton > button {

            width:
                100%;

            min-height:
                48px;

            border:
                1px solid rgba(255,255,255,0.10);

            border-radius:
                15px;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #6d28d9
                );

            color:
                white !important;

            font-weight:
                750;

            letter-spacing:
                0.01em;

            box-shadow:
                0 10px 26px rgba(37,99,235,0.22);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease,
                filter 0.2s ease;
        }


        .stButton > button:hover {

            transform:
                translateY(-2px);

            filter:
                brightness(1.08);

            box-shadow:
                0 16px 34px rgba(59,130,246,0.28);
        }


        .stButton > button:active {

            transform:
                translateY(0px);
        }


        /* =====================================================
           METRICS
        ===================================================== */

        [data-testid="stMetric"] {

            background:
                linear-gradient(
                    150deg,
                    rgba(16,27,47,0.95),
                    rgba(11,19,34,0.95)
                );

            border:
                1px solid rgba(255,255,255,0.075);

            padding:
                20px;

            border-radius:
                20px;

            box-shadow:
                0 12px 30px rgba(0,0,0,0.17);

            transition:
                transform 0.2s ease,
                border-color 0.2s ease;
        }


        [data-testid="stMetric"]:hover {

            transform:
                translateY(-3px);

            border-color:
                rgba(96,165,250,0.22);
        }


        [data-testid="stMetricLabel"] {

            color:
                #8ea0b6 !important;

            font-weight:
                650 !important;
        }


        [data-testid="stMetricValue"] {

            color:
                #f8fafc !important;

            font-weight:
                800 !important;

            letter-spacing:
                -0.025em;
        }


        /* =====================================================
           EXPANDERS
        ===================================================== */

        details {

            background:
                linear-gradient(
                    145deg,
                    rgba(15,25,43,0.88),
                    rgba(10,18,32,0.88)
                );

            border:
                1px solid rgba(255,255,255,0.07);

            border-radius:
                16px;

            padding:
                7px 11px;

            transition:
                border-color 0.2s ease;
        }


        details:hover {

            border-color:
                rgba(96,165,250,0.18);
        }


        /* =====================================================
           DATAFRAME
        ===================================================== */

        [data-testid="stDataFrame"] {

            overflow:
                hidden;

            border:
                1px solid rgba(255,255,255,0.07);

            border-radius:
                18px;

            box-shadow:
                0 12px 30px rgba(0,0,0,0.14);
        }


        /* =====================================================
           FILE UPLOADER
        ===================================================== */

        [data-testid="stFileUploader"] {

            background:
                rgba(12,21,38,0.65);

            border:
                1px dashed rgba(96,165,250,0.24);

            border-radius:
                20px;

            padding:
                12px;
        }


        /* =====================================================
           ALERT BOXES
        ===================================================== */

        div[data-baseweb="notification"] {

            border-radius:
                16px !important;

            border:
                1px solid rgba(255,255,255,0.08) !important;

            box-shadow:
                0 8px 20px rgba(0,0,0,0.12);
        }


        /* =====================================================
           RADIO BUTTONS
        ===================================================== */

        [role="radiogroup"] {

            background:
                rgba(12,21,38,0.35);

            padding:
                12px;

            border-radius:
                16px;
        }


        /* =====================================================
           PROGRESS BAR
        ===================================================== */

        [data-testid="stProgressBar"] > div > div {

            background:
                linear-gradient(
                    90deg,
                    #3b82f6,
                    #8b5cf6,
                    #22d3ee
                ) !important;
        }


        /* =====================================================
           DIVIDER
        ===================================================== */

        hr {

            border-color:
                rgba(255,255,255,0.06) !important;

            margin-top:
                2rem !important;

            margin-bottom:
                2rem !important;
        }


        /* =====================================================
           REMOVE STREAMLIT CHROME
        ===================================================== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }


        /* =====================================================
           MOBILE
        ===================================================== */

        @media (
            max-width: 900px
        ) {

            .hero-card {

                padding:
                    30px 24px;
            }

            .hero-title {

                font-size:
                    2.35rem;
            }

            .hero-subtitle {

                font-size:
                    1rem;
            }

            .feature-grid {

                grid-template-columns:
                    1fr;
            }

            .block-container {

                padding-left:
                    1rem;

                padding-right:
                    1rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HERO
# =========================================================

def render_hero_section():

    hero_html = (
        '<div class="hero-card">'

        '<div class="hero-badge">'
        '✦ AI-Powered Learning Coach'
        '</div>'

        '<div class="hero-title">'
        'Understand the '
        '<span class="gradient-text">'
        'mistake'
        '</span>.'
        '<br>'
        'Master the concept.'
        '</div>'

        '<div class="hero-subtitle">'
        'A smarter way to learn mathematics. '
        'The coach studies your reasoning, identifies likely misconceptions, '
        'and guides you toward the solution without immediately giving the answer away.'
        '</div>'

        '<div class="hero-pills">'

        '<div class="hero-pill">'
        '✍️ Enter a problem'
        '</div>'

        '<div class="hero-pill">'
        '🧩 Show your thinking'
        '</div>'

        '<div class="hero-pill">'
        '🔍 Find the misconception'
        '</div>'

        '<div class="hero-pill">'
        '💡 Get guided hints'
        '</div>'

        '<div class="hero-pill">'
        '🔁 Retry'
        '</div>'

        '<div class="hero-pill">'
        '📈 Build mastery'
        '</div>'

        '</div>'

        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )


# =========================================================
# SECTION HEADER
# =========================================================

def render_section_header(
    title: str,
    subtitle: str = ""
):

    html = (
        f'<div class="section-title">'
        f'{title}'
        f'</div>'

        f'<div class="section-subtitle">'
        f'{subtitle}'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# FEATURE CARDS
# =========================================================

def render_feature_cards():

    html = (
        '<div class="feature-grid">'

        '<div class="feature-card">'

        '<div class="feature-step">'
        '01 · ASK'
        '</div>'

        '<div class="feature-title">'
        'Bring your problem'
        '</div>'

        '<div class="feature-desc">'
        'Enter the math question you are working on instead of searching directly for the solution.'
        '</div>'

        '</div>'


        '<div class="feature-card">'

        '<div class="feature-step">'
        '02 · THINK'
        '</div>'

        '<div class="feature-title">'
        'Show your reasoning'
        '</div>'

        '<div class="feature-desc">'
        'Share your attempted steps so the AI can understand how you approached the problem.'
        '</div>'

        '</div>'


        '<div class="feature-card">'

        '<div class="feature-step">'
        '03 · IMPROVE'
        '</div>'

        '<div class="feature-title">'
        'Fix the misconception'
        '</div>'

        '<div class="feature-desc">'
        'Receive progressively stronger hints, retry the problem, and learn from the reasoning error.'
        '</div>'

        '</div>'

        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# HIGHLIGHT BANNER
# =========================================================

def render_highlight_banner(
    text: str
):

    html = (
        '<div class="highlight-banner">'
        f'{text}'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# SOFT CARD
# =========================================================

def render_soft_card(
    title: str,
    text: str
):

    html = (
        '<div class="soft-card">'

        '<div class="soft-card-title">'
        f'{title}'
        '</div>'

        '<div class="soft-card-text">'
        f'{text}'
        '</div>'

        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )