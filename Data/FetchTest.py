from Data.Database import Database  # Adjust this import based on your actual file structure

def main():
    print("📥 Fetching active employees...")
    try:
        employees = Database.get_active_employees()
        for emp in employees:
            print(emp)
    except Exception as e:
        print("❌ Error fetching employees:", e)

if __name__ == "__main__":
    main()
