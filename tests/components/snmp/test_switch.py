"""SNMP switch tests."""

from unittest.mock import patch

from pysnmp.proto.rfc1902 import Integer32
import pytest

from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

config = {
    SWITCH_DOMAIN: {
        "platform": "snmp",
        "host": "192.0.2.1",
        # NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger
        "baseoid": "1.3.6.1.4.1.8072.2.1.1",
        "payload_on": 1,
        "payload_off": 0,
    },
}


async def test_snmp_integer_switch_state_returns_off(hass: HomeAssistant) -> None:
    """Test snmp switch returning integer payload_off using SNMPv2c."""

    config[SWITCH_DOMAIN]["version"] = "2c"
    mock_data = Integer32(config[SWITCH_DOMAIN]["payload_off"])

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        assert await async_setup_component(hass, SWITCH_DOMAIN, config)
        await hass.async_block_till_done()
        state = hass.states.get("switch.snmp")

    assert state.state == STATE_OFF


async def test_snmp_integer_switch_state_returns_on(hass: HomeAssistant) -> None:
    """Test snmp switch returning integer payload_on using SNMPv3."""

    config[SWITCH_DOMAIN]["version"] = "3"
    mock_data = Integer32(config[SWITCH_DOMAIN]["payload_on"])

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        assert await async_setup_component(hass, SWITCH_DOMAIN, config)
        await hass.async_block_till_done()
        state = hass.states.get("switch.snmp")

    assert state.state == STATE_ON


async def test_snmp_integer_switch_state_returns_unknown(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """Test snmp switch returning int 3 (not a configured payload) for unknown."""

    mock_data = Integer32(3)

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        assert await async_setup_component(hass, SWITCH_DOMAIN, config)
        await hass.async_block_till_done()
        state = hass.states.get("switch.snmp")

    assert state.state == STATE_UNKNOWN
    assert "Invalid payload '3' received for entity" in caplog.text


async def test_snmp_integer_switch_turn_on(hass: HomeAssistant) -> None:
    """Test turning on SNMP switch with payload_on configured as integer, returning integer payload_on, no command_payload_on configured."""

    mock_data = Integer32(config[SWITCH_DOMAIN]["payload_on"])

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        assert await async_setup_component(hass, SWITCH_DOMAIN, config)
        await hass.async_block_till_done()

    with patch(
        "homeassistant.components.snmp.switch.setCmd",
        # https://github.com/etingof/pysnmp/blob/master/pysnmp/hlapi/v3arch/asyncio/cmdgen.py#L168
        return_value=(None, None, None, [[mock_data]]),
    ):
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "switch.snmp"},
            blocking=True,
        )

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        state = hass.states.get("switch.snmp")

    assert state.state == STATE_ON


async def test_snmp_integer_switch_turn_off(hass: HomeAssistant) -> None:
    """Test turning on SNMP switch with payload_on configured as integer, returning integer payload_on, no command_payload_on configured."""

    mock_data = Integer32(config[SWITCH_DOMAIN]["payload_off"])

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        assert await async_setup_component(hass, SWITCH_DOMAIN, config)
        await hass.async_block_till_done()

    with patch(
        "homeassistant.components.snmp.switch.setCmd",
        # https://github.com/etingof/pysnmp/blob/master/pysnmp/hlapi/v3arch/asyncio/cmdgen.py#L168
        return_value=(None, None, None, [[mock_data]]),
    ):
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "switch.snmp"},
            blocking=True,
        )

    with patch(
        "homeassistant.components.snmp.switch.getCmd",
        return_value=(None, None, None, [[mock_data]]),
    ):
        state = hass.states.get("switch.snmp")

    assert state.state == STATE_OFF
