# Simple C2 SSH

**Simple C2 SSH** is a lightweight command-and-control (C2) system designed to manage and interact with multiple SSH servers through a centralized web-based interface.
This project aims to simplify SSH management, monitoring, and automation for system administrators, red teamers, or anyone who requires centralized control over distributed servers.

---

## Features

* **Centralized SSH Management**
  Manage multiple SSH servers from a single web dashboard.

* **User Authentication**
  Simple login system to restrict unauthorized access.

* **Server Health Monitoring**
  Check availability and basic health of registered SSH servers.

* **Command Execution (Summon)**
  Send and execute commands across connected SSH servers from the web interface.

* **Logging System**
  Store logs of executed commands and server interactions in JSON format for auditing.

* **Editable Server List**
  Add, edit, and remove SSH servers through the UI.

* **Single Server Architecture**
  All logic (API, backend, and frontend) is contained within a single Python server for simplicity.

---

## Project Structure

```
.
├── app.py              # Main application entry point
├── config.py           # Configuration file (settings, secrets, etc.)
├── db.json             # Database file for storing SSH server information
├── logs.json           # Log file for executed commands and interactions
├── requirements.txt    # Python dependencies
└── templates/          # HTML templates for the web interface
    ├── dashboard.html  # Main dashboard view
    ├── edit_ssh.html   # Form to add/edit SSH server entries
    ├── health.html     # Server health monitoring page
    ├── login.html      # Authentication page
    └── summon.html     # Command execution page
```

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourname/simple-c2-ssh.git
   cd simple-c2-ssh
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**
   Edit `config.py` and adjust your preferences (such as secret keys, default users, etc.).

4. **Run the server**

   ```bash
   python3 app.py
   ```

5. **Access the dashboard**
   Open your browser and go to:

   ```
   http://127.0.0.1:5000
   ```

---

## Usage

* **Login** using the credentials defined in `config.py`.
* **Add SSH servers** via the **Edit SSH** menu. Information is stored in `db.json`.
* **Monitor health** of your registered servers in the **Health** section.
* **Execute commands** on one or more servers through the **Summon** page.
* **Review logs** of executed commands in `logs.json`.

---

## Notes

* This project is intended for **educational and administrative purposes** only.
* Do not use Simple C2 SSH for unauthorized access or malicious activities.
* Since all data is stored in JSON files (`db.json`, `logs.json`), it is recommended to secure the environment properly.

---

## Future Improvements

* Support for role-based access control (RBAC).
* Encrypted storage for SSH credentials.
* Real-time log streaming.
* API endpoints for external integration.
* Deployment with Docker for easier setup.

---

## License

This project is licensed under the MIT License.

