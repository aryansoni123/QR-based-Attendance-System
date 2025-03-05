import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
import os
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import subprocess

# Storing credentials in {class_id: (teacher_id, password)} format
TEACHER_CREDENTIALS = {
    "DMS": ("DMS_teacher", "passDMS"),
    "COA": ("COA_teacher", "passCOA"),
    "TOC": ("TOC_teacher", "passTOC"),
    "DBMS": ("DBMS_teacher", "passDBMS"),
    "OOPSJ": ("OOPSJ_teacher", "passOOPSJ"),
    "LMP-2": ("LMP2_teacher", "passLMP2"),
    "LOOPSJ": ("LOOPSJ_teacher", "passLOOPSJ"),
    "LCOA": ("LCOA_teacher", "passLCOA"),
    "LDBMS": ("LDBMS_teacher", "passLDBMS")
}
# Expected WiFi name for attendance verification
EXPECTED_WIFI = "OnePlus Nord CE 2 Lite 5G"
CSV_FILE = "attendance.csv"

# Sample student data (ID -> Name, Password)
students ={
    "11": ("Arin", "arin"),
    "28": ("Mayank", "mayank"),
    "19": ("Gatik", "gatik"),
}

SUBJECTS = ["DMS", "COA", "TOC", "DBMS", "OOPSJ", "LMP-2", "LOOPSJ", "LCOA", "LDBMS"]


def generate_qr(class_id, qr_label):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5,
    )
    qr.add_data(class_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")
    
    img_path = f"qr_codes/{class_id}.png"
    img.save(img_path)
    
    qr_image = Image.open(img_path)
    qr_image = qr_image.resize((200, 200))  # Resize QR for display
    qr_photo = ImageTk.PhotoImage(qr_image)
    
    qr_label.config(image=qr_photo)
    qr_label.image = qr_photo  # Keep reference to avoid garbage collection

def scan_qr():
    cap = cv2.VideoCapture(0)
    print("Scanning... Place the QR code in front of the camera.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objs = decode(frame)
        for obj in decoded_objs:
            class_id = obj.data.decode('utf-8')  
            cap.release()
            cv2.destroyAllWindows()
            return class_id  

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def student_view_attendance():
    try:
        df = pd.read_csv(CSV_FILE)

        if student_name not in df["Name"].values:
            messagebox.showerror("Error", "Attendance record not found!")
            return

        student_attendance = df[df["Name"] == student_name].drop(columns=["Name"])  # Naam hata diya

        # Transforming data for better display
        subjects = list(student_attendance.columns)
        attendance_values = student_attendance.iloc[0].values  

        formatted_data = pd.DataFrame({"Subject": subjects, "Attendance": attendance_values})

        attendance_window = tk.Toplevel()
        attendance_window.title(f"Attendance - {student_name}")
        attendance_window.geometry("400x300")

        frame = tk.Frame(attendance_window)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=("Subject", "Attendance"), show="headings")
        tree.heading("Subject", text="Subject")
        tree.heading("Attendance", text="Attendance")
        tree.column("Subject", anchor="center", width=150)
        tree.column("Attendance", anchor="center", width=100)

        for index, row in formatted_data.iterrows():
            tree.insert("", tk.END, values=(row["Subject"], row["Attendance"]))

        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscroll=scrollbar.set)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load attendance: {e}")

def teacher_view_attendance():
    try:
        df = pd.read_csv(CSV_FILE)

        attendance_window = tk.Toplevel()
        attendance_window.title("Attendance Sheet")
        attendance_window.geometry("600x400")

        frame = tk.Frame(attendance_window)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame)
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for index, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscroll=scrollbar.set)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load attendance: {e}")

