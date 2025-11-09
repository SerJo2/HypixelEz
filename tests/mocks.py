"""
Mock data for Hypixel API testing
"""

# Mock response for UUID lookup
MOCK_UUID_RESPONSE = {
    "id": "eca19e2e713d49a98582320229f696ed"
}

# Mock response for profile list
MOCK_PROFILES_RESPONSE = {
    "success": True,
    "profiles": [
        {
            "profile_id": "f5791b0c-caf1-4701-aea3-d727ea53a901",
            "cute_name": "Peach"
        },
        {
            "profile_id": "0b1362a7-43e8-454b-a2ed-6db43ae32f19",
            "cute_name": "Kiwi"
        },
        {
            "profile_id": "eca19e2e-713d-49a9-8582-320229f696ed",
            "cute_name": "Zucchini"
        }
    ]
}

# Mock response for full profile data
MOCK_PROFILE_DATA = {
    "success": True,
    "profile": {
        "members": {
            "eca19e2e713d49a98582320229f696ed": {
                "collection": {
                    "LOG": 77760,
                    "COAL": 15000,
                    "IRON": 25000
                },
                "slayer": {
                    "slayer_bosses": {
                        "zombie": {
                            "claimed_levels": {
                                "level_1": True,
                                "level_2": True,
                                "level_3": True,
                                "level_4": True,
                                "level_5": True,
                                "level_6": True,
                                "level_7": True
                            },
                            "boss_kills_tier_0": 15,
                            "boss_kills_tier_1": 10,
                            "boss_kills_tier_2": 8,
                            "boss_kills_tier_3": 5,
                            "xp": 148706
                        },
                        "spider": {
                            "claimed_levels": {
                                "level_1": True,
                                "level_2": True
                            },
                            "boss_kills_tier_0": 5,
                            "boss_kills_tier_1": 3,
                            "xp": 50000
                        }
                    }
                },
                "player_data": {
                    "experience": {
                        "SKILL_CARPENTRY": 5409716,
                        "SKILL_FARMING": 1500000,
                        "SKILL_MINING": 2000000
                    }
                },
                "dungeons": {
                    "dungeon_types": {
                        "catacombs": {
                            "experience": 567442
                        }
                    },
                    "player_classes": {
                        "berserk": {
                            "experience": 378520
                        },
                        "healer": {
                            "experience": 15000
                        },
                        "mage": {
                            "experience": 30000
                        }
                    }
                },
                "leveling": {
                    "experience": 16915
                }
            }
        }
    }
}

# Mock error responses
MOCK_ERROR_RESPONSE = {
    "success": False,
    "cause": "Invalid API key"
}

MOCK_RATE_LIMIT_RESPONSE = {
    "success": False,
    "cause": "Key throttle"
}

# Mock empty/missing data
MOCK_EMPTY_PROFILE = {
    "success": True,
    "profile": {
        "members": {
            "eca19e2e713d49a98582320229f696ed": {
                "collection": {},
                "slayer": {"slayer_bosses": {}},
                "player_data": {"experience": {}},
                "dungeons": {
                    "dungeon_types": {"catacombs": {}},
                    "player_classes": {}
                },
                "leveling": {}
            }
        }
    }
}