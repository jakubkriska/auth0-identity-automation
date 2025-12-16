# Auth0 Identity Automation Engine

## 🚀 Project Overview
This project demonstrates **Infrastructure as Code (IaC)** by automating user onboarding for an organization. 
It uses Python to parse HR data (CSV) and provisions users securely into an Auth0 cloud directory via the Management API.

## 🛠 Tech Stack
* **Language:** Python 3.10+
* **Identity Provider:** Auth0 (Okta)
* **Security:** OAuth2 (Client Credentials Flow), Environment Variables for secret management.

## ⚙️ Key Features
* [x] Automated parsing of bulk user data (`.csv`).
* [x] Secure API Authentication using `python-dotenv`.
* [x] Error handling for duplicate users.
* [x] Generates standardized metadata (Department, Job Title).

## 📸 Proof of Concept
<img width="1140" height="562" alt="Screenshot 2025-12-16 at 3 01 08 PM" src="https://github.com/user-attachments/assets/45d988e1-b8f8-4717-ac38-8d8699f8229d" />



## 📦 How to Run
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Auth0 credentials.
4. Run `python main.py`.
