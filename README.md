                                                 Homeless Prevention Web Application
                                                                        
Overview : 
The Homeless Prevention Web Application is a multi-user platform designed to assist homeless individuals by connecting them with donors and volunteers, while also providing admin
functionalities to manage the system. It offers an organized solution for identifying and responding to homelessness emergencies, gathering donations, and providing shelters. The application facilitates seamless interaction among individuals, guests, donors, and administrators through a secure backend and user-friendly interface.

Features :

1. User Types
    - Individual: Homeless individuals seeking shelter or help can log in and provide detailed personal
    information for assistance.
    - Guest: Volunteers or community members can report emergencies or help request details on
    behalf of homeless people.
    - Donator: Users willing to provide shelter or donate items for homeless individuals can log in and
    provide necessary details.
    - Admin: Administrators oversee all system interactions, verify requests, and manage shelters.
      
2. Authentication
    - Secure login system for different user types (Individual, Guest, Donator, Admin).
    - Admin privileges for managing users and donations.
      
3. Form Submission
    - Collect detailed data through structured forms for individuals, guests, and donators.
    - Emergency requests with descriptions, locations, and optional photo uploads.
      
4. Admin Dashboard
    - Manage individual user data.
    - Verify and respond to emergency requests.
    - Manage donation offers and shelter availability.
      
5. Security
    - Password hashing using industry-standard techniques for authentication.
    - Secure file uploads for donors and guests with validation.
      
6. Database
    - All user data is stored securely using a relational database.
    - The app uses SQLAlchemy ORM to handle database interactions.
      
Technologies Used
    - Backend: Flask (Python)
    - Database:MySQL
    - Frontend: HTML5, CSS3 (Bootstrap for styling)
    - Forms & Validation: Flask-WTF
    - Authentication: Flask-Login
    - File Uploads: Secure file upload functionality for donors and guests.
    
Setup and Installation

Prerequisites
    Ensure that you have the following installed:
    - Python 3.x
    - pip (Python package manager)
    
Step-by-Step Installation

1. Clone the repository:
git clone https://github.com/username/homeless-prevention-app.git
cd homeless-prevention-app

2. Install dependencies:
pip install -r requirements.txt

3. Configure the application:
- Modify config.py for database connection or change the SQLALCHEMY_DATABASE_URI to your preferred database.
  
4. Set up the database:
flask db init
flask db migrate
flask db upgrade

6. Run the application:
python app.py

8. Open your web browser and navigate to:
http://127.0.0.1:5000/

Project Structure
        /homeless_prevention_app
        /static
        /css
        styles.css
        /templates
        base.html
        index.html
        individual.html
        guest.html
        donator.html
        admin.html
        login.html
        /models
        __init__.py
        user.py
        request.py
        /forms.py
        /app.py
        /config.py
        /requirements.txt
        
API Routes

        | Route | Method | Description |
        |--------------------|--------|------------------------------------------------------|
        | / | GET | Homepage |
        | /individual_login | GET | Individual login form |
        | /submit_individual | POST | Submit individual form |
        | /guest_login | GET | Guest login form |
        | /submit_guest | POST | Submit guest form |
        | /donator_login | GET | Donator login form |
        | /submit_donator | POST | Submit donator form |
        | /admin_login | GET | Admin login page |
        | /manage_individual | GET | Admin management of individual users |
        | /verify_requests | GET | Admin verification of requests |
        | /emergency_requests| GET | Admin view of emergency requests |
        | /manage_shelters | GET | Admin management of shelter data |
        
Security Considerations

    - Password Security: All user passwords are hashed and stored securely using werkzeug.security.
    - Form Validation: Inputs are validated for correctness and security to avoid injection attacks.
    - File Uploads: User-uploaded files are checked for security and handled appropriately.
    
Future Enhancements

    - Role-Based Access Control: Further refine access controls based on user roles.
    - Notification System: Implement real-time notifications for admins to respond to emergencies faster.
    - Data Analytics: Integrate data analytics tools to track donation trends and optimize resource
    allocation.
    - Multi-Language Support: Add support for multiple languages to make the platform globally
    accessible.
    - Mobile Optimization: Ensure the platform is responsive and fully functional on mobile devices.
    
Contribution Guidelines

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a feature branch (git checkout -b feature/new-feature).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a new Pull Request.
  
Contact
If you have any questions or suggestions, feel free to reach out
