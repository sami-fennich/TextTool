import importlib
import subprocess
import sys
import inspect
import shlex

# List of required libraries
required_libraries = ['cmd2', 'regex', 'os','pandas','shlex','inspect']

def install_library(library):
    """Install a library using pip."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', library])

def check_and_install_libraries():
    """Check if the required libraries are installed, and install them if not."""
    for library in required_libraries:
        try:
            # Try to import the library
            importlib.import_module(library)
            #print(f"{library} is already installed.")
        except ImportError:
            # If the library is not installed, install it
            print(f"{library} is not installed. Installing...")
            install_library(library)
            print(f"{library} has been installed.")

# Check and install required libraries
check_and_install_libraries()
_unquote = lambda s: s[1:-1] if s[0] == '"' == s[-1] else s

import cmd2
import regex as re
import os




def read_mapping_file(map_file, separator):
    import sys
    import os
    import pandas as pd  # Required for reading Excel files       
    """Read the mapping file and return a dictionary of replacements."""
    if map_file.lower().endswith(('.xls', '.xlsx')):
        # Handle Excel files
        df = pd.read_excel(map_file, usecols=[0, 1], header=None)  # Read first two columns
        return dict(zip(df[0], df[1]))
    else:
        # Handle text files
        if separator.lower() == "tab":
            separator = "\t"
        elif separator.lower() == "space":
            separator = " "
        
        replacements = {}
        with open(map_file, "r", encoding="utf-8") as map_f:
            for line in map_f:
                if separator in line:
                    parts = line.strip().split(separator, 1)
                    if len(parts) == 2:
                        key, value = parts
                        replacements[key] = value
        return replacements

def remove_spaces(s):
    return change_inside_quotes(s, ' ', 'hahi')

def retrieve_spaces(s):
    return change_inside_quotes(s, 'hahi', ' ')

class TextTool(cmd2.Cmd):
    def __init__(self):
        super().__init__(persistent_history_file=".text_tool_history.txt")
        self.text_lines = []
        self.current_lines = []
        self.previous_lines = []
        self.original_full_text = []
        self.selected_indices = []
        self.COLOR_HEADER = "\033[1;36m"  # Cyan
        self.COLOR_COMMAND = "\033[1;32m"  # Green
        self.COLOR_EXAMPLE = "\033[1;33m"  # Yellow
        self.COLOR_RESET = "\033[0m"  # Reset to default color        
        self.original_file_path = "c:/clipboard.txt"  # Default file path for clipboard content
        self.prompt= "TextTool> "
        self.intro = (
            f"{self.COLOR_HEADER}Welcome to the Text Manipulation Tool!{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}New to the tool? Type 'tutorial' to start an interactive guide!{self.COLOR_RESET}\n\n"
            "This tool allows you to perform advanced operations on text files or clipboard content.\n\n"
            f"{self.COLOR_HEADER}Main Features:{self.COLOR_RESET}\n"
            f"1. {self.COLOR_COMMAND}Load Content{self.COLOR_RESET}:\n"
            "   - Load a text file: " + f"{self.COLOR_COMMAND}`load <file_path>`{self.COLOR_RESET}\n"
            "   - Load from clipboard: " + f"{self.COLOR_COMMAND}`load`{self.COLOR_RESET} (no arguments)\n\n"
            f"2. {self.COLOR_COMMAND}Show Lines{self.COLOR_RESET}:\n"
            "   - Show all lines: " + f"{self.COLOR_COMMAND}`show`{self.COLOR_RESET}\n"
            "   - Show lines containing a string or regex: " + f"{self.COLOR_COMMAND}`show <string>`{self.COLOR_RESET}\n"
            "   - Show lines containing multiple strings/regex: " + f"{self.COLOR_COMMAND}`show \"string1 OR string2\"`{self.COLOR_RESET}\n\n"
            f"3. {self.COLOR_COMMAND}Select Lines{self.COLOR_RESET}:\n"
            "   - Select lines containing a string or regex: " + f"{self.COLOR_COMMAND}`select <string>`{self.COLOR_RESET}\n"
            "   - Select lines NOT containing a string/regex: " + f"{self.COLOR_COMMAND}`select \"!string1\"`{self.COLOR_RESET}\n"
            "   - Select lines containing multiple strings/regex: " + f"{self.COLOR_COMMAND}`select \"string1 OR string2\"`{self.COLOR_RESET}\n\n"
            f"4. {self.COLOR_COMMAND}Unselect Lines{self.COLOR_RESET}:\n"
            "   - Revert the last select action while keeping other replace modifications: " + f"{self.COLOR_COMMAND}`unselect`{self.COLOR_RESET}\n\n"
            f"5. {self.COLOR_COMMAND}Replace Text{self.COLOR_RESET}:\n"
            "   - Replace a string with another: " + f"{self.COLOR_COMMAND}`replace \"string1\" \"string2\"`{self.COLOR_RESET}\n"
            "   - Supports " + f"{self.COLOR_COMMAND}regex patterns{self.COLOR_RESET} and " + f"{self.COLOR_COMMAND}capture groups{self.COLOR_RESET}:\n"
            "     - Example: Replace dates (dd-mm-yyyy) with (yyyy/mm/dd):\n"
            "       " + f"{self.COLOR_EXAMPLE}`replace \"(\\d{{2}})-(\\d{{2}})-(\\d{{4}})\" \"\\3/\\2/\\1\"`{self.COLOR_RESET}\n"
            "     - Example: Replace all occurrences of 'error' with 'warning':\n"
            "       " + f"{self.COLOR_EXAMPLE}`replace \"error\" \"warning\"`{self.COLOR_RESET}\n"
            "     - Example: Insert a newline after each sentence:\n"
            "       " + f"{self.COLOR_EXAMPLE}`replace \"([.!?]) \" \"\\1\\n\"`{self.COLOR_RESET}\n\n"
            f"6. {self.COLOR_COMMAND}Save Content{self.COLOR_RESET}:\n"
            "   - Save to a new file: " + f"{self.COLOR_COMMAND}`save <file_path>`{self.COLOR_RESET}\n"
            "   - Overwrite the original file: " + f"{self.COLOR_COMMAND}`save`{self.COLOR_RESET} (no arguments)\n\n"
            f"7. {self.COLOR_COMMAND}Revert Changes{self.COLOR_RESET}:\n"
            "   - Undo the last action: " + f"{self.COLOR_COMMAND}`revert`{self.COLOR_RESET}\n\n"
            f"8. {self.COLOR_COMMAND}Exit the Tool{self.COLOR_RESET}:\n"
            "   - Exit the application: " + f"{self.COLOR_COMMAND}`exit`{self.COLOR_RESET}\n\n"
            f"{self.COLOR_HEADER}Advanced Features:{self.COLOR_RESET}\n"
            f"- {self.COLOR_COMMAND}Regex Support{self.COLOR_RESET}: All commands (`show`, `select`, `replace`) support regex patterns. You can use the command cheat_sheet_regex for regex help.\n"
            f"- {self.COLOR_COMMAND}Capture Groups{self.COLOR_RESET}: Use `\\1`, `\\2`, etc., in `replace` to reference capture groups.\n"
            f"- {self.COLOR_COMMAND}Clipboard Integration{self.COLOR_RESET}: Load and save content directly from/to the clipboard.\n"
            f"- {self.COLOR_COMMAND}History{self.COLOR_RESET}: Command history is preserved across sessions.\n\n"
            f"{self.COLOR_HEADER}Examples:{self.COLOR_RESET}\n"
            f"- Load a file: {self.COLOR_EXAMPLE}`load \"C:/example.txt\"`{self.COLOR_RESET}\n"
            f"- Show lines containing 'error': {self.COLOR_EXAMPLE}`show \"error\"`{self.COLOR_RESET}\n"
            f"- Replace 'error' with 'warning': {self.COLOR_EXAMPLE}`replace \"error\" \"warning\"`{self.COLOR_RESET}\n"
            f"- Save the modified text: {self.COLOR_EXAMPLE}`save \"C:/output.txt\"`{self.COLOR_RESET}\n"
            f"- Revert the last action: {self.COLOR_EXAMPLE}`revert`{self.COLOR_RESET}\n"
            f"- Unselect the last selection: {self.COLOR_EXAMPLE}`unselect`{self.COLOR_RESET}\n\n"
            f"{self.COLOR_HEADER}Advanced Functions (Enable with `advanced` command):{self.COLOR_RESET}\n"
            "This tool also provides additional advanced text processing functions, which are disabled by default.\n"
            f"To enable them, use `{self.COLOR_COMMAND}advanced{self.COLOR_RESET}`.\n\n"
            "Once enabled, you can use the following commands:\n\n"
            f"- {self.COLOR_COMMAND}extract_between{self.COLOR_RESET}: Extract text between two patterns.\n"
            f"- {self.COLOR_COMMAND}insert_line{self.COLOR_RESET}: Insert a new line at a specific position.\n"
            f"- {self.COLOR_COMMAND}merge_lines{self.COLOR_RESET}: Merge multiple lines into a single line.\n"
            f"- {self.COLOR_COMMAND}split_lines{self.COLOR_RESET}: Split lines using a specified delimiter.\n"
            f"- {self.COLOR_COMMAND}convert_case{self.COLOR_RESET}: Change text case (upper, lower, title).\n"
            f"- {self.COLOR_COMMAND}trim_whitespace{self.COLOR_RESET}: Remove leading and trailing spaces.\n"
            f"- {self.COLOR_COMMAND}reverse_lines{self.COLOR_RESET}: Reverse the order of lines.\n"
            f"- {self.COLOR_COMMAND}extract_emails{self.COLOR_RESET}: Extract email addresses from text.\n"
            f"- {self.COLOR_COMMAND}extract_urls{self.COLOR_RESET}: Extract URLs from text.\n"
            f"- {self.COLOR_COMMAND}replace_confirm{self.COLOR_RESET}: Interactive find-and-replace with user confirmation.\n"
            f"- {self.COLOR_COMMAND}replace_in_lines{self.COLOR_RESET}: Replace text only in matching lines.\n"
			f"- {self.COLOR_COMMAND}multiple_replace{self.COLOR_RESET}: Replace multiple strings in the current text using a mapping file.\n"
            f"- {self.COLOR_COMMAND}select_from_file{self.COLOR_RESET}: Select lines containing strings from a file.\n\n"
            f"To disable these functions and return to standard mode, use `{self.COLOR_COMMAND}standard{self.COLOR_RESET}`.\n\n"			
            f"{self.COLOR_COMMAND}Remember: Type 'tutorial' for an interactive guide through these features!{self.COLOR_RESET}\n\n"
            f"Type {self.COLOR_COMMAND}`[command] ?`{self.COLOR_RESET} for more details on each command.\n"
        )
        self.hidden_commands.append('shortcuts')
        self.hidden_commands.append('shell')
        #self.hidden_commands.append('run_script')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('set')
        self.hidden_commands.append('macro')
        self.hidden_commands.append('edit')
        self.hidden_commands.append('extract_between')
        self.hidden_commands.append('insert_line')
        self.hidden_commands.append('merge_lines')
        self.hidden_commands.append('split_lines')
        self.hidden_commands.append('convert_case')
        self.hidden_commands.append('trim_whitespace')
        self.hidden_commands.append('reverse_lines')
        self.hidden_commands.append('extract_emails')
        self.hidden_commands.append('extract_urls')
        self.hidden_commands.append('replace_confirm')
        self.hidden_commands.append('replace_in_lines')
        self.hidden_commands.append('select_from_file')	
        self.hidden_commands.append('multiple_replace')			

        



    def myhookmethod(self, params: cmd2.plugin.PostparsingData) -> cmd2.plugin.PostparsingData:
            #complete_mutliple_replace = cmd2.Cmd.path_complete
            from pathlib import Path
            if 'grep' in params.statement.raw:
                  script_path = Path(__file__).resolve()
                  script_dir = script_path.parent
                  newinput = params.statement.raw.replace('grep ', script_dir+ '\\grep.exe ')
                  params.statement = self.statement_parser.parse(newinput)
            return params


    def do_tutorial(self, arg):
        """Start an interactive tutorial that demonstrates how to use the Text Tool.

        Usage:
            tutorial  - Start the interactive tutorial.

        Notes:
            - Press Enter to advance through each step of the tutorial.
            - The tutorial includes real examples and demonstrates key features.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nStart an interactive tutorial that demonstrates how to use the Text Tool.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}tutorial{self.COLOR_RESET}  - Start the interactive tutorial.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - Press Enter to advance through each step of the tutorial.\n"
            f"  - The tutorial includes real examples and demonstrates key features.\n"
        )
        if arg.strip() == "?":
            self.poutput(help_text)
            return

        # Sample text for the tutorial
        sample_text = [
            "Error: Database connection failed at 12-05-2023\n",
            "Warning: Cache miss in user session\n",
            "Error: Invalid credentials provided\n",
            "Info: System startup completed at 15-05-2023\n",
            "Warning: High CPU usage detected\n",
            "Error: Database timeout after 30 seconds\n",
            "Info: Backup completed successfully\n",
            "Warning: Low disk space on drive C:\n",
            "\n",
            "Error: Connection timeout at 18-05-2023\n"
        ]

        tutorial_steps = [
            (
                f"{self.COLOR_HEADER}Welcome to the Text Tool Tutorial!{self.COLOR_RESET}\n"
                "This tutorial will guide you through the main features of the Text Tool.\n"
                "Press Enter after each step to continue..."
            ),
            (
                f"{self.COLOR_HEADER}1. Loading Text{self.COLOR_RESET}\n"
                "There are two ways to load text into the tool:\n\n"
                f"a) From a file:\n{self.COLOR_COMMAND}TextTool> load \"path/to/file.txt\"{self.COLOR_RESET}\n\n"
                f"b) From clipboard:\n{self.COLOR_COMMAND}TextTool> load{self.COLOR_RESET}\n\n"
                "For this tutorial, we'll use a sample text with log entries."
            ),
            (
                f"{self.COLOR_HEADER}2. Showing Text{self.COLOR_RESET}\n"
                f"To display all loaded text:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n\n"
                "Here's our sample text:"
            ),
            (
                f"{self.COLOR_HEADER}3. Filtering Text{self.COLOR_RESET}\n"
                f"To show only lines containing specific text:\n{self.COLOR_COMMAND}TextTool> show \"Error\"{self.COLOR_RESET}\n\n"
                "This will show only error messages:"
            ),
            (
                f"{self.COLOR_HEADER}4. Multiple Pattern Matching{self.COLOR_RESET}\n"
                f"To show lines containing either of two patterns:\n{self.COLOR_COMMAND}TextTool> show \"Error OR Warning\"{self.COLOR_RESET}\n\n"
                "This will show both errors and warnings:"
            ),
            (
                f"{self.COLOR_HEADER}5. Copying Output to Clipboard{self.COLOR_RESET}\n"
                f"Add '>' after any show command to copy the output to clipboard:\n{self.COLOR_COMMAND}TextTool> show \"Error\" >{self.COLOR_RESET}\n\n"
                "The matching lines will be copied to your clipboard."
            ),
            (
                f"{self.COLOR_HEADER}6. Selecting Lines{self.COLOR_RESET}\n"
                f"Select lines for further operations:\n{self.COLOR_COMMAND}TextTool> select \"Error\"{self.COLOR_RESET}\n\n"
                "This selects only the error messages for subsequent operations.\n"
                f"\nLet's see the selected lines:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n"
            ),
            (
                f"{self.COLOR_HEADER}7. Text Replacement{self.COLOR_RESET}\n"
                f"Replace text in the selected lines:\n{self.COLOR_COMMAND}TextTool> replace \"Error\" \"Critical\"{self.COLOR_RESET}\n\n"
                f"Let's see the result:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n"
            ),
            (
                f"{self.COLOR_HEADER}8. Advanced Regex Replacement{self.COLOR_RESET}\n"
                f"Use regex to change date format:\n{self.COLOR_COMMAND}TextTool> replace \"(\\d{{2}})-(\\d{{2}})-(\\d{{4}})\" \"\\3/\\2/\\1\"{self.COLOR_RESET}\n\n"
                f"Let's see the result:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n"
            ),
            (
                f"{self.COLOR_HEADER}9. Reverting Changes{self.COLOR_RESET}\n"
                f"To undo the last operation:\n{self.COLOR_COMMAND}TextTool> revert{self.COLOR_RESET}\n\n"
                f"Let's see the reverted text:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n"
            ),
            (
                f"{self.COLOR_HEADER}10. Sorting and Removing Duplicates{self.COLOR_RESET}\n"
                f"Sort all lines:\n{self.COLOR_COMMAND}TextTool> sort{self.COLOR_RESET}\n\n"
                f"Let's see the sorted text:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}\n\n"
                f"Remove duplicate lines:\n{self.COLOR_COMMAND}TextTool> unique{self.COLOR_RESET}\n\n"
                f"Let's see the result:\n{self.COLOR_COMMAND}TextTool> show{self.COLOR_RESET}"
            ),
            (
                f"{self.COLOR_HEADER}11. Saving Results{self.COLOR_RESET}\n"
                f"Save to a new file:\n{self.COLOR_COMMAND}TextTool> save \"output.txt\"{self.COLOR_RESET}\n\n"
                f"Or overwrite the original file:\n{self.COLOR_COMMAND}TextTool> save{self.COLOR_RESET}"
            ),
            (
                f"{self.COLOR_HEADER}Tutorial Completed!{self.COLOR_RESET}\n"
                "You've learned the main features of the Text Tool. Some additional tips:\n\n"
                "- Use 'help <command>' for detailed information about any command\n"
                "- Use 'cheat_sheet_regex' for regex pattern help\n"
                "- Remember you can copy output to clipboard with '>'\n"
                "- You can follow any command with ? in order to get help\n\n"                
                "Happy text processing!"
            )
        ]

        # Store the original lines
        original_lines = self.current_lines.copy() if self.current_lines else []

        try:
            # Go through each tutorial step
            for i, step in enumerate(tutorial_steps, 1):
                self.poutput("\n" + step)
                
                # Set sample text as current text
                if i == 3:
                    self.current_lines = sample_text.copy()
                    self.poutput("\n" + "".join(self.current_lines))
                
                # Show filtered results for error messages
                elif i == 4:
                    error_lines = [line for line in sample_text if "Error" in line]
                    self.poutput("\n" + "".join(error_lines))
                
                # Show filtered results for errors and warnings
                elif i == 5:
                    error_warning_lines = [line for line in sample_text if "Error" in line or "Warning" in line]
                    self.poutput("\n" + "".join(error_warning_lines))

                # Select error lines
                elif i == 7:
                    self.current_lines = sample_text.copy()
                    selected_lines = [line for line in self.current_lines if "Error" in line]
                    self.current_lines = selected_lines
                    self.poutput("\nSelected lines:")
                    self.poutput("".join(self.current_lines))

                # Replace Error with Critical
                elif i == 8:
                    self.current_lines = [line.replace("Error", "Critical") for line in self.current_lines]
                    self.poutput("\nAfter replacement:")
                    self.poutput("".join(self.current_lines))

                # Change date format
                elif i == 9:
                    import re
                    self.current_lines = [re.sub(r"(\d{2})-(\d{2})-(\d{4})", r"\3/\2/\1", line) for line in self.current_lines]
                    self.poutput("\nAfter date format change:")
                    self.poutput("".join(self.current_lines))

                # Revert changes
                elif i == 10:
                    self.current_lines = [line.replace("Critical", "Error").replace("2023/05/12", "12-05-2023").replace("2023/05/18", "18-05-2023") for line in self.current_lines]
                    self.poutput("\nAfter reverting:")
                    self.poutput("".join(self.current_lines))

                # Sort and remove duplicates
                elif i == 11:
                    # First show sorted
                    self.current_lines.sort()
                    self.poutput("\nAfter sorting:")
                    self.poutput("".join(self.current_lines))
                    
                    # Then show after removing duplicates
                    self.current_lines = list(dict.fromkeys(self.current_lines))
                    self.poutput("\nAfter removing duplicates:")
                    self.poutput("".join(self.current_lines))

                input("\nPress Enter to continue...")

        finally:
            # Restore the original lines
            self.current_lines = original_lines

    def do_load(self, arg):
        """Load a text file or clipboard content for operations.

        Usage:
            load <file_path>  - Load a text file from the specified path.
            load             - Load content from the clipboard.

        Examples:
            load "C:/example.txt"  - Loads the file 'example.txt'.
            load                  - Loads content from the clipboard.

        Notes:
            - If no file path is provided, the tool will attempt to load text from the clipboard.
            - The clipboard content will be treated as a list of lines.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nLoad a text file or clipboard content for operations.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}load <file_path>{self.COLOR_RESET}  - Load a text file from the specified path.\n"
            f"  {self.COLOR_EXAMPLE}load{self.COLOR_RESET}             - Load content from the clipboard.\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}load \"C:/example.txt\"{self.COLOR_RESET}  - Loads the file 'example.txt'.\n"
            f"  {self.COLOR_EXAMPLE}load{self.COLOR_RESET}                  - Loads content from the clipboard.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - If no file path is provided, the tool will attempt to load text from the clipboard.\n"
            f"  - The clipboard content will be treated as a list of lines.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if arg:
            # Remove surrounding quotes if present
            file_path = arg.strip('"')

            if not os.path.exists(file_path):
                self.poutput(f"Error: File '{file_path}' does not exist.")
                return

            with open(file_path, 'r') as file:
                self.text_lines = file.readlines()
                self.current_lines = self.text_lines.copy()
            self.original_file_path = file_path  # Store the original file path
            self.poutput(f"File '{file_path}' loaded successfully.")
        else:
            # Load content from the clipboard
            clipboard_content = cmd2.clipboard.get_paste_buffer()
            if clipboard_content:
                self.text_lines = [ s.replace("\r","") for s in clipboard_content.splitlines(keepends=True)]
                self.current_lines = self.text_lines.copy()
                self.original_file_path = None  # No file path for clipboard content
                self.poutput("Clipboard content loaded successfully.")
            else:
                self.poutput("Error: Clipboard is empty or does not contain text.")

    def do_show(self, arg):
        """Show lines containing the given string(s) or regex pattern(s).

        Usage:
            show <string>         - Show lines containing the specified string or regex.
            show "string1 OR string2" - Show lines containing either string1 or string2.

        Examples:
            show "error"          - Shows all lines containing the word "error".
            show "error OR warning" - Shows lines containing either "error" or "warning".

        Notes:
            - The search is case-sensitive.
            - Supports regex patterns for more complex searches.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nShow lines containing the given string(s) or regex pattern(s).{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}show <string>{self.COLOR_RESET}         - Show lines containing the specified string or regex.\n"
            f"  {self.COLOR_EXAMPLE}show \"string1 OR string2\"{self.COLOR_RESET} - Show lines containing either string1 or string2.\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}show \"error\"{self.COLOR_RESET}          - Shows all lines containing the word \"error\".\n"
            f"  {self.COLOR_EXAMPLE}show \"error OR warning\"{self.COLOR_RESET} - Shows lines containing either \"error\" or \"warning\".\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - The search is case-sensitive.\n"
            f"  - Supports regex patterns for more complex searches.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # Extract the raw input string from the cmd2.parsing.Statement object
        if hasattr(arg, 'args'):
            arg = arg.args

        if not arg:
            self.poutput(''.join(self.current_lines))
            return

        # Remove surrounding quotes if present
        arg = arg.strip('"').strip("'")

        # Split the input string on the keyword "OR"
        search_terms = [term.strip() for term in arg.split("OR")]

        try:
            # Compile regex patterns for each search term
            regexes = [re.compile(term) for term in search_terms]
            # Find lines that match any of the regex patterns
            matching_lines = [
                line for line in self.current_lines
                if any(regex.search(line) for regex in regexes)
            ]
            if matching_lines:
                self.poutput(''.join(matching_lines))
            else:
                self.poutput("No lines matched the pattern.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")



    def do_select(self, arg):
        """Select lines containing (or not containing) the given string(s) or regex pattern(s).

        Usage:
            select <string>         - Select lines containing the specified string or regex.
            select "!string"        - Select lines that do NOT contain the specified string or regex.
            select "string1 OR string2" - Select lines containing either string1 or string2.

        Special Placeholders:
            - Use [pipe] instead of the pipe character (|) in your input.
            - Use [doublequote] instead of double quotes (") in your input.
            - Use [quote] instead of quotes (') in your input.
            - Use [tab] instead of tabulation character in your input.
            - Use [spaces] to match one or more spaces (all kind of spaces)

        Examples:
            select "error"          - Selects lines containing the word "error".
            select "!error"         - Selects lines that do NOT contain the word "error".
            select "error OR warning" - Selects lines containing either "error" or "warning".

        Notes:
            - The selection is case-sensitive.
            - Supports regex patterns for more complex selections.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nSelect lines containing (or not containing) the given string(s) or regex pattern(s).{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}select <string>{self.COLOR_RESET}         - Select lines containing the specified string or regex.\n"
            f"  {self.COLOR_EXAMPLE}select \"!string\"{self.COLOR_RESET}        - Select lines that do NOT contain the specified string or regex.\n"
            f"  {self.COLOR_EXAMPLE}select \"string1 OR string2\"{self.COLOR_RESET} - Select lines containing either string1 or string2.\n\n"
            f"{self.COLOR_COMMAND}Special Placeholders:{self.COLOR_RESET}\n"
            f"  - Use {self.COLOR_EXAMPLE}[pipe]{self.COLOR_RESET} instead of the pipe character (|) in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[doublequote]{self.COLOR_RESET} instead of double quotes (\") in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[quote]{self.COLOR_RESET} instead of quotes (') in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[tab]{self.COLOR_RESET} instead of tabulation character in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[spaces]{self.COLOR_RESET} to match one or more spaces (all kind of spaces).\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}select \"error\"{self.COLOR_RESET}          - Selects lines containing the word \"error\".\n"
            f"  {self.COLOR_EXAMPLE}select \"!error\"{self.COLOR_RESET}         - Selects lines that do NOT contain the word \"error\".\n"
            f"  {self.COLOR_EXAMPLE}select \"error OR warning\"{self.COLOR_RESET} - Selects lines containing either \"error\" or \"warning\".\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - The selection is case-sensitive.\n"
            f"  - Supports regex patterns for more complex selections.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()
        # Save the current state for unselect functionality
        self.original_full_text = self.current_lines.copy()
        self.selected_indices = []

        # Extract the raw input string from the cmd2.parsing.Statement object
        if hasattr(arg, 'args'):
            arg = arg.args

        if not arg:
            #self.poutput("Error: Please provide a string or regex.")
            #return
            arg=""

        # Remove surrounding quotes if present
        arg = arg.strip('"').strip("'")

        # Check if the selection is negated (e.g., "!string1")
        negate = False
        if arg.startswith("!"):
            negate = True
            arg = arg[1:]  # Remove the "!" prefix

        # Split the input string on the keyword "OR"
        search_terms = [term.strip() for term in arg.split("OR")]

        try:
            # Compile regex patterns for each search term
            regexes = [re.compile(term.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+")) for term in search_terms]
            if negate:
                # Select lines that do NOT match any of the regex patterns
                self.current_lines = [
                    line for line in self.current_lines
                    if not any(regex.search(line) for regex in regexes)
                ]
                self.selected_indices = [
                    i for i, line in enumerate(self.original_full_text)
                    if not any(regex.search(line) for regex in regexes)
                ]
            else:
                # Select lines that match any of the regex patterns
                self.current_lines = [
                    line for line in self.current_lines
                    if any(regex.search(line) for regex in regexes)
                ]
                self.selected_indices = [
                    i for i, line in enumerate(self.original_full_text)
                    if any(regex.search(line) for regex in regexes)
                ]
            self.poutput(f"Selected {len(self.current_lines)} lines.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")


    def do_unselect(self, arg):
        """Revert the last select action while keeping other modifications.

        Usage:
            unselect  - Reverts the last select action.

        Notes:
            - This command restores the original full text but overwrites the selected lines with their modified versions.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nRevert the last select action while keeping other modifications.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}unselect{self.COLOR_RESET}  - Reverts the last select action.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - This command restores the original full text but overwrites the selected lines with their modified versions.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not hasattr(self, 'original_full_text') or not self.original_full_text:
            self.poutput("Error: No original full text to revert to.")
            return
        if not hasattr(self, 'selected_indices') or not self.selected_indices:
            self.poutput("Error: No selected lines to revert.")
            return

        # Restore the original full text
        self.previous_lines = self.current_lines.copy()
        restored_text = self.original_full_text.copy()

        # Overwrite the selected lines with their modified versions
        for i, modified_line in zip(self.selected_indices, self.current_lines):
            if i < len(restored_text):
                restored_text[i] = modified_line

        # Update the current lines
        self.current_lines = restored_text
        self.poutput("Reverted to the original full text with modified selected lines.")
    

    def do_multiple_replace(self, arg):
        """Replace multiple strings in the current text using a mapping file.

        Usage:
            multiple_replace <map_file> [separator] [ > output_file ]

        Arguments:
            <map_file>     - Path to the mapping file (can be a text file or Excel file with two columns).
            <separator>    - Separator for text mapping files. Use "tab" for tab characters, "space" for spaces,
                             or a specific character. If the map file is an Excel file, this is ignored. Default value is "space".

        Description:
            This function replaces all occurrences of text found in the first column of the mapping file
            with the corresponding text in the second column. The separator determines how the columns in the
            mapping file are parsed (ignored for Excel files).

        Examples:
            multiple_replace map.txt tab  - Replaces text using a tab-separated mapping file.
            multiple_replace map.xlsx     - Replaces text using an Excel mapping file.
            multiple_replace map.xlsx > output.txt - Saves the output to 'output.txt'.
            multiple_replace map.xlsx >   - Outputs the result to the clipboard.

        Notes:
            - The mapping file should have two columns: the first column contains the text to be replaced,
              and the second column contains the replacement text.
            - For Excel files, only the first two columns are used.
        """
        import sys
        import os
        import pandas as pd  # Required for reading Excel files    
        help_text = (
            f"{self.COLOR_HEADER}\nReplace multiple strings in the current text using a mapping file.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace <map_file> [separator] [ > output_file ]{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Arguments:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}<map_file>{self.COLOR_RESET}     - Path to the mapping file (can be a text file or Excel file with two columns).\n"
            f"  {self.COLOR_EXAMPLE}<separator>{self.COLOR_RESET}    - Separator for text mapping files. Use \"tab\" for tab characters, \"space\" for spaces,\n"
            f"                     or a specific character. If the map file is an Excel file, this is ignored. Default value is \"space\".\n\n"
            f"{self.COLOR_COMMAND}Description:{self.COLOR_RESET}\n"
            f"  This function replaces all occurrences of text found in the first column of the mapping file\n"
            f"  with the corresponding text in the second column. The separator determines how the columns in the\n"
            f"  mapping file are parsed (ignored for Excel files).\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace map.txt tab{self.COLOR_RESET}  - Replaces text using a tab-separated mapping file.\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace map.xlsx{self.COLOR_RESET}     - Replaces text using an Excel mapping file.\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace map.xlsx > output.txt{self.COLOR_RESET} - Saves the output to 'output.txt'.\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace map.xlsx >{self.COLOR_RESET}   - Outputs the result to the clipboard.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - The mapping file should have two columns: the first column contains the text to be replaced,\n"
            f"    and the second column contains the replacement text.\n"
            f"  - For Excel files, only the first two columns are used.\n"
        )
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function        
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return
        self.previous_lines = self.current_lines.copy()

        try:
            arg=arg.args
        except:
            a=0 
        arg=remove_spaces(arg)  
        if len(arg.split())==2:
            separator = _unquote(arg.split()[1])
        elif len(arg.split())==1:
            separator="space"
        else:
            self.poutput(help_text)
            return
        #input_file=_unquote(retrieve_spaces(arg.split()[0]))
        map_file=_unquote(retrieve_spaces(arg.split()[0]))
        #if not os.path.exists(input_file):
            #print(f"Error: Input file '{input_file}' does not exist.")
            #sys.exit(1)
        if not os.path.exists(map_file):
            print(f"Error: Mapping file '{map_file}' does not exist.")
            sys.exit(1)  
        replacements = read_mapping_file(map_file, separator)      
        #with open(input_file, "r", encoding="utf-8") as input_f:
            #content = input_f.read()
        for old_text, new_text in replacements.items():
            self.current_lines = [line.replace(old_text, new_text) for line in self.current_lines]
            #content = content.replace(old_text, new_text)  
           
        self.poutput("Replacement completed.")

    def do_replace(self, arg):
        """Replace a string with another in the current text. Supports regex and capture groups.

        Usage:
            replace "string1" "string2"  - Replace string1 with string2.
            replace string1 string2      - Replace string1 with string2 (if no spaces in strings).

        Special Placeholders:
            - Use [pipe] instead of the pipe character (|) in your input.
            - Use [doublequote] instead of double quotes (") in your input.
            - Use [quote] instead of quotes (') in your input.
            - Use [tab] instead of tabulation character in your input.
            - Use [spaces] to match one or more spaces (all kind of spaces)

        Examples:
            replace "error" "warning"  - Replaces all occurrences of "error" with "warning".
            replace "\\d{2}-\\d{2}-\\d{4}" "\\3/\\2/\\1" - Replaces dates in format dd-mm-yyyy with yyyy/mm/dd.
            replace "([.!?]) " "\\1\\n" - Inserts a newline after each sentence.

        Notes:
            - Supports regex patterns and capture groups.
            - Use \\1, \\2, etc., to reference capture groups in the replacement string.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nReplace a string with another in the current text. Supports regex and capture groups.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}replace \"string1\" \"string2\"{self.COLOR_RESET}  - Replace string1 with string2.\n"
            f"  {self.COLOR_EXAMPLE}replace string1 string2{self.COLOR_RESET}      - Replace string1 with string2 (if no spaces in strings).\n\n"
            f"{self.COLOR_COMMAND}Special Placeholders:{self.COLOR_RESET}\n"
            f"  - Use {self.COLOR_EXAMPLE}[pipe]{self.COLOR_RESET} instead of the pipe character (|) in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[doublequote]{self.COLOR_RESET} instead of double quotes (\") in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[quote]{self.COLOR_RESET} instead of quotes (') in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[tab]{self.COLOR_RESET} instead of tabulation character in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[spaces]{self.COLOR_RESET} to match one or more spaces (all kind of spaces).\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}replace \"error\" \"warning\"{self.COLOR_RESET}  - Replaces all occurrences of \"error\" with \"warning\".\n"
            f"  {self.COLOR_EXAMPLE}replace \"\\d{{2}}-\\d{{2}}-\\d{{4}}\" \"\\3/\\2/\\1\"{self.COLOR_RESET} - Replaces dates in format dd-mm-yyyy with yyyy/mm/dd.\n"
            f"  {self.COLOR_EXAMPLE}replace \"([.!?]) \" \"\\1\\n\"{self.COLOR_RESET} - Inserts a newline after each sentence.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - Supports regex patterns and capture groups.\n"
            f"  - Use {self.COLOR_EXAMPLE}\\1, \\2, etc.{self.COLOR_RESET}, to reference capture groups in the replacement string.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # Save the current state for revert functionality
        self.previous_lines = self.current_lines.copy()

        # Extract the raw input string from the cmd2.parsing.Statement object
        if hasattr(arg, 'args'):
            arg = arg.args

        # Replace [pipe] with | and [doublequote] with " in the input
        #arg = arg.replace("[pipe]", "|").replace("[doublequote]", '"')

        # Check if the arguments are quoted
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            string1, string2 = args[1], args[3]
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            string1, string2 = args[1], args[3]            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput("Error: Invalid arguments. Usage: replace \"string1\" \"string2\" OR replace string1 string2")
                return
            string1, string2 = args[0], args[1]

        try:
            # Compile the regex pattern
            regex = re.compile(string1.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"))

            # Replace \0 with the entire match
            if "\\0" in string2:
                def replacement(match):
                    return string2.replace("\\0", match.group(0)).replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+")

                self.current_lines = [regex.sub(replacement, line) for line in self.current_lines]
            else:
                # Perform the replacement using the regex pattern and the replacement string
                self.current_lines = [regex.sub(string2.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"), line) for line in self.current_lines]

            self.poutput("Replacement completed.")
        except re.error as e:
            self.poutput(f"Error: Invalid regex pattern or replacement string. Details: {e}")
            self.poutput(f"Literal replacement will be now tried")
            try:
                self.current_lines = [line.replace(string1.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"), string2.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+")) for line in self.current_lines]
                self.poutput("Literal Replacement completed.")
            except re.error as d:
                self.poutput(f"Literal Replacement failed. Details: {d}")
            
                


    def do_revert(self, arg):
        """Revert the last replace or select action.

        Usage:
            revert  - Reverts the last replace or select action.

        Notes:
            - This command restores the text to its state before the last replace or select operation.
            - Only the last action can be reverted.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nRevert the last replace or select action.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}revert{self.COLOR_RESET}  - Reverts the last replace or select action.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - This command restores the text to its state before the last replace or select operation.\n"
            f"  - Only the last action can be reverted.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not self.previous_lines:
            self.poutput("Error: No previous state to revert to.")
            return

        # Restore the previous state
        self.current_lines = self.previous_lines.copy()
        self.poutput("Reverted to the previous state.")

    def do_cheat_sheet_regex(self, arg):
        """Display an extensive regex cheat sheet with examples and explanations.

        Usage:
            cheat_sheet_regex  - Displays a regex cheat sheet.

        Notes:
            - The cheat sheet provides examples and explanations for common regex patterns,
              quantifiers, anchors, character classes, groups, and special characters.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nDisplay an extensive regex cheat sheet with examples and explanations.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}cheat_sheet_regex{self.COLOR_RESET}  - Displays a regex cheat sheet.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - The cheat sheet provides examples and explanations for common regex patterns,\n"
            f"    quantifiers, anchors, character classes, groups, and special characters.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"

            self.poutput(help_text)
            return  # Exit the function
        cheat_sheet = f"""
    {self.COLOR_HEADER}Regex Cheat Sheet{self.COLOR_RESET}
    
    {self.COLOR_COMMAND}1. Basic Patterns:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`abc`{self.COLOR_RESET}: Matches the exact sequence "abc".
        - {self.COLOR_EXAMPLE}`a OR b`{self.COLOR_RESET}: Matches either "a" or "b".
        - {self.COLOR_EXAMPLE}`[abc]`{self.COLOR_RESET}: Matches any single character from the set "a", "b", or "c".
        - {self.COLOR_EXAMPLE}`[^abc]`{self.COLOR_RESET}: Matches any single character NOT in the set "a", "b", or "c".
        - {self.COLOR_EXAMPLE}`[a-z]`{self.COLOR_RESET}: Matches any single lowercase letter from "a" to "z".
        - {self.COLOR_EXAMPLE}`[A-Z]`{self.COLOR_RESET}: Matches any single uppercase letter from "A" to "Z".
        - {self.COLOR_EXAMPLE}`[0-9]`{self.COLOR_RESET}: Matches any single digit from "0" to "9".
    
    {self.COLOR_COMMAND}2. Quantifiers:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`a*`{self.COLOR_RESET}: Matches zero or more occurrences of "a".
        - {self.COLOR_EXAMPLE}`a+`{self.COLOR_RESET}: Matches one or more occurrences of "a".
        - {self.COLOR_EXAMPLE}`a?`{self.COLOR_RESET}: Matches zero or one occurrence of "a".
        - {self.COLOR_EXAMPLE}`a{{3}}`{self.COLOR_RESET}: Matches exactly 3 occurrences of "a".
        - {self.COLOR_EXAMPLE}`a{{3,}}`{self.COLOR_RESET}: Matches 3 or more occurrences of "a".
        - {self.COLOR_EXAMPLE}`a{{3,5}}`{self.COLOR_RESET}: Matches between 3 and 5 occurrences of "a".
    
    {self.COLOR_COMMAND}3. Anchors:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`^abc`{self.COLOR_RESET}: Matches "abc" only at the start of a line.
        - {self.COLOR_EXAMPLE}`abc$`{self.COLOR_RESET}: Matches "abc" only at the end of a line.
        - {self.COLOR_EXAMPLE}`\Aabc`{self.COLOR_RESET}: Matches "abc" only at the start of the string.
        - {self.COLOR_EXAMPLE}`abc\Z`{self.COLOR_RESET}: Matches "abc" only at the end of the string.
        - {self.COLOR_EXAMPLE}`\bword\b`{self.COLOR_RESET}: Matches "word" as a whole word (word boundary).
    
    {self.COLOR_COMMAND}4. Character Classes:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`\d`{self.COLOR_RESET}: Matches any digit (equivalent to `[0-9]`).
        - {self.COLOR_EXAMPLE}`\D`{self.COLOR_RESET}: Matches any non-digit (equivalent to `[^0-9]`).
        - {self.COLOR_EXAMPLE}`\w`{self.COLOR_RESET}: Matches any word character (alphanumeric + underscore).
        - {self.COLOR_EXAMPLE}`\W`{self.COLOR_RESET}: Matches any non-word character.
        - {self.COLOR_EXAMPLE}`\s`{self.COLOR_RESET}: Matches any whitespace character (space, tab, newline).
        - {self.COLOR_EXAMPLE}`\S`{self.COLOR_RESET}: Matches any non-whitespace character.
        - {self.COLOR_EXAMPLE}`.`{self.COLOR_RESET}: Matches any character except a newline.
    
    {self.COLOR_COMMAND}5. Groups and Capturing:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`(abc)`{self.COLOR_RESET}: Matches "abc" and captures it as a group.
        - {self.COLOR_EXAMPLE}`\\1`{self.COLOR_RESET}: Refers to the first captured group (valid in replacement).
        - {self.COLOR_EXAMPLE}`\\0`{self.COLOR_RESET}: Refers to the entire match (implemented in this tool).
    
    {self.COLOR_COMMAND}6. Special Characters:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`\.`{self.COLOR_RESET}: Matches a literal period (escape special characters).
        - {self.COLOR_EXAMPLE}`\\`{self.COLOR_RESET}: Matches a literal backslash.
        - {self.COLOR_EXAMPLE}`\n`{self.COLOR_RESET}: Matches a newline character (valid in replacement).
        - {self.COLOR_EXAMPLE}`\t`{self.COLOR_RESET}: Matches a tab character (valid in replacement).
        - {self.COLOR_EXAMPLE}`\r`{self.COLOR_RESET}: Matches a carriage return character.
    
    {self.COLOR_COMMAND}7. Replacement String Rules:{self.COLOR_RESET}
        - {self.COLOR_EXAMPLE}`\\1`, `\\2`, etc.{self.COLOR_RESET}: Backreferences to captured groups (valid in replacement).
        - {self.COLOR_EXAMPLE}`\\0`{self.COLOR_RESET}: Refers to the entire match (implemented in this tool).
        - {self.COLOR_EXAMPLE}`\s`, `\d`, `\w`, etc.{self.COLOR_RESET}: NOT valid in replacement (only in pattern).
        """
        self.poutput(cheat_sheet)

    def do_save(self, arg):
        """Save the modified text to an output file. If no file path is provided, overwrite the original file.

        Usage:
            save [file_path]  - Save the modified text to the specified file path.
            save             - Overwrite the original file with the modified text.

        Examples:
            save "C:/output.txt"  - Saves the modified text to 'output.txt'.
            save                 - Overwrites the original file with the modified text.

        Notes:
            - If no file path is provided, the tool will attempt to overwrite the original file.
            - If the original file path is not available, a file path must be provided.
        """
        if arg.strip() == "?":  # Check if the argument is just "?"
            function_name = inspect.currentframe().f_code.co_name # Returns 'do_create'
            command_name = function_name[3:] # Remove 'do_' prefix to get 'create'
            self.do_help(command_name)  # Execute help for the current function
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # If no file path is provided, use the original file path
        if not arg:
            if not self.original_file_path:
                self.poutput("Error: No original file path is available. Please provide a file path.")
                return
            file_path = self.original_file_path
        else:
            # Remove surrounding quotes if present
            file_path = arg.strip('"').strip("'")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            file.writelines(self.current_lines)
        self.poutput(f"File saved successfully to '{file_path}'.")


    def do_advanced(self, arg):
        """enable advanced text operation functions :

            do_extract_between
            insert_line
            merge_lines
            split_lines
            convert_case
            trim_whitespace
            reverse_lines
            extract_emails
            extract_urls
            replace_confirm
        """    
        if arg.strip() == "?":
            self.do_help("advanced")
            return
        try:
            self.hidden_commands.remove('extract_between')
        except:
            a = 0                  
        try:
            self.hidden_commands.remove('insert_line')
        except:
            a = 0
        try:
            self.hidden_commands.remove('merge_lines')
        except:
            a = 0    
        try:
            self.hidden_commands.remove('split_lines')
        except:
            a = 0         
        try:
            self.hidden_commands.remove('convert_case')
        except:
            a = 0      
        try:
            self.hidden_commands.remove('trim_whitespace')
        except:
            a = 0     
        try:
            self.hidden_commands.remove('reverse_lines')
        except:
            a = 0     
        try:
            self.hidden_commands.remove('extract_emails')
        except:
            a = 0     
        try:
            self.hidden_commands.remove('extract_urls')
        except:
            a = 0           
        try:
            self.hidden_commands.remove('replace_confirm')
        except:
            a = 0   
        try:
            self.hidden_commands.remove('replace_in_lines')
        except:
            a = 0        
        try:
            self.hidden_commands.remove('select_from_file')
        except:
            a = 0    
        try:
            self.hidden_commands.remove('multiple_replace')
        except:
            a = 0       			
   			


    def do_standard(self, arg):
        """disable the advanced text operation functions.

        """    
        if arg.strip() == "?":
            self.do_help("standard")
            return
        try:
            self.hidden_commands.append('extract_between')
        except:
            a = 0                  
        try:
            self.hidden_commands.append('insert_line')
        except:
            a = 0
        try:
            self.hidden_commands.append('merge_lines')
        except:
            a = 0    
        try:
            self.hidden_commands.append('split_lines')
        except:
            a = 0         
        try:
            self.hidden_commands.append('convert_case')
        except:
            a = 0      
        try:
            self.hidden_commands.append('trim_whitespace')
        except:
            a = 0     
        try:
            self.hidden_commands.append('reverse_lines')
        except:
            a = 0     
        try:
            self.hidden_commands.append('extract_emails')
        except:
            a = 0     
        try:
            self.hidden_commands.append('extract_urls')
        except:
            a = 0                 
        try:
            self.hidden_commands.append('replace_confirm')
        except:
            a = 0 
        try:
            self.hidden_commands.append('replace_in_lines')
        except:
            a = 0   
        try:
            self.hidden_commands.append('select_from_file')
        except:
            a = 0 		
        try:
            self.hidden_commands.append('multiple_replace')
        except:
            a = 0 			

    def do_replace_confirm(self, arg):
        """Interactive find and replace with user confirmation.
        
        Usage:
            replace_confirm "old_text" "new_text"
        
        The user is prompted for each match:
          - (y)es → Replace this occurrence
          - (n)o → Skip this occurrence
          - (a)ll → Replace all occurrences
          - (q)uit → Stop replacing
        """

        if arg.strip() == "?":
            self.do_help("replace_confirm")
            return

        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return



        self.previous_lines = self.current_lines.copy()
        
        if hasattr(arg, 'args'):
            arg = arg.args

        # Replace [pipe] with | and [doublequote] with " in the input
        #arg = arg.replace("[pipe]", "|").replace("[doublequote]", '"')

        # Check if the arguments are quoted
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            old_text,new_text = args[1], args[3]
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            old_text,new_text = args[1], args[3]            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput("Error: Invalid arguments. Usage: replace_confirm \"old_text\" \"new_text\"")
                return
            old_text,new_text = args[0], args[1]
        
        regex = re.compile(re.escape(old_text))  # Escape special chars for literal match
        updated_lines = []
        
        replace_all = False
        for line in self.current_lines:
            matches = list(regex.finditer(line))
            if not matches:
                updated_lines.append(line)
                continue
            
            start_idx = 0
            new_line = ""
            
            for match in matches:
                before = line[start_idx:match.start()]
                highlight = f"\033[1;31m{match.group()}\033[0m"  # Highlight match in red
                self.poutput(f"{before}{highlight}{line[match.end():]}")
                
                if replace_all:
                    new_line += before + new_text
                    start_idx = match.end()
                    continue
                
                choice = input("Replace this occurrence? (y/n/a/q): ").strip().lower()
                if choice == "y":
                    new_line += before + new_text
                elif choice == "n":
                    new_line += before + match.group()
                elif choice == "a":
                    new_line += before + new_text
                    replace_all = True
                elif choice == "q":
                    updated_lines.append(line)
                    self.current_lines = updated_lines + self.current_lines[len(updated_lines):]
                    return
                else:
                    new_line += before + match.group()
                start_idx = match.end()
            
            new_line += line[start_idx:]
            updated_lines.append(new_line)
        
        self.current_lines = updated_lines
        self.poutput("Replacement completed.")


    def do_exit(self, arg):
        """Exit the tool.

        Usage:
            exit  - Exits the text manipulation tool.

        Notes:
            - This command will terminate the application.
        """
        self.poutput("Exiting...")
        return True


    def do_count(self, arg):
        """Count the occurrences of a specific string or regex pattern in the current text.

        Usage:
            count <pattern>  - Count the occurrences of the specified pattern.

        Examples:
            count "error"  - Counts the number of times "error" appears in the text.
        """
        if arg.strip() == "?":
            self.do_help("count")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        pattern = arg.strip('"').strip("'")
        try:
            regex = re.compile(pattern)
            count = sum(1 for line in self.current_lines if regex.search(line))
            self.poutput(f"Pattern '{pattern}' found {count} times.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")


    def do_replace_in_lines(self, arg):
        """Replace a string or regex pattern only in lines that match another pattern.

        Usage:
            replace_in_lines "search_pattern" "replace_pattern" "target_pattern"

        Examples:
            replace_in_lines "error" "warning" "2023"  - Replaces "error" with "warning" only in lines containing "2023".
        """
        if arg.strip() == "?":
            self.do_help("replace_in_lines")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return
            
        self.previous_lines = self.current_lines.copy()

        args = arg.split('"')
        if len(args) < 7:
            self.poutput("Error: Invalid arguments. Usage: replace_in_lines \"search_pattern\" \"replace_pattern\" \"target_pattern\"")
            return

        search_pattern = args[1]
        replace_pattern = args[3]
        target_pattern = args[5]

        try:
            target_regex = re.compile(target_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"))
            search_regex = re.compile(search_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"))
            self.current_lines = [
                search_regex.sub(replace_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"), line) if target_regex.search(line) else line
                for line in self.current_lines
            ]
            self.poutput("Replacement completed in specified lines.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")
            self.poutput(f"Literal replacement will be now tried")
            try:
                self.current_lines = [line.replace(search_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+"), replace_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+")) if target_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',"[^\S\r\n]+") in line else line for line in self.current_lines]
                self.poutput("Literal Replacement completed.")
            except re.error as d:
                self.poutput(f"Literal Replacement failed. Details: {d}")                


    def do_extract_between(self, arg):
        """Extract lines that lie between two specified patterns.

        Usage:
            extract_between "start_pattern" "end_pattern"

        Examples:
            extract_between "start" "end"  - Extracts all lines between the first occurrence of "start" and the first occurrence of "end".
        """
        if arg.strip() == "?":
            self.do_help("extract_between")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        args = arg.split('"')
        if len(args) < 5:
            self.poutput("Error: Invalid arguments. Usage: extract_between \"start_pattern\" \"end_pattern\"")
            return

        start_pattern = args[1]
        end_pattern = args[3]

        try:
            start_regex = re.compile(start_pattern)
            end_regex = re.compile(end_pattern)
            extracting = False
            extracted_lines = []

            for line in self.current_lines:
                if start_regex.search(line):
                    extracting = True
                if extracting:
                    extracted_lines.append(line)
                if end_regex.search(line):
                    break

            self.current_lines = extracted_lines
            self.poutput("Lines extracted successfully.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")


    def do_insert_line(self, arg):
        """Insert a line of text at a specific line number.

        Usage:
            insert_line <line_number> "text_to_insert"

        Examples:
            insert_line 5 "This is a new line"  - Inserts the text at line 5.
        """
        if arg.strip() == "?":
            self.do_help("insert_line")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        args = arg.split('"')
        if len(args) < 2:
            self.poutput("Error: Invalid arguments. Usage: insert_line <line_number> \"text_to_insert\"")
            return

        try:
            line_number = int(args[0].strip())
            text_to_insert = args[1] + "\n"
            if line_number < 1 or line_number > len(self.current_lines):
                self.poutput("Error: Line number out of range.")
                return

            self.current_lines.insert(line_number - 1, text_to_insert)
            self.poutput(f"Line inserted successfully at position {line_number}.")
        except ValueError:
            self.poutput("Error: Invalid line number.")


    def do_split_lines(self, arg):
        """Split lines by a specified delimiter into multiple lines.

        Usage:
            split_lines <delimiter>

        Examples:
            split_lines ","  - Splits lines at each comma.
        """
        if arg.strip() == "?":
            self.do_help("split_lines")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        delimiter = arg.strip()
        new_lines = []
        for line in self.current_lines:
            new_lines.extend(line.split(delimiter))
        self.current_lines = [line + "\n" for line in new_lines]
        self.poutput("Lines split successfully.")

    def do_merge_lines(self, arg):
        """Merge multiple lines into a single line, optionally separated by a delimiter.

        Usage:
            merge_lines [delimiter]

        Examples:
            merge_lines ","  - Merges all lines into a single line separated by commas.
        """
        if arg.strip() == "?":
            self.do_help("merge_lines")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        delimiter = arg.strip() if arg else ""
        merged_line = delimiter.join(line.strip() for line in self.current_lines)
        self.current_lines = [merged_line + "\n"]
        self.poutput("Lines merged successfully.")


    def do_select_from_file(self, arg):
        """Select or exclude lines from the loaded text based on a list from a file or an Excel sheet.

        Usage:
            select_from_file "<file_path>" [negate]

        Arguments:
            "<file_path>"  - Path to the text or Excel file containing the selection strings.
            [negate]       - Optional flag to exclude matching lines instead of selecting them.

        Examples:
            select_from_file "C:/strings.txt"        - Selects lines containing strings from 'strings.txt'.
            select_from_file "C:/strings.xlsx"       - Selects lines containing values from the first column of 'strings.xlsx'.
            select_from_file "C:/strings.txt" negate - Excludes lines containing strings from 'strings.txt'.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nSelect or exclude lines from the loaded text based on a list from a file or an Excel sheet.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}select_from_file \"<file_path>\" [negate]{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Arguments:{self.COLOR_RESET}\n"
			f"  {self.COLOR_EXAMPLE}\"<file_path>\"  - Path to the text or Excel file containing the selection strings.{self.COLOR_RESET}\n"
			f"  {self.COLOR_EXAMPLE}[negate]       - Optional flag to exclude matching lines instead of selecting them.\n\n"
        )
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function

        args = shlex.split(arg)
        if not args:
            self.poutput("Error: No file specified.")
            return
        
        file_path = args[0].strip('"').strip("'")
        negate = "negate" in args
        
        if not os.path.exists(file_path):
            self.poutput(f"Error: File '{file_path}' does not exist.")
            return
        
        # Read list of strings
        strings = []
        if file_path.lower().endswith(('.xls', '.xlsx')):
            try:
                df = pd.read_excel(file_path, usecols=[0], header=None)
                strings = df[0].dropna().astype(str).tolist()
            except Exception as e:
                self.poutput(f"Error reading Excel file: {e}")
                return
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                strings = [line.strip() for line in file if line.strip()]
        
        if not strings:
            self.poutput("Error: The file is empty or contains no valid strings.")
            return
        
        # Save previous state
        self.previous_lines = self.current_lines.copy()
        
        if negate:
            self.current_lines = [line for line in self.current_lines if not any(s in line for s in strings)]
        else:
            self.current_lines = [line for line in self.current_lines if any(s in line for s in strings)]
        
        action = "Excluded" if negate else "Selected"
        self.poutput(f"{action} {len(self.current_lines)} lines based on '{file_path}'.")




    def do_convert_case(self, arg):
        """Convert the text to uppercase, lowercase, or title case.

        Usage:
            convert_case <upper|lower|title>

        Examples:
            convert_case upper  - Converts all text to uppercase.
        """
        if arg.strip() == "?":
            self.do_help("convert_case")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        case_type = arg.strip().lower()
        if case_type == "upper":
            self.current_lines = [line.upper() for line in self.current_lines]
        elif case_type == "lower":
            self.current_lines = [line.lower() for line in self.current_lines]
        elif case_type == "title":
            self.current_lines = [line.title() for line in self.current_lines]
        else:
            self.poutput("Error: Invalid case type. Use 'upper', 'lower', or 'title'.")
            return

        self.poutput(f"Text converted to {case_type} case successfully.")


    def do_trim_whitespace(self, arg):
        """Trim leading and trailing whitespace from each line.

        Usage:
            trim_whitespace

        Examples:
            trim_whitespace  - Removes leading and trailing spaces from each line.
        """
        if arg.strip() == "?":
            self.do_help("trim_whitespace")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        self.current_lines = [line.strip() + "\n" for line in self.current_lines]
        self.poutput("Whitespace trimmed successfully.")


    def do_reverse_lines(self, arg):
        """Reverse the order of lines in the text.

        Usage:
            reverse_lines

        Examples:
            reverse_lines  - Reverses the order of all lines.
        """
        if arg.strip() == "?":
            self.do_help("reverse_lines")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        self.current_lines.reverse()
        self.poutput("Lines reversed successfully.")



    def do_extract_urls(self, arg):
        """Extract all URLs from the text.

        Usage:
            extract_urls

        Examples:
            extract_urls  - Extracts all URLs from the text.
        """
        if arg.strip() == "?":
            self.do_help("extract_urls")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        url_pattern = re.compile(r'https?://[^\s]+')
        urls = [url for line in self.current_lines for url in url_pattern.findall(line)]
        self.current_lines = [url + "\n" for url in urls]
        self.poutput("URLs extracted successfully.")

    def do_extract_emails(self, arg):
        """Extract all email addresses from the text.

        Usage:
            extract_emails

        Examples:
            extract_emails  - Extracts all email addresses from the text.
        """
        if arg.strip() == "?":
            self.do_help("extract_emails")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = [email for line in self.current_lines for email in email_pattern.findall(line)]
        self.current_lines = [email + "\n" for email in emails]
        self.poutput("Emails extracted successfully.")

            
    def complete_load(self, text, line, begidx, endidx):
        """Autocomplete file paths for the load command."""
        # Get the directory and file prefix from the text
        if not text:
            dir_path = "."  # Current directory
            file_prefix = ""
        else:
            # Handle paths correctly for both Linux and Windows
            dir_path, file_prefix = os.path.split(text)

            # If dir_path is empty (e.g., user typed "load file"), use the current directory
            if not dir_path:
                dir_path = "."

        # Ensure the directory exists
        if not os.path.exists(dir_path):
            return []

        # List all files in the directory that match the prefix
        completions = []
        for f in os.listdir(dir_path):
            if f.startswith(file_prefix) and os.path.isfile(os.path.join(dir_path, f)):
                # Return the full path, using the correct path separator for the OS
                full_path = os.path.join(dir_path, f)
                completions.append(full_path)

        return completions

    def do_sort(self, arg):
        """Sort the lines in the current text.

        Usage:
            sort  - Sorts the lines in the current text.

        Notes:
            - This command sorts the lines in ascending order.
            - The sorting is case-sensitive.
        """
        if arg.strip() == "?":  # Check if the argument is just "?"
            function_name = inspect.currentframe().f_code.co_name # Returns 'do_create'
            command_name = function_name[3:] # Remove 'do_' prefix to get 'create'
            self.do_help(command_name)  # Execute help for the current function
            return  # Exit the function        
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # Save the current state for revert functionality
        self.previous_lines = self.current_lines.copy()

        # Sort the lines
        self.current_lines.sort()
        self.poutput("Lines sorted successfully.")

    def do_unique(self, arg):
        """Remove duplicate lines from the current text and display the number of deleted lines.

        Usage:
            unique  - Removes duplicate lines from the current text.

        Notes:
            - This command removes duplicate lines, keeping only the first occurrence of each line.
            - The number of deleted lines is displayed after the operation.
        """
        if arg.strip() == "?":  # Check if the argument is just "?"
            function_name = inspect.currentframe().f_code.co_name # Returns 'do_create'
            command_name = function_name[3:] # Remove 'do_' prefix to get 'create'
            self.do_help(command_name)  # Execute help for the current function
            return  # Exit the function
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.do_help(self._cmd_func_name)  # Execute help for the current function
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # Save the current state for revert functionality
        self.previous_lines = self.current_lines.copy()

        # Remove duplicate lines
        unique_lines = []
        seen = set()
        deleted_lines_count = 0

        for line in self.current_lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)
            else:
                deleted_lines_count += 1

        self.current_lines = unique_lines
        self.poutput(f"Duplicate lines removed successfully. Deleted {deleted_lines_count} lines.")
        
        
    def do_remove_empty_lines(self, arg):
        """Remove empty lines from the current text.

        Usage:
            remove_empty_lines  - Removes empty lines from the current text.

        Notes:
            - This command removes lines that are empty or contain only whitespace.
            - The number of deleted lines is displayed after the operation.
        """
        if arg.strip() == "?":  # Check if the argument is just "?"
            function_name = inspect.currentframe().f_code.co_name # Returns 'do_create'
            command_name = function_name[3:] # Remove 'do_' prefix to get 'create'
            self.do_help(command_name)  # Execute help for the current function
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        # Save the current state for revert functionality
        self.previous_lines = self.current_lines.copy()

        # Remove empty lines
        non_empty_lines = [line for line in self.current_lines if line.strip()]
        deleted_lines_count = len(self.current_lines) - len(non_empty_lines)
        self.current_lines = non_empty_lines

        self.poutput(f"Empty lines removed successfully. Deleted {deleted_lines_count} lines.")
        

if __name__ == '__main__':
    app = TextTool()
    app.cmdloop()
