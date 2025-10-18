
import subprocess
import sys
import inspect
import shlex
import win32clipboard
import importlib
global input_file
import difflib
# List of required libraries
required_libraries = ['cmd2', 'regex','pandas','regex','pathlib']
input_file= ""

def install_library(library):
    """Install a library using pip."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', library])
    except:
        return

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
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


if len(sys.argv)>1:
    input_file = " ".join(sys.argv[1:]).replace('"','')
    input_file='"'+input_file+'"'
    # sys.argv=['']
    input_file =input_file.replace('/','\\')
    sys.argv=['']

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

def get_copied_file():
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            if data and len(data) > 0:
                return data[0]  # Return the first file path
    finally:
        win32clipboard.CloseClipboard()
    return None

def change_inside_quotes(s, old, new):
    """Helper function to replace old substring with new substring inside quotes."""
    return re.sub(r'(["\']).*?\1', lambda m: m.group().replace(old, new), s)

def remove_spaces(s):
    return change_inside_quotes(s, ' ', 'hahi')

def retrieve_spaces(s):
    return change_inside_quotes(s, 'hahi', ' ')

class TextTool(cmd2.Cmd):
    def __init__(self):
        global input_file
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
        #self.original_file_path = "c:/clipboard.txt"  # Default file path for clipboard content
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
        self.hidden_commands.append('select_from_file')	
        self.liveview_box = None  # keep reference to the text box
        self.liveview_root = None        
        self.start_live_view()
        if input_file:
            self.do_load(input_file)  

    def start_live_view(self):
        """Launch Tkinter window showing live updates of current_lines, with cursor line tracking."""
        import tkinter as tk
        from tkinter.scrolledtext import ScrolledText

        # If a window already exists and is still valid, bring it to front
        if hasattr(self, "liveview_root") and self.liveview_root:
            try:
                if self.liveview_root.winfo_exists():
                    self.liveview_root.lift()
                    self.liveview_root.focus_force()
                    return
            except:
                pass
        
        # Clean up any lingering references
        self.liveview_root = None
        self.liveview_box = None
        self.file_path_label = None
        self.update_file_path_display = None

        def run_viewer():
            self.liveview_root = tk.Tk()
            self.liveview_root.title("Live Text Viewer – 0 lines")
            
            # File path label at the top
            file_path_frame = tk.Frame(self.liveview_root, bg="#f0f0f0")
            self.file_path_label = tk.Label(file_path_frame, text="", anchor="w", 
                                         font=("Consolas", 9), bg="#f0f0f0", fg="#333333")
            self.file_path_label.pack(fill="x", padx=5, pady=2)
            file_path_frame.pack(fill="x", side="top")
            
            def update_file_path_display():
                """Update the file path display."""
                try:
                    if hasattr(self, 'original_file_path') and self.original_file_path:
                        self.file_path_label.config(text=f"📄 File: {self.original_file_path}")
                    else:
                        self.file_path_label.config(text="📄 File: (Unsaved)")
                except:
                    pass
            
            # Store the function as instance method so it can be called from outside
            self.update_file_path_display = update_file_path_display
            
            # Initial file path display
            update_file_path_display()
            
            self.liveview_box = ScrolledText(
                self.liveview_root, width=100, height=40, font=("Consolas", 10)
            )
            self.liveview_box.pack(fill="both", expand=True)

            # Create a small status bar
            status = tk.Label(self.liveview_root, text="Line: 1", anchor="w", font=("Consolas", 9))
            status.pack(fill="x", side="bottom")

            # Search frame with enhanced features
            search_frame = tk.Frame(self.liveview_root)
            search_label = tk.Label(search_frame, text="Find:", font=("Consolas", 9))
            search_label.pack(side="left", padx=2)

            search_entry = tk.Entry(search_frame, width=30)
            search_entry.pack(side="left", fill="x", expand=True, padx=2)

            # Case-sensitive checkbox
            case_sensitive_var = tk.BooleanVar(value=False)
            case_check = tk.Checkbutton(search_frame, text="Case", variable=case_sensitive_var, 
                                         font=("Consolas", 9))
            case_check.pack(side="left", padx=2)

            # Regex checkbox
            regex_var = tk.BooleanVar(value=False)
            regex_check = tk.Checkbutton(search_frame, text="Regex", variable=regex_var, 
                                          font=("Consolas", 9))
            regex_check.pack(side="left", padx=2)

            # ENHANCEMENT 6: Whole word matching
            whole_word_var = tk.BooleanVar(value=False)
            whole_word_check = tk.Checkbutton(search_frame, text="Whole Word", 
                                               variable=whole_word_var, font=("Consolas", 9))
            whole_word_check.pack(side="left", padx=2)

            # Navigation buttons
            prev_button = tk.Button(search_frame, text="◄ Prev", font=("Consolas", 9), width=8)
            prev_button.pack(side="left", padx=2)

            next_button = tk.Button(search_frame, text="Next ►", font=("Consolas", 9), width=8)
            next_button.pack(side="left", padx=2)

            # Match counter label
            match_label = tk.Label(search_frame, text="", font=("Consolas", 9))
            match_label.pack(side="left", padx=5)

            # Close button
            close_button = tk.Button(search_frame, text="✕", width=3, font=("Consolas", 8),
                                   command=lambda: search_frame.pack_forget())
            close_button.pack(side="right", padx=2)

            # Store match positions
            match_positions = []
            current_match_index = [-1]  # Use list to allow modification in nested functions

            def perform_search(event=None):
                """Enhanced search with whole word matching."""
                query = search_entry.get()
                self.liveview_box.tag_remove("search_highlight", "1.0", tk.END)
                self.liveview_box.tag_remove("current_match", "1.0", tk.END)
                match_positions.clear()
                current_match_index[0] = -1
                match_label.config(text="")
                
                if not query:
                    return
                
                case_sensitive = case_sensitive_var.get()
                use_regex = regex_var.get()
                whole_word = whole_word_var.get()
                
                try:
                    if use_regex:
                        import re
                        flags = 0 if case_sensitive else re.IGNORECASE
                        if whole_word:
                            query = r'\b' + query + r'\b'
                        pattern = re.compile(query, flags)
                        
                        text_content = self.liveview_box.get("1.0", tk.END)
                        for match in pattern.finditer(text_content):
                            start_idx = f"1.0+{match.start()}c"
                            end_idx = f"1.0+{match.end()}c"
                            match_positions.append((start_idx, end_idx))
                            self.liveview_box.tag_add("search_highlight", start_idx, end_idx)
                    else:
                        start_pos = "1.0"
                        while True:
                            start_pos = self.liveview_box.search(
                                query, start_pos, stopindex=tk.END, 
                                nocase=not case_sensitive
                            )
                            if not start_pos:
                                break
                            
                            end_pos = f"{start_pos}+{len(query)}c"
                            
                            # Check whole word
                            if whole_word:
                                before_char = self.liveview_box.get(f"{start_pos}-1c", start_pos)
                                after_char = self.liveview_box.get(end_pos, f"{end_pos}+1c")
                                if before_char.isalnum() or after_char.isalnum():
                                    start_pos = end_pos
                                    continue
                            
                            match_positions.append((start_pos, end_pos))
                            self.liveview_box.tag_add("search_highlight", start_pos, end_pos)
                            start_pos = end_pos
                    
                    if match_positions:
                        match_label.config(text=f"{len(match_positions)} matches")
                        current_match_index[0] = 0
                        highlight_current_match()
                    else:
                        match_label.config(text="No matches")
                        
                    self.liveview_box.tag_config("search_highlight", background="yellow", foreground="black")
                    self.liveview_box.tag_config("current_match", background="orange", foreground="black")
                    
                except Exception as e:
                    match_label.config(text=f"Error: {str(e)[:20]}")

            def highlight_current_match():
                """Highlight the current match and scroll to it."""
                if not match_positions or current_match_index[0] < 0:
                    return
                
                # Remove previous current match highlighting
                self.liveview_box.tag_remove("current_match", "1.0", tk.END)
                
                # Highlight current match
                start_pos, end_pos = match_positions[current_match_index[0]]
                self.liveview_box.tag_add("current_match", start_pos, end_pos)
                
                # Scroll to current match
                self.liveview_box.see(start_pos)
                
                # Update counter
                match_label.config(
                    text=f"Match {current_match_index[0] + 1} of {len(match_positions)}"
                )

            def next_match(event=None):
                """Navigate to next match."""
                if not match_positions:
                    return
                current_match_index[0] = (current_match_index[0] + 1) % len(match_positions)
                highlight_current_match()

            def prev_match(event=None):
                """Navigate to previous match."""
                if not match_positions:
                    return
                current_match_index[0] = (current_match_index[0] - 1) % len(match_positions)
                highlight_current_match()

            # Bind events
            search_entry.bind("<KeyRelease>", perform_search)
            search_entry.bind("<Return>", lambda e: next_match())
            case_check.config(command=perform_search)
            regex_check.config(command=perform_search)
            whole_word_check.config(command=perform_search)
            next_button.config(command=next_match)
            prev_button.config(command=prev_match)

            # Keyboard shortcuts
            self.liveview_root.bind("<F3>", next_match)
            self.liveview_root.bind("<Shift-F3>", prev_match)

            # Save button frame
            save_frame = tk.Frame(self.liveview_root)
            
            save_button = tk.Button(save_frame, text="💾 Save", font=("Consolas", 10), 
                                    command=lambda: save_from_liveview())
            save_button.pack(side="left", padx=5, pady=2)
            
            save_as_button = tk.Button(save_frame, text="💾 Save As...", font=("Consolas", 10), 
                                        command=lambda: save_as_from_liveview())
            save_as_button.pack(side="left", padx=5, pady=2)

            replace_button = tk.Button(save_frame, text="🔧 Replace...", font=("Consolas", 10), 
                                      command=lambda: open_replace_dialog())
            replace_button.pack(side="left", padx=5, pady=2)

            # ADD THIS REVERT BUTTON
            revert_button = tk.Button(save_frame, text="↶ Revert", font=("Consolas", 10), 
                                     command=lambda: self.do_revert(""))
            revert_button.pack(side="left", padx=5, pady=2)

            
            sync_button = tk.Button(save_frame, text="⟲ Sync to TextTool", font=("Consolas", 10), 
                                    command=lambda: sync_from_liveview_internal())
            sync_button.pack(side="left", padx=5, pady=2)

            # ADD COMMAND PALETTE BUTTON
            command_palette_button = tk.Button(save_frame, text="⌨️ Commands", font=("Consolas", 10), 
                                               command=lambda: open_command_palette())
            command_palette_button.pack(side="left", padx=5, pady=2)
            info_frame = tk.Frame(self.liveview_root, bg="#f0f0f0")
            info_frame.pack(fill=tk.X, side=tk.BOTTOM)

            info_label = tk.Label(info_frame, 
                                 text="💡 This window shows a live preview. The tool is designed for command line usage. " +
                                      "You can close this window anytime and reopen it with the 'liveview' command.",
                                 font=("Consolas", 8), 
                                 bg="#f0f0f0", 
                                 fg="#666666",
                                 wraplength=580,  # Adjust based on your window width
                                 justify=tk.LEFT)
            info_label.pack(padx=5, pady=2)            
            
            save_frame.pack(fill="x", side="top")
            
            def open_replace_dialog():
                
                """Open the smart replacement dialog"""
                import tkinter as tk
                from tkinter import ttk, messagebox
                
                dialog = tk.Toplevel()
                dialog.title("Smart Text Replacement")
                dialog.geometry("500x250")  # Adjusted size
                dialog.resizable(False, False)
                dialog.transient(self.liveview_root)  # Make it modal to main window
                dialog.grab_set()  # Make it modal
                
                # Main frame
                main_frame = ttk.Frame(dialog, padding="15")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Operation type
                ttk.Label(main_frame, text="Replacement Type:").grid(row=0, column=0, sticky=tk.W, pady=8)
                operation_var = tk.StringVar(value="Simple Replace")
                operation_combo = ttk.Combobox(main_frame, textvariable=operation_var, 
                                             values=["Simple Replace", "Replace in Matching Lines", 
                                                     "Right Replace", "Left Replace"],
                                             state="readonly", width=20)
                operation_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=5)
                
                # Search pattern
                ttk.Label(main_frame, text="Search Pattern:").grid(row=1, column=0, sticky=tk.W, pady=8)
                search_entry = ttk.Entry(main_frame, width=30)
                search_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=5)
                
                # Replacement text
                ttk.Label(main_frame, text="Replacement Text:").grid(row=2, column=0, sticky=tk.W, pady=8)
                replace_entry = ttk.Entry(main_frame, width=30)
                replace_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8, padx=5)
                
                # Target pattern (for Replace in Matching Lines)
                target_frame = ttk.Frame(main_frame)
                target_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=8)
                
                ttk.Label(target_frame, text="Only in lines containing:").grid(row=0, column=0, sticky=tk.W)
                target_entry = ttk.Entry(target_frame, width=25)
                target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
                
                # Initially hide target frame
                target_frame.grid_remove()
                
                # Case Sensitive option only
                case_frame = ttk.Frame(main_frame)
                case_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
                
                case_var = tk.BooleanVar(value=False)  # Default to case insensitive
                case_check = tk.Checkbutton(case_frame, text="Case Sensitive", variable=case_var,
                                           font=("", 9))
                case_check.pack(side=tk.LEFT)
                
                # Button frame
                button_frame = ttk.Frame(main_frame)
                button_frame.grid(row=5, column=0, columnspan=2, pady=15)
                
                def on_operation_change(*args):
                    """Show/hide target pattern based on operation"""
                    if operation_var.get() == "Replace in Matching Lines":
                        target_frame.grid()
                    else:
                        target_frame.grid_remove()
                
                def apply_replacement():
                    """Apply the replacement using existing commands"""
                    try:
                        search_pattern = search_entry.get()
                        replace_pattern = replace_entry.get()
                        target_pattern = target_entry.get()
                        operation = operation_var.get()
                        case_sensitive = case_var.get()
                        
                        if not search_pattern:
                            messagebox.showwarning("Warning", "Please enter a search pattern.")
                            return
                        
                        # Build the command based on operation type
                        if operation == "Simple Replace":
                            cmd = f'replace "{search_pattern}" "{replace_pattern}"'
                            if case_sensitive:
                                cmd += " case_sensitive"
                        
                        elif operation == "Replace in Matching Lines":
                            if not target_pattern:
                                messagebox.showwarning("Warning", "Please enter a target pattern for line matching.")
                                return
                            cmd = f'replace_in_lines "{search_pattern}" "{replace_pattern}" "{target_pattern}"'
                            if case_sensitive:
                                cmd += " case_sensitive"
                        
                        elif operation == "Right Replace":
                            cmd = f'right_replace "{search_pattern}" "{replace_pattern}"'
                            if case_sensitive:
                                cmd += " case_sensitive"
                        
                        elif operation == "Left Replace":
                            cmd = f'left_replace "{search_pattern}" "{replace_pattern}"'
                            if case_sensitive:
                                cmd += " case_sensitive"
                        
                        else:
                            messagebox.showerror("Error", "Unknown operation type")
                            return
                        
                        # Execute the command
                        self.onecmd(cmd)
                        
                        # Update Live View with changes
                        self.update_live_view()
                        
                        messagebox.showinfo("Success", "Replacement applied successfully!")
                        dialog.destroy()
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to apply replacement:\n{str(e)}")
                
                # Bind operation change event
                operation_var.trace('w', on_operation_change)
                
                # Buttons
                ttk.Button(button_frame, text="Apply Replacement", command=apply_replacement).pack(side=tk.LEFT, padx=8)
                ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=8)
                
                # Configure grid weights
                main_frame.columnconfigure(1, weight=1)
                
                # Set focus to search entry
                search_entry.focus()
                
                # Center the dialog
                dialog.update_idletasks()
                x = self.liveview_root.winfo_x() + (self.liveview_root.winfo_width() - dialog.winfo_width()) // 2
                y = self.liveview_root.winfo_y() + (self.liveview_root.winfo_height() - dialog.winfo_height()) // 2
                dialog.geometry(f"+{x}+{y}")

            def open_command_palette():
                """Open a command palette dialog showing all available commands."""
                import tkinter as tk
                from tkinter import ttk, messagebox
                
                palette = tk.Toplevel()
                palette.title("Command Palette")
                palette.geometry("600x500")
                palette.resizable(True, True)
                palette.transient(self.liveview_root)
                palette.grab_set()
                
                # Main frame
                main_frame = ttk.Frame(palette, padding="10")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Search frame
                search_frame = ttk.Frame(main_frame)
                search_frame.pack(fill=tk.X, pady=(0, 10))
                
                ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
                search_var = tk.StringVar()
                search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
                search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                search_entry.focus()
                
                # Commands listbox with scrollbar
                list_frame = ttk.Frame(main_frame)
                list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                scrollbar = ttk.Scrollbar(list_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                commands_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                             font=("Consolas", 10), selectmode=tk.SINGLE)
                commands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.config(command=commands_listbox.yview)
                
                # Parameters frame (initially hidden)
                params_frame = ttk.Frame(main_frame)
                
                ttk.Label(params_frame, text="Parameters:").pack(anchor=tk.W)
                params_entry = ttk.Entry(params_frame, width=50)
                params_entry.pack(fill=tk.X, pady=(5, 10))
                
                # Button frame
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill=tk.X)
                
                execute_button = ttk.Button(button_frame, text="Execute", state=tk.DISABLED)
                execute_button.pack(side=tk.LEFT, padx=(0, 5))
                
                cancel_button = ttk.Button(button_frame, text="Close", command=palette.destroy)
                cancel_button.pack(side=tk.LEFT)
                
                # Get all available commands
                def get_all_commands():
                    """Get all available commands with their help text."""
                    commands = []
                    excluded_commands = ['py', 'ipy','quit','help','liveview']  # Commands to exclude from the list
                    
                    for attr_name in dir(self):
                        if attr_name.startswith('do_'):
                            command_name = attr_name[3:]
                            if (command_name not in self.hidden_commands and 
                                not command_name.startswith('_') and
                                command_name not in excluded_commands):  # Add this filter
                                # Get help text
                                method = getattr(self, attr_name)
                                help_text = method.__doc__ or "No description available"
                                # Extract first line of help for display
                                first_line = help_text.strip().split('\n')[0]
                                commands.append((command_name, first_line))
                    return sorted(commands, key=lambda x: x[0])
                
                all_commands = get_all_commands()
                command_dict = {name: (name, help_text) for name, help_text in all_commands}
                
                def update_commands_list(*args):
                    """Update the commands list based on search filter."""
                    filter_text = search_var.get().lower()
                    commands_listbox.delete(0, tk.END)
                    
                    for name, help_text in all_commands:
                        if filter_text in name.lower() or filter_text in help_text.lower():
                            display_text = f"{name:<20} - {help_text}"
                            commands_listbox.insert(tk.END, display_text)
                
                def on_command_select(event):
                    """Handle command selection."""
                    selection = commands_listbox.curselection()
                    if selection:
                        index = selection[0]
                        display_text = commands_listbox.get(index)
                        command_name = display_text.split(' - ')[0].strip()
                        
                        # Check if command needs parameters by looking at its help text
                        command_method = getattr(self, f'do_{command_name}')
                        help_text = command_method.__doc__ or ""
                        
                        # Simple heuristic: if help text mentions "Usage:" with arguments, it likely needs params
                        needs_params = any(keyword in help_text for keyword in ['<', '[', 'Usage:', 'arguments'])
                        
                        if needs_params:
                            # Show parameters frame
                            params_frame.pack(fill=tk.X, pady=(10, 0))
                            params_entry.delete(0, tk.END)
                            params_entry.focus()
                            execute_button.config(state=tk.NORMAL, 
                                                command=lambda: execute_command(command_name, params_entry.get()))
                        else:
                            # Hide parameters frame and enable execute
                            params_frame.pack_forget()
                            execute_button.config(state=tk.NORMAL, 
                                                command=lambda: execute_command(command_name, ""))
                
                def execute_command(command_name, parameters):
                    """Execute the selected command with parameters."""
                    try:
                        full_command = f"{command_name} {parameters}".strip()
                        self.onecmd(full_command)
                        
                        # Update Live View if command might have changed content
                        if command_name in ['load', 'replace', 'select', 'revert', 'sort', 'unique', 
                                          'remove_empty_lines', 'multiple_replace']:
                            self.update_live_view()
                        
                        palette.destroy()
                        #messagebox.showinfo("Success", f"Command '{command_name}' executed successfully!")
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to execute command:\n{str(e)}")
                
                def on_double_click(event):
                    """Handle double-click on command list."""
                    on_command_select(event)
                    selection = commands_listbox.curselection()
                    if selection:
                        execute_button.invoke()
                
                def on_enter_key(event):
                    """Handle Enter key in parameters field or when listbox has focus."""
                    if params_entry.focus_get() == params_entry and params_entry.get().strip():
                        execute_button.invoke()
                    elif commands_listbox.focus_get() == commands_listbox and commands_listbox.curselection():
                        on_command_select(None)
                        execute_button.invoke()
                
                # Bind events
                search_var.trace('w', update_commands_list)
                commands_listbox.bind('<<ListboxSelect>>', on_command_select)
                commands_listbox.bind('<Double-Button-1>', on_double_click)
                params_entry.bind('<Return>', on_enter_key)
                commands_listbox.bind('<Return>', on_enter_key)
                search_entry.bind('<Return>', lambda e: commands_listbox.focus_set())
                
                # Populate initial list
                update_commands_list()
                
                # Select first item if available
                if commands_listbox.size() > 0:
                    commands_listbox.selection_set(0)
                    commands_listbox.see(0)
                    on_command_select(None)
                
                # Center the palette
                palette.update_idletasks()
                x = self.liveview_root.winfo_x() + (self.liveview_root.winfo_width() - palette.winfo_width()) // 2
                y = self.liveview_root.winfo_y() + (self.liveview_root.winfo_height() - palette.winfo_height()) // 2
                palette.geometry(f"+{x}+{y}")

            def save_from_liveview():
                """Save the Live View content directly to a file."""
                from tkinter import filedialog, messagebox
                try:
                    # Get content from liveview
                    content = self.liveview_box.get("1.0", tk.END)
                    
                    # Use original file path if available
                    if hasattr(self, 'original_file_path') and self.original_file_path:
                        file_path = self.original_file_path
                    else:
                        # Ask for file path
                        file_path = filedialog.asksaveasfilename(
                            title="Save File",
                            defaultextension=".txt",
                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                        )
                        if not file_path:
                            return
                        
                        # Update original file path for first-time save
                        self.original_file_path = file_path
                        update_file_path_display()
                    
                    # Write to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    messagebox.showinfo("Success", f"File saved successfully to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

            def save_as_from_liveview():
                """Save the Live View content to a new file."""
                from tkinter import filedialog, messagebox
                try:
                    # Get content from liveview
                    content = self.liveview_box.get("1.0", tk.END)
                    
                    # Ask for file path
                    file_path = filedialog.asksaveasfilename(
                        title="Save File As",
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                    )
                    if not file_path:
                        return
                    
                    # Write to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Update original file path
                    self.original_file_path = file_path
                    
                    # Update file path display
                    update_file_path_display()
                    
                    messagebox.showinfo("Success", f"File saved successfully to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

            def sync_from_liveview_internal():
                """Synchronize Live View content back to current_lines."""
                from tkinter import messagebox
                try:
                    # Read all content from the text box
                    new_text = self.liveview_box.get("1.0", tk.END)

                    # Save current state for revert
                    self.previous_lines = self.current_lines.copy()

                    # Replace current_lines with content from Live View
                    self.current_lines = [line for line in new_text.splitlines(keepends=True)]

                    # Refresh Live View to ensure consistency
                    self.update_live_view()

                    messagebox.showinfo("Success", f"Synchronized {len(self.current_lines)} lines from Live View.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to sync:\n{str(e)}")

            # Bind Ctrl+S to save
            self.liveview_root.bind("<Control-s>", lambda e: save_from_liveview())

            # Hide by default, will appear on Ctrl+F
            search_frame.pack_forget()

            def toggle_search(event=None):
                """Toggle visibility of search bar."""
                if search_frame.winfo_ismapped():
                    search_frame.pack_forget()
                else:
                    search_frame.pack(fill="x", side="top")
                    search_entry.focus_set()

            # Bind Ctrl+F to open search bar
            self.liveview_root.bind("<Control-f>", toggle_search)
            self.liveview_root.bind("<Control-r>", lambda e: open_replace_dialog())

            def update_cursor_position(event=None):
                try:
                    index = self.liveview_box.index(tk.INSERT)  # format "line.column"
                    line, col = index.split(".")
                    total = len(self.current_lines)
                    self.liveview_root.title(f"Live Text Viewer – {len(self.current_lines)} lines (Line {line}, Col {col})")
                    status.config(text=f"Line: {line} / {total}  |  Column: {col}")
                except Exception:
                    pass

            # Bind events for cursor movement and mouse clicks
            self.liveview_box.bind("<ButtonRelease>", update_cursor_position)
            self.liveview_box.bind("<KeyRelease>", update_cursor_position)
            self.liveview_box.bind("<Motion>", update_cursor_position)

            # Handle window close
            def on_close():
                try:
                    self.liveview_root.quit()  # Stop the mainloop
                    self.liveview_root.destroy()  # Destroy the window
                except:
                    pass
                # Clean up all references
                self.liveview_root = None
                self.liveview_box = None
                self.file_path_label = None
                self.update_file_path_display = None

            self.liveview_root.protocol("WM_DELETE_WINDOW", on_close)

            # Initial display
            self.update_live_view()
            self.liveview_root.mainloop()

        threading.Thread(target=run_viewer, daemon=True).start()


    def update_live_view(self):
        """Refresh Live View immediately."""
        if hasattr(self, "liveview_box") and self.liveview_box:
            try:
                # Check if the widget still exists
                if self.liveview_box.winfo_exists():
                    self.liveview_box.delete("1.0", tk.END)
                    self.liveview_box.insert(tk.END, ''.join(self.current_lines))
                    if hasattr(self, "liveview_root") and self.liveview_root:
                        self.liveview_root.title(f"Live Text Viewer – {len(self.current_lines)} lines")
            except Exception as e:
                # Window was destroyed, clean up references
                self.liveview_root = None
                self.liveview_box = None
                self.file_path_label = None
                self.update_file_path_display = None


        
    def do_liveview(self, arg):
        """Open a live viewer window that shows current_lines in real time."""
        self.start_live_view()
        self.poutput("Live viewer started")

        



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
                    #self.update_live_view()
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
                    #self.update_live_view()
                    selected_lines = [line for line in self.current_lines if "Error" in line]
                    self.current_lines = selected_lines
                    #self.update_live_view()
                    self.poutput("\nSelected lines:")
                    self.poutput("".join(self.current_lines))

                # Replace Error with Critical
                elif i == 8:
                    self.current_lines = [line.replace("Error", "Critical") for line in self.current_lines]
                    #self.update_live_view()
                    self.poutput("\nAfter replacement:")
                    self.poutput("".join(self.current_lines))

                # Change date format
                elif i == 9:
                    import re
                    self.current_lines = [re.sub(r"(\d{2})-(\d{2})-(\d{4})", r"\3/\2/\1", line) for line in self.current_lines]
                    #self.update_live_view()
                    self.poutput("\nAfter date format change:")
                    self.poutput("".join(self.current_lines))

                # Revert changes
                elif i == 10:
                    self.current_lines = [line.replace("Critical", "Error").replace("2023/05/12", "12-05-2023").replace("2023/05/18", "18-05-2023") for line in self.current_lines]
                    #self.update_live_view()
                    self.poutput("\nAfter reverting:")
                    self.poutput("".join(self.current_lines))

                # Sort and remove duplicates
                elif i == 11:
                    # First show sorted
                    self.current_lines.sort()
                    #self.update_live_view()
                    self.poutput("\nAfter sorting:")
                    self.poutput("".join(self.current_lines))
                    
                    # Then show after removing duplicates
                    self.current_lines = list(dict.fromkeys(self.current_lines))
                    #self.update_live_view()
                    self.poutput("\nAfter removing duplicates:")
                    self.poutput("".join(self.current_lines))

                input("\nPress Enter to continue...")

        finally:
            # Restore the original lines
            self.current_lines = original_lines
            self.update_live_view()

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
            self.update_live_view()
            
            # Update file path display in liveview
            if hasattr(self, 'update_file_path_display'):
                self.update_file_path_display()
            
            self.poutput(f"File '{file_path}' loaded successfully.")
        else:
            # Load content from the clipboard
            clipboard_content = cmd2.clipboard.get_paste_buffer()
            if clipboard_content:
                self.text_lines = [ s.replace("\r","") for s in clipboard_content.splitlines(keepends=True)]
                self.current_lines = self.text_lines.copy()
                self.update_live_view()
                self.original_file_path = None  # No file path for clipboard content
                
                # Update file path display in liveview
                if hasattr(self, 'update_file_path_display'):
                    self.update_file_path_display()
                
                self.poutput("Clipboard content loaded successfully.")
            else:
                file_path = get_copied_file()
                if file_path:
                    self.do_load(file_path)
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
            regexes = [re.compile(term.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+")) for term in search_terms]
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
            self.update_live_view()
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
        self.update_live_view()
        self.poutput("Reverted to the original full text with modified selected lines.")
    

    def do_delete(self, arg):
        """Delete lines containing (or not containing) the given string(s) or regex pattern(s).

        Usage:
            delete <string>         - Delete lines containing the specified string or regex.
            delete "!string"        - Delete lines that do NOT contain the specified string or regex.
            delete "string1 OR string2" - Delete lines containing either string1 or string2.

        Special Placeholders:
            - Use [pipe] instead of the pipe character (|) in your input.
            - Use [doublequote] instead of double quotes (") in your input.
            - Use [quote] instead of quotes (') in your input.
            - Use [tab] instead of tabulation character in your input.
            - Use [spaces] to match one or more spaces (all kind of spaces)

        Examples:
            delete "error"          - Deletes lines containing the word "error".
            delete "!error"         - Deletes lines that do NOT contain the word "error".
            delete "error OR warning" - Deletes lines containing either "error" or "warning".

        Notes:
            - The deleteion is case-sensitive.
            - Supports regex patterns for more complex deleteions.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nDelete lines containing (or not containing) the given string(s) or regex pattern(s).{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}delete <string>{self.COLOR_RESET}         - Delete lines containing the specified string or regex.\n"
            f"  {self.COLOR_EXAMPLE}delete \"!string\"{self.COLOR_RESET}        - Delete lines that do NOT contain the specified string or regex.\n"
            f"  {self.COLOR_EXAMPLE}delete \"string1 OR string2\"{self.COLOR_RESET} - Delete lines containing either string1 or string2.\n\n"
            f"{self.COLOR_COMMAND}Special Placeholders:{self.COLOR_RESET}\n"
            f"  - Use {self.COLOR_EXAMPLE}[pipe]{self.COLOR_RESET} instead of the pipe character (|) in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[doublequote]{self.COLOR_RESET} instead of double quotes (\") in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[quote]{self.COLOR_RESET} instead of quotes (') in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[tab]{self.COLOR_RESET} instead of tabulation character in your input.\n"
            f"  - Use {self.COLOR_EXAMPLE}[spaces]{self.COLOR_RESET} to match one or more spaces (all kind of spaces).\n\n"
            f"{self.COLOR_COMMAND}Examples:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}delete \"error\"{self.COLOR_RESET}          - Deletes lines containing the word \"error\".\n"
            f"  {self.COLOR_EXAMPLE}delete \"!error\"{self.COLOR_RESET}         - Deletes lines that do NOT contain the word \"error\".\n"
            f"  {self.COLOR_EXAMPLE}delete \"error OR warning\"{self.COLOR_RESET} - Deletes lines containing either \"error\" or \"warning\".\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - The deleteion is case-sensitive.\n"
            f"  - Supports regex patterns for more complex deleteions.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()
        # Save the current state for undelete functionality
        self.original_full_text = self.current_lines.copy()
        self.deleteed_indices = []

        # Extract the raw input string from the cmd2.parsing.Statement object
        if hasattr(arg, 'args'):
            arg = arg.args

        if not arg:
            #self.poutput("Error: Please provide a string or regex.")
            #return
            arg=""

        # Remove surrounding quotes if present
        arg = arg.strip('"').strip("'")

        # Check if the deleteion is negated (e.g., "!string1")
        negate = False
        if arg.startswith("!"):
            negate = True
            arg = arg[1:]  # Remove the "!" prefix

        # Split the input string on the keyword "OR"
        search_terms = [term.strip() for term in arg.split("OR")]

        try:
            # Compile regex patterns for each search term
            regexes = [re.compile(term.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+")) for term in search_terms]
            if not negate:
                # Delete lines that do NOT match any of the regex patterns
                self.current_lines = [
                    line for line in self.current_lines
                    if not any(regex.search(line) for regex in regexes)
                ]
                self.deleteed_indices = [
                    i for i, line in enumerate(self.original_full_text)
                    if not any(regex.search(line) for regex in regexes)
                ]
            else:
                # Delete lines that match any of the regex patterns
                self.current_lines = [
                    line for line in self.current_lines
                    if any(regex.search(line) for regex in regexes)
                ]
                self.deleteed_indices = [
                    i for i, line in enumerate(self.original_full_text)
                    if any(regex.search(line) for regex in regexes)
                ]
            self.update_live_view()
            self.poutput(f"Remaining {len(self.current_lines)} lines.")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")





    def do_undelete(self, arg):
        """Revert the last delete action while keeping other modifications.

        Usage:
            undelete  - Reverts the last delete action.

        Notes:
            - This command restores the original full text but overwrites the deleted lines with their modified versions.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nRevert the last delete action while keeping other modifications.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}undelete{self.COLOR_RESET}  - Reverts the last delete action.\n\n"
            f"{self.COLOR_COMMAND}Notes:{self.COLOR_RESET}\n"
            f"  - This command restores the original full text but overwrites the deleteed lines with their modified versions.\n"
        )        
        if arg.strip() == "?":  # Check if the argument is just "?"
            self.poutput(help_text)
            return  # Exit the function
        if not hasattr(self, 'original_full_text') or not self.original_full_text:
            self.poutput("Error: No original full text to revert to.")
            return
        if not hasattr(self, 'deleteed_indices') or not self.deleteed_indices:
            self.poutput("Error: No deleteed lines to revert.")
            return

        # Restore the original full text
        self.previous_lines = self.current_lines.copy()
        restored_text = self.original_full_text.copy()

        # Overwrite the deleteed lines with their modified versions
        for i, modified_line in zip(self.deleteed_indices, self.current_lines):
            if i < len(restored_text):
                restored_text[i] = modified_line

        # Update the current lines
        self.current_lines = restored_text
        self.update_live_view()
        self.poutput("Reverted to the original full text with modified deleted lines.")


    def do_multiple_replace(self, arg):
        """Replace multiple strings in the current text using a mapping file or clipboard content.

        Usage:
            multiple_replace <map_file> [separator] [ > output_file ]
            multiple_replace             - Use clipboard content as the mapping file with space as the separator.

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
            multiple_replace              - Uses clipboard content as the mapping file with space as the separator.
        """
        import sys
        import os
        import pandas as pd  # Required for reading Excel files    
        help_text = (
            f"{self.COLOR_HEADER}\nReplace multiple strings in the current text using a mapping file or clipboard content.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace <map_file> [separator] [ > output_file ]{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace{self.COLOR_RESET}             - Use clipboard content as the mapping file with space as the separator.\n\n"
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
            f"  {self.COLOR_EXAMPLE}multiple_replace map.xlsx >{self.COLOR_RESET}   - Outputs the result to the clipboard.\n"
            f"  {self.COLOR_EXAMPLE}multiple_replace{self.COLOR_RESET}              - Uses clipboard content as the mapping file with space as the separator.\n\n"
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
        
        if not arg:  # If no arguments are provided, use clipboard content
            clipboard_content = cmd2.clipboard.get_paste_buffer()
            if not clipboard_content:
                self.poutput("Error: Clipboard is empty or does not contain text.")
                return
            
            # Split clipboard content into lines and then into key-value pairs
            replacements = {}
            for line in clipboard_content.splitlines():
                parts = line.strip().split(" ", 1)  # Split on the first space
                if len(parts) == 2:
                    key, value = parts
                    replacements[key] = value
                else:
                    self.poutput(f"Warning: Skipping invalid line in clipboard: {line}")
            
            if not replacements:
                self.poutput("Error: No valid key-value pairs found in clipboard.")
                return
            
            # Perform the replacements
            for old_text, new_text in replacements.items():
                self.current_lines = [line.replace(old_text, new_text) for line in self.current_lines]
            
            self.update_live_view()
            self.poutput("Replacement completed using clipboard content.")
            return
        
        # If arguments are provided, proceed with the original logic
        if len(arg.split())==2:
            separator = _unquote(arg.split()[1])
        elif len(arg.split())==1:
            separator="space"
        else:
            self.poutput(help_text)
            return
        
        map_file=_unquote(retrieve_spaces(arg.split()[0]))
        if not os.path.exists(map_file):
            print(f"Error: Mapping file '{map_file}' does not exist.")
            sys.exit(1)  
        replacements = read_mapping_file(map_file, separator)      
        for old_text, new_text in replacements.items():
            self.current_lines = [line.replace(old_text, new_text) for line in self.current_lines]
            
        self.update_live_view()
        self.poutput("Replacement completed.")
        
    def do_replace(self, arg):
        """Replace a string with another in the current text. Supports regex and capture groups.
        
        Usage:
            replace "string1" "string2" [case_sensitive]
            replace string1 string2 [case_sensitive]

        By default, replacement is case insensitive.
        Add 'case_sensitive' to make it case sensitive.
        """
        help_text = (
            f"{self.COLOR_HEADER}\nReplace a string with another in the current text. Supports regex and capture groups.{self.COLOR_RESET}\n\n"
            f"{self.COLOR_COMMAND}Usage:{self.COLOR_RESET}\n"
            f"  {self.COLOR_EXAMPLE}replace \"string1\" \"string2\"{self.COLOR_RESET}  - Replace string1 with string2 (case insensitive).\n"
            f"  {self.COLOR_EXAMPLE}replace \"string1\" \"string2\" case_sensitive{self.COLOR_RESET}  - Case sensitive replacement.\n"
            f"  {self.COLOR_EXAMPLE}replace string1 string2{self.COLOR_RESET}      - Replace string1 with string2 (if no spaces in strings).\n\n"
            # ... rest of help text remains the same
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

        # Check for case_sensitive parameter
        case_sensitive = "case_sensitive" in arg
        if case_sensitive:
            arg = arg.replace("case_sensitive", "").strip()

        # Check if the arguments are quoted
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput("Error: Invalid arguments. Usage: replace \"string1\" \"string2\" OR replace string1 string2")
                return
            string1, string2 = args[0], args[1]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"

        try:
            # Compile the regex pattern with appropriate flags
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(string1.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), flags)

            # Replace \0 with the entire match
            if "\\0" in string2:
                def replacement(match):
                    return string2.replace("\\0", match.group(0)).replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+")

                self.current_lines = [regex.sub(replacement, line) for line in self.current_lines]
                self.update_live_view()
            else:
                # Perform the replacement using the regex pattern and the replacement string
                self.current_lines = [regex.sub(string2.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), line) for line in self.current_lines]
                self.update_live_view()

            sensitivity = "case sensitive" if case_sensitive else "case insensitive"
            self.poutput(f"Replacement completed ({sensitivity}).")
        except re.error as e:
            self.poutput(f"Error: Invalid regex pattern or replacement string. Details: {e}")
            self.poutput(f"Literal replacement will be now tried")
            try:
                if case_sensitive:
                    self.current_lines = [line.replace(string1.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), string2.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+")) for line in self.current_lines]
                else:
                    # Case insensitive literal replacement
                    for i, line in enumerate(self.current_lines):
                        line_lower = line.lower()
                        search_lower = string1.lower()
                        if search_lower in line_lower:
                            start_idx = line_lower.find(search_lower)
                            end_idx = start_idx + len(string1)
                            self.current_lines[i] = line[:start_idx] + string2 + line[end_idx:]
                self.update_live_view()
                sensitivity = "case sensitive" if case_sensitive else "case insensitive"
                self.poutput(f"Literal Replacement completed ({sensitivity}).")
            except Exception as d:
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
        self.update_live_view()
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
            - {self.COLOR_EXAMPLE}`\\Aabc`{self.COLOR_RESET}: Matches "abc" only at the start of the string.
            - {self.COLOR_EXAMPLE}`abc\\Z`{self.COLOR_RESET}: Matches "abc" only at the end of the string.
            - {self.COLOR_EXAMPLE}`\\bword\\b`{self.COLOR_RESET}: Matches "word" as a whole word (word boundary).
        
        {self.COLOR_COMMAND}4. Character Classes:{self.COLOR_RESET}
            - {self.COLOR_EXAMPLE}`\\d`{self.COLOR_RESET}: Matches any digit (equivalent to `[0-9]`).
            - {self.COLOR_EXAMPLE}`\\D`{self.COLOR_RESET}: Matches any non-digit (equivalent to `[^0-9]`).
            - {self.COLOR_EXAMPLE}`\\w`{self.COLOR_RESET}: Matches any word character (alphanumeric + underscore).
            - {self.COLOR_EXAMPLE}`\\W`{self.COLOR_RESET}: Matches any non-word character.
            - {self.COLOR_EXAMPLE}`\\s`{self.COLOR_RESET}: Matches any whitespace character (space, tab, newline).
            - {self.COLOR_EXAMPLE}`\\S`{self.COLOR_RESET}: Matches any non-whitespace character.
            - {self.COLOR_EXAMPLE}`.`{self.COLOR_RESET}: Matches any character except a newline.
        
        {self.COLOR_COMMAND}5. Groups and Capturing:{self.COLOR_RESET}
            - {self.COLOR_EXAMPLE}`(abc)`{self.COLOR_RESET}: Matches "abc" and captures it as a group.
            - {self.COLOR_EXAMPLE}`\\1`{self.COLOR_RESET}: Refers to the first captured group (valid in replacement).
            - {self.COLOR_EXAMPLE}`\\0`{self.COLOR_RESET}: Refers to the entire match (implemented in this tool).
        
        {self.COLOR_COMMAND}6. Special Characters:{self.COLOR_RESET}
            - {self.COLOR_EXAMPLE}`\\.`{self.COLOR_RESET}: Matches a literal period (escape special characters).
            - {self.COLOR_EXAMPLE}`\\\\`{self.COLOR_RESET}: Matches a literal backslash.
            - {self.COLOR_EXAMPLE}`\\n`{self.COLOR_RESET}: Matches a newline character (valid in replacement).
            - {self.COLOR_EXAMPLE}`\\t`{self.COLOR_RESET}: Matches a tab character (valid in replacement).
            - {self.COLOR_EXAMPLE}`\\r`{self.COLOR_RESET}: Matches a carriage return character.
        
        {self.COLOR_COMMAND}7. Replacement String Rules:{self.COLOR_RESET}
            - {self.COLOR_EXAMPLE}`\\1`, `\\2`, etc.{self.COLOR_RESET}: Backreferences to captured groups (valid in replacement).
            - {self.COLOR_EXAMPLE}`\\0`{self.COLOR_RESET}: Refers to the entire match (implemented in this tool).
            - {self.COLOR_EXAMPLE}`\\s`, `\\d`, `\\w`, etc.{self.COLOR_RESET}: NOT valid in replacement (only in pattern).
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
            self.hidden_commands.remove('select_from_file')
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
            self.hidden_commands.append('select_from_file')
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
                    self.update_live_view()
                    return
                else:
                    new_line += before + match.group()
                start_idx = match.end()
            
            new_line += line[start_idx:]
            updated_lines.append(new_line)
        
        self.current_lines = updated_lines
        self.update_live_view()
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
            replace_in_lines "search_pattern" "replace_pattern" "target_pattern" [case_sensitive]

        By default, replacement is case insensitive.
        Add 'case_sensitive' to make it case sensitive.
        """
        if arg.strip() == "?":
            self.do_help("replace_in_lines")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return
            
        self.previous_lines = self.current_lines.copy()

        # Check for case_sensitive parameter
        case_sensitive = "case_sensitive" in arg
        if case_sensitive:
            arg = arg.replace("case_sensitive", "").strip()

        # Check if the arguments are quoted
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            search_pattern, replace_pattern, target_pattern= args[1], args[3], args[5]
            if (search_pattern.startswith("(") or search_pattern.startswith("\\") or "." in search_pattern) and not (search_pattern.startswith("^") and search_pattern.endswith("$")):
                search_pattern = f"^{search_pattern}$"
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            search_pattern, replace_pattern, target_pattern= args[1], args[3], args[5]
            if (search_pattern.startswith("(") or search_pattern.startswith("\\") or "." in search_pattern) and not (search_pattern.startswith("^") and search_pattern.endswith("$")):
                search_pattern = f"^{search_pattern}$"            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput("Error: Invalid arguments. Usage: replace_in_lines \"search_pattern\" \"replace_pattern\" \"target_pattern\" ")
                return
            search_pattern, replace_pattern, target_pattern= args[0], args[1], args[2]
            if (search_pattern.startswith("(") or search_pattern.startswith("\\") or "." in search_pattern) and not (search_pattern.startswith("^") and search_pattern.endswith("$")):
                search_pattern = f"^{search_pattern}$"

        try:
            # Use appropriate flags based on case sensitivity
            flags = 0 if case_sensitive else re.IGNORECASE
            target_regex = re.compile(target_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), flags)
            search_regex = re.compile(search_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), flags)
            
            self.current_lines = [
                search_regex.sub(replace_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), line) if target_regex.search(line) else line
                for line in self.current_lines
            ]
            self.update_live_view()
            sensitivity = "case sensitive" if case_sensitive else "case insensitive"
            self.poutput(f"Replacement completed in specified lines ({sensitivity}).")
        except re.error:
            self.poutput("Error: Invalid regex pattern.")
            self.poutput(f"Literal replacement will be now tried")
            try:
                if case_sensitive:
                    self.current_lines = [line.replace(search_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+"), replace_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+")) if target_pattern.replace('[doublequote]','\\"').replace('[pipe]','\\|').replace('[quote]',"\\'").replace('[tab]',"\t").replace('[spaces]',r"[^\S\r\n]+") in line else line for line in self.current_lines]
                else:
                    # Case insensitive literal replacement
                    target_lower = target_pattern.lower()
                    search_lower = search_pattern.lower()
                    for i, line in enumerate(self.current_lines):
                        if target_lower in line.lower():
                            line_lower = line.lower()
                            if search_lower in line_lower:
                                start_idx = line_lower.find(search_lower)
                                end_idx = start_idx + len(search_pattern)
                                self.current_lines[i] = line[:start_idx] + replace_pattern + line[end_idx:]
                self.update_live_view()
                sensitivity = "case sensitive" if case_sensitive else "case insensitive"
                self.poutput(f"Literal Replacement completed ({sensitivity}).")
            except Exception as d:
                self.poutput(f"Literal Replacement failed. Details: {d}")

    def do_extract_between(self, arg):
        """Extract all sections of text between pairs of start_pattern and end_pattern.

        Usage:
            extract_between "start_pattern" "end_pattern"

        Description:
            Finds every occurrence of start_pattern and extracts all text from that point
            until the next occurrence of end_pattern (inclusive). The process repeats
            for the whole text.

        Example:
            extract_between "BEGIN" "END"
            → extracts all segments between each 'BEGIN' and the next 'END'.
        """
        if arg.strip() == "?":
            self.do_help("extract_between")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            start_pattern, end_pattern = args[1], args[3]
            if (start_pattern.startswith("(") or start_pattern.startswith("\\") or "." in start_pattern) and not (start_pattern.startswith("^") and start_pattern.endswith("$")):
                start_pattern = f"^{start_pattern}$"
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            start_pattern, end_pattern = args[1], args[3]
            if (start_pattern.startswith("(") or start_pattern.startswith("\\") or "." in start_pattern) and not (start_pattern.startswith("^") and start_pattern.endswith("$")):
                start_pattern = f"^{start_pattern}$"            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput("Error: Invalid arguments. Usage: extract_between \"start_pattern\" \"end_pattern\"")
                return
            start_pattern, end_pattern = args[0], args[1]
            if (start_pattern.startswith("(") or start_pattern.startswith("\\") or "." in start_pattern) and not (start_pattern.startswith("^") and start_pattern.endswith("$")):
                start_pattern = f"^{start_pattern}$"

        try:
            start_regex = re.compile(start_pattern)
            end_regex = re.compile(end_pattern)

            extracting = False
            extracted_lines = []

            i = 0
            while i < len(self.current_lines):
                line = self.current_lines[i]
                if not extracting and start_regex.search(line):
                    # Found a start
                    extracting = True
                    segment = [line]
                    i += 1
                    # Collect until the next end_pattern
                    while i < len(self.current_lines):
                        segment.append(self.current_lines[i])
                        if end_regex.search(self.current_lines[i]):
                            extracted_lines.extend(segment)
                            break
                        i += 1
                    
                    extracting = False
                i += 1

            if extracted_lines:
                self.current_lines = extracted_lines
                self.update_live_view()
                self.poutput(f"Extracted {len(extracted_lines)} lines between matching patterns.")
            else:
                self.poutput("No matching start/end patterns found.")
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
            self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        import pandas as pd
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
            self.update_live_view()
        else:
            self.current_lines = [line for line in self.current_lines if any(s in line for s in strings)]
            self.update_live_view()
        
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
            self.update_live_view()
        elif case_type == "lower":
            self.current_lines = [line.lower() for line in self.current_lines]
            self.update_live_view()
        elif case_type == "title":
            self.current_lines = [line.title() for line in self.current_lines]
            self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()
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
        self.update_live_view()

        self.poutput(f"Empty lines removed successfully. Deleted {deleted_lines_count} lines.")
        

    def do_sync_from_liveview(self, arg):
        """Synchronize the content of the Live View back into current_lines.

        Usage:
            sync_from_liveview

        Description:
            Reads the editable content of the Live View window and overwrites
            self.current_lines with it.
            Useful if the user manually modified text directly in the Live View.

        Notes:
            - If the Live View window is not open, an error is shown.
            - The synchronization replaces current_lines entirely.
            - The previous state is saved so 'revert' can undo the change.
            - The Live View is refreshed immediately after syncing.
        """
        if not hasattr(self, "liveview_box") or self.liveview_box is None:
            self.poutput("Error: Live View window is not running.")
            return

        try:
            # Read all content from the text box
            new_text = self.liveview_box.get("1.0", tk.END)

            # Save current state for revert
            self.previous_lines = self.current_lines.copy()

            # Replace current_lines with content from Live View
            self.current_lines = [line for line in new_text.splitlines(keepends=True)]

            # Refresh Live View to ensure consistency and show new line count
            self.update_live_view()

            self.poutput(f"Synchronized {len(self.current_lines)} lines from Live View.")
        except Exception as e:
            self.poutput(f"Error reading Live View content: {e}")


    def do_right_replace(self, arg):
        """Replace everything from and including string1 to the end of the line with string2.

        Usage:
            right_replace "string1" "string2" [case_sensitive]

        By default, replacement is case insensitive.
        Add 'case_sensitive' to make it case sensitive.
        """
        if arg.strip() == "?":
            self.do_help("right_replace")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        # Check for case_sensitive parameter
        case_sensitive = "case_sensitive" in arg
        if case_sensitive:
            arg = arg.replace("case_sensitive", "").strip()

        # Parse arguments
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput('Error: Invalid syntax. Usage: right_replace "string1" "string2"')
                return
            string1, string2 = args[0], args[1]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"

        new_lines = []
        for line in self.current_lines:
            if case_sensitive:
                idx = line.find(string1)
            else:
                idx = line.lower().find(string1.lower())
            if idx != -1:
                new_lines.append(line[:idx] + string2 + "\n")
            else:
                new_lines.append(line)
        self.current_lines = new_lines

        self.update_live_view()
        sensitivity = "case sensitive" if case_sensitive else "case insensitive"
        self.poutput(f"Right-side replacement completed ({sensitivity}).")

    def do_left_replace(self, arg):
        """Replace everything from the start of the line up to and including string1 with string2.

        Usage:
            left_replace "string1" "string2" [case_sensitive]

        By default, replacement is case insensitive.
        Add 'case_sensitive' to make it case sensitive.
        """
        if arg.strip() == "?":
            self.do_help("left_replace")
            return
        if not self.current_lines:
            self.poutput("Error: No file is loaded.")
            return

        self.previous_lines = self.current_lines.copy()

        # Check for case_sensitive parameter
        case_sensitive = "case_sensitive" in arg
        if case_sensitive:
            arg = arg.replace("case_sensitive", "").strip()

        # Parse arguments
        if arg.startswith('"') and arg.count('"') >= 2:
            # Split the arguments by double quotes
            args = arg.split('"')
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"
        elif arg.startswith("'") and arg.count("'") >= 2:
            # Split the arguments by double quotes
            args = arg.split("'")
            string1, string2 = args[1], args[3]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"            
        else:
            # Split the arguments by spaces (for unquoted arguments)
            args = arg.split()
            if len(args) < 2:
                self.poutput('Error: Invalid syntax. Usage: left_replace "string1" "string2"')
                return
            string1, string2 = args[0], args[1]
            if (string1.startswith("(") or string1.startswith("\\") or "." in string1) and not (string1.startswith("^") and string1.endswith("$")):
                string1 = f"^{string1}$"

        new_lines = []
        for line in self.current_lines:
            if case_sensitive:
                idx = line.find(string1)
            else:
                idx = line.lower().find(string1.lower())
            if idx != -1:
                new_lines.append(string2 + line[idx + len(string1):])
            else:
                new_lines.append(line)
        self.current_lines = new_lines

        self.update_live_view()
        sensitivity = "case sensitive" if case_sensitive else "case insensitive"
        self.poutput(f"Left-side replacement completed ({sensitivity}).")



    def do_diff(self, arg):
        diff = difflib.unified_diff(
            self.previous_lines, self.current_lines,
            fromfile='previous', tofile='current', lineterm=''
        )
        self.poutput('\n'.join(diff))



if __name__ == '__main__':
    app = TextTool()
    app.cmdloop()
