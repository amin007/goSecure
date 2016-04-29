import subprocess
import RPi.GPIO as GPIO
import time

def set_vpn_params(vpn_server, user_id, user_psk):
    #set the goSecure server IP address in the ipsec.conf file
    with open("/etc/ipsec.conf") as fin:
        lines = fin.readlines()

    for x in range(0, len(lines)):
        if((lines[x].strip())[0:7] == "leftid="):
            lines[x] = "        leftid=%s       #unique id of client\n" % user_id
        if((lines[x].strip())[0:6] == "right="):
            lines[x] = "        right=%s       #strongSwan server external IP\n" % vpn_server

    with open("/etc/ipsec.conf", "w") as fout:
        for line in lines:
            fout.write(line)

    #save the username and secret to the ipsec.secrets file
    secrets = open("/etc/ipsec.secrets", "w")
    secrets.write("%s : PSK %s" % (user_id, user_psk))
    secrets.close()

    if(vpn_server != "" or user_id != "" or user_psk != ""):
        restart_vpn()
        subprocess.check_output(["sudo", "ip", "route", "add", "table", "220", "192.168.50.0/24", "dev", "eth0"])

        vpn_status = (subprocess.check_output(["sudo", "ipsec", "status"])).split("\n")
        if((vpn_status[1].strip())[9:20] == "ESTABLISHED"):
            #turn on LED
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(7,GPIO.OUT)
            GPIO.output(7,GPIO.HIGH)

def reset_vpn_params():
    set_vpn_params("", "", "")

def start_vpn():
    subprocess.check_output(["sudo", "ipsec", "start"])
    subprocess.check_output(["sudo", "ip", "route", "add", "table", "220", "192.168.50.0/24", "dev", "eth0"])

    vpn_status = (subprocess.check_output(["sudo", "ipsec", "status"])).split("\n")
    if((vpn_status[1].strip())[9:20] == "ESTABLISHED"):
        #turn on LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(7,GPIO.OUT)
        GPIO.output(7,GPIO.HIGH)

def stop_vpn():
    subprocess.check_output(["sudo", "ipsec", "stop"])
    #turn off LED
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(7,GPIO.OUT)
    GPIO.output(7,GPIO.LOW)

def restart_vpn():
    #turn off LED
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(7,GPIO.OUT)
    GPIO.output(7,GPIO.LOW)
    subprocess.check_output(["sudo", "ipsec", "restart"])
    subprocess.check_output(["sudo", "ip", "route", "add", "table", "220", "192.168.50.0/24", "dev", "eth0"])
    time.sleep(3)
    vpn_status = (subprocess.check_output(["sudo", "ipsec", "status"])).split("\n")
    if((vpn_status[1].strip())[9:20] == "ESTABLISHED"):
        GPIO.output(7,GPIO.HIGH)
