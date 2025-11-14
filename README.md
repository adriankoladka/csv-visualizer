# CsvVisualizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple web application for generating basic data visualizations from CSV files. This tool allows users to upload a CSV, select data for the axes, choose a chart type, and download the resulting visualization as a PNG image.

## Table of Contents

- [Project Description](#project-description)
- [Tech Stack](#tech-stack)
- [Getting Started Locally](#getting-started-locally)
- [Available Scripts](#available-scripts)
- [Project Scope](#project-scope)
- [Project Status](#project-status)
- [License](#license)

## Project Description

The CsvVisualizer is a Minimum Viable Product (MVP) designed to provide a simple, web-based interface for non-technical users to generate basic data visualizations from CSV files. Users can upload one or more CSV files, manage them in a session-based list, and select a file to generate a chart. For a selected file, users can choose data columns for the X and Y axes, pick a chart type (Bar, Line, or Scatter), and generate a static chart image. All uploaded data is processed within the user's session and is not stored persistently. The application focuses on simplicity and speed, allowing users to quickly create and download visualizations for presentations or reports without needing to use complex software.

## Tech Stack

The project is built with the following technologies:

- **Backend:**
  - Python 3.13
  - Flask (Web Framework)
  - Pandas (Data Handling)
  - Matplotlib (Data Visualization)
  - Flask-Login (User Authentication)
  - python-dotenv (Environment Variables)
- **Frontend:**
  - Jinja2 (Templating)
- **Testing & CI/CD:**
  - Pytest
  - GitHub Actions

## Getting Started Locally

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3.13 or later
- pip

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/adriankoladka/csv-visualizer.git
    cd csv-visualizer
    ```

2.  **Create and activate a virtual environment:**
    - On Windows:
      ```sh
      python -m venv csvviz
      .\csvviz\Scripts\activate
      ```
    - On macOS/Linux:
      ```sh
      python3 -m venv csvviz
      source csvviz/bin/activate
      ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add the necessary configuration (e.g., `SECRET_KEY`).
    ```
    FLASK_APP=csvviz
    FLASK_ENV=development
    SECRET_KEY='your_super_secret_key'
    ```

5.  **Run the application:**
    ```sh
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Available Scripts

- **Run the application (development mode):**
  ```sh
  flask run
  ```
- **Run tests:**
  ```sh
  pytest
  ```

## Project Scope

### In Scope

-   **File Upload:** Upload CSV files up to 1MB with UTF-8 encoding and headers in the first row.
-   **User Authentication:** Secure login system for user access.
-   **Chart Configuration:** Select columns for X and Y axes and choose a chart type (Bar, Line, or Scatter).
-   **Visualization Generation:** Generate static chart images from the data.
-   **Chart Download:** Download the generated chart as a PNG file.
-   **Session-Based Data Management:** View, update, and delete uploaded files within the current session. Data is deleted upon logout.

### Out of Scope

-   Support for file formats other than CSV (e.g., JSON, XLSX).
-   Interactive visualizations (e.g., tooltips, zooming).
-   Advanced chart types (e.g., heatmaps, 3D plots).
-   Data transformation or cleaning capabilities.
-   Persistent storage of user data or files across sessions.

## Project Status

**In Development**

This project is currently in the development phase as an MVP.

## License

This project is licensed under the MIT License. 
See the [LICENSE](https://opensource.org/licenses/MIT) file for details.
