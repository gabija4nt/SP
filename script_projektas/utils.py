import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

last_ask_times = {}

def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ignored_programs": []}

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def ask_confirmation(process_name, ram_usage):
    config = load_config()
    ignored = config.get("ignored_programs", [])

    if process_name in ignored:
        return False

    response_data = {"confirmed": False}

    def ask():
        result = messagebox.askyesno(
            "Patvirtinimas", 
            f"Jūsų programa {process_name} naudoja {ram_usage} MB RAM.\nAr norite ją uždaryti?"
        )
        if result:
            response_data["confirmed"] = True
        else:
            more_ask = messagebox.askyesno(
                "Daugiau neklausti", 
                "Ar norite, kad ši programa nebebūtų stebima?"
            )
            if more_ask:
                ignored.append(process_name)
                config["ignored_programs"] = ignored
                save_config(config)

        root.destroy()
    
    root = tk.Tk()
    root.after(0, ask)
    root.mainloop()
    
    return response_data["confirmed"]

def log_shutdown(process_name, ram_usage):
    with open("shutdown.log", "a", encoding="utf-8") as f:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] Uždaryta: {process_name} (RAM: {ram_usage} MB)\n")
