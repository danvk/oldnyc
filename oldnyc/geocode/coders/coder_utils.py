from typing import Any

from oldnyc.geocode.geocode_types import Locatable


def get_lat_lng_from_geocode(
    geocode: dict[str, Any], data: Locatable
) -> tuple[str, float, float] | None:
    """Extract a location from a Google Maps geocoding API response if it has the expected type."""
    desired_types = data["type"]
    if not isinstance(desired_types, list):
        desired_types = [desired_types]
    for data_type in desired_types:
        # N = len(geocode["results"])
        for i, result in enumerate(geocode["results"]):
            # partial matches tend to be inaccurate.
            # if result.get('partial_match'): continue
            # data['type'] is something like 'address' or 'intersection'.
            if data_type in result["types"]:
                # sys.stderr.write(f"Match on {i} / {N}: {result}\n")
                loc = result["geometry"]["location"]
                return (data_type, loc["lat"], loc["lng"])
