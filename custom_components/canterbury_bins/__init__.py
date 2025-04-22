"""The Canterbury Bins integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
import json
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_UPRN,
    CONF_USRN,
    API_URL,
    UPDATE_INTERVAL,
    BIN_TYPES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Canterbury Bins from a config entry."""
    _LOGGER.debug("Setting up Canterbury Bins integration")
    coordinator = CanterburyBinsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, ["sensor"]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class CanterburyBinsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Canterbury Bins data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.uprn = entry.data[CONF_UPRN]
        self.usrn = entry.data[CONF_USRN]
        self._session = aiohttp.ClientSession()
        _LOGGER.debug("Initialized coordinator with UPRN: %s, USRN: %s", self.uprn, self.usrn)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via API."""
        try:
            _LOGGER.debug("Fetching data from API")
            async with async_timeout.timeout(10):
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-GB,en;q=0.5",
                    "Content-Type": "application/json",
                    "Origin": "https://www.canterbury.gov.uk",
                }
                
                data = {
                    "uprn": self.uprn,
                    "usrn": self.usrn
                }

                _LOGGER.debug("Making API request to %s with data: %s", API_URL, data)
                async with self._session.post(API_URL, headers=headers, json=data) as response:
                    if response.status != 200:
                        _LOGGER.error("API request failed with status %d", response.status)
                        raise UpdateFailed(f"Error communicating with API: {response.status}")

                    result = await response.json()
                    _LOGGER.debug("Raw API response: %s", result)
                    
                    dates = json.loads(result.get("dates", "{}"))
                    status = json.loads(result.get("status", "{}"))
                    _LOGGER.debug("Parsed dates: %s", dates)
                    _LOGGER.debug("Parsed status: %s", status)
                    
                    # Process each bin type's dates
                    processed_dates = {}
                    for bin_key, bin_name in BIN_TYPES.items():
                        date_list = dates.get(bin_key, [])
                        if date_list:
                            # Sort dates to get the next collection date
                            date_list.sort()
                            next_date_str = date_list[0].split('T')[0]  # Remove time portion
                            processed_dates[bin_key] = {
                                "next_date": next_date_str,
                                "future_dates": len(date_list) - 1
                            }
                            _LOGGER.debug("Processed dates for %s: %s", bin_key, processed_dates[bin_key])
                        else:
                            processed_dates[bin_key] = {
                                "next_date": None,
                                "future_dates": 0
                            }
                            _LOGGER.debug("No dates found for %s", bin_key)
                    
                    # Process status information
                    street_status = status.get("streetStatus", [])
                    last_collections = {}
                    _LOGGER.debug("Processing street status: %s", street_status)
                    
                    # First, group events by bin type
                    events_by_bin = {}
                    for event in street_status:
                        event_type = event.get("type", "").lower()
                        # Map event types to our bin keys
                        bin_key = {
                            "general": "blackBinDay",
                            "recycling": "recyclingBinDay",
                            "food": "foodBinDay",
                            "garden": "gardenBinDay"
                        }.get(event_type)
                        
                        if bin_key:
                            if bin_key not in events_by_bin:
                                events_by_bin[bin_key] = []
                            events_by_bin[bin_key].append(event)
                    
                    # Then find the most recent event for each bin type
                    for bin_key, events in events_by_bin.items():
                        if events:
                            # Sort events by date (newest first)
                            events.sort(key=lambda x: x.get("date", ""), reverse=True)
                            most_recent = events[0]
                            
                            timestamp = most_recent.get("date", "")
                            outcome = most_recent.get("outcome", "")
                            workpack = most_recent.get("workpack", "")
                            
                            last_collections[bin_key] = {
                                "timestamp": timestamp,
                                "date": timestamp.split('T')[0],  # Keep date-only version for compatibility
                                "outcome": outcome,
                                "workpack": workpack
                            }
                            _LOGGER.debug("Most recent collection for %s: %s", bin_key, last_collections[bin_key])
                    
                    # Add last collection info to processed dates
                    for bin_key in processed_dates:
                        if bin_key in last_collections:
                            processed_dates[bin_key]["last_collection"] = last_collections[bin_key]
                            _LOGGER.debug("Added last collection info to %s: %s", bin_key, last_collections[bin_key])
                    
                    _LOGGER.debug("Final processed data: %s", processed_dates)
                    return processed_dates

        except Exception as err:
            _LOGGER.exception("Error in _async_update_data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def async_unload(self):
        """Unload the coordinator."""
        await self._session.close() 