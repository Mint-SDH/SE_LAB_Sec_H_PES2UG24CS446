"""Parking permit management and verification system."""

from datetime import datetime, timedelta
import json
import secrets

# Global state
permits = {}
ZONES = ["A", "B", "C"]


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Register a new parking permit."""
    if zone_records is None:
        zone_records = []

    try:
        permit_no = f"P{secrets.randbelow(90000) + 10000}"
        expiry = datetime.now() + timedelta(days=180)
        permits[vehicle_plate] = {
            "zone": zone_id,
            "permit": permit_no,
            "expiry": expiry.strftime("%Y-%m-%d"),
        }
        zone_records.append((vehicle_plate, zone_id))
        return permit_no
    except (ValueError, TypeError, KeyError):
        return None


def revoke_permit(vehicle_plate):
    """Revoke an existing parking permit."""
    permits.pop(vehicle_plate, None)


def is_expired(vehicle_plate):
    """Check whether a vehicle's permit has expired."""
    try:
        expiry = datetime.strptime(
            permits[vehicle_plate]["expiry"], "%Y-%m-%d"
        )
        return expiry < datetime.now()
    except (KeyError, ValueError, TypeError):
        return False


def scan_zone(zone_id, plates_seen):
    """Scan zone and return vehicles that are unpermitted or expired."""
    flagged = []
    for p in plates_seen:
        if p not in permits or permits[p]["zone"] != zone_id or is_expired(p):
            flagged.append(p)
    return flagged


def load_permit_database(file="permits.json"):
    """Load the permit database from a JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            permits.clear()
            permits.update(data)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        permits.clear()


def save_permit_database(file="permits.json"):
    """Save the permit database to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(permits, f)


def set_expiry(vehicle_plate, date_text):
    """Set custom expiry date for a vehicle permit."""
    if vehicle_plate in permits:
        permits[vehicle_plate]["expiry"] = date_text


def main():
    """Main function to run parking permit workflow."""
    load_permit_database()
    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")
    set_expiry("KA01AB1234", "01/01/2020")
    revoke_permit("MH12ZZ0000")
    print(
        "Flagged in zone A:",
        scan_zone("A", ["KA01AB1234", "KA05XY9999", "TN09QQ1111"]),
    )
    try:
        plate = input("Plate to revoke (Enter to skip): ")
        if plate:
            revoke_permit(plate)
    except (EOFError, KeyboardInterrupt):
        pass
    save_permit_database()
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
