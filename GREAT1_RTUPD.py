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
    XML_origin_path = r"/Users/hanjunjie/tools/generate_xml_great/origin_xml/great1-RTUPD.xml"
    work_dir = r"/Users/hanjunjie/Master_3/1-IUGG/UPD_GFZ_CHN_BDS2"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
    XML_origin_path = r"/cache/hanjunjie/Software/Tools/generate_xml_great/origin_xml/great1-RTUPD.xml"
    work_dir = r"/data02/hanjunjie/Project/B-THESIS/UPD_GFZ_CHN_BDS2"
import great2_generate_xml as gen_xml
import Linux_Win_HJJ as Run
PURPOSE = "RTUPD"

##----------Python Log----------##
##----------SET 1----------##
Run.mkdir(os.path.join(work_dir))
software = r"/cache/hanjunjie/Software/GREAT/great1.0_sixtents_231124/build/Bin"
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
area = sys.argv[8]
# site_list_str = "TRO1  VARS"
# HETT  OVE6  ROM2  OST6\
#  OLK2  PYHA  LEK6  METG  LOV6  IRBE\
#  NOR7  SPT7  VAIN  HAS6  RANT  REDZ\
#  LAMA  HELG  GELL  LDB2  GOML  GOET\
#  BRTS  LEIJ  WARE  INVR  ARIS  TLL1\
#  SNEO  WTZZ  AUBG  BUTE  BACA  MIKL\
#  POLV  COMO  EGLT  SWAS  MARS  ZADA\
#  AJAC  SCOA  ACOR  ALME  MMET  ORID\
#  IZMI  NICO  SAVU  SUN6  MNSK  TER2\
#  SMLA  IJMU  DYNG  DEVA  MALL  MAH1\
#  LODZ  ZYWI  AUTN  ENTZ  VILL"
#site list generate
if area == "CHN":
    site_list = ['hkks','hkst','hkws','hkcl','hksl','hknp','hkss','hkmw',\
                 'hkkt','hkoh','hklt','hksc','hktk','t430','hkpc','hklm','M192','WHHN', 
                 'V092','WHJX','K042','H053','W038','H074','H038','N062','WHXZ','K101', 
                 'K110','E033','1012','D018','J003','N068','H068','N047','Y065','U029', 
                 '2KJ1','D002','XGXN','H055','I092','K059','WUH2','T023','N032','S028', 
                 'F094','H035','1140','WHHP','O038','EZEC','X046','N010','D007','A010', 
                 '3026','P053','1022','T044','WHJA','C004','D017','M175','H139','K057', 
                 'N004','N028','SXXA','FYFN','NYNZ','WUDA','WHYJ','CZDZ','YYJK','XXFH', 
                 'WHDS','WHXK','CQKZ','PXAY','WHSP','NCAY','K070']
elif area == "HK":
    site_list = ["HKCL","HKKS","HKKT","HKLM","HKLT","HKMW","HKNP","HKOH","HKPC","HKSC","HKSL","HKSS","HKST","HKTK","HKWS","T430"]
    site_list_new = []
    for cur_site in site_list:
        site_list_new.append(cur_site.lower())
    site_list = site_list_new
else:
    sys.exit()
# site_temp = site.split("_")
# site_temp = site_list_str.split()
# for cur_site in site_temp:
#     if cur_site != "NONE":
#         site_list.append(cur_site)

#Find the short site name and long site name
if (cur_platform == "Darwin"):
    file = open('./sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
else:
    file = open('/cache/hanjunjie/Software/Tools/generate_xml_great/sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_xyz = {}
for cur_dic in site_list_csv:
    for cur_site_short in site_list:
        if cur_site_short.upper() in cur_dic["Name"]:
            site_xyz[cur_site_short] = [float(cur_dic["X"]),float(cur_dic["Y"]),float(cur_dic["Z"])]
for cur_site_short in site_list:
    if cur_site_short not in site_xyz.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short))
        site_xyz[cur_site_short] = [0,0,0]

# SET PATH
if (cur_platform == "Darwin"):
    upd_path = "/cache/hanjunjie/Project/B-IUGG/UPD_Europe_RAW_ALL_30S/UPD_WithoutDCB"
    obs_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/OBS".format(year)
    nav_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/NAV".format(year)
    sp3_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/SP3".format(year)
    clk_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/CLK".format(year)
else:
    upd_path = "/cache/hanjunjie/Project/B-IUGG/UPD_Europe_RAW_ALL_30S/UPD_WithoutDCB"
    obs_path = "/data02/hanjunjie/Data/{:0>4}/OBS".format(year)
    nav_path = "/cache/hanjunjie/Data/{:0>4}/NAV".format(year)
    sp3_path = "/cache/hanjunjie/Data/{:0>4}/SP3".format(year)
    clk_path = "/cache/hanjunjie/Data/{:0>4}/CLK".format(year)

count_int,doy_int,year_int = int(count),int(doy),int(year)
logging.info("##--START ALL--##")
Run.mkdir(os.path.join(work_dir,"UPD_SAVE"))
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
    cur_xml_name = "great-UPD-{:0>4}-{:0>3}-min-{}-sec-{}.xml".format(year_int,doy_int,cur_time.minute,cur_time.second)
    shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
    #Change Gen
    gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),cur_sys,int(sampling),site_list)
    # Change input obs
    gen_xml.change_inputs_obs(cur_xml_name,obs_path,year_int,doy_int,int(hour),int(s_length),site_list)
    # Change input nav
    gen_xml.change_inputs_nav(cur_xml_name,"brdm",nav_path,year_int,doy_int,int(hour),int(s_length))
    # Change input sp3clk
    gen_xml.change_inputs_sp3clk(cur_xml_name,"gfz",sp3_path,clk_path,year_int,doy_int,int(hour),int(s_length))
    # Change system file
    gen_xml.change_inputs_sys_great1(cur_xml_name,cur_sys) # Not Complete
    #Change receiver
    gen_xml.set_receiver_parameter(cur_xml_name,site_list,site_xyz)
    logging.info("END Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    logging.info("Start Process {} {:0>4}-{:0>3}".format(PURPOSE,year_int,doy_int))
    ##--------Start the Programe#--------##
    # Run.run_app(software,"great_npp",cur_xml_name,log_dir="./",log_name=PURPOSE+"-app.log")
    if os.path.exists("upd_nl"):
        shutil.copyfile("upd_nl",os.path.join(work_dir,"UPD_BNC","upd_nl_{:0>4}{:0>3}_GEC".format(year_int,doy_int)))
        shutil.copyfile("upd_wl",os.path.join(work_dir,"UPD_BNC","upd_wl_{:0>4}{:0>3}_GEC".format(year_int,doy_int)))
    for cur_site in site_list:
        if os.path.exists("{}_resfile".format(cur_site)):
            os.remove("{}_resfile".format(cur_site))
    if os.path.exists("clkfiletemp_{:0>4}{:0>3}".format(year_int,doy_int)):
        os.remove("clkfiletemp_{:0>4}{:0>3}".format(year_int,doy_int))
    if os.path.exists("WL-res"):
        os.remove("WL-res")
    # if os.path.exists("upd"):
    #     shutil.rmtree("upd")
    doy_int = doy_int + 1
    count_int = count_int - 1

logging.info("##--NORMAL END--##")
