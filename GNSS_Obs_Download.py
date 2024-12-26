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
thread_num = 8
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    data_save = "/Users/hanjunjie/Gap1/Data"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    data_save = "/data02/hanjunjie/Data_ZWD"
import download_data_product as dl
CDDIS = "https://cddis.nasa.gov/archive"
WHU = "ftp://igs.gnsswhu.cn/pub"
EPN = "ftp://ftp.epncb.oma.be/pub"
HK = "https://rinex.geodetic.gov.hk/rinex3/"
cur_time = datetime.utcnow()
log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)


year = sys.argv[1]
doy = sys.argv[2]
count = sys.argv[3]
site_list = sys.argv[4].split("_")
if len(sys.argv) > 5:
    data_centre = sys.argv[5].upper()
else:
    data_centre = "J.J.Han"


count_int,doy_int,year_int = int(count),int(doy),int(year)

#Find the short site name and long site name
file = open('./sys_file/LongName_BLH_XYZ.csv','r',encoding='utf8')
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
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS","{:0>3}".format(doy_int))
    LH.mkdir(save_dir)
    for cur_site_short in site_list:
        logging.info("START Obs Site = {}-{}, Year ={:0>4} , Doy = {:0>3}".format(cur_site_short,site_dict_short_long[cur_site_short],year_int,doy_int))
        
        if data_centre == "EPN":
            dl.download_obs_file_EPN(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
        elif data_centre == "HK":
            dl.download_obs_file_HK(data_save,HK,year_int,doy_int,cur_site_short)
        elif data_centre == "CDDIS":
            dl.download_obs_file_CDDIS(data_save,CDDIS,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
        else:
            logging.warning("{} is not support".format(data_centre))
            is_download = dl.download_obs_file_EPN(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
            if not is_download:
                dl.download_obs_file_CDDIS(data_save,CDDIS,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
            if not is_download:
                is_download = dl.download_obs_file_HK(data_save,HK,year_int,doy_int,cur_site_short)
            if not is_download:
                logging.error("{} FAIL!!! ALL!!!".format(cur_site_short))
    doy_int = doy_int + 1
    count_int = count_int - 1


