"""Test cleanup edge cases and error handling paths."""

import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

import pytest

from mcp_latex_tools.tools.cleanup import (
    clean_latex,
    find_auxiliary_files,
    get_default_cleanup_extensions,
    get_protected_extensions,
    is_auxiliary_file
)


class TestSingleFileCleanup:
    """Test single file cleanup edge cases."""
    
    def test_clean_single_auxiliary_file_directly(self):
        """Test cleanup of a single auxiliary file directly."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file directly
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Test cleaning the auxiliary file directly
            result = clean_latex(str(aux_file))
            
            assert result.success
            assert result.cleaned_files_count == 1
            assert str(aux_file) in result.cleaned_files
            assert not aux_file.exists()
    
    def test_clean_single_non_auxiliary_file(self):
        """Test cleanup of a single non-auxiliary file (should not be cleaned)."""
        # Create temporary directory with non-auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create non-auxiliary file
            txt_file = temp_path / "document.txt"
            txt_file.write_text("text content")
            
            # Test cleaning the non-auxiliary file
            result = clean_latex(str(txt_file))
            
            assert result.success
            assert result.cleaned_files_count == 0
            assert len(result.cleaned_files) == 0
            assert txt_file.exists()  # Should not be deleted
    
    def test_clean_single_protected_file(self):
        """Test cleanup of a single protected file (should not be cleaned)."""
        # Create temporary directory with protected file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create protected file
            tex_file = temp_path / "document.tex"
            tex_file.write_text("\\documentclass{article}")
            
            # Test cleaning the protected file
            result = clean_latex(str(tex_file))
            
            assert result.success
            assert result.cleaned_files_count == 0
            assert len(result.cleaned_files) == 0
            assert tex_file.exists()  # Should not be deleted


class TestExceptionHandling:
    """Test exception handling in cleanup operations."""
    
    def test_cleanup_with_permission_error_on_file_removal(self):
        """Test cleanup when file removal fails due to permission error."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Mock Path.unlink to raise permission error
            with patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied")):
                result = clean_latex(str(temp_path))
                
                # Should succeed overall but not clean the file
                assert result.success
                assert result.cleaned_files_count == 0
                assert len(result.cleaned_files) == 0
                assert aux_file.exists()  # Should still exist
    
    def test_cleanup_with_os_error_during_file_removal(self):
        """Test cleanup when file removal fails due to OS error."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Mock Path.unlink to raise OS error
            with patch('pathlib.Path.unlink', side_effect=OSError("File in use")):
                result = clean_latex(str(temp_path))
                
                # Should succeed overall but not clean the file
                assert result.success
                assert result.cleaned_files_count == 0
                assert len(result.cleaned_files) == 0
                assert aux_file.exists()  # Should still exist
    
    def test_cleanup_with_generic_exception_during_main_operation(self):
        """Test cleanup when generic exception occurs during main operation."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock find_auxiliary_files to raise exception
            with patch('mcp_latex_tools.tools.cleanup.find_auxiliary_files', side_effect=RuntimeError("Unexpected error")):
                result = clean_latex(str(temp_path))
                
                assert not result.success
                assert "Unexpected error" in result.error_message
                assert result.cleanup_time_seconds is not None
    
    def test_cleanup_with_backup_directory_creation_failure(self):
        """Test cleanup when backup directory creation fails."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Mock backup directory creation to fail
            with patch('mcp_latex_tools.tools.cleanup.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "invalid/path"
                
                result = clean_latex(str(temp_path), create_backup=True)
                
                # Should handle backup creation failure gracefully
                # The exact behavior depends on implementation, but should not crash
                assert result.cleanup_time_seconds is not None


class TestBackupDirectoryCreation:
    """Test backup directory creation edge cases."""
    
    def test_cleanup_directory_with_backup_creation(self):
        """Test cleanup of directory with backup creation."""
        # Create temporary directory with auxiliary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary files
            aux_files = [
                temp_path / "document.aux",
                temp_path / "document.log",
                temp_path / "document.out"
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            # Test cleanup with backup creation
            result = clean_latex(str(temp_path), create_backup=True)
            
            assert result.success
            assert result.cleaned_files_count == 3
            assert result.backup_directory is not None
            assert Path(result.backup_directory).exists()
            
            # Verify backup contains the files
            backup_path = Path(result.backup_directory)
            backup_files = list(backup_path.glob("*"))
            assert len(backup_files) == 3
    
    def test_cleanup_single_file_with_backup_creation(self):
        """Test cleanup of single file with backup creation."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Test cleanup with backup creation
            result = clean_latex(str(aux_file), create_backup=True)
            
            assert result.success
            assert result.cleaned_files_count == 1
            assert result.backup_directory is not None
            assert Path(result.backup_directory).exists()
            
            # Verify backup contains the file
            backup_path = Path(result.backup_directory)
            backup_files = list(backup_path.glob("*"))
            assert len(backup_files) == 1
            assert backup_files[0].name == "document.aux"


