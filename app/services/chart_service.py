"""
Contains the business logic for chart generation.
"""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from flask import current_app  # noqa: E402


def create_chart(
    file_path: str, x_axis: str, y_axis: str, chart_type: str
) -> tuple[str | None, str | None]:
    """
    Generates a chart from a CSV file and saves it as a PNG image.

    Args:
        file_path (str): The path to the CSV file.
        x_axis (str): The column to use for the X-axis.
        y_axis (str): The column to use for the Y-axis.
        chart_type (str): The type of chart to generate ('bar', 'line',
                          'scatter').

    Returns:
        tuple[str | None, str | None]: A tuple of (filename, error_message).
            Returns (filename, None) on success, (None, error_message) on failure.
    """
    try:
        df = pd.read_csv(file_path)

        # Check if file is empty
        if df.empty:
            return None, "The CSV file is empty."

        # Ensure the selected columns exist
        if x_axis not in df.columns:
            return (
                None,
                f"Column '{x_axis}' not found in the CSV file.",
            )
        if y_axis not in df.columns:
            return (
                None,
                f"Column '{y_axis}' not found in the CSV file.",
            )

        # Check if Y-axis contains numeric data
        if not pd.api.types.is_numeric_dtype(df[y_axis]):
            return (
                None,
                f"Column '{y_axis}' must contain numeric data for charting.",
            )

        # Remove rows with NaN values in selected columns
        df_clean = df[[x_axis, y_axis]].dropna()
        if df_clean.empty:
            return None, "No valid data found after removing missing values."

        plt.figure(figsize=(10, 6))

        # Highlight the max value
        max_val_index = df_clean[y_axis].idxmax()
        colors = ["grey"] * len(df_clean)
        colors[list(df_clean.index).index(max_val_index)] = "red"

        if chart_type == "bar":
            plt.bar(df_clean[x_axis], df_clean[y_axis], color=colors)
        elif chart_type == "line":
            plt.plot(df_clean[x_axis], df_clean[y_axis], color="grey")
            plt.scatter(
                df_clean[x_axis].iloc[
                    list(df_clean.index).index(max_val_index)
                ],
                df_clean[y_axis].iloc[
                    list(df_clean.index).index(max_val_index)
                ],
                color="red",
                zorder=5,
            )
        elif chart_type == "scatter":
            plt.scatter(df_clean[x_axis], df_clean[y_axis], color=colors)
        else:
            return None, f"Invalid chart type: {chart_type}"

        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.title(f"Chart from {os.path.basename(file_path)}")
        plt.grid(True)
        plt.tight_layout()

        # Save the chart to the instance/charts directory
        charts_dir = Path(current_app.instance_path) / "charts"
        os.makedirs(charts_dir, exist_ok=True)
        chart_filename = f"{Path(file_path).stem}_{chart_type}.png"
        chart_path = charts_dir / chart_filename
        plt.savefig(chart_path)
        plt.close()

        return chart_filename, None
    except pd.errors.EmptyDataError:
        return None, "The CSV file is empty or invalid."
    except ValueError as e:
        return None, f"Data error: {str(e)}"
    except Exception as e:
        return None, f"Could not generate chart: {str(e)}"
