import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


class Processor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None

    def load_image(self, path):
        self.original_image = cv2.imread(path)
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            return True
        return False

    def process(self, scale_percent, sharpness_value):
        if self.original_image is None:
            return None, (0, 0)

        width = int(self.original_image.shape[1] * scale_percent / 100)
        height = int(self.original_image.shape[0] * scale_percent / 100)
        new_dimensions = (width, height)

        resized = cv2.resize(self.original_image, new_dimensions, interpolation=cv2.INTER_LINEAR)

        if sharpness_value > 0:
            kernel_size = int(sharpness_value // 10) * 2 + 3 
            blurred = cv2.GaussianBlur(resized, (kernel_size, kernel_size), 0)
            
            sharpened = cv2.addWeighted(resized, 1.5, blurred, -0.5, 0)
            self.processed_image = np.clip(sharpened, 0, 255).astype(np.uint8)
        else:
            self.processed_image = resized.copy()

        return self.processed_image, new_dimensions

    def save_image(self, path):
        if self.processed_image is not None:
            return cv2.imwrite(path, self.processed_image)
        return False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenCV + Tkinter: Resize & Sharpness")
        self.geometry("900x650")

        self.processor = Processor()
        self.image_path = None

        self._create_widgets()

    def _create_widgets(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(control_frame, text="Открыть фото", command=self._open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Применить", command=self._apply_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить", command=self._save_image).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Масштаб (%):").pack(side=tk.LEFT, padx=(15, 2))
        self.spin_scale = ttk.Spinbox(control_frame, from_=20, to=150, width=5)
        self.spin_scale.set(100)
        self.spin_scale.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Резкость:").pack(side=tk.LEFT, padx=(15, 2))
        self.slider_sharp = ttk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.slider_sharp.set(0)
        self.slider_sharp.pack(side=tk.LEFT, padx=5)

        self.lbl_dims = ttk.Label(control_frame, text="Размер: 0 x 0 px", font=("Arial", 10, "bold"))
        self.lbl_dims.pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_orig = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_orig, text="Оригинал")
        self.lbl_orig_img = ttk.Label(self.tab_orig)
        self.lbl_orig_img.pack(fill=tk.BOTH, expand=True)

        self.tab_proc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_proc, text="Обработка")
        self.lbl_proc_img = ttk.Label(self.tab_proc)
        self.lbl_proc_img.pack(fill=tk.BOTH, expand=True)

    def _open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            if self.processor.load_image(file_path):
                self.image_path = file_path
                self._display_image(self.processor.original_image, self.lbl_orig_img)
                self.lbl_proc_img.config(image='')
                h, w, _ = self.processor.original_image.shape
                self.lbl_dims.config(text=f"Размер: {w} x {h} px")
                self.notebook.select(0) 
            else:
                messagebox.onerror("Ошибка", "Не удалось загрузить изображение.")

    def _apply_processing(self):
        if self.processor.original_image is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return

        try:
            scale = float(self.spin_scale.get())
            sharp = float(self.slider_sharp.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные параметры ввода.")
            return

        img_out, dims = self.processor.process(scale, sharp)

        if img_out is not None:
            self.lbl_dims.config(text=f"Размер: {dims[0]} x {dims[1]} px")
            self._display_image(img_out, self.lbl_proc_img)
            self.notebook.select(1) 

    def _save_image(self):
        if self.processor.processed_image is None:
            messagebox.showwarning("Внимание", " Нет обработанного изображения для сохранения!")
            return

        ext = os.path.splitext(self.image_path)[1] if self.image_path else ".jpg"
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All Files", "*.*")]
        )
        
        if save_path:
            if self.processor.save_image(save_path):
                messagebox.showinfo("Успех", "Изображение успешно сохранено!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изображение.")

    def _display_image(self, cv_img, label_widget):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)

        max_size = (850, 500)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)

        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        label_widget.image = tk_img 
        label_widget.config(image=tk_img, anchor=tk.CENTER)


if __name__ == "__main__":
    app = App()
    app.mainloop()
