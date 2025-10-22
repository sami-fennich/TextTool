# TextTool - Advanced Text Manipulation Tool

A powerful, feature-rich command-line text processing tool built with Python. TextTool provides an intuitive interface for performing complex text operations including regex replacements, filtering, data extraction, and batch processing.

## Features

### Core Functionality
- **Load & Save**: Load from files or clipboard, save to new files or overwrite originals
- **Filtering**: Select, show, and delete lines based on patterns or regex
- **Text Replacement**: Simple text replacement, regex patterns, and capture groups
- **Organization**: Sort lines, remove duplicates, and reorganize content
- **Undo/Revert**: Full undo support for all operations

### Advanced Operations
- **Bulk Replacement**: Replace multiple strings using mapping files or clipboard
- **Conditional Replacement**: Replace text only in lines matching specific criteria
- **Extraction**: Extract URLs, emails, text between delimiters, or specific columns
- **Data Processing**: Filter by length, detect mismatches, convert CSV to tables
- **Batch Processing**: Use placeholder templates for mail-merge style operations
- **Code Blocks**: Extract and process indented content hierarchically

### Interactive Features
- **Live View**: Real-time visual editor with syntax highlighting
- **Search & Navigation**: Find text with regex support, whole-word matching
- **Command Palette**: Access all commands with fuzzy search
- **Context Menu**: Right-click operations for quick actions
- **History**: Persistent command history across sessions

## Installation

### Requirements
- Python 3.7+
- Windows, macOS, or Linux

### Setup
```bash
# Clone or download the repository
git clone https://github.com/yourusername/TextTool.git
cd TextTool

# Install required dependencies
pip install cmd2 regex pandas openpyxl win32clipboard

# Run the tool
python TextTool.py
```

## Quick Start

### Basic Usage
```bash
# Start TextTool
python TextTool.py

# Load a file
load "path/to/file.txt"

# Load from clipboard
load

# Show all lines
show

# Show lines containing "error"
show "error"

# Replace text
replace "old" "new"

# Save changes
save
```

### Common Tasks

**Filter and extract specific lines:**
```
select "error"
show
```

**Replace with regex patterns:**
```
replace "(\d{2})-(\d{2})-(\d{4})" "\3/\2/\1"
```

**Remove duplicates and sort:**
```
sort
unique
remove_empty_lines
```

**Extract specific columns from CSV:**
```
extract_column "1,3,5" ","
```

**Interactive replacement with confirmation:**
```
replace_confirm "old_text" "new_text"
```

## Core Commands

### File Operations
| Command | Purpose |
|---------|---------|
| `load [file_path]` | Load a text file or clipboard content |
| `save [file_path]` | Save modified text to file |
| `revert` | Undo the last operation |

### Viewing & Filtering
| Command | Purpose |
|---------|---------|
| `show [pattern]` | Display lines matching pattern |
| `select [pattern]` | Keep only lines matching pattern |
| `delete [pattern]` | Remove lines matching pattern |
| `count [pattern]` | Count matching lines |

### Text Modification
| Command | Purpose |
|---------|---------|
| `replace "old" "new"` | Replace text with optional regex |
| `right_replace "old" "new"` | Replace from pattern to end of line |
| `left_replace "old" "new"` | Replace from start to pattern |
| `replace_confirm "old" "new"` | Interactive replacement with confirmation |
| `conditional_replace "search" "replace" "target"` | Replace only in matching lines |

### Data Processing
| Command | Purpose |
|---------|---------|
| `sort` | Sort all lines alphabetically |
| `unique` | Remove duplicate lines |
| `remove_empty_lines` | Delete blank lines |
| `trim_whitespace` | Remove leading/trailing spaces |
| `convert_case upper\|lower\|title` | Change text case |

### Extraction & Analysis
| Command | Purpose |
|---------|---------|
| `extract_emails` | Extract email addresses |
| `extract_urls` | Extract URLs |
| `extract_between "start" "end"` | Extract text between delimiters |
| `extract_column "1,3,5" [delimiter]` | Extract specific columns |
| `find_duplicates [threshold]` | Find and count duplicates |
| `statistics` | Display comprehensive text statistics |

### Advanced Features
| Command | Purpose |
|---------|---------|
| `bulk_replace [file] [separator]` | Replace multiple strings from mapping file |
| `placeholder_replace "placeholder" [file]` | Template-based batch replacement |
| `select_indented "pattern"` | Select hierarchical indented blocks |
| `select_lines "1-5,10,15-20"` | Select specific line ranges |
| `filter_length min [max]` | Filter by line length |
| `csv_to_table [delimiter]` | Display CSV as formatted table |

## Advanced Usage

### Regular Expressions
TextTool supports full regex functionality:

```
# Show lines starting with capital letter
show "^[A-Z]"

# Show lines with digits
show "\d+"

# Replace date format
replace "(\d{2})-(\d{2})-(\d{4})" "\3/\2/\1"

# Extract content in brackets
show "\[.*?\]"
```

### Bulk Operations with Mapping Files
Create a mapping file for batch replacements:

**map.txt** (tab-separated):
```
old_value    new_value
error        ERROR
warning      WARNING
info         INFO
```

```
bulk_replace map.txt tab
```

### Template-Based Replacements
Generate multiple versions from a template:

**data.txt**:
```
name   age   city
john   25    london
jane   30    paris
```

