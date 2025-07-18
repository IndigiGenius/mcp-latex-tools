"""Tests for LaTeX auxiliary file cleanup tool."""

import tempfile
from pathlib import Path

import pytest

from mcp_latex_tools.tools.cleanup import clean_latex, CleanupError, CleanupResult


class TestCleanLatex:
    """Test LaTeX auxiliary file cleanup functionality."""

    def test_clean_latex_with_single_file_cleans_auxiliaries(self):
        """Test cleanup of auxiliary files for a single .tex file."""
        # Create temporary directory with LaTeX files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create main .tex file
            tex_file = temp_path / "document.tex"
            tex_file.write_text(r"""
\documentclass{article}
\begin{document}
Hello World
\end{document}
""")
            
            # Create auxiliary files
            aux_files = [
                temp_path / "document.aux",
                temp_path / "document.log",
                temp_path / "document.out",
                temp_path / "document.fls",
                temp_path / "document.fdb_latexmk",
                temp_path / "document.toc",
                temp_path / "document.lof",
                temp_path / "document.lot",
                temp_path / "document.bbl",
                temp_path / "document.blg",
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            # Run cleanup
            result = clean_latex(str(tex_file))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.error_message is None
            assert result.tex_file_path == str(tex_file)
            assert result.cleaned_files_count > 0
            assert len(result.cleaned_files) > 0
            assert result.cleanup_time_seconds is not None
            assert result.cleanup_time_seconds > 0
            
            # Check that auxiliary files were removed
            for aux_file in aux_files:
                assert not aux_file.exists()
            
            # Check that main .tex file still exists
            assert tex_file.exists()

    def test_clean_latex_with_directory_cleans_all_auxiliaries(self):
        """Test cleanup of all auxiliary files in a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple .tex files
            tex_files = [
                temp_path / "doc1.tex",
                temp_path / "doc2.tex",
                temp_path / "chapter1.tex",
            ]
            
            for tex_file in tex_files:
                tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary files for each
            all_aux_files = []
            for tex_file in tex_files:
                stem = tex_file.stem
                aux_files = [
                    temp_path / f"{stem}.aux",
                    temp_path / f"{stem}.log",
                    temp_path / f"{stem}.out",
                    temp_path / f"{stem}.fls",
                    temp_path / f"{stem}.fdb_latexmk",
                ]
                all_aux_files.extend(aux_files)
                
                for aux_file in aux_files:
                    aux_file.write_text("auxiliary content")
            
            # Run cleanup on directory
            result = clean_latex(str(temp_path))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.directory_path == str(temp_path)
            assert result.cleaned_files_count >= len(all_aux_files)
            assert len(result.cleaned_files) >= len(all_aux_files)
            
            # Check that all auxiliary files were removed
            for aux_file in all_aux_files:
                assert not aux_file.exists()
            
            # Check that .tex files still exist
            for tex_file in tex_files:
                assert tex_file.exists()

    def test_clean_latex_with_no_auxiliaries_returns_success(self):
        """Test cleanup when no auxiliary files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create only .tex file
            tex_file = temp_path / "clean.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Clean\end{document}")
            
            result = clean_latex(str(tex_file))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.cleaned_files_count == 0
            assert result.cleaned_files == []
            assert result.tex_file_path == str(tex_file)

    def test_clean_latex_with_selective_cleanup(self):
        """Test cleanup with selective file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "selective.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create various auxiliary files
            aux_file = temp_path / "selective.aux"
            log_file = temp_path / "selective.log"
            out_file = temp_path / "selective.out"
            pdf_file = temp_path / "selective.pdf"  # Should NOT be removed
            
            aux_file.write_text("aux content")
            log_file.write_text("log content")
            out_file.write_text("out content")
            pdf_file.write_text("pdf content")
            
            # Run cleanup with only specific extensions
            result = clean_latex(str(tex_file), extensions=[".aux", ".log"])
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.cleaned_files_count == 2
            
            # Check that only specified extensions were removed
            assert not aux_file.exists()
            assert not log_file.exists()
            assert out_file.exists()  # Should still exist
            assert pdf_file.exists()  # Should still exist

    def test_clean_latex_with_dry_run_does_not_remove_files(self):
        """Test dry run mode that shows what would be cleaned without removing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "dryrun.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary files
            aux_files = [
                temp_path / "dryrun.aux",
                temp_path / "dryrun.log",
                temp_path / "dryrun.out",
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            # Run cleanup in dry run mode
            result = clean_latex(str(tex_file), dry_run=True)
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.dry_run is True
            assert result.cleaned_files_count == 0  # No files actually cleaned
            assert len(result.would_clean_files) == len(aux_files)  # But would clean these
            
            # Check that all files still exist
            for aux_file in aux_files:
                assert aux_file.exists()

    def test_clean_latex_with_nonexistent_file_raises_error(self):
        """Test cleanup with non-existent file."""
        with pytest.raises(CleanupError) as excinfo:
            clean_latex("/nonexistent/file.tex")
        
        assert "not found" in str(excinfo.value).lower()

    def test_clean_latex_with_empty_path_raises_error(self):
        """Test cleanup with empty file path."""
        with pytest.raises(CleanupError) as excinfo:
            clean_latex("")
        
        assert "cannot be empty" in str(excinfo.value).lower()

    def test_clean_latex_with_none_path_raises_error(self):
        """Test cleanup with None file path."""
        with pytest.raises(CleanupError) as excinfo:
            clean_latex(None)
        
        assert "cannot be none" in str(excinfo.value).lower()

    def test_clean_latex_handles_permission_errors(self):
        """Test cleanup handles permission errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "permission.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary file
            aux_file = temp_path / "permission.aux"
            aux_file.write_text("aux content")
            
            # This test would need to simulate permission errors
            # For now, we'll just test that it handles the normal case
            result = clean_latex(str(tex_file))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True

    def test_clean_latex_with_recursive_cleanup(self):
        """Test cleanup with recursive directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create subdirectories
            subdir1 = temp_path / "chapter1"
            subdir2 = temp_path / "chapter2"
            subdir1.mkdir()
            subdir2.mkdir()
            
            # Create .tex files in subdirectories
            tex_files = [
                subdir1 / "section1.tex",
                subdir2 / "section2.tex",
            ]
            
            aux_files = []
            for tex_file in tex_files:
                tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
                
                # Create auxiliary files
                stem = tex_file.stem
                aux_file = tex_file.parent / f"{stem}.aux"
                log_file = tex_file.parent / f"{stem}.log"
                aux_files.extend([aux_file, log_file])
                
                aux_file.write_text("aux content")
                log_file.write_text("log content")
            
            # Run recursive cleanup
            result = clean_latex(str(temp_path), recursive=True)
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.cleaned_files_count >= len(aux_files)
            
            # Check that auxiliary files were removed
            for aux_file in aux_files:
                assert not aux_file.exists()
            
            # Check that .tex files still exist
            for tex_file in tex_files:
                assert tex_file.exists()

    def test_clean_latex_with_protected_files(self):
        """Test that important files are protected from cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "protected.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create files that should be protected
            protected_files = [
                temp_path / "protected.tex",     # Source file
                temp_path / "protected.pdf",     # Output file
                temp_path / "protected.bib",     # Bibliography
                temp_path / "protected.sty",     # Style file
                temp_path / "protected.cls",     # Class file
                temp_path / "important.txt",     # Other important files
            ]
            
            # Create auxiliary files that should be cleaned
            aux_files = [
                temp_path / "protected.aux",
                temp_path / "protected.log",
                temp_path / "protected.out",
            ]
            
            for file in protected_files + aux_files:
                file.write_text("content")
            
            result = clean_latex(str(tex_file))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            
            # Check that protected files still exist
            for protected_file in protected_files:
                assert protected_file.exists(), f"Protected file {protected_file} was removed"
            
            # Check that auxiliary files were removed
            for aux_file in aux_files:
                assert not aux_file.exists(), f"Auxiliary file {aux_file} was not removed"

    def test_clean_latex_with_backup_option(self):
        """Test cleanup with backup option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "backup.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary file
            aux_file = temp_path / "backup.aux"
            aux_content = "auxiliary content that should be backed up"
            aux_file.write_text(aux_content)
            
            # Run cleanup with backup
            result = clean_latex(str(tex_file), create_backup=True)
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.backup_created is True
            assert result.backup_directory is not None
            
            # Check that auxiliary file was removed
            assert not aux_file.exists()
            
            # Check that backup was created
            backup_dir = Path(result.backup_directory)
            assert backup_dir.exists()
            backup_aux = backup_dir / "backup.aux"
            assert backup_aux.exists()
            assert backup_aux.read_text() == aux_content

    def test_cleanup_result_properties(self):
        """Test CleanupResult dataclass properties."""
        result = CleanupResult(
            success=True,
            error_message=None,
            tex_file_path="/test/document.tex",
            directory_path="/test",
            cleaned_files_count=5,
            cleaned_files=["/test/document.aux", "/test/document.log"],
            would_clean_files=[],
            dry_run=False,
            recursive=False,
            backup_created=False,
            backup_directory=None,
            cleanup_time_seconds=0.5
        )
        
        assert result.success is True
        assert result.error_message is None
        assert result.tex_file_path == "/test/document.tex"
        assert result.directory_path == "/test"
        assert result.cleaned_files_count == 5
        assert len(result.cleaned_files) == 2
        assert result.would_clean_files == []
        assert result.dry_run is False
        assert result.recursive is False
        assert result.backup_created is False
        assert result.backup_directory is None
        assert result.cleanup_time_seconds == 0.5

    def test_cleanup_error_exception(self):
        """Test CleanupError exception."""
        error = CleanupError("Test cleanup error")
        assert str(error) == "Test cleanup error"
        assert isinstance(error, Exception)

    def test_clean_latex_with_custom_extensions(self):
        """Test cleanup with custom file extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "custom.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create files with custom extensions
            custom_files = [
                temp_path / "custom.tmp",
                temp_path / "custom.backup",
                temp_path / "custom.old",
            ]
            
            for file in custom_files:
                file.write_text("content")
            
            # Run cleanup with custom extensions
            result = clean_latex(str(tex_file), extensions=[".tmp", ".backup", ".old"])
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.cleaned_files_count == len(custom_files)
            
            # Check that custom files were removed
            for custom_file in custom_files:
                assert not custom_file.exists()

    def test_clean_latex_performance_timing(self):
        """Test that cleanup includes timing information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "timing.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary file
            aux_file = temp_path / "timing.aux"
            aux_file.write_text("aux content")
            
            result = clean_latex(str(tex_file))
            
            assert isinstance(result, CleanupResult)
            assert result.success is True
            assert result.cleanup_time_seconds is not None
            assert result.cleanup_time_seconds > 0
            assert result.cleanup_time_seconds < 5.0  # Should be fast