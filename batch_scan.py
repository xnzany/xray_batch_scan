#环境： python3 batch_scan.py
#用法： 将url放入batch_urls_xray.txt文件进行扫描即可，根据自己的需求更改scan_command即可

import re
import time
from multiprocessing import Pool
import subprocess
import urllib.parse

def get_output_filename(targeturl):
    hostname = urllib.parse.urlparse(targeturl).hostname
    date_format = time.strftime('%Y%m%d%H%M%S', time.localtime())
    return f"{hostname}_{date_format}"

"""
TODO: xray扫描命令,自行更改
"""
def get_scan_command(targeturl):
    # 输出文件
    output_html = f"./batch_scan_output/{get_output_filename(targeturl)}.html"
    # 要执行的xray命令
    scan_command = f"xray_windows_amd64.exe webscan --basic-crawler {targeturl} --html-output {output_html}"
    # print(scan_command)
    return scan_command

# 获取url扫描
def get_url():
    print("Xray Scan Start~")
    with open("batch_urls_xray.txt", 'r') as f:
        lines = f.readlines()
        # 进度标识位
        schedule = 1
        schedules = len(lines)
        # 最多四个进程(此线程是在xray默认线程数的基础上的。xray默认线程数:10)
        pool = Pool(4) if (schedules >= 4) else Pool(schedules)
        # 匹配http | https请求头
        pattern = re.compile(r'^(https|http)://')
        for line in lines:
            try:
                if not pattern.match(line.strip()):
                    targeturl = "http://"+line.strip()
                else:
                    targeturl = line.strip()
                pool.apply_async(func=do_scan, args=(targeturl, schedule, schedules))
                schedule += 1
            except Exception as e:
                print(e)
        pool.close()
        pool.join()
        print("Xray Scan End~")

# 报告
def do_scan(targeturl, schedule, schedules):
    print(f"当前正在扫描第{schedule}个任务，还剩{schedules - schedule}条任务，程序总共执行了{(schedule / schedules * 100)}%")
    scan_command = get_scan_command(targeturl)
    print(f"执行的命令: {scan_command}")
    result, error = subprocess.Popen(scan_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
    #报错输出
    print(result.decode("GB2312"))
    print("报错:" + error)
    if error:
        print("报错:" + error)
# 
if __name__ == '__main__':
    get_url()
