"""Prompt templates and hardcoded responses for evaluation."""

# Follow-up questions based on score ranges
FOLLOW_UP_PROMPTS = {
    "low": [
        "Can you elaborate more on that? I'd like deeper details.",
        "What was your biggest challenge with this topic?",
        "Can you provide a concrete example?",
        "How would you approach this differently?",
        "What have you learned from this experience?"
    ],
    "medium": [
        "That's a good start. Can you provide a specific example?",
        "How would you improve that approach?",
        "What edge cases did you consider?",
        "Can you explain the trade-offs you made?",
        "How did you measure success?"
    ],
    "high": [
        "Great explanation. How would you handle a more complex scenario?",
        "What was the most challenging part?",
        "How would you scale this solution?",
        "What would you do differently next time?",
        "Can you discuss the technical trade-offs?"
    ],
    "excellent": [
        "Excellent answer. Now tell me about a time you applied this in practice.",
        "How did you overcome the toughest challenge?",
        "What did you learn from this project?",
        "How would you mentor someone on this topic?",
        "What would be your next step in this area?"
    ]
}

# Generic strength statements
STRENGTH_STATEMENTS = [
    "Good technical depth",
    "Clear communication",
    "Relevant example provided",
    "Structured thinking",
    "Problem-solving approach",
    "Attention to detail",
    "Understanding of trade-offs",
    "Practical experience",
    "Good use of terminology",
    "Thoughtful consideration"
]

# Generic improvement areas
IMPROVEMENT_STATEMENTS = [
    "More specific details needed",
    "Could be more concise",
    "Consider alternative approaches",
    "Add concrete examples",
    "Explain technical terms better",
    "Address edge cases",
    "Discuss performance implications",
    "Consider scalability",
    "Provide quantitative metrics",
    "Explain your reasoning more"
]

# Summary report template
SUMMARY_TEMPLATE = """Based on your {role} interview performance:

You achieved an overall score of {overall_score}/10, with an average score of {average_score}/10 across all questions. Your responses demonstrated strengths in {strength1} and {strength2}. 

To improve your interview performance, focus on {improvement1} and {improvement2}. These are common areas where candidates can strengthen their answers with more specific examples and deeper technical reasoning.

Overall, your interview showed {performance_level} understanding of the core concepts. Continue practicing with diverse scenarios and aim to provide more detailed, real-world examples in your future interviews."""

# Performance level descriptions
PERFORMANCE_LEVELS = {
    "excellent": (8.5, 10.0, "Excellent"),
    "strong": (7.0, 8.4, "Strong"),
    "good": (5.5, 6.9, "Good"),
    "fair": (4.0, 5.4, "Fair"),
    "needs_improvement": (1.0, 3.9, "Needs Improvement")
}


def get_follow_up_question(score):
    """
    Get a follow-up question based on score.

    Args:
        score (float): Answer score (1.0-10.0).

    Returns:
        str: Follow-up question.
    """
    if score < 4:
        return "low"
    elif score < 6:
        return "medium"
    elif score < 8:
        return "high"
    else:
        return "excellent"


def get_performance_level(score):
    """
    Get performance level description for a score.

    Args:
        score (float): Answer score (1.0-10.0).

    Returns:
        str: Performance level name.
    """
    for level, (min_score, max_score, name) in PERFORMANCE_LEVELS.items():
        if min_score <= score <= max_score:
            return name
    return "Needs Improvement"
