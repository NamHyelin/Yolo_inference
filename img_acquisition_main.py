import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, QDate, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5 import uic

import time

import argparse
import msvcrt
import os
import sys
import time
import threading

import save_excel
import Yolo_inference as Yolo

form_class = uic.loadUiType("daesunform.ui")[0]

init_result = {"Standard": 0, "Diamond": 0, "Jinro": 0, "Chungha": 0, "Cass": 0, "Bud": 0, "Cafri": 0, "Maesil": 0, "Empty": 0, "Etc": 0}


class Thread1(QThread):
    go_terminate = pyqtSignal()


    def __init__(self, Config, parent = None):
        super().__init__(parent)
        self.config = Config
        self.check_end = 0
        self.Yolo_infer = Yolo.Yolo()

    def yolo_test(self, path, inf_done, save_path):
        result_fullimg = init_result.copy()
        '''
        img = list(sorted(os.listdir(path), key = self.mtime))[inf_done] #infer 안한 마지막 이미지 로드
        image_path = path + '/' + img
        result_fullimg = Yolo.Yolo(image_path)
        '''
        #infer_start = time.time()
        '''cam 4 ver'''

        #todo CAM1
        paths = path + str('/CAM1')
        self.mtime = lambda f: os.stat(os.path.join(paths, f)).st_mtime
        img = list(sorted(os.listdir(paths), key=self.mtime))[inf_done]
        image_path = paths + '/' + img
        # infer_start2 = time.time()
        result_img = self.Yolo_infer.yolo(image_path, save_path + '/CAM1')
        print('Cam', str(1), ':  ', img, '    ', result_img)
        # infer_end2 = time.time()

        #todo CAM2-4
        for i in range(2,5):
            # paths = str(path.split('/')[0]) + str('/') + str(path.split('/')[1]) + str('/') + str('CAM') + str(i)  #폴더명에서 뒤에 한칸만 CAM2/3/4 로 바꿔서 읽음

            # CAM2-4에 CAM1에서 detect한 img와 같은 이름의 img가 있는지 검사
            paths = path + str('/CAM{}'.format(i))
            self.mtime = lambda f: os.stat(os.path.join(paths, f)).st_mtime

            if img in list(sorted(os.listdir(paths), key=self.mtime)): # ....있으면 detect
                image_path = paths + '/' + img
                # infer_start2 = time.time()
                result_img = self.Yolo_infer.yolo(image_path, save_path + '/CAM{}'.format(i))
                # infer_end2 = time.time()
            else:      # ..................................................없으면 for문 break, inference 결과로 0,..0 출력
                result_fullimg = init_result
                break

            #result_img={"Standard": 1, "Jinro": 1, "Chungha": 1, "Cass": 1, "Bud": 1, "Cafri": 1, "Maesil": 1, "Empty": 1, "Etc": 1}
            print('Cam', i, ':  ', img, '    ', result_img)
            #print('{} inference time : {}'.format(i + 1, round(infer_end2 - infer_start2, 2)))

            for key in result_fullimg.keys():
               result_fullimg[key]+=result_img[key]

        #infer_end = time.time()
        #print('inference time : {}'.format(round(infer_end-infer_start,2)))
        #result_fullimg = Yolo.Yolo(path)
        #result_fullimg = {"Standard": 1, "Diamond": 1, "Jinro": 1, "Chungha": 1, "Cass": 1, "Bud": 1, "Cafri": 1, "Maesil": 1, "Empty": 1, "Etc": 1}

        return result_fullimg


    def run(self):

        config = self.config
        img_path = config['img_dir']
        img_subpath = config['img_dir'] + str('/CAM1')
        suffix = '.bmp'
        csv_path = config['excel_dir']

        save_hours_empty = config['_save_empty']  # 몇시간동안 데이터 안들어오면 csv_save
        save_hours = config['_save_hours']  # 몇시간마다 주기적으로 csv_save
        save_time = config['_save_time']  # 몇시에 csv_save

        mem = 0
        num = []
        inf_done = 0
        inf_time = time.time()
        inference_result = init_result.copy()
        final_result = init_result.copy()

        save_dir_date = ''

        print('\n<Yolov4 inference>\n')
        print('save csv when no new data appears for {} hours'.format(save_hours_empty))
        print('save csv every {} hours'.format(save_hours)) #current : sec
        print('save csv at {} o clock\n'.format(save_time))
        print('press s to save csv')
        print('press c multiple times to stop')
        print('__________________________________________________________\n')

        start_time = time.time()

        while 1 :
            # self.mtime = lambda f: os.stat(os.path.join(img_path, f)).st_mtime
            if mem != len(os.listdir(img_subpath)) and len(os.listdir(img_subpath)) > 0:

                Date = time.strftime('%Y-%m-%d', time.localtime())
                #server_address = 'C:/Users/admin/Desktop/Yolo_inference/foldertest'
                #server_address = 'C:\\Users\\admin\\Desktop\\Yolo_inference\\foldertest'
                #server_address = '\\\\203.255.254.10\\Share'
                server_address = 'C:\\Users\\SujinKook\\Desktop\\nia_code\\Yolo_inference_final\\test'

                if Date != save_dir_date :
                    try :
                        dir_date = server_address + '/' + Date
                        os.makedirs(dir_date)
                        os.makedirs(dir_date + '/Data')
                        os.makedirs(dir_date + '/Image')

                        for i in range(1,5) :
                            os.makedirs(dir_date + '/Image/Machine_{}'.format(i))
                            for j in range(1,5) :
                                os.makedirs(dir_date + '/Image/Machine_{}/CAM{}'.format(i, j))

                        save_dir_date = Date

                    except FileExistsError :
                        save_dir_date = Date
                        continue

                #if not os.path.exists(server_address + '/' + Date) :
                #    os.makedirs(server_address + '/' + Date)

                if inf_done < len(list(sorted(os.listdir(img_subpath)))):

                    '''inference with img'''
                    result = self.yolo_test(img_path, inf_done, dir_date + '/Image/Machine_1')  # ~~~image
                    for key in result.keys():
                        inference_result[key] += result[key]
                        final_result[key] += result[key]
                    print(inference_result)

                    inf_done += 1
                    inf_time = time.time()

                    if int(time.time() - start_time) % save_hours == 0 :
                         end_of_day = False
                         print('csv_save: ', Date, "-bottle.xlsx       Time:", time.strftime('%H:%M:%S', time.localtime()))
                         save_excel.Csv_save(inference_result, Date, csv_path, end_of_day)
                         inference_result = init_result.copy()

                if (time.time() - inf_time > save_hours_empty and inference_result != init_result) or (time.localtime
                        (time.time()).tm_hour == save_time and inference_result != init_result) or self.check_end == 1 or (int(time.time() - start_time) % save_hours == 0 and inference_result != init_result) :
                    Date = time.strftime('%Y-%m-%d', time.localtime())

                    '''csv_save'''
                    end_of_day = False
                    print('csv_save: ', Date, "-bottle.xlsx       Time:", time.strftime('%H:%M:%S', time.localtime()))

                    if time.localtime(time.time()).tm_hour == save_time or  self.check_end == 1:
                        end_of_day = True


                    save_excel.Csv_save(inference_result, Date, csv_path, end_of_day)
                    inference_result = init_result.copy()  # 초기화

                    if end_of_day == True :
                        save_excel.final_read(Date, csv_path, dir_date + '/Data')
                        '''delete imgs'''
                        for i in range(4):
                            paths = img_path + str('/CAM{}'.format(i+1))
                            for f in os.listdir(paths):
                                os.remove(paths+'/'+f)
                        inf_done=0


                    inf_time = time.time()

                    if self.check_end == 1 :
                        self.go_terminate.emit()
                        break


    def change(self):
        self.check_end = 1