class TestUtilityFunctions:
    """Test utility functions for cleanup operations."""
    
    def test_get_default_cleanup_extensions(self):
        """Test get_default_cleanup_extensions function."""
        extensions = get_default_cleanup_extensions()
        
        assert isinstance(extensions, set)
        assert len(extensions) > 0
        assert '.aux' in extensions
        assert '.log' in extensions
        assert '.out' in extensions
        assert '.fls' in extensions
        assert '.fdb_latexmk' in extensions
        
        # Verify it's a copy (modifications don't affect original)
        original_size = len(extensions)
        extensions.add('.custom')
        
        # Get again and verify original is unchanged
        extensions2 = get_default_cleanup_extensions()
        assert len(extensions2) == original_size
        assert '.custom' not in extensions2
    
    def test_get_protected_extensions(self):
        """Test get_protected_extensions function."""
        extensions = get_protected_extensions()
        
        assert isinstance(extensions, set)
        assert len(extensions) > 0
        assert '.tex' in extensions
        assert '.pdf' in extensions
        assert '.bib' in extensions
        assert '.sty' in extensions
        assert '.cls' in extensions
        
        # Verify it's a copy (modifications don't affect original)
        original_size = len(extensions)
        extensions.add('.custom')
        
        # Get again and verify original is unchanged
        extensions2 = get_protected_extensions()
        assert len(extensions2) == original_size
        assert '.custom' not in extensions2
    
    def test_is_auxiliary_file_with_auxiliary_files(self):
        """Test is_auxiliary_file function with auxiliary files."""
        assert is_auxiliary_file(Path("document.aux"))
        assert is_auxiliary_file(Path("document.log"))
        assert is_auxiliary_file(Path("document.out"))
        assert is_auxiliary_file(Path("document.fls"))
        assert is_auxiliary_file(Path("document.fdb_latexmk"))
        assert is_auxiliary_file(Path("document.toc"))
        
        # Test with different file paths
        assert is_auxiliary_file(Path("/path/to/document.aux"))
        assert is_auxiliary_file(Path("./document.log"))
    
    def test_is_auxiliary_file_with_protected_files(self):
        """Test is_auxiliary_file function with protected files."""
        assert not is_auxiliary_file(Path("document.tex"))
        assert not is_auxiliary_file(Path("document.pdf"))
        assert not is_auxiliary_file(Path("document.bib"))
        assert not is_auxiliary_file(Path("document.sty"))
        assert not is_auxiliary_file(Path("document.cls"))
        
        # Test with different file paths
        assert not is_auxiliary_file(Path("/path/to/document.tex"))
        assert not is_auxiliary_file(Path("./document.pdf"))
    
    def test_is_auxiliary_file_with_unknown_extensions(self):
        """Test is_auxiliary_file function with unknown extensions."""
        assert not is_auxiliary_file(Path("document.txt"))
        assert not is_auxiliary_file(Path("document.py"))
        assert not is_auxiliary_file(Path("document.cpp"))
        assert not is_auxiliary_file(Path("document.unknown"))
        
        # Test with different file paths
        assert not is_auxiliary_file(Path("/path/to/document.txt"))
        assert not is_auxiliary_file(Path("./document.unknown"))


