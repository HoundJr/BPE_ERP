# CNC ERP Web App (Flask)

A lightweight ERP system for small CNC machine shops.

## Setup Instructions

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the database:

```bash
python init_db.py
```

4. Run the app:

```bash
python app.py
```

Access it at http://localhost:5000