class App(QMainWindow, form_class):
    change_check_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.date = QDate.currentDate()
        self.setupUi(self)

        self.btn_imgpath.clicked.connect(self.imgpathFunciton)
        self.btn_excelpath.clicked.connect(self.excelpathFunction)
        self.btn_setting.clicked.connect(self.settingFunction)
        self.btn_start.clicked.connect(self.startFunction)
        self.btn_stop.clicked.connect(self.stopFunction)
        self.initUI()



    def startFunction(self):
        print('start Function')
        print('status')
        self.setting()
        self.statusBar().showMessage('진행 중')


        self.main = Thread1(self.config, self)
        self.change_check_signal.connect(self.main.change)
        self.main.go_terminate.connect(self.main_terminate)
        self.main.start()


    @pyqtSlot()
    def main_terminate(self):
        self.main.terminate()

    def setting(self):
        try :
            self.config
        except :
            self.config = None

        if self.config == None :
            self.config = dict()
            self.config['_save_hours'] = 10
            self.config['_save_empty'] = 10
            self.config['_save_time'] = 22

            self.sB_savehours.setValue(self.config['_save_hours'])
            self.sB_saveempty.setValue(self.config['_save_empty'])
            self.sB_savetime.setValue(self.config['_save_time'])
        else :
            print(self.config)

        if self.tb_imgpath.text() == "" :
            self.tb_imgpath.setText('C:/Users/SujinKook/Desktop/nia_code/Yolo_inference/image')
        if self.tb_excelpath.text() == "" :
            self.tb_excelpath.setText('C:/Users/SujinKook/Desktop/nia_code/Yolo_inference/excel')

        self.config['img_dir'] = self.tb_imgpath.text()
        self.config['excel_dir'] = self.tb_excelpath.text()

        print(self.config)

    def stopFunction(self):
        print('stop Function')
        self.statusBar().showMessage(self.date.toString(Qt.DefaultLocaleLongDate))

        self.main.check_end = 1

        self.change_check_signal.emit(1)

    def imgpathFunciton(self):
        img_dir = QFileDialog.getExistingDirectory(self, '저장 경로 찾기')
        self.tb_imgpath.setText(img_dir)

    def excelpathFunction(self):
        excel_dir = QFileDialog.getExistingDirectory(self, '저장 경로 찾기')
        self.tb_excelpath.setText(excel_dir)

    def settingFunction(self):
        _save_hours = self.sB_savehours.value()
        _save_empty = self.sB_saveempty.value()
        _save_time = self.sB_savetime.value()
        print('save hours {} / save empty {} / save time {}'.format(_save_hours, _save_empty, _save_time))

        self.config = dict()
        self.config['_save_hours'] = _save_hours
        self.config['_save_empty'] = _save_empty
        self.config['_save_time'] = _save_time

    def initUI(self):
        #상태바
        self.statusBar().showMessage(self.date.toString(Qt.DefaultLocaleLongDate))

        self.sB_savehours.setMinimum(0)
        self.sB_savehours.setMaximum(60)

        self.sB_saveempty.setMinimum(0)
        self.sB_saveempty.setMaximum(10)

        self.sB_savetime.setMinimum(0)
        self.sB_savetime.setMaximum(11)


if __name__ == '__main__' :
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

    # app.exec_ : event loop / 종료되면 0 반환 / 그 아래 코드는 실행하지 않음.
    # sys.exit() : system 종료 / 0 들어오면 종료
    # 따로 써도 됨.
