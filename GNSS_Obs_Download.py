import os
import ftplib
import shutil
import os
import shutil
import ftplib
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
import logging
import platform
from datetime import datetime
import csv
import threading
import Linux_Win_HJJ as LH
thread_num = 4
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    data_save = "/Users/hanjunjie/Master_3/Data"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    data_save = "/cache/hanjunjie/Data"
import download_data_product as dl
CDDIS = "https://cddis.nasa.gov/archive"
WHU = "ftp://igs.gnsswhu.cn/pub"
EPN = "ftp://ftp.epncb.oma.be/pub"
cur_time = datetime.utcnow()
log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)


year = sys.argv[1]
doy = sys.argv[2]
count = sys.argv[3]
data_centre = sys.argv[4].upper()
site_list = sys.argv[5].split("_")
#UPD_EPN
# site_list = "TRO1  VARS  HETT  OVE6  ROM2  OST6\
#   OLK2  PYHA  LEK6  METG  LOV6  IRBE\
#   NOR7  SPT7  VAIN  HAS6  RANT  REDZ\
#   LAMA  HELG  GELL  LDB2  GOML  GOET\
#   BRTS  LEIJ  WARE  INVR  ARIS  TLL1\
#   SNEO  WTZZ  AUBG  BUTE  BACA  MIKL\
#   POLV  COMO  EGLT  SWAS  MARS  ZADA\
#   AJAC  SCOA  ACOR  ALME  MMET  ORID\
#   IZMI  NICO  SAVU  SUN6  MNSK  TER2\
#   SMLA  IJMU  DYNG  DEVA  MALL  MAH1\
#   LODZ  ZYWI  AUTN  ENTZ  VILL"
#AUG_GER
site_list = ["TERS","IJMU","DENT","WSRT","KOS1","BRUX","DOUR","WARE","REDU","EIJS","TIT2","EUSK","DILL","DIEP","BADH","KLOP","FFMJ","KARL","HOBU","PTBB","GOET"]
# site_list = site_list.split()
count_int,doy_int,year_int = int(count),int(doy),int(year)

#Find the short site name and long site name
file = open('./sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_dict_short_long = {}
for cur_dic in site_list_csv:
    for cur_site_short in site_list:
        if cur_site_short in cur_dic["Name"]:
            site_dict_short_long[cur_site_short] = cur_dic["Name"]
for cur_site_short in site_list:
    if cur_site_short not in site_dict_short_long.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short))
        site_dict_short_long[cur_site_short] = "{}00XXX".format(cur_site_short.upper())


thread_process = []
while count_int > 0:
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_TEMP","{:0>3}".format(doy_int))
    LH.mkdir(save_dir)
    for cur_site_short in site_list:
        logging.info("START Obs Site = {}-{}, Year ={:0>4} , Doy = {:0>3}".format(cur_site_short,site_dict_short_long[cur_site_short],year_int,doy_int))
        if data_centre == "EPN":
            thread_process.append(threading.Thread(target=dl.download_obs_file_EPN,args=(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short]),daemon=False))
            # dl.download_obs_file_EPN(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
        else:
            logging.error("{} is not support".format(data_centre))
    process_num = 0
    thread_start = []
    for cur_thread in thread_process:
        cur_thread.start()
        thread_start.append(cur_thread)
        if len(thread_start) == thread_num:
            for cur_start_thread in thread_start:
                cur_start_thread.join()
            thread_start = []
    doy_int = doy_int + 1
    count_int = count_int - 1


