"""
Unit tests for py4csr.plotting.plot_result module.

Tests PlotResult and PlotCollection classes.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from pathlib import Path

from py4csr.plotting.plot_result import PlotResult, PlotCollection


class TestPlotResultInit:
    """Test PlotResult initialization."""

    def test_basic_initialization(self):
        """Test basic PlotResult initialization."""
        fig, ax = plt.subplots()
        metadata = {"plot_type": "boxplot", "title": "Test Plot"}

        result = PlotResult(figure=fig, metadata=metadata)

        assert result.figure is not None
        assert result.metadata["plot_type"] == "boxplot"
        assert isinstance(result.validation_results, dict)
        assert isinstance(result.file_paths, dict)
        plt.close(fig)

    def test_initialization_with_validation(self):
        """Test initialization with validation results."""
        fig, ax = plt.subplots()
        metadata = {"plot_type": "lineplot"}
        validation = {"passed": True, "warnings": []}

        result = PlotResult(
            figure=fig, metadata=metadata, validation_results=validation
        )

        assert result.validation_results["passed"] is True
        plt.close(fig)


class TestPlotResultSave:
    """Test PlotResult save method."""

    def test_save_default_formats(self, temp_output_dir):
        """Test saving with default formats."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "test_plot"

        saved_files = result.save(output_path)

        assert "png" in saved_files
        assert "pdf" in saved_files
        assert Path(saved_files["png"]).exists()
        assert Path(saved_files["pdf"]).exists()
        plt.close(fig)

    def test_save_custom_formats(self, temp_output_dir):
        """Test saving with custom formats."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "test_plot"

        saved_files = result.save(output_path, formats=["png", "svg"])

        assert "png" in saved_files
        assert "svg" in saved_files
        assert "pdf" not in saved_files
        plt.close(fig)

    def test_save_with_custom_dpi(self, temp_output_dir):
        """Test saving with custom DPI."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "test_plot"

        saved_files = result.save(output_path, formats=["png"], dpi=150)

        assert Path(saved_files["png"]).exists()
        plt.close(fig)

    def test_save_creates_directory(self, temp_output_dir):
        """Test that save creates directory if it doesn't exist."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "subdir" / "test_plot"

        saved_files = result.save(output_path, formats=["png"])

        assert Path(saved_files["png"]).exists()
        plt.close(fig)


class TestPlotResultMethods:
    """Test PlotResult methods."""

    def test_get_metadata(self):
        """Test get_metadata method."""
        fig, ax = plt.subplots()
        metadata = {"plot_type": "boxplot", "title": "Test Plot"}

        result = PlotResult(figure=fig, metadata=metadata)
        retrieved_metadata = result.get_metadata()

        assert retrieved_metadata["plot_type"] == "boxplot"
        assert retrieved_metadata["title"] == "Test Plot"
        # Should be a copy
        retrieved_metadata["new_key"] = "new_value"
        assert "new_key" not in result.metadata
        plt.close(fig)

    def test_get_file_summary_no_files(self):
        """Test get_file_summary with no saved files."""
        fig, ax = plt.subplots()
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        summary = result.get_file_summary()

        assert summary["total_files"] == 0
        assert summary["total_size_mb"] == 0
        plt.close(fig)

    def test_get_file_summary_with_files(self, temp_output_dir):
        """Test get_file_summary with saved files."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "test_plot"
        result.save(output_path, formats=["png"])

        summary = result.get_file_summary()

        assert summary["total_files"] == 1
        assert summary["total_size_mb"] > 0
        assert "png" in summary["files"]
        assert summary["files"]["png"]["exists"] is True
        plt.close(fig)

    def test_close(self):
        """Test close method."""
        fig, ax = plt.subplots()
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        fig_num = fig.number

        result.close()

        # Figure should be closed
        assert fig_num not in plt.get_fignums()


