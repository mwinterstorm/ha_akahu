import asyncio
from typing import Any, Dict, Optional

import voluptuous as vol
from aiohttp import ClientError, ClientResponseError
from async_timeout import timeout

from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, API_HOST

CONF_APP_TOKEN = "app_token"

class AkahuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Akahu."""
    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Ensure only one config entry (or one per app_token if that’s your model)
            # If app_token uniquely identifies an Akahu app, prefer using that.
            await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_APP_TOKEN]}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            headers = {
                "Authorization": f"Bearer {user_input[CONF_TOKEN]}",
                "X-Akahu-ID": user_input[CONF_APP_TOKEN],
            }

            try:
                async with timeout(15):
                    async with session.get(f"{API_HOST}/me", headers=headers) as resp:
                        # Explicit handling is nicer than generic raise_for_status
                        if resp.status == 200:
                            return self.async_create_entry(title="Akahu", data=user_input)
                        if resp.status in (401, 403):
                            errors["base"] = "invalid_auth"
                        elif resp.status in (429, 500, 502, 503, 504):
                            errors["base"] = "cannot_connect"
                        else:
                            errors["base"] = "unknown"

            except ClientResponseError as e:
                if e.status in (401, 403):
                    errors["base"] = "invalid_auth"
                elif e.status in (429, 500, 502, 503, 504):
                    errors["base"] = "cannot_connect"
                else:
                    errors["base"] = "unknown"
            except (asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APP_TOKEN): str,
                vol.Required(CONF_TOKEN): str,
            }),
            errors=errors,
        )
