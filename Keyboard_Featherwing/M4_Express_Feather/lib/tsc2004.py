# SPDX-FileCopyrightText: 2021 arturo182 for Solder Party AB
#
# SPDX-License-Identifier: MIT
"""
`tsc2004`
================================================================================

CircuitPython driver for the TSC2004 resistive touch sensor

* Author(s): arturo182

Implementation Notes
--------------------

**Hardware:**

* `Keyboard FeatherWing <https://www.tindie.com/products/20905/>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
import time

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/solderparty/arturo182_CircuitPython_tsc2004.git"


_TSC2004_ADDR = const(0x4B)

_MAX_12BIT    = 0x0fff
_RESISTOR_VAL = 280

# Control Byte 0
_TSC2004_REG_READ      = const(0x01)
_TSC2004_REG_PND0      = const(0x02)
_TSC2004_REG_X         = const(0x0 << 3)
_TSC2004_REG_Y         = const(0x1 << 3)
_TSC2004_REG_Z1        = const(0x2 << 3)
_TSC2004_REG_Z2        = const(0x3 << 3)
_TSC2004_REG_AUX       = const(0x4 << 3)
_TSC2004_REG_TEMP1     = const(0x5 << 3)
_TSC2004_REG_TEMP2     = const(0x6 << 3)
_TSC2004_REG_STATUS    = const(0x7 << 3)
_TSC2004_REG_AUX_HIGH  = const(0x8 << 3)
_TSC2004_REG_AUX_LOW   = const(0x9 << 3)
_TSC2004_REG_TEMP_HIGH = const(0xA << 3)
_TSC2004_REG_TEMP_LOW  = const(0xB << 3)
_TSC2004_REG_CFR0      = const(0xC << 3)
_TSC2004_REG_CFR1      = const(0xD << 3)
_TSC2004_REG_CFR2      = const(0xE << 3)
_TSC2004_REG_CONV_FUNC = const(0xF << 3)

# Control Byte 1
_TSC2004_CMD        = const(1 << 7)
_TSC2004_CMD_NORMAL = const(0x00)
_TSC2004_CMD_STOP   = const(1 << 0)
_TSC2004_CMD_RESET  = const(1 << 1)
_TSC2004_CMD_12BIT  = const(1 << 2)

# Config Register 0
CFR0_PRECHARGE_20US    = const(0x00 << 5)
CFR0_PRECHARGE_84US    = const(0x01 << 5)
CFR0_PRECHARGE_276US   = const(0x02 << 5)
CFR0_PRECHARGE_340US   = const(0x03 << 5)
CFR0_PRECHARGE_1_044MS = const(0x04 << 5)
CFR0_PRECHARGE_1_108MS = const(0x05 << 5)
CFR0_PRECHARGE_1_300MS = const(0x06 << 5)
CFR0_PRECHARGE_1_364MS = const(0x07 << 5)

CFR0_STABTIME_0US   = const(0x00 << 8)
CFR0_STABTIME_100US = const(0x01 << 8)
CFR0_STABTIME_500US = const(0x02 << 8)
CFR0_STABTIME_1MS   = const(0x03 << 8)
CFR0_STABTIME_5MS   = const(0x04 << 8)
CFR0_STABTIME_10MS  = const(0x05 << 8)
CFR0_STABTIME_50MS  = const(0x06 << 8)
CFR0_STABTIME_100MS = const(0x07 << 8)

CFR0_CLOCK_4MHZ      = const(0x00 << 11)
CFR0_CLOCK_2MHZ      = const(0x01 << 11)
CFR0_CLOCK_1MHZ      = const(0x02 << 11)

CFR0_12BIT           = const(1 << 13)
CFR0_STATUS          = const(1 << 14)
CFR0_PENMODE         = const(1 << 15)

# Config Register 1
CFR1_BATCHDELAY_0MS   = (0x00 << 0)
CFR1_BATCHDELAY_1MS   = (0x01 << 0)
CFR1_BATCHDELAY_2MS   = (0x02 << 0)
CFR1_BATCHDELAY_4MS   = (0x03 << 0)
CFR1_BATCHDELAY_10MS  = (0x04 << 0)
CFR1_BATCHDELAY_20MS  = (0x05 << 0)
CFR1_BATCHDELAY_40MS  = (0x06 << 0)
CFR1_BATCHDELAY_100MS = (0x07 << 0)

# Config Register 2
CFR2_MAVE_Z    = (1 << 2)
CFR2_MAVE_Y    = (1 << 3)
CFR2_MAVE_X    = (1 << 4)
CFR2_AVG_7     = (0x01 << 11)
CFR2_MEDIUM_15 = (0x03 << 12)

STATUS_DAV_X    = 0x8000
STATUS_DAV_Y    = 0x4000
STATUS_DAV_Z1   = 0x2000
STATUS_DAV_Z2   = 0x1000
STATUS_DAV_MASK = (STATUS_DAV_X | STATUS_DAV_Y | STATUS_DAV_Z1 | STATUS_DAV_Z2)


class TSC2004:
    def __init__(self, i2c, address=_TSC2004_ADDR):
        self._i2c = I2CDevice(i2c, address)
        self._buffer = bytearray(3)

        self.reset()

        cfr0 = (CFR0_STABTIME_1MS | CFR0_CLOCK_1MHZ | CFR0_12BIT | CFR0_PRECHARGE_276US | CFR0_PENMODE)
        self._write_register(_TSC2004_REG_CFR0, cfr0)

        self._write_register(_TSC2004_REG_CFR1, CFR1_BATCHDELAY_4MS)

        cfr2 = (CFR2_MAVE_Z | CFR2_MAVE_Y | CFR2_MAVE_X | CFR2_AVG_7 | CFR2_MEDIUM_15)
        self._write_register(_TSC2004_REG_CFR2, cfr2)

        self._write_cmd(_TSC2004_CMD_NORMAL)

    def reset(self):
        self._write_cmd(_TSC2004_CMD_RESET)

    @property
    def touched(self):
        touching = self._read_register(_TSC2004_REG_CFR0) & (CFR0_PENMODE | CFR0_STATUS)
        return touching != 0

    @property
    def get_point(self):
        (x, y, pressure) = self.read_data()
        return {'x': x, 'y': y, 'pressure': pressure}

    @property
    def touches(self):
        touches = []

        tries = 5
        prev = (0, 0, 0)

        while (tries > 0):
            (x, y, pressure) = self.read_data()

            # Fuzzy compare to filter out if change was too small
            if (abs(prev[0] - x) < 4) or (abs(prev[1] - y) < 8) or (abs(prev[2] - pressure) < 2):
                continue

            if (x > 0) and (y > 0) and (pressure > 0):
                touches.append({'x': x, 'y': y, 'pressure': pressure})
                prev = (x, y, pressure)

            tries -= 1

        return touches

    def read_data(self):
        while (self._read_register(_TSC2004_REG_STATUS) & STATUS_DAV_MASK) == 0:
            pass

        x = self._read_register(_TSC2004_REG_X)
        y = self._read_register(_TSC2004_REG_Y)
        z1 = self._read_register(_TSC2004_REG_Z1)
        z2 = self._read_register(_TSC2004_REG_Z2)

        if (x > _MAX_12BIT) or (y > _MAX_12BIT) or (z1 == 0) or (z2 > _MAX_12BIT) or (z1 >= z2):
            return (0, 0, 0)

        pressure  = x * (z2 - z1) / z1
        pressure *= _RESISTOR_VAL / 4096

        return (x, y, pressure)

    def touch_point(self):
        if (self._read_register(_TSC2004_REG_STATUS) & STATUS_DAV_MASK) == 0:
            return (-1,-1,-1)
        else:
            x = self._read_register(_TSC2004_REG_X)
            y = self._read_register(_TSC2004_REG_Y)
            z1 = self._read_register(_TSC2004_REG_Z1)
            z2 = self._read_register(_TSC2004_REG_Z2)
            if (x > _MAX_12BIT) or (y > _MAX_12BIT) or (z1 == 0) or (z2 > _MAX_12BIT) or (z1 >= z2):
                return (0, 0, 0)
            pressure  = x * (z2 - z1) / z1
            pressure *= _RESISTOR_VAL / 4096
            return (x, y, pressure)

    def _write_cmd(self, cmd):
        with self._i2c as i2c:
            self._buffer[0] = _TSC2004_CMD | _TSC2004_CMD_12BIT | cmd
            i2c.write(self._buffer, end=1)

    def _read_register(self, reg):
        with self._i2c as i2c:
            self._buffer[0] = reg | _TSC2004_REG_READ
            i2c.write(self._buffer, end=1)
            i2c.readinto(self._buffer, end=2)

        return (self._buffer[0] << 8 | self._buffer[1])

    def _write_register(self, reg, value):
        with self._i2c as i2c:
            self._buffer[0] = reg | _TSC2004_REG_PND0
            self._buffer[1] = (value >> 8) & 0xFF
            self._buffer[2] = (value >> 0) & 0xFF
            i2c.write(self._buffer, end=3)

