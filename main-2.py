import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Menu, Frame, Label, Toplevel
import os
import time
import shutil
from threading import Thread

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
        
        self.clipboard_action = None
        self.clipboard_path = None

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

        self.tree_frame = Frame(self.container)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, columns=('Size', 'Modified'), yscrollcommand=self.tree_scroll_y.set)
        self.tree.heading('#0', text='Nombre', command=lambda: self.treeview_sort_column('name'))
        self.tree.heading('Size', text='Tamaño', command=lambda: self.treeview_sort_column('size'))
        self.tree.heading('Modified', text='Última modificación', command=lambda: self.treeview_sort_column('modified'))
        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('Size', stretch=tk.YES)
        self.tree.column('Modified', stretch=tk.YES)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll_y.config(command=self.tree.yview)

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
        items = []
        for entry in os.scandir(path):
            size = '<DIR>' if entry.is_dir() else f'{os.path.getsize(entry.path)} bytes'
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(entry.path)))
            items.append((entry.name, size, mod_time, entry.path))
        
        sorted_items = self.bubble_sort(items, self.sort_column, self.reverse_sort)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in sorted_items:
            self.tree.insert('', 'end', iid=entry[3], text=entry[0], values=(entry[1], entry[2]))

    def bubble_sort(self, items, column, reverse):
        n = len(items)
        for i in range(n):
            for j in range(0, n-i-1):
                if column == 'name':
                    a, b = items[j][0], items[j+1][0]
                elif column == 'size':
                    a, b = self.convert_size(items[j][1]), self.convert_size(items[j+1][1])
                elif column == 'modified':
                    a, b = items[j][2], items[j+1][2]
                if (a > b and not reverse) or (a < b and reverse):
                    items[j], items[j+1] = items[j+1], items[j]
        return items

    def convert_size(self, size_str):
        if size_str == '<DIR>':
            return 0
        return int(size_str.split()[0])

    def treeview_sort_column(self, col):
        if self.sort_column == col:
            self.reverse_sort = not self.reverse_sort
        else:
            self.sort_column = col
            self.reverse_sort = False
        self.refresh()

    def show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        menu = Menu(self, tearoff=0)
        if iid:
            self.tree.selection_set(iid)
            menu.add_command(label="Renombrar", command=self.rename)
            menu.add_command(label="Eliminar", command=self.delete)
            menu.add_command(label="Copiar", command=self.copy)
            menu.add_command(label="Cortar", command=self.cut)
        else:
            menu.add_command(label="Pegar", command=self.paste, state=tk.NORMAL if self.clipboard_path else tk.DISABLED)
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
            self.show_progress_window()
            Thread(target=self.delayed_rename, args=(old_name, new_name)).start()

    def delayed_rename(self, old_name, new_name):
        time.sleep(2)  # Añadir un retraso de 2 segundos
        try:
            os.rename(os.path.join(self.current_path, old_name), os.path.join(self.current_path, new_name))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Error al renombrar: {e}")
        finally:
            self.progress_window.destroy()

    def delete(self):
        item = self.tree.selection()[0]
        name = self.tree.item(item, 'text')
        response = messagebox.askyesno("Eliminar", "¿Estás seguro de querer eliminar esto?")
        if response:
            self.show_progress_window()
            Thread(target=self.delayed_delete, args=(name,)).start()

    def delayed_delete(self, name):
        time.sleep(2)  # Añadir un retraso de 2 segundos
        try:
            path = os.path.join(self.current_path, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")
        finally:
            self.progress_window.destroy()

    def copy(self):
        item = self.tree.selection()[0]
        self.clipboard_path = os.path.join(self.current_path, self.tree.item(item, 'text'))
        self.clipboard_action = 'copy'

    def cut(self):
        item = self.tree.selection()[0]
        self.clipboard_path = os.path.join(self.current_path, self.tree.item(item, 'text'))
        self.clipboard_action = 'cut'

    def paste(self):
        if not self.clipboard_path:
            return
        self.show_progress_window()
        Thread(target=self.delayed_paste).start()

    def delayed_paste(self):
        time.sleep(2)  # Añadir un retraso de 2 segundos
        src_path = self.clipboard_path
        dest_path = os.path.join(self.current_path, os.path.basename(src_path))
        try:
            if self.clipboard_action == 'copy':
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
            elif self.clipboard_action == 'cut':
                shutil.move(src_path, dest_path)
                self.clipboard_path = None
                self.clipboard_action = None
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Error al pegar el archivo o carpeta: {e}")
        finally:
            self.progress_window.destroy()

    def show_progress_window(self):
        self.progress_window = Toplevel(self)
        self.progress_window.title("Procesando")
        self.progress_window.geometry("300x100")
        Label(self.progress_window, text="Por favor espera...").pack(pady=20)
        self.progress_bar = ttk.Progressbar(self.progress_window, mode='indeterminate')
        self.progress_bar.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.progress_bar.start()

if __name__ == '__main__':
    app = FileManager()
    app.mainloop()
