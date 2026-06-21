import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")


class ImageCopyViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Copy Viewer")

        self.src_dir = ""
        self.dst_dir = ""
        self.image_paths = []
        self.idx = 0
        self.tk_img = None

        self.label_info = tk.Label(root, text="A 폴더와 B 폴더를 선택하세요")
        self.label_info.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        jump_frame = tk.Frame(root)
        jump_frame.pack(pady=5)

        tk.Label(jump_frame, text="이동:").pack(side=tk.LEFT)

        self.jump_entry = tk.Entry(jump_frame, width=10)
        self.jump_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            jump_frame,
            text="Go",
            command=self.jump_to_image
        ).pack(side=tk.LEFT)

        self.jump_entry.bind("<Return>", lambda e: self.jump_to_image())

        tk.Button(btn_frame, text="A 폴더 선택", command=self.select_src).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="B 폴더 선택", command=self.select_dst).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="이전", command=self.prev_image).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="다음", command=self.next_image).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="복사", command=self.copy_image).grid(row=0, column=4, padx=5)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)
        
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<space>", lambda e: self.copy_image())

    def select_src(self):
        self.src_dir = filedialog.askdirectory(title="A 디렉토리 선택")
        if not self.src_dir:
            return

        self.image_paths = [
            os.path.join(self.src_dir, f)
            for f in os.listdir(self.src_dir)
            if f.lower().endswith(IMAGE_EXTS)
        ]

        self.image_paths.sort()
        self.idx = 0

        if not self.image_paths:
            messagebox.showwarning("경고", "선택한 폴더에 이미지가 없습니다.")
            return

        self.show_image()

    def select_dst(self):
        self.dst_dir = filedialog.askdirectory(title="B 디렉토리 선택")
        if self.dst_dir:
            messagebox.showinfo("완료", f"B 폴더 선택됨:\n{self.dst_dir}")

    def show_image(self):
        if not self.image_paths:
            return

        path = self.image_paths[self.idx]

        img = Image.open(path).convert("RGB")
        img.thumbnail((1000, 550))

        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

        filename = os.path.basename(path)
        self.label_info.config(
            text=f"{self.idx + 1} / {len(self.image_paths)} | {filename}"
        )

    def next_image(self):
        if not self.image_paths:
            return
        self.idx = (self.idx + 1) % len(self.image_paths)
        self.show_image()

    def prev_image(self):
        if not self.image_paths:
            return
        self.idx = (self.idx - 1) % len(self.image_paths)
        self.show_image()

    def copy_image(self):
        if not self.image_paths:
            return

        if not self.dst_dir:
            messagebox.showwarning("경고", "먼저 B 디렉토리를 선택하세요.")
            return

        src_path = self.image_paths[self.idx]
        filename = os.path.basename(src_path)
        dst_path = os.path.join(self.dst_dir, filename)

        shutil.copy2(src_path, dst_path)

        messagebox.showinfo("복사 완료", f"{filename}\nB 폴더로 복사했습니다.")

    def jump_to_image(self):
        if not self.image_paths:
            return

        try:
            target = int(self.jump_entry.get())

            if 1 <= target <= len(self.image_paths):
                self.idx = target - 1
                self.show_image()
            else:
                messagebox.showwarning(
                    "범위 오류",
                    f"1 ~ {len(self.image_paths)} 사이 값을 입력하세요."
                )

        except ValueError:
            messagebox.showwarning(
                "입력 오류",
                "숫자를 입력하세요."
            )

if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = ImageCopyViewer(root)
    root.mainloop()