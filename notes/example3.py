#! /opt/conda/bin/python

import time
import live555
import threading
import av
import numpy as np
import cv2
import numpy as np
import io
import traceback


seconds = 10000

url = "rtsp://admin:1234567a@172.16.115.206:666/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"
url = "rtsp://admin:1234567a@172.16.115.165:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"


class Frame:
    def __init__(self):
        self.rawData = io.BytesIO()
        self.container = av.open(self.rawData, format="h264", mode='r')
        self.key_frame_bytes = None
        self.frame_count = 0

    def oneFrame(self, codecName, bytes, sec, usec, durUSec):
        # print('frame for %s: %d bytes' % (codecName, len(bytes)))
        self.rawData.truncate(0)
        self.rawData.seek(0)
        self.rawData.write(b'\0\0\0\1' + bytes)
        self.rawData.seek(0)
        for packet in self.container.demux():
            if packet.size == 0:
                continue
            try:
                frames = packet.decode()
            except:
                # traceback.print_exc()
                continue
            else:
                self.key_frame_bytes = bytes
            for idx, frame in enumerate(frames):
                self.frame_count += 1
                print("Number of decoded frames: ", self.frame_count)
                image = frame.to_rgb().to_ndarray()
                st = time.time()
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                # image = cv2.resize(image, (960, 540))
                ed = time.time()
                print("time", ed - st)
                cv2.imshow("frame", image)
                cv2.waitKey(1)



# Starts pulling frames from the URL, with the provided callback:
useTCP = False
frame = Frame()
live555.startRTSP(url, frame.oneFrame, useTCP)
stream1_state = live555.StreamClientState()

print('------------------------------------------------')
print(type(stream1_state))
# Run Live555's event loop in a background thread:
t = threading.Thread(target=live555.runEventLoop, args=())
t.setDaemon(True)
t.start()

endTime = time.time() + seconds
while time.time() < endTime:
    time.sleep(0.1)


# Tell Live555's event loop to stop:
live555.stopEventLoop()


# Wait for the background thread to finish:
t.join()
