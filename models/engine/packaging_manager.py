#!/usr/bin/python3
"""Packaging Manager Module"""

import json
from models.engine.db_manager import get_all

PACK_CONFIG = "settings/packaging_config.json"

def load_config():
    """Load configuration from JSON file"""
    try:
        with open(PACK_CONFIG, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file '{PACK_CONFIG}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{PACK_CONFIG}'.")
        return None

def show_settings(config):
    """Display the settings from the configuration file"""
    for key, value in config.items():
        print(f"---------{key} Config Found---------")
        if key == "BOX":
            print("***Box Label Barcodes Order Scan***")
            for i in range(len(value)):
                print(f"Scan Step {i+1}:")
                print(f"Barcode: {value[i]['barcode']}")
                print(f"Prefix: {value[i]['prefix']}")
                print(f"Photo: {value[i]['photo']}")
        elif key == "FX":
            print("***FX Labels Order Scan***")
            s = 0
            for label, vars in value.items():
                print(f"### Step {s+1} :FX {label} Label Scan ###")
                for j in range(len(vars)):
                    print(f"___Scan Step {j+1}:___")
                    print(f"Barcode: {vars[j]['barcode']}")
                    print(f"Prefix: {vars[j]['prefix']}")
                    print(f"Photo: {vars[j]['photo']}")
                s += 1
            print(f"FX has {s} Labels")
    return True

def check_packaging_config():
    config = load_config()
    if config is None:
        return None
    else:
        if "BOX" not in config.keys():
            print("BOX Config Not Found")
            return None
        if len(config["BOX"]) < 3:
            print("Missing Barcodes Box Label config")
            return None
        if "FX" not in config.keys():
            print("FX Config Not Found")
            return None
        if len(config["FX"]) < 1:
            print("Missing FX Labels config")
            return None
        for label, vars in config["FX"].items():
            if len(vars) < 2:
                print(f"Missing FX {label} Barcode config")
                return None
    return config

def check_box_ref(box_ref):
    """Check Box Reference"""
    all_boxes = get_all("galia")
    if all_boxes is None:
        print("Galia Table is Empty")
        return None
    for box in all_boxes:
        if box["reference"] == box_ref and box["status"] == "open":
            return box
    return None