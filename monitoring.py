from scapy.all import PcapReader, IP, IPv6, TCP, UDP, DNS
from scapy.error import Scapy_Exception
from datetime import datetime, timezone
import sqlite3
import os
import time
import glob
import shutil

# Répertoires
BASE_DIR = "/home/ubuntu/Documents/LAN"
LOG_DIR = os.path.join(BASE_DIR, "LOG")
ARCH_DIR = os.path.join(LOG_DIR, "ARCH")

# Base SQLite
DB_FILE = os.path.join(BASE_DIR, "network_monitor.db")

# Intervalle entre deux scans du dossier (en secondes)
POLL_INTERVAL = 30

# Seuils pour éviter de lire un fichier encore en cours d'écriture
MIN_AGE_SECONDS = 60       # au moins 60 s sans modification
MIN_SIZE_BYTES = 64        # au moins 64 octets (évite les fichiers vides)


def iso_time(pkt_time):
    """Convertit le timestamp du paquet en ISO8601 (UTC)."""
    ts_float = float(pkt_time)
    return datetime.fromtimestamp(ts_float, tz=timezone.utc).isoformat()


def get_ips(pkt):
    """Retourne (src_ip, dst_ip) en IPv4 ou IPv6, ou (None, None)."""
    if IP in pkt:
        return pkt[IP].src, pkt[IP].dst
    elif IPv6 in pkt:
        return pkt[IPv6].src, pkt[IPv6].dst
    else:
        return None, None


def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(ARCH_DIR, exist_ok=True)


def should_process(path):
    """Vérifie que le fichier est assez vieux et assez gros pour être traité."""
    try:
        size = os.path.getsize(path)
        age = time.time() - os.path.getmtime(path)
    except FileNotFoundError:
        return False

    if size < MIN_SIZE_BYTES:
        return False

    if age < MIN_AGE_SECONDS:
        return False

    return True


def get_conn():
    return sqlite3.connect(DB_FILE)


def insert_http(conn, ts, pcap_name, src_ip, src_port, dst_ip, dst_port, info=""):
    """Insère un évènement HTTP dans la base."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO http_ftp_logs (
            timestamp, pcap_file, src_ip, src_port, dst_ip, dst_port, protocol, info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ts, pcap_name, src_ip, src_port, dst_ip, dst_port, "HTTP", info))
    conn.commit()


def insert_dns(conn, ts, pcap_name, src_ip, dst_ip, qname, qtype, is_mdns):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO dns_logs (
            timestamp, pcap_file, src_ip, dst_ip, query_name, is_mdns
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ts, pcap_name, src_ip, dst_ip, qname, qtype, is_mdns))
    conn.commit()


def analyze_pcap(pcap_path):
    """Analyse un fichier pcap/pcapng pour HTTP et DNS, et stocke en BDD."""
    print(f"[i] Analyse de {pcap_path}")
    pcap_name = os.path.basename(pcap_path)
    conn = get_conn()

    # set pour éviter les doublons DNS dans CE fichier
    seen_dns = set()

    try:
        with PcapReader(pcap_path) as pcap:
            for pkt in pcap:
                ts = iso_time(pkt.time)
                src_ip, dst_ip = get_ips(pkt)
                if src_ip is None:
                    continue  # pas d'IP, on ignore

                # --- 1) HTTP (détection par ports TCP) ---
                if TCP in pkt:
                    sport = pkt[TCP].sport
                    dport = pkt[TCP].dport

                    # HTTP (ports courants)
                    if sport in (80, 8080, 8000) or dport in (80, 8080, 8000):
                        print(f"[HTTP] {ts}  {src_ip}:{sport} -> {dst_ip}:{dport}")
                        insert_http(
                            conn, ts, pcap_name,
                            src_ip, sport, dst_ip, dport
                        )

                # --- 2) DNS / mDNS ---
                dns = pkt.getlayer(DNS)
                if dns is None:
                    continue

                # On ne garde que les REQUÊTES (qr = 0)
                if dns.qr != 0:
                    continue

                qname = None
                qtype = None

                if dns.qd:  # section question
                    try:
                        qname = dns.qd.qname.decode(errors="ignore").rstrip(".")
                    except AttributeError:
                        qname = str(dns.qd.qname)
                    qtype = str(dns.qd.qtype)

                if not qname:
                    continue

                # mDNS si port 5353 (source ou destination)
                is_mdns = 0
                if UDP in pkt and (pkt[UDP].sport == 5353 or pkt[UDP].dport == 5353):
                    is_mdns = 1

                # Clé de déduplication : même src, dst, nom, type, mDNS dans ce pcap
                key = (src_ip, dst_ip, qname, qtype, is_mdns)
                if key in seen_dns:
                    continue
                seen_dns.add(key)

                print(f"[DNS ] {ts}  {src_ip} -> {dst_ip}  domaine = {qname}")
                insert_dns(
                    conn, ts, pcap_name,
                    src_ip, dst_ip, qname, qtype, is_mdns
                )

    except Scapy_Exception as e:
        print(f"[!] Erreur Scapy sur {pcap_path} : {e}")
        print("[!] Je laisse le fichier dans LOG, il sera réessayé plus tard.")
        conn.close()
        return False

    conn.close()
    print(f"[i] Fin d'analyse : {pcap_path}")
    return True


def main():
    ensure_dirs()
    print(f"[i] Surveillance du dossier : {LOG_DIR}")

    deja_faits = set()

    while True:
        pcaps = sorted(
            glob.glob(os.path.join(LOG_DIR, "*.pcap")) +
            glob.glob(os.path.join(LOG_DIR, "*.pcapng"))
        )

        for pcap in pcaps:
            if pcap in deja_faits:
                continue

            if not should_process(pcap):
                continue

            ok = analyze_pcap(pcap)
            if not ok:
                continue

            dest = os.path.join(ARCH_DIR, os.path.basename(pcap))
            shutil.move(pcap, dest)
            deja_faits.add(pcap)
            print(f"[i] Fichier archivé : {dest}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

