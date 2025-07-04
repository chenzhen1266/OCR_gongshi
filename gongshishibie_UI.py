# UI界面

from PIL import ImageGrab, ImageTk
import pyperclip
from pix2tex.cli import LatexOCR
import latex2mathml.converter
from xml.sax.saxutils import escape
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class FormulaConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("公式转换工具")

        # 初始化模型（只加载一次）
        self.model = LatexOCR()

        # 创建界面布局
        self.create_widgets()
        self.update_content()  # 初始加载

    def create_widgets(self):
        # 图片显示区域
        self.img_frame = ttk.Frame(self.root)
        self.img_frame.grid(row=0, column=0, padx=10, pady=10)
        self.img_label = ttk.Label(self.img_frame, text="剪贴板图片预览")
        self.img_label.pack()

        # 结果展示区域
        result_frame = ttk.Frame(self.root)
        result_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # LaTeX 结果显示
        ttk.Label(result_frame, text="LaTeX 格式：").pack(anchor="w")
        self.latex_text = scrolledtext.ScrolledText(result_frame, width=50, height=10)
        self.latex_text.pack()

        # MathML 结果显示
        ttk.Label(result_frame, text="MathML 格式：").pack(anchor="w", pady=(10, 0))
        self.mathml_text = scrolledtext.ScrolledText(result_frame, width=50, height=15)
        self.mathml_text.pack()

        # 控制按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.refresh_btn = ttk.Button(btn_frame, text="重新识别", command=self.update_content)
        self.refresh_btn.pack(side="left", padx=5)

        self.copy_latex_btn = ttk.Button(btn_frame, text="复制LaTeX", command=self.copy_latex)
        self.copy_latex_btn.pack(side="left", padx=5)

        self.copy_mathml_btn = ttk.Button(btn_frame, text="复制MathML", command=self.copy_mathml)
        self.copy_mathml_btn.pack(side="left", padx=5)

    def update_content(self):
        try:
            image = ImageGrab.grabclipboard()
            if not image:
                messagebox.showwarning("警告", "剪贴板中无图片")
                return

            # 更新图片显示
            image.thumbnail((300, 300))  # 限制预览尺寸
            tk_image = ImageTk.PhotoImage(image)
            self.img_label.configure(image=tk_image)
            self.img_label.image = tk_image  # 保持引用

            # 识别公式
            latex_code = self.model(image)

            # 转换 MathML
            mathml_core = latex2mathml.converter.convert(latex_code)
            escaped_latex = escape(latex_code)
            mathml_output = f'<math xmlns="http://www.w3.org/1998/Math/MathML">\n' \
                            f'  <semantics>\n' \
                            f'    {mathml_core}\n' \
                            f'    <annotation encoding="application/x-tex">{escaped_latex}</annotation>\n' \
                            f'  </semantics>\n' \
                            f'</math>'

            # 更新文本显示
            self.latex_text.delete(1.0, tk.END)
            self.latex_text.insert(tk.END, latex_code)

            self.mathml_text.delete(1.0, tk.END)
            self.mathml_text.insert(tk.END, mathml_output)

        except Exception as e:
            messagebox.showerror("错误", f"处理时发生错误：{str(e)}")

    def copy_latex(self):
        latex = self.latex_text.get(1.0, tk.END)
        pyperclip.copy(latex)
        messagebox.showinfo("成功", "LaTeX 已复制到剪贴板")

    def copy_mathml(self):
        mathml = self.mathml_text.get(1.0, tk.END)
        pyperclip.copy(mathml)
        messagebox.showinfo("成功", "MathML 已复制到剪贴板")


if __name__ == "__main__":
    root = tk.Tk()
    app = FormulaConverterApp(root)
    root.mainloop()



