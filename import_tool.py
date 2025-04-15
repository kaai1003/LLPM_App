#!/usr/bin/python3

from models.reference import Reference
from models.line import Line
from models.process import Process
from models.project import Project
from models.job import Job
from models.user import User
from models.engine.db_manager import get_connection
from models.engine.db_manager import get_obj
from models.engine.db_manager import get_all
from models.engine.db_manager import load_csv

if get_connection():
    print("Connection Established")
else:
    print("Connection Failed")
    exit(1)

print("--------Welcome to Tool Importer--------")
print("Select table to Import:\n1- Users\n2- Jobs \n3- Lines\n4- Process\n5- Projects\n6- References")

table_selected = input("please type number of table to be Imported: ")

if table_selected == "1":
    users = load_csv("import/users.csv")
    for user in users:
        obj = User(**user)
        obj.save()
    print("Users Imported Succefully")
    exit(0)
elif table_selected == "2":
    jobs = load_csv("import/jobs.csv")
    for job in jobs:
        obj = Job(**job)
        obj.save()
    print("Jobs Imported Succefully")
    exit(0)
elif table_selected == "3":
    lines = load_csv("import/lines.csv")
    for l in lines:
        obj = Line(**l)
        obj.save()
    print("Lines Imported Succefully")
    exit(0)
elif table_selected == "4":
    process = load_csv("import/process.csv")
    for p in process:
        obj = Process(**p)
        obj.save()
    print("Process Imported Succefully")
    exit(0)
elif table_selected == "5":
    projects = load_csv("import/projects.csv")
    for p in projects:
        obj = Project(**p)
        obj.save()
    print("Projects Imported Succefully")
    exit(0)
elif table_selected == "6":
    refs = load_csv("import/refs.csv")
    for ref in refs:
        obj = Reference(**ref)
        obj.save()
    print("References Imported Succefully")
    exit(0)
else:
    print("incorrect Selection, please try again")
    exit(1)