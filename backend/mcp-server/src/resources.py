"""
Static MCP resources that describe NYC neighborhood playbooks and category taxonomy.
These resources are exposed both by the FastMCP server (cloud) and the stdio server.
"""

NEIGHBORHOOD_GUIDES = [
    {
        "slug": "west-village",
        "name": "West Village",
        "vibe": "Candle-lit brownstones, intimate dining rooms, and late-night jazz hideaways.",
        "best_for": ["date-night", "celebration", "after-work"],
        "signature_pois": [
            "Employees Only",
            "L'Artusi",
            "Via Carota",
        ],
        "must_try": [
            "9th Street pasta crawl (L'Artusi → I Sodi)",
            "Speakeasy crawl down Hudson Street",
        ],
    },
    {
        "slug": "flatiron-nomad",
        "name": "Flatiron & NoMad",
        "vibe": "Design-forward dining rooms, chef counter energy, and power lunches that stretch into dinner.",
        "best_for": ["business-dinner", "business-lunch", "celebration"],
        "signature_pois": [
            "Eleven Madison Park",
            "The NoMad Bar",
            "Koloman",
        ],
        "must_try": [
            "Chef's tasting at EMP followed by digestifs at The NoMad Bar",
            "Midday strategy session at Koloman's front café",
        ],
    },
    {
        "slug": "brooklyn-bridge-corridor",
        "name": "Brooklyn Heights & DUMBO",
        "vibe": "Skyline views, riverfront promenades, and inventive tasting menus tucked into restored warehouses.",
        "best_for": ["family-dinner", "sunset-stroll", "special-occasion"],
        "signature_pois": [
            "The River Café",
            "Vinegar Hill House",
            "Celestine",
        ],
        "must_try": [
            "Golden hour cocktails underneath the Brooklyn Bridge",
            "Wood-fired brunch in Vinegar Hill",
        ],
    },
    {
        "slug": "midtown-power",
        "name": "Midtown Power Corridor",
        "vibe": "Marble lobbies, legacy steakhouses, and Michelin-grade temples built for decisive dinners.",
        "best_for": ["business-dinner", "pre-theatre", "client-win"],
        "signature_pois": [
            "Le Bernardin",
            "The Modern",
            "Keens Steakhouse",
        ],
        "must_try": [
            "Pre-show tasting menu at The Modern",
            "Closing toast with a 100-year-old brandy at Keens",
        ],
    },
]

CATEGORY_TAXONOMY = {
    "fine-dining": {
        "description": "Michelin-caliber rooms, extended tasting menus, chef tables, and white-glove service.",
        "prestige_range": "110-150",
        "ideal_occasions": ["celebration", "date-night", "client-win"],
        "hallmarks": [
            "Multi-course tasting menus with optional wine pairings",
            "Dedicated reservations desk and jacket-friendly dress code",
            "Signature dish lineage (e.g., EMP's plant-based tasting)",
        ],
    },
    "casual-dining": {
        "description": "Neighborhood staples with James Beard nods, power lunches, and cult favorite pizzas.",
        "prestige_range": "70-109",
        "ideal_occasions": ["family-dinner", "after-work", "weekend-brunch"],
        "hallmarks": [
            "Walk-in friendly counters or bar seating",
            "Chef-driven menus with seasonal specials",
            "Comfortable price points without sacrificing sourcing",
        ],
    },
    "bars-cocktails": {
        "description": "Award-winning bar programs, low-lit speakeasies, and zero-proof tasting flights.",
        "prestige_range": "60-95",
        "ideal_occasions": ["after-work", "late-night", "date-night"],
        "hallmarks": [
            "House clarified milk punches and reserve spirit programs",
            "Snack menus curated with local purveyors",
            "Standing room vibes with impeccable playlists",
        ],
    },
}

RESOURCE_MAP = {
    "nyc-poi://guides/neighborhoods": {
        "name": "Neighborhood Playbook",
        "description": "Context cards for the neighborhoods we cover during demos.",
        "mime_type": "application/json",
        "data": {"neighborhoods": NEIGHBORHOOD_GUIDES},
    },
    "nyc-poi://taxonomy/categories": {
        "name": "Category Taxonomy",
        "description": "Prestige-focused taxonomy aligning fine dining, casual dining, and cocktail bars.",
        "mime_type": "application/json",
        "data": {"categories": CATEGORY_TAXONOMY},
    },
}
