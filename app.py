import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
from datetime import datetime


class SQLiteViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Viewer - Professional Edition")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f2f5")

        # Setup styles
        self.setup_styles()

        self.conn = None
        self.cursor = None
        self.current_table = None
        self.db_name = None

        # Create main container
        main_container = ttk.Frame(root, style="Card.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Top panel with info and open button
        top_frame = ttk.Frame(main_container, style="Header.TFrame")
        top_frame.pack(fill="x", padx=10, pady=10)

        # Title and database info
        self.title_label = ttk.Label(top_frame,
                                     text="SQLite Database Viewer",
                                     style="Title.TLabel",
                                     font=("Segoe UI", 16, "bold"))
        self.title_label.pack(side="left", padx=10)

        self.db_info_label = ttk.Label(top_frame,
                                       text="No database opened",
                                       style="Info.TLabel",
                                       font=("Segoe UI", 10))
        self.db_info_label.pack(side="left", padx=10)

        # Open database button with icon
        self.btn_open = ttk.Button(top_frame,
                                   text="📂 Open Database",
                                   command=self.open_database,
                                   style="Primary.TButton")
        self.btn_open.pack(side="right", padx=10)

        # Control panel
        control_frame = ttk.Frame(main_container, style="Card.TFrame")
        control_frame.pack(fill="x", padx=10, pady=10)

        # Table selection
        ttk.Label(control_frame,
                  text="Table:",
                  style="Label.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.table_selector = ttk.Combobox(control_frame,
                                           state="readonly",
                                           width=30,
                                           style="Custom.TCombobox")
        self.table_selector.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.table_selector.bind("<<ComboboxSelected>>", self.load_table)

        # Search field
        ttk.Label(control_frame,
                  text="Search:",
                  style="Label.TLabel").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")

        self.entry_search = ttk.Entry(control_frame,
                                      width=40,
                                      style="Search.TEntry")
        self.entry_search.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.btn_search = ttk.Button(control_frame,
                                     text="🔍 Search",
                                     command=self.search_records,
                                     style="Secondary.TButton")
        self.btn_search.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.btn_clear_search = ttk.Button(control_frame,
                                           text="🗑 Clear",
                                           command=self.clear_search,
                                           style="Tertiary.TButton")
        self.btn_clear_search.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Data table
        table_container = ttk.Frame(main_container, style="Card.TFrame")
        table_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(table_container)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Horizontal scrollbar
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_frame,
                                 show="headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set,
                                 style="Tree.Treeview")
        self.tree.pack(fill="both", expand=True)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Control buttons panel
        btn_frame = ttk.Frame(main_container, style="Card.TFrame")
        btn_frame.pack(fill="x", padx=10, pady=10)

        # Create buttons with icons
        buttons = [
            ("➕ Add Record", self.add_record, "Success.TButton"),
            ("✏ Edit Record", self.edit_record, "Warning.TButton"),
            ("❌ Delete Record", self.delete_record, "Danger.TButton"),
            ("🔄 Refresh", self.load_table, "Info.TButton"),
            ("📊 Table Info", self.show_table_info, "Primary.TButton"),
            ("💾 Export", self.export_data_menu, "Success.TButton")
        ]

        for i, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(btn_frame,
                             text=text,
                             command=command,
                             style=style)
            btn.grid(row=0, column=i, padx=5, pady=5)

        # Status bar
        self.status_bar = ttk.Label(main_container,
                                    text="Ready to work",
                                    style="Status.TLabel")
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

        # Styles for alternating row colors
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('selected', background='#007bff', foreground='white')

    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()

        # Use 'clam' theme as base
        style.theme_use('clam')

        # Configure colors
        colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }

        # Style for main background
        style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Header.TFrame", background="#ffffff")

        # Label styles
        style.configure("Title.TLabel", background="#ffffff", foreground=colors['dark'])
        style.configure("Info.TLabel", background="#ffffff", foreground=colors['secondary'])
        style.configure("Label.TLabel", background="#ffffff", foreground=colors['dark'], font=("Segoe UI", 9))
        style.configure("Status.TLabel", background=colors['dark'], foreground="#ffffff", anchor="center")

        # Button styles
        style.configure("Primary.TButton",
                        background=colors['primary'],
                        foreground="white",
                        borderwidth=0,
                        focuscolor="none")
        style.map("Primary.TButton",
                  background=[('active', '#0056b3'), ('disabled', colors['secondary'])])

        style.configure("Secondary.TButton",
                        background=colors['secondary'],
                        foreground="white",
                        borderwidth=0)
        style.map("Secondary.TButton",
                  background=[('active', '#545b62'), ('disabled', colors['secondary'])])

        style.configure("Success.TButton",
                        background=colors['success'],
                        foreground="white",
                        borderwidth=0)
        style.map("Success.TButton",
                  background=[('active', '#1e7e34'), ('disabled', colors['secondary'])])

        style.configure("Danger.TButton",
                        background=colors['danger'],
                        foreground="white",
                        borderwidth=0)
        style.map("Danger.TButton",
                  background=[('active', '#bd2130'), ('disabled', colors['secondary'])])

        style.configure("Warning.TButton",
                        background=colors['warning'],
                        foreground=colors['dark'],
                        borderwidth=0)
        style.map("Warning.TButton",
                  background=[('active', '#e0a800'), ('disabled', colors['secondary'])])

        style.configure("Info.TButton",
                        background=colors['info'],
                        foreground="white",
                        borderwidth=0)
        style.map("Info.TButton",
                  background=[('active', '#117a8b'), ('disabled', colors['secondary'])])

        style.configure("Tertiary.TButton",
                        background=colors['light'],
                        foreground=colors['dark'],
                        borderwidth=0)
        style.map("Tertiary.TButton",
                  background=[('active', '#e2e6ea'), ('disabled', colors['secondary'])])

        # Entry field style
        style.configure("Search.TEntry",
                        fieldbackground="#ffffff",
                        borderwidth=1,
                        relief="solid")

        # Treeview style
        style.configure("Tree.Treeview",
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        foreground=colors['dark'],
                        rowheight=25,
                        borderwidth=0)

        style.configure("Tree.Treeview.Heading",
                        background=colors['primary'],
                        foreground="white",
                        relief="flat",
                        borderwidth=0,
                        font=("Segoe UI", 10, "bold"))

        style.map("Tree.Treeview.Heading",
                  background=[('active', colors['primary'])])

    def open_database(self):
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[
                ("SQLite Database", "*.sqlite *.db *.sqlite3"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return

        try:
            self.conn = sqlite3.connect(file_path)
            self.cursor = self.conn.cursor()
            self.db_name = os.path.basename(file_path)
            self.db_info_label.config(text=f"Database: {self.db_name}")
            self.load_tables()
            self.status_bar.config(text=f"Database opened successfully: {self.db_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database:\n{e}")
            self.status_bar.config(text="Error opening database")

    def load_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in self.cursor.fetchall()]

        if tables:
            self.table_selector["values"] = tables
            self.table_selector.current(0)
            self.load_table()
            self.status_bar.config(text=f"Loaded {len(tables)} tables")
        else:
            messagebox.showinfo("Information", "No tables found in database")
            self.status_bar.config(text="No tables in database")

    def load_table(self, event=None):
        if not self.table_selector.get():
            return

        self.current_table = self.table_selector.get()
        self.db_info_label.config(text=f"Database: {self.db_name} | Table: {self.current_table}")

        try:
            self.cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in self.cursor.fetchall()]

            # Clear current data
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.tree["columns"] = columns

            # Configure headers
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, minwidth=50, stretch=True)

            # Load data
            self.cursor.execute(f"SELECT * FROM {self.current_table}")
            rows = self.cursor.fetchall()

            # Add rows with alternating colors
            for i, row in enumerate(rows):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row, tags=(tag,))

            self.status_bar.config(text=f"Table '{self.current_table}': {len(rows)} records")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table:\n{e}")
            self.status_bar.config(text="Error loading table")

    def search_records(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table for search")
            return

        search_text = self.entry_search.get().strip()
        if not search_text:
            self.load_table()
            return

        try:
            self.cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in self.cursor.fetchall()]

            query = f"SELECT * FROM {self.current_table} WHERE " + " OR ".join([f"{col} LIKE ?" for col in columns])
            self.cursor.execute(query, tuple(f"%{search_text}%" for _ in columns))
            results = self.cursor.fetchall()

            # Clear table
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Display results
            for i, row in enumerate(results):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row, tags=(tag,))

            self.status_bar.config(text=f"Found {len(results)} records for: '{search_text}'")

        except Exception as e:
            messagebox.showerror("Error", f"Search error:\n{e}")

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.load_table()
        self.status_bar.config(text="Search cleared")

    def add_record(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table")
            return

        cols = self.tree["columns"]
        values = self.get_user_input(cols, "Add New Record")

        if values:
            try:
                placeholders = ", ".join("?" * len(cols))
                query = f"INSERT INTO {self.current_table} VALUES ({placeholders})"
                self.cursor.execute(query, values)
                self.conn.commit()
                self.load_table()
                self.status_bar.config(text="Record added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add record:\n{e}")

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to edit")
            return

        cols = self.tree["columns"]
        old_values = self.tree.item(selected[0])["values"]
        new_values = self.get_user_input(cols, "Edit Record", old_values)

        if new_values:
            try:
                # Find primary key
                self.cursor.execute(f"PRAGMA table_info({self.current_table})")
                table_info = self.cursor.fetchall()
                pk_column = None
                for col in table_info:
                    if col[5]:  # Fifth element shows if column is PK
                        pk_column = col[1]
                        break

                if pk_column:
                    pk_index = [col[1] for col in table_info].index(pk_column)
                    set_clause = ", ".join(f"{col} = ?" for col in cols)
                    query = f"UPDATE {self.current_table} SET {set_clause} WHERE {pk_column} = ?"
                    self.cursor.execute(query, new_values + [old_values[pk_index]])
                else:
                    # If no PK, use all values for WHERE
                    set_clause = ", ".join(f"{col} = ?" for col in cols)
                    where_clause = " AND ".join(f"{col} = ?" for col in cols)
                    query = f"UPDATE {self.current_table} SET {set_clause} WHERE {where_clause}"
                    self.cursor.execute(query, new_values + old_values)

                self.conn.commit()
                self.load_table()
                self.status_bar.config(text="Record updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update record:\n{e}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete")
            return

        confirm = messagebox.askyesno("Confirm Deletion",
                                      "Are you sure you want to delete the selected record?",
                                      icon='warning')
        if confirm:
            try:
                old_values = self.tree.item(selected[0])["values"]

                # Find primary key for deletion
                self.cursor.execute(f"PRAGMA table_info({self.current_table})")
                table_info = self.cursor.fetchall()
                pk_column = None
                for col in table_info:
                    if col[5]:
                        pk_column = col[1]
                        break

                if pk_column:
                    pk_index = [col[1] for col in table_info].index(pk_column)
                    query = f"DELETE FROM {self.current_table} WHERE {pk_column} = ?"
                    self.cursor.execute(query, (old_values[pk_index],))
                else:
                    # If no PK, use all values for WHERE
                    where_clause = " AND ".join(f"{col} = ?" for col in self.tree["columns"])
                    query = f"DELETE FROM {self.current_table} WHERE {where_clause}"
                    self.cursor.execute(query, old_values)

                self.conn.commit()
                self.load_table()
                self.status_bar.config(text="Record deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record:\n{e}")

    def show_table_info(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table")
            return

        try:
            self.cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns_info = self.cursor.fetchall()

            self.cursor.execute(f"SELECT COUNT(*) FROM {self.current_table}")
            row_count = self.cursor.fetchone()[0]

            info_text = f"Table: {self.current_table}\n"
            info_text += f"Record count: {row_count}\n\n"
            info_text += "Table structure:\n"
            info_text += "-" * 50 + "\n"

            for col in columns_info:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else "NULL"
                pk = "PRIMARY KEY" if col[5] else ""
                info_text += f"{col_name}: {col_type} {not_null} {pk}\n"

            messagebox.showinfo("Table Information", info_text)
            self.status_bar.config(text=f"Table information: '{self.current_table}'")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get table information:\n{e}")

    def export_data_menu(self):
        """Show export options menu"""
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table")
            return

        # Create menu for export options
        export_menu = tk.Menu(self.root, tearoff=0)
        export_menu.add_command(label="📊 Export to CSV", command=self.export_to_csv)
        export_menu.add_command(label="📈 Export to Excel", command=self.export_to_excel)
        export_menu.add_separator()
        export_menu.add_command(label="📄 Export as SQL", command=self.export_to_sql)
        export_menu.add_command(label="📝 Export as Text", command=self.export_to_text)

        # Show menu near export button
        try:
            export_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            export_menu.grab_release()

    def export_to_csv(self):
        """Export data to CSV format"""
        self.export_data('csv')

    def export_to_excel(self):
        """Export data to Excel format"""
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table")
            return

        try:
            # Get data from database
            self.cursor.execute(f"SELECT * FROM {self.current_table}")
            data = self.cursor.fetchall()

            # Get column names
            self.cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in self.cursor.fetchall()]

            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)

            # Ask for save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{self.current_table}_{timestamp}.xlsx"

            file_path = filedialog.asksaveasfilename(
                title="Export to Excel",
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("Excel 97-2003", "*.xls"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                # Export to Excel with formatting
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=self.current_table, index=False)

                    # Auto-adjust column widths
                    worksheet = writer.sheets[self.current_table]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

                self.status_bar.config(text=f"Data exported to Excel: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Successful",
                                    f"Data successfully exported to Excel!\n\n"
                                    f"File: {os.path.basename(file_path)}\n"
                                    f"Path: {file_path}\n"
                                    f"Records: {len(data)}")

        except ImportError:
            messagebox.showerror("Export Error",
                                 "Required libraries not installed.\n\n"
                                 "Please install pandas and openpyxl:\n"
                                 "pip install pandas openpyxl")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Excel:\n{e}")

    def export_to_sql(self):
        """Export data to SQL format"""
        self.export_data('sql')

    def export_to_text(self):
        """Export data to Text format"""
        self.export_data('txt')

    def export_data(self, filetype='csv'):
        """General export function"""
        if not self.current_table:
            messagebox.showwarning("Warning", "Select a table")
            return

        file_extensions = {
            'csv': '.csv',
            'excel': '.xlsx',
            'sql': '.sql',
            'txt': '.txt'
        }

        file_types = {
            'csv': [("CSV files", "*.csv"), ("All files", "*.*")],
            'excel': [("Excel files", "*.xlsx"), ("Excel 97-2003", "*.xls"), ("All files", "*.*")],
            'sql': [("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
            'txt': [("Text files", "*.txt"), ("All files", "*.*")]
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{self.current_table}_{timestamp}{file_extensions.get(filetype, '.csv')}"

        file_path = filedialog.asksaveasfilename(
            title=f"Export to {filetype.upper()}",
            defaultextension=file_extensions.get(filetype, '.csv'),
            initialfile=default_filename,
            filetypes=file_types.get(filetype, [("All files", "*.*")])
        )

        if file_path:
            try:
                self.cursor.execute(f"SELECT * FROM {self.current_table}")
                rows = self.cursor.fetchall()

                # Get column names
                cols = self.tree["columns"]

                if filetype == 'csv':
                    # Export to CSV
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # Write headers
                        f.write(','.join(cols) + '\n')
                        # Write data
                        for row in rows:
                            f.write(','.join(str(value).replace(',', ';') for value in row) + '\n')

                elif filetype == 'txt':
                    # Export to text with formatting
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Table: {self.current_table}\n")
                        f.write(f"Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Record count: {len(rows)}\n")
                        f.write("=" * 80 + "\n\n")

                        # Write headers
                        header = " | ".join(cols)
                        f.write(header + "\n")
                        f.write("-" * len(header) + "\n")

                        # Write data
                        for row in rows:
                            line = " | ".join(str(value) for value in row)
                            f.write(line + "\n")

                elif filetype == 'sql':
                    # Export as SQL INSERT statements
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"-- SQL Export for table: {self.current_table}\n")
                        f.write(f"-- Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"-- Record count: {len(rows)}\n\n")

                        for row in rows:
                            values = []
                            for value in row:
                                if value is None:
                                    values.append("NULL")
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                else:
                                    # ИСПРАВЛЕННАЯ СТРОКА - используем переменную для экранирования
                                    escaped_value = str(value).replace("'", "''")
                                    values.append(f"'{escaped_value}'")

                            insert_stmt = f"INSERT INTO {self.current_table} VALUES ({', '.join(values)});\n"
                            f.write(insert_stmt)

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{e}")

    def get_user_input(self, columns, title, old_values=None):
        input_win = tk.Toplevel(self.root)
        input_win.title(title)
        input_win.geometry("400x400")
        input_win.configure(bg="#f0f2f5")
        input_win.transient(self.root)
        input_win.grab_set()

        # Center the window
        input_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - input_win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - input_win.winfo_height()) // 2
        input_win.geometry(f"+{x}+{y}")

        container = ttk.Frame(input_win, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(container,
                  text=title,
                  style="Title.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(pady=10)

        entries = []
        for i, col in enumerate(columns):
            frame = ttk.Frame(container)
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame,
                      text=f"{col}:",
                      style="Label.TLabel",
                      width=20).pack(side="left")

            entry = ttk.Entry(frame,
                              style="Search.TEntry",
                              width=30)
            entry.pack(side="left", fill="x", expand=True)

            if old_values:
                entry.insert(0, old_values[i])

            entries.append(entry)

        def submit():
            values = [entry.get() for entry in entries]
            input_win.destroy()
            input_win.result = values

        def cancel():
            input_win.destroy()
            input_win.result = None

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame,
                   text="✅ Save",
                   command=submit,
                   style="Success.TButton").pack(side="left", padx=5)

        ttk.Button(btn_frame,
                   text="❌ Cancel",
                   command=cancel,
                   style="Danger.TButton").pack(side="left", padx=5)

        # Handle Enter key for submission
        input_win.bind('<Return>', lambda e: submit())
        input_win.bind('<Escape>', lambda e: cancel())

        input_win.result = None
        input_win.wait_window()
        return input_win.result


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteViewer(root)
    root.mainloop()