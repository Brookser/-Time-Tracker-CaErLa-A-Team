from Data.Database import Database

def create_department():
    print("🏗️ Creating department D001...")
    Database.connect()
    cursor = Database._Database__connection.cursor()

    # Check if department already exists
    cursor.execute("SELECT * FROM department WHERE DPTID = ?", ("D001",))
    if cursor.fetchone():
        print("✅ Department D001 already exists.")
        return

    # Insert new department
    cursor.execute("INSERT INTO department (DPTID, DPT_NAME) VALUES (?, ?)", ("D001", "Engineering"))
    Database._Database__connection.commit()
    print("✅ Department D001 created.")

def create_employee():
    print("👤 Creating sample employee...")
    try:
        Database.add_employee(
            empid="E001",
            first_name="Casey",
            last_name="Hill",
            dptid="D001",
            email="casey.hill@example.com",
            mgr_empid=None,
            active=1
        )
        print("✅ Employee E001 created!")
    except Exception as e:
        print("❌ Failed to create employee:")
        print(e)

def main():
    create_department()
    create_employee()

if __name__ == "__main__":
    main()
