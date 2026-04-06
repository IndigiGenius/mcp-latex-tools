"""Tests for MCP Resources and Prompts functionality."""

import json
import pytest

from mcp.types import AnyUrl
from mcp_latex_tools.server import (
    list_resources,
    read_resource,
    list_prompts,
    get_prompt,
)
from mcp_latex_tools.tools.cleanup import (
    DEFAULT_CLEANUP_EXTENSIONS as CLEANUP_EXTENSIONS,
    PROTECTED_EXTENSIONS,
)


class TestMCPResources:
    """Tests for MCP Resources functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_expected_resources(self):
        """Test that list_resources returns all expected resources."""
        resources = await list_resources()

        assert len(resources) == 3

        # Check resource URIs (convert to string for comparison)
        uris = [str(r.uri) for r in resources]
        assert "latex://config/cleanup-extensions" in uris
        assert "latex://config/protected-extensions" in uris
        assert "latex://help/workflow" in uris

    @pytest.mark.asyncio
    async def test_list_resources_has_correct_mime_types(self):
        """Test that resources have correct MIME types."""
        resources = await list_resources()

        # Use string keys for the resource map
        resource_map = {str(r.uri): r for r in resources}

        assert (
            resource_map["latex://config/cleanup-extensions"].mimeType
            == "application/json"
        )
        assert (
            resource_map["latex://config/protected-extensions"].mimeType
            == "application/json"
        )
        assert resource_map["latex://help/workflow"].mimeType == "text/markdown"

    @pytest.mark.asyncio
    async def test_read_resource_cleanup_extensions(self):
        """Test reading cleanup extensions resource."""
        content = await read_resource("latex://config/cleanup-extensions")

        data = json.loads(content)
        assert "extensions" in data
        assert "description" in data
        assert "count" in data

        # Verify all cleanup extensions are present
        for ext in CLEANUP_EXTENSIONS:
            assert ext in data["extensions"]

        assert data["count"] == len(CLEANUP_EXTENSIONS)

    @pytest.mark.asyncio
    async def test_read_resource_protected_extensions(self):
        """Test reading protected extensions resource."""
        content = await read_resource("latex://config/protected-extensions")

        data = json.loads(content)
        assert "extensions" in data
        assert "description" in data
        assert "count" in data

        # Verify all protected extensions are present
        for ext in PROTECTED_EXTENSIONS:
            assert ext in data["extensions"]

        assert data["count"] == len(PROTECTED_EXTENSIONS)

    @pytest.mark.asyncio
    async def test_read_resource_workflow_guide(self):
        """Test reading workflow guide resource."""
        content = await read_resource("latex://help/workflow")

        # Should be markdown content
        assert "# LaTeX Compilation Workflow" in content
        assert "validate_latex" in content
        assert "compile_latex" in content
        assert "pdf_info" in content
        assert "cleanup" in content

    @pytest.mark.asyncio
    async def test_read_resource_with_anyurl_cleanup_extensions(self):
        """Test that read_resource works with AnyUrl objects (MCP dispatch path)."""
        content = await read_resource(AnyUrl("latex://config/cleanup-extensions"))
        data = json.loads(content)
        assert "extensions" in data
        assert data["count"] == len(CLEANUP_EXTENSIONS)

    @pytest.mark.asyncio
    async def test_read_resource_with_anyurl_protected_extensions(self):
        """Test that read_resource works with AnyUrl objects for protected extensions."""
        content = await read_resource(AnyUrl("latex://config/protected-extensions"))
        data = json.loads(content)
        assert "extensions" in data
        assert data["count"] == len(PROTECTED_EXTENSIONS)

    @pytest.mark.asyncio
    async def test_read_resource_with_anyurl_workflow(self):
        """Test that read_resource works with AnyUrl objects for workflow guide."""
        content = await read_resource(AnyUrl("latex://help/workflow"))
        assert "# LaTeX Compilation Workflow" in content

    @pytest.mark.asyncio
    async def test_read_resource_unknown_uri_raises_error(self):
        """Test that reading unknown resource raises ValueError."""
        with pytest.raises(ValueError, match="Unknown resource"):
            await read_resource("latex://unknown/resource")


class TestMCPPrompts:
    """Tests for MCP Prompts functionality."""

    @pytest.mark.asyncio
    async def test_list_prompts_returns_expected_prompts(self):
        """Test that list_prompts returns all expected prompts."""
        prompts = await list_prompts()

        assert len(prompts) == 3

        # Check prompt names
        names = [p.name for p in prompts]
        assert "compile-and-verify" in names
        assert "diagnose-compilation-error" in names
        assert "prepare-fresh-build" in names

    @pytest.mark.asyncio
    async def test_list_prompts_have_descriptions(self):
        """Test that all prompts have descriptions."""
        prompts = await list_prompts()

        for prompt in prompts:
            assert prompt.description is not None
            assert len(prompt.description) > 0

    @pytest.mark.asyncio
    async def test_list_prompts_have_required_arguments(self):
        """Test that prompts have tex_path as required argument."""
        prompts = await list_prompts()

        for prompt in prompts:
            # All prompts should have tex_path argument
            arg_names = [arg.name for arg in prompt.arguments]
            assert "tex_path" in arg_names

            # tex_path should be required
            tex_path_arg = next(
                arg for arg in prompt.arguments if arg.name == "tex_path"
            )
            assert tex_path_arg.required is True

    @pytest.mark.asyncio
    async def test_get_prompt_compile_and_verify(self):
        """Test getting compile-and-verify prompt."""
        result = await get_prompt("compile-and-verify", {"tex_path": "test.tex"})

        assert result.description is not None
        assert "test.tex" in result.description

        # Check that messages contain workflow steps
        assert len(result.messages) == 1
        message_text = result.messages[0].content.text
        assert "VALIDATE" in message_text
        assert "COMPILE" in message_text
        assert "VERIFY" in message_text
        assert "test.tex" in message_text

    @pytest.mark.asyncio
    async def test_get_prompt_compile_and_verify_with_cleanup_false(self):
        """Test compile-and-verify prompt with cleanup disabled."""
        result = await get_prompt(
            "compile-and-verify", {"tex_path": "test.tex", "cleanup": "false"}
        )

        message_text = result.messages[0].content.text
        assert "SKIP CLEANUP" in message_text

    @pytest.mark.asyncio
    async def test_get_prompt_diagnose_compilation_error(self):
        """Test getting diagnose-compilation-error prompt."""
        result = await get_prompt(
            "diagnose-compilation-error", {"tex_path": "broken.tex"}
        )

        assert result.description is not None
        assert "broken.tex" in result.description

        message_text = result.messages[0].content.text
        assert "VALIDATE (Quick)" in message_text
        assert "VALIDATE (Full)" in message_text
        assert "VALIDATE (Strict)" in message_text
        assert "DIAGNOSIS" in message_text

    @pytest.mark.asyncio
    async def test_get_prompt_prepare_fresh_build(self):
        """Test getting prepare-fresh-build prompt."""
        result = await get_prompt("prepare-fresh-build", {"tex_path": "document.tex"})

        assert result.description is not None
        assert "document.tex" in result.description

        message_text = result.messages[0].content.text
        assert "PREVIEW CLEANUP" in message_text
        assert "CLEAN" in message_text
        assert "create_backup" in message_text
        assert "COMPILE" in message_text
        assert "VERIFY" in message_text

    @pytest.mark.asyncio
    async def test_get_prompt_with_no_arguments(self):
        """Test getting prompt with no arguments uses placeholder."""
        result = await get_prompt("compile-and-verify", None)

        message_text = result.messages[0].content.text
        assert "<tex_path>" in message_text

    @pytest.mark.asyncio
    async def test_get_prompt_unknown_name_raises_error(self):
        """Test that getting unknown prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await get_prompt("unknown-prompt", {})


