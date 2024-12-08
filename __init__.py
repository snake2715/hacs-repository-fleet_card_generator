"""Fleet Card Generator Integration."""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fleet_card_generator"

async def async_setup(hass, config):
    """Set up the Fleet Card Generator integration."""
    _LOGGER.info("Setting up Fleet Card Generator")
    # Initialization code goes here

    return True 