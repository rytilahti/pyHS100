import datetime
import logging

from .pyHS100 import SmartDevice

_LOGGER = logging.getLogger(__name__)


class SmartPlug(SmartDevice):
    """Representation of a TP-Link Smart Switch.

    Usage example when used as library:
    p = SmartPlug("192.168.1.105")
    # print the devices alias
    print(p.alias)
    # change state of plug
    p.state = "ON"
    p.state = "OFF"
    # query and print current state of plug
    print(p.state)

    Errors reported by the device are raised as SmartPlugExceptions,
    and should be handled by the user of the library.

    Note:
    The library references the same structure as defined for the D-Link Switch
    """
    # switch states
    SWITCH_STATE_ON = 'ON'
    SWITCH_STATE_OFF = 'OFF'
    SWITCH_STATE_UNKNOWN = 'UNKNOWN'

    # possible device features
    FEATURE_ENERGY_METER = 'ENE'
    FEATURE_TIMER = 'TIM'

    ALL_FEATURES = (FEATURE_ENERGY_METER, FEATURE_TIMER)

    def __init__(self, ip_address, protocol=None):
        SmartDevice.__init__(self, ip_address, protocol)
        self.emeter_type = "emeter"
        self.emeter_units = False

    @property
    def state(self):
        """
        Retrieve the switch state

        :returns: one of
                  SWITCH_STATE_ON
                  SWITCH_STATE_OFF
                  SWITCH_STATE_UNKNOWN
        :rtype: str
        """
        relay_state = self.sys_info['relay_state']

        if relay_state == 0:
            return SmartPlug.SWITCH_STATE_OFF
        elif relay_state == 1:
            return SmartPlug.SWITCH_STATE_ON
        else:
            _LOGGER.warning("Unknown state %s returned.", relay_state)
            return SmartPlug.SWITCH_STATE_UNKNOWN

    @state.setter
    def state(self, value):
        """
        Set the new switch state

        :param value: one of
                    SWITCH_STATE_ON
                    SWITCH_STATE_OFF
        :raises ValueError: on invalid state
        :raises SmartPlugException: on error

        """
        if not isinstance(value, str):
            raise ValueError("State must be str, not of %s.", type(value))
        elif value.upper() == SmartPlug.SWITCH_STATE_ON:
            self.turn_on()
        elif value.upper() == SmartPlug.SWITCH_STATE_OFF:
            self.turn_off()
        else:
            raise ValueError("State %s is not valid.", value)

    @property
    def is_on(self):
        """
        Returns whether device is on.

        :return: True if device is on, False otherwise
        """
        return bool(self.sys_info['relay_state'])

    def turn_on(self):
        """
        Turn the switch on.

        :raises SmartPlugException: on error
        """
        self._query_helper("system", "set_relay_state", {"state": 1})

    def turn_off(self):
        """
        Turn the switch off.

        :raises SmartPlugException: on error
        """
        self._query_helper("system", "set_relay_state", {"state": 0})

    @property
    def has_emeter(self):
        """
        Checks feature list for energey meter support.

        :return: True if energey meter is available
                 False if energymeter is missing
        """
        return SmartPlug.FEATURE_ENERGY_METER in self.features

    @property
    def features(self):
        """
        Returns features of the devices

        :return: list of features
        :rtype: list
        """
        features = self.sys_info['feature'].split(':')

        for feature in features:
            if feature not in SmartPlug.ALL_FEATURES:
                _LOGGER.warning("Unknown feature %s on device %s.",
                                feature, self.model)

        return features

    @property
    def led(self):
        """
        Returns the state of the led.

        :return: True if led is on, False otherwise
        :rtype: bool
        """
        return bool(1 - self.sys_info["led_off"])

    @led.setter
    def led(self, state):
        """
        Sets the state of the led (night mode)

        :param bool state: True to set led on, False to set led off
        :raises SmartPlugException: on error
        """
        self._query_helper("system", "set_led_off", {"off": int(not state)})

    @property
    def on_since(self):
        """
        Returns pretty-printed on-time

        :return: datetime for on since
        :rtype: datetime
        """
        return datetime.datetime.now() - \
            datetime.timedelta(seconds=self.sys_info["on_time"])
