import serial,time

A = b"AAAAAA"
send = b"%s\n" % (A)
ser = serial.Serial("/dev/ttyS1",115200)

while True:
    ser.write(send)
    recv = ser.readline()
    result = recv.replace(b"\n", b"").split(b',')
    print(result)
    time.sleep(1)