import psycopg2
import socket
import subprocess
import os
import time
import getpass
import sys
import shutil
import psutil
from colorama import Fore, Style, init
from datetime import datetime

class SystemMonitor:
    def get_pyinfo(self):
        with open("/proc/cpuinfo") as file:
            pyinfo = file.read()
            py = (pyinfo.splitlines()[38].split(":"))
            (_, pi) = py
            return pi.strip()
    def get_hostname(self):
        return socket.gethostname()
    def get_ip(self):
        return subprocess.getoutput("hostname -I").strip()
    def get_username(self):
        return getpass.getuser()
    def get_python_version(self):
        return sys.version
    def get_disk_usage(self):
        disk = shutil.disk_usage("/")
        total = disk.total
        used = disk.used
        percent = (used / total) * 100
        return round(percent, 1)
    def get_free(self):
        disk = shutil.disk_usage("/")
        free = disk.free / (1024 ** 2)
        return round(free, 3)
    def get_total(self):
        disk = shutil.disk_usage("/")
        total = disk.total / (1024 **3)
        return round(total, 2)
    def get_usage(self):
        disk = shutil.disk_usage("/")
        used = disk.used / (1024 **3)
        return round(used, 2)
    def get_uptime(self):
        with open("/proc/uptime") as file:
            up = int(float(file.read().split()[0]))
            if up >= 3600:
                hour = up // 3600
                second = up % 3600
                minute = second // 60
                finalsecond = up % 60
                up = f"{hour} Hours, {minute} Minutes and {finalsecond} Seconds"
            elif up >= 60:
                minute = up // 60
                second = up % 60
                up = f"{minute} Minutes and {second} Seconds"
            elif up < 60:
                up = f"{up} Seconds"
            return up
    def get_memtotal(self):
        with open("/proc/meminfo") as file:
            data = file.read()
            tot = int(data.splitlines()[0].split()[1])
            free = int(data.splitlines()[2].split()[1])
            total = tot // 1024
            left = free // 1024
            used = total - left
            percent = left / total
            percent = round((total - left) / total * 100, 1) 
            return total, left, percent, used
    def get_cputemp(self):
        with open("/sys/class/thermal/thermal_zone0/temp") as file:
            temp = int(file.read()) / 1000
            return round(temp, 1)
    def get_cpuusage(self):
        return psutil.cpu_percent(interval=None)
    def get_swap(self):
        swap = psutil.swap_memory()
        total = int(swap.total / 1000 ** 2)
        used = int(swap.used / 1000 ** 2)
        free = int(swap.free / 1000 ** 2)
        percent = round(swap.percent, 1)
        return total, used, free, percent
    def get_voltage(self):
        voltage = subprocess.getoutput("vcgencmd measure_volts")
        if "not found" in voltage:
            return "Unavailable"
        if "volt=" in voltage:
            return voltage.split("=")[1]
        return voltage

    def get_throttle(self):
        throttle = subprocess.getoutput("vcgencmd get_throttled")
        if "not found" in throttle:
            return "Unavailable"
        if throttle == "throttled=0x0":
            return "Good"
        return "Throttling Detected!"
    def get_traffic(self):
        traffic = psutil.net_io_counters()
        bsent, brecieve, psent, preceive, errin, errout, dropin, dropout = traffic
        bsent = round(bsent / 1000 **2, 1)
        brecieve = round(brecieve / 1000 **2, 1)
        return bsent, brecieve, psent, preceive, errin, errout, dropin, dropout
    def get_memcolour(self, percent):
        if percentmem < 70:
            return Fore.GREEN
        elif percentmem < 90:
            return Fore.YELLOW
        return Fore.RED
    def get_swapcolour(self, percent):
        if percentswap < 10:
            return Fore.GREEN
        elif percentswap < 25:
            return Fore.YELLOW
        return Fore.RED
    def write_to_database(self):
        conn = psycopg2.connect(
            host="10.42.0.246",
            database="monitoring",
            user="postgres",
            password="password"
        )
        cur = conn.cursor()
        totalmem, leftmem, percentmem, usedmem = self.get_memtotal()
        totalswap, usedswap, freeswap, percentswap = self.get_swap()
        cur.execute(
            """
            INSERT INTO system_stats

            (

                container_name,
                timestamp,
                cpu_usage,
                memory_usage,
                cpu_temperature,
                status,
                swap_usage,
                storage_usage,
                storage_free,
                storage_total,
                storage_used
            )

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                socket.gethostname(),
                datetime.now().astimezone(),
                self.get_cpuusage(),
                percentmem,
                self.get_cputemp(),
                "Online",
                percentswap,
                self.get_disk_usage(),
                self.get_free(),
                self.get_total(),
                self.get_usage(),
            )
        )
        conn.commit()
        conn.close()

if __name__ == "__main__":
    monitor = SystemMonitor()
    totalmem, leftmem, percentmem, usedmem = monitor.get_memtotal()
    totalswap, usedswap, freeswap, percentswap = monitor.get_swap()
    bsent, brecieve, psent, preceive, errin, errout, dropin, dropout = monitor.get_traffic()
    memcolour = monitor.get_memcolour(percentmem)
    swapcolour = monitor.get_swapcolour(percentswap)
    while True:
        os.system("clear")
        print("Press 1 For Overall Statistics")
        print("Press 2 For Disk Statistics") 
        print("Press 3 For RAM Statistics") 
        print("Press 4 For Temperature And Volatage Statistics") 
        print("Press 5 To Exit")
        choice = int(input("Please Make A Choice: "))

        while choice == 1:
            try:
                while True:
                    os.system("clear")
                    totalmem, leftmem, percentmem, usedmem = monitor.get_memtotal()
                    totalswap, usedswap, freeswap, percentswap = monitor.get_swap()
                    bsent, brecieve, psent, preceive, errin, errout, dropin, dropout = monitor.get_traffic()
                    memcolour = monitor.get_memcolour(percentmem)
                    swapcolour = monitor.get_swapcolour(percentswap)
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    print(f"Hostname: {monitor.get_hostname()}")
                    print(f"Username: {monitor.get_username()}")
                    print(f"IP: {monitor.get_ip()}")
                    print(f"Pi: {monitor.get_pyinfo()}")
                    print(f"Uptime: {monitor.get_uptime()}")
                    print(f"Python Version: {monitor.get_python_version()}")
                    print(f"Storage Usage: {monitor.get_usage()}Gb/{monitor.get_total()}Gb ({monitor.get_disk_usage()}%)")
                    print(f"Memory Usage: {memcolour}{usedmem}MB/{totalmem}MB ({percentmem}%){Style.RESET_ALL}")
                    print(f"Swap Usage: {swapcolour}{usedswap}MB/{totalswap}MB ({percentswap}%){Style.RESET_ALL}")
                    print(f"CPU Usage: {monitor.get_cpuusage()}%")
                    print(f"CPU Temperature: {monitor.get_cputemp()}C")
                    print(f"Voltage: {monitor.get_voltage()}")
                    print(f"Throttle Status {monitor.get_throttle()}")
                    print(f"Network Traffic: Sent: {bsent}MB, Received: {brecieve}MB, Packets Sent: {psent}, Packets Received: {preceive}, ")
                    print("Click (Ctrl + C) if you want to go back to main menu: ")
                    time.sleep(2)
            except KeyboardInterrupt:
                break
        while choice == 2:
            try:
                while True:
                    os.system("clear")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    print(f"Total storage is {monitor.get_total()} Gb")
                    print(f"Storage left {monitor.get_free()} Gb")
                    print(f"Storage Usage: {monitor.get_usage()}Gb/{monitor.get_total()}Gb {monitor.get_disk_usage()}%")
                    print("Click (Ctrl + C) if you want to go back to main menu: ")
                    time.sleep(2)
            except KeyboardInterrupt:
                break
        while choice == 3:
            try:
                while True:
                    os.system("clear")
                    totalmem, leftmem, percentmem, usedmem = monitor.get_memtotal()
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    print(f"Total Memory: {totalmem}MB")
                    print(f"Free Memory: {leftmem}MB")
                    print(f"Memory Usage: {usedmem}MB/{totalmem}MB ({percentmem}%)")
                    print("Click (Ctrl + C) if you want to go back to main menu: ")
                    time.sleep(2)
            except KeyboardInterrupt:
                break
        while choice == 4:
            try:
                while True:
                    os.system("clear")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    print(f"CPU Temperature: {monitor.get_cputemp()}C")
                    print(f"Voltage: {monitor.get_voltage()}")
                    print(f"Throttle Status {monitor.get_throttle()}")
                    print("Click (Ctrl + C) if you want to go back to main menu: ")                
                    time.sleep(2)
            except KeyboardInterrupt:
                break
        if choice == 5:
            sys.exit()