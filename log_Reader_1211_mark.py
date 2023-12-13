
import os
import re
# import sys
import csv
# import pandas as pd

import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

# from PyQt6.QtCore import Qt
# from PyQt6.QtWidgets import QWidget,QApplication,QTreeWidget,QPlainTextEdit,QHBoxLayout,QSplitter,QTreeWidgetItem
# from PyQt6.QtGui import QSyntaxHighlighter,QColor,QTextCharFormat,QFont

##############################################################################
# 呼叫资料,列表, 字典

def call_text(text_name):
    if text_name == 'UI_information':
        UI_information = ('Version: None(1128) \n'
                          'Defined station(PJNE) : \n'
                          '\tSWDL, Qt1~2, ALS, Force, Actuator, Mesa, IO1~6, CBT, Color, DVI, FACT\n'
                          '\tFCT\n'
                          '\n'
                          'Note : If APP have problem, please connect to PJNE EE team, thanks')

        return UI_information
    else:
        none_message = ''
        return none_message

def Call_dict(dict_name):
    # 指定各站UART file name
    if dict_name == 'dict_station_uartlogname':
        dict_station_uartlogname = {'QT0': 'CommBuilder_uartDut.log',
                                    'QT1': 'CommBuilder_uartDut.log',
                                    'DVI': 'dut-uart.log',
                                    'ColorCal': 'dut-uart.log',
                                    'IO1': 'EFIDut.log',
                                    'IO2': 'EFIDut.log',
                                    'IO3': 'EFIDut.log',
                                    'IO4': 'EFIDut.log',
                                    'IO5': 'EFIDut.log',
                                    'IO6': 'EFIDut.log',
                                    'ACTUATION': 'rawuart.log',
                                    'ALS': 'rawuart.log',
                                    'FORCE': 'rawuart.log',
                                    'BUTTON': 'cb-comm.log',
                                    'FCT': 'serial.log',
                                    'FACT': '.csv',
                                    'SW': 'write_sn.log',
                                    'SWDL': 'diagsoverusb_host_WRITE_FGSN' #'SWDL': 'write_sn.log'
                                    }
        return dict_station_uartlogname

    # for file path / station info
    if dict_name == 'file_info_dict':
        file_info_dict = {'device': None
                            , 'uart_path': None
                            , 'records_path': None
                            , 'station': None
                            , 'version': 'None'
                            , 'mlb': 'None'
                            , 'sn': 'None'
                            , 'message': None
                            , 'message_uart': None
                            , 'message_device': None
                            , 'bundle': 'None'
                            , 'ECID': 'None'
                            }
        return file_info_dict

    # log info for UI
    if dict_name == 'dict_testitem_to_tree':
        dict_testitem_to_tree = {'test_name': None
                                    , 'sub_test_name': None
                                    , 'time_start': None
                                    , 'time_stop': None
                                    , 'time_duration': None
                                    , 'pass_fail': None
                                    , 'records_fail': None
                                    , 'index_start': None
                                    , 'index_stop': None
                                    }
        return dict_testitem_to_tree


def call_keyword_dict(list_name):
    keyword_station = {}

    # R : fail
    # G : result, pass
    # B : send cmd, sub name
    # O : test start, receive
    # P : limit, other
    

    if list_name in ['QT0','QT1']:
        print('QT')
        keyword_station =   {'r':['\[CmdResult:\] (FAIL)','\[Test Fail\](.*)','\[ERROR\](.*)','<error>']
                            ,'g':['\[CmdResult:\] PASS','\[Test Pass\]']
                            ,'b':['\[Send:\].*','\[ParameterName\].*']
                            ,'o':['\[Rec:\]','\[Test Start\].*']
                            ,'p':['\[Exp:\]','\[upperLimit\]','\[lowerLimit\]']
                            }


    elif list_name in ['IO1','IO2','IO3','IO4','IO5','IO6']:
        print('IO')                     
        keyword_station =   {'r':['### .*:false ###','Timed out waiting for .*','test failed']
                            ,'g':['###### Test Done ######','### .*:true ###']
                            ,'b':['append data with key: \w*','command to send : (.*)']
                            ,'o':['value: [^ ]*','###### Test started ######','### .*Begin ###']
                            ,'p':['identifier: \w*',',mA,(.*)',',Mbps,(.*)',',mV,(.*)',',ohms,(.*)',',p[sS],(.*)',' ts:(.*)',',,\d.+']
                            }


    elif list_name in ['ALS','ACTUATION','FORCE','BUTTON']:
        print('ATLAS')
        keyword_station =   {'r':['(Failed command|TestFailedError)','t101ErrMessage: FAIL']
                            ,'g':['Test finished event for (.*)','Successfully completed command ([\w ]*)','Logging data for ([\w ]*)','t101ErrMessage: PASS']
                            ,'b':['names:\[\w*,(.*)\]','"name": ?([^,"\}]*)','command: (.*)',"Sending command to DUT: '(.*)'"]
                            ,'o':['measurement:(.*)','"value": ?([^, \}]*)','Open-lid Angle Check value:(.*)','response from DUT: (.*)']
                            ,'p':['"lowerLimit": ?([^, \}]*)','"upperLimit": ?([^, \}]*)']
                            }


    elif list_name in ['DVI','ColorCal']:
        print('DVI')
        keyword_station =   {'r':['failed s.*','<error>']
                            ,'g':['<<.*?/TestFinish>>','>>\s*Pass?:','>>\s*Result:','>>\s*Pass!']
                            ,'b':['Running Action .*','sending cb write:','key ?= ?\w*']
                            ,'o':['Running Test .*','>>\s*Measured.*','value ?= ?[\w\.]*']
                            ,'p':['ERROR:','Warning:']
                            }

    # R : fail
    # G : result, pass
    # B : send cmd, sub name
    # O : test start, receive
    # P : limit, other


    elif list_name in ['FCT']:
        print('FCT')
        keyword_station =   {'r':['\[Test Fail\](.*)','\[ERROR\](.*)','result: FAIL']
                            ,'g':['\[Test Pass\]','result: PASS']
                            ,'b':['\[ParameterName\].*']
                            ,'o':['\[Test Start\].*','value: [-\d\.]+']
                            ,'p':['\[upperLimit\]','\[lowerLimit\]','lower: [-\d\.]+','higher: [-\d\.]+','<error>']
                            }


    elif list_name in ['FACT']:
        print('FACT')
        keyword_station =   {'r':['Mask violation :']
                            ,'g':['<@>Finished .*']
                            ,'b':[]
                            ,'o':['<@>Running .*']
                            ,'p':[]
                            }

    elif list_name in ['STATION30']:
        print('CBT')
        keyword_station =   {'r':['Action \w* failed:','<error>','Failed test']
                            ,'g':[]
                            ,'b':['Running Action.*']
                            ,'o':['Running Test.*']
                            ,'p':[]
                            }


    elif list_name in ['SW','SWDL']:
        print('SWDL')
        keyword_station =   {'r':['========== test.*(fail|error).*']
                            ,'g':['========== test.*pass']
                            ,'b':[]
                            ,'o':['========== Action:.*','SPARTAN_CHARGER_.*','SPARTAN_NEUTRON_CYCLE_COUNT_CHECK.*']
                            ,'p':['SPARTAN_FW_CHECK.*','SPARTAN_NEUTRON_CYCLE_COUNT_[MW].*']
                            }


    return keyword_station


##############################################################################

# 计算时间
def cal_time_duration(time_start,time_stop):
    time_start = re.sub('-','/',time_start)
    time_stop  = re.sub('-','/',time_stop)
    time_start_split = re.split(r'\.',time_start)
    time_stop_split = re.split(r'\.',time_stop)
    time_start_s = time.mktime(time.strptime(time_start_split[0],"%Y/%m/%d %H:%M:%S"))
    time_stop_s = time.mktime(time.strptime(time_stop_split[0],"%Y/%m/%d %H:%M:%S"))
    time_s = time_stop_s-time_start_s
    # time_sx1000000 = time_s * 1000000
    # time_stop_start = time_sx1000000 + int(time_stop_split[1]) - int(time_start_split[1])
    # time_duration = time_stop_start / 1000000
    time_sx1000000 = time_s * (10**len(time_stop_split[1]))
    time_stop_start = time_sx1000000 + int(time_stop_split[1]) - int(time_start_split[1])
    time_duration = time_stop_start / (10**len(time_stop_split[1]))
    return time_duration

##############################################################################

# 删除治具log
def cut_fixture_unused_sentence(file_info_dict):
    # device_log = ''
    station = file_info_dict['station']
    device_path = file_info_dict['device']
    # records_path = file_info_dict['records_path']

    with open(device_path, "rb") as device_log_origin:
        device_log_origin = device_log_origin.read().decode("utf-8", "ignore")


    if station in ['QT0','QT1','ColorCal','DVI','FCT','STATION30','SW','SWDL']:
        device_log = re.sub(r'category=.*?\) (<default>)?',' ',device_log_origin)
        device_log = re.sub(r'\s*\n','\n',device_log)

    elif station in ['IO1','IO2','IO3','IO4','IO5','IO6']:
        device_log = re.sub(r'\+0800.*?com\.apple\.hwte\.atlas:group\d(\.DUT-slot\d)?\]',' ',device_log_origin)

    elif station in ['ALS','ACTUATION','BUTTON','FORCE']:
        if station == 'ALS':
            device_log = re.sub(r'(Group\(Fixture\)\.Unit\(Slot_\d\)\.Plugin|atlas\.AppContainer\.Group\(Fixture\)\.Unit|Station\.Plugin)',' ',device_log_origin)
        elif station == 'ACTUATION':
            device_log = re.sub(r'(Unit\(/dev/cu\.usbmodem14311302\)\.Plugin|atlas\.AppContainer(\.Unit\(/dev/cu\.usbmodem\d*\))?|Station\.Plugin)',' ',device_log_origin)
        elif station == 'BUTTON':
            device_log = re.sub(r'(Unit\(Unit1\)\.Plugin|atlas\.AppContainer\.Unit|Station\.Plugin)',' ',device_log_origin)
        elif station == 'FORCE':
            device_log = re.sub(r'(Unit\(/dev/cu\.usbmodem\d*?\)\.Plugin|atlas\.AppContainer\.Unit\(/dev/cu\.usbmodem\d*?\)|Station\.Plugin)',' ',device_log_origin)
    else:
        device_log = device_log_origin

    return device_log

# 依station做log解析
def classify_station_and_find_testitems(file_info_dict):
    # dict_testitem_to_tree = {}
    station = file_info_dict['station']
    # device_path = file_info_dict['device']
    # records_path = file_info_dict['records_path']

    if station in ['ColorCal','DVI']:
        dict_testitem_to_tree = Find_device_items_dvi_color_from(file_info_dict)
    elif station in ['QT0','QT1','FCT']:
        dict_testitem_to_tree = Find_device_items_qt_from(file_info_dict)
    elif station in ['IO1','IO2','IO3','IO4','IO5','IO6']:
        dict_testitem_to_tree = Find_device_items_IO_from(file_info_dict)
    elif station in ['ALS','ACTUATION','BUTTON','FORCE']:
        dict_testitem_to_tree = Find_device_items_Atlas_from(file_info_dict)
    elif station in ['FACT']:
        dict_testitem_to_tree = Find_device_items_FACT_from(file_info_dict)
    elif station in ['STATION30']:
        dict_testitem_to_tree = Find_device_items_CBT_from(file_info_dict)
    elif station in ['SW','SWDL']:
        dict_testitem_to_tree = Find_device_items_SWDL_from(file_info_dict)
    else:
        dict_testitem_to_tree = {}

    return dict_testitem_to_tree


