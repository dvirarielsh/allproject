import os
import json
import subprocess
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

PROJECTS_FILE = "projects.json"

class ProjectManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Project Manager")
        self.projects = []
        self.selected_project = None
        self.setup_ui()
        self.load_projects()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.project_list = tk.Listbox(self.master, width=40, exportselection=False)
        self.project_list.grid(row=0, column=0, rowspan=6, padx=5, pady=5, sticky="ns")
        self.project_list.bind("<<ListboxSelect>>", self.on_project_select)

        tk.Button(self.master, text="Add Project", command=self.add_project).grid(row=0, column=1, pady=2)
        tk.Button(self.master, text="Remove Project", command=self.remove_project).grid(row=1, column=1, pady=2)
        tk.Button(self.master, text="Open Folder", command=self.open_folder).grid(row=2, column=1, pady=2)

        self.file_list = tk.Listbox(self.master, width=40, exportselection=False)
        self.file_list.grid(row=0, column=2, rowspan=6, padx=5, pady=5, sticky="ns")
        self.file_list.bind("<<ListboxSelect>>", self.on_file_select)

        tk.Button(self.master, text="New File", command=self.new_file).grid(row=0, column=3, pady=2)
        tk.Button(self.master, text="Download File", command=self.download_file).grid(row=1, column=3, pady=2)
        tk.Button(self.master, text="Add File", command=self.add_file).grid(row=2, column=3, pady=2)
        tk.Button(self.master, text="Run File", command=self.run_file).grid(row=3, column=3, pady=2)

        self.preview = scrolledtext.ScrolledText(self.master, width=80, height=20, state="disabled")
        self.preview.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

    def load_projects(self):
        if os.path.exists(PROJECTS_FILE):
            try:
                with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                    self.projects = json.load(f)
                for p in self.projects:
                    self.project_list.insert(tk.END, p)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load projects: {e}")

    def save_projects(self):
        try:
            with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.projects, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save projects: {e}")

    def on_close(self):
        self.save_projects()
        self.master.destroy()

    def add_project(self):
        path = filedialog.askdirectory(title="Select Project Folder")
        if path:
            if path not in self.projects:
                self.projects.append(path)
                self.project_list.insert(tk.END, path)
                # automatically select the newly added project
                self.project_list.selection_clear(0, tk.END)
                self.project_list.selection_set(tk.END)
                self.project_list.activate(tk.END)
                self.on_project_select(None)
            else:
                messagebox.showinfo("Info", "Project already exists.")

    def remove_project(self):
        idx = self.project_list.curselection()
        if idx:
            index = idx[0]
            self.projects.pop(index)
            self.project_list.delete(index)
            self.file_list.delete(0, tk.END)
            self.preview.configure(state="normal")
            self.preview.delete(1.0, tk.END)
            self.preview.configure(state="disabled")
        else:
            messagebox.showinfo("Info", "No project selected.")

    def open_folder(self):
        idx = self.project_list.curselection()
        if idx:
            path = self.projects[idx[0]]
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {e}")
        else:
            messagebox.showinfo("Info", "No project selected.")

    def on_project_select(self, event):
        idx = self.project_list.curselection()
        self.file_list.delete(0, tk.END)
        self.preview.configure(state="normal")
        self.preview.delete(1.0, tk.END)
        self.preview.configure(state="disabled")
        if idx:
            path = self.projects[idx[0]]
            self.selected_project = path
            try:
                files = [f for f in os.listdir(path) if f.endswith('.py')]
                for f in files:
                    self.file_list.insert(tk.END, f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to list files: {e}")

    def on_file_select(self, event):
        idx = self.file_list.curselection()
        if idx and self.selected_project:
            filename = self.file_list.get(idx[0])
            filepath = os.path.join(self.selected_project, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.preview.configure(state="normal")
                self.preview.delete(1.0, tk.END)
                self.preview.insert(tk.END, content)
                self.preview.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def new_file(self):
        if not self.selected_project:
            messagebox.showinfo("Info", "Please select a project first.")
            return
        top = tk.Toplevel(self.master)
        top.title("Create New File")
        tk.Label(top, text="File Name:").pack(padx=5, pady=5)
        name_entry = tk.Entry(top)
        name_entry.pack(padx=5, pady=5)
        text = scrolledtext.ScrolledText(top, width=60, height=20)
        text.pack(padx=5, pady=5)
        def save_file():
            name = name_entry.get().strip()
            if not name.endswith('.py'):
                name += '.py'
            if name:
                path = os.path.join(self.selected_project, name)
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(text.get(1.0, tk.END))
                    self.file_list.insert(tk.END, name)
                    self.file_list.selection_clear(0, tk.END)
                    self.file_list.selection_set(tk.END)
                    self.file_list.activate(tk.END)
                    self.on_file_select(None)
                    top.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        tk.Button(top, text="Save", command=save_file).pack(pady=5)

    def download_file(self):
        idx = self.file_list.curselection()
        if idx and self.selected_project:
            filename = self.file_list.get(idx[0])
            src_path = os.path.join(self.selected_project, filename)
        dest_path = filedialog.asksaveasfilename(
            initialfile=filename,
            initialdir=self.selected_project
        )
        if dest_path:
            try:
                with open(src_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download file: {e}")
        else:
            messagebox.showinfo("Info", "No file selected.")

    def add_file(self):
        if not self.selected_project:
            messagebox.showinfo("Info", "Please select a project first.")
            return
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py")],
            initialdir=self.selected_project
        )
        if file_path:
            dest = os.path.join(self.selected_project, os.path.basename(file_path))
            if os.path.exists(dest):
                messagebox.showinfo("Info", "File already exists in project.")
                return
            try:
                shutil.copy(file_path, dest)
                self.file_list.insert(tk.END, os.path.basename(file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add file: {e}")

    def run_file(self):
        idx = self.file_list.curselection()
        if idx and self.selected_project:
            filename = self.file_list.get(idx[0])
            filepath = os.path.join(self.selected_project, filename)
            try:
                result = subprocess.run(
                    [sys.executable, filepath],
                    capture_output=True,
                    text=True,
                    cwd=self.selected_project,
                )
                output_window = tk.Toplevel(self.master)
                output_window.title(f"Output: {filename}")
                out_text = scrolledtext.ScrolledText(output_window, width=80, height=20)
                out_text.pack(padx=5, pady=5)
                out_text.insert(tk.END, result.stdout + '\n' + result.stderr)
                out_text.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run file: {e}")
        else:
            messagebox.showinfo("Info", "No file selected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagerApp(root)
    root.mainloop()
