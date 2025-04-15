#!/usr/bin/python3
"""App Settings"""

from models.engine.app_tools import load_settings
from models.engine.configurator import create_app_type
from models.engine.app_tools import load_lines
from models.engine.configurator import create_line
from models.engine.app_tools import check_db_conn
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_id
from models.engine.configurator import create_db
from models.engine.configurator import update_db
from models.engine.configurator import set_line_id
from models.engine.packaging_manager import show_settings
from models.engine.packaging_manager import check_packaging_config


print("Welcome to LLPM Settings")
print("Loading Settings....")
app_config = load_settings()
try:
    app_type = app_config["AppSettings"]["app_type"]
    print(f"{app_type} Application")
except:
    print('App Type is Not Set!!!')
    app_type = None
if app_type is None:
    print("Please Choose App Type: ")
    print("1- Orders Manager App")
    print("2- Picking App")
    print("3- Packaging App")
    app_type = input("Please Select App Type Number From the List: ")
    if app_type == "1":
        create_app_type("orders_manager")
        print("APP is set to Orders Manager")
        lines = load_lines()
        if lines:
            print("lines Found:")
            for line in lines:
                print(line)
            exit(0)
        print("No Line Found!!! please add lines")
        exit(1)
    elif app_type == "2":
        create_app_type("picking")
        print("APP is set to Picking Application")
        exit(0)
    elif app_type == "3":
        create_app_type("packaging")
        print("APP is set to Packaging Application")
        exit(0)
    else:
        print("incorrect Selection, please try again")
        exit(1)
elif app_type == "orders_manager":
    print("Welcome to Orders Manager Application")
    lines = load_lines()
    if lines:
        print("lines Found:")
        for line in lines:
            print(line)
        feedback = input("Add new Line ??\n1 - YES\n2 - No\n")
        if feedback == "1":
            while True:
                line_name = input("Insert Line Name: ")
                dbname = input("Insert DataBase Name: ")
                user = input("Insert User Name: ")
                password = input("Insert User Password: ")
                host = input("Insert DataBase Host: ")
                port = input("Insert DataBase Port: ")
                new_line = create_line(line_name,dbname,user,password,host,port)
                if new_line:
                    print(f"Line {line_name} Added successfully!")
                else:
                    print(f"Line {line_name} Already Exist!")
                feedback = input("Add new Line ??\n1 - YES\n2 - No\n")
                if feedback == "YES":
                    continue
                break
        exit(0)
    else:
        print("no Line Found!! please add new Line")
        while True:
            line_name = input("Insert Line Name: ")
            dbname = input("Insert DataBase Name: ")
            user = input("Insert User Name: ")
            password = input("Insert User Password: ")
            host = input("Insert DataBase Host: ")
            port = input("Insert DataBase Port: ")
            new_line = create_line(line_name,dbname,user,password,host,port)
            if new_line:
                print(f"Line {line_name} Added successfully!")
            else:
                print(f"Line {line_name} Already Exist!")
            feedback = input("Add new Line ??\n1 - YES\n2 - No\n")
            if feedback == "1":
                continue
            break
        exit(0)
elif app_type == "picking":
    print("Welcome to Picking Application")
    # check Picking line_id
    line_id = get_line_id()
    if line_id is None:
        print("Line ID Not Found!!")
        print("Please set Line ID")
        id = input("Insert Line ID: ")
        set_line_id(id)
        print(f"Line ID {id} set successfully!")
    print(f"Line ID: {line_id}")
    picking_settings = picking_db_conn()
    if picking_settings:
        print("Settings OK!!!")
        feedback = input("update Database ??\n1 - YES\n2 - No\n")
        if feedback == "1":
            name = "DATABASE"
            dbname = input("Insert DataBase Name: ")
            user = input("Insert User Name: ")
            password = input("Insert User Password: ")
            host = input("Insert DataBase Host: ")
            port = input("Insert DataBase Port: ")
            new_line = update_db(name,dbname,user,password,host,port)
            print(f"Picking {name} Updated successfully!")
        print(f"{app_type} Application\nLine ID: {line_id}\nDatabase Settings: {picking_settings}")
        exit(0)
    elif picking_settings == {}:
        print("Database Settings Not Set!!")
        name = "DATABASE"
        dbname = input("Insert DataBase Name: ")
        user = input("Insert User Name: ")
        password = input("Insert User Password: ")
        host = input("Insert DataBase Host: ")
        port = input("Insert DataBase Port: ")
        new_line = update_db(name,dbname,user,password,host,port)
        print(f"Picking {line_id} Database Updated successfully!")
        print(f"Settings OK!!!{app_type} Application\nLine ID: {line_id}\nDatabase Settings: {picking_settings}")
        exit(0)
    print("No Database Setting Found for Picking APP!!")
    feedback = input("Add new Database ??\n1 - YES\n2 - No\n")
    if feedback == "1":
        name = "DATABASE"
        dbname = input("Insert DataBase Name: ")
        user = input("Insert User Name: ")
        password = input("Insert User Password: ")
        host = input("Insert DataBase Host: ")
        port = input("Insert DataBase Port: ")
        new_line = create_db(name,dbname,user,password,host,port)
        print(f"Picking {line_id} Database Added successfully!")
        print(f"Settings OK!!!{app_type} Application\nLine ID: {line_id}\nDatabase Settings: {picking_settings}")
        exit(0)
    elif feedback == "2":
        print("You should Set Databse Settings Before Continue")
        exit(1)
    else:
        print("incorrect Selection, please try again")
        exit(1)
elif app_type == "packaging":
    print("Welcome to Packaging Application")
    # check Packaging line_id
    line_id = get_line_id()
    if line_id is None:
        print("Line ID Not Found!!")
        print("Please set Line ID")
        id = input("Insert Line ID: ")
        set_line_id(id)
        print(f"Line ID {id} set successfully!")
    print(f"Line ID: {line_id}")
    config = check_packaging_config()
    if config:
        print("Configuration loaded successfully.")
        show_settings(config)
    else:
        print("Failed to load configuration.")
        exit(1)
    exit(0)
