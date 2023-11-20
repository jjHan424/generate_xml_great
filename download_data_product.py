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
    CRX2RNX = "/Users/hanjunjie/tools/CRX2RNX"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    CRX2RNX = "/home/hanjunjie/tools/CRX2RNX"
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
        if (os.path.exists(".urs_cookies")):
            os.remove(".urs_cookies")
        if (os.path.exists(file_name_gz)):
            return True
        else:
            return False
    except OSError:
        logging.error("download failed for throw except!!!")
        sys.exit()

def gzip(local,file_name_gz,file_name):
    os.chdir(local)
    cmd = "gunzip -f {}".format(file_name_gz)
    try:
        result = subprocess.getstatusoutput(cmd)
        file_name_gz_value = file_name_gz.split(".")
        file_name_gz_after_gz = file_name_gz_value[0]+"." + file_name_gz_value[1]
        if (os.path.exists(file_name_gz_after_gz) and file_name != file_name_gz_after_gz):
            os.rename(file_name_gz_after_gz,file_name)
        if (os.path.exists(file_name_gz)):
            os.remove(file_name_gz)
    except OSError:
        logging.error("gzip failed for throw except!!!")
        sys.exit()

def crx2rnx(local,file_name_d,file_name):
    os.chdir(local)
    cmd = "{} {}".format(CRX2RNX,file_name_d)
    try:
        result = subprocess.getstatusoutput(cmd)
        if (os.path.exists(file_name_d)):
            os.remove(file_name_d)
    except OSError:
        logging.error("crx2rnx failed for throw except!!!")
        sys.exit()

# Download ZPD File with one site
def download_zpd_file(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"ZTD","{:0>3}".format(doy))
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}zpd".format(cur_site.lower(),doy,yy)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        # Different time different name
        if week <= 2237:
            file_name_gz = "{}{:0>3}0.{:0>2}zpd.gz".format(cur_site.lower(),doy,yy)
            source_file = source_raw + "/gnss/products/troposphere/zpd/{:0>4}/{:0>3}".format(year,doy)
        else:
            source_file = source_raw + "/gnss/products/troposphere/zpd/{:0>4}/IGS0OPSFIN_YYYYDDDHHMM_01D)05M_SITENAME_TRO.TRO.gz".format(year,doy,cur_site.lower(),doy,yy)
        
        if (download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
        else:
            logging.error("ZTD for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("ZTD for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download broadcast ephemeris
def download_nav_file_WHU(data_save = "",source_raw = "",year = 2021,doy = 310,cur_nav = "brdm"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"NAV")
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}n".format(cur_nav.lower(),doy,yy)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        # Different time different name and location just for WHU igs long name
        file_name_gz = "BRDM00DLR_S_{:0>4}{:0>3}0000_01D_MN.rnx.gz".format(year,doy)
        source_file = source_raw + "/gps/data/daily/{:0>4}/{:0>3}/{:0>2}p".format(year,doy,yy)
        download_bool = False
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
        
        #Short name
        file_name_gz = "brdm{:0>3}0.{:0>2}p.Z".format(doy,yy)
        source_file = source_raw + "/gnss/mgex/daily/rinex3/{:0>4}/{:0>3}/{:0>2}p".format(year,doy,yy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            logging.warning("NAV for {} at {:0>4}-{:0>3} download with long name FAIL".format(cur_nav,year,doy))
        
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("ZTD for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_nav,year,doy))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download ZPD File with one site
def download_obs_file_EPN(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX",cur_site_long = "XXXX"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_EPN","{:0>3}".format(doy))
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}o".format(cur_site.upper(),doy,yy)
    file_name_d = "{}{:0>3}0.{:2d}d".format(cur_site.upper(),doy,yy)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        # Different time different version of rinex
        #RINEX3 first From Receiver data MO
        file_name_gz = "{}_R_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site_long,year,doy)
        source_file = source_raw + "/obs/{:0>4}/{:0>3}".format(year,doy)
        download_bool = False
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            download_bool = True
        #RINEX3 first From Receiver data GO
        file_name_gz = "{}_R_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data Stream
        file_name_gz = "{}_S_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name Mixed obs with Stream".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data GO from Stream
        file_name_gz = "{}_S_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs with Stream".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data Unknown
        file_name_gz = "{}_U_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name Mixed obs with Unknown".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data GO from Unknown
        file_name_gz = "{}_U_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs with Unknown".format(cur_site,year,doy))
            download_bool = True
        #RINEX2
        file_name_gz = "{}{:0>3}0.{:2d}D.Z".format(cur_site.upper(),doy,yy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with short name with rinex2".format(cur_site,year,doy))
            download_bool = True
        if (download_bool and os.path.exists(os.path.join(save_dir,file_name_d))):
            crx2rnx(save_dir,file_name_d,file_name)
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("Obs for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
    else:
        logging.warn("This File {} exits!!!".format(file_name))