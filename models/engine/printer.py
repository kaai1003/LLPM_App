#!/usr/bin/python
"""print label Module"""
import win32print
import win32ui
import os

def godex_label(label,data):
    """generate label"""
    printer = 'Godex G500'
    template_path = f"./settings/{label}.txt"
    try:
        # Read the template
        with open(template_path, 'r') as template_file:
            label_content = template_file.read()

        # Replace variables in the template
        if data:
            label_content = label_content.format(**data)
            output_label = './settings/{}.txt'.format(label + '_output')
            # Save the modified label to a new file
            with open(output_label, 'w') as output_file:
                output_file.write(label_content)
            
            print(f"Label generated and saved to {output_label}")
            try:
                # Get the printer handle
                printer_handle = win32print.OpenPrinter(printer)
                
                # Open a print job
                job = win32print.StartDocPrinter(printer_handle, 1, ("Print Job", None, "RAW"))
                win32print.StartPagePrinter(printer_handle)

                
                # Send the content to the printer
                win32print.WritePrinter(printer_handle, label_content.encode('utf-8'))
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                print("File sent to the printer successfully.")
                # ✅ Delete the file after successful print
                if os.path.exists(output_label):
                    os.remove(output_label)
                    print(f"Deleted temporary file: {output_label}")
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def micra_label(label, data):
    """Generate and print label for Micra printer (EPL format)"""
    printer = 'Micra Printer'   # ⚠️ change this to the exact Windows printer name
    template_path = f"./settings/{label}.txt"

    try:
        # Read the template
        with open(template_path, 'r') as template_file:
            label_content = template_file.read()

        # Replace variables in the template
        if data:
            label_content = label_content.format(**data)
            output_label = f'./settings/{label}_output.txt'

            # Save the modified label to a new file
            with open(output_label, 'w') as output_file:
                output_file.write(label_content)

            print(f"Label generated and saved to {output_label}")

            try:
                # Open printer handle
                printer_handle = win32print.OpenPrinter(printer)

                # Start a print job
                job = win32print.StartDocPrinter(printer_handle, 1, ("Micra Print Job", None, "RAW"))
                win32print.StartPagePrinter(printer_handle)

                # EPL must be ASCII, not UTF-8
                win32print.WritePrinter(printer_handle, label_content.encode("ascii"))

                # End printing
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)

                print("File sent to the Micra printer successfully.")

                # ✅ Delete the file after success
                if os.path.exists(output_label):
                    os.remove(output_label)
                    print(f"Deleted temporary file: {output_label}")

            except Exception as e:
                print(f"Printing Error: {e}")

    except Exception as e:
        print(f"File/Template Error: {e}")

def tsc_label(nr_galia, ref, qt, op, date_time):
    PRINTER_NAME = "TSC TTP-246 PRO"

    # TSPL Label Command
    label_data = f"""
    SIZE 55 mm,25 mm
    GAP 3 mm,0 mm
    CLS

    TEXT 40,5,"3",0,1,1,"CONDITIONNMENT OK"
    BARCODE 50,40,"128",40,0,0,2,2,"C{nr_galia}"
    TEXT 80,82,"2",0,1,1,"{nr_galia}"
    TEXT 10,110,"3",0,1,1,"REF: P{ref}"
    TEXT 290,90,"2",0,1,1,"Qt: {qt}"
    TEXT 290,110,"2",0,1,1,"OP: {op}"
    TEXT 30,145,"2",0,1,1,"DATE: {date_time}"
    

    PRINT 1
    """
    # Open printer
    printer_handle = win32print.OpenPrinter(PRINTER_NAME)
    printer_info = win32print.GetPrinter(printer_handle, 2)
    printer_name = printer_info["pPrinterName"]

    # Send the label to the printer
    hprinter = win32print.OpenPrinter(printer_name)
    hprinter_job = win32print.StartDocPrinter(hprinter, 1, ("Label Print", None, "RAW"))
    win32print.StartPagePrinter(hprinter)
    win32print.WritePrinter(hprinter, label_data.encode("utf-8"))
    win32print.EndPagePrinter(hprinter)
    win32print.EndDocPrinter(hprinter)
    win32print.ClosePrinter(hprinter)

    print("Label sent successfully!")