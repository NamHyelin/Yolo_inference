import datetime
import cv2

from tool.utils import *
from tool.torch_utils import *
from tool.darknet2pytorch import Darknet
from tool.models import Yolov4
import time
import argparse

"""hyper parameters"""
use_cuda = True

class Yolo:
    def __init__(self):
        weight = './weight/yolov4_21nia_last.weights'
        cfg = './cfg/yolov4_21nia.cfg'

        self.mm = Darknet(cfg, inference = True)

        try : #pth file
            self.mm.load_state_dict(torch.load(weight, map_location = torch.device('cuda')))
        except : #weight file
            self.mm.load_weights(weight)

        if use_cuda :
            self.mm.cuda()

        self.num_classes = 10
        if self.num_classes == 20 :
            namesfile = 'data/voc.names'
        elif self.num_classes == 80:
            namesfile = 'data/coco.names'
        else:
            namesfile = 'data/soju21.names'

        self.class_names = load_class_names(namesfile)

    def yolo(self, Path, save_path):
        #start_time = time.time()
        result = self.detect_cv2(Path, save_path)
        #end_time = time.time()
        #print('detect time : {}'.format(round(end_time - start_time, 2)))
        return result

    def detect_cv2(self, imgfile, save_path):

        #time1 = time.time()
        img = cv2.imread(imgfile)

        while img is None:
            img = cv2.imread(imgfile)
        sized = cv2.resize(img, (640, 640))  # mm.width, mm.height
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        #print('cv2 time : {}'.format((round(time.time() - time1, 2))))

        #time2 = time.time()
        name_map, res = {}, {}
        for i, name in enumerate(self.class_names):
            name_map[i] = name
            res[name] = 0

        boxes = do_detect(self.mm, sized, 0.9, 0.6, use_cuda)
        boxes_revise = []

        for i in boxes:
            boxes_moment = []
            for j in i:
                if (j[3] - j[1] >= 0.23) & (j[2] - j[0] >= 0.23):
                    boxes_moment.append(j)
            boxes_revise.append(boxes_moment)

        for obj in boxes_revise[0]:
            res[name_map[obj[-1]]] += 1
        #print('detecting time : {}'.format(round(time.time() - time2 , 2)))

        #time3 = time.time()

        filename = imgfile.split('/')[-1].split('.')[0]
        filename = save_path + '/' + filename + '.jpg'
        plot_boxes_cv2(img, boxes_revise[0], savename=filename, class_names=self.class_names)

        #print('saving time : {}'.format(round(time.time() - time3, 2)))
        return res

#if __name__ == "__main__":
#result = Yolo('C:/Users/SujinKook/Desktop/image/1.bmp')
#print(result)
