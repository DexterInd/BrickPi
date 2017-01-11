#!/usr/bin/env python
# ThreadSafeBrickPi.py
#
# Frans Duijnhouwer
# frans.duijnhouwer<at>gmail.com
#
# Initial Date: January 28, 2014
# Last Updated: February 11, 2014
#
# This file has been made available online through a Creative Commons 
# Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Thread safe interface to the BrickPi
# This file defines the BrickPiCom class that provides a thread safe interface
# to the BrickPi. The implementation is based on the BrickPi.py interface
# written by: Jaikrishna, Karan Nayan and John Cole

###############################################################################
# Debugging:
# - NOTE THAT DEBUGGING ERROR MESSAGES ARE TURNED OFF BY DEFAULT.
#   To debug, just delete the '#'-character at the front of line 30.


from BrickPi import *
import threading
import time
import sys
import importlib

# DEBUG = 1  # Remove to hide debugging messages

BrickPiThreadLock = threading.Lock()

def class_for_name(class_name, module_name=""):
    if(module_name == ""):
        m = sys.modules[__name__]
    else:
      # load the module, will raise ImportError if module cannot be loaded
      m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

# A special metaclass to implement the singleton pattern in python.
class Singleton(type):
    _instances = {}
    def __call__( cls, *args, **kwargs ):
        debug = 0

        try:
            BrickPiThreadLock.acquire()

            if 'DEBUG' in globals():
                if DEBUG >= 1:
                    debug = 1

            if cls not in cls._instances:
                cls._instances[cls] = super( Singleton, cls ).__call__( *args, **kwargs )

                if debug:
                    print "DEBUG: Instantiating singleton class."

            elif debug:
                print "DEBUG: Singleton class already instantiated"

            return cls._instances[cls]
        finally:
            BrickPiThreadLock.release()

# Exception class
class BrickPiException(Exception):
        def __init__(self, msg):
            self._msg = msg
        def __str__(self):
            return repr(self._msg)