class TestFindAuxiliaryFiles:
    """Test find_auxiliary_files function comprehensively."""
    
    def test_find_auxiliary_files_in_directory_non_recursive(self):
        """Test finding auxiliary files in directory (non-recursive)."""
        # Create temporary directory with mixed files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary files
            aux_files = [
                temp_path / "document.aux",
                temp_path / "document.log",
                temp_path / "document.out"
            ]
            
            # Create protected files
            protected_files = [
                temp_path / "document.tex",
                temp_path / "document.pdf"
            ]
            
            # Create subdirectory with auxiliary files
            subdir = temp_path / "subdir"
            subdir.mkdir()
            subdir_aux = subdir / "subdoc.aux"
            subdir_aux.write_text("subdirectory auxiliary content")
            
            # Write content to all files
            for file in aux_files + protected_files:
                file.write_text("content")
            
            # Test non-recursive search
            found_files = find_auxiliary_files(str(temp_path), recursive=False)
            
            assert len(found_files) == 3
            found_names = {f.name for f in found_files}
            assert found_names == {"document.aux", "document.log", "document.out"}
            
            # Should not include subdirectory files
            assert not any(f.name == "subdoc.aux" for f in found_files)
    
    def test_find_auxiliary_files_in_directory_recursive(self):
        """Test finding auxiliary files in directory (recursive)."""
        # Create temporary directory with nested structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary files in root
            root_aux = temp_path / "document.aux"
            root_aux.write_text("root auxiliary content")
            
            # Create subdirectory with auxiliary files
            subdir = temp_path / "subdir"
            subdir.mkdir()
            subdir_aux = subdir / "subdoc.aux"
            subdir_aux.write_text("subdirectory auxiliary content")
            
            # Create nested subdirectory
            nested_subdir = subdir / "nested"
            nested_subdir.mkdir()
            nested_aux = nested_subdir / "nested.log"
            nested_aux.write_text("nested auxiliary content")
            
            # Test recursive search
            found_files = find_auxiliary_files(str(temp_path), recursive=True)
            
            assert len(found_files) == 3
            found_names = {f.name for f in found_files}
            assert found_names == {"document.aux", "subdoc.aux", "nested.log"}
    
    def test_find_auxiliary_files_with_custom_extensions(self):
        """Test finding auxiliary files with custom extensions."""
        # Create temporary directory with mixed files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files with various extensions
            files = [
                temp_path / "document.aux",  # Default auxiliary
                temp_path / "document.log",  # Default auxiliary
                temp_path / "document.custom",  # Custom extension
                temp_path / "document.tex",  # Protected
                temp_path / "document.another"  # Another custom
            ]
            
            for file in files:
                file.write_text("content")
            
            # Test with custom extensions
            custom_extensions = {'.custom', '.another'}
            found_files = find_auxiliary_files(str(temp_path), extensions=custom_extensions)
            
            assert len(found_files) == 2
            found_names = {f.name for f in found_files}
            assert found_names == {"document.custom", "document.another"}
    
    def test_find_auxiliary_files_in_empty_directory(self):
        """Test finding auxiliary files in empty directory."""
        # Create empty temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test search in empty directory
            found_files = find_auxiliary_files(str(temp_path))
            
            assert len(found_files) == 0
            assert found_files == []
    
    def test_find_auxiliary_files_with_mixed_file_types(self):
        """Test finding auxiliary files with protected files mixed in."""
        # Create temporary directory with mixed files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary files
            aux_files = [
                temp_path / "document.aux",
                temp_path / "document.log",
                temp_path / "document.out",
                temp_path / "document.fls",
                temp_path / "document.fdb_latexmk"
            ]
            
            # Create protected files
            protected_files = [
                temp_path / "document.tex",
                temp_path / "document.pdf",
                temp_path / "document.bib",
                temp_path / "references.bib"
            ]
            
            # Create unknown files
            unknown_files = [
                temp_path / "document.txt",
                temp_path / "readme.md",
                temp_path / "script.py"
            ]
            
            # Write content to all files
            for file in aux_files + protected_files + unknown_files:
                file.write_text("content")
            
            # Test search
            found_files = find_auxiliary_files(str(temp_path))
            
            assert len(found_files) == 5
            found_names = {f.name for f in found_files}
            expected_names = {"document.aux", "document.log", "document.out", 
                            "document.fls", "document.fdb_latexmk"}
            assert found_names == expected_names
    
    def test_find_auxiliary_files_with_permission_error(self):
        """Test finding auxiliary files when directory access fails."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock Path.glob to raise permission error
            with patch('pathlib.Path.glob', side_effect=PermissionError("Permission denied")):
                # Should handle permission error gracefully
                found_files = find_auxiliary_files(str(temp_path))
                
                # Should return empty list on permission error
                assert len(found_files) == 0
    
    def test_find_auxiliary_files_with_os_error(self):
        """Test finding auxiliary files when OS error occurs."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock Path.glob to raise OS error
            with patch('pathlib.Path.glob', side_effect=OSError("Disk error")):
                # Should handle OS error gracefully
                found_files = find_auxiliary_files(str(temp_path))
                
                # Should return empty list on OS error
                assert len(found_files) == 0


class TestCleanupIntegration:
    """Test cleanup integration scenarios with edge cases."""
    
    def test_cleanup_with_partial_failures_and_successes(self):
        """Test cleanup with some files failing and others succeeding."""
        # Create temporary directory with multiple auxiliary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary files
            aux_files = [
                temp_path / "document1.aux",
                temp_path / "document2.aux",
                temp_path / "document3.aux"
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            # Mock file removal to fail for one file
            original_unlink = Path.unlink
            def mock_unlink(self):
                if self.name == "document2.aux":
                    raise PermissionError("Permission denied")
                else:
                    original_unlink(self)
            
            with patch('pathlib.Path.unlink', side_effect=mock_unlink):
                result = clean_latex(str(temp_path))
                
                # Should succeed overall
                assert result.success
                # Should clean 2 out of 3 files
                assert result.cleaned_files_count == 2
                assert len(result.cleaned_files) == 2
                
                # Verify which files were cleaned
                cleaned_names = {Path(f).name for f in result.cleaned_files}
                assert cleaned_names == {"document1.aux", "document3.aux"}
                
                # Verify the failed file still exists
                assert (temp_path / "document2.aux").exists()
    
    def test_cleanup_timing_accuracy_with_errors(self):
        """Test that cleanup timing is accurate even with errors."""
        # Create temporary directory with auxiliary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create auxiliary file
            aux_file = temp_path / "document.aux"
            aux_file.write_text("auxiliary content")
            
            # Mock find_auxiliary_files to raise exception after delay
            import time
            def delayed_exception(*args, **kwargs):
                time.sleep(0.1)  # Simulate some processing time
                raise Exception("Simulated error")
            
            with patch('mcp_latex_tools.tools.cleanup.find_auxiliary_files', side_effect=delayed_exception):
                result = clean_latex(str(temp_path))
                
                assert not result.success
                assert result.cleanup_time_seconds is not None
                assert result.cleanup_time_seconds >= 0.1  # Should include the delay