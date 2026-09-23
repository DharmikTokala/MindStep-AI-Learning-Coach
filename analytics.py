from collections import Counter, defaultdict


def normalize_topic(topic):
    if not topic:
        return "Unknown"

    cleaned = topic.strip().lower()

    aliases = {
        "solving linear equations": "Linear Equations",
        "linear equation": "Linear Equations",
        "linear equations": "Linear Equations",
        "quadratic equation": "Quadratic Equations",
        "quadratic equations": "Quadratic Equations",
        "fractions": "Fractions",
        "fraction": "Fractions",
        "factorisation": "Factorization",
        "factorization": "Factorization",
        "distribution": "Distribution",
        "distributive property": "Distribution"
    }

    if cleaned in aliases:
        return aliases[cleaned]

    return topic.strip().title()


def calculate_dashboard_stats(attempts):

    if not attempts:
        return {
            "total_attempts": 0,
            "topics_practiced": 0,
            "misconception_types": 0,
            "topic_counts": {},
            "misconception_counts": {},
            "weak_topics": [],
            "strong_topics": [],
            "topic_error_rates": {},
            "correct_attempts": 0,
            "incorrect_attempts": 0
        }

    topic_counts = Counter()
    misconception_counts = Counter()

    topic_attempts = defaultdict(int)
    topic_errors = defaultdict(int)

    correct_attempts = 0
    incorrect_attempts = 0


    for row in attempts:

        topic = normalize_topic(
            row[4]
        )

        misconception = row[5]

        topic_counts[
            topic
        ] += 1

        topic_attempts[
            topic
        ] += 1


        # "no_clear_error" is how correct answers
        # are currently stored
        if misconception == "no_clear_error":

            correct_attempts += 1

        else:

            incorrect_attempts += 1

            misconception_counts[
                misconception
            ] += 1

            topic_errors[
                topic
            ] += 1


    # =====================================================
    # ERROR RATE BY TOPIC
    # =====================================================

    topic_error_rates = {}

    for topic in topic_attempts:

        total = topic_attempts[
            topic
        ]

        errors = topic_errors[
            topic
        ]

        if total > 0:

            error_rate = (
                errors / total
            )

        else:

            error_rate = 0

        topic_error_rates[
            topic
        ] = error_rate


    # =====================================================
    # WEAK TOPICS
    # Higher error rate = weaker
    # =====================================================

    weak_topics = sorted(
        topic_error_rates.items(),
        key=lambda item: (
            item[1],
            topic_attempts[item[0]]
        ),
        reverse=True
    )[:5]


    # =====================================================
    # STRONG TOPICS
    # Lower error rate = stronger
    # =====================================================

    strong_topics = sorted(
        topic_error_rates.items(),
        key=lambda item: (
            item[1],
            -topic_attempts[item[0]]
        )
    )[:5]


    return {

        "total_attempts":
            len(attempts),

        "topics_practiced":
            len(topic_counts),

        "misconception_types":
            len(misconception_counts),

        "topic_counts":
            dict(topic_counts),

        "misconception_counts":
            dict(misconception_counts),

        "weak_topics":
            weak_topics,

        "strong_topics":
            strong_topics,

        "topic_error_rates":
            topic_error_rates,

        "correct_attempts":
            correct_attempts,

        "incorrect_attempts":
            incorrect_attempts
    }