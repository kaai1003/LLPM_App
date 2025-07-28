#!/usr/bin/python3
"""Harness Packaging Application"""

from models.galia import Galia
from models.scanned import Scanned
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
from models.engine.packaging_manager import check_cpt_hns
from models.engine.packaging_manager import list_hns_labels
from models.engine.packaging_manager import show_open_galias


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
current_boxes = show_open_galias(line_id)
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
                print("---Error!!!!---: Incorrect Reference Prefix")
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
                    current_galia.scanned_q = 0
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
print("-----------Box Scan Completed-------------")
print(f"Scanned Box: {current_galia.to_dict()}")
print("----------------------------------------------")
print("-------Please Scan Harness Barcodes------")
while True:
    scan_result = False
    hns_label = config["FX"]
    hns_labels = list_hns_labels(hns_label)
    hns_label_count = len(hns_labels)
    current_cpt = None
    for i in range(hns_label_count):
        for brc in hns_label[hns_labels[i]]:
            prefix = brc.get("prefix", "")
            if brc["barcode"] == "reference":
                hns_ref = input(f"Please Scan {hns_labels[i]} Reference Harness Barcode: ")
                if hns_ref.startswith(prefix):
                    hns_ref = hns_ref[len(prefix):]
                    if hns_ref != current_galia.reference:
                        print(f"---Error!!!!---: Incorrect Reference Scanned {hns_ref} != {current_galia.reference}")
                        scan_result = False
                        break
                    print(f"Reference {hns_ref} Scanned")
                    scan_result = True
                    continue
                elif hns_ref == "exit":
                    print("Exit.....")
                    exit(0)
                else:
                    print("---Error!!!!---: Incorrect Harness reference Prefix")
                    scan_result = False
                    break
            elif brc["barcode"] == "compteur":
                cpt_len = brc["length"]
                hns_cpt = input(f"Please Scan {hns_labels[i]} Compteur Harness Barcode: ")
                if hns_cpt.startswith(prefix):
                    hns_cpt = hns_cpt[len(prefix):]
                    if len(hns_cpt) == cpt_len:
                        if current_cpt is None:
                            if check_cpt_hns(hns_cpt) is False:
                                print(f"---Error!!!!---: Compteur {hns_cpt} is Already Scanned")
                                scan_result = False
                                break
                            current_cpt = hns_cpt
                            scan_result = True
                            continue
                        if hns_cpt != current_cpt:
                            print(f"---Error!!!!---: Incorrect Compteur Scanned {hns_cpt} != {current_cpt}")
                            scan_result = False
                            break
                        print(f"Compteur {hns_cpt} Scanned")
                        scan_result = True
                        continue
                    print(f"---Error!!!!---: Incorrect Compteur Length {len(hns_cpt)} != {cpt_len}")
                    scan_result = False
                    break
                elif hns_cpt == "exit":
                    print("Exit.....")
                    exit(0)
                else:
                    print("---Error!!!!---: Incorrect Compteur Prefix")
                    scan_result = False
                    break
            elif brc["barcode"] == "box_type":
                box_size = input(f"Please Scan {hns_labels[i]} Box Type Barcode: ")
                if box_size.startswith(prefix):
                    box_size = box_size[len(prefix):]
                    if box_size != box_type:
                        print(f"---Error!!!!---: Incorrect Box Type Scanned {box_size} != {box_type}")
                        scan_result = False
                        break
                    print(f"Box Type {box_size} Scanned")
                    scan_result = True
                elif box_size == "exit":
                    print("Exit.....")
                    exit(0)
                else:
                    print("---Error!!!!---: Incorrect Box Type Prefix")
                    scan_result = False
                    break
        if scan_result is False:
            print("---Error!!!!---: Incorrect Harness Barcodes")
            break
    if i == hns_label_count - 1 and scan_result:
        # check if all harness are scanned
        current_galia.scanned_q += 1
        current_galia.remain_q -= 1
        scanned_hns = Scanned()
        scanned_hns.reference = current_galia.reference
        scanned_hns.counter = current_cpt
        scanned_hns.id_galia = current_galia.id
        print(f"---Harness {current_cpt} Scanned---")
        if current_galia.remain_q == 0:
            print(f"---All Harness Scanned for Galia {current_galia.nr_galia}---")
            # rescan Box to close it
            validation = False
            print("Please Rescan Box Reference and Nr Galia to Close it")
            for i in range(box_label_barcodes):
                prefix = box[i].get("prefix", "")
                if box[i]["barcode"] == "reference":
                    box_ref_val = input("Please Scan Box Reference: ")
                    if box_ref_val.startswith(prefix):
                        # Check if Ref opned in Database
                        box_ref_val = box_ref_val[len(prefix):]
                        if box_ref_val != current_galia.reference:
                            print(f"---Error!!!!---: Incorrect Reference Scanned {box_ref_val} != {current_galia.reference}")
                            validation = False
                            break
                        print(f"Reference {box_ref_val} Scanned")
                        validation = True
                        continue
                    elif box_ref_val == "exit":
                        print("Exit.....")
                        exit(0)
                    else:
                        print("---Error!!!!---: Incorrect Reference Prefix")
                        validation = False
                        break
                if box[i]["barcode"] == "nrgalia":
                    nr_galia_val = input("Please Scan BOX Numero Galia: ")
                    if nr_galia_val.startswith(prefix):
                        nr_galia_val = nr_galia_val[len(prefix):]
                        if nr_galia_val != current_galia.nr_galia:
                            print(f"---Error!!!!---: Incorrect Galia Scanned {nr_galia_val} != {current_galia.nr_galia}")
                            validation = False
                            break
                        print(f"Galia {nr_galia_val} Scanned")
                        validation = True
                        continue
                    elif nr_galia_val == "exit":
                        print("Exit.....")
                        exit(0)
                    else:
                        print("---Error!!!!---: Incorrect Nr Galia Prefix")
                        validation = False
                        break
            if i == box_label_barcodes - 1 and validation:
                # check if all harness are scanned
                current_galia.status = "closed"
                current_galia.update()
                scanned_hns.reference = current_galia.reference
                scanned_hns.counter = current_cpt
                scanned_hns.id_galia = current_galia.id
                scanned_hns.save()
                print(f"---print Label BOX Validation---")
                while True:
                    label_validation = input("Please Scan Label Validation: ")
                    if label_validation.startswith("C"):
                        if label_validation[len("C"):] != current_galia.nr_galia:
                            print(f"---Error!!!!---: Incorrect Label Validation {label_validation} != {current_galia.nr_galia}")
                            continue
                        print(f"Box {current_galia.nr_galia} Validation Label Scanned")
                        exit(0)
                    print("---Error!!!!---: Incorrect Label Validation Prefix")
                    continue
            print("---Error!!!!---: Incorrect Galia or Reference Scanned")
            exit(1)
        else:
            current_galia.update()
            scanned_hns.reference = current_galia.reference
            scanned_hns.counter = current_cpt
            scanned_hns.id_galia = current_galia.id
            scanned_hns.save()
            print(f"---Harness {current_galia.scanned_q} / {current_galia.remain_q} Scanned---")
            continue
    
exit(0)