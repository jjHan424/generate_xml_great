import os
import shutil
import ftplib
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
import logging
import platform
from datetime import datetime
cur_platform = platform.system()
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/generate_xml_great")
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/generate_xml_great")
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday
import Linux_Win_HJJ as run_mkdir



def change_gen_time(xml_file,year,doy,hour,s_length):
    tree = et.parse(xml_file)
    root = tree.getroot()
    gen = root.find("gen")
    #change time
    beg = gen.find("beg")
    end = gen.find("end")
    yyyy,mon,day = doy2ymd(year,doy)
    min = 0
    sec = 0
    beg.text = " {0:04}".format(int(yyyy)) + "-" + "{0:02}".format(int(mon)) + "-" + "{0:02}".format(int(day)) + " " + "{0:02}".format(int(hour)) + ":{0:02}".format(min) + ":{0:02} ".format(sec)
    hour_length = int(s_length / 3600)
    sec_length = s_length - hour_length * 3600
    while (hour_length >= 24):
        doy = doy + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        hour = hour - 24
        doy = doy + 1
    while (sec_length >= 3600):
        hour = hour + 1
        sec_length = sec_length - 3600
    while (sec_length >= 60):
        min = min + 1
        sec_length = sec_length - 60
    sec = sec + sec_length
    yyyy,mon,day = doy2ymd(year,doy)
    end.text = " {0:04}".format(int(yyyy)) + "-" + "{0:02}".format(int(mon)) + "-" + "{0:02}".format(int(day)) + " " + "{0:02}".format(int(hour)) + ":{0:02}".format(min) + ":{0:02} ".format(sec)
    tree.write(xml_file)

#Change XML gen
def change_gen(xmlfile = "great2.1.xml",year = 2021,doy = 310, hour = 0, s_length = 86395, cur_sys = "GEC3", sampling = 30,site_list = ["XXXX","YYYY","ZZZZ"]):
    #Change beg and end
    change_gen_time(xmlfile,year,doy,hour,s_length)
    tree = et.parse(xmlfile)
    root = tree.getroot()
    gen = root.find("gen")
    #Change Sys
    gen_sys = gen.find("sys")
    sys_text = ""
    if ("G" in cur_sys):
        sys_text = "GPS"
    if ("E" in cur_sys):
        sys_text = sys_text + " GAL"
    if ("R" in cur_sys):
        sys_text = sys_text + " GLO"
    if ("C" in cur_sys):
        sys_text = sys_text + " BDS"
    sys_text = " " + sys_text + " "
    gen_sys.text = sys_text
    #Change Sampling
    gen.find("int").text = " {:>2} ".format(sampling)
    #Change Site
    gen_rec = gen.find("rec")
    gen_rec.text = ""
    for cur_site in site_list:
        gen_rec.text = gen_rec.text + " " + cur_site.upper() + " "
    #Change BDS Band for B2 or B3
    if ("C3" in cur_sys):
        root.find("bds").find("band").text = " 2 6 "
    if ("C2" in cur_sys):
        root.find("bds").find("band").text = " 2 7 "
    tree.write(xmlfile)

#Change XML ionogrid
def change_ionogrid(xmlfile = "great2.1.xml",area = "WUHAN",wgt_mode = "GRID",ref_bl = [12,13],space_bl = [0.5,0.5],count_bl = [3,4],rm_site_list = [""],ck_site_list = [""]):
    tree = et.parse(xmlfile)
    ionogrid = tree.getroot().find("ionogrid")
    ionogrid.find("Mask").text = area
    ionogrid.find("wgt_mode").text = wgt_mode
    ionogrid.find("RefLat").text = " {:.2f} ".format(ref_bl[0])
    ionogrid.find("RefLon").text = " {:.2f} ".format(ref_bl[1])
    ionogrid.find("SpaceLat").text = " {:.2f} ".format(space_bl[0])
    ionogrid.find("SpaceLon").text = " {:.2f} ".format(space_bl[1])
    ionogrid.find("CountLat").text = " {:>2d} ".format(count_bl[0])
    ionogrid.find("CountLon").text = " {:>2d} ".format(count_bl[1])
    ionogrid.find("rec_rm").text = ""
    for cur_site in rm_site_list:
        ionogrid.find("rec_rm").text = ionogrid.find("rec_rm").text + " " + cur_site + " "
    ionogrid.find("rec_chk").text = ""
    for cur_site in ck_site_list:
        ionogrid.find("rec_chk").text = ionogrid.find("rec_chk").text + " " + cur_site + " "
    tree.write(xmlfile)

