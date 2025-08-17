import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId

# ----------------- MongoDB Connection -----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["509_A4_automotive_service"]
collection = db["appointments"]

# ----------------- Colors & Styles -----------------
BG_COLOR = "#f4f6f8"
FG_COLOR = "#333333"
BTN_COLOR = "#0078d7"
BTN_HOVER = "#005a9e"
ENTRY_BG = "#f0f2f5"
ENTRY_BORDER = "#d0d7de"

FONT_MAIN = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI Semibold", 10)
FONT_TITLE = ("Segoe UI", 15, "bold")

ROW_COLOR_1 = "#ffffff"   # even row
ROW_COLOR_2 = "#f9fafb"   # odd row

# ----------------- Helpers -----------------
def get_form_data():
    return {
        "appointment_id": entry_id.get().strip(),
        "customer_name": entry_name.get().strip(),
        "phone": entry_phone.get().strip(),
        "service_type": entry_service.get().strip(),
        "date": entry_date.get().strip(),
        "time": entry_time.get().strip()
    }

def clear_entries():
    for entry in (entry_id, entry_name, entry_phone, entry_service, entry_date, entry_time):
        entry.delete(0, tk.END)

def get_selected_oid():
    sel = tree.selection()
    if not sel:
        return None
    try:
        return ObjectId(sel[0])
    except Exception:
        return None

# ----------------- CRUD -----------------
def create_appointment():
    appt = get_form_data()
    if not all(appt.values()):
        messagebox.showerror("Error", "All fields are required.")
        return
    # Enforce unique appointment_id
    if collection.find_one({"appointment_id": appt["appointment_id"]}):
        messagebox.showerror("Error", "Appointment ID already exists.")
        return
    collection.insert_one(appt)
    messagebox.showinfo("Success", "Appointment added successfully!")
    clear_entries()
    read_appointments()

def read_appointments():
    # Clear table
    for row in tree.get_children():
        tree.delete(row)
    docs = list(collection.find())
    if not docs:
        return
    for idx, appt in enumerate(docs):
        tag = "evenrow" if idx % 2 == 0 else "oddrow"
        iid = str(appt["_id"])  # Store Mongo _id as the Treeview item id
        tree.insert(
            "", tk.END, iid=iid, tags=(tag,),
            values=(
                appt.get("appointment_id", ""),
                appt.get("customer_name", ""),
                appt.get("phone", ""),
                appt.get("service_type", ""),
                appt.get("date", ""),
                appt.get("time", "")
            )
        )

def update_appointment():
    oid = get_selected_oid()
    if not oid:
        messagebox.showerror("Error", "Please select an appointment to update.")
        return

    updated = get_form_data()
    if not all(updated.values()):
        messagebox.showerror("Error", "All fields are required.")
        return

    # Prevent duplicate appointment_id (exclude current doc)
    if collection.find_one({"appointment_id": updated["appointment_id"], "_id": {"$ne": oid}}):
        messagebox.showerror("Error", "Another appointment with this ID already exists.")
        return

    result = collection.update_one({"_id": oid}, {"$set": updated})
    if result.matched_count == 0:
        messagebox.showerror("Error", "Appointment not found. It may have been removed.")
    elif result.modified_count == 0:
        messagebox.showinfo("No change", "No fields changed — the data is already up to date.")
    else:
        messagebox.showinfo("Success", "Appointment updated successfully!")

    clear_entries()
    read_appointments()

def delete_appointment():
    oid = get_selected_oid()
    if not oid:
        messagebox.showerror("Error", "Please select an appointment to delete.")
        return

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
        result = collection.delete_one({"_id": oid})
        if result.deleted_count == 0:
            messagebox.showerror("Error", "Appointment not found. It may have been removed.")
        else:
            messagebox.showinfo("Success", "Appointment deleted successfully!")
        clear_entries()
        read_appointments()

