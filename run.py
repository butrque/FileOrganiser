import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import sys
import winreg as reg

def setup_startup():
  script_path = str(Path(__file__).resolve())
  key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

  try:
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)

    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")

    command = f'"{pythonw_path}" "{script_path}"'

    reg.SetValueEx(key, "FileOrganizer", 0, reg.REG_SZ, command)
    reg.CloseKey(key)
  except Exception as e:
    print(f"Błąd autostartu: {e}")

current_dir = Path(__file__).parent
config_path = current_dir / "config.json"


PHOTOS_DIR = PHOTOS = VIDEOS_DIR = VIDEOS = MUSIC_DIR = MUSIC = ARCHIVE_DIR = ARCHIVE = SCRIPTS_DIR = SCRIPTS = EXE_DIR = EXE = None # default

try:
    if Path(config_path).exists():

        with open(config_path, "r", encoding="utf-8") as config:
            config_data = json.load(config)

            if config_data.get("photos"):
                PHOTOS_DIR = Path(config_data["photos"])
            if config_data.get("videos"):
                VIDEOS_DIR = Path(config_data["videos"])
            if config_data.get("music"):
                MUSIC_DIR = Path(config_data["music"])
            if config_data.get("archive"):
                ARCHIVE_DIR = Path(config_data["archive"])
            if config_data.get("scripts"):
                SCRIPTS_DIR = Path(config_data["scripts"])
            if config_data.get("exe"):
                EXE_DIR = Path(config_data["exe"])

            PHOTOS = config_data.get("ifPhotos", False)
            VIDEOS = config_data.get("ifVideos", False)
            MUSIC = config_data.get("ifMusic", False)
            ARCHIVE = config_data.get("ifArchive", False)
            SCRIPTS = config_data.get("ifScripts", False)
            EXE = config_data.get("ifExe", False)

            
    elif Path(config_path).exists() == False:

        setup_startup()
        print("Nie znaleziono pliku config.json - stwórz konfigurację [T/N]")

        if input("Czy chcesz zapisywać pliki graficzne? [jpg, jpeg, png...]: ").lower() == "t":
            PHOTOS = True
            PHOTOS_DIR = input("Podaj ścieżke do folderu, w którym mają być zapisywane pliki graficzne: \n" ).strip('"\'')

        if input("Czy chcesz zapisywać pliki wideo? [mp4, mov...]: ").lower() == "t":
            VIDEOS = True
            VIDEOS_DIR = input("Podaj ścieżke do folderu, w którym mają być zapisywane pliki wideo: \n" ).strip('"\'')

        if input("Czy chcesz zapisywać pliki muzyczne? [mp3, m4a...]: ").lower() == "t":
            MUSIC = True    
            MUSIC_DIR  = input("Podaj ścieżke do folderu, w którym mają być zapisywane pliki muzyczne: \n" ).strip('"\'')

        if input("Czy chcesz zapisywać archiwa? [zip, rar, 7z...]: ").lower() == "t":
            ARCHIVE = True    
            ARCHIVE_DIR  = input("Podaj ścieżke do folderu, w którym mają być zapisywane archiwa: \n" ).strip('"\'')

        if input("Czy chcesz zapisywać pliki executable? [exe, msi]: ").lower() == "t":
            EXE = True    
            EXE_DIR  = input("Podaj ścieżke do folderu, w którym mają być zapisywane pliki wykonywalne: \n" ).strip('"\'')

        if input("Czy chcesz zapisywać pliki programistyczne/skrypty? [html, py, css, js, json, xml...]: ").lower() == "t":
            SCRIPTS = True    
            SCRIPTS_DIR  = input("Podaj ścieżke do folderu, w którym mają być zapisywane skrypty: \n" ).strip('"\'')

        print("Zapisano! Skrypt Automatycznie odpali się przy nastepnym odpaleniu systemu.")

        config_data = {

            "photos" : PHOTOS_DIR,
            "videos" : VIDEOS_DIR,
            "music" : MUSIC_DIR,
            "archive" : ARCHIVE_DIR,
            "scripts" : SCRIPTS_DIR,
            "exe" : EXE_DIR,
            "ifPhotos" : PHOTOS,
            "ifVideos" : VIDEOS,
            "ifMusic" : MUSIC,
            "ifArchive" : ARCHIVE,
            "ifScripts" : SCRIPTS,
            "ifExe" : EXE
            
        }
    
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

except Exception as e:
    print(e)
    
DOWNLOADS_DIR = Path.home() / "Downloads"

for i in [PHOTOS_DIR, VIDEOS_DIR, MUSIC_DIR, ARCHIVE_DIR, SCRIPTS_DIR, EXE_DIR]:
    if i != None: i = Path(i)

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or event.src_path.endswith(
            (".crdownload", ".temp", ".part")
        ):
            return

        time.sleep(1)

        file_path = Path(event.src_path)
        print(f"Wykryto Plik: {file_path}")
        print(file_path.suffix.lower())

        time.sleep(1)

        # = sortowanie =
        try:
            if file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".jps", ".gif"] and PHOTOS:
                file_path.rename(PHOTOS_DIR / file_path.name)
            elif file_path.suffix.lower() in [".mp4", ".mkv", ".avi", ".mov", ".webm"] and VIDEOS:
                file_path.rename(VIDEOS_DIR / file_path.name)
            elif file_path.suffix.lower() in [".mp3", ".wav", ".m4a"] and MUSIC:
                file_path.rename(MUSIC_DIR / file_path.name)    
            elif file_path.suffix.lower() in [".zip", ".7z", ".rar", ".tar"] and ARCHIVE:
                file_path.rename(ARCHIVE_DIR / file_path.name)
            elif file_path.suffix.lower() in [".exe", ".msi"] and EXE:
                file_path.rename(EXE_DIR / file_path.name)
            elif file_path.suffix.lower() in [".py", ".json", ".html", ".js", ".css", ".xml"] and SCRIPTS:
                file_path.rename(SCRIPTS_DIR / file_path.name)
            else:
                print("Nie obsługuje: " + file_path.suffix.lower())
        except Exception as e:
            print(e)

if __name__ == "__main__":
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(DOWNLOADS_DIR), recursive=False)

    observer.start()
    print("Uruchomiono, naciśnij Ctrl+C aby zatrzymać. ")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Zatrzymano.")

observer.join()