#Change XML inputs aug
def change_inputs_aug(xmlfile = "great2.1.xml",aug_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395, site_list = [""],cur_sys = "GEC3"):
    tree = et.parse(xmlfile)
    inputs_aug = tree.getroot().find("inputs").find("aug")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_aug.text = "\n"
    while (count_day < day_length):
        day = doy + count_day
        for cur_site in site_list:
            inputs_aug.text = inputs_aug.text + "     " + os.path.join(aug_dir,"{:0>4}{:0>3}".format(year,day),"server",cur_site+"-{}-FIXED-30.aug".format(cur_sys)) + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML inputs abs
def change_inputs_obs(xmlfile = "great2.1.xml",obs_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395, site_list = [""]):
    tree = et.parse(xmlfile)
    inputs_obs = tree.getroot().find("inputs").find("rinexo")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_obs.text = "\n"
    yy = year - 2000
    while (count_day < day_length):
        day = doy + count_day
        for cur_site in site_list:
            inputs_obs.text = inputs_obs.text + "     " + os.path.join(obs_dir,"{:0>3}".format(day),"{}{:0>3}0.{:0>2}o".format(cur_site,day,yy)) + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML inputs nav
def change_inputs_nav(xmlfile = "great2.1.xml",office = "brdm",nav_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395):
    tree = et.parse(xmlfile)
    inputs_nav = tree.getroot().find("inputs").find("rinexn")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_nav.text = "\n"
    yy = year - 2000
    while (count_day < day_length):
        day = doy + count_day
        inputs_nav.text = inputs_nav.text + "     " + os.path.join(nav_dir,"{}{:0>3}0.{:0>2}n".format(office,day,yy)) + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML inputs sp3clk
def change_inputs_sp3clk(xmlfile = "great2.1.xml",office = "gfz",sp3_dir = "default",clk_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395):
    tree = et.parse(xmlfile)
    inputs_sp3 = tree.getroot().find("inputs").find("sp3")
    inputs_clk = tree.getroot().find("inputs").find("rinexc")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_sp3.text,inputs_clk.text = "\n","\n"
    yy = year - 2000
    while (count_day < day_length):
        day = doy + count_day
        y_temp,mon,date = doy2ymd(int(year),int(day))
        week = ymd2gpsweekday(int(year),mon,date)
        inputs_sp3.text = inputs_sp3.text + "     " + os.path.join(sp3_dir,"{}{:5d}.sp3".format(office,week)) + "\n"
        inputs_clk.text = inputs_clk.text + "     " + os.path.join(clk_dir,"{}{:5d}.clk".format(office,week)) + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML inputs auggrid
def change_inputs_auggrid(xmlfile = "great2.1.xml",grid_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395,cur_site = "HKSC",area = "HK"):
    tree = et.parse(xmlfile)
    inputs_auggrid = tree.getroot().find("inputs").find("aug_grid")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_auggrid.text = "\n"
    yy = year - 2000
    while (count_day < day_length):
        day = doy + count_day
        inputs_auggrid.text = inputs_auggrid.text + "     " + os.path.join(grid_dir,"{:0>4}{:0>3}".format(year,day),"{}-R-{}-C-CROSS".format(area,cur_site),"GREAT-GEC3-30.grid") + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML inputs system file