# ----------------- UI Events -----------------
def on_row_select(event):
    sel = tree.selection()
    if not sel:
        return
    values = tree.item(sel[0])["values"]
    if len(values) >= 6:
        clear_entries()
        entry_id.insert(0, values[0])
        entry_name.insert(0, values[1])
        entry_phone.insert(0, values[2])
        entry_service.insert(0, values[3])
        entry_date.insert(0, values[4])
        entry_time.insert(0, values[5])

# ----------------- UI Setup -----------------
root = tk.Tk()
root.title("509 A4 Automotive Appointment Management")
root.geometry("900x600")
root.config(bg=BG_COLOR)

# Title
tk.Label(root, text="509 A4 Automotive Appointment Management",
         bg=BG_COLOR, fg=FG_COLOR, font=FONT_TITLE).pack(anchor="center", pady=(15, 5))

# Form
form_frame = tk.Frame(root, bg=BG_COLOR)
form_frame.pack(anchor="w", padx=20, pady=5)

def create_label_entry(text):
    tk.Label(form_frame, text=text, bg=BG_COLOR, fg=FG_COLOR, font=FONT_LABEL).pack(anchor="w", pady=(8, 0))
    entry_frame = tk.Frame(form_frame, bg=ENTRY_BORDER, bd=1)
    entry_frame.pack(anchor="w", pady=4)
    entry = tk.Entry(entry_frame, bg=ENTRY_BG, fg=FG_COLOR,
                     insertbackground="black", font=FONT_MAIN, width=40, relief="flat")
    entry.pack(ipady=5, ipadx=5, padx=1, pady=1)
    return entry

entry_id = create_label_entry("Appointment ID")
entry_name = create_label_entry("Customer Name")
entry_phone = create_label_entry("Phone Number")
entry_service = create_label_entry("Service Type")
entry_date = create_label_entry("Date (YYYY-MM-DD)")
entry_time = create_label_entry("Time (HH:MM)")

# Buttons
btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(anchor="w", padx=20, pady=10)

def create_button(text, command, color=BTN_COLOR):
    btn = tk.Button(btn_frame, text=text, command=command,
                    bg=color, fg="white", activebackground=BTN_HOVER, activeforeground="white",
                    font=FONT_LABEL, width=12, relief="flat", bd=0)
    btn.pack(side=tk.LEFT, padx=6, pady=3)
    return btn

create_button("Add", create_appointment)
create_button("View", read_appointments)
create_button("Update", update_appointment)
create_button("Delete", delete_appointment)
create_button("Clear", clear_entries, "#e74c3c")

# Table Frame
table_frame = tk.Frame(root, bg=BG_COLOR)
table_frame.pack(padx=20, pady=10, fill="both", expand=True)

columns = ("ID", "Customer Name", "Phone", "Service Type", "Date", "Time")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

# Column setup
tree.heading("ID", text="ID")
tree.heading("Customer Name", text="Customer Name")
tree.heading("Phone", text="Phone")
tree.heading("Service Type", text="Service Type")
tree.heading("Date", text="Date")
tree.heading("Time", text="Time")

tree.column("ID", anchor="center", width=140)
tree.column("Customer Name", anchor="center", width=160)
tree.column("Phone", anchor="center", width=120)
tree.column("Service Type", anchor="center", width=150)
tree.column("Date", anchor="center", width=100)
tree.column("Time", anchor="center", width=80)

# Scrollbars
vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Row striping styles
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", font=FONT_MAIN, background=ROW_COLOR_1, fieldbackground=ROW_COLOR_1, foreground=FG_COLOR)
style.map("Treeview", background=[("selected", BTN_COLOR)], foreground=[("selected", "white")])
tree.tag_configure("evenrow", background=ROW_COLOR_1)
tree.tag_configure("oddrow", background=ROW_COLOR_2)

tree.bind("<<TreeviewSelect>>", on_row_select)

# Initial Load
read_appointments()

root.mainloop()