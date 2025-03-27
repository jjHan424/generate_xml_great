import os
import shutil
import ftplib
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
import logging
import platform
import csv
from datetime import datetime
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    XML_origin_path = r"/Users/hanjunjie/tools/generate_xml_great/origin_xml/great1-ROTI.xml"
    work_dir = r"/Users/hanjunjie/Gap1/Magnetic_storm/Project"
else:
    sys.path.insert(0,"/data02/hanjunjie/Software/Tools/generate_xml_great_ROTI")
    XML_origin_path = r"/data02/hanjunjie/Software/Tools/generate_xml_great_ROTI/origin_xml/great1-ROTI.xml"
    work_dir = r"/data02/hanjunjie/Project/C-LX/ROTI"
import great2_generate_xml as gen_xml
import Linux_Win_HJJ as Run
PURPOSE = "ROTI"

##----------Python Log----------##
##----------SET 1----------##
Run.mkdir(os.path.join(work_dir))
software = r"/data02/hanjunjie/Software/GREAT/great1.0_ROTI_jdhuang/build/Bin"
cur_time = datetime.utcnow()
log_path = os.path.join(work_dir,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format(PURPOSE,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 9:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: year doy hour s_length system sampling count site amb reset_par\
                  \2021 310 2 79195 GEC3 30 1 HKSC_HKTK YES 3600")
    sys.exit()
#GEN
year = sys.argv[1]
doy = sys.argv[2]
hour = sys.argv[3]
s_length = sys.argv[4]
cur_sys = sys.argv[5]
sampling = sys.argv[6] # "30" or "5"
count = sys.argv[7]
#PPP
site_list_temp = sys.argv[8]

site_list = site_list_temp.split("_")


# SET PATH
if (cur_platform == "Darwin"):
    upd_path = "/cache/hanjunjie/Project/B-IUGG/UPD_Europe_RAW_ALL_30S/UPD_WithoutDCB"
    obs_path = "/Users/hanjunjie/Gap1/Data/{:0>4}/OBS".format(year)
    nav_path = "/Users/hanjunjie/Gap1/Data/{:0>4}/NAV".format(year)
    sp3_path = "/Users/hanjunjie/Gap1/Data/{:0>4}/SP3".format(year)
    clk_path = "/Users/hanjunjie/Gap1/Data/{:0>4}/CLK".format(year)
else:
    upd_path = "/data02/hanjunjie/Project/B-IUGG/UPD_Europe_RAW_ALL_30S/UPD_WithoutDCB"
    obs_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/OBS".format(year)
    nav_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/NAV".format(year)
    sp3_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/SP3".format(year)
    clk_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/CLK".format(year)

count_int,doy_int,year_int = int(count),int(doy),int(year)
logging.info("##--START ALL--##")
while count_int > 0:
    #Check and Make Dir
    os.chdir(work_dir)
    cur_dir = os.path.join(work_dir,"{:0>4}".format(year_int) + "{:0>3}".format(doy_int))
    if os.path.exists(cur_dir):
        logging.warning("This workdir {} is exist".format(cur_dir))
    else:
        os.mkdir(cur_dir)
    os.chdir(cur_dir)
    logging.info("START Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    #Copy XML File
    cur_xml_name = "great-ROTI-{:0>4}-{:0>3}-min-{}-sec-{}.xml".format(year_int,doy_int,cur_time.minute,cur_time.second)
    shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
    Run.mkdir(os.path.join("roti"))
    #Change Gen
    gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),cur_sys,int(sampling),site_list)
    # Change input obs
    gen_xml.change_inputs_obs(cur_xml_name,obs_path,year_int,doy_int,int(hour),int(s_length),site_list)
    # Change input nav
    gen_xml.change_inputs_nav(cur_xml_name,"brdm",nav_path,year_int,doy_int,int(hour),int(s_length))
    #Change receiver
    gen_xml.reset_receiver_parameter(cur_xml_name,site_list)
    logging.info("END Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    logging.info("Start Process {} {:0>4}-{:0>3}".format(PURPOSE,year_int,doy_int))
    ##--------Start the Programe#--------##
    if not gen_xml.check_input(cur_xml_name):
        logging.error("Skip {:0>3} due to lack file !!!".format(doy_int))
        doy_int = doy_int + 1
        count_int = count_int - 1
        continue
    # Run.run_app(software,"great_turboedit",cur_xml_name,log_dir="./",log_name=PURPOSE+"-app.log")
    doy_int = doy_int + 1
    count_int = count_int - 1

logging.info("##--NORMAL END--##")
