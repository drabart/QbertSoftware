#!/usr/bin/env python3
import asyncio
import math
import time

import odrive
from odrive.enums import AxisState, ControlMode, InputMode
from odrive.utils import dump_errors, request_state, start_liveplotter, stop_liveplotter

async def main():
    # Find a connected ODrive (this will block until you connect one)
    print("waiting for ODrive...")
    odrv0 = await odrive.find_async()
    print(f"found ODrive {odrv0._dev.serial_number}")

    try:
        await odrv0.reboot()
    except odrive.libodrive.DeviceLostException:
        pass

    odrv0 = await odrive.find_async()
    print(f"found ODrive {odrv0._dev.serial_number}")

    start_liveplotter([
        odrv0.axis0.encoder.pos_estimate
    ])

    # Enter closed loop control
    await odrv0.axis0.controller.config.input_mode.write(InputMode.TRAP_TRAJ)
    # await odrv0.axis0.controller.config.input_mode.write(InputMode.PASSTHROUGH)
    await odrv0.axis0.controller.config.control_mode.write(ControlMode.POSITION_CONTROL)
    await request_state(odrv0.axis0, AxisState.CLOSED_LOOP_CONTROL)

    print(await odrv0.axis0.current_state.read())

    # Run a sine wave until ODrive reports an error or user hits Ctrl+C
    try:
        while await odrv0.axis0.current_state.read() == AxisState.CLOSED_LOOP_CONTROL:
            await odrv0.axis0.controller.input_pos.write(2000)
            while await odrv0.axis0.encoder.pos_estimate.read() < 1999.5:
                time.sleep(0.01)
            await odrv0.axis0.controller.input_pos.write(0)
            while await odrv0.axis0.encoder.pos_estimate.read() > 0.5:
                time.sleep(0.01)

    finally:
        await request_state(odrv0.axis0, AxisState.IDLE)

    await dump_errors(odrv0)

    # Some more things you can try:

    # Directly assigning to a property is not allowed on an object obtained from
    # `odrive.find_async()`. See also `odrive.find_any_sync()`.
    odrv0.axis0.controller.input_pos = 1.23 # fails with `AttributeError`

    # Write to a read-only property:
    await odrv0.vbus_voltage.write(11.0)  # fails with `AttributeError: This property cannot be written to.`

    # Assign an incompatible value:
    await odrv0.axis0.controller.input_pos.write("I like trains")  # fails with `ValueError: could not convert string to float`

if __name__ == "__main__":
    asyncio.run(main())