def change_inputs_sys(xmlfile = "great2.1.xml",cur_sys = "GEC"):
    tree = et.parse(xmlfile)
    inputs_atx = tree.getroot().find("inputs").find("atx")
    inputs_blq = tree.getroot().find("inputs").find("blq")
    inputs_de = tree.getroot().find("inputs").find("de")
    inputs_eop = tree.getroot().find("inputs").find("eop")
    inputs_lep = tree.getroot().find("inputs").find("leapsecond")
    if cur_platform == "Darwin":
        inputs_atx.text="/Users/hanjunjie/Master_3/Data/model/igs_absolute_14.atx"
        inputs_blq.text="/Users/hanjunjie/Master_3/Data/model/oceanload"
        inputs_de.text ="/Users/hanjunjie/Master_3/Data/model/jpleph_de405_great"
        inputs_eop.text="/Users/hanjunjie/Master_3/Data/model/poleut1_2023"
        inputs_lep.text="/Users/hanjunjie/Master_3/Data/model/leap_seconds"
    else:
        if "C2" in cur_sys:
            inputs_atx.text="/cache/hanjunjie/Project/A-Paper-1/model/igs_absolute_14_BDS.atx"
            inputs_blq.text="/cache/hanjunjie/Project/A-Paper-1/model/oceanload"
            inputs_de.text ="/cache/hanjunjie/Project/A-Paper-1/model/jpleph_de405_great"
            inputs_eop.text="/cache/hanjunjie/Project/B-IUGG/model/poleut1_igmas"
            inputs_lep.text="/cache/hanjunjie/Project/A-Paper-1/model/leap_seconds"
        else:
            inputs_atx.text="/cache/hanjunjie/Project/B-IUGG/model/igs_absolute_14.atx"
            inputs_blq.text="/cache/hanjunjie/Project/A-Paper-1/model/oceanload"
            inputs_de.text ="/cache/hanjunjie/Project/A-Paper-1/model/jpleph_de405_great"
            inputs_eop.text="/cache/hanjunjie/Project/B-IUGG/model/poleut1_igmas"
            inputs_lep.text="/cache/hanjunjie/Project/A-Paper-1/model/leap_seconds"
    tree.write(xmlfile)

#Change XML inputs system file for great1
def change_inputs_sys_great1(xmlfile = "great2.1.xml",cur_sys = "GEC"):
    tree = et.parse(xmlfile)
    inputs_atx = tree.getroot().find("inputs").find("atx")
    inputs_blq = tree.getroot().find("inputs").find("blq")
    inputs_de = tree.getroot().find("inputs").find("DE")
    inputs_eop = tree.getroot().find("inputs").find("poleut1")
    inputs_lep = tree.getroot().find("inputs").find("leapsecond")
    if cur_platform == "Darwin":
        inputs_atx.text="/Users/hanjunjie/Master_3/Data/2023/model_BDS3/igs_absolute_14.atx"
        inputs_blq.text="/Users/hanjunjie/Master_3/Data/2023/model_BDS3/oceanload"
        inputs_de.text ="/Users/hanjunjie/Master_3/Data/2023/model_BDS3/jpleph_de405_great"
        inputs_eop.text="/Users/hanjunjie/Master_3/Data/2023/model_BDS3/poleut1"
        inputs_lep.text="/Users/hanjunjie/Master_3/Data/2023/model_BDS3/leap_seconds"
    else:
        if "C2" in cur_sys:
            inputs_atx.text="/cache/hanjunjie/Project/A-Paper-1/model/igs_absolute_14_BDS.atx"
            inputs_blq.text="/cache/hanjunjie/Project/A-Paper-1/model/oceanload"
            inputs_de.text ="/cache/hanjunjie/Project/A-Paper-1/model/jpleph_de405_great"
            inputs_eop.text="/cache/hanjunjie/Project/B-IUGG/model/poleut1_igmas"
            inputs_lep.text="/cache/hanjunjie/Project/A-Paper-1/model/leap_seconds"
        else:
            inputs_atx.text="/cache/hanjunjie/Project/B-IUGG/model/igs_absolute_14.atx"
            inputs_blq.text="/cache/hanjunjie/Project/A-Paper-1/model/oceanload"
            inputs_de.text ="/cache/hanjunjie/Project/A-Paper-1/model/jpleph_de405_great"
            inputs_eop.text="/cache/hanjunjie/Project/B-IUGG/model/poleut1_igmas"
            inputs_lep.text="/cache/hanjunjie/Project/A-Paper-1/model/leap_seconds"
    run_mkdir.mkdir("upd")
    tree.write(xmlfile)

