import paramiko #include library paramiko
import datetime
import csv
import sys
import random

# TimeStamp
now = datetime.datetime.now()

# Generate Password
chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
number = 1 # Buat 1 line password
length = 8 # Jumalah karakter acak

for pwd in range(number):
    passwords = ''
    for pwd in range(length):
        passwords += random.choice(chars)
    random_pas = passwords

#inisialisasi connection SSH with paramiko
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='192.168.76.177', username='admin', password='')

# open file Banner with ro
with open("banner.txt", "r", encoding="utf-8") as text:
    # Read File
    banner = text.read()
print(f"""{banner}""")
print("\n")

# List Config
print("=" * 25 + "Configure Access Point" + "=" * 25)
while True:
    id = input("Identity: ")
    if not id:
        print("Error: Identity tidak boleh kosong. Silakan coba lagi.")
        continue
    ip = input("IP Address: ")
    if not ip:
        print("Error: IP Address tidak boleh kosong. Silakan coba lagi.")
        continue
    ssid = input("SSID: ")
    if not ssid:
        print("Error: SSID tidak boleh kosong. Silakan coba lagi.")
        continue
    password = random_pas
    print(f"Password: {password}")

    break
print("\n")

# Enable Service Wireless
enabled_wifi = (f"interface wireless enable wlan1")

# 1. Configure IP Address
address = (f"ip address add address={ip} interface=wlan1")
sh_ip = ("ip address print")
prefix = '/'.join(ip.split('/')[-1:])
ip_pool = '.'.join(ip.split('.')[:3])

# 2. Configure DHCP Server
list_pool = (f"ip pool add name=pool_invention ranges={ip_pool}.10-{ip_pool}.100")
sh_pool = ("ip pool print")
network = (f"ip dhcp-server network add address={ip_pool}.0/{prefix} gateway={ip_pool}.1 dns-server=8.8.8.8,8.8.4.4")
sh_net = ("ip dhcp-server network print")
dhcp = (f"ip dhcp-server add name=pool_invention interface=wlan1 lease-time=120m address-pool=pool_inventio disabled=no")
sh_dhcp = (" ip dhcp-server print")

# 3. Configure Wireless
security_profile = (f"interface wireless security-profiles set default \
                    mode=dynamic-keys authentication-types=wpa-psk,wpa2-psk \
                    wpa2-pre-shared-key={password} wpa-pre-shared-key={password} \
                    unicast-ciphers=aes-ccm group-ciphers=aes-ccm ")
sh_sec = ("interface wireless security-profiles print ")
access_point = (f'interface wireless set wlan1 mode=ap-bridge band=2ghz-b/g/n ssid="{ssid}" radio-name=forkits ')
sh_wlan = (" interface wireless print")
identity = (f"system identity set name={id}")
sh_id = ("system identity print ")

stdin, stdout, stderr = ssh_client.exec_command(' system routerboar print ')

routerboard = {}
for line in stdout:
    result = line.strip('\n')
    if ':' in result:
        key, value = result.split(':', 1)
        routerboard[key.strip()] = value.strip()
model = routerboard['model']

# Check Data Router
def check_id_exists(filename, id):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == id:
                return True
    return False

# Import Data Router
def write_to_csv(filename):
    # Check row id
    if check_id_exists(filename, id):
        print(f"'Identity '{id}' sudah terdaftar di {filename}.")
        print('\n')
        sys.exit()
    # Open file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([id, ip, ssid, password, model, now])
filename = 'data_router.csv'
write_to_csv(filename)

# Executed Command
config = [
    enabled_wifi,
    address,
    sh_ip,
    list_pool,
    sh_pool,
    network,
    sh_net,
    dhcp,
    sh_dhcp,
    security_profile,
    sh_sec,
    access_point,
    sh_wlan,
    identity,
    sh_id
]

for post in config:
    stdin, stdout, stderr = ssh_client.exec_command(post)

    for line in stdout:
        print(line.strip('\n'))

# Closed Connections
ssh_client.close()