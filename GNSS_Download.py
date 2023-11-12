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
cur_time = datetime.utcnow()
log_path = os.path.join(data_save,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format("DOWNLOAD",cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)

year = sys.argv[1]
doy = sys.argv[2]
count = sys.argv[3]
download_mode = sys.argv[4].split("_")
if "ZTD" in download_mode or "OBS" in download_mode:
    site_list = sys.argv[5].split("_")

count_int,doy_int,year_int = int(count),int(doy),int(year)
while count_int > 0:
    if "ZTD" in download_mode:
        for cur_site in site_list:
            dl.download_zpd_file(data_save,CDDIS,year_int,doy_int,cur_site)
    doy_int = doy_int + 1
    count_int = count_int - 1


