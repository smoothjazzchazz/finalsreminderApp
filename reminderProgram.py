import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import webbrowser
import os
from urllib import parse, request


EXAMS = [
    {
        "course": "ECE 2k1 SP26 Final exam - M. Cui",
        "date": "2026-05-08",
        "start": "19:00",
        "end": "22:00",
        "location": "TBD",
    },
    {
        "course": "ECE 26400-004 Exam 3 (Final) - J. Kim",
        "date": "2026-05-08",
        "start": "13:00",
        "end": "16:00",
        "location": "TBD",
    },
    {
        "course": "ECE 20869 - Final - X. Qiu",
        "date": "2026-05-07",
        "start": "13:00",
        "end": "16:00",
        "location": "TBD",
    },
    {
        "course": "ECE 20875 - Exam 3 - Y. Ding",
        "date": "2026-05-06",
        "start": "15:30",
        "end": "17:08",
        "location": "TBD",
    },
    {
        "course": "MA266 Final",
        "date": "2026-05-06",
        "start": "08:00",
        "end": "11:00",
        "location": "ELLT 116",
    },
]

DEFAULT_STUDY_LINKS = [
    "https://youtube.com",
    "https://purdue.brightspace.com/d2l/home/6824",
    "https://tutorial.math.lamar.edu/",
    "https://www.boilerexams.com/courses"
]


class FinalsReminderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Finals Study Reminder")
        self.root.geometry("700x540")
        self.root.attributes("-topmost", True)

        self.reminder_interval_min = tk.IntVar(value=45)
        self.sms_enabled = tk.BooleanVar(value=False)

        title = tk.Label(
            root,
            text="Upcoming Finals - Keep Studying",
            font=("Segoe UI", 14, "bold"),
            pady=8,
        )
        title.pack()

        self.now_label = tk.Label(root, font=("Segoe UI", 10))
        self.now_label.pack(pady=(0, 8))

        self.listbox = tk.Listbox(root, width=102, height=12, font=("Consolas", 10))
        self.listbox.pack(padx=10, pady=4)

        controls = tk.Frame(root)
        controls.pack(pady=10)

        tk.Label(controls, text="Reminder every (minutes):").grid(row=0, column=0, padx=5)
        tk.Entry(controls, textvariable=self.reminder_interval_min, width=5).grid(
            row=0, column=1, padx=5
        )

        tk.Button(
            controls, text="Remind me now", command=self.show_reminder_popup, width=14
        ).grid(row=0, column=2, padx=10)
        tk.Checkbutton(
            controls, text="Send SMS", variable=self.sms_enabled, onvalue=True, offvalue=False
        ).grid(row=0, column=3, padx=(8, 0))

        self.status_label = tk.Label(root, font=("Segoe UI", 9))
        self.status_label.pack()

        links_frame = tk.LabelFrame(root, text="Study Resource Links", padx=8, pady=6)
        links_frame.pack(fill="x", padx=10, pady=(10, 8))

        input_row = tk.Frame(links_frame)
        input_row.pack(fill="x", pady=(0, 6))

        tk.Label(input_row, text="Add URL:").pack(side="left", padx=(0, 6))
        self.link_input_var = tk.StringVar()
        self.link_entry = tk.Entry(input_row, textvariable=self.link_input_var, width=62)
        self.link_entry.pack(side="left", fill="x", expand=True)
        self.link_entry.bind("<Return>", lambda _event: self.add_link())

        tk.Button(input_row, text="Add", width=8, command=self.add_link).pack(
            side="left", padx=(8, 0)
        )

        self.links_listbox = tk.Listbox(links_frame, height=4, font=("Consolas", 10))
        self.links_listbox.pack(fill="x")
        self.links_listbox.bind("<Double-Button-1>", lambda _event: self.open_selected_link())

        links_buttons = tk.Frame(links_frame)
        links_buttons.pack(fill="x", pady=(6, 0))
        tk.Button(
            links_buttons, text="Open Selected", width=14, command=self.open_selected_link
        ).pack(side="left")
        tk.Button(
            links_buttons, text="Remove Selected", width=14, command=self.remove_selected_link
        ).pack(side="left", padx=(8, 0))

        for link in DEFAULT_STUDY_LINKS:
            self.links_listbox.insert(tk.END, link)

        self.refresh_exam_list()
        self.update_clock()
        self.schedule_next_reminder()

    def parse_exam_datetime(self, exam):
        start_dt = datetime.strptime(f"{exam['date']} {exam['start']}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{exam['date']} {exam['end']}", "%Y-%m-%d %H:%M")
        return start_dt, end_dt

    def refresh_exam_list(self):
        self.listbox.delete(0, tk.END)
        now = datetime.now()

        sorted_exams = sorted(EXAMS, key=lambda e: (e["date"], e["start"]))
        for exam in sorted_exams:
            start_dt, end_dt = self.parse_exam_datetime(exam)
            days_left = (start_dt.date() - now.date()).days
            if days_left > 1:
                countdown = f"in {days_left} days"
            elif days_left == 1:
                countdown = "tomorrow"
            elif days_left == 0:
                countdown = "today"
            else:
                countdown = "passed"

            line = (
                f"{start_dt.strftime('%a %b %d')}  "
                f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}  |  "
                f"{exam['course']}  |  {exam['location']}  |  {countdown}"
            )
            self.listbox.insert(tk.END, line)

    def update_clock(self):
        now_text = datetime.now().strftime("Current time: %A, %b %d, %Y - %I:%M:%S %p")
        self.now_label.config(text=now_text)
        self.refresh_exam_list()
        self.root.after(1000, self.update_clock)

    def show_reminder_popup(self):
        now = datetime.now()
        upcoming = []
        for exam in EXAMS:
            start_dt, _ = self.parse_exam_datetime(exam)
            if start_dt > now:
                upcoming.append((start_dt, exam["course"]))

        upcoming.sort(key=lambda x: x[0])
        next_exam = (
            f"Next: {upcoming[0][1]} on {upcoming[0][0].strftime('%a %b %d at %I:%M %p')}"
            if upcoming
            else "No upcoming exams found."
        )

        reminder_text = (
            "Time to study for finals.\n\n"
            "Stay consistent today.\n"
            "Even 30 focused minutes helps.\n\n"
            f"{next_exam}"
        )

        messagebox.showinfo("Study Reminder", reminder_text)

        if self.sms_enabled.get():
            self.send_sms_reminder(reminder_text.replace("\n\n", " | ").replace("\n", " "))

    def schedule_next_reminder(self):
        try:
            mins = max(1, int(self.reminder_interval_min.get()))
        except (ValueError, tk.TclError):
            mins = 45
            self.reminder_interval_min.set(mins)

        next_time = datetime.now() + timedelta(minutes=mins)
        self.status_label.config(
            text=f"Next reminder at {next_time.strftime('%I:%M %p')} (every {mins} min)"
        )

        self.root.after(mins * 60 * 1000, self.reminder_cycle)

    def reminder_cycle(self):
        self.show_reminder_popup()
        self.schedule_next_reminder()

    def add_link(self):
        raw = self.link_input_var.get().strip()
        if not raw:
            return

        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw

        self.links_listbox.insert(tk.END, raw)
        self.link_input_var.set("")

    def open_selected_link(self):
        selected = self.links_listbox.curselection()
        if not selected:
            messagebox.showinfo("Open Link", "Select a link first.")
            return
        url = self.links_listbox.get(selected[0])
        webbrowser.open(url)

    def remove_selected_link(self):
        selected = self.links_listbox.curselection()
        if not selected:
            return
        self.links_listbox.delete(selected[0])

    def send_sms_reminder(self, message_text: str):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
        to_number = os.getenv("TWILIO_TO_NUMBER", "").strip()

        if not all([account_sid, auth_token, from_number, to_number]):
            return

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        payload = parse.urlencode(
            {"From": from_number, "To": to_number, "Body": message_text[:1500]}
        ).encode("utf-8")
        req = request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        credentials = f"{account_sid}:{auth_token}".encode("utf-8")
        # Twilio expects HTTP Basic with base64 encoding.
        import base64

        req.add_header(
            "Authorization",
            f"Basic {base64.b64encode(credentials).decode('ascii')}",
        )

        try:
            with request.urlopen(req, timeout=12):
                pass
        except Exception:
            # Keep reminders non-blocking even when SMS fails.
            return


def main():
    root = tk.Tk()
    app = FinalsReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
