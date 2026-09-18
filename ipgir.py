import socket
from concurrent.futures import ThreadPoolExecutor

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port
    except:
        return None

def scan_ports(ip, ports):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]
        for future in futures:
            port = future.result()
            if port:
                open_ports.append(port)
    return open_ports

if __name__ == "__main__":
    domain = input("Enter domain or website address: ").strip()
    ip = get_ip(domain)
    if not ip:
        print("Could not resolve domain.")
        exit()

    print(f"IP address for {domain} is {ip}")

    # پورت‌های پرتکرار و مهم
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 8080, 8443]

    open_ports = scan_ports(ip, common_ports)

    if open_ports:
        print(f"Open ports on {ip}: {open_ports}")
    else:
        print(f"No open common ports found on {ip}.")
