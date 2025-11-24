"""
Utility helpers for building MongoDB aggregation expressions that combine
prestige, proximity, and contextual signals into hybrid scores.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence


def _sum_components(components: Sequence[Any], default: int | float = 0) -> Any:
    """
    Combine aggregation expressions safely.

    MongoDB requires `$add` to receive at least two terms, so we normalize the
    component list to handle the 0- or 1-length cases automatically.
    """
    normalized = [component for component in components if component not in (None, 0)]

    if not normalized:
        return default
    if len(normalized) == 1:
        return normalized[0]
    return {"$add": normalized}


def hybrid_score_expression(
    radius_meters: int,
    *,
    categories: Iterable[str] | None = None,
) -> Any:
    """
    Build an expression that blends prestige with proximity and lightweight
    categorical boosts.
    """
    components: list[Any] = [
        {"$multiply": ["$prestige.score", 0.55]},
        {
            "$multiply": [
                {"$divide": [radius_meters, {"$add": ["$distance", 1]}]},
                22,
            ]
        },
    ]

    if categories:
        components.append(
            {
                "$cond": [
                    {"$in": ["$category", list(categories)]},
                    6,
                    0,
                ]
            }
        )

    return _sum_components(components)


def contextual_boost_expression(
    *,
    occasion: str | None = None,
    time_of_day: str | None = None,
    weather: str | None = None,
    group_size: int | None = None,
    budget: str | None = None,
) -> Any:
    """
    Build an expression that rewards POIs matching the caller's context.
    """
    components: list[Any] = []

    if occasion:
        components.append(
            {
                "$cond": [
                    {"$in": [occasion, {"$ifNull": ["$best_for.occasions", []]}]},
                    14,
                    0,
                ]
            }
        )

    if time_of_day:
        components.append(
            {
                "$cond": [
                    {"$in": [time_of_day, {"$ifNull": ["$best_for.time_of_day", []]}]},
                    8,
                    0,
                ]
            }
        )

    if weather and weather != "any":
        components.append(
            {
                "$cond": [
                    {"$in": [weather, {"$ifNull": ["$best_for.weather", ["any"]]}]},
                    6,
                    0,
                ]
            }
        )

    if group_size:
        components.append(
            {
                "$cond": [
                    {"$in": [group_size, {"$ifNull": ["$best_for.group_size", []]}]},
                    5,
                    0,
                ]
            }
        )

    if budget and budget != "any":
        components.append(
            {
                "$cond": [
                    {"$eq": [budget, {"$ifNull": ["$experience.price_range", budget]}]},
                    5,
                    0,
                ]
            }
        )

    return _sum_components(components)


def combine_score_components(*components: Any, default: int | float = 0) -> Any:
    """Convenience wrapper for blending multiple expressions."""
    return _sum_components(list(components), default=default)