# Function to open Teacher Dashboard
def open_teacher_dashboard(class_id):
    dashboard = tk.Toplevel()
    dashboard.title(f"Teacher Dashboard - {class_id}")
    dashboard.geometry("400x600")

    tk.Label(dashboard, text=f"Teacher Dashboard ({class_id})", font=("Arial", 16, "bold")).pack(pady=20)
    
    qr_label = tk.Label(dashboard)
    qr_label.pack(pady=10)
    
    generate_qr_btn = tk.Button(dashboard, text="Generate QR", font=("Arial", 14), bg="blue", fg="white", width=20, command=lambda: generate_qr(class_id, qr_label))
    generate_qr_btn.pack(pady=10)

    #view_attendance_btn = tk.Button(dashboard, text="View Attendance", font=("Arial", 14), bg="green", fg="white", width=20, command=view_attendance())
    view_attendance_btn = tk.Button(dashboard, text="View Attendance", font=("Arial", 14), bg="green", fg="white", width=20, command=teacher_view_attendance)

    view_attendance_btn.pack(pady=10)

def open_login_window():
    global login_window, entry_id, entry_pass, error_label
    login_window = tk.Tk()
    login_window.title("Login Portal")
    login_window.geometry("350x500")
    #login_window.configure(bg="#1e1e1e")

    heading_frame = tk.Frame(login_window)
    heading_frame.pack(side="top", fill="x", pady=(20, 10))

    frame = tk.Frame(login_window, padx=20, pady=20)
    frame.pack(expand=True)

    tk.Label(heading_frame, text="Attendance System", font=("Arial", 20, "bold")).pack(pady=(0,30))
    #tk.Label(frame, text="Student ID:", fg="white", bg="#1e1e1e").pack()
    student_btn = tk.Button(frame, text="Student Login", font=("Arial", 16), command=student_login, width=20, bg="lightblue")
    student_btn.pack(pady=20)
    
    #entry_id = ttk.Entry(frame, font=("Arial", 12))
    #entry_id.pack()


    teacher_btn = tk.Button(frame, text="Teacher Login", font=("Arial", 16), command=teacher_login, width=20, bg="lightgreen")
    teacher_btn.pack(pady=20)
    
    #tk.Label(frame, text="Password:", fg="white", bg="#1e1e1e").pack()
    #entry_pass = ttk.Entry(frame, show="*", font=("Arial", 12))
    #entry_pass.pack()

    #error_label = tk.Label(frame, text="", fg="red", bg="#1e1e1e")
    #error_label.pack()

    #tk.Button(frame, text="Login", font=("Arial", 12, "bold"), bg="#2196F3", fg="white", padx=10, pady=5, command=login).pack(pady=10)
    #tk.Button(frame, text="View Attendance Sheet", font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=10, pady=5, command=lambda: os.system(f'notepad {CSV_FILE}')).pack()

    login_window.mainloop()


def update_attendance(student_name, subject):
    df = pd.read_csv(CSV_FILE)
    
    if subject in df.columns and student_name in df["Name"].values:
        df.loc[df["Name"] == student_name, subject] += 1  # Increment attendance
        df.to_csv(CSV_FILE, index=False)
        print(f"Attendance updated for {student_name} in {subject}.")
        return True
    print("Invalid Subject or Student Name")
    return False


def get_wifi_ssid():
    try:
        result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode("utf-8")
        for line in result.split("\n"):
            if "SSID" in line:
                return line.split(":")[1].strip()
    except Exception as e:
        print("Error getting WiFi SSID:", e)
    return None


