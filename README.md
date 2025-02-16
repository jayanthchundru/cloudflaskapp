# Flask Registration & Login System

This is a simple Flask web application that allows users to register, login, and upload a file. The application stores user details in an SQLite database and provides authentication features.

## Features
- User Registration (Username, Password, First Name, Last Name, Email, Address)
- User Login & Logout
- Profile Page displaying user details
- File Upload with Word Count Feature
- Secure password storage using hashing

## Prerequisites
- Ubuntu Server (24.04 LTS recommended)
- Python 3.12 or later
- Flask framework
- SQLite3
- Apache2 with `mod_wsgi`

## Installation & Setup
### 1. Launch an EC2 Instance (Ubuntu 24.04 LTS)
Follow AWS EC2 instance creation steps and SSH into your server.

### 2. Install Required Dependencies
```bash
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip python3-flask sqlite3 -y
```

### 3. Set Up the Flask Application
```bash
cd /var/www/html/
sudo mkdir flaskapp
cd flaskapp
```

Clone your project or create the necessary files:
```bash
sudo touch flaskapp.py
sudo touch flaskapp.wsgi
sudo mkdir templates static uploads
```

### 4. Create a Virtual Environment (Optional but Recommended)
```bash
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install flask werkzeug
```

### 5. Set Up Database
```bash
sqlite3 users.db "CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT,
    lastname TEXT,
    email TEXT UNIQUE NOT NULL,
    address TEXT
);"
```

### 6. Configure File Upload Permissions
```bash
sudo chown -R www-data:www-data /var/www/html/flaskapp/uploads
sudo chmod -R 775 /var/www/html/flaskapp/uploads
```

### 7. Configure Apache for Flask
Create the WSGI file (`flaskapp.wsgi`):
```python
import sys
sys.path.insert(0, '/var/www/html/flaskapp')
from flaskapp import app as application
```

Edit the Apache configuration:
```bash
sudo nano /etc/apache2/sites-available/flaskapp.conf
```
Add:
```
<VirtualHost *:80>
    ServerName your-ec2-public-ip
    WSGIDaemonProcess flaskapp threads=5
    WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi
    <Directory /var/www/html/flaskapp>
        Require all granted
    </Directory>
    Alias /static /var/www/html/flaskapp/static
    <Directory /var/www/html/flaskapp/static>
        Require all granted
    </Directory>
</VirtualHost>
```
Enable the site and restart Apache:
```bash
sudo a2ensite flaskapp
sudo systemctl restart apache2
```

### 8. Run the Application (For Testing Locally)
```bash
python3 flaskapp.py
```
Visit `http://your-server-ip/` in your browser.

## Usage
1. **Registration**: Users sign up with a username, password, and other details.
2. **Login**: Users log in with their credentials.
3. **Profile Page**: Displays user details and allows file upload.
4. **File Upload**: Users can upload a `.txt` file and view the word count.
5. **Logout**: Users can log out and return to the login page.

## Troubleshooting
### Check Apache Logs for Errors
```bash
sudo tail -n 50 /var/log/apache2/error.log
```

### Database Locked Error
If you see `sqlite3.OperationalError: database is locked`, ensure connections are closed properly in `flaskapp.py`:
```python
finally:
    conn.close()
```

### Permission Denied for Uploads
If you get `PermissionError: [Errno 13] Permission denied: 'uploads'`, fix permissions:
```bash
sudo chown -R www-data:www-data /var/www/html/flaskapp/uploads
sudo chmod -R 775 /var/www/html/flaskapp/uploads
```

## Future Enhancements
- Add email verification
- Implement password reset functionality
- Improve UI with Bootstrap

## License
This project is open-source. Feel free to modify and improve it!