##############################################################################

# UI drop的功能, 输出 file_info_dict
#
# file_info_dict = {'device'        : device log path
#                  , 'uart_path'    : UART log path
#                  , 'records_path' : records path
#                  , 'station'      : station name
#                  , 'version'      : station version
#                  , 'mlb'          : MLB#
#                  , 'sn'           : SrNm
#                  , 'message'      : other info, unused now
#                  , 'message_uart' : for other message about uart, 目前只有FACT有用, 显示在UI选测试项之后的UART栏位
#                  , 'message_device': for other device info, 目前只有Qt0有做, 显示在UI的device log栏位
#                  , 'bundle'       : bundle
#                  , 'ECID'         : ECID
#                  }


def Open_all_path(folder_path):
    list_path = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            path_temp = os.path.join(root, file_name)
            list_path.append(path_temp)
    return list_path

# 所有站通用
def Find_station_info(device_path):
    with open(device_path, "rb") as device_log_origin:
        device_log_origin = device_log_origin.read().decode("utf-8", "ignore")

    station_line = re.search(r'(station name|softwarename)\W*(\w*)',device_log_origin)
    station_name = station_line.group(2)
    # print(station_name)


    version_line = re.search(r'(station version -|"softwareversion")[" =:}]*([^"=\s:}]*)',device_log_origin)
    version = version_line.group(2)

    mlb = 'None'
    sn = 'None'
    bundle = 'None'
    ECID = 'None'
    # mlb_line = re.search(r'(Global Variable MLB_SN:\s*)([A-Z0-9]{17,19})',device_log_origin)
    mlb_line = re.search(r'(mlbsn[^A-Z0-9]*)([A-Z0-9]{17,19})',device_log_origin,flags=re.I)
    if mlb_line:
        mlb = mlb_line.group(2)

    sn_line = re.search(r'(calling amIOK with sn\s*|"serialnumber" = ")([A-Z0-9]{10,19})',device_log_origin)
    if sn_line:
        sn = sn_line.group(2)

    bundle_line = re.search(r'(sdk|iOS Build Version|BuildNumber)\W*(\w*)',device_log_origin,flags=re.I)
    if bundle_line:
        bundle = bundle_line.group(2)

    ECID_line = re.search(r'ecid[: =]\W*(0x\w*)',device_log_origin,flags=re.I)
    if ECID_line:
        ECID = ECID_line.group(1)

    return station_name, version, sn, mlb, bundle, ECID

# 目前只有Qt0用
def find_other_part_info(device_path,file_info_dict):
    with open(device_path, "rb") as device_log_origin:
        device_log_origin = device_log_origin.read().decode("utf-8", "ignore")

    # other_part_info = Call_dict('other_part_info')
    file_info_dict['message_device'] = {}
    message_device = file_info_dict['message_device']

    find_SFC = re.search(r'SFC Result:.*',device_log_origin)
    if find_SFC:
        message_device['  ------SFC info------'] = '--------------------------------'
        find_SFC_ = find_SFC.group(0)
        search_word_SFC = (['"(sbuild)"\] = (.*?),','"(bt_keyboard_sn)"\] = (.*?),','"(coo)"\] = (.*?),'
                            ,'"(front_nvm_barcode)"\] = (.*?),','"(region_code)"\] = (.*?),'
                            ,'"(mesa_module_sn)"\] = (.*?),','"(mlbsn)"\] = (.*?),'
                            ,'"(wifivendor)"\] = (.*?),','"(CPU_OPTION)"\] = (.*?),','"(battery_sn)"\] = (.*?),'
                            ,'"(RAM_OPTION)"\] = (.*?),','"(STORAGE_OPTION)"\] = (.*?),','"(lcm_sn)"\] = (.*?),'
                            ,'"(mpn)"\] = (.*?),','"(bt_trackpad_sn)"\] = (.*?),'])
        # word_name_SFC = ['sbuild','bt_keyboard_sn']
        # self.highlighting_rules2 = [(re.compile("{}".format(keyword)), self.keyword_format2)
        #                             for keyword in self.keywords2]
        search_compile = [re.compile("{}".format(search_word)) for search_word in search_word_SFC]
        # print(search_compile)
        for pattern_ in search_compile:
            match_ = pattern_.search(find_SFC_)
            if match_:
                # print(match_.group(1))
                # print(match_.group(2))
                # message_device[match_.group(1)] = re.sub(' ','',match_.group(2))

                name_temp = match_.group(1)
                value_temp = re.sub(' ','',match_.group(2))
                compile_temp = re.compile(r'("{}.* == ".*?").*?\]'.format(value_temp))
                # find_do_check_in_log = re.search(r'\[.*{}.* == .*\]'.format(name_temp),device_log_origin)
                find_do_check_in_log = compile_temp.search(device_log_origin)
                if find_do_check_in_log:
                    message_device[name_temp] = re.sub('==',', ',re.sub('[ "]','',find_do_check_in_log.group(1)))
                else:
                    message_device[name_temp] = value_temp


    message_device['  ------NAND info------'] = '--------------------------------'

    find_NAND_SN = re.search(r'Serial number\W*(APPLE.*)',device_log_origin)
    if find_NAND_SN:
        message_device['NAND_Serial_number'] = re.sub(' ','',find_NAND_SN.group(1))

    find_NAND_Model = re.search(r'Model number\W*(APPLE.*)',device_log_origin)
    if find_NAND_Model:
        message_device['NAND_Model_number'] = re.sub(' ','',find_NAND_Model.group(1))

    find_NAND_version = re.search(r'Firmware version\W*(\d+\.\d+\.\d+)',device_log_origin)
    if find_NAND_version:
        message_device['NAND_FW'] = re.sub(' ','',find_NAND_version.group(1))

    find_NAND_capacity = re.search(r'SSD capacity\W*(\w*)',device_log_origin)
    if find_NAND_capacity:
        message_device['NAND_capacity'] = re.sub(' ','',find_NAND_capacity.group(1))

    find_NAND_vender = re.search(r'Global Variable NandVendor:\W*(\w*)',device_log_origin)
    if find_NAND_vender:
        message_device['NAND_vender'] = re.sub(' ','',find_NAND_vender.group(1))


    message_device['  ------SOC info------'] = '--------------------------------'

    find_SOC_info = re.search(r'Version  - Midas_(.*)',device_log_origin)
    if find_SOC_info:
        message_device['SOC'] = re.sub(' ','',find_SOC_info.group(1))

    find_SOC_ECID = re.search(r'ecid[: =]\W*(0x\w*)',device_log_origin,flags=re.I)
    if find_SOC_ECID:
        message_device['ECID'] = re.sub(' ','',find_SOC_ECID.group(1))


    message_device['  ------other info------'] = '--------------------------------'

    find_bundle = re.search(r'SDK\W*(\w*)',device_log_origin)
    if find_bundle:
        message_device['bundle'] = re.sub(' ','',find_bundle.group(1))

    find_AJ_Cable_SN = re.search(r'CableSN: (.*)',device_log_origin)
    if find_AJ_Cable_SN:
        message_device['AJ_Cable_SN'] = re.sub(' ','',find_AJ_Cable_SN.group(1))

    find_WarlockSN = re.search(r'warlockSN: (.*)',device_log_origin)
    if find_WarlockSN:
        message_device['WarlockSN'] = re.sub(' ','',find_WarlockSN.group(1))

    
    return file_info_dict

def Find_LogPath_StationName(folder_path):

    file_info_dict = Call_dict('file_info_dict')
    dict_station_uartlogname = Call_dict('dict_station_uartlogname')


    # find path of files
    for temp_path in folder_path:
        if os.path.isfile(temp_path):
            print("*"*888,'\n','only one file, not folder, file path:')
            print(temp_path,'\n',"*"*888)
            return file_info_dict
        elif os.path.isdir(temp_path):
            list_path = Open_all_path(temp_path)

    # find device path, station
    for path_temp in list_path:
        # if 'system/device.log' in path_temp:
        if 'system' in path_temp and 'device.log' in path_temp:
            # print('****** system/device.log ******')
            file_info_dict['device'] = path_temp
            # print(path_temp)

            station_name, version, sn, mlb, bundle, ECID = Find_station_info(file_info_dict['device'])
            # print(file_info_dict['device'])
            # print(station_name, version, sn, mlb)
            # print()

            file_info_dict['station'] = station_name
            file_info_dict['version'] = version
            file_info_dict['mlb']     = mlb
            file_info_dict['sn']      = sn
            file_info_dict['bundle']  = bundle
            file_info_dict['ECID']    = ECID

            if station_name in ['QT0']:
                file_info_dict = other_part_info = find_other_part_info(file_info_dict['device'],file_info_dict)


        # elif 'AtlasLogs/unit.log' in path_temp:
        elif 'AtlasLogs' in path_temp and 'unit.log' in path_temp:
            # if 'unit.log' in path_temp:
            # print('****** AtlasLogs log ******')
            file_info_dict['device'] = path_temp

            station_name, version, sn, mlb, bundle, ECID = Find_station_info(file_info_dict['device'])
            # print(file_info_dict['device'])
            # print(station_name, version, sn, mlb)
            # print()

            file_info_dict['station'] = station_name
            file_info_dict['version'] = version
            file_info_dict['mlb']     = mlb
            file_info_dict['sn']      = sn
            file_info_dict['bundle']  = bundle
            file_info_dict['ECID']    = ECID


        # FACT
        elif '-clf.log' in path_temp:
            find_sn = re.search(r'\d+-\d+-(\w+)',path_temp)
            file_info_dict['device'] = path_temp
            file_info_dict['station'] = 'FACT'
            file_info_dict['message_uart'] = "FACT station doesn't have uart.log file"
            if find_sn:
                file_info_dict['sn'] = find_sn.group(1)
                file_info_dict['message_uart'] += ',I try to use csv file: '+find_sn.group(1)+'-xxxxxxxx-xxxxxx.csv'


        if 'records.csv'in path_temp.lower():
            file_info_dict['records_path'] = path_temp

    # find UART path
    if file_info_dict['station'] in dict_station_uartlogname.keys():
        for path_temp in list_path:
            if dict_station_uartlogname[file_info_dict['station']] in path_temp:
                file_info_dict['uart_path'] = path_temp

                # # for FACT
                # if file_info_dict['station'] == 'FACT':
                #     with open(path_temp, "rb") as UART_log_origin:
                #         UART_log_origin = UART_log_origin.read().decode("utf-8", "ignore")
                #     for i in UART_log_origin:
                #         print(i)

    return file_info_dict



##############################################################################

