# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import commands
from subprocess import *
reload(sys)
sys.setdefaultencoding('utf-8')

apiPidPath = '/var/log/gunicorn/debug.pid'
managerPidPath = '/var/log/gunicorn/debug_manager.pid'
cwdPath = '/var/python/siegeServer'

def restartGunicorn(isKill):

    #未找到进程，直接重启
    if isKill:
        subprocess.call(['pkill -9 gunicorn'], shell=True)
        subprocess.call(['gunicorn -c gun.conf runserver:app'], shell=True, cwd=cwdPath)
        #subprocess.call(['gunicorn -c gun_manager.conf runserver_manager:app'], shell=True, cwd=cwdPath)
        print('kill all and restart all')
    #不kill平滑重启
    else:
        pid = open(apiPidPath).read().decode('utf8').strip()
        subprocess.call(['kill -HUP {0}'.format(pid)], shell=True)
        print('kill -HUP {0}'.format(pid))
        pid = open(managerPidPath).read().decode('utf8').strip()
        subprocess.call(['kill -HUP {0}'.format(pid)], shell=True)
        print('kill -HUP {0}'.format(pid))
        print('gracefull restart gunicorn')


if __name__ == '__main__':

    status, output = commands.getstatusoutput('ps -ef|grep gunicorn')
    if output.find('python2.7') >= 0:
        isKill = False
    else:
        isKill = True

    restartGunicorn(isKill)

    print 'restart gunicorn success'