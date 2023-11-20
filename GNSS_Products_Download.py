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
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    data_save = "/Users/hanjunjie/Master_3"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    data_save = "/cache/hanjunjie/Data"
import download_data_product as dl
CDDIS = "https://cddis.nasa.gov/archive"
WHU = "ftp://igs.gnsswhu.cn/pub"
cur_time = datetime.utcnow()
log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)


year = sys.argv[1]
doy = sys.argv[2]
count = sys.argv[3]
download_mode = sys.argv[4].split("_")
data_centre = sys.argv[5]

if "ZTD" in download_mode or "OBS" in download_mode:
    site_list = sys.argv[6].split("_")

count_int,doy_int,year_int = int(count),int(doy),int(year)


while count_int > 0:
    #ZTD
    if "ZTD" in download_mode:
        logging.info("BEGIN ZTD Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        for cur_site in site_list:
            logging.info("START ZTD Site = {}, Year ={:0>4} , Doy = {:0>3}".format(cur_site,year_int,doy_int))
            dl.download_zpd_file(data_save,CDDIS,year_int,doy_int,cur_site)
    logging.info("START NAV Year ={:0>4} , Doy = {:0>3}".format(year_int,doy_int))

    #NAV
    if "NAV" in download_mode:
        logging.info("BEGIN NAV Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "WHU" in data_centre:
            dl.download_nav_file_WHU(data_save,WHU,year_int,doy_int,"BRDM")
        else:
            logging.error("{} is not support".format(data_centre))
    #SP3
    #CLK
    doy_int = doy_int + 1
    count_int = count_int - 1


