# Simulated Device Manager for Windows
# In real deployment, this would control SIM/dongle hardware

fake_ips = [
    '203.0.113.10',
    '203.0.113.11',
    '203.0.113.12',
    '203.0.113.13',
    '203.0.113.14',
]

current_ip_index = 0
last_known_good_ip = None

def get_current_ip():
    return fake_ips[current_ip_index]

def rotate_ip():
    global current_ip_index
    current_ip_index = (current_ip_index + 1) % len(fake_ips)
    return fake_ips[current_ip_index]

def device_health():
    # Always healthy in simulation
    return True

def get_last_known_good_ip():
    return last_known_good_ip

def set_last_known_good_ip(ip):
    global last_known_good_ip
    last_known_good_ip = ip
