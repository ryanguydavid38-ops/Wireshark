#!/usr/bin/env python3
import sqlite3
import os

# Dossiers utilisés
DB_FILE = os.path.join("/home/ubuntu/Documents/LAN/network_monitor.db")

def main():

    # Connexion et execution
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Suppression des tables s'ils existent
    cur.execute("DROP TABLE IF EXISTS http_logs;")
    cur.execute("DROP TABLE IF EXISTS dns_logs;")

    # Création de la table HTTP
    cur.execute("""
    CREATE TABLE http_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,   -- date/heure du paquet
        pcap_file TEXT NOT NULL,   -- nom du fichier pcapng d'origine
        src_ip TEXT NOT NULL,
        src_port INTEGER,
        dst_ip TEXT NOT NULL,
        dst_port INTEGER
    );
    """)

    # Création de la table DNS / mDNS
    cur.execute("""
    CREATE TABLE dns_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,   -- Meme chose que la table HTTP
        pcap_file TEXT NOT NULL,   -- Idem
        src_ip TEXT NOT NULL,      
        dst_ip TEXT NOT NULL,      
        query_name TEXT,           -- nom de domaine demandé
        is_mdns INTEGER            -- 0 = DNS normal, 1 = mDNS (port=5353)
    );
    """)

    #Ecrit dans le fichier et ferme la co
    conn.commit() 
    conn.close() 
    print(f"[i] Base SQLite recréée : {DB_FILE}")

# C'est pour l'execution sur un cmd linux
if __name__ == "__main__":
    main()
