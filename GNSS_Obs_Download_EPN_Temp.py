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
data_centre = sys.argv[4].upper()
site_list = sys.argv[5].split("_")
#UPD_EPN
site_list = "TRO1  VARS  HETT  OVE6  ROM2  OST6\
 OLK2  PYHA  LEK6  METG  LOV6  IRBE\
 NOR7  SPT7  VAIN  HAS6  RANT  REDZ\
 LAMA  HELG  GELL  LDB2  GOML  GOET\
 BRTS  LEIJ  WARE  INVR  ARIS  TLL1\
 SNEO  WTZZ  AUBG  BUTE  BACA  MIKL\
 POLV  COMO  EGLT  SWAS  MARS  ZADA\
 AJAC  SCOA  ACOR  ALME  MMET  ORID\
 IZMI  NICO  SAVU  SUN6  MNSK  TER2\
 SMLA  IJMU  DYNG  DEVA  MALL  MAH1\
 LODZ  ZYWI  AUTN  ENTZ  VILL"
site_list = site_list + " TERS IJMU KOS1 WSRT DIEP BRUX WARE EIJS TIT2 EUSK DOUR REDU DILL KARL BADH FFMJ KLOP"
#AUG_GER
# site_list = ["TERS","IJMU","DENT","WSRT","KOS1","BRUX","DOUR","WARE","REDU","EIJS","TIT2","EUSK","DILL","DIEP","BADH","KLOP","FFMJ","KARL","HOBU","PTBB","GOET"]
#AUG_EPN1
# site_list = ["PTBB","REDU","KOS1","WSRT","BRUX","TIT2"]
#EPNBIG
# site_list = ["KLOP","BYDG","BUDD","CFRM","BSCN","VIRG","GRAC","VTRB","BSVZ","DUB2","WROC","POZE","UNPG","ENTZ","SAS2","WARE","CLIB","LINZ","PTBB","BUDP","DVCN","TUBO","TERS","MOPI","GARI","TRMI","ISRN","MOP2","BAUT","AXPV","UBEN","DIEP","HOBU","PZA2","AUTN","MSEL","RANT","TRF2","WARN","CAKO","WRLG","KDA2","GOET","LCRA","EUSK","GELL","ZADA","IENG","BOLG","EIJS","SRJV","REDZ","MEDI","AQUI","VEN1","ZIM2","ENZA","HELG","GSR1","RIVO","KARL","KOS1"]
site_list = site_list.split()
count_int,doy_int,year_int = int(count),int(doy),int(year)
#Spain
# site_list = ['ACOR','ALAC','ALBA','ALME','BCLN','BELL','BORR','CACE','CANT','CARG','CASE','CEBR','CEU1','CEUT','COBA','CREU','EBRE','ESCO','HUEL','IBIZ','IZAN','LEON','LLIV','LPAL','MAD2','MADR','MALA','MALL','MAS1','MELI','PASA','RIO1','RIOJ','SALA','SFER','SONS','TAR0','TARI','TERU','TOR1','VALA','VALE','VIGO','VILL','YEBE','ZARA']
site_list = ['WARE']
#Find the short site name and long site name
file = open('./sys_file/EUREF_Permanent_GNSS_Network_NEW.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_dict_short_long = {}
site_list = []
for cur_dic in site_list_csv:
    site_list.append(cur_dic["Name"][0:4])
    site_dict_short_long[cur_dic["Name"][0:4]] = cur_dic["Name"]
for cur_dic1 in site_list_csv:
    for cur_site_short in site_list:
        if cur_site_short in cur_dic1["Name"]:
            site_dict_short_long[cur_site_short] = cur_dic1["Name"]
for cur_site_short in site_list:
    if cur_site_short not in site_dict_short_long.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short))
        site_dict_short_long[cur_site_short] = "{}00XXX".format(cur_site_short.upper())


thread_process = []
for cur_site_short in site_list:
    count_int = 365
    doy_int = 1
    while count_int > 0:
        save_dir = os.path.join(data_save,"{:0>4}".format(year),"OBS_EPN_ALL","{:0>3}".format(doy_int))
        LH.mkdir(save_dir)
        logging.info("START Obs Site = {}-{}, Year ={:0>4} , Doy = {:0>3}".format(cur_site_short,site_dict_short_long[cur_site_short],year_int,doy_int))
        if data_centre == "EPN":
            isdownload = dl.download_obs_file_EPN(data_save,EPN,year_int,doy_int,cur_site_short,site_dict_short_long[cur_site_short])
        if isdownload:
            break
        else:
            doy_int = doy_int + 1
            count_int = count_int - 1

