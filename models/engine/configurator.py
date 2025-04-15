#!/usr/bin/python3
"""App configuratot Module"""

import configparser

CONFIG_FILE = "settings/config.ini"
LINES_CONFIG = "settings/lines.ini"


def create_app_type(app_type):
    config = configparser.ConfigParser()
    if "AppSettings" not in config:
        config["AppSettings"] = {}
    
    config["AppSettings"]["app_type"] = app_type
    
    with open(CONFIG_FILE, "w") as file:
        config.write(file)
    print(f"Configuration file '{CONFIG_FILE}' created successfully!")

def create_line(line_name,dbname,user,password,host,port):
    config = configparser.ConfigParser()
    config.read(LINES_CONFIG)
    if line_name in config:
        print(f"{line_name} Already Exist")
        return False
    config[line_name] = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port
    }
    with open(LINES_CONFIG, "w") as file:
        config.write(file)
    return True

def create_db(name,dbname,user,password,host,port):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if name in config:
        print(f"{name} Already Exist")
        return False
    config[name] = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port
    }
    with open(CONFIG_FILE, "w") as file:
        config.write(file)
    return True

def update_db(name,dbname,user,password,host,port):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if name in config:
        config[name] = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        with open(CONFIG_FILE, "w") as file:
            config.write(file)
        return True
    return False

def set_line_id(line_id):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config.set("AppSettings", "line_id", str(line_id))
    with open(CONFIG_FILE, "w") as file:
        config.write(file)
    print(f"Configuration file '{CONFIG_FILE}' created successfully!")