# 做log解析功能, 前面用classify_station_and_find_testitems()分类, 后面给UI做显示tree, log section
# 輸出dict_testitem_to_tree
#
# dict_testitem_to_tree = {'0':   {'test_name'      : test name
#                                 , 'sub_test_name' : sub test name
#                                 , 'time_start'    : start time, for find UART log
#                                 , 'time_stop'     : stop time, for find UART log
#                                 , 'time_duration' : time duration
#                                 , 'pass_fail'     : pass / fail / other
#                                 , 'records_fail'  : 读records.csv, 在records fail的测试项会标注fail, 显示在UI测试项第一栏标注红色
#                                 , 'index_start'   : 该测项device log开始行数
#                                 , 'index_stop'    : 该测项device log结束行数
#                                 }
#                         ,'1':   {...}
#                         ,'2':   {...}
#                         ,'3':   {...}
#                         ...       
#                         }


# Qt站完整, 没问题
def Find_device_items_qt_from(file_info_dict):
    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)

    # 切割log
    lines = re.split('\s*\n',device_log)
    for index_line in range(0,len(lines)):
        line = lines[index_line]

        # 分段, 里面用
        # temp_line.group(1) : time
        # temp_line.group(2) : 只有兩种 Test start / Test Pass(or Fail)
        # temp_line.group(3) : test index, 尾要带上”-“, 避免查到其他测试项, (ex: 找Main-1-xx, 如果查Main-1会查到Main-1x-xx)
        # temp_line.group(4) : other log
        temp_line = re.search(r'^(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+)\s*(.*?)\s*\[(\w+-\d+-)\d+\](.*)',line)
        if temp_line:
            index_temp = temp_line.group(3)
            start_pass_fail_temp = temp_line.group(2)
            other_temp = temp_line.group(4)

            # 有"Test start”开始做字典 / 资讯
            if 'Test Start' in start_pass_fail_temp:
                testname_subtestname_temp = re.search(r'<(.*?)>\s*<(.*?)>',other_temp)
                testname_temp = testname_subtestname_temp.group(1)
                subtestname_temp = testname_subtestname_temp.group(2)

                dict_testitem_to_tree[index_temp] = Call_dict('dict_testitem_to_tree')

                dict_testitem_to_tree[index_temp]['test_name']     = testname_temp
                dict_testitem_to_tree[index_temp]['sub_test_name'] = subtestname_temp
                # dict_testitem_to_tree[index_temp]['time_start']    = time_temp
                dict_testitem_to_tree[index_temp]['index_start']   = index_line

            # 找pass/fail, 如果都没有, 字典的['pass_fail']会保持None, UI显示蓝色
            if 'Fail' in start_pass_fail_temp:
                dict_testitem_to_tree[index_temp]['pass_fail'] = 'fail'
            elif 'Pass' in start_pass_fail_temp:
                dict_testitem_to_tree[index_temp]['pass_fail'] = 'pass'


            dict_testitem_to_tree[index_temp]['index_stop'] = index_line

    # 找测试项开始和结束, 使用index查. fail的测试项, 再报"[Test Fail]”后面会报fail讯息
    for index_temp,value_temp in dict_testitem_to_tree.items():

        start_line = lines[value_temp['index_start']]
        stop_line  = lines[value_temp['index_stop']]
        time_start = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+',start_line).group(0)
        time_stop  = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+',stop_line).group(0)

        value_temp['time_start'] = time_start
        value_temp['time_stop']  = time_stop
        value_temp['time_duration'] = cal_time_duration(time_start,time_stop)

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# Pass/Fail功能待建立 (部分fail log不在测试中发生, 在log最后面)
# 試試看抓, (12/15)
def Find_device_items_dvi_color_from(file_info_dict):
    dict_testitem_to_tree = {}
    records_path = file_info_dict['records_path']

    device_log = cut_fixture_unused_sentence(file_info_dict)

    # 找测试项, 关键字'<<(.*?)/TestFinish>>'
    find_testname_list = re.findall('<<(.*?)/TestFinish>>',device_log)
    print('test items')
    print('test items len : ',len(find_testname_list))
    print(find_testname_list)

    forcheck_items_start = []
    forcheck_items_stop = []

    # for find name correct, name1: xxxx / name2: xxxxyy
    # 避免测试项A与测试项B前面字段都相同的问题, 在切割log时后面带上一个空格
    device_log_ = re.sub('\n',' \n',device_log)
    lines = re.split('\n',device_log_)

    # 依测试项扫描log
    for i in range(0,len(find_testname_list)):
        index_temp = str(i)
        testname_temp = find_testname_list[i]

        # 做字典
        dict_testitem_to_tree[index_temp] = Call_dict('dict_testitem_to_tree')
        dict_testitem_to_tree[index_temp]['test_name'] = testname_temp

        # 扫描log
        for index_line in range(0,len(lines)):
            line = lines[index_line]

            # 开头行, 这边在测试项名称后面加空格
            if 'Running Test '+testname_temp+' ' in line:
                forcheck_items_start.append(line)
                time_start = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+',line)
                index_start_ = index_line
                # print(line)

                break
        # 扫描log
        for index_line in range(0,len(lines)):
            line = lines[index_line]

            # 找结束行, 这边在测试项名称后面有字符, 不用加空格
            if '<<'+testname_temp+'/TestFinish>>' in line:
                forcheck_items_stop.append(line)
                time_stop = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+',line)
                index_stop_ = index_line
                # print(line)



        if time_start and time_stop:
            time_start = time_start.group(0)
            time_stop = time_stop.group(0)
            time_duration = cal_time_duration(time_start,time_stop)

            dict_testitem_to_tree[index_temp]['time_start'] = time_start
            dict_testitem_to_tree[index_temp]['time_stop']  = time_stop
            dict_testitem_to_tree[index_temp]['time_duration'] = time_duration
            dict_testitem_to_tree[index_temp]['index_start'] = index_start_
            dict_testitem_to_tree[index_temp]['index_stop']  = index_stop_


    print('start line len : ',len(forcheck_items_start))
    print('stop line len : ',len(forcheck_items_stop))


    if len(forcheck_items_start) != len(forcheck_items_stop):
        print('******** error ********')
        print('start line len : ',len(forcheck_items_start))
        print('stop line len : ',len(forcheck_items_stop))

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能, 目前用records.csv标注fail项
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# 格式特殊, 没什么问题, 用records标fail
def Find_device_items_CBT_from(file_info_dict):
    dict_testitem_to_tree = {}
    records_path = file_info_dict['records_path']

    device_log = cut_fixture_unused_sentence(file_info_dict)

    lines = re.split('\n',device_log)
    index_temp = 0
    for index_line in range(0,len(lines)):
        line = lines[index_line]

        # 开头行
        if 'Running Test' in line:
            # print(line)
            find_testname = re.search(r'(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+) +Running Test (.*)',line)
            time_start = find_testname.group(1)
            testname = find_testname.group(2)

            dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
            dict_testitem_to_tree[str(index_temp)]['test_name'] = testname
            dict_testitem_to_tree[str(index_temp)]['time_start'] = time_start
            dict_testitem_to_tree[str(index_temp)]['index_start'] = index_line

            # 结束行 为 上一个测试项最后一行, 最后一个测试项的结束行 为log最后一行
            if index_temp >= 1:
                dict_testitem_to_tree[str(index_temp-1)]['index_stop'] = index_line - 1

                # 往前面找时间戳, 不一定每行都有时间戳, 找不到就往前找
                flag_temp = 1
                index_line_temp = index_line-1
                while flag_temp:
                    last_line = lines[index_line_temp]
                    find_time = re.search(r'(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+)',last_line)
                    index_line_temp -= 1
                    if find_time:
                        flag_temp = 0
                        time_stop = find_time.group(1)
                        dict_testitem_to_tree[str(index_temp-1)]['time_stop'] = time_stop

        # sub test name
        if 'Running Action' in line:
            find_sub_testname = re.search(r'Running Action (.*)',line)
            sub_testname = find_sub_testname.group(1)
            dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = sub_testname

            index_temp+=1

        # 最后一个测试项的结束行 为log最后一行
        if index_line == len(lines)-1:
            dict_testitem_to_tree[str(index_temp-1)]['index_stop'] = index_line
            flag_temp = 1
            index_line_temp = index_line

            # 往前面找时间戳, 不一定每行都有时间戳, 找不到就往前找
            while flag_temp:
                last_line = lines[index_line_temp-1]
                find_time = re.search(r'(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+)',last_line)
                if find_time:
                    flag_temp = 0
                    time_stop = find_time.group(1)
                    dict_testitem_to_tree[str(index_temp-1)]['time_stop'] = time_stop

    # 算时间 duration
    for index_,dict_value in dict_testitem_to_tree.items():
        dict_value['time_duration'] = cal_time_duration(dict_value['time_start'],dict_value['time_stop'])


    # 以下code, 用records标fail
    with open(records_path,'rb') as records_log_origin:
        records_log_origin = records_log_origin.read().decode("utf-8","ignore")
    lines = re.split('\n',records_log_origin)
    index_counter = 1
    for line in lines:
        print(len(line))
        if 'FAIL' in line:
            for index,value in dict_testitem_to_tree.items():
                if 'records' not in index:
                    if value['test_name'] in line and value['sub_test_name'] in line:
                        value['records_fail'] = 'fail'
                        # value['pass_fail'] = 'fail'

            index_name_records = 'records_'+str(index_counter)
            dict_testitem_to_tree[index_name_records] = Call_dict('dict_testitem_to_tree')

            line_split = re.split(',',line)
            flag_testname = 0
            for i in line_split:
                if i :
                    if flag_testname == 1:
                        dict_testitem_to_tree[index_name_records]['sub_test_name'] = i
                        break
                    if flag_testname == 0:
                        dict_testitem_to_tree[index_name_records]['test_name'] = i
                        flag_testname =1

            dict_testitem_to_tree[index_name_records]['records_fail'] = 'records.csv fail item.\n'\
                                                                        +'records messagge :'
            for i in line_split:
                dict_testitem_to_tree[index_name_records]['records_fail'] += i+'\n'

            index_counter+=1


    return dict_testitem_to_tree

