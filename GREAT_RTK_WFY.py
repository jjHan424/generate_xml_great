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
from PodItera_Batch import ymd2doy
import csv
import subprocess
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
    # XML_origin_path = r"/Users/hanjunjie/tools/generate_xml_great/origin_xml/great2-PPPRTK-ZTD.xml"
    work_dir = r"/Users/hanjunjie/Master_3/LX/train_temp"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great") #需要根据自己改路径
    # XML_origin_path = r"/cache/hanjunjie/Software/Tools/generate_xml_great/origin_xml/great2-PPPRTK-ZTD.xml"
    work_dir = r"/Users/hanjunjie/Master_3/LX/train_temp"
import great2_generate_xml as gen_xml
import Linux_Win_HJJ as Run
import download_data_product as dl
WHU = "ftp://igs.gnsswhu.cn/pub"
software = r"/cache/hanjunjie/Software/GREAT/great2.1_grid240126/build_Linux/Bin"
PURPOSE = "GREAT_RTK"
work_dir = sys.argv[1]
origin_xml = sys.argv[2]
# hour = sys.argv[3]
# s_length = sys.argv[4]
base_site = sys.argv[3]
# rover_site = sys.argv[4]
site_list = []
site_list.append(base_site)
# site_list.append(rover_site)
file_list = os.listdir(work_dir)
cur_xml_name = "GREAT_RTK.xml"
# base_site_list = ["ARWD","P222","STFU","SLAC"]
base_site_list = ["STFU"]
PHONES = ['pixel4', 'pixel4xl', 'pixel5', 'pixel6pro', 'pixel7pro',
          'mi8', 'xiaomimi8',
          'sm-g988b', 'sm-s908b', 'sm-a325f', 'sm-a505u', 'sm-a205u',
          'samsunga325g', 'samsunga32']

file = open('./sys_file/EUREF_Permanent_GNSS_Network.csv','r',encoding='utf8')
site_list_csv = csv.DictReader(file)
site_dict_short_long = {}
for cur_dic in site_list_csv:
    for cur_site_short in base_site_list:
        if cur_site_short in cur_dic["Name"]:
            site_dict_short_long[cur_site_short] = cur_dic["Name"]
for cur_site_short in base_site_list:
    if cur_site_short not in site_dict_short_long.keys():
        logging.error("There is no long name for {}!!!".format(cur_site_short))
        site_dict_short_long[cur_site_short] = "{}00XXX".format(cur_site_short.upper())

for cur_file in file_list:
    file_value = cur_file.split("-")
    if len(file_value) < 3:
        continue
    process_dir = os.path.join(work_dir,cur_file)
    year_int = int(file_value[0])
    mon_int = int(file_value[1])
    day_int = int(file_value[2])
    os.chdir(process_dir)
    shutil.copy(origin_xml,cur_xml_name)
    doy_int = ymd2doy(year_int,mon_int,day_int)
    ## Download ##
    # NAV #
    dl.download_nav_file_WHU(process_dir,WHU,year_int,doy_int,"BRDM",True)
    # Base OBS #
    for cur_site in base_site_list:
        dl.download_obs_file_RTK_WFY_NOAA(".",year_int,doy_int,cur_site,site_dict_short_long[cur_site])
        # dl.download_obs_file_RTK_WFY_CDDIS(".",year_int,doy_int,cur_site,site_dict_short_long[cur_site])

    # Conver rover obs #
    phone_index = 0
    for cur_phone in PHONES:
        site_list = []
        site_list.append(base_site)
        os.chdir(process_dir)
        if os.path.exists("./{}/supplemental/gnss_log.obs".format(cur_phone)):
            shutil.copy("./{}/supplemental/gnss_log.obs".format(cur_phone),"GR{:0>2}{:0>3}0.{}o".format(phone_index,doy_int,year_int-2000))
            ## 替换 MARKER NAME
            cmd_makername = "sed -i \"\" 's/.*MARKER NAME/GR{:0>2}                                                        MARKER NAME/1' {}".format(phone_index,"GR{:0>2}{:0>3}0.{}o".format(phone_index,doy_int,year_int-2000))
            subprocess.getstatusoutput(cmd_makername)
        else:
            phone_index = phone_index + 1
            continue
        site_list.append("GR{:0>2}".format(phone_index))
        # Start and End Time #
        with open("GR{:0>2}{:0>3}0.{}o".format(phone_index,doy_int,year_int-2000)) as f:
            for line in f:
                if line[0] == ">":
                    value = line.split()
                    hour = int(value[4])
                    break
        with open("GR{:0>2}{:0>3}0.{}o".format(phone_index,doy_int,year_int-2000)) as f:
            for line in reversed(f.readlines()):
                if line[0] == ">":
                    value = line.split()
                    hour_end = int(value[4]) + 1
                    break
        s_length = (hour_end - hour)*3600

        #Change Gen
        gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),"GEC3",1,site_list)
        gen_xml.change_node_subnode_string(cur_xml_name,"gen","rover","GR{:0>2}".format(phone_index))
        gen_xml.change_node_subnode_string(cur_xml_name,"gen","base",base_site)
        # Change input obs
        gen_xml.change_inputs_obs_RTK(cur_xml_name,"",year_int,doy_int,int(hour),int(s_length),site_list)
        if base_site == "STFU":
            gen_xml.change_inputs_obs_RTK_HighRate(cur_xml_name,"",year_int,doy_int,int(hour),int(s_length),[base_site])
        # Change input nav
        gen_xml.change_inputs_nav(cur_xml_name,"brdm","",year_int,doy_int,int(hour),int(s_length))
        # Change outputs
        gen_xml.change_outputs_RTK(cur_xml_name,"Fixed","GEC3",1,0)
        ##--------Start the Programe#--------##
        # Run.run_app(software,"GREAT_PVTFLT",cur_xml_name,log_dir="./",log_name=PURPOSE+"-app.log")
        phone_index = phone_index + 1

