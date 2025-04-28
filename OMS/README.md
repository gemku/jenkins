# Cafe Order System

## Overview
The Cafe Order System is a web application designed to manage cafe orders efficiently. It allows users to view the menu, place orders, and generate receipts. The application is built using Flask, a lightweight web framework for Python, and utilizes Bootstrap for responsive design.

## Project Structure
```
OMS
├── templates
│   └── receipt.html       # HTML template for the receipt page
├── static
│   ├── style.css          # Custom CSS styles for the application
│   └── script.js          # JavaScript for client-side interactivity
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── Dockerfile             # Instructions to build the Docker image
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd OMS
   ```

2. **Install Dependencies**
   It is recommended to use a virtual environment. You can create one using:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   Start the Flask application:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Docker Instructions

To build and run the Docker container, use the following commands:

1. **Build the Docker Image**
   ```bash
   docker build -t cafe-order-system .
   ```

2. **Run the Docker Container**
   ```bash
   docker run -p 5000:5000 cafe-order-system
   ```

The application will be available at `http://localhost:5000`.

## Usage
- Navigate to the home page to view the menu.
- Place orders by selecting items from the menu.
- View and download receipts for completed orders.