# IO站完整, 没问题
def Find_device_items_IO_from(file_info_dict):
    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)
    lines = re.split('\n',device_log)

    # 先把log每行格式改为 log资讯, 时间, 第几行
    # log资讯最前面是测试项名称, 方便做测试项搜索
    index_temp = 0
    log_for_find_time = ''
    for index_line in range(0,len(lines)):
        line = lines[index_line]
        log_temp = re.search(r'(\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+) *(.*)',line)
        if log_temp:
            log_for_find_time += log_temp.group(2)+' '+log_temp.group(1)+' '+str(index_line)+'\n'

        # 测试项, 做字典
        if '###### Test started ######' in line:
            find_testname = re.search(r'\[(\w*?)\]',line)
            testname = find_testname.group(1)
            dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
            dict_testitem_to_tree[str(index_temp)]['test_name'] = testname

            index_temp += 1


    for index_,value_ in dict_testitem_to_tree.items():
        testname_ = value_['test_name']

        # 直接搜索相同测试项的log, 开始/结束行资讯
        lines_list = re.findall(testname_+'\]'+'.*',log_for_find_time)

        line_start_ = re.search(r'(\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+) (\d+)',lines_list[0])
        
        line_stop_  = re.search(r'(\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+) (\d+)',lines_list[-1])
        

        time_start_  = line_start_.group(1)
        time_stop_   = line_stop_.group(1)
        index_start_ = line_start_.group(2)
        index_stop_  = line_stop_.group(2)

        time_duration_ = cal_time_duration(time_start_,time_stop_)

        value_['time_start']    = time_start_
        value_['time_stop']     = time_stop_
        value_['time_duration'] = time_duration_
        value_['index_start']   = int(index_start_)
        value_['index_stop']    = int(index_stop_)

        # 找 pass / fail
        pass_flag = None
        fail_flag = None
        error_flag = None
        for line in lines_list:

            if '###' in line:
                if 'false' in line:
                    fail_flag = 1
                if 'true' in line:
                    pass_flag = 1
            if 'test failed' in line:
                fail_flag = 1

        if fail_flag:
            value_['pass_fail'] = 'fail'
        elif pass_flag:
            value_['pass_fail'] = 'pass'

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# ['ALS','ACTUATION','BUTTON','FORCE'], 没什么问题, (Fail的测试项漏切几行log, 12/15调整)
def Find_device_items_Atlas_from(file_info_dict):

    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)

    lines = re.split('\n',device_log)

    # 有sub test项, 用”log_sections”存主测试项
    index_temp = 0
    log_sections = ''
    flag_ForceCal_ActuatorCal = 0
    section_ForceCal_ActuatorCal = ''
    index_ForceCal_ActuatorCal = []
    list_index_line = []
    find_end_word = 'Test finished event for '
    # flag_testfinish_to_executingcmd=0
    for index_line in range(0,len(lines)-1):
        line = lines[index_line]
        log_sections += line + '\n'
        list_index_line.append(index_line)
        # if 'Test finished event for ' in line:
        #     flag_testfinish_to_executingcmd = 1

        # 一个测试项结束, 关键字'Test finished event for '
        # or 关键字'*'*90 for ForceCal/ActuatorCal test
        if find_end_word in line:
            
            ######### ForceCal/ActuatorCal test ########
            # 这两站有特别测试项, 这段code处理
            if flag_ForceCal_ActuatorCal == 1:
                # print('*'*88)

                find_end_word = 'Test finished event for '
                flag_ForceCal_ActuatorCal = 0
                index_ForceCal_ActuatorCal += list_index_line
                print(lines[index_ForceCal_ActuatorCal[-1]])
                print('*'*888)
                list_index_line = []
                for index_line_temp in index_ForceCal_ActuatorCal:
                    line = lines[index_line_temp]
                    # section_ForceCal_ActuatorCal += line + '\n'
                    # list_index_line.append(index_line)
                    if 'Atlas.create_record' in line or index_line_temp == index_ForceCal_ActuatorCal[-1]:
                        if str(index_temp) in dict_testitem_to_tree.keys():
                            index_temp += 1
                        dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
                        dict_testitem_to_tree[str(index_temp)]['test_name']     = testname_

                        # Sub test name
                        find_subtestname = re.search(r'\[(ForceCal|ActuatorCal),\s*(.*)\]',section_ForceCal_ActuatorCal)
                        if find_subtestname:
                            subtestname_ = find_subtestname.group(2)
                            dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = subtestname_


                        # 行数/时间
                        find_time = re.findall(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',section_ForceCal_ActuatorCal)
                        print(index_temp)
                        print(section_ForceCal_ActuatorCal)
                        if find_time:
                            dict_testitem_to_tree[str(index_temp)]['time_start']    = find_time[0]
                            dict_testitem_to_tree[str(index_temp)]['time_stop']     = find_time[-1]
                            dict_testitem_to_tree[str(index_temp)]['time_duration'] = cal_time_duration(find_time[0],find_time[-1])
                        dict_testitem_to_tree[str(index_temp)]['index_start']   = list_index_line[0]
                        dict_testitem_to_tree[str(index_temp)]['index_stop']    = list_index_line[-1]
                        print(find_time[0])
                        print(find_time[-1])
                        print(dict_testitem_to_tree[str(index_temp)]['time_duration'])

                        # Pass/Fail for total log dict
                        find_pass_fail = re.search('t101ErrMessage: (\w*)',section_ForceCal_ActuatorCal)
                        if find_pass_fail:
                            dict_testitem_to_tree[str(index_temp)]['pass_fail'] = find_pass_fail.group(1).lower()

                        # 找measurement值, 有些测试项没有limit, 查到先判为pass
                        find_measurement = re.search(r'measurement:([\-\d\.]*)',section_ForceCal_ActuatorCal)
                        if find_measurement:
                            dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'pass'
                            measurement_ = find_measurement.group(1)

                        # 正常log状况, 比较limit与measurement
                        # 找limit值, 有些log跳行(治具问题), limit不只一个(跳到上个或下个测试项), 只做正常log状况
                        # 跳行状况, pass/fail设置为None
                        find_limit_list = re.findall(r'limit:\{(.*?)\}',section_ForceCal_ActuatorCal)
                        if len(find_limit_list) >= 2:
                            dict_testitem_to_tree[str(index_temp)]['pass_fail'] = None                        
                        elif len(find_limit_list) == 1:
                            # find_limit = re.search(r'limit:\{(.*?)\}',find_limit_list[0])
                            find_lowerlimit = re.search(r'"lowerLimit":([\-\d\.]*)',find_limit_list[0]).group(1)
                            find_upperlimit = re.search(r'"upperLimit":([\-\d\.]*)',find_limit_list[0]).group(1)
                            if float(find_upperlimit) <= float(measurement_) or float(measurement_) <= float(find_lowerlimit):
                                dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'



                        # print('-'*88)
                        # print(index_temp)
                        # print(dict_testitem_to_tree[str(index_temp)])
                        # print(section_ForceCal_ActuatorCal)
                        # index_temp += 1
                        section_ForceCal_ActuatorCal = ''
                        list_index_line = []
                    section_ForceCal_ActuatorCal += line + '\n'
                    list_index_line.append(index_line_temp)




            ######### Normal test ########
            else:
                testname_ = re.search('Test finished event for (.*)',line).group(1)
                time_stop_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',line).group(0)
                time_start_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',log_sections).group(0)
                # print(testname_)
                ######### ForceCal/ActuatorCal test ########
                # 这两站有特别测试项, 这段code切換
                if testname_ == 'ForceCal' or testname_ == 'ActuatorCal':
                    if len(index_ForceCal_ActuatorCal) == 0:
                        index_ForceCal_ActuatorCal += list_index_line
                        flag_ForceCal_ActuatorCal = 1
                        # Change end word, to cut test:'ForceCal'/'ActuatorCal' total log
                        find_end_word = '*'*90



                else:
                    if str(index_temp) in dict_testitem_to_tree.keys():
                        index_temp += 1
                    dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
                    dict_testitem_to_tree[str(index_temp)]['test_name']     = testname_
                    dict_testitem_to_tree[str(index_temp)]['time_start']    = time_start_
                    dict_testitem_to_tree[str(index_temp)]['time_stop']     = time_stop_
                    dict_testitem_to_tree[str(index_temp)]['time_duration'] = cal_time_duration(time_start_,time_stop_)
                    dict_testitem_to_tree[str(index_temp)]['index_start']   = list_index_line[0]
                    dict_testitem_to_tree[str(index_temp)]['index_stop']    = list_index_line[-1]


                    # 找 pass / fail
                    find_pass_ = re.search(r'(Successfully completed command|[Tt]est Complete!)',log_sections)
                    if find_pass_:
                        dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'pass'
                    find_fail_ = re.search('(Failed command|TestFailedError)',log_sections)
                    if find_fail_:
                        dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'

                    # 在”log_sections”找 sub test
                    find_sub_testname_list = re.findall('<Info> command: (.*)',log_sections)
                    if len(find_sub_testname_list) == 0:
                        print('len(find_sub_testname_list) == 0')


                    # 只有一个sub test, 直接做
                    elif len(find_sub_testname_list) == 1:
                        dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = find_sub_testname_list[0]
                        # special for "las_LidAngleCheck"
                        # las_LidAngleCheck测试, 确认是否超过limit
                        if 'las_LidAngleCheck' in testname_:
                            find_values = re.search(r'\{"lowerLimit":(.*?),.*"upperLimit":(.*?),.*"value":(.*?)\}',log_sections)
                            if find_values:
                                lowerlimit = find_values.group(1)
                                upperlimit = find_values.group(2)
                                value_ = find_values.group(3)
                                if float(upperlimit) <= float(value_) or float(value_) <= float(lowerlimit):
                                    dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'
                    # 多个sub test
                    elif  len(find_sub_testname_list) >= 2:
                        dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = 'multi-'
                        dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'multi-'


                        ####### do multi
                        # 这段有点绕, 主要是'Executing command’为开头行, 结尾行看UUID
                        # 再从sub test log里面判断pass/fail
                        sub_index_temp = 1
                        sub_section = ''
                        cmd_uuid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXX'
                        sub_list_index_line = []


                        for index_line_sub in list_index_line:
                            sub_line = lines[index_line_sub]

                            if 'Executing command'in sub_line:
                                cmd_uuid_flag = 0

                                for k in range(index_line_sub,list_index_line[-1]):
                                    k_line = lines[k]
                                    sub_section += k_line + '\n'
                                    sub_list_index_line.append(k)

                                    if cmd_uuid in k_line:
                                        spec_index = str(index_temp)+'-'+str(sub_index_temp)
                                        dict_testitem_to_tree[spec_index] = Call_dict('dict_testitem_to_tree')

                                        time_stop_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',k_line).group(0)
                                        time_start_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',sub_section).group(0)
                                        subtestname_ = re.search('<Info> command: (.*)',sub_section)
                                        if subtestname_:
                                            dict_testitem_to_tree[spec_index]['sub_test_name'] = subtestname_.group(1)
                                        if 'Successfully completed command' in k_line:
                                            dict_testitem_to_tree[spec_index]['pass_fail']  = 'pass'
                                        elif 'Failed command' in k_line:
                                            dict_testitem_to_tree[spec_index]['pass_fail']  = 'fail'


                                        dict_testitem_to_tree[spec_index]['test_name'] = '-'
                                        dict_testitem_to_tree[spec_index]['time_start'] = time_start_
                                        dict_testitem_to_tree[spec_index]['time_stop'] = time_stop_
                                        dict_testitem_to_tree[spec_index]['time_duration'] = cal_time_duration(time_start_,time_stop_)
                                        dict_testitem_to_tree[spec_index]['index_start'] = sub_list_index_line[0]
                                        dict_testitem_to_tree[spec_index]['index_stop'] = sub_list_index_line[-1]

                                        sub_index_temp +=1
                                        sub_section=''
                                        sub_list_index_line = []
                                        break

                                    if 'command uuid: ' in k_line and cmd_uuid_flag == 0:
                                        cmd_uuid = re.search(r'command uuid: *([\w-]*)',k_line).group(1)
                                        cmd_uuid_flag = 1


            # index_temp +=1
            log_sections = ''
            list_index_line = []

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# ['ALS','ACTUATION','BUTTON','FORCE'], 没什么问题, (Fail的测试项漏切几行log, 12/15调整)
def Find_device_items_Atlas_from_reserve(file_info_dict):

    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)

    lines = re.split('\n',device_log)

    # 有sub test项, 用”log_sections”存主测试项
    index_temp = 0
    log_sections = ''
    list_index_line = []
    # flag_testfinish_to_executingcmd=0
    for index_line in range(0,len(lines)-1):
        line = lines[index_line]
        log_sections += line + '\n'
        list_index_line.append(index_line)
        # if 'Test finished event for ' in line:
        #     flag_testfinish_to_executingcmd = 1

        # 一个测试项结束, 关键字'Test finished event for '
        if 'Test finished event for ' in line:
        # if flag_testfinish_to_executingcmd == 1 and 'Executing command' in lines[index_line+1]:
            # flag_testfinish_to_executingcmd=0
            testname_ = re.search('Test finished event for (.*)',line).group(1)
            time_stop_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',line).group(0)
            time_start_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',log_sections).group(0)

            dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
            dict_testitem_to_tree[str(index_temp)]['test_name']     = testname_
            dict_testitem_to_tree[str(index_temp)]['time_start']    = time_start_
            dict_testitem_to_tree[str(index_temp)]['time_stop']     = time_stop_
            dict_testitem_to_tree[str(index_temp)]['time_duration'] = cal_time_duration(time_start_,time_stop_)
            dict_testitem_to_tree[str(index_temp)]['index_start']   = list_index_line[0]
            dict_testitem_to_tree[str(index_temp)]['index_stop']    = list_index_line[-1]

            # 找 pass / fail
            find_pass_ = re.search(r'(Successfully completed command|[Tt]est Complete!)',log_sections)
            if find_pass_:
                dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'pass'
            find_fail_ = re.search('(Failed command|TestFailedError)',log_sections)
            if find_fail_:
                dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'

            # 在”log_sections”找 sub test
            find_sub_testname_list = re.findall('<Info> command: (.*)',log_sections)
            if len(find_sub_testname_list) == 0:

                ######### ForceCal/ActuatorCal test ########
                # 这两站有特别测试项, 这段code处理
                # 
                if testname_ == 'ForceCal' or testname_ == 'ActuatorCal':
                    find_subtestname = re.search(r'\[(ForceCal|ActuatorCal),\s*(.*)\]',log_sections)
                    if find_subtestname:
                        subtestname_ = find_subtestname.group(2)
                        dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = subtestname_

                    # 找measurement值, 有些测试项没有limit, 查到先判为pass
                    find_measurement = re.search(r'measurement:([\-\d\.]*)',log_sections)
                    if find_measurement:
                        dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'pass'
                        measurement_ = find_measurement.group(1)
                    # find_limit = re.search(r'limit:\{(.*?)\}',log_sections)
                    # if find_limit:
                    #     # print(find_limit.group(1))
                    #     find_lowerlimit = re.search(r'"lowerLimit":([\-\d\.]*)',find_limit.group(1)).group(1)
                    #     find_upperlimit = re.search(r'"upperLimit":([\-\d\.]*)',find_limit.group(1)).group(1)
                    #     # find_name_ = re.search(r'"name":(.*?),',find_limit.group(1)).group(1)
                    #     if float(find_upperlimit) <= float(measurement_) or float(measurement_) <= float(find_lowerlimit):
                    #         dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'

                    # 找limit值, 有些log跳行(治具问题), limit不只一个(跳到上个或下个测试项), 只做正常log状况
                    # 跳行状况, pass/fail设置为None
                    find_limit_list = re.findall(r'limit:\{(.*?)\}',log_sections)
                    if len(find_limit_list) >= 2:
                        dict_testitem_to_tree[str(index_temp)]['pass_fail'] = None

                    # 正常log状况, 比较limit与measurement
                    elif len(find_limit_list) == 1:
                        # find_limit = re.search(r'limit:\{(.*?)\}',find_limit_list[0])
                        find_lowerlimit = re.search(r'"lowerLimit":([\-\d\.]*)',find_limit_list[0]).group(1)
                        find_upperlimit = re.search(r'"upperLimit":([\-\d\.]*)',find_limit_list[0]).group(1)
                        if float(find_upperlimit) <= float(measurement_) or float(measurement_) <= float(find_lowerlimit):
                            dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'

            # 只有一个sub test, 直接做
            elif len(find_sub_testname_list) == 1:
                dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = find_sub_testname_list[0]
                # special for "las_LidAngleCheck"
                # 这项测试挺特殊的, 感觉是治具临时增加的测试
                if 'las_LidAngleCheck' in testname_:
                    find_values = re.search(r'\{"lowerLimit":(.*?),.*"upperLimit":(.*?),.*"value":(.*?)\}',log_sections)
                    if find_values:
                        lowerlimit = find_values.group(1)
                        upperlimit = find_values.group(2)
                        value_ = find_values.group(3)
                        if float(upperlimit) <= float(value_) or float(value_) <= float(lowerlimit):
                            dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'
            # 多个sub test
            elif  len(find_sub_testname_list) >= 2:
                dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = 'multi-'
                dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'multi-'


                ####### do multi
                # 这段有点绕, 主要是'Executing command’为开头行, 结尾行看UUID
                # 再从sub test log里面判断pass/fail
                sub_index_temp = 1
                sub_section = ''
                cmd_uuid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXX'
                sub_list_index_line = []


                for index_line_sub in list_index_line:
                    sub_line = lines[index_line_sub]

                    if 'Executing command'in sub_line:
                        cmd_uuid_flag = 0

                        for k in range(index_line_sub,list_index_line[-1]):
                            k_line = lines[k]
                            sub_section += k_line + '\n'
                            sub_list_index_line.append(k)

                            if cmd_uuid in k_line:
                                spec_index = str(index_temp)+'-'+str(sub_index_temp)
                                dict_testitem_to_tree[spec_index] = Call_dict('dict_testitem_to_tree')

                                time_stop_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',k_line).group(0)
                                time_start_ = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',sub_section).group(0)
                                subtestname_ = re.search('<Info> command: (.*)',sub_section)
                                if subtestname_:
                                    dict_testitem_to_tree[spec_index]['sub_test_name'] = subtestname_.group(1)
                                if 'Successfully completed command' in k_line:
                                    dict_testitem_to_tree[spec_index]['pass_fail']  = 'pass'
                                elif 'Failed command' in k_line:
                                    dict_testitem_to_tree[spec_index]['pass_fail']  = 'fail'


                                dict_testitem_to_tree[spec_index]['test_name'] = '-'
                                dict_testitem_to_tree[spec_index]['time_start'] = time_start_
                                dict_testitem_to_tree[spec_index]['time_stop'] = time_stop_
                                dict_testitem_to_tree[spec_index]['time_duration'] = cal_time_duration(time_start_,time_stop_)
                                dict_testitem_to_tree[spec_index]['index_start'] = sub_list_index_line[0]
                                dict_testitem_to_tree[spec_index]['index_stop'] = sub_list_index_line[-1]

                                sub_index_temp +=1
                                sub_section=''
                                sub_list_index_line = []
                                break

                            if 'command uuid: ' in k_line and cmd_uuid_flag == 0:
                                cmd_uuid = re.search(r'command uuid: *([\w-]*)',k_line).group(1)
                                cmd_uuid_flag = 1


            index_temp +=1
            log_sections = ''
            # print(list_index_line)
            list_index_line = []

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# 格式特殊, 没什么问题
def Find_device_items_FACT_from(file_info_dict):
    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)

    lines = re.split(' *\n',device_log)
    index_temp = 0
    for index_line in range(0,len(lines)):
        line = lines[index_line]

        # 开头行
        if '<@>Running' in line:
            dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
            pass_fail = None

            find_testname = re.search(r'(\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+).*?Running *(\w*)',line)
            if find_testname:
                testname_ = find_testname.group(2)

                time_start = find_testname.group(1)
                time_translate = re.search(r'(\d\d/\d\d)/(\d\d)( *\d\d?:\d\d:\d\d.\d+)',time_start)
                time_start_ = '20' + time_translate.group(2) + '/' + time_translate.group(1) + time_translate.group(3)

                dict_testitem_to_tree[str(index_temp)]['test_name'] = testname_
                dict_testitem_to_tree[str(index_temp)]['time_start'] = time_start_
                dict_testitem_to_tree[str(index_temp)]['index_start'] = index_line

            index_temp +=1

        # fail keyword, 目前只查到以下fail关键字, 要扩充直接在这边加
        if 'Mask violation :' in line:
            pass_fail = 'fail'

        # 结束行
        if '<@>Finished' in line:
            find_testname = re.search(r'(\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+).*?Finished *(\w*)',line)
            if find_testname:
                testname_stop = find_testname.group(2)

                time_stop = find_testname.group(1)
                time_translate = re.search(r'(\d\d/\d\d)/(\d\d)( *\d\d?:\d\d:\d\d.\d+)',time_stop)
                time_stop_ = '20' + time_translate.group(2) + '/' + time_translate.group(1) + time_translate.group(3)

                dict_testitem_to_tree[str(index_temp-1)]['time_stop'] = time_stop_
                dict_testitem_to_tree[str(index_temp-1)]['index_stop'] = index_line
                dict_testitem_to_tree[str(index_temp-1)]['time_duration'] = cal_time_duration(time_start_,time_stop_)
                if pass_fail:
                    dict_testitem_to_tree[str(index_temp-1)]['pass_fail'] = pass_fail
                elif testname_stop == testname_:
                    dict_testitem_to_tree[str(index_temp-1)]['pass_fail'] = 'pass'

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree

# SWDL
def Find_device_items_SWDL_from(file_info_dict):
    dict_testitem_to_tree = {}

    device_log = cut_fixture_unused_sentence(file_info_dict)

    index_temp = 0
    lines = re.split(' *\n',device_log)
    for index_line in range(0,len(lines)):
        line = lines[index_line]
        # print(line)

        if '==========' in line:

            # 开头行
            if 'Action:' in line:
                print(line)
                find_time_testname = re.search(r'(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+).*Action: (\w*?/)?(\w*?)_(\w*?) ==========',line)
                testname_ = find_time_testname.group(3)
                sub_testname_ = find_time_testname.group(4)
                time_start = find_time_testname.group(1)

                dict_testitem_to_tree[str(index_temp)] = Call_dict('dict_testitem_to_tree')
                dict_testitem_to_tree[str(index_temp)]['test_name'] = testname_
                dict_testitem_to_tree[str(index_temp)]['sub_test_name'] = sub_testname_
                dict_testitem_to_tree[str(index_temp)]['time_start'] = time_start
                dict_testitem_to_tree[str(index_temp)]['index_start'] = index_line

                print(dict_testitem_to_tree)
                print(testname_)
                print(sub_testname_)
                print(time_start)
                print(index_line)

            # 结束行, 治具报 pass / fail 同一行
            elif 'test' in line:
                find_time_pass = re.search(r'(\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d.\d+).*\(.*\) *(\w*)', line)
                time_stop = find_time_pass.group(1)
                pass_fail = find_time_pass.group(2)
                dict_testitem_to_tree[str(index_temp)]['time_stop'] = time_stop
                dict_testitem_to_tree[str(index_temp)]['index_stop'] = index_line
                dict_testitem_to_tree[str(index_temp)]['time_duration'] = cal_time_duration(time_start,time_stop)
                if pass_fail.lower() == 'pass':
                    dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'pass'
                elif pass_fail.lower() == 'fail':
                    dict_testitem_to_tree[str(index_temp)]['pass_fail'] = 'fail'

                print(time_stop)
                print(pass_fail)
                print(index_line)

                index_temp +=1

    # 把records.csv的fail项放在最后面, 看record fail项比较方便, 可不用此功能
    Add_records_fail_item(file_info_dict, dict_testitem_to_tree)
    return dict_testitem_to_tree


