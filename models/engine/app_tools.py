#!/usr/bin/python3
"""App Tools Functions"""

import configparser
import json
import os
from models.tracker import Tracker
from models.harness import Harness
from models.engine.db_manager import get_list_obj
from models.engine.db_manager import get_obj
from datetime import datetime, timedelta

CONFIG_FILE = "settings/config.ini"
LINES_CONFIG = "settings/lines.ini"
DASH_CONFIG = "settings/dashboard.ini"

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


def get_dashboard_config(config_path=DASH_CONFIG):
    """Retrieve Dashboard config as a dictionary from the INI file"""
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return {}

    config.read(config_path)

    if "Dashboard" not in config:
        return {}

    # Convert the values to int where possible
    result = {}
    for key, value in config["Dashboard"].items():
        value = value.strip()
        if value == "":
            result[key] = ""
        else:
            try:
                result[key] = int(value)
            except ValueError:
                result[key] = value
    return result

def set_dashboard_config(data, config_path=DASH_CONFIG):
    """Create or update the Dashboard section in the INI config file"""
    config = configparser.ConfigParser()
    
    # Load existing file if it exists
    if os.path.exists(config_path):
        config.read(config_path)

    if "Dashboard" not in config:
        config["Dashboard"] = {}

    for key, value in data.items():
        config["Dashboard"][key] = str(value)

    # Write back to the file
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def get_expected_fx(shift_range, shift_target):
    """
    Calculate expected number of scanned FX based on elapsed time in shift.
    
    Parameters:
        shift_range (str): shift time range in format "HH:MM-HH:MM"
        shift_target (int): total expected scanned FX for the full shift

    Returns:
        int: expected FX count at current time
    """
    try:
        # Parse shift range
        start_str, end_str = shift_range.split('-')
        now = datetime.now()
        today = now.date()

        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        start_dt = datetime.combine(today, start_time)
        end_dt = datetime.combine(today, end_time)

        # Handle overnight shifts (e.g., 22:00–06:00)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        # Clip current time between start and end
        if now < start_dt:
            elapsed_minutes = 0
        elif now >= end_dt:
            elapsed_minutes = (end_dt - start_dt).total_seconds() / 60
        else:
            elapsed_minutes = (now - start_dt).total_seconds() / 60

        total_minutes = (end_dt - start_dt).total_seconds() / 60

        if total_minutes == 0:
            return 0

        expected = (elapsed_minutes / total_minutes) * shift_target
        return int(expected)

    except Exception as e:
        print("Error in get_expected_fx:", e)
        return 0