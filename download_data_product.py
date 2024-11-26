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
    CRX2RNX = "/Users/hanjunjie/tools/RNXCMP_4.1.0_MacOSX10.14_gcc/bin/CRX2RNX"
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
    # cmd = "curl -c .urs_cookies -b .urs_cookies -n -L -u 用户名：密码 {} -O".format(source+"/"+file_name_gz)
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
        if (not os.path.exists(file_name_gz_after_gz)):
            return False
        if (os.path.exists(file_name_gz_after_gz) and file_name != file_name_gz_after_gz):
            os.rename(file_name_gz_after_gz,file_name)
        if (os.path.exists(file_name_gz)):
            os.remove(file_name_gz)
    except OSError:
        logging.error("gzip failed for throw except!!!")
        sys.exit()

def tar(local,file_name_gz,file_name):
    os.chdir(local)
    cmd = "tar -xvf {}".format(file_name_gz)
    try:
        result = subprocess.getstatusoutput(cmd)
    except OSError:
        logging.error("gzip failed for throw except!!!")
        sys.exit()

def crx2rnx(local,file_name_d,file_name):
    os.chdir(local)
    cmd = "{} {}".format(CRX2RNX,file_name_d)
    cmd_antenna = "sed -i 's/.*ANTENNA: DELTA H\/E\/N/        0.0000        0.0000        0.0000                  ANTENNA: DELTA H\/E\/N/1' {}".format(file_name)
    try:
        result = subprocess.getstatusoutput(cmd)
        result = subprocess.getstatusoutput(cmd_antenna)
        if (os.path.exists(file_name_d)):
            os.remove(file_name_d)
    except OSError:
        logging.error("crx2rnx failed for throw except!!!")
        sys.exit()

def crx2rnx_WFY(local,file_name_d,file_name):
    os.chdir(local)
    cmd = "{} {}".format(CRX2RNX,file_name_d)
    # cmd_antenna = "sed -i 's/.*ANTENNA: DELTA H\/E\/N/        0.0000        0.0000        0.0000                  ANTENNA: DELTA H\/E\/N/1' {}".format(file_name)
    try:
        result = subprocess.getstatusoutput(cmd)
        # result = subprocess.getstatusoutput(cmd_antenna)
        if (os.path.exists(file_name_d)):
            os.remove(file_name_d)
    except OSError:
        logging.error("crx2rnx failed for throw except!!!")
        sys.exit()

