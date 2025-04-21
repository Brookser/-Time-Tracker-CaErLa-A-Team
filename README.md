# ⏱️ Time Tracker (CaErLa A-Team)

The Time Tracker is an app for logging time and managing projects. Built for individuals and teams, 
it supports multiple user roles (like Individual Users, Managers, and Admins) to track time, 
view performance, and generate actionable reports. Designed with clarity and scalability in mind, 
it helps teams stay aligned, improve productivity, and deliver work on time.

Built with Python, Flask, and MariaDB, the app delivers core time tracking features through a lightweight, scalable framework.


## 👥 Authors
Abdullatif Al-Abdulrazzaq, Erika Brooks, and Casey Hill


## 📚 Table of Contents
- [General Info](#general-info)
- [Technologies Used](#technologies-used)
- [Setup](#setup)
- [Project Status](#project-status)
- [Known Bugs](#known-bugs)
- [License](#license)


## 📖 General Info
This application allows users to:
- Log time entries manually or with a start/stop system
- Create and manage employees, projects, and departments
- View and filter reports by project and date range
- Track work across teams using a MariaDB backend and Flask frontend


## 🛠 Technologies Used

- **Python 3.11**
- **Flask** – with Jinja2 templates for web rendering
- **MariaDB** – hosted on AWS EC2
- **HTML/CSS** – for the frontend reporting UI
- **Pytest** – for unit testing
- **python-dotenv** – for handling environment variables
- **Chrome** – for browser testing
- **JetBrains PyCharm** – for development
- Organized using **Test-Driven Development (TDD)** principles

- **Additional Package for Tests** pip install mysql-connector-python

## 🧩 Setup & Installation

<details>
<summary><strong style="font-size: 1.3em;"> Initial Setup </strong></summary>

1. Clone this repository:
```bash
git clone https://github.com/Brookser/-Time-Tracker-CaErLa-A-Team.git
cd Time-Tracker-CaErLa-A-Team
```

2. Set up a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
pip install tabluate
pip install prettytable

</details>


<details>
<summary><strong style="font-size: 1.3em;"> Database Setup </strong></summary>

> **Note: The full schema is still being finalized. Once complete, it will be provided in a \`schema.sql\` file.**

If you'd like to create your own local copy of the database:

1. Make sure MariaDB is installed.
2. Log in and create the database:
```bash
CREATE DATABASE time_tracker;
USE time_tracker;
```

3. Run the schema script:
```bash
source schema.sql
```

> 🛠️ **Using a different database?**
>
> This project uses the \`mariadb\` Python library to connect to a MariaDB instance hosted on AWS EC2.  
> If you plan to use another SQL database (e.g., MySQL, SQLite, PostgreSQL), you will need to:
> - Replace \`import mariadb\` with the appropriate connector for your DB
> - Update the \`Database.connect()\` method in \`src/Data/Database.py\` to match your driver’s connection format
> - Ensure your SQL tables match the structure provided in \`schema.sql\`

</details>

<details>
<summary><strong style="font-size: 1.3em;"> Environment Configuration </strong></summary>

Create a `.env` file in the root of the project with the following:
```env
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=time_tracker
DB_PORT=3306
```

</details>

<details>
<summary><strong style="font-size: 1.3em;"> Run the App </strong></summary>

```bash
python src/WebUI.py
```

Visit the app in your browser at:
`http://localhost:5000`

</details>

## 🚧 Project Status

This project is actively being developed as a team MVP.  
Next planned features:
- Role-based login/auth
- In-browser start/stop time tracking
- Project and employee CRUD functionality for admins and managers



## 🐛 Known Bugs

- No error handling for failed DB connections (MVP build)
- Time report filters not yet fully implemented



## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
