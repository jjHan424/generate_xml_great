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
if cur_platform == "Windows":
    data_save = r"E:\PhD_1"
elif (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    data_save = "/Users/hanjunjie/Gap1/Data"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    data_save = "/D6/junjie/Data"
import download_data_product as dl
CDDIS = "https://cddis.nasa.gov/archive"
WHU = "ftp://igs.gnsswhu.cn/pub"
EPN = "ftp://ftp.epncb.oma.be/pub"
HK = "https://rinex.geodetic.gov.hk/rinex3/"
RENAGFRA = "https://renag.resif.fr/pub"
cur_time = datetime.utcnow()
log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
if cur_platform == "Windows":
    log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}{:0>2d}{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)


year = sys.argv[1]
doy = sys.argv[2]
count = sys.argv[3]
site_list = sys.argv[4].split("_")
data_centre = "J.J.Han"
sample = 30
if len(sys.argv) > 5:
    data_centre = sys.argv[5].upper()
if data_centre == "HK" or data_centre == "RENAGFRA":
    if len(sys.argv) > 6:
        sample = int(sys.argv[6])
    else:
        sample = 30
    if len(sys.argv) > 7:
        start_hour = int(sys.argv[7])
    else:
        start_hour = 0
    if len(sys.argv) > 8:
        end_hour = int(sys.argv[8])
    else:
        end_hour = 24


count_int,doy_int,year_int = int(count),int(doy),int(year)

#Find the short site name and long site name
file = open('./sys_file/LongName_BLH_XYZ.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_dict_short_long = {}
for cur_dic in site_list_csv:
    for cur_site_short in site_list:
        if cur_site_short[0:4] in cur_dic["Name"]:
            site_dict_short_long[cur_site_short[0:4]] = cur_dic["Name"]
for cur_site_short in site_list:
    if cur_site_short not in site_dict_short_long.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short[0:4]))
        site_dict_short_long[cur_site_short[0:4]] = "{}00XXX".format(cur_site_short[0:4].upper())


thread_process = []
while count_int > 0:
    # save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_HK_{:0>2}S".format(sample),"{:0>3}".format(doy_int))
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_{:0>2}S".format(sample),"{:0>3}".format(doy_int))
    LH.mkdir(save_dir)
    for cur_site_short_raw in site_list:
        cur_site_short = cur_site_short_raw[0:4]
        logging.info("START Obs Site = {}-{}, Year ={:0>4} , Doy = {:0>3}".format(cur_site_short,site_dict_short_long[cur_site_short],year_int,doy_int))
        if data_centre == "EPN":
            dl.download_obs_file_EPN(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
        elif data_centre == "HK":
            if sample == 30:
                dl.download_obs_file_HK(data_save,HK,year_int,doy_int,cur_site_short)
            elif sample == 5 or sample == 1:
                dl.download_obs_file_HK_5S(data_save,HK,year_int,doy_int,cur_site_short,sample,start_hour,end_hour)
        elif data_centre == "CDDIS":
            dl.download_obs_file_CDDIS(data_save,CDDIS,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short],save_dir)
        elif data_centre == "RENAGFRA":
            if sample == 30:
                dl.download_obs_file_RENAGFRA(data_save,RENAGFRA,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short],save_dir)
            elif sample == 1:
                dl.download_obs_file_RENAGFRA_1S(data_save,RENAGFRA,year_int,doy_int,cur_site_short,sample,start_hour,end_hour)
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


