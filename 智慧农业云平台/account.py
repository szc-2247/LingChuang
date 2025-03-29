import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import subprocess

# 全局变量，用于存储 after 任务的 ID
after_id = None

# 检查文件是否存在，不存在则创建
def check_file():
    if not os.path.exists('accounts.txt'):
        with open('accounts.txt', 'w') as file:
            pass

# 注册函数
def register():
    username = entry_register_username.get()
    password = entry_register_password.get()
    confirm_password = entry_register_confirm_password.get()

    if password != confirm_password:
        messagebox.showerror("错误", "两次输入的密码不一致，请重新输入！")
        return

    with open('accounts.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if ',' in line:
                stored_username, _ = line.split(',')
                if stored_username == username:
                    messagebox.showerror("错误", "该账号已存在，请选择其他账号！")
                    return

    with open('accounts.txt', 'a') as file:
        file.write(f"{username},{password}\n")
    messagebox.showinfo("成功", "注册成功！请登录。")
    register_window.destroy()

# 登录函数
def login():
    username = entry_login_username.get()
    password = entry_login_password.get()

    with open('accounts.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if ',' in line:
                stored_username, stored_password = line.split(',')
                if stored_username == username and stored_password == password:
                    messagebox.showinfo("成功", "登录成功！")
                    root.destroy()
                    try:
                        # 取消所有 after 任务
                        if after_id:
                            root.after_cancel(after_id)
                        # 这里模拟跳转到 main.py
                        subprocess.call(['python', 'main.py'])
                    except KeyboardInterrupt:
                        print("程序被手动中断")
                    return

    messagebox.showerror("错误", "账号不存在或密码错误")

# 显示/隐藏密码函数
def toggle_password_visibility():
    if show_password.get():
        entry_login_password.config(show="")
        button_toggle_password.config(text="隐藏")
    else:
        entry_login_password.config(show="*")
        button_toggle_password.config(text="可见")

# 创建主窗口
root = tk.Tk()
root.title("智农兴商———智慧农业乡村振兴系统")
root.geometry("500x400")

# 检查文件
check_file()

# 标题


# 显示 logo（假设 logo.png 在同一目录下）
try:
    logo = Image.open("logo.png")
    logo = logo.resize((230, 200), Image.LANCZOS)
    photo = ImageTk.PhotoImage(logo)
    label_logo = tk.Label(root, image=photo)
    label_logo.image = photo
    label_logo.pack(pady=10)
except ImportError:
    print("请安装 Pillow 库以显示图片。")
except FileNotFoundError:
    print("未找到 logo.png 文件。")

# 登录部分
frame_login = tk.Frame(root)
frame_login.pack(pady=20)

label_login_username = tk.Label(frame_login, text="账号:")
label_login_username.grid(row=0, column=0)
entry_login_username = tk.Entry(frame_login)
entry_login_username.grid(row=0, column=1)

label_login_password = tk.Label(frame_login, text="密码:")
label_login_password.grid(row=1, column=0)
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.grid(row=1, column=1)

show_password = tk.BooleanVar()
show_password.set(False)
button_toggle_password = tk.Button(frame_login, text="可见",
                                   command=lambda: [show_password.set(not show_password.get()), toggle_password_visibility()])
button_toggle_password.grid(row=1, column=2)

# 注册和登录按钮
button_register = tk.Button(root, text="注册", command=lambda: open_register_window())
button_register.pack(side=tk.LEFT, padx=20)

button_login = tk.Button(root, text="登录", command=login)
button_login.pack(side=tk.RIGHT, padx=20)

# 打开注册窗口
def open_register_window():
    global register_window, entry_register_username, entry_register_password, entry_register_confirm_password
    register_window = tk.Toplevel(root)
    register_window.title("注册")

    label_register_username = tk.Label(register_window, text="账号:")
    label_register_username.pack()
    entry_register_username = tk.Entry(register_window)
    entry_register_username.pack()

    label_register_password = tk.Label(register_window, text="密码:")
    label_register_password.pack()
    entry_register_password = tk.Entry(register_window, show="*")
    entry_register_password.pack()

    label_register_confirm_password = tk.Label(register_window, text="重复密码:")
    label_register_confirm_password.pack()
    entry_register_confirm_password = tk.Entry(register_window, show="*")
    entry_register_confirm_password.pack()

    button_register_submit = tk.Button(register_window, text="注册", command=register)
    button_register_submit.pack(pady=20)

root.mainloop()