# AI Rules for CsvVisualizer

This project is a simple web application that allows users to generate basic data visualizations from CSV files. 
It is built using Python: Flask, Pandas, Matplotlib and Jinja2.

## PROJECT STRUCTURE

When introducing changes to the project, always follow the directory structure below:

app/
├── __init__.py
├── auth/
├── main/
├── services/
├── static/
└── templates/
instance/

When modifying the directory structure, always update this section.

## BACKEND

### Guidelines for PYTHON

- Always use type hints when functions and methods are defined.

- For classes, always add docstrings. The docstrings must follow below format:
```
"""
Brief explanation of the class.
"""
```

- For functions and methods, always add docstrings. The docstrings must follow below format:
```
"""
Brief explanation of the class/function/method.
Args:
    <arg_name> (<arg_type>): <description>
    ...
Returns:
    <return_type>: <description>
"""
```

- Follow PEP 8 style guidelines for Python code. Key points include:
  1. Use 4 spaces per indentation level.
  2. Limit all lines to a maximum of 79 characters.
  3. Use blank lines to separate top-level function and class definitions.
  4. Use spaces around operators and after commas, but not directly inside parentheses, brackets, or braces.

- When importing modules, follow the PEP 8 guidelines for imports:
  1. Standard library imports.
  2. Related third party imports.
  3. Local application/library specific imports.
  You should put a blank line between each group of imports.

- When naming variables, functions, classes, and methods, follow the PEP 8 naming conventions:
  1. Use lowercase_with_underscores for functions and variable names.
  2. Use CapitalizedWords for class names.
  3. Use UPPERCASE_WITH_UNDERSCORES for constants.

- Each time you create or update a file, use black package to format the code in line with PEP 8 guidelines. Do this by executing the command black {source_file_or_directory}.

- Python version used in this project is 3.13.0.

- pip version used in this project is 24.2.

- To deal with confidential information, use python-dotenv package to load environment variables from a .env file. python-dotenv version used in this project is 1.1.1.

- To deal with dependencies, use existing virtual environment - csvviz - and requirements.txt file.

- Before coding, always make sure to activate existing virtual environment - csvviz - and deactivate it after work is completed.

#### FLASK

- Flask version used in this project is 3.1.2.

- Flask-Login version used in this project is 0.6.3.

- Use application factory pattern to create Flask application instance: goal is to make the testing easier.

- Use blueprints to organize the application structure into modules.

- Centralize configuration in a config.py file.

- Implement user feedback using Flask's flash() messaging system. 

- Reflect the distinction between authenticated and unauthenticated users in the application.

#### PANDAS

- pandas version used in this project is 2.3.3.

- Follow method chaining pattern when interacting with pandas DataFrames.

- During pandas DataFrame creation, always use appropriate data types for each column to optimize memory consumption.

- Instead of using loops to iterate over DataFrame rows, utilize pandas vectorized operations for better performance.

#### MATPLOTLIB

- matplotlib version used in this project is 3.10.7.

- During chart creation, use grey as the base color for bars on bar charts, lines on line charts and dots. on scatter plots. Then, use different, single color only to highlight data points which seem the most important. An example of such data point would be the highest value in the dataset coming from user-uploaded CSV file.

- Do not use 3D charts.

- Make sure axis scales are consistent.

- Always add labels to axes and a title to the chart. The title should be derived from CSV file's name.

- The charts generated in this project are static.

## FRONTEND

### Guidelines for JINJA2

- Jinja2 version used in this project is 3.1.6.

- Create a base.html template containing the common HTML structure to support template inheritance.

- Use url_for() and never hardcode URLs in the templates.

- Use Jinja2 control structures like {% if %} to dynamically generate content.

## DEVOPS

### Guidelines for CI/CD

#### GITHUB_ACTIONS

- Extract common steps into composite actions in separate files.

- Cache the dependencies using cache option in actions/setup-python action.

- Use single workflow file for the entire project and store it in .github/workflows directory. Name the workflow file python-csvviz-app.yml.

- The workflow must contain 2 jobs at minimum: build and test.

- build job's steps should use Flake8 for linting and Mypy for type checking.

- test job must depend on build job. Its steps will be based on pytest.

- Use ubuntu-latest as the runner for each job.

- Install dependencies from requirements.txt file using pip.

### Guidelines for testing

#### PYTEST

- pytest version used in this project is 8.4.2.

- Each test case's name must start with test_.

- Each module containing test cases must be created in CSVVIZ\csv-visualizer\tests.

- Use fixtures to avoid code duplication and place them in conftest.py file to enable sharing across multiple test modules.

- Use markers to categorize tests.