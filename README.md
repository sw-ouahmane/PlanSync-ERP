# PlanSync-ERP

PlanSync-ERP is a web-based application designed to manage tasks and operations, particularly for logistics, shipping management, or warehouse operations. The application offers features for task assignment, user management, and statistics tracking to improve workflow efficiency. It provides an organized platform to track tasks, resources, and user activities in real-time.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **User Authentication:** Secure login, logout, and session management.
- **Profile Management:** Display personal information such as profile image, contact details, and user matricule.
- **Task Management:** Add, view, and manage tasks, with fields like shift, poste, navire, etc.
- **Task Validation:** Admins can validate tasks, leave remarks, and update task statuses.
- **Role-Based Access:** Admins have specific functionality to manage users, add/delete admins, and view statistics.
- **Responsive Design:** Built with Bootstrap to ensure a smooth experience across devices.
- **Admin Dashboard:** Manage users and tasks, add/delete users, and change admin passwords.

---

## Installation

### Prerequisites

- Python 3.x
- Flask
- Virtual environment (`venv`)
- SQLAlchemy (for database management)
- Bootstrap (for frontend styling)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sw-ouahmane/PlanSync-ERP.git
   cd PlanSync-ERP
