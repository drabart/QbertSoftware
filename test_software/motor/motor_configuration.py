import argparse
import json
import odrive
from odrive.utils import backup_config, restore_config

def save_config(odrv, file_name):
    cfg = backup_config(odrv)
    with open(file_name, 'w') as f:
        json.dump(cfg, f, indent=4)
    print("Config backed up to", file_name)

def load_config(odrv, file_name):
    with open(file_name, 'r') as f:
        cfg = json.load(f)
    restore_config(odrv, cfg)
    print("Config restored from", file_name)
    print("⚠️  Note: encoder offset calibration and some parameters may not be restored — re-calibrate if needed.")

def main():
    parser = argparse.ArgumentParser(description="ODrive backup / restore via Python")
    parser.add_argument(
        "file_name", nargs="?", default="motor_config.json",
        help="Config JSON file to use (default: motor_config.json)"
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Backup config to ODrive instead of restore"
    )
    args = parser.parse_args()

    print("Looking for ODrive...")
    odrv = odrive.find_any()
    print("Connected to ODrive:", odrv)

    if args.backup:
        save_config(odrv, args.file_name)
    else:
        load_config(odrv, args.file_name)

if __name__ == "__main__":
    main()

