from maix import nn, pwm, camera, display, image 
import serial,time

# YOLO
input_size = (224, 224)
model = "/root/model/model-68645.awnn.mud"
labels = ['Cola', 'LockLock']
anchors = [0.97, 1.66, 5.81, 2.75, 1.53, 2.66, 4.97, 2.34, 1.28, 2.19]
class YOLOv2:
    def __init__(self, model_path, labels, anchors, net_in_size, net_out_size):
        self.labels = labels
        self.anchors = anchors
        self.net_in_size = net_in_size
        self.net_out_size = net_out_size
        print("-- load model:", model)
        self.model = nn.load(model_path)
        print("-- load ok")
        print("-- init yolo2 decoder")
        self._decoder = nn.decoder.Yolo2(len(labels), anchors, net_in_size=net_in_size, net_out_size=net_out_size)
        print("-- init complete")

    def run(self, img, nms=0.3, threshold=0.5):
        out = self.model.forward(img, layout="hwc")
        boxes, probs = self._decoder.run(out, nms=nms, threshold=threshold, img_size=input_size)
        return boxes, probs

    def draw(self, img, boxes, probs):
        cid = -1
        for i, box in enumerate(boxes):
            class_id = probs[i][0]
            cid = class_id
            prob = probs[i][1][class_id]
            msg = "{}:{:.2f}%".format(self.labels[class_id], prob*100)
            img.draw_rectangle(box[0], box[1], box[0] + box[2], box[1] + box[3], color=(255, 255, 255), thickness=2)
            img.draw_string(box[0] + 2, box[1] + 2, msg, scale = 1.2, color = (255, 255, 255), thickness = 2)
        return cid+1

camera.config(size=input_size)
yolov2 = YOLOv2(model, labels, anchors, input_size, (input_size[0] // 32, input_size[1] // 32))

# DG995MG
DG995MG = pwm.PWM(8)
DG995MG.export()
DG995MG.period = 30000000  
DG995MG.enable = True        
DG995MG.duty_cycle = 15000000 + 2400000*0

# UART
DetectData = ['0','0','0','0','0','0']
ser = serial.Serial("/dev/ttyS1",115200)

# MAIN
Info = image.new(size = (240, 240), 
                              color = (255, 255, 255), mode = "RGB")
ColaNum = 0
LockLockNum = 0
img = camera.capture()
img = camera.capture()
img = camera.capture()
for i in range(6):
    img = camera.capture()
    boxes, probs = yolov2.run(img, nms=0.3, threshold=0.5)
    DetectData[0] = yolov2.draw(img, boxes, probs)
    display.show(img)
    print(i)
    if (DetectData[0] != 0):
        break

if (DetectData[0] == 1):
    ColaNum += 1
elif (DetectData[0] == 2):
    LockLockNum += 1
else:
    ColaNum = 0
    LockLockNum = 0


while True:
    recv = ser.read(5)
    if (recv == b"start"):
        break

        
for i in range(1,6):
    DG995MG.duty_cycle = 15000000 + 2400000*i
    time.sleep(0.5)
    img = camera.capture()
    img = camera.capture()
    img = camera.capture()
    for x in range(6):
        img = camera.capture()
        boxes, probs = yolov2.run(img, nms=0.3, threshold=0.5)
        DetectData[i] = yolov2.draw(img, boxes, probs)
        display.show(img)
        if (DetectData[i] != 0):
            break
 
    if (DetectData[i] == 1):
        ColaNum += 1
    elif (DetectData[i] == 2):
        LockLockNum += 1

    if (ColaNum == 3):
        for i in range(len(DetectData)):
            if DetectData[i] != 1:
                DetectData[i] = 2
        break
    elif (LockLockNum == 3):
        for i in range(len(DetectData)):
            if DetectData[i] != 2:
                DetectData[i] = 1
        break



TotalCola = 0
TotalLockLock = 0

for data in DetectData:
    if (data == 1):
        TotalCola += 1        
    elif (data == 2): 
        TotalLockLock += 1

result = ""
if(TotalCola != 3 and TotalLockLock != 3):
    Info = image.new(size = (240, 240), 
                              color = (255, 0, 0), mode = "RGB")
    result = "000000"
else:
    Info = image.new(size = (240, 240), 
                              color = (0, 255, 0), mode = "RGB")
    for data in DetectData:
        result += str(data)
    

send = result.encode()
ser.write(send)
print(send)
Info.draw_string(80, 30, "Cola:"+ str(TotalCola), scale = 2.0, 
                              color = (0, 0, 255), thickness = 2)
Info.draw_string(80, 80, "Lock:"+ str(TotalLockLock), scale = 2.0, 
                              color = (0, 0, 255), thickness = 2)
Info.draw_string(80, 130, result, scale = 2.0, 
                              color = (0, 0, 255), thickness = 2)
display.show(Info)   #把这张图显示出来


del yolov2
del camera
del ser