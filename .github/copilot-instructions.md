# AI Rules for CsvVisualizer

This project is a simple web application that allows users to generate basic data visualizations from CSV files. 
It is built using Python: Flask, Pandas, Matplotlib and Jinja2.

## BACKEND

### Guidelines for PYTHON

- Always use type hints when functions and methods are defined.

- For classes, always add docstrings. The docstrings must follow below format (exclude short_description tags):
```
"""
<short_description>
Brief explanation of the class.
</short_description>
"""
```

- For functions and methods, always add docstrings. The docstrings must follow below format (exclude short_description tags):
```
"""
<short_description>
Brief explanation of the class/function/method.
</short_description>
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

#### FLASK

- Flask version used in this project is 3.1.2.

- Flask-Login version used in this project is 0.6.3.

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

## DEVOPS

### Guidelines for CI/CD

#### GITHUB_ACTIONS

- Extract common steps into composite actions in separate files.

### Guidelines for testing

#### PYTEST

- pytest version used in this project is 8.4.2.