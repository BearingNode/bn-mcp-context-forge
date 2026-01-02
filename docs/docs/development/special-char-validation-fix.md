# Special Character Validation Fix

## Overview

This document describes a fix to the special character validation logic in the MCP Gateway's `SecurityValidator` class to ensure error messages accurately reflect the characters allowed by validation patterns.

## Background

The `SecurityValidator` class in `mcpgateway/common/validators.py` performs input validation for various fields like names, identifiers, tool names, and URIs. It uses regex patterns defined in `mcpgateway/common/config.py` to validate input.

### The Issue

The error messages returned when validation failed did not accurately reflect the characters actually allowed by the validation patterns:

1. **NAME_PATTERN** (`^[a-zA-Z0-9_.\-\s]+$`) allows:
   - Letters (a-zA-Z)
   - Numbers (0-9)
   - Underscore (_)
   - **Dot (.)** ← Missing from error message
   - Hyphen (-)
   - **Spaces (\s)** ← Missing from error message

2. **TOOL_NAME_PATTERN** (`^[a-zA-Z][a-zA-Z0-9._-]*$`) allows:
   - Must start with a letter
   - Then: letters, numbers, underscore, **dot**, and hyphen
   - **Dot** was missing from error message

This caused confusion when users tried to use dots or spaces in names, as they would receive error messages saying these characters weren't allowed, even though the validation pattern actually permitted them.

## The Fix

### Changes Made

1. **Updated `validate_name` error message** (line ~305):
   - **Before**: "can only contain letters, numbers, underscore, and hyphen"
   - **After**: "can only contain letters, numbers, underscore, hyphen, dot, and spaces"

2. **Updated `validate_tool_name` error message** (line ~498):
   - **Before**: "must start with a letter and contain only letters, numbers, and underscore"
   - **After**: "must start with a letter and contain only letters, numbers, underscore, dot, and hyphen"

3. **Added defense-in-depth comments** to explain the validation strategy:
   - Pattern match provides the primary validation
   - HTML special character check serves as a safety net
   - This approach ensures security even if patterns are misconfigured

4. **Updated `validate_uri` and `validate_identifier` comments** for consistency

### Code Example

```python
# Before - Missing "dot" and "spaces" in error message
if not re.match(cls.NAME_PATTERN, value):
    raise ValueError(f"{field_name} can only contain letters, numbers, underscore, and hyphen.")

# After - Accurate error message
if not re.match(cls.NAME_PATTERN, value):
    raise ValueError(f"{field_name} can only contain letters, numbers, underscore, hyphen, dot, and spaces.")
```

## Defense-in-Depth Validation

The validation uses a defense-in-depth approach with two layers:

1. **Pattern Match** (primary): Validates against the configured regex pattern
2. **HTML Special Character Check** (safety net): Explicitly blocks HTML-unsafe characters

This redundancy might seem unnecessary since well-formed patterns already exclude HTML special characters. However, it provides:

- **Safety against misconfiguration**: If patterns are changed incorrectly, the HTML check still protects
- **Clear security intent**: Makes it explicit that HTML characters are not allowed
- **Graceful degradation**: If one check fails, the other still catches issues

## Testing

### New Test File

Created `tests/unit/mcpgateway/validation/test_special_char_validation_fix.py` with 14 comprehensive tests:

- ✅ Verify dots work in names and identifiers
- ✅ Verify spaces work in names (but not identifiers)
- ✅ Verify error messages mention all allowed characters
- ✅ Verify defense-in-depth blocking of HTML special characters
- ✅ Verify combinations of allowed special characters

### Test Results

- **New tests**: 14/14 passed
- **Existing validation tests**: 95/95 passed (3 skipped)
- **Security tests**: 58/58 passed (2 skipped)

## Impact

This fix has **minimal runtime impact**:

- No changes to validation logic or performance
- Only error message text updated
- All existing tests continue to pass
- No breaking changes to API or behavior

## Usage Examples

### Valid Name Examples (after fix)

```python
from mcpgateway.common.validators import SecurityValidator

# All of these now work and have accurate error messages if they fail:
SecurityValidator.validate_name("my.test.name", "Name")      # ✓ Dot allowed
SecurityValidator.validate_name("my test name", "Name")       # ✓ Space allowed
SecurityValidator.validate_name("my_test-name", "Name")       # ✓ Underscore and hyphen allowed
SecurityValidator.validate_name("test.name v2", "Name")       # ✓ All combined
```

### Valid Identifier Examples

```python
SecurityValidator.validate_identifier("my.test.id", "ID")     # ✓ Dot allowed
SecurityValidator.validate_identifier("my_test-id", "ID")     # ✓ Underscore and hyphen allowed
# SecurityValidator.validate_identifier("my test id", "ID")   # ✗ Space NOT allowed in identifiers
```

### Valid Tool Name Examples

```python
SecurityValidator.validate_tool_name("my_tool.v1")            # ✓ Dot allowed
SecurityValidator.validate_tool_name("my-tool_name")          # ✓ Hyphen and underscore allowed
# SecurityValidator.validate_tool_name("1tool")               # ✗ Must start with letter
```

## Related Files

- **Main code**: `mcpgateway/common/validators.py`
- **Config patterns**: `mcpgateway/common/config.py`
- **New tests**: `tests/unit/mcpgateway/validation/test_special_char_validation_fix.py`
- **Existing tests**: `tests/unit/mcpgateway/validation/test_validators.py`

## See Also

- [Input Validation Best Practices](../architecture/security-features.md)
- [Testing Guidelines](../testing/)
- [Security Documentation](../../SECURITY.md)
