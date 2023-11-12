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
import Linux_Win_HJJ as LH
from datetime import datetime
# import requests
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
import PodBatch_win as Pod
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday
import subprocess
# cddis = "https://urs.earthdata.nasa.gov"
# cddis = "cddis.gsfc.nasa.gov"
cddis = "ftp.epncb.oma.be"
work_dir = "/Users/hanjunjie/Master_3"

def download(source,file_name_gz,local):
    os.chdir(local)
    cmd = "curl -c .urs_cookies -b .urs_cookies -n -L {} -O".format(source+"/"+file_name_gz)
    try:
        result = subprocess.getstatusoutput(cmd)
        if (os.path.exists(file_name_gz)):
            return True
        else:
            return False
    except OSError:
        logging.error("run failed for throw except.")
        sys.exit()

def gzip(local,file_name_gz):
    os.chdir(local)
    cmd = "gunzip -f {}".format(file_name_gz)
    try:
        result = subprocess.getstatusoutput(cmd)
    except OSError:
        logging.error("run failed for throw except.")
        sys.exit()

def download_zpd_file(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"ZTD","{:0>3}".format(doy))
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}zpd".format(cur_site.lower(),doy,yy)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        if week <= 2237:
            file_name_gz = "{}{:0>3}0.{:0>2}zpd.gz".format(cur_site.lower(),doy,yy)
            source_file = source_raw + "/gnss/products/troposphere/zpd/{:0>4}/{:0>3}".format(year,doy)
        else:
            source_file = source_raw + "/gnss/products/troposphere/zpd/{:0>4}/IGS0OPSFIN_YYYYDDDHHMM_01D)05M_SITENAME_TRO.TRO.gz".format(year,doy,cur_site.lower(),doy,yy)
        if (download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz)
    else:
        logging.warn("This File {} exits!!!".format(file_name))
    # gzip("H","/Users/hanjunjie/Master_3")