# 读record.csv的fail项, 放在UI測試項欄最后面, 不做不影响运行
def Add_records_fail_item(file_info_dict,dict_testitem_to_tree):
    if file_info_dict['records_path'] == None:
        return
    records_path = file_info_dict['records_path']

    with open(records_path,'rb') as records_log_origin:
        records_log_origin = records_log_origin.read().decode("utf-8","ignore")
    lines = re.split('\n', records_log_origin)
    index_counter = 1
    for line in lines:
        line_split = re.split(',', line)
        for cell_ in line_split:
            if cell_.lower() == 'fail' or cell_ == 'RELAXED PASS':

                for index, value in dict_testitem_to_tree.items():
                    if 'records' not in index:
                        if value['sub_test_name']:
                            if value['test_name'] in line and value['sub_test_name'] in line:
                                value['records_fail'] = 'fail'
                            elif value['test_name'] in line and value['sub_test_name'] == 'multi-':
                                value['records_fail'] = 'fail'
                        elif value['test_name'] in line:
                            value['records_fail'] = 'fail'

                index_name_records = 'records_' + str(index_counter)
                dict_testitem_to_tree[index_name_records] = Call_dict('dict_testitem_to_tree')

                line_split = re.split(',', line)
                flag_testname = 0
                for i in line_split:
                    if i:
                        if flag_testname == 1:
                            dict_testitem_to_tree[index_name_records]['sub_test_name'] = i
                            break
                        if flag_testname == 0:
                            dict_testitem_to_tree[index_name_records]['test_name'] = i
                            flag_testname = 1

                dict_testitem_to_tree[index_name_records]['records_fail'] = 'records.csv fail item.\n' \
                                                                            + 'records messagge :\n'
                for i in line_split:
                    dict_testitem_to_tree[index_name_records]['records_fail'] += i + '\n'

                index_counter += 1





##############################################################################
##############################################################################
##############################################################################
# 这个区间给UI用的

# find device log section
def Find_device_log_section(file_info_dict,dict_testitem_to_tree):

    device_log = cut_fixture_unused_sentence(file_info_dict)
    lines = re.split('\n',device_log)

    log_section = ''
    for index_temp in range(dict_testitem_to_tree['index_start'],dict_testitem_to_tree['index_stop']+1):
        log_section += lines[index_temp] + '\n'

    return log_section

# find uart log section, 开头行 "[000658E2:0801401C] :-)"
def Find_uart_log_section(file_info_dict,time_start,time_stop):
    with open(file_info_dict['uart_path'], "rb") as uart_log_origin:
        uart_log_origin = uart_log_origin.read().decode("utf-8", "ignore")


    time_from_check = re.search(r'(\d\d\d\d.\d\d.\d\d )(\d\d?)(:\d\d:\d\d.\d+)',time_start)
    if len(time_from_check.group(2)) == 1:
        time_start = time_from_check.group(1)+'0'+time_from_check.group(2)+time_from_check.group(3)

    time_from_check = re.search(r'(\d\d\d\d.\d\d.\d\d )(\d\d?)(:\d\d:\d\d.\d+)',time_stop)
    if len(time_from_check.group(2)) == 1:
        time_stop = time_from_check.group(1)+'0'+time_from_check.group(2)+time_from_check.group(3)

    time_start = float(re.sub(r'[-/: ]','',time_start))
    time_stop  = float(re.sub(r'[-/: ]','',time_stop))


    flag_start = 0
    uart_log_section = ''
    line_last = ''
    lines = re.split('\n',uart_log_origin)
    for line in lines:

        if '-write' in line:
            uart_time = re.search(r'\d\d\d\d.\d\d.\d\d \d\d:\d\d:\d\d.\d+',line).group(0)
            uart_time = float(re.sub(r'[-/: ]','',uart_time))

            if time_start <= uart_time and uart_time <= time_stop:
                flag_start = 1
            else:
                flag_start = 0

        if flag_start == 1:
            uart_log_section += line_last+'\n'

        line_last = line

    return uart_log_section

# find uart log section, 只看时间
def Find_uart_log_section_onlytime(file_info_dict,time_start,time_stop):
    with open(file_info_dict['uart_path'], "rb") as uart_log_origin:
        uart_log_origin = uart_log_origin.read().decode("utf-8", "ignore")

    time_from_check = re.search(r'(\d\d\d\d.\d\d.\d\d )(\d\d?)(:\d\d:\d\d.\d+)',time_start)
    if len(time_from_check.group(2)) == 1:
        time_start = time_from_check.group(1)+'0'+time_from_check.group(2)+time_from_check.group(3)

    time_from_check = re.search(r'(\d\d\d\d.\d\d.\d\d )(\d\d?)(:\d\d:\d\d.\d+)',time_stop)
    if len(time_from_check.group(2)) == 1:
        time_stop = time_from_check.group(1)+'0'+time_from_check.group(2)+time_from_check.group(3)

    time_start = float(re.sub(r'[-/: ]','',time_start))
    time_stop  = float(re.sub(r'[-/: ]','',time_stop))


    # flag_start = 0
    uart_log_section = ''
    # line_last = ''
    lines = re.split('\n',uart_log_origin)
    for line in lines:

        # if '<post-write>' in line or 'rawuart-write' in line:
        # uart_time = re.search(r'\d\d\d\d-\d\d-\d\d \d\d?:\d\d:\d\d.\d+',line).group(0)
        uart_time = re.search(r'\d\d\d\d.\d\d.\d\d \d\d:\d\d:\d\d.\d+',line)
        # print(line)
        # print(uart_time)
        if uart_time:
            uart_time = float(re.sub(r'[-/: ]','',uart_time.group(0)))

            if time_start <= uart_time and uart_time <= time_stop:
                uart_log_section += line+'\n'
        #     flag_start = 1
        # else:
        #     flag_start = 0

        # if flag_start == 1:
            # uart_log_section += line_last+'\n'

        # line_last = line

    return uart_log_section

# FACT没有UART log档案, 用xxxxxxxxxxx-xxxxxxxx-xxxxxx.csv档案
def Find_uart_csv_section_FACT(file_info_dict,time_start,time_stop):
    with open(file_info_dict['uart_path'], "r") as uart_csv:
        uart_csv_r = csv.reader(uart_csv)

        uart_log_section =    '########################################################################################\n'\
                             +'#####           '+file_info_dict['message_uart'] +'          #####\n'\
                             +'########################################################################################\n'

        time_start = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d',time_start).group(0)
        time_stop = re.search(r'\d\d\d\d/\d\d/\d\d \d\d?:\d\d:\d\d',time_stop).group(0)

        section_temp = ''
        flag_first_row = 0
        title_row = []
        for csv_row in uart_csv_r:
            if flag_first_row == 0:
                flag_first_row = 1
                for i in csv_row:
                    title_row.append(re.sub('\s*','',i)+' :\n')
                # print(title_row)
            else:
                # for csv_colunm in csv_row:
                section_temp += '-'*66+'\n'
                for j in range(0,len(csv_row)):
                    section_temp += title_row[j] + csv_row[j] +'\n'

                    time_temp = re.search(r'\d\d/\d\d/\d\d \d\d:\d\d:\d\d',csv_row[j])

                    if time_temp:
                        time_translate = re.search(r'(\d\d/\d\d)/(\d\d)( \d\d:\d\d:\d\d)',time_temp.group(0))
                        time_uart = '20' + time_translate.group(2)+'/'+time_translate.group(1)+time_translate.group(3)
                        if time_uart >= time_start and time_uart <= time_stop:
                            uart_log_section += section_temp
                            section_temp = ''
                        else:
                            section_temp = ''


    return uart_log_section

# 做highlight时, 把该测试项的UART log有的命令都拉出来做keywords
def Find_uart_keywords(uart_log_section):
    keyword_UART_cmd_r = []
    keyword_UART_cmd_w = []
    keyword_UART_cmd = []
    flag_rw = ''
    if uart_log_section:
        lines = re.split('\n',uart_log_section)
        print('UART lines: ',len(lines))
        for line in lines:
            # print(line)
            cmd_ = re.search(r'(.*)\[\d{4,5}\]: ?(.+)',line)
        
            if cmd_:
                if 'write' in cmd_.group(1):
                    flag_rw = 'w'
                else:
                    flag_rw = 'r'
                cmd_ = cmd_.group(2)
                cmd_ = re.sub(r'<Info> ','',cmd_)

                # only_1word = re.sub(r'\w','',cmd_)
                # if only_1word !='' and len(cmd_) >=5:
                cmd_ = re.sub(r'(^\s*|\s*$)','',cmd_)
                head_word = re.search(r'^\W',cmd_)
                if head_word and len(cmd_) >=3:
                    sentence_ = re.search(r'(.)(.*)',cmd_)
                    sentence_1 = sentence_.group(1)
                    sentence_2 = sentence_.group(2)
                    sentence_2 = re.sub(r'[^\w \-]', '.', sentence_2)
                    cmd_chang_special_word = "(\s|^|'|\")\\" +sentence_1+sentence_2 +"(\s|$|'|\")"
                    if cmd_chang_special_word not in keyword_UART_cmd:
                        keyword_UART_cmd.append(cmd_chang_special_word)
                        if flag_rw == 'w':
                            keyword_UART_cmd_w.append(cmd_chang_special_word)
                        else:
                            keyword_UART_cmd_r.append(cmd_chang_special_word)

                elif len(cmd_) >=3:
                    # cmd_chang_special_word = re.sub(r'[\(\)\[\]\{\}\\\*\?\^\$\|\+]','.',cmd_)
                    cmd_chang_special_word = re.sub(r'[^\w \-]','.',cmd_)
                    # cmd_chang_special_word = re.sub(r'(^\s*|\s*$)','',cmd_chang_special_word)
                    cmd_chang_special_word = "(\s|$|'|\")" + cmd_chang_special_word +"(\s|$|'|\")"

                    # cmd_chang_special_word = re.sub(r'\s\s+','\s*',cmd_chang_special_word)
                    if '......' not in cmd_chang_special_word and cmd_chang_special_word not in keyword_UART_cmd:
                        keyword_UART_cmd.append(cmd_chang_special_word)
                        if flag_rw == 'w':
                            keyword_UART_cmd_w.append(cmd_chang_special_word)
                        else:
                            keyword_UART_cmd_r.append(cmd_chang_special_word)
    ###### do? delete?
    # print('--'*888)
    # print(len(keyword_UART_cmd_w))
    # print(len(keyword_UART_cmd_r))
    # if len(keyword_UART_cmd_w) >= 100:
    #     keyword_UART_cmd_w = []
    # if len(keyword_UART_cmd_r) >= 100:
    #     keyword_UART_cmd_r = []
    return keyword_UART_cmd_w,keyword_UART_cmd_r

##############################################################################
##############################################################################
##############################################################################









