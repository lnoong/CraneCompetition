import time
from maix import display,image,gpio,camera
class v83x_ADC():
    def __init__(self, addr=b"0x05070080") -> None:
        self.addr = addr
        self.path = "/sys/class/sunxi_dump/dump"
        self.file = open(self.path, "wb+")
        self.last = self.value()
    def __del__(self):
        try:
            if self.file:
                self.file.close()
                del self.file
        except Exception as e:
            pass
    def value(self):
        self.file.write(b"0x05070080")
        self.file.seek(0)
        return int(self.file.read()[:-1], 16)

camera.config(size=(224, 224))
BUTTON = v83x_ADC()
count = 0
while True:
    img = camera.capture()
    display.show(img)
    
    val = BUTTON.value()
    if val<400 and val>350:
        print('key1')
        count += 1
        path= '/root/pic/' + str(count) + '.jpg'
        img.save(path)
        time.sleep(0.3)
        print(count)
    elif val==0:
        camera.close()
        del BUTTON

