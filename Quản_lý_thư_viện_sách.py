import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import re
from datetime import datetime
from tkcalendar import DateEntry
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Hàm tạo màu pastel ngẫu nhiên
def generate_pastel_color():
    def r(): return random.randint(200, 255)
    return f'#{r():02x}{r():02x}{r():02x}'
# Kết nối đến SQLite
conn = sqlite3.connect('library.db')
cur = conn.cursor()
# Tạo bảng nếu chưa tồn tại
cur.execute('''CREATE TABLE IF NOT EXISTS books (
    title TEXT,
    author TEXT,
    year TEXT,
    isbn TEXT,
    quantity INTEGER,
    borrowed_by TEXT DEFAULT NULL,
    borrow_date TEXT DEFAULT NULL,
    return_date TEXT DEFAULT NULL,
    status TEXT DEFAULT NULL,
    UNIQUE(title, author, year, isbn)
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    name TEXT,
    borrowed_books INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
)''')

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng Dụng Quản Lý Thư Viện")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')

        self.current_user = None

        self.main_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.show_login_register_screen()
    # Hiển thị màn hình đăng nhập/đăng ký
    def show_login_register_screen(self):
        self.clear_frame()

        title_label = tk.Label(self.main_frame, text="Ứng Dụng Quản Lý Thư Viện", font=("Helvetica", 28, "bold"), bg="#d3d3d3", fg="#2c3e50")
        title_label.pack(pady=40)

        login_btn = ttk.Button(self.main_frame, text="Đăng Nhập", command=self.show_login_screen, style="TButton")
        register_btn = ttk.Button(self.main_frame, text="Đăng Ký", command=self.show_register_screen, style="TButton")

        login_btn.pack(pady=20, ipadx=20, ipady=10)
        register_btn.pack(pady=20, ipadx=20, ipady=10)
    # Hiển thị màn hình đăng nhập
    def show_login_screen(self):
        self.clear_frame()

        title_label = tk.Label(self.main_frame, text="Đăng Nhập", font=("Helvetica", 28, "bold"), bg="#d3d3d3", fg="#2c3e50")
        title_label.pack(pady=20)

        tk.Label(self.main_frame, text="Tên Đăng Nhập:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.username_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14))
        self.username_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Mật Khẩu:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.password_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Loại Tài Khoản:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.account_type_combobox = ttk.Combobox(self.main_frame, values=["admin", "user"], font=("Helvetica", 14))
        self.account_type_combobox.pack(pady=5)
        self.account_type_combobox.current(1)  # Mặc định là "user"

        login_btn = ttk.Button(self.main_frame, text="Đăng Nhập", command=self.login, style="TButton")
        login_btn.pack(pady=20, ipadx=20, ipady=10)

        back_btn = ttk.Button(self.main_frame, text="Quay Lại", command=self.show_login_register_screen, style="TButton")
        back_btn.pack(pady=20, ipadx=20, ipady=10)
    # Hiển thị màn hình đăng ký
    def show_register_screen(self):
        self.clear_frame()

        title_label = tk.Label(self.main_frame, text="Đăng Ký", font=("Helvetica", 28, "bold"), bg="#d3d3d3", fg="#2c3e50")
        title_label.pack(pady=20)

        tk.Label(self.main_frame, text="Tên Đăng Nhập:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14))
        self.reg_username_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Mật Khẩu:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), show="*")
        self.reg_password_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Xác Nhận Mật Khẩu:", font=("Helvetica", 14), bg="#f5f5f5", fg="#2c3e50").pack(pady=5)
        self.reg_confirm_password_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), show="*")
        self.reg_confirm_password_entry.pack(pady=5)

        register_btn = ttk.Button(self.main_frame, text="Đăng Ký", command=self.register, style="TButton")
        register_btn.pack(pady=20, ipadx=20, ipady=10)

        back_btn = ttk.Button(self.main_frame, text="Quay Lại", command=self.show_login_register_screen, style="TButton")
        back_btn.pack(pady=20, ipadx=20, ipady=10)
    # Kiểm tra mật khẩu
    def validate_password(self, password):
        if 8 <= len(password) <= 16 and re.search(r"[a-zA-Z]", password) and re.search(r"[0-9]", password):
            return True
        return False
    # Xử lý đăng nhập
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        account_type = self.account_type_combobox.get()

        if username == "admin" and password == "admin" and account_type == "admin":
            self.current_user = ("admin", "admin", "admin")
            self.show_admin_screen()
            return

        cur.execute("SELECT * FROM users WHERE username=? AND password=? AND is_active=1", (username, password))
        user = cur.fetchone()

        if user and account_type == "user":
            self.current_user = user
            self.show_user_screen()
        elif user and account_type == "admin":
            self.current_user = user
            self.show_admin_screen()
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập, mật khẩu hoặc loại tài khoản không hợp lệ. Vui lòng thử lại.")
    # Xử lý đăng ký
    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Lỗi", "Tất cả các trường là bắt buộc")
            return

        if not self.validate_password(password):
            messagebox.showerror("Lỗi", "Mật khẩu phải có độ dài từ 8 đến 16 ký tự và phải có cả chữ và số")
            return

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật Khẩu không khớp")
            return

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Thành công", "Đăng ký thành công")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
    # Hiển thị giao diện người dùng
    def show_user_screen(self):
        def view_books():
            tree.delete(*tree.get_children())
            cur.execute("SELECT * FROM books")
            for idx, row in enumerate(cur.fetchall()):
                author = row[1]
                if author not in author_colors:
                    author_colors[author] = generate_pastel_color()
                tree.insert("", tk.END, values=(idx + 1, *row), tags=(author,))
                tree.tag_configure(author, background=author_colors[author])

        def search_books():
            tree.delete(*tree.get_children())
            query = "SELECT * FROM books WHERE title=? OR author=? OR year=? OR isbn=?"
            params = (entry_title.get(), entry_author.get(), entry_year.get(), entry_isbn.get())
            results = list(cur.execute(query, params))
            if results:
                for idx, row in enumerate(results):
                    tree.insert("", tk.END, values=(idx + 1, *row))
            else:
                messagebox.showinfo("Thông Báo", "Không tìm thấy kết quả phù hợp.")
            self.clear_entries()  # Clear entries after search

        self.clear_frame()

        frame_book_info = tk.Frame(self.main_frame, bg='#d3d3d3')
        frame_book_info.pack(pady=20, padx=20, fill=tk.BOTH)
        labels = ["Tên Sách:", "Tác Giả:", "Năm:", "Mã Sách:"]
        for idx, text in enumerate(labels):
            tk.Label(frame_book_info, text=text, font=("Helvetica", 12), bg="#d3d3d3").grid(row=idx, column=0, padx=10, pady=10, sticky=tk.E)
            tk.Entry(frame_book_info, font=("Helvetica", 12)).grid(row=idx, column=1, padx=10, pady=10)

        global entry_title, entry_author, entry_year, entry_isbn
        entry_title, entry_author, entry_year, entry_isbn = frame_book_info.winfo_children()[1::2]

        frame_controls = tk.Frame(self.main_frame, bg='#d3d3d3', bd=10)
        frame_controls.pack(pady=10, padx=20, fill=tk.BOTH)
        buttons = [
            ("Xem", view_books),
            ("Tìm Kiếm", search_books)
        ]

        for idx, (text, command) in enumerate(buttons):
            tk.Button(frame_controls, text=text, width=20, command=command, bg="#F5A9BC", fg="white", font=("Helvetica", 12)).grid(row=0, column=idx, padx=10, pady=10)
        # Thêm nút đăng xuất
        logout_btn = tk.Button(frame_controls, text="Đăng Xuất", width=20, command=self.logout, bg="#FF6347", fg="white", font=("Helvetica", 12, "bold"))
        logout_btn.grid(row=0, column=len(buttons), padx=10, pady=10)

        tk.Label(self.main_frame, text=f"Chào Sinh Viên: {self.current_user[0]}", font=("Helvetica", 16, "bold"), fg="#6A5ACD", bg='#d3d3d3').place(x=800, y=10)

        frame_display = tk.Frame(self.main_frame, bg="white", bd=5, relief="raised")
        frame_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        global tree
        tree = ttk.Treeview(frame_display, columns=['STT', 'Tên Sách ', 'Tác Giả ', 'Năm ', 'Mã Sách ', 'Số Lượng '], show="headings")
        tree.column('STT', width=50, anchor='center')
        tree.column('Tên Sách ', width=170)
        tree.column('Tác Giả ', width=170)
        tree.column('Năm ', width=100, anchor='center')
        tree.column('Mã Sách ', width=100, anchor='center')
        tree.column('Số Lượng ', width=100, anchor='center')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)
    # Hiển thị giao diện quản trị viên
    def show_admin_screen(self):
        self.clear_frame()

        frame_controls = tk.Frame(self.main_frame, bg='#d3d3d3', bd=10)
        frame_controls.pack(pady=10, padx=20, fill=tk.BOTH)
        buttons = [
            ("Xem", self.view_books),
            ("Tìm Kiếm", self.search_books),
            ("Thêm", self.add_book),
            ("Cập Nhật", self.update_book),
            ("Xóa", self.delete_book),
            ("Cấp Sách", self.issue_book),
            ("Quản Lý Người Dùng", self.manage_users),
            ("Đăng Xuất", self.logout)
        ]

        for idx, (text, command) in enumerate(buttons):
            color = "#FF6347" if text == "Đăng Xuất" else "#F5A9BC"
            tk.Button(frame_controls, text=text, width=17, command=command, bg=color, fg="white", font=("Helvetica", 12)).grid(row=0, column=idx, padx=10, pady=10)

        frame_display = tk.Frame(self.main_frame, bg="white", bd=5, relief="raised")
        frame_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(frame_display, columns=['STT', 'Tên Sách ', 'Tác Giả ', 'Năm ', 'Mã Sách ', 'Số Lượng '], show="headings")
        self.tree.column('STT', width=50, anchor='center')
        self.tree.column('Tên Sách ', width=170)
        self.tree.column('Tác Giả ', width=170)
        self.tree.column('Năm ', width=100, anchor='center')
        self.tree.column('Mã Sách ', width=100, anchor='center')
        self.tree.column('Số Lượng ', width=100, anchor='center')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        frame_book_info = tk.Frame(self.main_frame, bg='#d3d3d3')
        frame_book_info.pack(pady=20, padx=20, fill=tk.BOTH)
        labels = ["Tên Sách:", "Tác Giả:", "Năm:", "Mã Sách:", "Số Lượng:"]
        self.entry_title = tk.Entry(frame_book_info, font=("Helvetica", 12))
        self.entry_author = tk.Entry(frame_book_info, font=("Helvetica", 12))
        self.entry_year = tk.Entry(frame_book_info, font=("Helvetica", 12))
        self.entry_isbn = tk.Entry(frame_book_info, font=("Helvetica", 12))
        self.entry_quantity = tk.Entry(frame_book_info, font=("Helvetica", 12))
        entries = [self.entry_title, self.entry_author, self.entry_year, self.entry_isbn, self.entry_quantity]

        for idx, (text, entry) in enumerate(zip(labels, entries)):
            tk.Label(frame_book_info, text=text, font=("Helvetica", 12), bg="#d3d3d3").grid(row=idx, column=0, padx=10, pady=10, sticky=tk.E)
            entry.grid(row=idx, column=1, padx=10, pady=10)
    # Xóa nội dung khung hiển thị
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    # Xem sách
    def view_books(self):
        self.tree.delete(*self.tree.get_children())
        cur.execute("SELECT * FROM books")
        for idx, row in enumerate(cur.fetchall()):
            author = row[1]
            if author not in author_colors:
                author_colors[author] = generate_pastel_color()
            self.tree.insert("", tk.END, values=(idx + 1, *row), tags=(author,))
            self.tree.tag_configure(author, background=author_colors[author])
    # Tìm kiếm sách
    def search_books(self):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT * FROM books WHERE title=? OR author=? OR year=? ORx isbn=?"
        params = (self.entry_title.get(), self.entry_author.get(), self.entry_year.get(), self.entry_isbn.get())
        results = list(cur.execute(query, params))
        if results:
            for idx, row in enumerate(results):
                self.tree.insert("", tk.END, values=(idx + 1, *row))
        else:
            messagebox.showinfo("Thông Báo", "Không tìm thấy kết quả phù hợp.")
        self.clear_entries()  # Clear entries after search
    # Thêm sách
    def validate_entry(self, value):
        return value.isdigit()

    def add_book(self):
        if not (self.entry_title.get() and self.entry_author.get() and self.validate_entry(self.entry_year.get()) and self.validate_entry(self.entry_isbn.get()) and self.validate_entry(self.entry_quantity.get())):
            messagebox.showinfo("Thông Báo", "Vui lòng nhập đầy đủ thông tin và sử dụng số cho Năm, Mã Sách, và Số Lượng")
            return
        try:
            cur.execute("INSERT INTO books (title, author, year, isbn, quantity) VALUES (?, ?, ?, ?, ?)",
                         (self.entry_title.get(), self.entry_author.get(), self.entry_year.get(), self.entry_isbn.get(), self.entry_quantity.get()))
            conn.commit()
            self.clear_entries()
            self.view_books()
            messagebox.showinfo("Thông Báo", "Thêm sách thành công")
        except sqlite3.IntegrityError:
            messagebox.showinfo("Thông Báo", "Thông tin sách đã tồn tại")
    # Cập nhật sách
    def update_book(self):
        selected = self.tree.focus()
        values = self.tree.item(selected, 'values')
        if not values:
            messagebox.showinfo("Thông Báo", "Vui lòng chọn sách để cập nhật")
            return
        cur.execute("UPDATE books SET title=?, author=?, year=?, isbn=?, quantity=? WHERE title=? AND author=? AND year=? AND isbn=?",
                         (self.entry_title.get(), self.entry_author.get(), self.entry_year.get(), self.entry_isbn.get(), self.entry_quantity.get(), values[1], values[2], values[3], values[4]))
        conn.commit()
        self.clear_entries()
        self.view_books()
        messagebox.showinfo("Thông Báo", "Cập nhật sách thành công")
    # Xóa sách
    def delete_book(self):
        selected = self.tree.focus()
        values = self.tree.item(selected, 'values')
        if not values:
            messagebox.showinfo("Thông Báo", "Vui lòng chọn sách để xóa")
            return
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc chắn muốn xóa sách này không?"):
            cur.execute("DELETE FROM books WHERE title=? AND author=? AND year=? AND isbn=?", (values[1], values[2], values[3], values[4]))
            conn.commit()
            self.clear_entries()
            self.view_books()
    # Quản lý người dùng
    def manage_users(self):
        self.clear_frame()

        def view_users():
            users_tree.delete(*users_tree.get_children())
            cur.execute("SELECT * FROM users")
            for row in cur.fetchall():
                users_tree.insert("", tk.END, values=row)

        def add_user():
            if not (entry_username.get() and entry_password.get()):
                messagebox.showinfo("Thông Báo", "Vui lòng nhập đầy đủ thông tin")
                return
            if not self.validate_password(entry_password.get()):
                messagebox.showinfo("Lỗi", "Mật khẩu phải có độ dài từ 8 đến 16 ký tự và phải có cả chữ và số")
                return
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (entry_username.get(), entry_password.get()))
                conn.commit()
                view_users()
                messagebox.showinfo("Thông Báo", "Thêm người dùng thành công")
            except sqlite3.IntegrityError:
                messagebox.showinfo("Thông Báo", "Người dùng đã tồn tại")

        def delete_user():
            selected = users_tree.focus()
            values = users_tree.item(selected, 'values')
            if not values:
                messagebox.showinfo("Thông Báo", "Vui lòng chọn người dùng để xóa")
                return
            if messagebox.askyesno("Xác Nhận", "Bạn có chắc chắn muốn xóa người dùng này không?"):
                cur.execute("DELETE FROM users WHERE username=?", (values[0],))
                conn.commit()
                view_users()

        frame_controls = tk.Frame(self.main_frame, bg='#d3d3d3', bd=10)
        frame_controls.pack(pady=10, padx=20, fill=tk.BOTH)
        tk.Button(frame_controls, text="Xem Người Dùng", width=17, command=view_users, bg="#F5A9BC", fg="white").grid(row=0, column=0, padx=10, pady=10)
        tk.Button(frame_controls, text="Thêm Người Dùng", width=17, command=add_user, bg="#F5A9BC", fg="white").grid(row=0, column=1, padx=10, pady=10)
        tk.Button(frame_controls, text="Xóa Người Dùng", width=17, command=delete_user, bg="#F5A9BC", fg="white").grid(row=0, column=2, padx=10, pady=10)
        tk.Button(frame_controls, text="Quay Lại", width=17, command=self.show_admin_screen, bg="#F5A9BC", fg="white").grid(row=0, column=3, padx=10, pady=10)

        frame_users = tk.Frame(self.main_frame, bg="white", bd=5, relief="raised")
        frame_users.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        users_tree = ttk.Treeview(frame_users, columns=['Tên Đăng Nhập', 'Mật Khẩu'], show="headings")
        users_tree.heading('Tên Đăng Nhập', text='Tên Đăng Nhập')
        users_tree.heading('Mật Khẩu', text='Mật Khẩu')
        users_tree.pack(fill=tk.BOTH, expand=True)

        frame_user_info = tk.Frame(self.main_frame, bg='#d3d3d3')
        frame_user_info.pack(pady=20, padx=20, fill=tk.BOTH)
        tk.Label(frame_user_info, text="Tên Đăng Nhập:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Label(frame_user_info, text="Mật Khẩu:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        entry_username = tk.Entry(frame_user_info, font=("Helvetica", 12))
        entry_password = tk.Entry(frame_user_info, font=("Helvetica", 12), show='*')
        entry_username.grid(row=0, column=1, padx=10, pady=10)
        entry_password.grid(row=1, column=1, padx=10, pady=10)
    # Cấp sách
    def issue_book(self):
        self.clear_frame()
        frame_controls = tk.Frame(self.main_frame, bg='#d3d3d3', bd=10)
        frame_controls.pack(pady=10, padx=20, fill=tk.BOTH)
        tk.Button(frame_controls, text="Cấp Sách", width=17, command=self.issue_book_confirm, bg="#F5A9BC", fg="white").grid(row=0, column=0, padx=10, pady=10)
        tk.Button(frame_controls, text="Trả Sách", width=17, command=self.return_book, bg="#F5A9BC", fg="white").grid(row=0, column=1, padx=10, pady=10)
        tk.Button(frame_controls, text="Thống Kê", width=17, command=self.show_statistics, bg="#F5A9BC", fg="white").grid(row=0, column=2, padx=10, pady=10)
        tk.Button(frame_controls, text="Quay Lại", width=17, command=self.show_admin_screen, bg="#F5A9BC", fg="white").grid(row=0, column=3, padx=10, pady=10)

        frame_issue = tk.Frame(self.main_frame, bg='#d3d3d3')
        frame_issue.pack(pady=20, padx=20, fill=tk.BOTH)

        cur.execute("SELECT username FROM users")
        usernames = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT isbn FROM books")
        isbns = [row[0] for row in cur.fetchall()]

        tk.Label(frame_issue, text="Tên Đăng Nhập:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Label(frame_issue, text="Mã Sách:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Label(frame_issue, text="Ngày Mượn:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Label(frame_issue, text="Ngày Trả:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=3, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Label(frame_issue, text="Số Lượng Sách:", font=("Helvetica", 12), bg="#d3d3d3").grid(row=4, column=0, padx=10, pady=10, sticky=tk.E)  # Updated label

        self.entry_user = ttk.Combobox(frame_issue, values=usernames, font=("Helvetica", 12))
        self.entry_isbn_issue = ttk.Combobox(frame_issue, values=isbns, font=("Helvetica", 12))
        self.entry_borrow_date = DateEntry(frame_issue, font=("Helvetica", 12))
        self.entry_return_date = DateEntry(frame_issue, font=("Helvetica", 12))
        self.entry_quantity_issue = tk.Entry(frame_issue, font=("Helvetica", 12))
        self.entry_user.grid(row=0, column=1, padx=10, pady=10)
        self.entry_isbn_issue.grid(row=1, column=1, padx=10, pady=10)
        self.entry_borrow_date.grid(row=2, column=1, padx=10, pady=10)
        self.entry_return_date.grid(row=3, column=1, padx=10, pady=10)
        self.entry_quantity_issue.grid(row=4, column=1, padx=10, pady=10)

        frame_borrow_records = tk.Frame(self.main_frame, bg="white", bd=5, relief="raised")
        frame_borrow_records.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.borrow_tree = ttk.Treeview(frame_borrow_records, columns=['STT', 'Tên Đăng Nhập', 'Mã Sách ', 'Tên Sách ', 'Tác Giả ', 'Năm ', 'Số Lượng Sách ', 'Ngày Mượn', 'Ngày Trả', 'Trạng thái'], show="headings")
        self.borrow_tree.column('STT', width=50, anchor='center')
        self.borrow_tree.column('Tên Đăng Nhập', width=100)
        self.borrow_tree.column('Mã Sách ', width=100, anchor='center')
        self.borrow_tree.column('Tên Sách ', width=170)
        self.borrow_tree.column('Tác Giả ', width=170)
        self.borrow_tree.column('Năm ', width=100, anchor='center')
        self.borrow_tree.column('Số Lượng Sách ', width=100, anchor='center')  # Updated column name
        self.borrow_tree.column('Ngày Mượn', width=100, anchor='center')
        self.borrow_tree.column('Ngày Trả', width=100, anchor='center')
        self.borrow_tree.column('Trạng thái', width=100, anchor='center')
        for col in self.borrow_tree["columns"]:
            self.borrow_tree.heading(col, text=col)
        self.borrow_tree.pack(fill=tk.BOTH, expand=True)
        self.update_borrow_tree()
    # Cập nhật bảng phiếu mượn
    def update_borrow_tree(self):
        self.borrow_tree.delete(*self.borrow_tree.get_children())
        cur.execute("SELECT rowid, * FROM books WHERE borrowed_by IS NOT NULL")
        for idx, row in enumerate(cur.fetchall()):
            return_date = datetime.strptime(row[8], "%Y-%m-%d")
            actual_return_date = datetime.now()
            status = "Đã Cấp Sách Thành Công" if actual_return_date <= return_date else "Đã quá hạn trả sách "
            self.borrow_tree.insert("", tk.END, values=(idx + 1, row[6], row[4], row[1], row[2], row[3], row[5], row[7], row[8], status))
    # Xác nhận cấp sách
    def issue_book_confirm(self):
        username = self.entry_user.get()
        isbn = self.entry_isbn_issue.get()
        borrow_date = self.entry_borrow_date.get_date().strftime("%Y-%m-%d")
        return_date = self.entry_return_date.get_date().strftime("%Y-%m-%d")
        quantity = self.entry_quantity_issue.get()

        if not (username and isbn and borrow_date and return_date and quantity):
            messagebox.showinfo("Thông Báo", "Vui lòng nhập đầy đủ thông tin")
            return

        borrow_date_obj = datetime.strptime(borrow_date, "%Y-%m-%d")
        return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")

        if borrow_date_obj > return_date_obj:
            messagebox.showinfo("Thông Báo", "Ngày mượn phải nhỏ hơn hoặc bằng Ngày trả")
            return

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        if not user:
            messagebox.showinfo("Thông Báo", "Người dùng không tồn tại")
            return
        cur.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        book = cur.fetchone()
        if not book:
            messagebox.showinfo("Thông Báo", "Sách không tồn tại")
            return
        if book[4] < int(quantity):
            messagebox.showinfo("Thông Báo", "Không đủ sách để cấp")
            return

        cur.execute("UPDATE books SET borrowed_by=?, borrow_date=?, return_date=?, quantity=quantity-? WHERE isbn=?",
                    (username, borrow_date, return_date, quantity, isbn))
        conn.commit()
        self.update_borrow_tree()
        messagebox.showinfo("Thông Báo", "Cấp sách thành công")
    # Xác nhận trả sách
    def return_book(self):
        selected = self.borrow_tree.focus()
        values = self.borrow_tree.item(selected, 'values')
        if not values:
            messagebox.showinfo("Thông Báo", "Vui lòng chọn sách để trả")
            return
        return_date = datetime.strptime(values[8], "%Y-%m-%d")
        actual_return_date = datetime.now()
        status = "Đã Cấp Sách Thành Công" if actual_return_date <= return_date else "Đã quá hạn trả sách "

        cur.execute("UPDATE books SET borrowed_by=NULL, borrow_date=NULL, return_date=NULL, status=?, quantity=quantity+? WHERE isbn=?",
                    (status, values[6], values[2]))
        conn.commit()
        self.update_borrow_tree()
        messagebox.showinfo("Thông Báo", "Trả sách thành công")
    # Xóa phiếu mượn sách
    def delete_record(self):
        selected = self.borrow_tree.focus()
        values = self.borrow_tree.item(selected, 'values')
        if not values:
            messagebox.showinfo("Thông Báo", "Vui lòng chọn phiếu mượn để xóa")
            return
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc chắn muốn xóa phiếu mượn này không?"):
            cur.execute("DELETE FROM books WHERE rowid=?", (values[0],))
            conn.commit()
            self.update_borrow_tree()
            messagebox.showinfo("Thông Báo", "Xóa phiếu mượn thành công")
    # Hiển thị thống kê
    def show_statistics(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Thống Kê")
        stats_window.geometry("800x600")
        stats_window.configure(bg='#f5f5f5')

        cur.execute("SELECT COUNT(*) FROM books")
        book_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM books WHERE borrowed_by IS NOT NULL")
        borrowed_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM books WHERE return_date < ?", (datetime.now().strftime("%Y-%m-%d"),))
        overdue_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM books WHERE borrowed_by IS NOT NULL")
        borrow_records = cur.fetchall()
        # Hiển thị số liệu thống kê dưới dạng lưới các hộp màu
        stats_frame = tk.Frame(stats_window, bg='#f5f5f5')
        stats_frame.pack(pady=10)
        
        stats_data = [
            ("Tổng số sách có trong hệ thống", book_count),
            ("Tổng số sách đã cho mượn", borrowed_count),
            ("Tổng số phiếu mượn sách", len(borrow_records)),
            ("Tổng số phiếu mượn sách quá hạn", overdue_count),
            ("Tổng số tài khoản sinh viên trong hệ thống", user_count)
        ]
        
        for idx, (text, value) in enumerate(stats_data):
            row = idx // 3
            col = idx % 3
            stat_frame = tk.Frame(stats_frame, bg=generate_pastel_color(), bd=2, relief="raised")
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            tk.Label(stat_frame, text=text, font=("Helvetica", 12), bg=stat_frame["bg"]).pack(padx=10, pady=10)
            tk.Label(stat_frame, text=value, font=("Helvetica", 12, "bold"), bg=stat_frame["bg"]).pack(padx=10, pady=10)

        book_data = [book_count, borrowed_count]
        book_labels = ['Tổng Số Sách', 'Sách Đã Cho Mượn']
        student_data = [user_count, len(borrow_records), overdue_count]
        student_labels = ['Tổng Số Sinh Viên', 'Phiếu Mượn', 'Phiếu Mượn Quá Hạn']

        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].pie(book_data, labels=book_labels, autopct='%1.1f%%')
        axes[0].set_title('Biểu Đồ Sách')
        axes[1].pie(student_data, labels=student_labels, autopct='%1.1f%%')
        axes[1].set_title('Biểu Đồ Sinh Viên Và Phiếu Mượn')

        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # Thêm nút in
        print_btn = ttk.Button(stats_window, text="In Ra", command=lambda: self.print_statistics(stats_data))
        print_btn.pack(pady=10)
    # Chức năng in số liệu thống kê ra file Excel
    def print_statistics(self, stats_data):
        if messagebox.askyesno("Xác Nhận", "Bạn có muốn in ra thông tin thống kê không?"):
            df = pd.DataFrame(stats_data, columns=["Thông Tin", "Giá Trị"])
            df.to_excel("library_statistics.xlsx", index=False)
            messagebox.showinfo("Thông Báo", "In ra file Excel thành công")
    # Xóa các thông tin đã nhập
    def clear_entries(self):
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_isbn.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)

    def logout(self):
        if messagebox.askyesno("Xác Nhận", "Bạn có muốn đăng xuất không?"):
            self.current_user = None
            self.show_login_register_screen()

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    author_colors = {}
    main()
