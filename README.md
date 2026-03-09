📚 LibSys-AviNav
Smart AI-Powered Library Management System

LibSys-AviNav is a modern AI-powered Library Management System designed to simplify book management, student records, and library operations through a clean dashboard and intelligent automation.

The system provides QR-based identity cards, barcode-based book issuing, AI book recommendations, and real-time analytics to streamline library workflows.

Built with Flask + SQLite + Modern UI Dashboard, it delivers a powerful yet lightweight library management experience.

🚀 Features
📊 Admin Dashboard

Modern analytics dashboard

Library activity statistics

Book issuing trends visualization

Department borrowing insights

📚 Book Management

Add / update / delete books

Track available and issued books

Barcode integration for quick scanning

👨‍🎓 Student Management

Add and manage students

Generate digital student identity cards

QR code integration for student identification

📖 Book Issue & Return

Fast book issuing system

Barcode-based book identification

Automatic overdue detection

Fine calculation system

🪪 Smart Identity Cards

Generate library identity cards

Embedded QR codes for quick access

Used for issuing and returning books

📌 Reservation System

Students can reserve books

Track pending reservations

🤖 AI Book Recommendation

Intelligent book suggestions

Personalized reading recommendations

📈 Reports & Analytics

Monthly issue statistics

Department borrowing analysis

Library performance insights

🖥️ Tech Stack
Technology	Usage
Python	Backend logic
Flask	Web framework
SQLite	Lightweight database
HTML5 / CSS3 / JavaScript	Frontend
Chart.js	Data visualization
QR Code Generator	Identity cards
Barcode System	Book issue scanning
📂 Project Structure
LibSys-AviNav
│
├── app.py
├── database.db
├── requirements.txt
│
├── templates
│   ├── admin
│   ├── auth
│   ├── student
│   └── public
│
├── static
│   ├── css
│   ├── js
│   ├── images
│
└── README.md
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/abhinav20-pixel/LibSys-AviNav.git
cd LibSys-AviNav
2️⃣ Install Dependencies

Create a virtual environment (recommended)

python -m venv venv

Activate it

Windows

venv\Scripts\activate

Linux / Mac

source venv/bin/activate

Install required libraries

pip install -r requirements.txt
3️⃣ Run the Application
python app.py

Server will start at

http://127.0.0.1:5000
🔐 Default Login Credentials
Admin Access
URL:
http://127.0.0.1:5000/auth/login

Username: admin
Password: admin123
Student Access

After creating a student in the admin panel:

Username: Roll Number
Password: Roll Number
🧪 Testing the System
Admin Flow

Login as Admin

Add students in Students section

Add books in Books section

Generate Identity Card

Issue books using QR Code or Barcode

Return books and check fine calculation

Student Flow

Visit homepage

Explore library catalog

Search books using live filter

Reserve available books

Login using roll number

Track issued books and reservations

📸 Dashboard Preview

Admin dashboard includes:

Total books

Total students

Issued books

Overdue books

Monthly issue chart

Department borrowing chart

🌟 Future Improvements

Face recognition entry system

Email notifications

Mobile responsive student portal

Online book request system

Advanced AI recommendation engine

👨‍💻 Author

Abhinav (AviNav)
GitHub:
https://github.com/abhinav20-pixel

📸 Screenshots
🧭 Admin Dashboard
<img width="1919" height="1199" alt="Dashboard" src="https://github.com/user-attachments/assets/b64f8ff6-63ba-4094-9ccc-3f9f44dad6b1" />

📚 Books Management Page
<img width="1919" height="1199" alt="book issue" src="https://github.com/user-attachments/assets/8502d320-f1ae-4057-8d4d-b021a896a580" />

👨‍🎓 Students Management Page
<img width="1919" height="1199" alt="students" src="https://github.com/user-attachments/assets/b792705c-5cbd-48a6-97f9-c82c744ecbd9" />

📖 Issue Books Page
<img width="1919" height="1199" alt="issue page" src="https://github.com/user-attachments/assets/657eb4ab-4286-4421-baf0-120431e2f89b" />

🔎 Explore Library Page
<img width="1919" height="1199" alt="explore page" src="https://github.com/user-attachments/assets/3e25498d-405a-4824-9887-d66c45ecb297" />




⭐ Support

If you like this project, please ⭐ the repository.

GitHub Description (use this)
LibSys-AviNav — A modern AI-powered Library Management System built with Flask, SQLite, and a clean analytics dashboard. Features include QR-based student identity cards, barcode book issuing, AI recommendations, reservation system, and real-time library analytics.
GitHub Topics (add these)
library-management
flask
python
sqlite
ai-recommendation
barcode-scanner
qr-code
admin-dashboard
library-system
