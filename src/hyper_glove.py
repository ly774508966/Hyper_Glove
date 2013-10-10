# -*- coding: cp1252 -*-
"""
Use pySerial to receive streaming data from multiple MPU-6050 IMUs
attached to an Arduino Micro.


Some examples I am not using:
#print "Serial port: ", ser.portstr       # check which port was really used
# ser.write("hello")      # write a string
"""

import serial
import collections
import re
import time

ser_port_manual = 4

""" function calls at bottom for now """

def init_IMU_dictionaries():

    # Initialize a dict for each IMU
    # Expand this to handle N IMUs based on passed parameters
    IMU_dictionaries = { 'time': {'tm' : collections.deque() },
                         'IMU0': {'gy' : collections.deque(),
                                  'gp' : collections.deque(),
                                  'gr' : collections.deque(),
                                  'ax' : collections.deque(),
                                  'ay' : collections.deque(),
                                  'az' : collections.deque() },
                         'IMU1': {'gy' : collections.deque(),
                                  'gp' : collections.deque(),
                                  'gr' : collections.deque(),
                                  'ax' : collections.deque(),
                                  'ay' : collections.deque(),
                                  'az' : collections.deque() },
                         'IMU2': {'gy' : collections.deque(),
                                  'gp' : collections.deque(),
                                  'gr' : collections.deque(),
                                  'ax' : collections.deque(),
                                  'ay' : collections.deque(),
                                  'az' : collections.deque() },
                         'IMU3': {'gy' : collections.deque(),
                                  'gp' : collections.deque(),
                                  'gr' : collections.deque(),
                                  'ax' : collections.deque(),
                                  'ay' : collections.deque(),
                                  'az' : collections.deque() } }

    return IMU_dictionaries


def split_one_data_string(serial_raw):
    """
    serial_raw initializes with data to lob off the front, but immediately
    synchronizes to always begin with ST when the serial stream is well
    formed.

    A. Split on the first XX
    B. Search string for ST
        B1. If no ST, discard string, return to A.
        B2. If ST is found, discard string before ST.
    C. Pass to parser
    """



    """
    ERROR CHECKING AGAIN - it is necessary to make sure I am passing the
    right number of values. I can't just pray that xyz.split will give a
    list with 2 items. That will fail.
    
    sr_mutations = serial_raw
    
    mutation_values = []
    mutation_values = sr_mutations.split("XX", 1)
    print mutation_values
    """

    ## split off everything before the first XX
    ## If the XX is first, this will throw an error BUGFIX REQUIRED
    sr_mutations = ""
    raw_data_string, sr_mutations = serial_raw.split("XX", 1)
    raw_data_string = raw_data_string + "XX" #add suffix, to parse, for now


    ## If the raw_data_string doesn't have a start, dump it and
    ## grab the next one.
    ## This *NEEDS* better handling, but not today.
    if raw_data_string.find("ST") == -1: # if there is no ST in the string
        # This doesn't work if the string is just XX, it breaks.
        # Does the string guarantee a length > 2? That would unbreak it...
        raw_data_string, sr_mutations = sr_mutations.split("XX", 1)
        raw_data_string = raw_data_string + "XX" #add suffix, to parse, for now
    if raw_data_string[0:2] != "ST":
        malformed_data, raw_data_string = raw_data_string.split("ST", 1)
        raw_data_string = "ST" + raw_data_string #add prefix, to parse, for now


    serial_raw = sr_mutations # return the stream without the processed data.
    
    
    ## Do nothing for now, this is a rudimentary test, but is forced true above
    if raw_data_string[-2:] != "XX":
        print "Exception: String did not end with XX!"
        raise
    if raw_data_string[0:2] != "ST":
        print "Exception: String did not begin with ST!"
        raise


    return [raw_data_string, serial_raw]

    