class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.setAcceptDrops(True)
        self.last_index = None


        self.tree.itemClicked.connect(self.function)

    # test items
    def function(self,item,column):

        # 选同一个测试项不重复做
        test_index = item.text(0)
        if test_index == self.last_index:
            return


        test_time_start = self.dict_testitem_to_tree[test_index]['time_start']
        test_time_stop  = self.dict_testitem_to_tree[test_index]['time_stop']

        # 做device log
        if self.dict_testitem_to_tree[test_index]['index_start'] != None:
            device_log_section = Find_device_log_section(self.file_info_dict
                                                        ,self.dict_testitem_to_tree[test_index])
        elif self.dict_testitem_to_tree[test_index]['records_fail']:
            device_log_section = self.dict_testitem_to_tree[test_index]['records_fail']

        # 給highlight用
        global uart_log_section_for_highlight
        uart_log_section_for_highlight = ''

        # 做UART log
        if self.file_info_dict['uart_path'] and test_time_start != None:
            if self.file_info_dict['station'] in ['BUTTON','SW','SWDL']:
                uart_log_section = Find_uart_log_section_onlytime(self.file_info_dict
                                                                    ,test_time_start
                                                                    ,test_time_stop)
            elif self.file_info_dict['station'] in ['FACT']:
                uart_log_section = Find_uart_csv_section_FACT(self.file_info_dict
                                                                    ,test_time_start
                                                                    ,test_time_stop)

            else:
                uart_log_section = Find_uart_log_section(self.file_info_dict
                                                        ,test_time_start
                                                        ,test_time_stop)
            # 給highlight
            uart_log_section_for_highlight = uart_log_section

            # show UART log
            self.textedit_uart.setPlainText(uart_log_section)
        else:
            self.textedit_uart.setPlainText('no UART log in folder, or other error.')





        # 做highlight, show log
        self.textedit_device.setPlainText(device_log_section)
        print(self.textedit_device.document)
        self.highlighter = MyHighlighter(self.textedit_device.document())


        self.last_index = test_index



    # 拉档案途中会有功能, 目前没用到
    def dragEnterEvent(self, event):
        # print("drag event")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # 拉档案在这边
    def dropEvent(self, event):
        files = []
        urls = [u for u in event.mimeData().urls()]
        for url in urls:
            files.append(url.toLocalFile())
        print(files)


        # inital
        self.tree.clear()
        self.textedit_device.setPlainText('')
        self.textedit_uart.setPlainText('')
        self.topinfo.setPlainText('')
        self.dict_testitem_to_tree = None


        # 限制一次只能拉一个档案, 输出file_info_dict
        print(len(files))
        print(files[0])
        if len(files) == 1:
            self.file_info_dict = Find_LogPath_StationName(files)

            # 給highlight用
            global file_info_dict
            file_info_dict = self.file_info_dict


        # 如果有特殊情况写在’message’里, 没状况正常运行
        if self.file_info_dict['message'] == None:
            self.dict_testitem_to_tree = classify_station_and_find_testitems(self.file_info_dict)
        else:
            self.topinfo.setPlainText(self.file_info_dict['message'])


        # 做tree
        if self.dict_testitem_to_tree:
            temp_list = []

            for index,temp_dict in self.dict_testitem_to_tree.items():
                time_duration = str(temp_dict['time_duration'])


                if temp_dict['sub_test_name'] != None:
                    item = QTreeWidgetItem([index,temp_dict['test_name'],temp_dict['sub_test_name'],time_duration])
                else:
                    item = QTreeWidgetItem([index,temp_dict['test_name'],'NA',time_duration])
                temp_list.append(item)

                if temp_dict['pass_fail'] == 'pass':
                    pass
                elif temp_dict['pass_fail'] == None:
                    for column in range(1,self.tree.columnCount()):
                        item.setBackground(column,QColor(168,168,255))
                elif temp_dict['pass_fail'] == 'fail':
                    for column in range(1,self.tree.columnCount()):
                        item.setBackground(column,QColor(255,168,168))
                elif temp_dict['pass_fail'] == 'oneline':
                    item.setBackground(0,QColor(255,168,168))
                elif temp_dict['pass_fail'] == 'multi-':
                    item.setBackground(2,QColor(166,166,166))
                else:
                    item.setBackground(0,QColor(255,168,168))

                if temp_dict['records_fail']:
                    item.setBackground(0, QColor(188,88,88))

            self.tree.insertTopLevelItems(0,temp_list)


        # 显示station info, 显示在UI上面栏
        station_info = ''
        if self.file_info_dict['station']:
            station_info  = 'Log path(device): ' + self.file_info_dict['device']
            station_info += '\n'+'Station name    : ' + self.file_info_dict['station']
            station_info += '\n'+'Station version : ' + self.file_info_dict['version']

            if self.file_info_dict['sn']    != 'None':
                station_info += '\n'+'SrNm                 : ' + self.file_info_dict['sn']
            if self.file_info_dict['mlb']   != 'None':
                station_info += '\n'+'MLB#                 : ' + self.file_info_dict['mlb']
            if self.file_info_dict['bundle']!= 'None':
                station_info += '\n'+'bundle               : ' + self.file_info_dict['bundle']
            if self.file_info_dict['ECID']  != 'None':
                station_info += '\n'+'ECID                  : ' + self.file_info_dict['ECID']

            self.topinfo.setPlainText(station_info)

        # 显示other info, 目前只有Qt0有做
        if self.file_info_dict['message_device']:
            device_info = ''
            for k,v in self.file_info_dict['message_device'].items():
                if len(k) >= 8:
                    device_info += k.upper()+'\t: '+v+'\n'
                else:
                    device_info += k.upper()+'\t\t: '+v+'\n'
            self.textedit_device.setPlainText(device_info)

        # 档案不符在UI上面栏显示资讯,放后面直接覆盖前面任何结果
        if len(files) != 1:
            self.topinfo.setPlainText("Files incorrect, or the station haven't defined.")
            self.tree.clear()
            self.textedit_device.setPlainText('')
            self.textedit_uart.setPlainText('')

        # print, 方便找资讯
        for k,v in self.dict_testitem_to_tree.items():
            print(k)
            print(v)

    # 介面初始化
    def init_ui(self):

        self.setWindowTitle("Log Reader")

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(['Index','Test name','sub Testname','Times'])


        self.textedit_device = QPlainTextEdit()
        self.textedit_device.setPlainText('device log')


        self.textedit_uart = QPlainTextEdit()
        self.textedit_uart.setPlainText('UART log')


        self.topinfo = QPlainTextEdit()
        UI_information = call_text('UI_information')
        self.topinfo.setPlainText(UI_information)

        self.hbox = QHBoxLayout()

        self.splitter_textedit = QSplitter(Qt.Orientation.Vertical)
        self.splitter_textedit.addWidget(self.textedit_device)
        self.splitter_textedit.addWidget(self.textedit_uart)


        self.topleft = QSplitter(Qt.Orientation.Horizontal)
        self.topleft.addWidget(self.tree)


        self.splitter_bottom = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_bottom.addWidget(self.topleft)
        self.splitter_bottom.addWidget(self.splitter_textedit)
        self.splitter_bottom.setSizes([300,800])


        self.splitter_total = QSplitter(Qt.Orientation.Vertical)
        self.splitter_total.addWidget(self.topinfo)
        self.splitter_total.addWidget(self.splitter_bottom)
        self.splitter_total.setSizes([120,800])


        self.setGeometry(100, 100, 1500, 800)
        self.hbox.addWidget(self.splitter_total)
        self.setLayout(self.hbox)



# highlight做两项
# (1) station keyword, 在call_keyword_dict()里面. 
# (2) UART keyword, 抓该段UART log所有字, 分read / write, 在Find_uart_keywords()
# 细节应该比我熟 :-)
class MyHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.keyword_UART_cmd = Find_uart_keywords(uart_log_section_for_highlight)
        self.keyword_UART_cmd_w,self.keyword_UART_cmd_r = Find_uart_keywords(uart_log_section_for_highlight)

        self.keyword_station = call_keyword_dict(file_info_dict['station'])
        # print('-'*88)
        # print(self.keyword_station)
        # print(self.keyword_UART_cmd_w)
        # print(self.keyword_UART_cmd_r)




        self.iCounter = 0  #用于计数当前是哪一行

        # 1: 时间信息,无需关键字，直接定义正则表达式

        # 2: 定义段落标题类文字，大字体
        # self.keywords2 = ['Build Info', 'Device info','post-write.*:(.*)']
        # self.keywords2 =    []

        # self.keywords2_ =    []

        # 3: 定义信息类文字 待提取
        # self.keywords3 = ["caesiumCPort0DOWN", "caesiumCPort0UP", "InterActiveUI", "titaniumCPort0DOWN", "titaniumCPort1UP","titaniumCPort1DOWN","caesiumCPort1UP","caesiumCPort1DOWN","titaniumCPort0UP",
        #                   "model-name","model-identifier","vendor","platform-board-id", "board-revision","mboot-configuration","chip-id","chip-version","ecid"]

        #self.keywords3 =    [,'Mask violation','results = {.*']
        # self.keywords3 =    []






        # 每行开头的时间格式
        self.keyword_format1 = QTextCharFormat()
        self.keyword_format1.setForeground(QColor("#148385"))

        # 段落标题 Build Info
        self.keyword_format2 = QTextCharFormat()
        # self.keyword_format2.setForeground(QColor("#33aa00"))
        # font = QFont("Comic Sans MS", 11)
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format2.setFont(font)

        #定义信息类文字
        self.keyword_format3 = QTextCharFormat()
        self.keyword_format3.setForeground(QColor("#FF6666"))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format3.setFont(font)


        self.keyword_format_UART_cmd = QTextCharFormat()
        self.keyword_format_UART_cmd.setForeground(QColor("#66DDDD"))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_UART_cmd.setFont(font)

        
        color = {'r':"#FF0000"
                ,'g':"#00CC00"
                ,'b':"#0000FF"
                ,'o':"#FF6633"
                ,'p':"#BB6FBB"
                }
        self.keyword_format_r = QTextCharFormat()
        self.keyword_format_r.setForeground(QColor(color['r']))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_r.setFont(font)

        self.keyword_format_g = QTextCharFormat()
        self.keyword_format_g.setForeground(QColor(color['g']))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_g.setFont(font)

        self.keyword_format_b = QTextCharFormat()
        self.keyword_format_b.setForeground(QColor(color['b']))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_b.setFont(font)

        self.keyword_format_o = QTextCharFormat()
        self.keyword_format_o.setForeground(QColor(color['o']))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_o.setFont(font)

        self.keyword_format_p = QTextCharFormat()
        self.keyword_format_p.setForeground(QColor(color['p']))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format_p.setFont(font)

        self.keyword_format_dict = {'r':self.keyword_format_r
                                    ,'g':self.keyword_format_g
                                    ,'b':self.keyword_format_b
                                    ,'o':self.keyword_format_o
                                    ,'p':self.keyword_format_p
                                    }





        # 定义正则表达式, 每行开头的时间
        self.highlighting_rules1 = [(re.compile(r"^\[(.*?)\]"), self.keyword_format1)]  #问号表示非贪婪模式

        # 定义正则表达式, 仅仅简单替换关键字
        # self.highlighting_rules2 = [(re.compile("{}".format(keyword)), self.keyword_format2)
        #                             for keyword in self.keywords2]
        # self.highlighting_rules2_ = [(re.compile("{}".format(keyword)), self.keyword_format2)
        #                             for keyword in self.keywords2_]
        # print(self.highlighting_rules2)
        # 定义正则表达式
        # self.highlighting_rules3 = [(re.compile("{}".format(keyword)), self.keyword_format3)
        #                             for keyword in self.keywords3]

        self.highlighting_station = {}
        for k,v in self.keyword_station.items():
            self.highlighting_station[k] = [(re.compile("{}".format(keyword)), self.keyword_format_dict[k]) 
                                            for keyword in self.keyword_station[k]]
        # for k,v in self.highlighting_station.items():
        #     print(k)
        #     print(v)

        # self.highlighting_station = [(re.compile("{}".format(keyword)), self.keyword_format2)
        #                             for keyword in self.keyword_station]

        
        self.highlighting_rules_UART_cmd_r = [(re.compile("{}".format(keyword)), self.keyword_format_UART_cmd)
                                            for keyword in self.keyword_UART_cmd_r]

        self.highlighting_rules_UART_cmd_w = [(re.compile("{}".format(keyword)), self.keyword_format_UART_cmd)
                                            for keyword in self.keyword_UART_cmd_w]

    def highlightBlock(self, text):

        # print('*'*88)

        # for pattern, format in self.highlighting_rules2:
        #     match = pattern.search(text)

        #     while match:
        #         index = match.start()           # start 表示起始位置
        #         length = len(match.group(0))
        #         self.setFormat(index, length, self.keyword_format2)  #Build Info

        #         index_1 = match.start(1)
        #         length_1 = len(match.group(1))
        #         self.setFormat(index_1, length_1, self.keyword_format3)

        #         match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了


        # for pattern, format in self.highlighting_rules2_:
        #     match = pattern.search(text)

        #     while match:
        #         index = match.start()
        #         length = len(match.group(0))
        #         self.setFormat(index, length, self.keyword_format2)

        #         index_1 = match.start(1)
        #         length_1 = len(match.group(1))
        #         self.setFormat(index_1, length_1, self.keyword_format3)

        #         index_2 = match.start(2)
        #         length_2 = len(match.group(2))
        #         self.setFormat(index_2, length_2, self.keyword_format3)

        #         match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了

        for k,v in self.highlighting_station.items():
            for pattern, format in v:
                # print(text)
                # print(pattern)
                match = pattern.search(text)

                while match:
                    index = match.start()
                    length = len(match.group(0))
                    self.setFormat(index, length, format)

                    match = pattern.search(text, pos=index + length)

                    # if match.group(1):
                    #     index_1 = match.start(1)
                    #     length_1 = len(match.group(1))
                    #     self.setFormat(index_1, length_1, self.keyword_format3)

                    #     match = pattern.search(text, pos=index + length)
        



        


        for pattern, format in self.highlighting_rules_UART_cmd_r:
            match = pattern.search(text)
            # print(pattern,'\t',text)
            while match:
                index = match.start()
                length = len(match.group(0))
                self.setFormat(index, length, self.keyword_format_UART_cmd)  #Build Info
                match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了
                #SI.log(f"Win_SyntaxText_Log: {text} " )

        for pattern, format in self.highlighting_rules_UART_cmd_w:
            match = pattern.search(text)
            # print(pattern,'\t',text)
            while match:
                index = match.start()
                length = len(match.group(0))
                self.setFormat(index, length, self.keyword_format_UART_cmd)  #Build Info
                match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了
                #SI.log(f"Win_SyntaxText_Log: {text} " )


        # for pattern, format in self.highlighting_rules3:
        #     match = pattern.search(text)
        #     while match:
        #         index = match.start()
        #         length = len(match.group(0))
        #         self.setFormat(index, length, self.keyword_format3)  #Build Info
        #         match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了
        #         #SI.log(f"Win_SyntaxText_Log: {text} " )













        #这段特别放到最后，确保每行开头都能被着色，哪怕是Checkpoint所在行
        for pattern, format in self.highlighting_rules1:
            match = pattern.search(text)
            while match:
                index = match.start()
                length = len(match.group(0))
                self.setFormat(index, length, self.keyword_format1)  #  [14:20:14.3109] entering ramrod_clear_ap_nonce
                match = 0  # 这里必须强制退出, 否则卡死在循环里了

        self.setCurrentBlockState(0)

        self.iCounter = self.iCounter+1