# The BrickPiCom class serializes calls to BrickPiSetupSensors and
# BrickPiUpdateValues. This is accomplished by acquiring the module
# global 'BrickPiThreadLock' before calling those BrickPi functions
# and releasing the lock when done.
# The class has been designed to minimize calls to these functions,
# but also to be flexible enough to support I2C sensors with
# complicated setup requirements.
class BrickPiCom:
    __metaclass__ = Singleton

    # Nested Motor class
    class Motor:
        def __init__(self, port):
            self._lock = threading.Lock()
            self._port = port

        def __str__(self):
            msg = ("Motor on port %d\n  id: %d\n  enabled: %d\n  power: %d\n" 
                % (self._port, id(self), BrickPi.MotorEnable[self._port],
                   BrickPi.MotorSpeed[self._port]))
            return msg

        def get_port(self):
            return self._port

        def enable(self):
            self._lock.acquire()
            try:
                BrickPi.MotorEnable[self._port] = 1
            finally:
                self._lock.release()

        def disable(self):
            self._lock.acquire()
            try:
                BrickPi.MotorEnable[self._port] = 0
            finally:
                self._lock.release()

        def is_enabled(self):
            return self._enabled

        def set_power(self, p):
            self._lock.acquire()
            try:
                BrickPi.MotorSpeed[self._port] = max(-255, min(255, p))
            finally:
                self._lock.release()

        def get_power(self):
            return BrickPi.MotorSpeed[self._port]

        def set_encoder(self, encoder=0):
            self._lock.acquire()
            try:
                BrickPi.EncoderOffset[self._port] = (
                    BrickPi.Encoder[self._port] - encoder)
            finally:
                self._lock.release()

        def get_encoder(self):
            return BrickPi.Encoder[self._port]

    # Construction
    def __init__(self, minimumUpdateInterval=0.0):
        self._motors = [None] * 4
        self._sensors = [[] for i in range(4)]
        self._sensorClassNames = [[] for i in range(4)]
        self._sensorType = [-1] * 4
        self._i2cAddress = [[] for i in range(4)]
        self._timeLastUpdate = time.time()
        self._minimumUpdateInterval = minimumUpdateInterval
        BrickPiSetup()

        if 'DEBUG' in globals():
            if DEBUG >= 1:
              print "DEBUG: BrickPiCom created."

    #
    # TODO: description of interface method
    #
    def register_motor(self, port, enabled=True, power=0, encoder=0):
        BrickPiThreadLock.acquire()
        debug = 0

        try:
            if 'DEBUG' in globals():
                if DEBUG >= 1:
                    debug = 1
                    print("DEBUG: BrickPiCom: register_motor, START\n"
                          "       Motor on port %d" % (port))
            motor = self._motors[port]
            if(motor == None):
                # No motor registered on this port yet.
                BrickPi.MotorEnable[port] = 1
                BrickPi.MotorSpeed[port] = 0
                result = BrickPiUpdateValues()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiUpdateValues failed with code: %d"
                           % (result))
                    raise BrickPiException(msg)

                motor = BrickPiCom.Motor(port)
                self._motors[port] = motor
                motor.set_encoder(encoder) # Reset the encoder
                motor.enable()
                motor.set_power(0)
                result = BrickPiUpdateValues()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiUpdateValues failed with code: %d"
                           % (result))
                    raise BrickPiException(msg)

                motor.set_power(power)

                if not enabled:
                    motor.disable()

                if debug:
                    print("DEBUG: BrickPiCom: added new motor, encoder: %d\n"
                        % (motor.get_encoder()))
            else:
                # A motor has already been registered on this port.
                # Just return a reference.
                if debug:
                    print "DEBUG: BrickPiCom: motor already registered"
            return motor
        except BrickPiException as e:
            print("ERROR: BrickPiCom::register_motor: "
                  "an exception occurred and processing has been aborted. "
                  "The exception message was:\n%s\n" % (e))
            raise # Re-throw.
        finally:
            if(debug):
                print self._motors[port]
                print self._motors
                print "DEBUG: BrickPiCom::register_motor, END"
            BrickPiThreadLock.release()

    # Thread safe sensors are specializations of class BrickPiSensor.
    # They need to be registered with BrickPiCom.
    #
    def register_sensor(self, sensorClassName, sensorModuleName, port, *args):
        BrickPiThreadLock.acquire()
        debug = 0

        try:
            if 'DEBUG' in globals():
                if DEBUG >= 1:
                    debug = 1
                    print("DEBUG: BrickPiCom::register_sensor, START\n"
                          "       Sensor class %s on port %d"
                          % (sensorClassName, port))
            # First check
            sensor, flagNew = self.__check_sensor(
                sensorClassName, sensorModuleName, port, debug, *args)

            if flagNew:
                # Add the new sensor instance
                deviceIndex = self.__add_sensor(
                    sensor, port, sensorClassName, debug)
                # Initialize the sensor.
                self.__initialize_sensor(
                    sensor, port, deviceIndex, sensorClassName, debug)
            return sensor
        except BrickPiException as e:
            print("ERROR: BrickPiCom::register_sensor: "
                  "an exception occurred and processing has been aborted. "
                  "The exception message was:\n%s\n" % (e))
            raise # Re-throw.
        finally:
            if(debug):
                print "DEBUG: Sensor class names:", self._sensorClassNames
                print "DEBUG: Sensor type codes :", self._sensorType
                print "DEBUG: I2C addresses     :", self._i2cAddress
                print "DEBUG: BrickPiCom::register_sensor, END"
            BrickPiThreadLock.release()

    # When a thread needs input from the sensors it registered, 
    # it calls the BrickPiCom.update() method.
    #
    def update(self):
        BrickPiThreadLock.acquire()
        debug = 0
        try:
            if 'DEBUG' in globals():
                if DEBUG >= 1:
                    debug = 1
                    print "DEBUG: BrickPiCom::update START"

            # Different threads can call this method, so many updates may be
            # requested in a very short time interval. Some sensors may not
            # handle this very well (LEGO US sensor?). Therefore, a minimum
            # update interval can be set. If update is called within
            # _minimumUpdateInterval after the last call, it is ignored.
            dt = time.time() - self._timeLastUpdate
            if(dt < self._minimumUpdateInterval):
                if debug:
                    print("DEBUG: Skipping update within minimum update "
                        "interval (%f), dt = %f" 
                        % (self._minimumUpdateInterval, dt))
                return 0

            # Allow the sensors to perform setup if necessary
            self.__setup_sensors(debug)

            if debug:
                print("DEBUG: BrickPiCom::update: calling BrickPiUpdateValues")

            # Update
            result = BrickPiUpdateValues()

            # Update the last call time
            self._timeLastUpdate = time.time()

            if(result):
                msg = "BrickPiUpdateValues failed with code: %d" % (result)
                raise BrickPiException(msg)

            for i in range(4):
                for j in range(len(self._sensors[i])):
                    s = self._sensors[i][j]
                    if(self._sensorType[i] in
                       [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
                        eds = s.callback_expected_data_size()
                        if eds:
                            if(BrickPi.Sensor[i] & (0x01 << j)):
                                s.callback_update(
                                    BrickPi.SensorI2CIn[i][j][0:eds]) 
                            elif debug:
                                print("WARNING: BrickPiCom::update: I2C sensor "
                                    "%s on port %d failed to return values." %
                                    (self._sensorClassNames[i][j], i))
                        else:
                            print("DEBUG: Sensor %s on port %d does not expect "
                                  "data; no update required." 
                                  % (self._sensorClassNames[i][j], i))
                    else:
                        # None-I2C sensors are always updated.
                        s.callback_update(BrickPi.Sensor[i])
            if debug:
                print "DEBUG: encoder offset :", BrickPi.EncoderOffset
                print "DEBUG: motor enabled  :", BrickPi.MotorEnable
                print "DEBUG: motor speed    :", BrickPi.MotorSpeed
                print "DEBUG: motor objects  :", self._motors
            return 0
        except BrickPiException as e:
            print("ERROR: BrickPiCom::update: "
                  " an exception occurred and processing has been aborted."
                  " The exception message was:\n%s\n" % (e))
            raise # Re-throw.
        finally:
            if debug:
                print "DEBUG: BrickPiCom::update, END"
            BrickPiThreadLock.release()

    #
    #
    def set_motor_timeout(self, timeout):
        BrickPiThreadLock.acquire()
        debug = 0

        try:
            if 'DEBUG' in globals():
                if DEBUG >= 1:
                    debug = 1
                    print "DEBUG: BrickPiCom::set_motor_timeout, START"
            BrickPi.Timeout = timeout
            result = BrickPiSetTimeout()

            if result:
                msg = ("BrickPiSetTimeout failed, code %d" % (result))
                raise BrickPiException(msg)

        except BrickPiException as e:
            print("ERROR: BrickPiCom::set_motor_timeout: "
                  " an exception occurred and processing has been aborted."
                  " The exception message was:\n%s\n" % (e))
            raise # Re-throw.
        finally:
            if debug:
                print "DEBUG: BrickPiCom::set_motor_timeout, END"

            BrickPiThreadLock.release()

    def set_minimum_update_interval(self, mui):
        BrickPiThreadLock.acquire()
        self._minimumUpdateInterval = abs(float(mui))
        BrickPiThreadLock.release()

    #------------------------------------------------------------------
    # From here implementation methods, thus not part of the interface.
    # Should therefore never be called outside of this class definition.
    #------------------------------------------------------------------

    def __check_sensor(self, sensorClassName, sensorModuleName, port, debug,
                       *args):
        if debug:
            print("DEBUG: BrickPiCom::__check_sensor, START\n"
                  "       Check sensor class %s on port %d"
                  % (sensorClassName, port))
        # Import the module and get the class definition for this sensor.
        sensor_class = class_for_name(sensorClassName, sensorModuleName)
        # Instantiate the sensor class
        sensor = sensor_class(port, *args)
        flagNew = True
        # Get the type of this sensor
        sensorType = sensor.get_type()

        if(self._sensorType[port] == -1):
            # No sensors defined on this port yet, so all good.
            self._sensorType[port] = sensorType

        elif(sensorType != self._sensorType[port]):
            msg = ("Cannot register sensor %s of type %d on port %d another"
                    " sensor type (%d) has already been registered there." 
                    % (sensorClassName, sensorType, port, 
                        self._sensorType[port]))
            raise BrickPiException(msg)

        else:
            # Not the only sensor on this port, but of the same type.
            # This can mean one of two things:
            # 1) It is an I2C sensor that shares a port with another
            #    I2C sensor
            # 2) The same sensor is registered again (e.g. by
            #    another thread).
            if(sensorType in [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
                # Check if a sensor of class sensorClassName with
                # address has already been registered.
                count = self._sensorClassNames[port].count(sensorClassName)
                if(count):
                    index = 0
                    address = sensor.get_address()
                    for scn in self._sensorClassNames[port]:
                        if(scn == sensorClassName):
                            if(address == self._i2cAddress[port][index]):
                                # The same device.
                                if debug:
                                    print("DEBUG: BrickPiCom::__check_sensor: "
                                          "I2C sensor %s on port %d already "
                                          "registered." 
                                          % (sensorClassName, port))
                                sensor = self._sensors[port][index]
                                flagNew = False
                        index += 1
            else:
                # return the already registered instance of this sensor
                if debug:
                    print("DEBUG: BrickPiCom::__check_sensor: Sensor %s on "
                          "port %d already registered." 
                          % (sensorClassName, port))
                sensor = self._sensors[port][0]
                flagNew = False

        if debug:
            print "DEBUG: BrickPiCom::__check_sensor, END"

        return sensor, flagNew

    def __add_sensor(self, sensor, port, sensorClassName, debug):
        if debug:
            print("DEBUG: BrickPiCom::__add_sensor, START\n"
                  "       Add class %s on port %d"
                  % (sensorClassName, port))
        # Add the new sensor instance
        di = 0 # device index
        sensorType = sensor.get_type()

        if(sensorType in [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):

            if(len(self._sensors[port]) >= 8):
                msg = ("More than 8 I2C devices registered on port %d\n "
                        "cannot add sensor %s\n"
                        % (port, sensorClassName))
                raise BrickPiException(msg)

            address = sensor.get_address()
            self._i2cAddress[port].append(address)
            numsens = len(self._i2cAddress[port])

            if(BrickPi.SensorI2CDevices[port] > 0):
                BrickPi.SensorI2CDevices[port] += 1
            else:
                BrickPi.SensorI2CDevices[port] = 1

            if(BrickPi.SensorI2CDevices[port] != numsens):
                msg = "Panic: Internal state corrupted."
                raise BrickPiException(msg)

            di = numsens - 1
            BrickPi.SensorI2CAddr[port][di] = address

        BrickPi.SensorType[port] = sensorType
        self._sensors[port].append(sensor)
        self._sensorClassNames[port].append(sensorClassName)

        if debug:
            print "DEBUG: BrickPiCom::__add_sensor, END"
        return di

    def __initialize_sensor(
        self, sensor, port, di, sensorClassName, debug):
        #
        if debug:
            print("DEBUG: BrickPiCom::__initialize_sensor, START\n"
                  "       Initialize class %s on port %d"
                  % (sensorClassName, port))

        sensorType = sensor.get_type()

        if(sensorType in [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
            # I2C sensors may have a lot initialization to do,
            # but they cannot change type.
            if debug:
                print "DEBUG: BrickPiCom::initialize_sensor I2C"

            step = 1
            while step:
                outArray, numBytesIn, speed, settings, sdelay, udelay, \
                    step = sensor.callback_init(step)
                outLen = len(outArray)

                for i in range(outLen):
                    BrickPi.SensorI2COut[port][di][i] = outArray[i]

                BrickPi.SensorI2CWrite[port][di] = outLen
                BrickPi.SensorI2CRead[port][di] = numBytesIn

                # Speed is actually a speed limit. A higher value
                # means a lower I2C bus speed.
                # The sensor with the highest speed (limit) value
                # determines the bus speed for all on this port.
                if(abs(speed) > BrickPi.SensorI2CSpeed[port]):
                    BrickPi.SensorI2CSpeed[port] = abs(speed)

                BrickPi.SensorSettings[port][di] = settings
                result = BrickPiSetupSensors()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiSetupSensors failed with code: %d"
                           % (result))
                    raise BrickPiException(msg)

                time.sleep(sdelay)
                result = BrickPiUpdateValues()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiUpdateValues failed with code: %d"
                           % (result))
                    raise BrickPiException(msg)

                time.sleep(udelay)

                if numBytesIn:
                    if(BrickPi.Sensor[port] & (0x01 << di)):
                        sensor.callback_update(
                            BrickPi.SensorI2CIn[port][di][0:numBytesIn])
                    elif debug:
                        print("WARNING: BrickPiCom::register_sensor: "
                              "I2C sensor %s on port %d failed to return "
                              "values." % (sensorClassName, port))
        else:
            # For non-I2C sensors there is only one thing it can do:
            # change its type. E.g. the color sensor can change its
            # light color and sensing mode (color recognition or
            # light intensity). After changing its type, the sensor
            # might need some time to configure itself. That is what
            # the delays are for.
            if debug:
                print "DEBUG: BrickPiCom::initialize_sensor non-I2C"

            step = 1
            while step:
                newType, sdelay, udelay, step = sensor.callback_init(step)

                if(newType >= 0 ):
                    if(newType in [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
                        msg = "Cannot switch none-I2C sensor to type I2C"
                        raise BrickPiException(msg)

                    self._sensorType[port] = newType
                    BrickPi.SensorType[port] = newType

                time.sleep(sdelay)
                result = BrickPiSetupSensors()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiSetupSensors failed with code: %d"
                            % (result))
                    raise BrickPiException(msg)

                time.sleep(udelay)
                result = BrickPiUpdateValues()

                if result:
                    # BrickPi -> RPi communication error.
                    msg = ("BrickPiUpdateValues failed with code: %d"
                           % (result))
                    raise BrickPiException(msg)

                sensor.callback_update(BrickPi.Sensor[port])

        if debug:
            print "DEBUG: BrickPiCom::__initialize_sensor, END"

    def __setup_sensors(self, debug):
        if debug:
            print "DEBUG: BrickPiCom::__setup_sensors, START"
        # Build a list of sensors that require setup.
        setupList = []
        for i in range(4):
            for j in range(len(self._sensors[i])):
                if(self._sensors[i][j].setup_required()):
                    setupList.append((i,j))

        # Perform setup (if necessary)
        step = 1
        while len(setupList):
            setupDelay = 0.0
            updateDelay = 0.0
            i2cin = []
            values = []
            sl = list(setupList) # make a copy

            for ij in sl:
                sdelay = 0
                udelay = 0
                more = 0
                p = ij[0]
                d = ij[1]
                s = self._sensors[p][d]
                t = self._sensorType[p]

                if debug:
                    print("DEBUG: BrickPiCom::_setup_sensors: setup step %d "
                          "for sensor %s" 
                          %(step, self._sensorClassNames[p][d]))

                if(t in [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
                    #
                    outArray, numBytesIn, speed, settings, sdelay, \
                        udelay, more = s.callback_setup(step)
                    outLen = len(outArray)

                    for i in range(outLen):
                        BrickPi.SensorI2COut[p][d][i] = outArray[i]

                    BrickPi.SensorI2CWrite[p][d] = outLen
                    BrickPi.SensorI2CRead[p][d] = numBytesIn

                    if numBytesIn:
                        i2cin.append((p,d,numBytesIn))

                    if(abs(speed) > BrickPi.SensorI2CSpeed[p]):
                        BrickPi.SensorI2CSpeed[p] = abs(speed)

                    BrickPi.SensorSettings[p][d] = settings
                else:
                    #
                    newType, sdelay, udelay, more = s.callback_setup(step)

                    if(newType >= 0):
                        if(newType in 
                            [TYPE_SENSOR_I2C, TYPE_SENSOR_I2C_9V]):
                            msg = "Cannot switch none-I2C sensor to type I2C"
                            raise BrickPiException(msg)

                        self._sensorType[p] = newType
                        BrickPi.SensorType[p] = newType

                    values.append(p)

                if(sdelay > setupDelay):
                    setupDelay = sdelay

                if(udelay > updateDelay):
                    updateDelay = udelay

                if(more == 0):
                    setupList.remove(ij)
            #
            result = BrickPiSetupSensors()

            if(result):
                msg = "BrickPiSetupSensors failed with code: %d" % (result)
                raise BrickPiException(msg)

            time.sleep(setupDelay)
            result = BrickPiUpdateValues()

            if(result):
                msg = "BrickPiUpdateValues failed with code: %d" % (result)
                raise BrickPiException(msg)

            time.sleep(updateDelay)

            # Handle I2C input
            for ijk in i2cin:
                p = ijk[0]
                d = ijk[1]
                n = ijk[2]
                s = self._sensors[p][d]

                if(BrickPi.Sensor[p] & (0x01 << d)):
                    s.callback_update(
                        BrickPi.SensorI2CIn[p][d][0:n])
                elif debug:
                    print("WARNING: BrickPiCom::_setup_sensors: I2C sensor %s "
                            "on port %d failed to return values." %
                            (self._sensorClassNames[p][d], p))

            # Handle other sensor input
            for i in values:
                s = self._sensors[i][0]
                s.callback_update(BrickPi.Sensor[i])

            # Next step in setup.
            step += 1

        if debug:
            print "DEBUG: BrickPiCom::__setup_sensors, END"
        # Setup sensors done.

# End of BrickPiCom class definition


# Base class for sensors
class BrickPiSensor:
    def get_type(self):
        msg = ("ERROR: BrickPiSensor::get_type: Cannot instantiate "
               "BrickPiSensor class.")
        raise BrickPiException(msg)

    def callback_init(self, stage):
        return -1, 0, 0, 0

    def setup_required(self):
        return 0

    def callback_setup(self, stage):
        return -1, 0, 0, 0

    def callback_update(self, value):
        msg = ("ERROR: BrickPiSensor::callback_update: Cannot instantiate "
               "BrickPiSensor class.")
        raise BrickPiException(msg)

# Base class for I2C sensors
class BrickPiI2CSensor(BrickPiSensor):
    def get_address(self):
        msg = ("ERROR: BrickPiI2CSensor::callback_update: Cannot instantiate "
               "BrickPiI2CSensor class.")
        raise BrickPiException(msg)

    def callback_init(self, stage):
        a = []
        # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
        return a, 0, 0, 0, 0, 0, 0

    def callback_setup(self, stage):
        a = []
        # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
        return a, 0, 0, 0, 0, 0, 0

    def callback_expected_data_size(self):
        return 0






