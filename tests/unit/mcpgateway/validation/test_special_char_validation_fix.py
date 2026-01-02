# -*- coding: utf-8 -*-
"""Location: ./tests/unit/mcpgateway/validation/test_special_char_validation_fix.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0

Test for special character validation fix.

This test file validates the fix for special character validation error messages
to ensure they accurately reflect the characters allowed by the validation patterns.

Background:
- The NAME_PATTERN allows: a-zA-Z0-9_.-<space>
- The IDENTIFIER_PATTERN allows: a-zA-Z0-9_-.
- The TOOL_NAME_PATTERN allows: ^[a-zA-Z][a-zA-Z0-9._-]*

The issue was that error messages didn't mention "dot" and "spaces" even though
these characters were allowed by the patterns. This caused confusion when users
tried to use dots or spaces in names and received error messages that didn't
reflect the actual allowed characters.
"""

# Third-Party
import pytest

# First-Party
from mcpgateway.common.validators import SecurityValidator


class TestSpecialCharacterValidation:
    """Test that validation error messages accurately reflect allowed characters."""

    def test_name_allows_dots(self):
        """NAME_PATTERN allows dots - verify they work."""
        result = SecurityValidator.validate_name("my.test.name", "Name")
        assert result == "my.test.name"

    def test_name_allows_spaces(self):
        """NAME_PATTERN allows spaces - verify they work."""
        result = SecurityValidator.validate_name("my test name", "Name")
        assert result == "my test name"

    def test_name_allows_hyphens(self):
        """NAME_PATTERN allows hyphens - verify they work."""
        result = SecurityValidator.validate_name("my-test-name", "Name")
        assert result == "my-test-name"

    def test_name_allows_underscores(self):
        """NAME_PATTERN allows underscores - verify they work."""
        result = SecurityValidator.validate_name("my_test_name", "Name")
        assert result == "my_test_name"

    def test_name_error_message_mentions_allowed_chars(self):
        """Error message should mention all allowed characters."""
        with pytest.raises(ValueError) as exc_info:
            SecurityValidator.validate_name("invalid<script>", "Name")
        
        error_msg = str(exc_info.value)
        # Error message should mention dot and spaces which are allowed
        assert "dot" in error_msg.lower() or "." in error_msg
        assert "space" in error_msg.lower()
        assert "hyphen" in error_msg.lower() or "-" in error_msg
        assert "underscore" in error_msg.lower() or "_" in error_msg

    def test_identifier_allows_dots(self):
        """IDENTIFIER_PATTERN allows dots - verify they work."""
        result = SecurityValidator.validate_identifier("my.test.id", "ID")
        assert result == "my.test.id"

    def test_identifier_allows_hyphens_and_underscores(self):
        """IDENTIFIER_PATTERN allows hyphens and underscores - verify they work."""
        result = SecurityValidator.validate_identifier("my_test-id", "ID")
        assert result == "my_test-id"

    def test_identifier_rejects_spaces(self):
        """IDENTIFIER_PATTERN does NOT allow spaces - verify rejection."""
        with pytest.raises(ValueError) as exc_info:
            SecurityValidator.validate_identifier("my test id", "ID")
        
        error_msg = str(exc_info.value)
        assert "can only contain" in error_msg.lower()

    def test_identifier_error_message_mentions_allowed_chars(self):
        """Error message should mention all allowed characters."""
        with pytest.raises(ValueError) as exc_info:
            SecurityValidator.validate_identifier("invalid<script>", "ID")
        
        error_msg = str(exc_info.value)
        # Error message should mention dots which are allowed
        assert "dot" in error_msg.lower() or "." in error_msg
        assert "hyphen" in error_msg.lower() or "-" in error_msg

    def test_tool_name_allows_dots(self):
        """TOOL_NAME_PATTERN allows dots - verify they work."""
        result = SecurityValidator.validate_tool_name("my_tool.v1")
        assert result == "my_tool.v1"

    def test_tool_name_allows_hyphens(self):
        """TOOL_NAME_PATTERN allows hyphens - verify they work."""
        result = SecurityValidator.validate_tool_name("my-tool_name")
        assert result == "my-tool_name"

    def test_tool_name_error_message_mentions_allowed_chars(self):
        """Error message should mention all allowed characters."""
        with pytest.raises(ValueError) as exc_info:
            SecurityValidator.validate_tool_name("1tool")  # Must start with letter
        
        error_msg = str(exc_info.value)
        # Error message should mention dot and hyphen which are allowed
        assert "dot" in error_msg.lower() or "." in error_msg
        assert "hyphen" in error_msg.lower() or "-" in error_msg

    def test_defense_in_depth_pattern_and_html_check(self):
        """Verify defense-in-depth: both pattern check and HTML char check."""
        # HTML special chars should be rejected by pattern match first
        with pytest.raises(ValueError):
            SecurityValidator.validate_name("name<script>", "Name")
        
        with pytest.raises(ValueError):
            SecurityValidator.validate_name('name"test', "Name")
        
        with pytest.raises(ValueError):
            SecurityValidator.validate_name("name'test", "Name")
        
        with pytest.raises(ValueError):
            SecurityValidator.validate_name("name/test", "Name")

    def test_combined_special_chars(self):
        """Test combinations of allowed special characters."""
        # Name allows dots, hyphens, underscores, and spaces
        result = SecurityValidator.validate_name("my_test.name-v1 final", "Name")
        assert result == "my_test.name-v1 final"
        
        # Identifier allows dots, hyphens, and underscores (no spaces)
        result = SecurityValidator.validate_identifier("my_test.id-v1.0", "ID")
        assert result == "my_test.id-v1.0"
        
        # Tool name allows dots, hyphens, and underscores
        result = SecurityValidator.validate_tool_name("my_tool.v1-beta")
        assert result == "my_tool.v1-beta"