#Change XML outputs log
def change_outputs_log(xmlfile = "great2.1.xml",purpose = "ByHjj",mode = "TIME"):
    tree = et.parse(xmlfile)
    outputs_log = tree.getroot().find("outputs").find("log")
    cur_time = datetime.utcnow()
    if mode == "TIME":
        outputs_log.attrib["name"] = "{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}".format(purpose,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second)
    else:
        outputs_log.attrib["name"] = "{}-{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}".format(purpose,mode,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second)
    tree.write(xmlfile)
 
 #Change XML outputs aug

#Change XML outputs auggrid
def change_outputs_aug2grid(xmlfile = "great2.1.xml",area = "XXXX",rm_site_list= [""],ck_site_list = [""],cur_sys = "GEC",sampling = 5):
    tree = et.parse(xmlfile)
    outputs_aug = tree.getroot().find("outputs").find("aug")
    outputs_aug.text = "{}-R-".format(area)
    output_dir = "{}-R-".format(area)
    for cur_site in rm_site_list:
        outputs_aug.text = outputs_aug.text + cur_site + "-"
        output_dir = output_dir + cur_site + "-"
    outputs_aug.text = outputs_aug.text + "C-"
    output_dir = output_dir + "C-"
    for cur_site in ck_site_list:
        outputs_aug.text = outputs_aug.text + cur_site + "-"
        output_dir = output_dir + cur_site + "-"
    outputs_aug.text = outputs_aug.text[:-1]
    output_dir = output_dir[:-1]
    run_mkdir.mkdir(output_dir)
    outputs_aug.text = os.path.join(outputs_aug.text,"$(rec)-{}-{:d}.aug".format(cur_sys,sampling))
    tree.write(xmlfile)

#Change XML outputs for Server of PPPRTK (ppp flt enu aug)
def change_outputs_aug(xmlfile = "great2.1.xml",amb = "XXXX",cur_sys = "GEC",sampling = 5,reset_par = 0):
    tree = et.parse(xmlfile)
    outputs_ppp = tree.getroot().find("outputs").find("ppp")
    outputs_flt = tree.getroot().find("outputs").find("flt")
    outputs_enu = tree.getroot().find("outputs").find("enu")
    outputs_aug = tree.getroot().find("outputs").find("aug")
    
    run_mkdir.mkdir("server")
    if reset_par == 0:
        outputs_ppp.text = os.path.join("server","$(rec)-{}-{}-{:d}.ppp".format(cur_sys,amb,sampling))
        outputs_flt.text = os.path.join("server","$(rec)-{}-{}-{:d}.flt".format(cur_sys,amb,sampling))
        outputs_enu.text = os.path.join("server","$(rec)-{}-{}-{:d}.enu".format(cur_sys,amb,sampling))
        outputs_aug.text = os.path.join("server","$(rec)-{}-{}-{:d}.aug".format(cur_sys,amb,sampling))
    else:
        outputs_ppp.text = os.path.join("server","$(rec)-{}-{}-{:d}-{}.ppp".format(cur_sys,amb,sampling,reset_par))
        outputs_flt.text = os.path.join("server","$(rec)-{}-{}-{:d}-{}.flt".format(cur_sys,amb,sampling,reset_par))
        outputs_enu.text = os.path.join("server","$(rec)-{}-{}-{:d}-{}.enu".format(cur_sys,amb,sampling,reset_par))
        outputs_aug.text = os.path.join("server","$(rec)-{}-{}-{:d}-{}.aug".format(cur_sys,amb,sampling,reset_par))
    tree.write(xmlfile)

#Change XML outputs for Client of PPPRTK (flt aug)
def change_outputs_client(xmlfile = "great2.1.xml",amb = "XXXX",cur_sys = "GEC",sampling = 5,reset_par = 0):
    tree = et.parse(xmlfile)
    outputs_flt = tree.getroot().find("outputs").find("flt")
    outputs_aug = tree.getroot().find("outputs").find("aug")
    
    run_mkdir.mkdir("client")
    if reset_par == 0:
        outputs_flt.text = os.path.join("client","$(rec)-{}-{}-{:d}.flt".format(cur_sys,amb,sampling))
        outputs_aug.text = os.path.join("client","$(rec)-{}-{}-{:d}.aug".format(cur_sys,amb,sampling))
    else:
        outputs_flt.text = os.path.join("client","$(rec)-{}-{}-{:d}-{}.flt".format(cur_sys,amb,sampling,reset_par))
        outputs_aug.text = os.path.join("client","$(rec)-{}-{}-{:d}-{}.aug".format(cur_sys,amb,sampling,reset_par))
    tree.write(xmlfile)

