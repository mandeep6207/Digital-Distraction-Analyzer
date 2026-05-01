from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


MAX_SCREEN_TIME = 16
MAX_SOCIAL_MEDIA = 8
MAX_APP_SWITCHES = 200
MAX_PRODUCTIVE_HOURS = 12

SCORING_WEIGHTS = {
    "screen_time": 30,
    "social_media": 30,
    "app_switches": 20,
    "productive_hours": 20,
}


@dataclass(frozen=True)
class UsageInput:
    screen_time: float
    social_media: float
    productive_hours: float
    app_switches: int


def _normalize(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0
    return min(max(value / maximum, 0), 1)


def validate_inputs(raw_data: dict[str, str]) -> tuple[UsageInput | None, dict[str, str]]:
    errors: dict[str, str] = {}
    cleaned: dict[str, float] = {}

    fields = {
        "screen_time": "Total screen time",
        "social_media": "Social media usage",
        "productive_hours": "Productive hours",
        "app_switches": "App switches",
    }

    for field, label in fields.items():
        value = raw_data.get(field, "")
        if value == "":
            errors[field] = f"{label} is required."
            continue
        try:
            number = float(value)
        except ValueError:
            errors[field] = f"{label} must be a number."
            continue
        if number < 0:
            errors[field] = f"{label} cannot be negative."
            continue
        cleaned[field] = number

    if errors:
        return None, errors

    if cleaned["screen_time"] > 24:
        errors["screen_time"] = "Screen time cannot exceed 24 hours."
    if cleaned["social_media"] > cleaned["screen_time"]:
        errors["social_media"] = "Social media usage cannot exceed total screen time."
    if cleaned["productive_hours"] > 24:
        errors["productive_hours"] = "Productive hours cannot exceed 24 hours."
    if cleaned["productive_hours"] > cleaned["screen_time"]:
        errors["productive_hours"] = "Productive hours should not exceed total screen time."
    if cleaned["app_switches"] > 1000:
        errors["app_switches"] = "App switches look unusually high. Use a daily count under 1000."

    if errors:
        return None, errors

    return (
        UsageInput(
            screen_time=cleaned["screen_time"],
            social_media=cleaned["social_media"],
            productive_hours=cleaned["productive_hours"],
            app_switches=int(round(cleaned["app_switches"])),
        ),
        {},
    )


def analyze_distraction(data: UsageInput) -> dict:
    frame = pd.DataFrame(
        [
            {
                "screen_time": data.screen_time,
                "social_media": data.social_media,
                "productive_hours": data.productive_hours,
                "app_switches": data.app_switches,
            }
        ]
    )

    screen_component = _normalize(frame.at[0, "screen_time"], MAX_SCREEN_TIME) * SCORING_WEIGHTS["screen_time"]
    social_component = _normalize(frame.at[0, "social_media"], MAX_SOCIAL_MEDIA) * SCORING_WEIGHTS["social_media"]
    switch_component = _normalize(frame.at[0, "app_switches"], MAX_APP_SWITCHES) * SCORING_WEIGHTS["app_switches"]
    productivity_component = (1 - _normalize(frame.at[0, "productive_hours"], MAX_PRODUCTIVE_HOURS)) * SCORING_WEIGHTS["productive_hours"]

    score = round(screen_component + social_component + switch_component + productivity_component)
    score = min(max(score, 0), 100)

    insights = build_insights(data, score)
    suggestions = build_suggestions(data, score)

    distraction_hours = max(data.screen_time - data.productive_hours, 0)

    return {
        "score": score,
        "focus_level": focus_level(score),
        "focus_class": focus_class(score),
        "insights": insights,
        "suggestions": suggestions,
        "time_distribution": {
            "labels": ["Social Media", "Productive Work", "Other Screen Time"],
            "values": [
                round(data.social_media, 2),
                round(data.productive_hours, 2),
                round(max(data.screen_time - data.social_media - data.productive_hours, 0), 2),
            ],
        },
        "productivity_distribution": {
            "labels": ["Productive Hours", "Distracted Screen Hours"],
            "values": [round(data.productive_hours, 2), round(distraction_hours, 2)],
        },
        "summary": {
            "screen_time": data.screen_time,
            "social_media": data.social_media,
            "productive_hours": data.productive_hours,
            "app_switches": data.app_switches,
        },
    }


def focus_level(score: int) -> str:
    if score <= 30:
        return "Highly Focused"
    if score <= 70:
        return "Moderate"
    return "Highly Distracted"


def focus_class(score: int) -> str:
    if score <= 30:
        return "success"
    if score <= 70:
        return "warning"
    return "danger"


def build_insights(data: UsageInput, score: int) -> list[str]:
    insights = []

    social_share = data.social_media / data.screen_time if data.screen_time else 0

    if data.social_media >= 2.5:
        insights.append("High social media usage detected.")
    if social_share >= 0.4:
        insights.append("Social media takes up a large share of your total screen time.")
    if data.screen_time >= 8:
        insights.append("Excessive screen time may be reducing focus.")
    if data.app_switches >= 80:
        insights.append("Frequent app switching indicates digital distraction.")
    if data.productive_hours < 3:
        insights.append("Low productive hours warning.")
    if score <= 30:
        insights.append("Your digital habits currently support strong focus.")
    if not insights:
        insights.append("Your usage pattern is balanced, with room for small improvements.")

    return insights


def build_suggestions(data: UsageInput, score: int) -> list[str]:
    suggestions = []

    if data.social_media >= 2:
        suggestions.append("Reduce social media usage with app limits or scheduled check-ins.")
    if data.productive_hours < 5:
        suggestions.append("Increase deep work sessions by blocking distraction-free time.")
    if data.app_switches >= 60:
        suggestions.append("Batch similar tasks to reduce context switching.")
    if data.social_media and data.social_media / max(data.screen_time, 1) >= 0.35:
        suggestions.append("Move social apps off your home screen to reduce impulse checks.")
    if score > 50:
        suggestions.append("Use focus techniques like Pomodoro or 50/10 work cycles.")
    if data.screen_time >= 8:
        suggestions.append("Plan offline breaks to lower total screen fatigue.")
    if not suggestions:
        suggestions.append("Keep your current rhythm and review your habits weekly.")

    return suggestions
