import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, Menu, Frame, Label
import os
import time
import shutil

class FileManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Simulador de Gestor de Archivos')
        self.geometry('800x500')

        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.history = []
        self.sort_column = "name"
        self.reverse_sort = False
        self.view_mode = 'details'  # 'details' or 'grid'

        self.setup_toolbar()
        self.setup_views()

        self.refresh()

    def setup_toolbar(self):
        self.toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.view_button = ttk.Button(self.toolbar, text='Cambiar Vista', command=self.toggle_view)
        self.view_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.back_button = ttk.Button(self.toolbar, text='Atrás', command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.refresh_button = ttk.Button(self.toolbar, text='Actualizar', command=self.refresh)
        self.refresh_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.create_folder_button = ttk.Button(self.toolbar, text='Crear Carpeta', command=self.create_folder)
        self.create_folder_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.rename_button = ttk.Button(self.toolbar, text='Renombrar', command=self.rename)
        self.rename_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.delete_button = ttk.Button(self.toolbar, text='Eliminar', command=self.delete)
        self.delete_button.pack(side=tk.LEFT, padx=2, pady=2)

    def setup_views(self):
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.container, columns=('Size', 'Modified'))
        self.tree.heading('#0', text='Nombre', command=lambda: self.treeview_sort_column('name'))
        self.tree.heading('Size', text='Tamaño', command=lambda: self.treeview_sort_column('size'))
        self.tree.heading('Modified', text='Última modificación', command=lambda: self.treeview_sort_column('modified'))
        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('Size', stretch=tk.YES)
        self.tree.column('Modified', stretch=tk.YES)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.grid_frame = Frame(self.container)
        self.grid_labels = []

    def toggle_view(self):
        if self.view_mode == 'details':
            self.view_mode = 'grid'
            self.tree.pack_forget()
            self.display_grid_view()
        else:
            self.view_mode = 'details'
            self.grid_frame.pack_forget()
            self.tree.pack(fill=tk.BOTH, expand=True)
        self.refresh()

    def display_grid_view(self):
        for label in self.grid_labels:
            label.destroy()
        self.grid_labels.clear()

        row = 0
        column = 0
        for entry in os.scandir(self.current_path):
            frame = Frame(self.grid_frame, borderwidth=1, relief=tk.RAISED)
            label = Label(frame, text=entry.name, padx=10, pady=10)
            label.pack()
            frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)
            self.grid_labels.append(frame)
            column += 1
            if column > 3:
                column = 0
                row += 1
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        if self.view_mode == 'details':
            self.load_directory_contents(self.current_path)
        elif self.view_mode == 'grid':
            self.display_grid_view()

    def load_directory_contents(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in os.scandir(path):
            size = '<DIR>' if entry.is_dir() else f'{os.path.getsize(entry.path)} bytes'
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(entry.path)))
            self.tree.insert('', 'end', iid=entry.path, text=entry.name, values=(size, mod_time))

    def show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            menu = Menu(self, tearoff=0)
            menu.add_command(label="Renombrar", command=self.rename)
            menu.add_command(label="Eliminar", command=self.delete)
            menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            path = self.tree.item(item, 'text')
            full_path = os.path.join(self.current_path, path)
            if os.path.isdir(full_path):
                self.history.append(self.current_path)
                self.current_path = full_path
                self.refresh()

    def go_back(self):
        if self.history:
            self.current_path = self.history.pop()
            self.refresh()

    def create_folder(self):
        new_folder_name = simpledialog.askstring("Crear Carpeta", "Nombre de la nueva carpeta:")
        if new_folder_name:
            new_folder_path = os.path.join(self.current_path, new_folder_name)
            try:
                os.makedirs(new_folder_path)
                self.refresh()
            except FileExistsError:
                messagebox.showerror("Error", "Una carpeta con ese nombre ya existe.")

    def rename(self):
        item = self.tree.selection()[0]
        old_name = self.tree.item(item, 'text')
        new_name = simpledialog.askstring("Renombrar", "Nuevo nombre:", initialvalue=old_name)
        if new_name and new_name != old_name:
            os.rename(os.path.join(self.current_path, old_name), os.path.join(self.current_path, new_name))
            self.refresh()

    def delete(self):
        item = self.tree.selection()[0]
        name = self.tree.item(item, 'text')
        response = messagebox.askyesno("Eliminar", "¿Estás seguro de querer eliminar esto?")
        if response:
            path = os.path.join(self.current_path, name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except PermissionError as e:
                messagebox.showerror("Error", f"Permiso denegado: {e}")
            self.refresh()

if __name__ == '__main__':
    app = FileManager()
    app.mainloop()