class TestExtensionConstants:
    """Tests for extension constant definitions."""

    def test_cleanup_extensions_are_lowercase(self):
        """Test that all cleanup extensions are lowercase."""
        for ext in CLEANUP_EXTENSIONS:
            assert ext == ext.lower()

    def test_cleanup_extensions_start_with_dot(self):
        """Test that all cleanup extensions start with a dot."""
        for ext in CLEANUP_EXTENSIONS:
            assert ext.startswith(".")

    def test_protected_extensions_are_lowercase(self):
        """Test that all protected extensions are lowercase."""
        for ext in PROTECTED_EXTENSIONS:
            assert ext == ext.lower()

    def test_protected_extensions_start_with_dot(self):
        """Test that all protected extensions start with a dot."""
        for ext in PROTECTED_EXTENSIONS:
            assert ext.startswith(".")

    def test_no_overlap_between_cleanup_and_protected(self):
        """Test that cleanup and protected extensions don't overlap."""
        overlap = CLEANUP_EXTENSIONS & PROTECTED_EXTENSIONS
        assert len(overlap) == 0, f"Extensions in both sets: {overlap}"

    def test_tex_and_pdf_are_protected(self):
        """Test that .tex and .pdf are in protected extensions."""
        assert ".tex" in PROTECTED_EXTENSIONS
        assert ".pdf" in PROTECTED_EXTENSIONS
        assert ".bib" in PROTECTED_EXTENSIONS

    def test_common_auxiliary_extensions_in_cleanup(self):
        """Test that common auxiliary extensions are in cleanup set."""
        common_aux = {".aux", ".log", ".out", ".toc", ".lof", ".lot"}
        for ext in common_aux:
            assert ext in CLEANUP_EXTENSIONS