**Template in TextTool:**
```
placeholder_replace "{{name}}" "{{age}}" data.txt
```

### Conditional Processing
Replace text only in matching lines:

```
# Replace "error" with "ERROR" only in lines containing "critical"
conditional_replace "error" "ERROR" "critical"
```

### Interactive Live View
```
# Open visual editor with real-time preview
liveview

# Search with Ctrl+F
# Replace with Ctrl+R
# Save with Ctrl+S
```

## Special Features

### Live View Editor
- Real-time text display and editing
- Search with regex support
- Whole-word and case-sensitive matching
- Find/Next navigation with F3 shortcuts
- Direct save functionality
- Load files via dialog
- Paste from clipboard

### Command Palette
Press keyboard shortcut or use menu to access all commands with:
- Fuzzy search across all functions
- Inline parameter entry
- Immediate execution

### Clipboard Integration
- Load text from clipboard with `load`
- Use clipboard as source for mapping files in `bulk_replace`
- Direct copy/paste in Live View
- Seamless workflow integration

## Standard vs Advanced Mode

Standard mode provides essential text processing:
```
advanced    # Enable advanced functions
standard    # Return to basic mode
```

**Advanced Mode** adds:
- `extract_between` - Extract sections
- `extract_column` - Column extraction
- `bulk_replace` - Mapping-based replacement
- `placeholder_replace` - Template expansion
- `find_duplicates` - Duplicate detection
- `filter_length` - Length-based filtering
- `csv_to_table` - Table formatting
- And more...

## Special Placeholders

Use these in patterns when special characters cause issues:

| Placeholder | Represents |
|-------------|-----------|
| `[pipe]` | Pipe character `\|` |
| `[doublequote]` | Double quote `"` |
| `[quote]` | Single quote `'` |
| `[tab]` | Tab character |
| `[spaces]` | One or more spaces |

Example:
```
replace "[pipe]" "PIPE"    # Replace all pipes with "PIPE"
select "[spaces]+"         # Select lines with multiple spaces
```

## Examples

### Log File Analysis
```
load "app.log"
show "error"                    # View all errors
count "error"                   # Count errors
select "2024-01"                # Filter by date
statistics                      # Get summary stats
save "errors_2024-01.log"
```

### Data Cleaning
```
load "data.csv"
remove_empty_lines              # Remove blank lines
trim_whitespace                 # Clean spacing
convert_case lower              # Normalize case
unique                          # Remove duplicates
sort                            # Organize
csv_to_table ","                # Verify format
save "cleaned_data.csv"
```

### Configuration File Processing
```
load "config.yaml"
select_indented "database:"     # Extract database section
show                            # Review
replace "localhost" "prod.server"  # Update
save "config_prod.yaml"
```

### Email List Generation
```
load "template.txt"
placeholder_replace "{{EMAIL}}" "{{NAME}}" "emails.txt"
# Generates personalized version for each row
save "personalized_emails.txt"
```

## Command Help

Every command includes built-in help:

```
command ?                   # Show detailed help for command
help command                # Alternative help syntax
cheat_sheet_regex           # Display regex reference
tutorial                    # Interactive tutorial
```

## Keyboard Shortcuts

### Live View
| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save file |
| Ctrl+F | Find/Search |
| Ctrl+R | Replace dialog |
| F3 | Find next |
| Shift+F3 | Find previous |
| Tab | Indent selected lines |
| Shift+Tab | Unindent selected lines |

## Requirements & Dependencies

- `cmd2`: CLI framework
- `regex`: Advanced regular expressions
- `pandas`: Excel file handling
- `openpyxl`: Excel support
- `win32clipboard`: Clipboard access (Windows)

Auto-installed on first run.

## Performance Tips

- **Large files**: Disable highlighting with the `Highlight` toggle in Live View
- **Complex regex**: Test patterns with `show` before `replace`
- **Bulk operations**: Use `select` first to reduce processing scope
- **Memory**: Process files in sections rather than all at once

## Troubleshooting

**Issue: Clipboard not working**
- Ensure clipboard content is plain text
- Use `load "file.txt"` as alternative

**Issue: Regex not matching**
- Use `cheat_sheet_regex` for pattern help
- Test simple patterns first
- Remember to escape special characters

**Issue: Large file is slow**
- Disable highlighting in Live View
- Use `select` to work with smaller subsets
- Consider processing in multiple passes

**Issue: Special characters causing issues**
- Use special placeholders: `[pipe]`, `[tab]`, `[spaces]`
- Or escape with backslash: `\\|`, `\\t`

## Best Practices

1. **Always preview before save**: Use `show` to verify changes
2. **Use revert frequently**: Test operations knowing you can undo
3. **Save intermediate results**: Keep backups of important stages
4. **Test regex patterns**: Start simple, build complexity gradually
5. **Document your workflow**: Save command history for reference
6. **Use comments**: Add notes between operations for clarity

## Contributing

Contributions welcome! Please:
- Test thoroughly before submitting
- Document new features clearly
- Follow existing code style
- Update README with new commands

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the interactive tutorial: `tutorial`

## Version History

**Latest Version**: 1.0.0
- Full feature set for text processing
- Real-time Live View editor
- Advanced regex support
- Batch processing capabilities
- Comprehensive command library

---

**Happy text processing!** 🚀
