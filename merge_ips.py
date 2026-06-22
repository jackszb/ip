#!/usr/bin/env python3
import requests
import json
import ipaddress

URLS = [
    "https://raw.githubusercontent.com/jackszb/sukka-surge/main/ip/china_ip.json",
    "https://raw.githubusercontent.com/jackszb/sukka-surge/main/ip/china_ip_ipv6.json",
    "https://raw.githubusercontent.com/jackszb/sukka-surge/main/ip/lan.json"
]

OUTPUT_FILE = "ips-direct.json"


def fetch_ips(url):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("rules", [])[0].get("ip_cidr", [])
    except Exception as e:
        print(f"❌ 下载失败: {url} -> {e}")
        return []


def classify_ips(ip_list):
    ipv4 = set()
    ipv6 = set()

    for ip in ip_list:
        try:
            # 判断是否为CIDR或单IP
            net = ipaddress.ip_network(ip, strict=False)
            if isinstance(net, ipaddress.IPv4Network):
                ipv4.add(ip)
            else:
                ipv6.add(ip)
        except Exception:
            continue

    return ipv4, ipv6


def main():
    all_ips = []

    for url in URLS:
        all_ips.extend(fetch_ips(url))

    # 分类
    ipv4_set, ipv6_set = classify_ips(all_ips)

    # 排序
    ipv4_sorted = sorted(ipv4_set, key=lambda x: ipaddress.ip_network(x, strict=False))
    ipv6_sorted = sorted(ipv6_set, key=lambda x: ipaddress.ip_network(x, strict=False))

    # ipv4 在前 + ipv6 在后
    final_list = ipv4_sorted + ipv6_sorted

    output = {
        "version": 4,
        "rules": [
            {
                "ip_cidr": final_list
            }
        ]
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ 已生成 {OUTPUT_FILE} ，共 {len(final_list)} 条")


if __name__ == "__main__":
    main()