def student_dashboard():
    attendance_window = tk.Tk()
    attendance_window.title("QR Attendance Scanner")
    attendance_window.geometry("350x500")
    #attendance_window.configure(bg="#1e1e1e")

    label = tk.Label(attendance_window, text="Scan your QR Code", font=("Arial", 20, "bold"))
    label.pack(pady=20)

    def scan_and_mark():
        class_id = scan_qr()
        if class_id and class_id in SUBJECTS:  # Validate class_id
            wifi_ssid = get_wifi_ssid()
            if wifi_ssid == EXPECTED_WIFI:
                if update_attendance(student_name, class_id):
                    messagebox.showinfo("Success", f"Attendance marked for {class_id}")
                    attendance_window.destroy()
                    open_login_window()
                else:
                    messagebox.showerror("Error", "Invalid Class ID")
            else:
                messagebox.showerror("Error", "Wrong WiFi Network")
        else:
            messagebox.showerror("Error", "Invalid QR Code")


    btn_scan = tk.Button(attendance_window, text="Scan QR Code", font=("Arial",16 , "bold"), bg="#4CAF50", fg="white", padx=30, pady=5, command=scan_and_mark)
    btn_scan.pack(pady=20)

    btn_attend = tk.Button(attendance_window, text="View Attendance", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", padx=30, pady=5, command=student_view_attendance)
    btn_attend.pack(pady=20)

    attendance_window.mainloop()


def validate_login(user_type, user_id, password, window):
    if user_type == "Student":
        if user_id in students and students[user_id][1] == password:
            messagebox.showinfo("Login Success", "Welcome, "f"{students[user_id][0]}")
            global student_name
            student_name = students[user_id][0]  # Get student name
            #error_label.config(text="", fg="red")
            window.destroy()
            student_dashboard()
        else:
            messagebox.showinfo("Wrong Credentials","Invalid ID or Password")
            #error_label.config(text="Invalid ID or Password", fg="red")
    elif user_type == "Teacher":
        for class_id, (stored_id, stored_pass) in TEACHER_CREDENTIALS.items():
            if user_id == stored_id and password == stored_pass:
                messagebox.showinfo("Login Success", f"Welcome, {user_id}!")
                window.destroy()
                open_teacher_dashboard(class_id)
                return
        messagebox.showerror("Invalid Credentials", "Incorrect User ID or Password!")
    else:
        messagebox.showerror("Invalid Credentials", "Incorrect User ID or Password!")

def student_login():
    login_window.withdraw()
    student_window = tk.Toplevel()
    student_window.title("Student Login")
    student_window.geometry("350x500")
    tk.Label(student_window, text="Student Login", font=("Arial", 18, "bold")).pack(pady=20)
    tk.Label(student_window, text="User ID:", font=("Arial", 14)).pack(anchor="w", padx=20)
    user_id_entry = tk.Entry(student_window, font=("Arial", 14), width=30)
    user_id_entry.pack(pady=5, padx=20)
    tk.Label(student_window, text="Password:", font=("Arial", 14)).pack(anchor="w", padx=20)
    password_entry = tk.Entry(student_window, font=("Arial", 14), width=30, show="*")
    password_entry.pack(pady=5, padx=20)
    
    def attempt_login():
        user_id = user_id_entry.get()
        password = password_entry.get()
        validate_login("Student", user_id, password, student_window)
    
    login_btn = tk.Button(student_window, text="Login", font=("Arial", 14), bg="green", fg="white", width=15, command=attempt_login)
    login_btn.pack(pady=20)
    #view_attendance_btn = tk.Button(student_window, text="View Attendance", font=("Arial", 14), bg="blue", fg="white", width=15)
    #view_attendance_btn.pack(side="bottom", pady=30, anchor="se", padx=20)
    student_window.mainloop()

def teacher_login():
    login_window.withdraw()
    teacher_window = tk.Toplevel()
    teacher_window.title("Teacher Login")
    teacher_window.geometry("350x500")
    tk.Label(teacher_window, text="Teacher Login", font=("Arial", 18, "bold")).pack(pady=20)
    tk.Label(teacher_window, text="User ID:", font=("Arial", 14)).pack(anchor="w", padx=20)
    user_id_entry = tk.Entry(teacher_window, font=("Arial", 14), width=30)
    user_id_entry.pack(pady=5, padx=20)
    tk.Label(teacher_window, text="Password:", font=("Arial", 14)).pack(anchor="w", padx=20)
    password_entry = tk.Entry(teacher_window, font=("Arial", 14), width=30, show="*")
    password_entry.pack(pady=5, padx=20)
    
    def attempt_login():
        user_id = user_id_entry.get()
        password = password_entry.get()
        validate_login("Teacher", user_id, password, teacher_window)
    
    login_btn = tk.Button(teacher_window, text="Login", font=("Arial", 14), bg="green", fg="white", width=15, command=attempt_login)
    login_btn.pack(pady=20)
    teacher_window.mainloop()


open_login_window()