# 这个没用到, 方便看code
class MyHighlighter_reserve(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.iCounter = 0  #用于计数当前是哪一行

        # 1: 时间信息,无需关键字，直接定义正则表达式

        # 2: 定义段落标题类文字，大字体
        # self.keywords2 = ['Build Info', 'Device info','post-write.*:(.*)']
        self.keywords2 =    ['<post-write.*:(.*)'
                            ,'\[Test \w*?\] ?\[.*?\] ?\[\] ?\[(.*?)\]'
                            ,'\[Send:\] func:fSendCommand cmd:(.*?) additional.*'
                            ,'\[ParameterName\] => ?(.*)'
                            ,'\[lowerLimit\] => ?(.*)'
                            ,'\[units\] => ?(.*)'
                            ,'\[upperLimit\] => ?(.*)'
                            ,'checking numeric limits......: ?(.*)'
                            ,'\[(\w*)\] ###### (Test started|Test Done) ######'
                            ,'###.*(false|true).*'
                            ,'append data with key:\W*(\w*)'
                            ,'value:\W*([\w.-]*)'
                            ,'command to send : (.*)'
                            ]

        # 3: 定义信息类文字 待提取
        # self.keywords3 = ["caesiumCPort0DOWN", "caesiumCPort0UP", "InterActiveUI", "titaniumCPort0DOWN", "titaniumCPort1UP","titaniumCPort1DOWN","caesiumCPort1UP","caesiumCPort1DOWN","titaniumCPort0UP",
        #                   "model-name","model-identifier","vendor","platform-board-id", "board-revision","mboot-configuration","chip-id","chip-version","ecid"]

        self.keywords3 =    ['Test Fail'
                            ,'Test Start'
                            ,'Test Pass'
                            ,'\[CmdResult:\] ERROR'
                            ,'Mask violation'
                            ,'results = {.*'
                            ]



        # # 4: 定义FW升级步骤关键字
        # self.keywords4 = ["### Setup Test Begin ###", "### Setup Test Finish:true ###"
        #                    ]

        # # 5: 定义普通着色的关键字
        # self.keywords5 = ['### Run Test Begin ###', '### Run Test Finish:true ###', '### Limit Check Begin ###', '### Limit Check Finish:true ###', '### Teardown Test Begin ###','### Teardown Test Finish:true ###'
        #                   ]

        # # 6: 定义特殊的关键字， 整行修改背景色的
        # self.keywords6 = ['Test started', '###### Test Done ######']




        # 每行开头的时间格式
        self.keyword_format1 = QTextCharFormat()
        self.keyword_format1.setForeground(QColor("#148385"))

        # 段落标题 Build Info
        self.keyword_format2 = QTextCharFormat()
        # self.keyword_format2.setForeground(QColor("#33aa00"))
        # font = QFont("Comic Sans MS", 11)
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format2.setFont(font)

        #定义信息类文字
        self.keyword_format3 = QTextCharFormat()
        self.keyword_format3.setForeground(QColor("#FF6666"))
        font = QFont()
        font.setBold(True)  # 设置粗体字
        #font.setPointSize(8)  # 设置字号
        self.keyword_format3.setFont(font)




        # 定义正则表达式, 每行开头的时间
        self.highlighting_rules1 = [(re.compile(r"^\[(.*?)\]"), self.keyword_format1)]  #问号表示非贪婪模式

        # 定义正则表达式, 仅仅简单替换关键字
        self.highlighting_rules2 = [(re.compile("{}".format(keyword)), self.keyword_format2)
                                    for keyword in self.keywords2]
        # print(self.highlighting_rules2)
        # 定义正则表达式
        self.highlighting_rules3 = [(re.compile("{}".format(keyword)), self.keyword_format3)
                                    for keyword in self.keywords3]
        # # 定义正则表达式
        # self.highlighting_rules4 = [(re.compile("\\b{}\\b".format(keyword)), self.keyword_format4)
        #                             for keyword in self.keywords4]
        # # 定义正则表达式
        # self.highlighting_rules5 = [(re.compile("\\b{}\\b".format(keyword)), self.keyword_format5)
        #                             for keyword in self.keywords5]
        # # 定义正则表达式
        # self.highlighting_rules6 = [(re.compile("\\b{}\\b".format(keyword)), self.keyword_format6)
        #                             for keyword in self.keywords6]




    def highlightBlock(self, text):

        # print('*'*88)

        for pattern, format in self.highlighting_rules2:
            match = pattern.search(text)
            # print(pattern)
            # print(match)

            while match:
                # print(text)
                # print(pattern)
                # print(match)
                index = match.start()           # start 表示起始位置
                length = len(match.group(0))
                # print(index,length)
                self.setFormat(index, length, self.keyword_format2)  #Build Info
                # print('$'*66)
                # print(match.group(0))
                # print(match.group(1))
                # print(match.start(0))
                # print(match.start(1))
                index_1 = match.start(1)
                length_1 = len(match.group(1))
                self.setFormat(index_1, length_1, self.keyword_format3)


                # if match.group(1):
                #     compile_temp = re.compile(match.group(1))
                #     # keyword_match_group1 = re.search(match.group(1),text)
                #     keyword_match_group1 = compile_temp.search(text)
                #     index_1 = keyword_match_group1.start()
                #     length_1 = len(keyword_match_group1.group(0))
                #     self.setFormat(index_1, length_1, self.keyword_format3)

                #     print(match.group(1))
                #     print(re.search(match.group(1),text))
                #     print(keyword_match_group1)



                match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了



        for pattern, format in self.highlighting_rules3:
            match = pattern.search(text)
            while match:
                index = match.start()
                length = len(match.group(0))
                self.setFormat(index, length, self.keyword_format3)  #Build Info
                match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了
                #SI.log(f"Win_SyntaxText_Log: {text} " )

        # for pattern, format in self.highlighting_rules4:
        #     match = pattern.search(text)
        #     while match:
        #         index = match.start()
        #         length = len(match.group(0))
        #         self.setFormat(index, length, self.keyword_format4)  #Build Info
        #         match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了

        # for pattern, format in self.highlighting_rules5:
        #     match = pattern.search(text)
        #     while match:
        #         index = match.start()
        #         length = len(match.group(0))
        #         self.setFormat(index, length, format)
        #         match = pattern.search(text, pos=index + length)#一行如果只有一个关键字，则本句执行一次后就index=-1了

        # for pattern, format in self.highlighting_rules6:
        #     match = pattern.search(text)
        #     if match:
        #         self.setFormat(0, len(text), self.keyword_format6a)
        #         while match:
        #             index = match.start()
        #             length = len(match.group(0))
        #             self.setFormat(index, length, format)
        #             match = pattern.search(text, pos=index + length)  # 一行如果只有一个关键字，则本句执行一次后就index=-1了

        #这段特别放到最后，确保每行开头都能被着色，哪怕是Checkpoint所在行
        for pattern, format in self.highlighting_rules1:
            match = pattern.search(text)
            while match:
                index = match.start()
                length = len(match.group(0))
                self.setFormat(index, length, self.keyword_format1)  #  [14:20:14.3109] entering ramrod_clear_ap_nonce
                match = 0  # 这里必须强制退出, 否则卡死在循环里了

        self.setCurrentBlockState(0)

        self.iCounter = self.iCounter+1


        # print("index: {:.5f} ".format(self.iCounter), text)



if __name__ == '__main__':
    app = QApplication([])
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec()








