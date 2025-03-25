import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
from fpdf import FPDF
import re


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker 💰")
        self.root.geometry("600x650")

        self.style = Style(theme="darkly")

        ttk.Label(self.root, text="💰 Expense Tracker", font=("Arial", 18, "bold")).pack(pady=10)

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(pady=10, fill="x")

        ttk.Label(frame, text="Expense Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.expense_name = ttk.Entry(frame, width=25)
        self.expense_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Amount (₹):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount = ttk.Entry(frame, width=25)
        self.amount.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.category = ttk.Combobox(frame, values=["Food 🍔", "Transport 🚗", "Shopping 🛍️", "Bills 💡", "Other 📝"], width=23)
        self.category.grid(row=2, column=1, padx=5, pady=5)
        self.category.current(0)

        self.add_button = ttk.Button(self.root, text="➕ Add Expense", command=self.add_expense, style="success.TButton")
        self.add_button.pack(pady=5)

        self.summary_button = ttk.Button(self.root, text="📊 View Summary", command=self.show_summary, style="primary.TButton")
        self.summary_button.pack()

        self.balance_label = ttk.Label(self.root, text="Total Spent: ₹0", font=("Arial", 12, "bold"))
        self.balance_label.pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Name", "Amount", "Category", "Date"), show="headings")
        self.tree.heading("Name", text="Expense Name")
        self.tree.heading("Amount", text="Amount (₹)")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree.bind("<Double-1>", self.edit_expense)

        self.delete_button = ttk.Button(self.root, text="🗑️ Delete Expense", command=self.delete_expense, style="danger.TButton")
        self.delete_button.pack(pady=5)

        self.export_button = ttk.Button(self.root, text="📄 Export to PDF", command=self.export_to_pdf, style="info.TButton")
        self.export_button.pack(pady=5)

        self.theme_button = ttk.Button(self.root, text="🌙 Toggle Dark Mode", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.load_expenses()

    def add_expense(self):
        name = self.expense_name.get()
        amount = self.amount.get()
        category = self.category.get()
        date = datetime.now().strftime("%Y-%m-%d")

        if not name or not amount.isdigit():
            messagebox.showerror("Error", "Please enter valid details!")
            return

        df = pd.DataFrame([[name, int(amount), category, date]], columns=["Name", "Amount", "Category", "Date"])
        try:
            existing = pd.read_csv("expenses.csv")

            # Ensure "Date" column exists
            if "Date" not in existing.columns:
                existing["Date"] = "N/A"

            df = pd.concat([existing, df], ignore_index=True)
        except FileNotFoundError:
            pass

        df.to_csv("expenses.csv", index=False)
        self.tree.insert("", "end", values=(name, amount, category, date))
        self.update_balance()
        self.expense_name.delete(0, "end")
        self.amount.delete(0, "end")
        messagebox.showinfo("Success", "Expense added successfully!")

    def load_expenses(self):
        try:
            df = pd.read_csv("expenses.csv")

            # Ensure "Date" column exists
            if "Date" not in df.columns:
                df["Date"] = "N/A"

            for _, row in df.iterrows():
                self.tree.insert("", "end", values=(row["Name"], row["Amount"], row["Category"], row["Date"]))

            self.update_balance()
        except FileNotFoundError:
            pass

    def update_balance(self):
        try:
            df = pd.read_csv("expenses.csv")
            total = df["Amount"].sum()
            self.balance_label.config(text=f"Total Spent: ₹{total}")
        except FileNotFoundError:
            self.balance_label.config(text="Total Spent: ₹0")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an expense to delete.")
            return

        values = self.tree.item(selected[0], "values")
        df = pd.read_csv("expenses.csv")

        # Convert Amount to int for filtering
        df["Amount"] = df["Amount"].astype(int)
        df = df[(df["Name"] != values[0]) | (df["Amount"] != int(values[1])) | (df["Category"] != values[2])]
        df.to_csv("expenses.csv", index=False)

        self.tree.delete(selected[0])
        self.update_balance()

    def remove_emojis(self, text):
        return re.sub(r'[^\w\s,.-]', '', text)

    def export_to_pdf(self):
        try:
            df = pd.read_csv("expenses.csv")

            if df.empty:
                messagebox.showerror("Error", "No expenses found!")
                return

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Expense Report", ln=True, align="C")
            pdf.ln(10)

            # Table Headers
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 10, "Date", border=1, align="C")
            pdf.cell(50, 10, "Name", border=1, align="C")
            pdf.cell(40, 10, "Amount (INR)", border=1, align="C")
            pdf.cell(50, 10, "Category", border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", "", 12)

            for _, row in df.iterrows():
                date = row["Date"]
                name = self.remove_emojis(row["Name"][:20])
                amount = f"INR {row['Amount']}"
                category = self.remove_emojis(row["Category"][:15])  

                pdf.cell(50, 10, date, border=1)
                pdf.cell(50, 10, name, border=1)
                pdf.cell(40, 10, amount, border=1, align="C")
                pdf.cell(50, 10, category, border=1)
                pdf.ln()


            pdf.output("Expense_Report.pdf", "F")
            messagebox.showinfo("Success", "PDF exported successfully!\nSaved as 'Expense_Report.pdf'.")

        except FileNotFoundError:
            messagebox.showerror("Error", "No expenses found!")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")


    def toggle_theme(self):
        new_theme = "superhero" if self.style.theme_use() == "darkly" else "darkly"
        self.style.theme_use(new_theme)

    def edit_expense(self, event):
        pass  # Future feature

    def show_summary(self):
        try:
            df = pd.read_csv("expenses.csv")

            summary = df.groupby("Category")["Amount"].sum()

            colors = ['#FF6B6B', '#4D96FF', '#28A745', '#FFC107', '#6610F2']
            plt.figure(figsize=(6, 4))
            bars = plt.bar(summary.index, summary.values, color=random.choices(colors, k=len(summary)))
            plt.xlabel("Category")
            plt.ylabel("Total Amount Spent (₹)")
            plt.title("📊 Expense Summary")
            plt.xticks(rotation=15)

            for bar in bars:
                plt.text(bar.get_x() + bar.get_width()/2 - 0.15, bar.get_height() + 5, f"{int(bar.get_height())}₹", fontsize=10)

            plt.show()
        except FileNotFoundError:
            messagebox.showerror("Error", "No expenses found!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
