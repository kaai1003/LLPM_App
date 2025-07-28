#!/usr/bin/python3
"""App Tools Functions"""

import configparser
import json
import os
from models.tracker import Tracker
from models.harness import Harness
from models.engine.db_manager import get_list_obj
from models.engine.db_manager import get_obj

CONFIG_FILE = "settings/config.ini"
LINES_CONFIG = "settings/lines.ini"

def load_settings():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def check_app_type():
    """check App Type"""
    app_config = load_settings()
    try:
        app_type = app_config["AppSettings"]["app_type"]
        return app_type
    except:
        return None

def load_lines():
    config = configparser.ConfigParser()
    config.read(LINES_CONFIG)
    if not config.sections():
        print("No lines found in the configuration file.")
        return None
    return config.sections()

def check_db_conn(id):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config.sections()

def get_line_conn(line_id):
    config = configparser.ConfigParser()
    config.read(LINES_CONFIG)
    if line_id in config:
        print(f"{line_id} Exist")
        return {key: value if key != "port" else int(value) for key, value in config[line_id].items()}
    print(f"line {line_id} Not Exist")
    return None

def picking_db_conn():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if "DATABASE" in config:
        print("Database Exist")
        return {key: value if key != "port" else int(value) for key, value in config["DATABASE"].items()}
    print(f"DATABASE Not Exist")
    return None

def get_line_id():
    app_config = load_settings()
    try:
        line_id = app_config["AppSettings"]["line_id"]
        return line_id
    except:
        return None

def get_line_details(line_id):
    """Get Line Details"""
    line_details = get_obj("lines", "line_id", line_id)
    if line_details:
        print(f"Line Details: {line_details}")
        return line_details
    return None
    
def insert_harness_track(refrence, cpt, line_id, process, status):
    """Insert Harness Track"""
    harness_track = {'reference': refrence,
                         'compteur': cpt,
                         'line_id': line_id,
                         'process': process,
                         'harness_status': status,
                         }
    Tracker(**harness_track).save()
    print(f"Harness Track {refrence} Inserted with Compteur {cpt}")
    return True

def insert_harness_details(refrence, cpt, line_id, process, result):
    """Insert Harness Track"""
    harness_details = {'reference': refrence,
                         'compteur': cpt,
                         'line_id': line_id,
                         'process': process,
                         'test_result': result,
                         }
    Harness(**harness_details).save()
    print(f"Harness Track {refrence} Inserted with Compteur {cpt}")
    return True

def set_dashboard_config(dashboard):
    """Set DB connection as env variable"""
    # set db_conn dictionnary as windows env variable
    os.environ["DASHBOARD_CONFIG"] = json.dumps(dashboard)