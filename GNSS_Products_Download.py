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
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    data_save = "/Users/hanjunjie/Gap1/Data"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    data_save = "/D6/junjie/Data"
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
if "SP3" in download_mode or "CLK" in download_mode or "BIA" in download_mode:
    analysis_name = sys.argv[6]
    solution_type = sys.argv[7]

if "ZTD" in download_mode or "OBS" in download_mode:
    site_list = sys.argv[6].split("_")
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

count_int,doy_int,year_int = int(count),int(doy),int(year)


while count_int > 0:
    #ZTD
    if "ZTD" in download_mode:
        logging.info("BEGIN ZTD Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        for cur_site in site_list:
            logging.info("START ZTD Site = {}, Year ={:0>4} , Doy = {:0>3}".format(cur_site,year_int,doy_int))
            dl.download_zpd_file(data_save,CDDIS,year_int,doy_int,cur_site,site_dict_short_long[cur_site])
    logging.info("START Year ={:0>4} , Doy = {:0>3}".format(year_int,doy_int))

    #NAV
    if "NAV" in download_mode:
        logging.info("BEGIN NAV Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "WHU" in data_centre:
            dl.download_nav_file_WHU(data_save,WHU,year_int,doy_int,"BRDM")
        if "CDDIS" in data_centre:
            dl.download_nav_file_CDDIS(data_save,CDDIS,year_int,doy_int,"BRDM")
        else:
            logging.error("{} is not support".format(data_centre))
    #SP3
    if "SP3" in download_mode:
        logging.info("BEGIN SP3 Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "WHU" in data_centre:
            dl.download_sp3_file_WHU(data_save,WHU,year_int,doy_int,analysis_name,solution_type)
        if "CDDIS" in data_centre:
            dl.download_sp3_file_WHU(data_save,CDDIS,year_int,doy_int,analysis_name,solution_type)
        else:
            logging.error("{} is not support".format(data_centre))
    #CLK
    if "CLK" in download_mode:
        logging.info("BEGIN CLK Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "WHU" in data_centre:
            dl.download_clk_file_WHU(data_save,WHU,year_int,doy_int,analysis_name,solution_type)
        if "CDDIS" in data_centre:
            dl.download_clk_file_WHU(data_save,CDDIS,year_int,doy_int,analysis_name,solution_type)
        else:
            logging.error("{} is not support".format(data_centre))
    
    #OSB
    if "OSB" in download_mode:
        logging.info("BEGIN BIA Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "CDDIS" in data_centre:
            dl.download_osb_file(data_save,CDDIS,year_int,doy_int,analysis_name,solution_type)
        else:
            logging.error("{} is not support".format(data_centre))
    
    #DCB
    if "DCB" in download_mode:
        logging.info("BEGIN BIA Year ={:0>4} , Doy = {:0>3} from {}".format(year_int,doy_int,data_centre))
        if "CDDIS" in data_centre:
            dl.download_dcb_file(data_save,CDDIS,year_int,doy_int,analysis_name,solution_type)
        else:
            logging.error("{} is not support".format(data_centre))
    doy_int = doy_int + 1
    count_int = count_int - 1


