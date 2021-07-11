# YANGPATH=/home/adam/libyang-cffi/newtests/yang python m.py


import os, psutil
import gc
import sys
import time

process = psutil.Process(os.getpid())

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


print(sizeof_fmt(process.memory_info().rss))  # in bytes

print('PID', process)

import yangvoodoo
print('import yangvoodoo')
print(sizeof_fmt(process.memory_info().rss))  # in bytes



for c in range(5):
    print('*'*80)
    print(c)
    print('*'*80)
    session = yangvoodoo.DataAccess()
    print('session = yangvoodoo.DataAccess()')

    print(sizeof_fmt(process.memory_info().rss))  # in bytes

    session.connect('minimal-integrationtest')
    print('session.connect')


    print(sizeof_fmt(process.memory_info().rss))  # in bytes

    print('del session')
    del session

    for i in range(5):
        print(sizeof_fmt(process.memory_info().rss))  # in bytes
        print(gc.collect())
        print('  gc.collect() ',i)
    time.sleep(1)
