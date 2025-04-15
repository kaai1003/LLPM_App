#!/usr/bin/python3
"""Harness Packaging Application"""

from models.galia import Galia
import datetime
import keyboard
from models.engine.db_manager import get_connection
from models.engine.db_manager import set_db_conn
from models.engine.app_tools import load_settings
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_id
from models.engine.app_tools import insert_harness_track
from models.engine.app_tools import insert_harness_details
from models.engine.db_manager import get_obj
from models.engine.picking_manager import display_jobs
from models.engine.picking_manager import update_orders
from models.engine.packaging_manager import check_packaging_config
from models.engine.packaging_manager import check_box_ref


# check App Settings
app_config = load_settings()
try:
    app_type = app_config["AppSettings"]["app_type"]
except:
    app_type = None
if app_type != "packaging":
    print("Error Settings ! please go to Setting")
    exit(1)
print("Welcome to Harness Packaging Application")
# load database settings
db_settings = picking_db_conn()

if db_settings is None:
    print("Error Loading Database Settings")
    exit(1)
print(get_connection(db_settings) is not None)
set_db_conn(db_settings)
line_id = get_line_id()
if line_id is None:
    print("Error Loading Line Settings")
    exit(1)
print(f"Line ID: {line_id}")
config = check_packaging_config()
if config is None:
    print("Error Loading Packaging Config")
    exit(1)
print("-----Box Scan------")
while True:
    box = config["BOX"]
    status_galia = None
    box_ref = None
    nr_galia = None
    opned_box_ref = None
    galia_obj = None
    current_galia = None
    box_label_barcodes = len(box)
    for i in range(box_label_barcodes):
        prefix = box[i].get("prefix", "")
        if box[i]["barcode"] == "reference":
            box_ref = input("Please Scan Box Reference: ")
            if box_ref.startswith(prefix):
                # Check if Ref opned in Database
                box_ref = box_ref[len(prefix):]
                ref_obj = get_obj("reference", "ref", box_ref)
                if ref_obj is None:
                    print(f"---Error!!!!---: Reference {box_ref} Not Found")
                    break
                print(f"Reference {box_ref} Found")
            elif box_ref == "exit":
                print("Exit.....")
                exit(0)
            else:
                print("---Error!!!!---: Incorrect Refrence Prefix")
                break
            # Check if there is Box open with same reference
            opned_box_ref = check_box_ref(box_ref)
        elif box[i]["barcode"] == "nrgalia":
            nr_galia = input("Please Scan BOX Numero Galia: ")
            if nr_galia.startswith(prefix):
                nr_galia = nr_galia[len(prefix):]
                if opned_box_ref:
                    if opned_box_ref["nr_galia"] == nr_galia:
                        status_galia = "open"
                        current_galia = Galia(**opned_box_ref)
                        print(f"Galia {nr_galia} is Opened and {opned_box_ref['scanned_q']} Fx Scanned")
                        continue
                    print(f"---Error!!!!---: Box With Reference {box_ref} is Open // Nr Galia {opned_box_ref['nr_galia']}")
                    print("Please Complete the Open Box First!!!")
                    break
                # check if nrgalia exist in Database
                galia_obj = get_obj("galia", "nr_galia", nr_galia)
                if galia_obj is None:
                    status_galia = "new"
                    current_galia = Galia()
                    current_galia.nr_galia = nr_galia
                    current_galia.reference = box_ref
                    current_galia.line_id = line_id
                    print(f"New Galia {nr_galia} Scanned")
                    continue
                elif galia_obj["status"] == "closed":
                    status_galia = "closed"
                    print(f"Galia {nr_galia[len(prefix):]} is Already Closed")
                    break
                elif galia_obj["status"] == "open":
                    print(f"---Error!!!!---: Galia {nr_galia} is Already Opened with Different Reference {galia_obj['reference']}")
                    print("Please Check the Scanned Galia!!!")
                    break
            elif nr_galia == "exit":
                print("Exit.....")
                exit(0)
            else:
                print("---Error!!!!---: Incorrect Nr Galia Prefix")
                break
        elif box[i]["barcode"] == "quantity":
            quantity = input("Please Scan BOX Quantity: ")
            if quantity.startswith(prefix):
                try:
                    quantity = int(quantity[len(prefix):])
                except:
                    print("---Error!!!!---: Incorrect Quantity Value")
                    break
                if status_galia == "new":
                    current_galia.total_q = quantity
                    current_galia.remain_q = quantity
                    current_galia.status = "open"
                    current_galia.save()
                    print(f"---New Galia {current_galia.nr_galia} Created---")
                    continue
                    # check Scanned Quantity
                elif status_galia == "open":
                    if quantity != current_galia.total_q:
                        print(f"---Error!!!!---: Incorrect Quantity Scanned {quantity} != {current_galia.total_q}")
                        break
                    print(f"{current_galia.scanned_q} Fx Scanned on Galia {current_galia.nr_galia}")
                    current_galia.update()
                    continue
                print("---Error!!!!---: Incorrect Status Galia")
                break
            elif quantity == "exit":
                print("Exit.....")
                exit(0)
            else:
                print("---Error!!!!---: Incorrect Quantity Prefix")
                break
        elif box[i]['barcode'] == "box_type":
            box_type = input("Please Scan BOX Type: ")
            if box_type.startswith(prefix):
                box_type = box_type[len(prefix):]
                continue
            elif box_ref == "exit":
                print("Exit.....")
                exit(0)
            else:
                print("---Error!!!!---: Incorrect Box Type Prefix")
                break
    if i == box_label_barcodes - 1:
        break
print("Box Scan Completed")
print(f"Scanned Box: {current_galia.to_dict()}")
exit(0)