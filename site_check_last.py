import urllib
import time
import re
import json
import subprocess
import os
import sys



sourcepath = (os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(sourcepath + '/sitecheck_logs'):
    os.makedirs(sourcepath + '/sitecheck_logs')

if not os.path.exists(sourcepath + '/sitecheck_logs/main.txt'):
    with open(sourcepath + '/sitecheck_logs/main.txt', "w+"):
        pass


def installpackets():
    list = ['mpg321', 'libnotify-bin']
    for i in list:
        rc = os.system('which ' + i)
        if rc == 0:
            pass
        else:
            os.system('apt-get install ' + i + ' -y')


def urlmain():
    return 'http://zakupka.com,http://satom.ru,http://tomas.by,http://tomas.kz'


def logging(info, url):
    with open(sourcepath + '/sitecheck_logs/sitecheck_mod.log',
              'a' if os.path.exists(sourcepath + '/sitecheck_logs/sitecheck_mod.log') else 'w+') as text:
        text.write(str(time.ctime())[:-4] + '  ' + str(info) + '  code:' + str(url) + '\n')


def mode():
    return 'r+' if os.path.exists(sourcepath + '/sitecheck_logs/main.txt') else 'w+'


def writecontent(save_data):
    with open(sourcepath + '/sitecheck_logs/main.txt', "w+") as prev_data_file:
        save_data['last_check_time'] = str(time.ctime())[:-4]
        prev_data_file.seek(0)
        prev_data_file.write(json.dumps(save_data))
        prev_data_file.truncate()
        prev_data_file.close()


def regular():
    return str(re.findall('http://(\D*)', site)).replace('\'', '').replace('[', '').replace(']', '')


def getcode(url):
    return urllib.urlopen(url).getcode()


try:
    user = subprocess.Popen("who".split(" "), stdout=subprocess.PIPE).stdout.read().split()[0]
    old_data = json.loads(''.join(open(sourcepath + '/sitecheck_logs/main.txt', mode()).readlines()))
    save_data = old_data.copy()
except Exception:
    old_data = {}
    save_data = {}

if not old_data:
    installpackets()
    os.popen("DISPLAY=:0 sudo -u " + user + " notify-send 'First run!\n ' 're-run script!' -i gtk-info")
    for site in urlmain().split(","):
        save_data[regular()] = 0
        writecontent(save_data)

    sys.exit()

for site in urlmain().split(","):
    start = time.time()
    try:
        got_code = getcode(str(site))
        if got_code not in [200, 301]:
            time_used = round(time.time() - start, 2)
            os.system("DISPLAY=:0 sudo -u " + user + " mpg321 " + sourcepath + "/beep-error.mp3")
            os.popen(
                "DISPLAY=:0 sudo -u " + user + " notify-send 'Connection warning!\n  %s' 'Code error: %s, check time: %s' -i gtk-info" % (
                    regular(), got_code, ' time:' + str(time_used)))
            save_data[regular()] = 1

            logging('Failed: ' + site, str(got_code) + '  time:' + str(time_used))
            writecontent(save_data)

        if int(old_data[regular()]) < 2 and got_code in [200, 301]:
            time_used = round(time.time() - start, 2)
            os.popen(
                "DISPLAY=:0 sudo -u " + user + " notify-send 'CONNECTION ESTABLISHED!\n  %s' 'Code: %s, check time: %s' -i gtk-info" % (
                    str(site), got_code, str(time_used)))
            os.system("DISPLAY=:0 sudo -u " + user + " mpg321 " + sourcepath + "/beep-ok.mp3")
            save_data[regular()] = 2
            logging('Work! ' + site, str(got_code) + '  time:' + str(time_used))
            writecontent(save_data)

        elif int(old_data[regular()]) == 2 and got_code in [200, 301]:
            save_data[regular()] = 2
            writecontent(save_data)
    except Exception as e:
        time_used = round(time.time() - start, 2)
        logging(('Error! ' + str(site)), str(e) + '  time:' + str(time_used))
        os.popen(
            "DISPLAY=:0 sudo -u " + user + " notify-send 'Connection error!\n  %s' '%s, check time: %s' -i gtk-info" % (
                regular(), e, str(time_used)))
        os.system("DISPLAY=:0 sudo -u " + user + " mpg321 " + sourcepath + "/beep-error.mp3")
        save_data[regular()] = 0
        writecontent(save_data)

# print 'OLDINFO: ', old_data
# print 'sAVEINFO: ', save_data