class TestPlotCollectionInit:
    """Test PlotCollection initialization."""

    def test_basic_initialization(self):
        """Test basic PlotCollection initialization."""
        collection = PlotCollection()

        assert isinstance(collection.plots, dict)
        assert len(collection.plots) == 0
        assert collection.metadata["total_plots"] == 0

    def test_add_plot(self):
        """Test adding plot to collection."""
        collection = PlotCollection()

        fig, ax = plt.subplots()
        metadata = {"plot_type": "boxplot"}
        plot_result = PlotResult(figure=fig, metadata=metadata)

        collection.add_plot("demographics", plot_result)

        assert "demographics" in collection.plots
        assert collection.metadata["total_plots"] == 1
        plt.close(fig)

    def test_add_multiple_plots(self):
        """Test adding multiple plots."""
        collection = PlotCollection()

        for i in range(3):
            fig, ax = plt.subplots()
            metadata = {"plot_type": f"plot_{i}"}
            plot_result = PlotResult(figure=fig, metadata=metadata)
            collection.add_plot(f"plot_{i}", plot_result)

        assert len(collection.plots) == 3
        assert collection.metadata["total_plots"] == 3

        # Clean up
        for plot in collection.plots.values():
            plt.close(plot.figure)


class TestPlotCollectionMethods:
    """Test PlotCollection methods."""

    def test_get_plot(self):
        """Test getting plot from collection."""
        collection = PlotCollection()

        fig, ax = plt.subplots()
        metadata = {"plot_type": "boxplot"}
        plot_result = PlotResult(figure=fig, metadata=metadata)
        collection.add_plot("demographics", plot_result)

        retrieved = collection.get_plot("demographics")

        assert retrieved is plot_result
        plt.close(fig)

    def test_get_plot_nonexistent(self):
        """Test getting nonexistent plot."""
        collection = PlotCollection()

        result = collection.get_plot("nonexistent")

        assert result is None

    def test_save_all(self, temp_output_dir):
        """Test saving all plots."""
        collection = PlotCollection()

        for i in range(2):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            metadata = {"plot_type": f"plot_{i}"}
            plot_result = PlotResult(figure=fig, metadata=metadata)
            collection.add_plot(f"plot_{i}", plot_result)

        saved_files = collection.save_all(temp_output_dir, formats=["png"])

        assert len(saved_files) == 2
        assert "plot_0" in saved_files
        assert "plot_1" in saved_files

        # Clean up
        for plot in collection.plots.values():
            plt.close(plot.figure)

    def test_close_all(self):
        """Test closing all plots."""
        collection = PlotCollection()

        fig_nums = []
        for i in range(3):
            fig, ax = plt.subplots()
            fig_nums.append(fig.number)
            metadata = {"plot_type": f"plot_{i}"}
            plot_result = PlotResult(figure=fig, metadata=metadata)
            collection.add_plot(f"plot_{i}", plot_result)

        collection.close_all()

        # All figures should be closed
        for fig_num in fig_nums:
            assert fig_num not in plt.get_fignums()

    def test_get_summary(self, temp_output_dir):
        """Test getting collection summary."""
        collection = PlotCollection()

        for i in range(2):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            metadata = {"plot_type": f"plot_{i}"}
            plot_result = PlotResult(figure=fig, metadata=metadata)
            collection.add_plot(f"plot_{i}", plot_result)

        # Save one plot
        collection.plots["plot_0"].save(
            temp_output_dir / "plot_0", formats=["png"]
        )

        summary = collection.get_summary()

        assert summary["total_plots"] == 2
        assert summary["total_files"] == 1
        assert "creation_time" in summary

        # Clean up
        for plot in collection.plots.values():
            plt.close(plot.figure)


class TestPlotResultEdgeCases:
    """Test edge cases."""

    def test_empty_metadata(self):
        """Test with empty metadata."""
        fig, ax = plt.subplots()
        metadata = {}

        result = PlotResult(figure=fig, metadata=metadata)

        assert isinstance(result.metadata, dict)
        plt.close(fig)

    def test_save_single_format(self, temp_output_dir):
        """Test saving single format."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        metadata = {"plot_type": "lineplot"}

        result = PlotResult(figure=fig, metadata=metadata)
        output_path = temp_output_dir / "test_plot"

        saved_files = result.save(output_path, formats=["png"])

        assert len(saved_files) == 1
        assert "png" in saved_files
        plt.close(fig)

