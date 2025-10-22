# TextTool - Advanced Text Manipulation Tool

TextTool is a powerful command-line tool designed for advanced text manipulation. It allows users to load, modify, and save text files or clipboard content with a wide range of features, including regex support, text replacement, line selection, and more.

## Features

- **Load Content**: Load text from a file or clipboard.
- **Show Lines**: Display lines containing specific strings or regex patterns.
- **Select Lines**: Select lines based on specific criteria (e.g., containing or not containing a string).
- **Replace Text**: Replace strings or regex patterns with new text, including support for capture groups.
- **Save Content**: Save modified text to a file or overwrite the original file.
- **Revert Changes**: Undo the last replace or select action.
- **Regex Support**: All commands support regex patterns for advanced text manipulation.
- **Clipboard Integration**: Load and save content directly from/to the clipboard.
- **History**: Command history is preserved across sessions.
- **Advanced Features**: Includes functions like extracting emails, URLs, trimming whitespace, converting case, and more.

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required libraries using pip:

   ```bash
   pip install cmd2 regex pandas win32clipboard
   ```

## Usage

Run the script using Python:

```bash
python TextTool.py
```

## Main Commands

- `load <file_path>`: Load a text file from the specified path.
- `load`: Load content from the clipboard.
- `show <string>`: Show lines containing the specified string or regex.
- `select <string>`: Select lines containing the specified string or regex.
- `replace "string1" "string2"`: Replace `string1` with `string2`.
- `save <file_path>`: Save the modified text to the specified file.
- `save`: Overwrite the original file with the modified text.
- `revert`: Revert the last replace or select action.
- `exit`: Exit the tool.

## Examples

**Load a file:**
```bash
TextTool> load "C:/example.txt"
```

**Show lines containing "error":**
```bash
TextTool> show "error"
```

**Replace "error" with "warning":**
```bash
TextTool> replace "error" "warning"
```

**Save the modified text:**
```bash
TextTool> save "C:/output.txt"
```

**Revert the last action:**
```bash
TextTool> revert
```

## Advanced Features

To enable advanced features, use the `advanced` command:
```bash
TextTool> advanced
```
This will unlock additional commands such as:

- `extract_emails`: Extract all email addresses from the text.
- `extract_urls`: Extract all URLs from the text.
- `trim_whitespace`: Trim leading and trailing whitespace from each line.
- `convert_case <upper|lower|title>`: Convert the text to uppercase, lowercase, or title case.
- `reverse_lines`: Reverse the order of lines in the text.

To disable advanced features, use the `standard` command:
```bash
TextTool> standard
```

## Tutorial
To start an interactive tutorial, type:
```bash
TextTool> tutorial
```
The tutorial will guide you through the main features of the tool with real examples.

## Regex Cheat Sheet
To display a regex cheat sheet, type:
```bash
TextTool> cheat_sheet_regex
```
This will provide examples and explanations for common regex patterns, quantifiers, anchors, character classes, groups, and special characters.

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
Happy text processing with **TextTool**! 🚀