#Change XML anywhere with string
def change_node_subnode_string(xmlfile = "great2.1.xml",node = "ambiguity",subnode = "fix_mode",data = "NO"):
    tree = et.parse(xmlfile)
    outputs_aug = tree.getroot().find(node).find(subnode).text = " " + data + " "
    tree.write(xmlfile)

#Change XML inputs upd
def change_inputs_upd(xmlfile = "great2.1.xml",upd_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395):
    tree = et.parse(xmlfile)
    inputs_upd = tree.getroot().find("inputs").find("upd")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_upd.text = "\n"
    while (count_day < day_length):
        day = doy + count_day
        inputs_upd.text = inputs_upd.text + "     " + os.path.join(upd_dir,"upd_wl_{:0>4}{:0>3}_GEC".format(year,day)) + "\n"
        inputs_upd.text = inputs_upd.text + "     " + os.path.join(upd_dir,"upd_nl_{:0>4}{:0>3}_GEC".format(year,day)) + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML filter any
def change_filter_anystring(xmlfile = "great2.1.xml",attribt = "reset_par",data = "0"):
    tree = et.parse(xmlfile)
    outputs_filter = tree.getroot().find("filter")
    outputs_filter.attrib[attribt] = data
    tree.write(xmlfile)

#Reset XML receiver and parameter to 0
def reset_receiver_parameter(xmlfile = "great2.1.xml",site_list = [""]):
    tree = et.parse(xmlfile)
    outputs_receiver = tree.getroot().find("receiver")
    outputs_parameters = tree.getroot().find("parameters")
    for cur_site in site_list:
        cur_site_rec = Element("rec")
        cur_site_rec.attrib["id"] = cur_site
        cur_site_rec.attrib["X"] = "{:>8.4f}".format(0)
        cur_site_rec.attrib["Y"] = "{:>8.4f}".format(0)
        cur_site_rec.attrib["Z"] = "{:>8.4f}".format(0)
        cur_site_rec.tail = "\n"
        outputs_receiver.append(cur_site_rec)

        cur_site_rec = Element("STA")
        cur_site_rec.attrib["ID"] = cur_site
        cur_site_rec.attrib["sigCLK"] = "9000"
        cur_site_rec.attrib["sigPOS"] = "100_100_100"
        cur_site_rec.attrib["sigSION"] = "9000"
        cur_site_rec.attrib["sigTropPd"] = "0.015"
        cur_site_rec.attrib["sigZTD"] = "0.201"
        cur_site_rec.tail = "\n"
        outputs_parameters.append(cur_site_rec)
    tree.write(xmlfile)

#Set XML receiver and parameter according to EPN csv
def set_receiver_parameter(xmlfile = "great2.1.xml",site_list = [""],site_xyz = {}):
    tree = et.parse(xmlfile)
    outputs_receiver = tree.getroot().find("receiver")
    outputs_parameters = tree.getroot().find("parameters")
    for cur_site in site_list:
        cur_site_rec = Element("rec")
        cur_site_rec.attrib["id"] = cur_site
        cur_site_rec.attrib["X"] = "{:>8.4f}".format(site_xyz[cur_site][0])
        cur_site_rec.attrib["Y"] = "{:>8.4f}".format(site_xyz[cur_site][1])
        cur_site_rec.attrib["Z"] = "{:>8.4f}".format(site_xyz[cur_site][2])
        cur_site_rec.tail = "\n"
        outputs_receiver.append(cur_site_rec)

        cur_site_rec = Element("STA")
        cur_site_rec.attrib["ID"] = cur_site
        cur_site_rec.attrib["sigCLK"] = "9000"
        cur_site_rec.attrib["sigPOS"] = "0.1_0.1_0.1"
        cur_site_rec.attrib["sigSION"] = "9000"
        cur_site_rec.attrib["sigTropPd"] = "0.015"
        cur_site_rec.attrib["sigZTD"] = "0.201"
        cur_site_rec.tail = "\n"
        outputs_parameters.append(cur_site_rec)
    tree.write(xmlfile)
