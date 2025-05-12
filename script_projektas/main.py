import json
import time
import psutil
from utils import ask_confirmation, log_shutdown
from datetime import datetime

last_ask_times = {}

def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json failas nerastas. Sukuriame tuščią konfigūraciją.")
        return {}  # Jei failas nerastas, grąžiname tuščią žodyną
    except json.JSONDecodeError:
        print("Nepavyko nuskaityti config.json. Patikrinkite failą.")
        return {}

def get_hour():
    return datetime.now().hour

def terminate_process_by_name(name):
    try:
        for proc in psutil.process_iter(["name", "memory_info"]):
            try:
                if proc.info["name"].lower() == name.lower():
                    print(f"Bandome uždaryti procesą: {proc.info['name']}")  # Debug
                    proc.terminate()
                    print(f"Procesas uždarytas: {proc.info['name']}")  # Debug
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Klaida uždarant procesą: {e}")  # Loggins klaidas, kai procesas nebegalioja arba nėra prieigos
    except Exception as e:
        print(f"Įvyko klaida bandant peržiūrėti ar uždaryti procesą: {e}")  # Užfiksuoti klaidas per visą funkciją

def monitor():
    try:
        config = load_config()
        processes = config.get("processes", [])
        interval = config.get("check_interval_sec", 5)

        while True:

            # Peržiūrėk visus procesus
            for proc in psutil.process_iter(["name", "memory_info"]):
                for item in processes:
                    target_name = item["name"]
                    ram_limit = item["ram_limit_mb"]
                    key = target_name.lower()
                    now = time.time()

                    if proc.info["name"].lower() == target_name.lower():
                        try:
                            # Bandome gauti RAM naudojimą
                            ram_usage = proc.memory_info().rss // (1024 * 1024)
                            print(f"Patikriname {target_name}: {ram_usage} MB RAM")  # Debug

                            # Jei RAM viršija limitą
                            if ram_usage > ram_limit:
                                # Jei prieš mažiau nei 15 min. buvo paspausta "Ne" – neklauskime
                                if key in last_ask_times and now - last_ask_times[key] < 10:
                                    print(f"Neklausiama darkart, nes buvo paspausta 'Ne' prieš mažiau nei 10 sek.")
                                    continue

                                # Čia klausiame vartotojo, ar jis nori uždaryti procesą
                                if ask_confirmation(target_name, ram_usage):
                                    terminate_process_by_name(target_name)
                                    log_shutdown(target_name, ram_usage)
                                    print(f"{target_name} uždaryta.")
                                    if key in last_ask_times:
                                        del last_ask_times[key]  # išvalom seną laiką
                                else:
                                    print(f"Vartotojas atšaukė: {target_name}")
                                    last_ask_times[key] = now  # Įrašome laiką, kad žinotume, kada buvo paspausta "Ne"
                        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                            # Jei klaida gauti RAM arba uždaryti procesą, tai išveda klaidą ir tęsiasi toliau
                            print(f"Klaida su procesu {target_name}: {e}")
                        except Exception as e:
                            # Bendras klaidų apdorojimas, jei kažkas kito įvyko
                            print(f"Nežinoma klaida stebint procesą {target_name}: {e}")

            time.sleep(interval)
    except Exception as e:
        print(f"Įvyko klaida stebint procesus: {e}")  # Užfiksuoti klaidas monitoriaus funkcijoje

if __name__ == "__main__":
    monitor()
