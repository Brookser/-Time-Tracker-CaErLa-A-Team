# ⏱️ Time Tracker (CaErLa A-Team)

A lightweight time tracking web app with a database backend and built-in reporting features.  
Built using Python, Flask, and MariaDB — this MVP is part of a team project to recreate basic time tracking functionality like Harvest or Toggl.

---

## 🚧 Project Overview

The Time Tracker app lets users:

- Log time entries manually or via start/stop
- Create and manage employees, projects, and departments
- View logged time entries in a web dashboard
- Filter/report by project and timeframe (in progress)

---

## 🧱 Tech Stack

- **Python 3.11**
- **Flask** (Jinja2 templating)
- **MariaDB** (hosted on AWS EC2)
- **HTML/CSS** for the reporting UI
- **Pytest** for unit testing
- **Chrome** Browser for testing
- **JetBrains PyCharm** as primary development env 
- Organized using **TDD principles**

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Brookser/-Time-Tracker-CaErLa-A-Team.git
cd Time-Tracker-CaErLa-A-Team
```

### 2. Requirements & Libraries
Make sure you have Python 3.11+ installed. This project uses:

- Flask – for serving the web interface
- python-dotenv – for loading DB credentials from .env
- MariaDB Connector – mariadb library for database access
- Pytest – for running unit tests

### 3. Database Setup
>**Note: The full schema is still being finalized. Once complete, it will be provided in a schema.sql file.Log in and create the database:**

If you'd like to create your own local copy of the database:

1. Make sure MariaDB is installed.
2. Log in and create the database:

```bash 
CREATE DATABASE time_tracker;
USE time_tracker;
```
Run the schema script:
```bash
source schema.sql
```
> 🛠️ **Using a different database?**
>
> This project uses the `mariadb` Python library to connect to a MariaDB instance hosted on AWS EC2.  
> If you plan to use another SQL database (e.g., MySQL, SQLite, PostgreSQL), you will need to:
>
> - Replace `import mariadb` with the appropriate connector for your DB
> - Update the `Database.connect()` method in `src/Data/Database.py` to match your driver’s connection format
> - Ensure your SQL tables match the structure provided in `schema.sql`


### 4. Set up your .env file

```bash
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=time_tracker
DB_PORT=3306 # or whatever port you have configured
```
### 5. Run the app
```bash
python src/WebUI.py
```