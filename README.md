# 🖥️ IT Asset Management System

A CLI-based IT asset management system designed for hospital / clinic environments.  
Built with **Pure Python** using an **MVC architecture**.

---

## 🏗️ Architecture

```text
it-asset-management/
├── app/
│   ├── models/          → Data structures (Asset class)
│   ├── services/        → Business logic (CRUD, filtering, export)
│   └── utils/           → Helper functions (input validation)
├── cli/
│   └── main.py          → Terminal interface
├── tests/               → Unit tests (pytest)
├── config.py            → Centralized configuration
└── seed_data.py         → Sample data
```

---

## ⚙️ Tech Stack

- **Language**  : Python 3.8+
- **Storage**   : SQLite (via the built-in `sqlite3` library)
- **Pattern**   : MVC + Service Layer
- **Testing**   : pytest

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/USERNAME/it-asset-management.git
cd it-asset-management
```

### 2. Install dependencies

```bash
pip install pytest
```

### 3. Seed sample data (Optional)

```bash
python seed_data.py
```

### 4. Run the application

```bash
python cli/main.py
```

### 5. Run tests

```bash
pytest tests/ -v
```

---

## ✅ Features

### CRUD Operations

- Add assets using a step-by-step input wizard
- View all assets in a table format
- Search assets by keyword
- Edit assets — all fields are optional
- Delete assets with confirmation

### Filtering & Monitoring

- Filter by status or location — supports multi-select
- Automatic summary statistics on the main menu
- Old asset reminders — define your own year threshold
- Statistics dashboard

### Import & Export

- Export to CSV — ready to open in Excel
- Import from CSV — duplicate and required-column validation
- Automatic backup whenever data changes

### System Features

- Activity logging with timestamps
- Auto-backup — stores the latest 10 backups

---

## 🧠 Python Concepts Used

`OOP` · `MVC Architecture` · `Type Hints` · `pytest` ·  
`try/except` · `list comprehension` · `collections.Counter` ·  
`datetime` · `csv` · `json` · `shutil` · `os.path`

---

## 🗺️ Roadmap

- [x] Full-featured CLI
- [x] MVC architecture
- [x] Unit testing with pytest
- [x] Migration to SQLite
- [x] Web interface using Flask
- [ ] Deployment to the hospital local network
- [ ] User login & role management

---

## 👨‍💻 Author

Created for hospital IT asset management needs.