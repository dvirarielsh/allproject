# Python Project Manager

This Tkinter application lets you manage multiple Python project folders. After adding a project the files in that folder are shown automatically. You can:

This simple Tkinter application lets you manage multiple Python project folders. You can:

- Add or remove project directories.
- View `.py` files for each project and preview their contents.
- Create new Python files within a project.
- Download a copy of any file to another location.
- Run a selected file and see its output.
- Open the project folder in Windows Explorer.

The list of projects is stored in `projects.json` and loaded on startup.

Run the program with:

```bash
python main.py
```

The GUI requires a graphical environment such as Windows 10. Running on a headless server will cause Tkinter to fail.


