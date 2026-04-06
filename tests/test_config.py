"""Tests for mcp_latex_tools.config — configuration system."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from mcp_latex_tools.config import (
    CONFIG_FILENAME,
    CompilationConfig,
    CleanupConfig,
    ToolConfig,
    find_config_file,
    load_config,
)


class TestToolConfigDefaults:
    """ToolConfig() with no arguments must match all current hardcoded defaults."""

    def test_default_compilation(self) -> None:
        cfg = ToolConfig()
        assert cfg.compilation.engine == "pdflatex"
        assert cfg.compilation.passes == 1
        assert cfg.compilation.timeout == 30

    def test_default_validation(self) -> None:
        cfg = ToolConfig()
        assert cfg.validation.quick is False
        assert cfg.validation.strict is False
        assert cfg.validation.max_errors == 10

    def test_default_cleanup(self) -> None:
        cfg = ToolConfig()
        assert cfg.cleanup.dry_run is False
        assert cfg.cleanup.recursive is False
        assert cfg.cleanup.create_backup is False
        assert cfg.cleanup.extensions is None

    def test_default_pdf_info(self) -> None:
        cfg = ToolConfig()
        assert cfg.pdf_info.include_text is False

    def test_default_detect_packages(self) -> None:
        cfg = ToolConfig()
        assert cfg.detect_packages.check_installed is True


class TestToolConfigPartial:
    """Partial config data fills remaining fields with defaults."""

    def test_partial_compilation_section(self) -> None:
        cfg = ToolConfig.model_validate({"compilation": {"engine": "xelatex"}})
        assert cfg.compilation.engine == "xelatex"
        assert cfg.compilation.timeout == 30
        assert cfg.compilation.passes == 1

    def test_partial_sections_fill_defaults(self) -> None:
        cfg = ToolConfig.model_validate({"cleanup": {"dry_run": True}})
        assert cfg.cleanup.dry_run is True
        assert cfg.compilation.engine == "pdflatex"
        assert cfg.validation.quick is False

    def test_full_config_from_dict(self) -> None:
        data = {
            "compilation": {"engine": "lualatex", "passes": "auto", "timeout": 120},
            "cleanup": {"dry_run": True, "extensions": [".aux", ".log"]},
        }
        cfg = ToolConfig.model_validate(data)
        assert cfg.compilation.engine == "lualatex"
        assert cfg.compilation.passes == "auto"
        assert cfg.compilation.timeout == 120
        assert cfg.cleanup.dry_run is True
        assert cfg.cleanup.extensions == [".aux", ".log"]

    def test_compilation_passes_accepts_int(self) -> None:
        cfg = CompilationConfig(passes=3)
        assert cfg.passes == 3

    def test_compilation_passes_accepts_auto(self) -> None:
        cfg = CompilationConfig(passes="auto")
        assert cfg.passes == "auto"

    def test_invalid_timeout_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CompilationConfig(timeout="not_a_number")  # type: ignore[arg-type]

    def test_invalid_dry_run_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CleanupConfig(dry_run=[1, 2])  # type: ignore[arg-type]


class TestFindConfigFile:
    """Config file discovery — walk up from start_dir to root."""

    def test_finds_config_in_start_dir(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\nengine = "xelatex"\n')
        result = find_config_file(start_dir=tmp_path)
        assert result == cfg_file

    def test_finds_config_in_parent_dir(self, tmp_path: Path) -> None:
        child = tmp_path / "subdir"
        child.mkdir()
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\nengine = "xelatex"\n')
        result = find_config_file(start_dir=child)
        assert result == cfg_file

    def test_finds_config_in_grandparent_dir(self, tmp_path: Path) -> None:
        grandchild = tmp_path / "a" / "b"
        grandchild.mkdir(parents=True)
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\nengine = "xelatex"\n')
        result = find_config_file(start_dir=grandchild)
        assert result == cfg_file

    def test_returns_none_when_no_config(self, tmp_path: Path) -> None:
        result = find_config_file(start_dir=tmp_path)
        assert result is None

    def test_nearest_config_wins(self, tmp_path: Path) -> None:
        parent_cfg = tmp_path / CONFIG_FILENAME
        parent_cfg.write_text('[compilation]\nengine = "pdflatex"\n')
        child = tmp_path / "subdir"
        child.mkdir()
        child_cfg = child / CONFIG_FILENAME
        child_cfg.write_text('[compilation]\nengine = "xelatex"\n')
        result = find_config_file(start_dir=child)
        assert result == child_cfg


class TestLoadConfig:
    """Config loading from TOML files."""

    def test_load_valid_toml(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\nengine = "xelatex"\ntimeout = 60\n')
        cfg = load_config(config_path=cfg_file)
        assert cfg.compilation.engine == "xelatex"
        assert cfg.compilation.timeout == 60

    def test_load_returns_defaults_when_no_file(self, tmp_path: Path) -> None:
        # Explicit non-existent path
        cfg = load_config(config_path=tmp_path / "nonexistent.toml")
        assert cfg == ToolConfig()

    def test_load_returns_defaults_on_malformed_toml(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("this is not [[ valid toml")
        cfg = load_config(config_path=cfg_file)
        assert cfg == ToolConfig()

    def test_load_returns_defaults_on_invalid_values(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\ntimeout = "not_a_number"\n')
        cfg = load_config(config_path=cfg_file)
        assert cfg == ToolConfig()

    def test_load_partial_sections(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("[cleanup]\ndry_run = true\n")
        cfg = load_config(config_path=cfg_file)
        assert cfg.cleanup.dry_run is True
        assert cfg.compilation.engine == "pdflatex"

    def test_load_empty_file(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("")
        cfg = load_config(config_path=cfg_file)
        assert cfg == ToolConfig()

    def test_load_with_all_sections(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text(
            '[compilation]\nengine = "lualatex"\npasses = "auto"\ntimeout = 120\n\n'
            "[validation]\nstrict = true\nmax_errors = 5\n\n"
            '[cleanup]\ndry_run = true\nextensions = [".aux", ".log"]\n\n'
            "[pdf_info]\ninclude_text = true\n\n"
            "[detect_packages]\ncheck_installed = false\n"
        )
        cfg = load_config(config_path=cfg_file)
        assert cfg.compilation.engine == "lualatex"
        assert cfg.compilation.passes == "auto"
        assert cfg.compilation.timeout == 120
        assert cfg.validation.strict is True
        assert cfg.validation.max_errors == 5
        assert cfg.cleanup.dry_run is True
        assert cfg.cleanup.extensions == [".aux", ".log"]
        assert cfg.pdf_info.include_text is True
        assert cfg.detect_packages.check_installed is False

    def test_load_ignores_unknown_keys(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text(
            '[compilation]\nengine = "xelatex"\nfuture_key = "ignored"\n'
        )
        cfg = load_config(config_path=cfg_file)
        assert cfg.compilation.engine == "xelatex"

    def test_load_autodiscover_from_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_config() with no args discovers config via find_config_file."""
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text('[compilation]\nengine = "xelatex"\n')
        monkeypatch.chdir(tmp_path)
        cfg = load_config()
        assert cfg.compilation.engine == "xelatex"
