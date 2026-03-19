# Blog

A blogging tool for my own use built from scratch using Python and FastAPI. 

## Features

* **Server-Side Rendering (SSR):** Uses Jinja2 templates to inject Python data directly into the HTML.
* **Local File Database:** Articles are stored locally as `.json` files.
* **CRUD Operations:** Create, Read, Update, and Delete journal entries.
* **Session Authentication:** Cookie-based security system to protect the admin dashboard and destructive routes.
* **Custom UI:** "Comic-book" style aesthetic using CSS flexbox and a master `base.html` template.

## Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** HTML5, CSS3, Jinja2
* **Storage:** JSON (File System)
* **Security:** `python-dotenv`, HTTP Cookies

---

## Quick Start & Installation

Follow these steps to get the local server running on your machine.

### 1. Clone the repository
```bash
git clone https://github.com/Bunz42/blog.git
cd blog
```

### 2. Set up the Virtual Environment
It is highly recommended to run this project in an isolated Python environment.
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Credentials
Create a file named `.env` in the root directory of the project. This file is gitignored to keep your login safe. Add your desired credentials:
```env
ADMIN_USERNAME=your_chosen_username
ADMIN_PASSWORD=your_chosen_password
```

### 5. Run the Application
Start the FastAPI development server:
```bash
fastapi dev main.py
```

The application will be live at: `http://127.0.0.1:8000/home`

---

## Accessing the Dashboard

To write or edit entries:
1. Click **Admin Login** in the top right corner of the home page.
2. Enter the credentials you set in your `.env` file.
3. You will be granted a session cookie and redirected to the authoring dashboard.