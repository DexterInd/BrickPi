To use custom I2C devices with the BrickPi, through the BrickPi.h drivers (for sensor ports 1-4, not sensor port 5).

You can configure the sensor port type as either `TYPE_SENSOR_I2C` or `TYPE_SENSOR_I2C_9V` (e.g. `BrickPi.SensorType[PORT_1] = TYPE_SENSOR_I2C;`). `TYPE_SENSOR_I2C_9V` sets up the sensor port for I2C (same as `TYPE_SENSOR_I2C`), and also turns on the 9v pullup on sensor port pin 1.

You can configure the I2C bus speed using `BrickPi.SensorI2CSpeed` (e.g. `BrickPi.SensorI2CSpeed[PORT_1] = 10;`). The speed is a delay used to slow down the I2C bus (in units of about 1uS), placed between each I2C bus transition. A value of 0 means no delay (max speed, which is usually around 100k). Because the BrickPi FW supports clock stretching, the maximum speed is dependant on the electrical characteristics of the bus (i.e. cable length). Most I2C slaves that use hardware I2C should support full speed (delay of 0).

You can configure the number of devices on an I2C bus using `BrickPi.SensorI2CDevices` (e.g. `BrickPi.SensorI2CDevices[PORT_1] = 3;`). This number can be 1 through 8. While this is typically used for situations of multiple physical slaves on a single I2C bus, it really just indicates how many independent I2C transactions should take place for every call to `BrickPiUpdateValues()`.

For each I2C device, you can set the I2C address (bits 1-7 of 0-7), using `BrickPi.SensorI2CAddr` (e.g. `BrickPi.SensorI2CAddr[PORT_1][2] = 0x10;` would set the I2C address of device 3 on sensor port 1 to 0x10).

For each I2C device, you can optionally set some transaction settings using `BrickPi.SensorSettings` (e.g. `BrickPi.SensorSettings[PORT_1][0] = (BIT_I2C_MID | BIT_I2C_SAME);` would set the settings of device 1 on sensor port 1 to use `BIT_I2C_MID` and `BIT_I2C_SAME`). The supported flags are `BIT_I2C_MID` and `BIT_I2C_SAME`. `BIT_I2C_MID` tells the BrickPi FW to issue a clock pulse between writing and reading bytes (this is contrary to the I2C standard, and as far as I know is only required by the Lego NXT Ultrasonic sensor). `BIT_I2C_SAME` tells the BrickPi FW that the I2C transactions for this device are always going to be the same, and to not expect to receive the length and output data with the values update. An example for when to use `BIT_I2C_SAME` is when you always want to write the byte 0x42, and then read 6 bytes (e.g. for polling a sensor).

For each I2C device, you can set the number of bytes to write using `BrickPi.SensorI2CWrite` (e.g. `BrickPi.SensorI2CWrite[PORT_1][1] = 4;` would set the number of bytes to write to device 2, to be 4).

For each I2C device, you can set the number of bytes to read using `BrickPi.SensorI2CRead` (e.g. `BrickPi.SensorI2CRead[PORT_1][4] = 0;` would set the number of bytes to write to device 5, to be 0).

There is an I2C write buffer for each I2C device, called `BrickPi.SensorI2COut`. You can access each byte using e.g. `BrickPi.SensorI2COut[PORT_1][3][0] = 137;` which would set port 1, device 4, write buffer byte 1 to 137.

There is an I2C read buffer for each I2C device, called `BrickPi.SensorI2CIn`. You can access each byte using e.g. `value = BrickPi.SensorI2CIn[PORT_1][5][3];` which would set value to port 1, device 6, read buffer byte 4.

The sensor type (e.g. `TYPE_SENSOR_I2C`), bus speed, number of devices, device I2C address(es), and device I2C settings, are sent to the BrickPi using function `BrickPiSetupSensors()`. In the case of the flag `BIT_I2C_SAME` being used for a device, the number of bytes to write and read, and the bytes to write are sent to the BrickPi when you call `BrickPiSetupSensors()`. If you don't use flag `BIT_I2C_SAME` for a device, the number of bytes to write and read, and the bytes to write are sent every time you call `BrickPiUpdateValues()`.
