# View Implementation Plan: base.html

## 1. Overview
This document outlines the implementation plan for the `base.html` template. This template serves as the foundational layout for all other views in the CsvVisualizer application. Its purpose is to provide a consistent HTML structure, header, and a mechanism for displaying global messages, ensuring a uniform look and feel across the entire application. It is not rendered directly but is extended by other templates like `login.html` and `dashboard.html`.

## 2. Key Components and Structure
This section details the static and dynamic parts of the template itself.
*   **HTML Boilerplate:** The template will define the standard `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` structure. The `<head>` will contain the character set, viewport settings, and the application title.
*   **Header:** A persistent `<header>` element will be present at the top of every page.
    *   It will contain an `<h1>` tag with the application title, "CsvVisualizer".
    *   It will include a conditional "Logout" link. This link will only be rendered if a user is authenticated (`current_user.is_authenticated` is `True`). The link will point to the `url_for('auth.logout')` endpoint.
*   **Flash Message Display:** A dedicated section within the `<main>` element will be responsible for rendering status messages from Flask's `flash()` system (e.g., "Invalid credentials", "File uploaded successfully").
    *   This will be implemented using a `with get_flashed_messages() as messages` block.
    *   If `messages` exist, it will render them in an unordered list (`<ul>`).
*   **Jinja2 Content Block:** The template will define the primary content area using `{% block content %}{% endblock %}`. This block acts as a placeholder that child templates (like `login.html` or `dashboard.html`) will override to inject their specific page content.

## 3. Dynamic Context
This section describes the global data or functions the template needs access to, which are provided by Flask and its extensions.
*   `current_user`: A global variable provided by the Flask-Login extension. It represents the currently logged-in user object, allowing the template to check `current_user.is_authenticated`.
*   `get_flashed_messages()`: A global function provided by Flask. It retrieves any messages that were added to the session using the `flash()` function in the backend logic.
*   `url_for()`: A global function provided by Flask to generate URLs for specific view functions, preventing the need to hardcode URLs in the template.

## 4. Child Template Contract
This section defines the rules that any child template extending `base.html` must follow to function correctly.
*   The child template **must** begin with the statement `{% extends "base.html" %}`.
*   The child template **must** place all of its main page content inside a `{% block content %}` block. Any content outside of this block will either be ignored or may break the page layout.
