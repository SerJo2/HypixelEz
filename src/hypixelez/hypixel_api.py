import requests

from .constants import CollectionKey
from .logger import setup_logging, get_logger

_DEBUG_ = True
_LOGGER_NAME_ = "hypixelez"

_CATA_CUMULATIVE_XP_ = [
    50,
    125,
    235,
    395,
    625,
    955,
    1425,
    2095,
    3045,
    4385,
    6275,
    8940,
    12700,
    17960,
    25340,
    35640,
    50040,
    70040,
    97640,
    135640,
    188140,
    259640,
    356640,
    488640,
    668640,
    911640,
    1239640,
    1684640,
    2284640,
    3084640,
    4149640,
    5559640,
    7459640,
    9959640,
    13259640,
    17559640,
    23159640,
    30359640,
    39559640,
    51559640,
    66559640,
    85559640,
    109559640,
    139559640,
    177559640,
    225559640,
    285559640,
    360559640,
    453559640,
    569809640,
]

_SKILL_CUMULATIVE_LEVELS_ = [
    0,
    50,
    175,
    375,
    675,
    1175,
    1925,
    2925,
    4425,
    6425,
    9925,
    14925,
    22425,
    32425,
    47425,
    67425,
    97425,
    147425,
    222425,
    322425,
    522425,
    822425,
    1222425,
    1722425,
    2322425,
    3022425,
    3822425,
    4722425,
    5722425,
    6822425,
    8022425,
    9322425,
    10722425,
    12222425,
    13822425,
    15522425,
    17322425,
    19222425,
    21222425,
    23322425,
    25522425,
    27822425,
    30222425,
    32722425,
    35322425,
    38072425,
    40972425,
    44072425,
    47472425,
    51172425,
    55172425,
    59472425,
    64072425,
    68972425,
    74172425,
    79672425,
    85472425,
    91572425,
    97972425,
    104672425,
    111672425,
]

_SKILL_LEVEL_UP_LEVELS_ = {
    0,
    50,
    125,
    200,
    300,
    500,
    750,
    1000,
    1500,
    2000,
    3500,
    5000,
    7500,
    10000,
    15000,
    20000,
    30000,
    50000,
    75000,
    100000,
    200000,
    300000,
    400000,
    500000,
    600000,
    700000,
    800000,
    900000,
    1000000,
    1100000,
    1200000,
    1300000,
    1400000,
    1500000,
    1600000,
    1700000,
    1800000,
    1900000,
    2000000,
    2100000,
    2200000,
    2300000,
    2400000,
    2500000,
    2600000,
    2750000,
    2900000,
    3100000,
    3400000,
    3700000,
    4000000,
    4300000,
    4600000,
    4900000,
    5200000,
    5500000,
    5800000,
    6100000,
    6400000,
    6700000,
    7000000,
}


def _calculate_level(xp: int, cumulative_levels: list) -> int:
    """Calculate the level for a given XP using a cumulative XP table.

    Args:
        xp: Total accumulated XP.
        cumulative_levels: A list where each item is the cumulative XP required
            to reach the corresponding level index.

    Returns:
        The computed level as an integer index (0-based relative to the table).
    """
    for i, required_xp in enumerate(cumulative_levels):
        if required_xp > xp:
            return i
    return len(cumulative_levels)


def _calculate_current_xp(xp: int, cumulative_levels: list) -> int:
    """Calculate current XP progress within the current level.

    This returns how much XP the player has earned toward the next level,
    not the total XP.

    Args:
        xp: Total accumulated XP.
        cumulative_levels: A list of cumulative XP thresholds.

    Returns:
        XP accumulated within the current level.
    """
    level = _calculate_level(xp, cumulative_levels)
    if level == 0:
        return xp
    return xp - cumulative_levels[level - 1]


