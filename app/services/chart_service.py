"""
Contains the business logic for chart generation.
"""
import os
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from flask import current_app


def create_chart(
    file_path: str, x_axis: str, y_axis: str, chart_type: str
) -> str | None:
    """
    Generates a chart from a CSV file and saves it as a PNG image.

    Args:
        file_path (str): The path to the CSV file.
        x_axis (str): The column to use for the X-axis.
        y_axis (str): The column to use for the Y-axis.
        chart_type (str): The type of chart to generate ('bar', 'line',
                          'scatter').

    Returns:
        str | None: The filename of the generated chart, or None on failure.
    """
    try:
        df = pd.read_csv(file_path)

        # Ensure the selected columns exist
        if x_axis not in df.columns or y_axis not in df.columns:
            return None

        plt.figure(figsize=(10, 6))

        # Highlight the max value
        max_val_index = df[y_axis].idxmax()
        colors = ["grey"] * len(df)
        colors[max_val_index] = "red"

        if chart_type == "bar":
            plt.bar(df[x_axis], df[y_axis], color=colors)
        elif chart_type == "line":
            plt.plot(df[x_axis], df[y_axis], color="grey")
            plt.scatter(
                df[x_axis][max_val_index],
                df[y_axis][max_val_index],
                color="red",
                zorder=5,
            )
        elif chart_type == "scatter":
            plt.scatter(df[x_axis], df[y_axis], color=colors)
        else:
            return None

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

        return chart_filename
    except Exception:
        return None
