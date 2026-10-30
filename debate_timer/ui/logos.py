"""Optional Pillow logo selection and rendering."""
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class LogoMixin:
    def choose_logos(self):
        paths = filedialog.askopenfilenames(
            title="Elegir logos (se pueden elegir varios)",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if paths:
            for path in paths:
                if path not in self.logo_paths:
                    self.logo_paths.append(path)
            self.load_logos()

    def clear_logos(self):
        self.logo_paths = []
        self.load_logos()

    def load_logos(self):
        for child in self.display_logo_frame.winfo_children():
            child.destroy()
        self.logo_imgs = []

        if not self.logo_paths:
            return

        if not PIL_AVAILABLE:
            messagebox.showwarning("Logos requieren Pillow", "Para usar logos instala Pillow con: pip install pillow")
            return

        thumb_size = (190, 105) if len(self.logo_paths) == 1 else (140, 80)

        for path in self.logo_paths:
            try:
                editor = getattr(self, "size_editor", None)
                custom_size = editor.values.get("logo:" + path, {}).get("logo_size") if editor else None
                with Image.open(path) as source:
                    img = source.copy()
                if custom_size:
                    factor = custom_size / max(img.size)
                    img = img.resize((max(1, round(img.width * factor)), max(1, round(img.height * factor))),
                                     Image.Resampling.LANCZOS)
                else:
                    img.thumbnail(thumb_size)
                photo = ImageTk.PhotoImage(img)
                self.logo_imgs.append(photo)
                label = tk.Label(self.display_logo_frame, image=photo, bg=self.DISPLAY_BG)
                label.size_key = "logo:" + path
                label.pack(side="left", padx=10)
            except Exception as e:
                messagebox.showerror("Error con un logo", f"{path}\n{e}")
        if hasattr(self, "size_editor"):
            self.size_editor.register()
            for child in self.display_logo_frame.winfo_children():
                self.size_editor.apply(child)
