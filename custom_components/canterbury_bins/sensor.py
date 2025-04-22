"""Sensor platform for Canterbury Bins."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BIN_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Canterbury Bins sensors."""
    _LOGGER.debug("Setting up Canterbury Bins sensors")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    if not coordinator.data:
        _LOGGER.warning("No data available from coordinator")
        return

    _LOGGER.debug("Coordinator data: %s", coordinator.data)
    
    sensors = []
    for bin_key, bin_name in BIN_TYPES.items():
        # Create next collection sensor
        sensors.append(CanterburyBinsNextSensor(coordinator, bin_key, bin_name))
        # Create last collection sensor
        sensors.append(CanterburyBinsLastSensor(coordinator, bin_key, bin_name))
    
    _LOGGER.debug("Created %d sensors: %s", len(sensors), [s._attr_name for s in sensors])
    async_add_entities(sensors)

class CanterburyBinsNextSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Canterbury Bins next collection sensor."""

    def __init__(self, coordinator, bin_key: str, bin_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._bin_key = bin_key
        self._attr_name = f"Next {bin_name} Collection"
        self._attr_unique_id = f"canterbury_bins_next_{bin_key}"
        self._attr_icon = "mdi:delete-empty" if bin_key == "blackBinDay" else "mdi:recycle"
        _LOGGER.debug("Initialized next collection sensor: %s (key: %s)", self._attr_name, bin_key)

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data available for %s", self._attr_name)
            return None

        bin_data = self.coordinator.data.get(self._bin_key, {})
        next_date = bin_data.get("next_date")
        
        if not next_date:
            _LOGGER.debug("No next date available for %s", self._attr_name)
            return None

        try:
            # Add time component for midnight
            timestamp = f"{next_date}T00:00:00"
            _LOGGER.debug("Sensor %s value: %s", self._attr_name, timestamp)
            return timestamp
        except ValueError as err:
            _LOGGER.error("Error parsing date for %s: %s", self._attr_name, err)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data available for %s attributes", self._attr_name)
            return {}

        bin_data = self.coordinator.data.get(self._bin_key, {})
        next_date = bin_data.get("next_date")
        future_dates = bin_data.get("future_dates", 0)
        
        attributes = {
            "future_collections": future_dates
        }

        if not next_date:
            return attributes

        try:
            date = datetime.strptime(next_date, "%Y-%m-%d")
            days_until = (date - datetime.now()).days
            attributes.update({
                "days_until": days_until,
                "collection_date": date.strftime("%A, %d %B %Y")
            })
        except ValueError as err:
            _LOGGER.error("Error calculating days until for %s: %s", self._attr_name, err)

        return attributes

class CanterburyBinsLastSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Canterbury Bins last collection sensor."""

    def __init__(self, coordinator, bin_key: str, bin_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._bin_key = bin_key
        self._attr_name = f"Last {bin_name} Collection"
        self._attr_unique_id = f"canterbury_bins_last_{bin_key}"
        self._attr_icon = "mdi:delete-empty" if bin_key == "blackBinDay" else "mdi:recycle"
        _LOGGER.debug("Initialized last collection sensor: %s (key: %s)", self._attr_name, bin_key)

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data available for %s", self._attr_name)
            return None

        bin_data = self.coordinator.data.get(self._bin_key, {})
        last_collection = bin_data.get("last_collection", {})
        
        if not last_collection:
            _LOGGER.debug("No last collection available for %s", self._attr_name)
            return None

        timestamp = last_collection.get("timestamp")
        if not timestamp:
            return None

        _LOGGER.debug("Sensor %s value: %s", self._attr_name, timestamp)
        return timestamp

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data available for %s attributes", self._attr_name)
            return {}

        bin_data = self.coordinator.data.get(self._bin_key, {})
        last_collection = bin_data.get("last_collection", {})
        
        if not last_collection:
            return {}

        timestamp = last_collection.get("timestamp")
        try:
            # Try to parse the timestamp to format it nicely
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            formatted_time = dt.strftime("%H:%M")
        except ValueError:
            try:
                # Try without milliseconds
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                formatted_time = dt.strftime("%H:%M")
            except ValueError:
                formatted_time = "00:00"  # Fallback for midnight timestamps

        return {
            "collection_time": formatted_time,
            "collection_date": last_collection.get("date"),
            "outcome": last_collection.get("outcome"),
            "workpack": last_collection.get("workpack")
        } 