# Download ZPD File with one site
def download_zpd_file(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX",cur_site_long = "XXXXXXXXX"):
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
            file_name_gz = "IGS0OPSFIN_{:0>4}{:0>3}0000_01D_05M_{}_TRO.TRO.gz".format(year,doy,cur_site_long)
            source_file = source_raw + "/gnss/products/troposphere/zpd/{:0>4}/{:0>3}".format(year,doy)
    
        if (download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)

        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("ZTD for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
        else:
            logging.info("ZTD for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download broadcast ephemeris
def download_nav_file_WHU(data_save = "",source_raw = "",year = 2021,doy = 310,cur_nav = "brdm",download_cur_file = False):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"NAV")
    if download_cur_file:
        save_dir = data_save
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
        if (not download_bool):
            file_name_gz = "brdm{:0>3}0.{:0>2}p.Z".format(doy,yy)
            source_file = source_raw + "/gnss/mgex/daily/rinex3/{:0>4}/{:0>3}/{:0>2}p".format(year,doy,yy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            logging.warning("NAV for {} at {:0>4}-{:0>3} download with long name FAIL".format(cur_nav,year,doy))
        
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("NAV for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_nav,year,doy))
        else:
            logging.info("NAV for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download Obs File from EPN with one site
def download_obs_file_EPN(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX",cur_site_long = "XXXX"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS","{:0>3}".format(doy))
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
            gzip(save_dir,file_name_gz,file_name_d)
            download_bool = True
        #RINEX3 first From Receiver data GO
        if (not download_bool):
            file_name_gz = "{}_R_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data Stream
        if (not download_bool):
            file_name_gz = "{}_S_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name Mixed obs with Stream".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data GO from Stream
        if (not download_bool):
            file_name_gz = "{}_S_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs with Stream".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data Unknown
        if (not download_bool):
            file_name_gz = "{}_U_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name Mixed obs with Unknown".format(cur_site,year,doy))
            download_bool = True
        #RINEX3 first From Receiver data GO from Unknown
        if (not download_bool):
            file_name_gz = "{}_U_{:0>4}{:0>3}0000_01D_30S_GO.crx.gz".format(cur_site_long,year,doy)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            logging.warning("OBS for {} at {:0>4}-{:0>3} download with long name GPS obs with Unknown".format(cur_site,year,doy))
            download_bool = True
        #RINEX2
        if (not download_bool):
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
            logging.info("Obs for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download Obs File from HongKong with one site
def download_obs_file_HK(data_save = "",source_raw = "",year = 2021,doy = 310,cur_site = "XXXX",sample = 30):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS","{:0>3}".format(doy))
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}o".format(cur_site.upper(),doy,yy)
    file_name_d = "{}{:0>3}0.{:2d}d".format(cur_site.upper(),doy,yy)
    site_name_lower = cur_site.lower()
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        # Different time different version of rinex
        #RINEX3 first From Receiver data MO
        file_name_gz = "{}00HKG_R_{:0>4}{:0>3}0000_01D_30S_MO.crx.gz".format(cur_site.upper(),year,doy)
        source_file = source_raw + "/{:0>4}/{:0>3}/{}/{}s".format(year,doy,site_name_lower,sample)
        download_bool = False
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name_d)
            download_bool = True
        if (download_bool and os.path.exists(os.path.join(save_dir,file_name_d))):
            crx2rnx(save_dir,file_name_d,file_name)
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("Obs for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
        else:
            logging.info("Obs for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

def download_obs_file_RTK_WFY_NOAA(data_save = ".",year = 2021,doy = 310,cur_site = "XXXX",cur_site_long = "XXXX"):
    # save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_EPN","{:0>3}".format(doy))
    save_dir = data_save
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}o".format(cur_site.upper(),doy,yy)
    file_name_d = "{}{:0>3}0.{:2d}d".format(cur_site.upper(),doy,yy)
    cddis = "https://cddis.nasa.gov/archive/gnss/data/highrate"
    noaa = "https://geodesy.noaa.gov/corsdata/rinex"
    source_raw = noaa
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        download_bool = False
        # Different time different version of rinex
        # From NOAA
        file_name_gz = "{}{:0>3}0.{:2d}d.gz".format(cur_site.lower(),doy,yy)
        source_file = source_raw + "/{:0>4}/{:0>3}/{}".format(year,doy,cur_site.lower())
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            if (gzip(save_dir,file_name_gz,file_name_d)):
                download_bool = True
        if (download_bool and os.path.exists(os.path.join(save_dir,file_name_d))):
            crx2rnx_WFY(save_dir,file_name_d,file_name)
        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("Obs for {} at {:0>4}-{:0>3} download FAIL!!!".format(cur_site,year,doy))
        else:
            logging.info("Obs for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

def download_obs_file_RTK_WFY_CDDIS(data_save = ".",year = 2021,doy = 310,cur_site = "XXXX",cur_site_long = "XXXX"):
    # save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_EPN","{:0>3}".format(doy))
    save_dir = data_save
    LH.mkdir(save_dir)
    yy = year-2000
    file_name = "{}{:0>3}0.{:2d}o".format(cur_site.upper(),doy,yy)
    file_name_d = "{}{:0>3}0.{:2d}d".format(cur_site.upper(),doy,yy)
    cddis = "https://cddis.nasa.gov/archive/gnss/data/highrate"
    noaa = "https://geodesy.noaa.gov/corsdata/rinex"
    source_raw = noaa
    if (not os.path.exists(os.path.join(save_dir,"gnss"))):
        y_temp,mon,date = doy2ymd((year),(doy))
        weekd = ymd2gpsweekday(int(year),mon,date)
        week = int(weekd/10)
        download_bool = False
        # Different time different version of rinex
        # From CDDIS
        source_raw = cddis
        file_name_gz = "{}_S_{:0>4}{:0>3}0000_01D_01S_MO.crx.tar".format(cur_site_long,year,doy)
        source_file = source_raw + "/{:0>4}/{:0>3}".format(year,doy,cur_site.lower())
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            tar(save_dir,file_name_gz,file_name_d)
            download_bool = True
        # download_bool = True
        # tar(save_dir,file_name_gz,file_name_d)
        os.chdir(os.path.join(".","gnss","data","highrate","{:0>4}".format(year),"{:0>3}".format(doy),"{}d".format(yy)))
        if download_bool:
            for i in range(24):
                os.chdir("{:0>2}".format(i))
                for j in range(4):
                    file_name_gz = "{}_S_{:0>4}{:0>3}{:0>2}{:0>2}_15M_01S_MO.crx.gz".format(cur_site_long,year,doy,i,j*15)
                    file_name_d = "{}{:0>3}{}.{:2d}d".format(cur_site.upper(),doy,j+1,yy)
                    if os.path.exists(os.path.join(save_dir,file_name_gz)):
                        gzip(save_dir,file_name_gz,file_name_d)
                        crx2rnx_WFY(save_dir,file_name_d,file_name)
                os.chdir("..")
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download SP3
def download_sp3_file_WHU(data_save = "",source_raw = "",year = 2021,doy = 310,cur_analysis = "gfz",cur_type = "FIN"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"SP3")
    LH.mkdir(save_dir)
    yy = year-2000
    y_temp,mon,date = doy2ymd((year),(doy))
    weekd = ymd2gpsweekday(int(year),mon,date)
    week = int(weekd/10)
    file_name = "{}{:0>5}.sp3".format(cur_analysis.lower(),weekd)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        if week >= 1962:
            file_name_gz = "{}0MGX{}_{:0>4}{:0>3}0000_01D_05M_ORB.SP3.gz".format(cur_analysis.upper(),cur_type.upper(),year,doy)
            source_file = source_raw + "/gps/products/{:0>4}".format(week)
        else:
            if cur_analysis.lower() == "cod":
                cur_analysis_short = "com"
            elif cur_analysis.lower() == "gfz":
                cur_analysis_short = "gbm"
            file_name_gz = "{}{:0>5}.sp3.Z".format(cur_analysis_short.lower(),weekd)
            source_file = source_raw + "/gps/products/mgex/{:0>4}".format(week)
        download_bool = False
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            download_bool = True
        #Download from mgex
        if (not download_bool):
            source_file = source_raw + "/gps/products/mgex/{:0>4}".format(week)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            download_bool = True

        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("SP3 for {} at {:0>4}-{:0>3} from {} download FAIL!!!".format(file_name_gz,year,doy,source_file))
        else:
            logging.info("SP3 for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))

# Download CLK
def download_clk_file_WHU(data_save = "",source_raw = "",year = 2021,doy = 310,cur_analysis = "gfz",cur_type = "FIN"):
    save_dir = os.path.join(data_save,"{:0>4}".format(year),"CLK")
    LH.mkdir(save_dir)
    yy = year-2000
    y_temp,mon,date = doy2ymd((year),(doy))
    weekd = ymd2gpsweekday(int(year),mon,date)
    week = int(weekd/10)
    file_name = "{}{:0>5}.clk".format(cur_analysis.lower(),weekd)
    if (not os.path.exists(os.path.join(save_dir,file_name))):
        if week >= 1962:
            file_name_gz = "{}0MGX{}_{:0>4}{:0>3}0000_01D_30S_CLK.CLK.gz".format(cur_analysis.upper(),cur_type.upper(),year,doy)
            source_file = source_raw + "/gps/products/{:0>4}".format(week)
        else:
            if cur_analysis.lower() == "cod":
                cur_analysis_short = "com"
            elif cur_analysis.lower() == "gfz":
                cur_analysis_short = "gbm"
            file_name_gz = "{}{:0>5}.clk.Z".format(cur_analysis_short.lower(),weekd)
            source_file = source_raw + "/gps/products/mgex/{:0>4}".format(week)
        download_bool = False
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            download_bool = True
        #Download from mgex
        if (not download_bool):
            source_file = source_raw + "/gps/products/mgex/{:0>4}".format(week)
        if (not download_bool and download(source_file,file_name_gz,save_dir)):
            gzip(save_dir,file_name_gz,file_name)
            download_bool = True

        if (not os.path.exists(os.path.join(save_dir,file_name))):
            logging.error("CLK for {} at {:0>4}-{:0>3} from {} download FAIL!!!".format(file_name_gz,year,doy,source_file))
        else:
            logging.info("CLK for {} at {:0>4}-{:0>3} download from {}".format(file_name_gz,year,doy,source_file))
    else:
        logging.warn("This File {} exits!!!".format(file_name))