def parse_values(raw_data_string, IMU_dictionaries):
    """
    Parse values from a raw data string into the deque stream.

    The data contains all FOUR IMUs and the time difference, so this
    must be changed to support more or fewer IMUs.

    Assume the string already contains only ST<values>XX
    (this could be easily mitigated by auto detecting the number of IMUs
    in the string here, then iterating over that many)

    
    # (Example of re.compile)
    # h = re.compile('hello')
    # h.match('hello world')

    Variables in the strings: IMU Number, gy, gp, gr, ax, ay, az, t.

    Example data string (no white space in the actual string):
    ST
    m0gy165gp168gr-229ax-2476ay14924az1536
    m1gy-262gp-39gr-27ax-6700ay10352az9384
    m2gy-39gp-41gr204ax-6492ay10564az10032
    m3gy-35gp137gr36ax3868ay13972az4260
    t14
    XX

    These values can be stripped as strings and converted to proper numbers.
    Just use int("value") once the proper portion of the string is stripped.

    Compile your regular expressions into re objects using re.compile!
    see the python regular expressions (re) documentation!
    """


    # 0. Save original for reference, for testing?
    rds_mutations = raw_data_string


    ## 1. Strip off the ends and chop out the time data.
    rds_mutations = re.split('STm', rds_mutations)
    # added m to fix the empty item in onlyIMUdata_string.split("m") below.
    
    rds_mutations = re.split('XX', rds_mutations[1])
    rds_mutations = re.split('t', rds_mutations[0])
    time_difference = rds_mutations[1]
    onlyIMUdata_string = rds_mutations[0]

    ##  append time to the time deque, stored in time dict in IMU_dictionaries
    IMU_dictionaries['time']['tm'].append(int(time_difference))

    ## 2. Strip each IMU down to a separate string.
    """ This generates a list containing a string for each IMU's data """
    list_containing_each_IMU_string = onlyIMUdata_string.split("m") # also removes the m

    ## This can be used if there is a different number of IMUs...
    ## Right now this isn't a consideration in other code.
    number_of_IMUs = len(list_containing_each_IMU_string)


    ## 3. Strip all the data into variables for collecting.
    for each in list_containing_each_IMU_string:
        """
        Note that the data_tail splits these specifically
        The front of the data_tail contains the information
        whose header has just been chopped off.
        The reading_type variable is subsequently discarded each partition
        """
        IMU_number, reading_type, data_tail = each.partition("gy")
        gy, reading_type, data_tail = data_tail.partition("gp")
        gp, reading_type, data_tail = data_tail.partition("gr")
        gr, reading_type, data_tail = data_tail.partition("ax")
        ax, reading_type, data_tail = data_tail.partition("ay")
        ay, reading_type, data_tail = data_tail.partition("az")
        az = data_tail # the nub at the end of data_tail is az raw data.

        # Generate the dictionary name from the reported IMU
        IMU_dictname = "IMU" + IMU_number
        ## 4. Integrate all the variables into the appropriate deque
        ##     be sure to convert to integers (they are strings)
        IMU_dictionaries[IMU_dictname]['gy'].append(int(gy))
        IMU_dictionaries[IMU_dictname]['gp'].append(int(gp))
        IMU_dictionaries[IMU_dictname]['gr'].append(int(gr))
        IMU_dictionaries[IMU_dictname]['ax'].append(int(ax))
        IMU_dictionaries[IMU_dictname]['ay'].append(int(ay))
        IMU_dictionaries[IMU_dictname]['az'].append(int(az))


    ## Final Step: Return the data structures to the outside scope
    return IMU_dictionaries
    



def serial_open(ser, ser_port_manual):

    """
    Open the relevant serial port.
    How should I detect this?
    """

    ser.baudrate = 115200 # This is pretty close to my send speed... am I lagging?
    ser.port = ser_port_manual
    ser.timeout = 1
    
    ser.open()

    return ser


def append_serial_raw_string(ser, serial_raw):

    """
    Return serial data from the serial object
    """
    if len(serial_raw) < 400:
        s = ser.read(400) ## slightly over 2 datapoints
        serial_raw += s

    return serial_raw


def read_controller(ser, serial_raw, IMU_dictionaries):
    """
    Control reads and build the IMU_dictionaries

    """
    # Read one string from serial buffer
    serial_raw = append_serial_raw_string(ser, serial_raw)

    # Split a data string off from serial_raw for processing
    raw_data_string, serial_raw = split_one_data_string(serial_raw)

    # Process the raw data string, feed into data structures
    IMU_dictionaries = parse_values(raw_data_string, IMU_dictionaries)

    return [ser, serial_raw, IMU_dictionaries]

""" now calling functions """

# Initialize deques
IMU_dictionaries = init_IMU_dictionaries()

# Initialize raw serial data string
serial_raw = ""

# Initialize and open serial port
ser = serial.Serial()
serial_open(ser, ser_port_manual)


for z in range(0,5):

    # print "Iterations: ", z+1
    start = time.clock()
    
    for x in range(0,60):
        ser, serial_raw, IMU_dictionaries = read_controller(ser, serial_raw, IMU_dictionaries)
        if x == 0:
            print IMU_dictionaries
    
    IMU_dictionaries['time']['tm'].clear()
    for IMU_number in range(0,4):
        IMU_dictname = "IMU" + str(IMU_number)
        IMU_dictionaries[IMU_dictname]['gy'].clear()
        IMU_dictionaries[IMU_dictname]['gp'].clear()
        IMU_dictionaries[IMU_dictname]['gr'].clear()
        IMU_dictionaries[IMU_dictname]['ax'].clear()
        IMU_dictionaries[IMU_dictname]['ay'].clear()
        IMU_dictionaries[IMU_dictname]['az'].clear()
    
    # print serial_raw
    # print (time.clock() - start), "seconds elapsed."

# Clean up
ser.close()