class HypixelClient:
    """HTTP client for the Hypixel SkyBlock API.

    This client also supports resolving Minecraft usernames to UUIDs via Mojang API.
    """

    def __init__(
        self,
        api_key: str,
        debug=_DEBUG_,
        base_url="https://api.hypixel.net/v2/skyblock/profile",
    ):
        """Create a Hypixel API client.

        Args:
            api_key: Hypixel API key (get one at https://developer.hypixel.net/).
            debug: If True, enables debug logging; otherwise uses info-level logging.
            base_url: Hypixel endpoint used by :meth:`fetch_profile_info`.

        Notes:
            - Initializes an internal `requests.Session`.
            - Maintains an in-memory UUID cache for `get_uuid_by_name`.
        """
        setup_logging(debug)
        self.logger = get_logger(_LOGGER_NAME_)
        self._uuid_cache = {}

        self.api_key = api_key
        self.session = requests.Session()
        self.base_url = base_url

    def get_uuid_by_name(self, name: str) -> str | None:
        """Resolve a Minecraft username to a UUID using Mojang API.

        The result is cached in-memory for the lifetime of the client.

        Args:
            name: Minecraft username.

        Returns:
            The UUID string if found; otherwise None.
            Returns None also in case of network errors.

        Notes:
            This method currently swallows `requests` exceptions and returns None
            instead of raising.
        """

        if name in self._uuid_cache:
            self.logger.debug(f"UUID cache HIT for: {name}")
            return self._uuid_cache[name]

        try:
            response = requests.get(
                f"https://api.mojang.com/users/profiles/minecraft/{name}", timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if "id" not in data:
                self.logger.warning(f"UUID not found for player: {name}")
                return None
            self._uuid_cache[name] = data["id"]
            self.logger.debug(f"Cached UUID for: {name}")
            return self._uuid_cache[name]

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch UUID for {name}: {e}")
            return None

    def get_profile_names_ids_by_id(self, uuid: str) -> dict:
        """Get available SkyBlock profiles for a player UUID.

        Args:
            uuid: Minecraft UUID.

        Returns:
            A mapping ``{profile_name: profile_id}``, where profile_name is
            the Hypixel "cute_name" (e.g. "Peach"), and profile_id is the profile id.

        Raises:
            requests.RequestException: If the underlying HTTP request fails.

        Notes:
            This method currently assumes the response contains a ``"profiles"`` key.
        """
        headers = {
            "API-Key": self.api_key,
        }
        params = {"uuid": uuid}

        response = self.session.get(
            "https://api.hypixel.net/v2/skyblock/profiles",
            headers=headers,
            params=params,
        ).json()
        x = response["profiles"]

        names = {}

        for i in x:
            names[i["cute_name"]] = i["profile_id"]

        return names

    def fetch_profile_info(self, uuid: str, profile: str):
        """Fetch full SkyBlock profile data and wrap it in :class:`SkyblockProfileData`.

        Args:
            uuid: Minecraft UUID.
            profile: SkyBlock profile id.

        Returns:
            A :class:`SkyblockProfileData` instance with the raw API response and UUID.

        Raises:
            requests.RequestException: For network issues or non-2xx HTTP status.
            Exception: If Hypixel returns ``success=false`` (API-level error).

        Notes:
            On API-level errors the code currently raises a generic `Exception`.
            Consider introducing a custom exception type for better UX and docs.
        """
        headers = {
            "API-Key": self.api_key,
        }
        params = {"uuid": uuid, "profile": profile}

        try:
            response = self.session.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data["success"]:
                raise Exception(f"API Error: {data.get('cause', 'Unknown error')}")

            return SkyblockProfileData(data, uuid)
        except requests.exceptions.RequestException as e:
            raise e


class SkyblockProfileData:
    """Wrapper around Hypixel SkyBlock profile JSON with convenience getters.

    Most getter methods are "safe": if the requested data is missing, they return
    a default value (usually 0 or an empty list) and log a warning.
    """

    def __init__(self, raw_data, uuid):
        """Create a profile data wrapper.

        Args:
            raw_data: Full JSON response from Hypixel profile endpoint.
            uuid: Minecraft UUID of the requested player (used to select member data).
        """
        self._data = raw_data
        self._uuid = uuid
        self._logger = get_logger(_LOGGER_NAME_)

    def get_collection(self, collection_name: CollectionKey | str) -> int:
        """Get the amount collected for a specific collection.

        Args:
            collection_name: Collection key (e.g. "LOG", "WHEAT").
                Full list: :class:`~hypixelez.constants.CollectionKey`.

        Returns:
            Collection amount if present, otherwise 0.
        """
        try:
            return self._data["profile"]["members"][self._uuid]["collection"][
                collection_name
            ]
        except (KeyError, ValueError):
            self._logger.warning(f"Collection '{collection_name}' not found")
            return 0

    def get_slayer_stats(self, slayer_name) -> list:
        """Get slayer boss kill statistics by tiers.

        Args:
            slayer_name: Slayer id (e.g. "zombie", "spider", "wolf", ...).

        Returns:
            A list of tier kill counts if present, otherwise an empty list.

        Notes:
            The current implementation iterates over keys inside the slayer dict and
            appends values for keys that contain ``"boss_kills_tier"``.
            If you need stable ordering (tier1..tierN), consider sorting keys.
        """
        try:
            stats = list()
            for i in self._data["profile"]["members"][self._uuid]["slayer"][
                "slayer_bosses"
            ][slayer_name]:
                if "boss_kills_tier" in i:
                    stats.append(
                        self._data["profile"]["members"][self._uuid]["slayer"][
                            "slayer_bosses"
                        ][slayer_name][i]
                    )
            return stats
        except (KeyError, ValueError):
            self._logger.warning(f"Slayer '{slayer_name}' not found")
            return []

    def get_skill_level(self, skill_name) -> int:
        """Get the current level for a given SkyBlock skill.

        Args:
            skill_name: Skill XP key (e.g. "SKILL_CARPENTRY").

        Returns:
            Skill level if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["player_data"][
                    "experience"
                ][skill_name]
            )
            return _calculate_level(xp, _SKILL_CUMULATIVE_LEVELS_) - 1
        except (KeyError, ValueError):
            self._logger.warning(f"Skill '{skill_name}' not found")
            return 0

    def get_skill_current_level_xp(self, skill_name) -> int:
        """Get XP progress within the current level for a given skill.

        Args:
            skill_name: Skill XP key (e.g. "SKILL_CARPENTRY").

        Returns:
            Current level XP progress if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["player_data"][
                    "experience"
                ][skill_name]
            )

            return _calculate_current_xp(xp, _SKILL_CUMULATIVE_LEVELS_)
        except (KeyError, ValueError):
            self._logger.warning(f"Skill '{skill_name}' not found")
            return 0

    def get_cata_xp(self) -> int:
        """Get Catacombs XP progress within the current Catacombs level.

        Returns:
            Current Catacombs level XP progress if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["dungeons"][
                    "dungeon_types"
                ]["catacombs"]["experience"]
            )
            return _calculate_current_xp(xp, _CATA_CUMULATIVE_XP_)
        except (KeyError, ValueError):
            self._logger.warning(f"Catacomb not found")
            return 0

    def get_cata_level(self) -> int:
        """Get the Catacombs level.

        Returns:
            Catacombs level if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["dungeons"][
                    "dungeon_types"
                ]["catacombs"]["experience"]
            )
            return _calculate_level(xp, _CATA_CUMULATIVE_XP_)
        except (KeyError, ValueError):
            self._logger.warning(f"Catacomb not found")
            return 0

    def get_cata_class_xp(self, class_name) -> int:
        """Get dungeon class XP progress within the current class level.

        Args:
            class_name: Dungeon class id (e.g. "mage", "berserk", "archer", "tank", "healer").

        Returns:
            Current class level XP progress if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["dungeons"][
                    "player_classes"
                ][class_name]["experience"]
            )
            return _calculate_current_xp(xp, _CATA_CUMULATIVE_XP_)
        except (KeyError, ValueError):
            self._logger.warning(f"Class '{class_name}' not found")
            return 0

    def get_cata_class_level(self, class_name) -> int:
        """Get the dungeon class level.

        Args:
            class_name: Dungeon class id (e.g. "mage", "berserk", "archer", "tank", "healer").

        Returns:
            Class level if present, otherwise 0.
        """
        try:
            xp = int(
                self._data["profile"]["members"][self._uuid]["dungeons"][
                    "player_classes"
                ][class_name]["experience"]
            )
            return _calculate_level(xp, _CATA_CUMULATIVE_XP_)
        except (KeyError, ValueError):
            self._logger.warning(f"Class '{class_name}' not found")
            return 0

    def get_slayer_xp(self, slayer_name) -> int:
        """Get total slayer XP for a specific slayer.

        Args:
            slayer_name: Slayer id (e.g. "zombie", "spider", "wolf", ...).

        Returns:
            Total slayer XP if present, otherwise 0.
        """
        try:
            slayer_data = self._data["profile"]["members"][self._uuid]["slayer"][
                "slayer_bosses"
            ][slayer_name]
            return slayer_data.get("xp", 0)  # Явно обращаемся к полю xp
        except KeyError:
            return 0

    def get_slayer_level(self, slayer_name) -> int:
        """Get the slayer level derived from claimed levels.

        Args:
            slayer_name: Slayer id (e.g. "zombie", "spider", "wolf", ...).

        Returns:
            Highest claimed slayer level if present, otherwise 0.
        """
        try:
            claimed_levels = self._data["profile"]["members"][self._uuid]["slayer"][
                "slayer_bosses"
            ][slayer_name].get("claimed_levels", {})
            max_level = 0

            for level_key in claimed_levels:
                if level_key.startswith("level_"):
                    try:
                        level = int(level_key.split("_")[1])
                        max_level = max(max_level, level)
                    except (IndexError, ValueError):
                        continue
            return max_level
        except (KeyError, ValueError):
            self._logger.warning(f"Slayer '{slayer_name}' not found")
            return 0

    def get_slayer_stats_by_tier(self, slayer_name, tier) -> int:
        """Get slayer boss kill count for a specific tier.

        Args:
            slayer_name: Slayer id (e.g. "zombie", "spider", "wolf", ...).
            tier: Tier number (1-indexed). For example, tier=1 means "tier I".

        Returns:
            Kill count for the requested tier if present, otherwise 0.

        Notes:
            If `tier` is out of range, the implementation will fall back to 0.
        """
        try:
            return self.get_slayer_stats(slayer_name)[tier - 1]
        except (KeyError, ValueError):
            self._logger.warning(f"Slayer '{slayer_name}' with tier '{tier}' not found")
            return 0

    def get_global_level(self) -> int:
        """Get the global SkyBlock level.

        Returns:
            Global level if present, otherwise 0.

        Notes:
            The current implementation derives level as ``experience // 100``.
        """
        try:
            xp = self._data["profile"]["members"][self._uuid]["leveling"]["experience"]
            return xp // 100
        except (KeyError, ValueError):
            self._logger.warning(f"Global level not found")
            return 0

    def get_global_xp(self) -> int:
        """Get XP progress within the current global SkyBlock level.

        Returns:
            Current global level XP progress if present, otherwise 0.

        Notes:
            The current implementation derives progress as ``experience % 100``.
        """
        try:
            xp = self._data["profile"]["members"][self._uuid]["leveling"]["experience"]
            return xp % 100
        except (KeyError, ValueError):
            self._logger.warning(f"Global xp not found")
            return 0
