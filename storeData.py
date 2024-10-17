import get
import time
from database import BusData

if __name__ == "__main__":
    dbFile = "busData.db"
    db = BusData(dbFile)
    db.tableCreation()
    try:
        while True:
            data = get.getVehicle("1")
            db.inputData(data)
            time.sleep(6)
    except KeyboardInterrupt:
        print("\nProgram interrupted! Exiting...")
    finally:
        print("Database connection closed.")
