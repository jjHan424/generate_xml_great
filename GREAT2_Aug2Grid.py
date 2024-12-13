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
    XML_origin_path = r"/Users/hanjunjie/tools/generate_xml_great/origin_xml/great2-Aug2Grid-NOCRD.xml"
    work_dir = r"/Users/hanjunjie/Gap1/ZWD_Retrieval_PPPRTK/Project"
else:
    sys.path.insert(0,"/data02/hanjunjie/Software/Tools/generate_xml_great")
    XML_origin_path = r"/data02/hanjunjie/Software/Tools/generate_xml_great/origin_xml/great2-Aug2Grid-NOCRD.xml"
    work_dir = r"/data02/hanjunjie/Project/E-ZTD_Retrival/AUG2GRID/FLT"
import great2_generate_xml as gen_xml
import Linux_Win_HJJ as Run
PURPOSE = "AUG2GRID"
if not os.path.exists(work_dir):
    Run.mkdir(work_dir)
##----------Python Log----------##
##----------SET 1----------##
software = r"/data02/hanjunjie/Software/GREAT/great2.1_ZTD241211/build_Linux/Bin"
cur_time = datetime.utcnow()
log_path = os.path.join(work_dir,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format(PURPOSE,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 12:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: year doy hour s_length system sampling count area grid_mode rm_site ck_site\
                  \2021 310 2 79195 GEC3 30 1 EPN_GER ChkSite XXXX_XXXX XXXX_XXXX")
    sys.exit()
#GEN
year = sys.argv[1]
doy = sys.argv[2]
hour = sys.argv[3]
s_length = sys.argv[4]
cur_sys = sys.argv[5]
sampling = sys.argv[6] # "30" or "5"
count = sys.argv[7]
#NPP
area = sys.argv[8]
grid_mode = sys.argv[9]
rm_site = sys.argv[10]
ck_site = sys.argv[11]
#site list generate
rm_site_list,ck_site_list = [],[]
site_temp = rm_site.split("_")
for cur_site in site_temp:
    if cur_site != "NONE":
        rm_site_list.append(cur_site)
site_temp = ck_site.split("_")
for cur_site in site_temp:
    if cur_site != "NONE":
        ck_site_list.append(cur_site)
if grid_mode.upper() == "CHKCROSS":
    ck_site_list = ["CROSS"]


# SET AREA
if area == "EPN1":
    aug_path = "/data02/hanjunjie/Project/E-ZTD_Retrival/AUG/FLT"
    site_list = ['TERS','IJMU','KOS1','WSRT','DIEP','BRUX','WARE','EIJS','TIT2','EUSK','DOUR','REDU','DILL','KARL','BADH','FFMJ','KLOP']
    Mask = "EPN1"
    RefLon,RefLat = 4.0442,53.687
    SpaceLon,SpaceLat = 1,1
    CountLon,CountLat = 6,6
elif area == "EPN2":
    aug_path = "/data02/hanjunjie/Project/E-ZTD_Retrival/AUG/FLT"
    site_list = ["VAE6",'ONSA','SPT0','JON6','BUDP','HAS6']
    Mask = "EPN2"
    RefLon,RefLat = 9.4009,58.7161
    SpaceLon,SpaceLat = 1,1
    CountLon,CountLat = 6,3
elif area == "CHNWH9":
    aug_path = "/cache/hanjunjie/Project/B-IUGG/AUG_EPN_UPD_UC"
    site_list = ["N028","N047","N068","WHDS","WHSP","WHXZ","XGXN","WHYJ","WUDA"]
    Mask = "CHNWH9"
    RefLon,RefLat = 112.91,31.59
    SpaceLon,SpaceLat = 0.5,0.5
    CountLon,CountLat = 5,4
elif area == "CHNHK16":
    aug_path = "/data02/hanjunjie/Project/B-THESIS/AUG"
    site_list = ["HKCL","HKKS","HKKT","HKLM","HKLT","HKMW","HKNP","HKOH","HKPC","HKSC","HKSL","HKSS","HKST","HKTK","HKWS","T430"]
    Mask = "CHNHK16"
    RefLon,RefLat = 113.86,22.58
    SpaceLon,SpaceLat = 0.1,0.1
    CountLon,CountLat = 6,5
else:
    sys.exit()

if (cur_platform == "Darwin"):
    file = open('./sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
else:
    file = open('/data02/hanjunjie/Software/Tools/generate_xml_great/sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_xyz = {}
for cur_dic in site_list_csv:
    for cur_site_short in site_list:
        if cur_site_short in cur_dic["Name"]:
            site_xyz[cur_site_short] = [float(cur_dic["X"]),float(cur_dic["Y"]),float(cur_dic["Z"])]
for cur_site_short in site_list:
    if cur_site_short not in site_xyz.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short))
        site_xyz[cur_site_short] = [0,0,0]

count_int,doy_int,year_int = int(count),int(doy),int(year)
logging.info("##--START ALL--##")
if (cur_platform == "Darwin"):
    obs_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/OBS".format(year)
    nav_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/NAV".format(year)
    sp3_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/SP3".format(year)
    clk_path = "/Users/hanjunjie/Master_3/Data/{:0>4}/CLK".format(year)
else:
    obs_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/OBS".format(year)
    nav_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/NAV".format(year)
    sp3_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/SP3".format(year)
    clk_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/CLK".format(year)

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
    cur_xml_name = "great-Aug2Grid-{}-{:0>4}-{:0>3}-min-{}-sec-{}.xml".format(area,year_int,doy_int,cur_time.minute,cur_time.second)
    shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
    #Change Gen
    gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),cur_sys,int(sampling),site_list)
    #Change ionogrid
    gen_xml.change_ionogrid(cur_xml_name,area,grid_mode,[RefLat,RefLon],[SpaceLat,SpaceLon],[CountLat,CountLon],rm_site_list,ck_site_list)
    #Change input aug
    gen_xml.change_inputs_aug(cur_xml_name,aug_path,year_int,doy_int,int(hour),int(s_length),site_list,cur_sys)
    # Change input nav
    gen_xml.change_inputs_nav(cur_xml_name,"brdm",nav_path,year_int,doy_int,int(hour),int(s_length))
    # Change input sp3clk
    gen_xml.change_inputs_sp3clk(cur_xml_name,"gfz",sp3_path,clk_path,year_int,doy_int,int(hour),int(s_length))
    #Change outputs auggrid
    gen_xml.change_outputs_aug2grid(cur_xml_name,area,rm_site_list,ck_site_list,cur_sys,int(sampling))
    #Change outputs log
    gen_xml.change_outputs_log(cur_xml_name,PURPOSE)
    #Change receiver
    gen_xml.set_receiver_parameter(cur_xml_name,site_list,site_xyz)
    gen_xml.change_node_subnode_string(cur_xml_name,"ionogrid","min_site","5")
    gen_xml.change_node_subnode_string(cur_xml_name,"ionogrid","poly_par_num","4")
    gen_xml.change_node_subnode_string(cur_xml_name,"ionogrid","bias_baseline","500")
    logging.info("END Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    logging.info("Start Process {} {:0>4}-{:0>3}".format(PURPOSE,year_int,doy_int))
    #--------Start the Programe--------#
    if not gen_xml.check_input(cur_xml_name):
        logging.error("Skip {:0>3} due to lack file !!!".format(doy_int))
        doy_int = doy_int + 1
        count_int = count_int - 1
        continue
    # Run.run_app(software,"GREAT_Aug2Grid",cur_xml_name,log_dir="./",log_name=PURPOSE+"-app.log")
    doy_int = doy_int + 1
    count_int = count_int - 1

logging.info("##--NORMAL END--##")
