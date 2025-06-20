# logic.py

def calculate_average_level(levels):
    """Calculate average stratum level (rounded to nearest int)"""
    if not levels:
        return 0
    return round(sum(levels) / len(levels))


def interpret_level(level, purpose):
    """Return short summary and description based on level and use case"""
    stratum_ranges = {
        1: ("Short-term action", "You operate with focus on immediate tasks or daily goals."),
        2: ("Pattern and routine", "You handle recurring issues and short cycles (weeks–months)."),
        3: ("Project cycle focus", "You think in terms of quarters or 1-year execution plans."),
        4: ("Operational systems", "You work with functions, policies, or 2–3 year improvements."),
        5: ("Strategic leadership", "You manage complexity with a 5-year horizon and organizational influence."),
        6: ("Vision and innovation", "You think systemically over 10+ years, shaping structures and culture."),
        7: ("Societal shaping", "You envision transformations over decades, often influencing broader systems.")
    }

    summary, description = stratum_ranges.get(level, ("Undefined", "No clear interpretation."))

    if purpose == "Recruitment / Candidate Assessment":
        description += " This can help estimate alignment with role complexity."
    elif purpose == "Leadership Development":
        description += " Consider this your developmental time horizon — a basis for deeper reflection."
    elif purpose == "Self-reflection":
        description += " Use this insight to reflect on where you thrive and where you may want to grow."

    return summary, description
