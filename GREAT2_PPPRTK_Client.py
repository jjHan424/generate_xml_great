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
    XML_origin_path = r"/Users/hanjunjie/tools/generate_xml_great/origin_xml/great2-PPPRTK-ZTD.xml"
    work_dir = r"/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Project"
else:
    sys.path.insert(0,"/data02/hanjunjie/Software/Tools/generate_xml_great")
    XML_origin_path = r"/data02/hanjunjie/Software/Tools/generate_xml_great/origin_xml/great2-PPPRTK-ZTD.xml"
    work_dir = r"/data02/hanjunjie/Project/E-ZTD_Retrival/ZWD/PPP"
import great2_generate_xml as gen_xml
import Linux_Win_HJJ as Run
PURPOSE = "PPPRTKClient"

##----------Python Log----------##
##----------SET 1----------##
if not os.path.exists(work_dir):
    Run.mkdir(work_dir)
software = r"/data02/hanjunjie/Software/GREAT/great2.1_ZTD241211/build_Linux/Bin"
cur_time = datetime.utcnow()
log_path = os.path.join(work_dir,"{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format(PURPOSE,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 11:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: year doy hour s_length system sampling count site aug_mode reset_par\
                  \2021 310 2 79195 GEC3 30 1 HKSC_HKTK ChkCross 3600")
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
site = sys.argv[8]
aug_mode = sys.argv[9]
amb = sys.argv[10]
reset_par = sys.argv[11]
#site list generate
site_list = []
site_temp = site.split("_")
for cur_site in site_temp:
    if cur_site != "NONE":
        site_list.append(cur_site)
if amb == "YES":
    amb = "FIXED"
else:
    amb = "FLOAT"

# SET PATH
if (cur_platform == "Darwin"):
    upd_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/{:0>4}/UPD".format(year)
    obs_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/{:0>4}/OBS".format(year)
    nav_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/{:0>4}/NAV".format(year)
    sp3_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/{:0>4}/SP3".format(year)
    clk_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/{:0>4}/CLK".format(year)
    aug_path = "/Users/hanjunjie/Gap1/IONO_Accuracy_Predict/Data/AUG"
    grid_path = "/cache/hanjunjie/Project/C-ZTD/Aug2Grid"
else:
    upd_path = "/data02/hanjunjie/Project/E-ZTD_Retrival/UPD/UPD_GFZ_EPN_BDS3/UPD_SAVE"
    obs_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/OBS".format(year)
    nav_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/NAV".format(year)
    sp3_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/SP3".format(year)
    clk_path = "/data02/hanjunjie/Data_ZWD/{:0>4}/CLK".format(year)
    aug_path = "/data02/hanjunjie/Project/C-ZTD/Aug2Grid"
    grid_path = "/data02/hanjunjie/Project/B-THESIS/GRID/NEW"
    roti_path = ""

client_EPN1 = ["ONSA","ONS1","SPT7","SPT0"]
client_EPN2 = ["TLMF","TLSE","EBRE"]
client_EPN_GER = ["REDU","KOS1","WSRT","BRUX","FFMJ"]
client_HK = ["HKLT"]
area = "NONE"

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
    # For Multi Sites
    for cur_site in site_list:
        logging.info("START Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
        #Copy XML File
        cur_xml_name = "great-PPPRTK-{}-{:0>4}-{:0>3}-min-{}-sec-{}.xml".format(cur_site,year_int,doy_int,cur_time.minute,cur_time.second)
        shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
        #Change Gen
        gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),cur_sys,int(sampling),[cur_site])
        gen_xml.change_node_subnode_string(cur_xml_name,"gen","rover",cur_site)
        #Change AMB and Inputs UPD
        if amb == "FIXED":
            gen_xml.change_node_subnode_string(cur_xml_name,"ambiguity","fix_mode","SEARCH")
            gen_xml.change_inputs_upd(cur_xml_name,upd_path,year_int,doy_int,int(hour),int(s_length))
        else:
            gen_xml.change_node_subnode_string(cur_xml_name,"ambiguity","fix_mode","NO")
            gen_xml.change_node_subnode_string(cur_xml_name,"inputs","upd","")
        gen_xml.change_node_subnode_string(cur_xml_name,"ionogrid","wgt_mode",aug_mode)
        # Change input obs
        gen_xml.change_inputs_obs(cur_xml_name,obs_path,year_int,doy_int,int(hour),int(s_length),[cur_site])
        # Change input nav
        gen_xml.change_inputs_nav(cur_xml_name,"brdm",nav_path,year_int,doy_int,int(hour),int(s_length))
        # Change input sp3clk
        gen_xml.change_inputs_sp3clk(cur_xml_name,"gfz",sp3_path,clk_path,year_int,doy_int,int(hour),int(s_length))
        # Change input auggrid
        if cur_site in client_EPN1:
            area = "EPN1"
        elif cur_site in client_EPN2:
            area = "EPN2"
        elif cur_site in client_EPN_GER:
            area = "EPNGER"
        elif cur_site in client_HK:
            area = "CHN_HK"
        # else:
        #     sys.exit()
        if aug_mode != "OFF":
            gen_xml.change_inputs_auggrid(cur_xml_name,grid_path,year_int,doy_int,int(hour),int(s_length),cur_site,area,client_EPN_GER,cur_sys)
        gen_xml.change_node_subnode_string(cur_xml_name,"inputs","aug_grid","")
        # if i > 0:
        #     gen_xml.change_node_subnode_string(cur_xml_name,"inputs","aug_grid","/data02/hanjunjie/Project/B-THESIS/PPPRTK/EPN_GER_AUG/{}{:0>3}/{}.grid".format(year_int,doy_int,i))
        # Change system file
        gen_xml.change_inputs_sys(cur_xml_name,cur_sys) # Not Complete
        #Change outputs auggrid
        # gen_xml.change_outputs_aug(cur_xml_name,"FIXED",cur_sys,int(sampling),int(reset_par))
        gen_xml.change_outputs_client(cur_xml_name,amb,cur_sys,int(sampling),int(reset_par))
        #Change outputs log
        gen_xml.change_outputs_log(cur_xml_name,PURPOSE,"DOY",cur_site,year_int,doy_int)
        #Change filter any
        gen_xml.change_filter_anystring(cur_xml_name,"reset_par",reset_par)
        #Change receiver
        gen_xml.reset_receiver_parameter(cur_xml_name,[cur_site])
        #Change for ZTD out
        gen_xml.change_node_subnode_string(cur_xml_name,"npp","ZTD_OUT","TRUE")
        logging.info("END Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
        logging.info("Start Process {} {:0>4}-{:0>3}".format(PURPOSE,year_int,doy_int))
        ##--------Start the Programe#--------##
        if not gen_xml.check_input(cur_xml_name):
            logging.error("Skip {:0>3} due to lack file !!!".format(doy_int))
            doy_int = doy_int + 1
            count_int = count_int - 1
            continue
        # Run.run_app(software,"GREAT_PPPRTK",cur_xml_name,log_dir="./",log_name=PURPOSE+"-app.log")
    doy_int = doy_int + 1
    count_int = count_int - 1

logging.info("##--NORMAL END--##")
