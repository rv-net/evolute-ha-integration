"""Shared entity helpers for the Evolute integration."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


def build_device_info(car: dict[str, Any]) -> DeviceInfo:
    """Return the device registry entry shared by every entity of one car."""
    model = car.get("model")
    modification = car.get("modification")
    model_year = car.get("model_year")

    info: DeviceInfo = {
        "identifiers": {(DOMAIN, car["car_id"])},
        "name": car.get("name") or f"Evolute {car['car_id']}",
        "manufacturer": "Evolute",
        "model": model,
        "suggested_area": "Garage",
    }
    if modification:
        info["model_id"] = modification
    if car.get("vin"):
        info["serial_number"] = car["vin"]
    if model_year:
        info["hw_version"] = str(model_year)
    return info


def car_supports(car: dict[str, Any], key: str, unsupported_v2: tuple[str, ...]) -> bool:
    """Whether an entity key has any data source for this car."""
    return not (car.get("telemetry_v2") and key in unsupported_v2)


def remove_stale_entities(
    hass: HomeAssistant,
    platform: str,
    car: dict[str, Any],
    unsupported_v2: tuple[str, ...],
) -> None:
    """Drop entities an older version created that this car can never fill."""
    if not car.get("telemetry_v2"):
        return
    registry = er.async_get(hass)
    for key in unsupported_v2:
        entity_id = registry.async_get_entity_id(
            platform, DOMAIN, f"evolute_{car['car_id']}_{key}"
        )
        if entity_id:
            registry.async_remove(entity_id)
