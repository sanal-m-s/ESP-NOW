# pip install pyserial

import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import font as tkfont
import serial
import serial.tools.list_ports
import threading
from datetime import datetime

# ---------- Colors & Fonts ----------
BG_COLOR = "#1e1e2f"
HEADER_COLOR = "#27293d"
CHAT_BG = "#2b2d42"
SENT_BG = "#4361ee"
RECV_BG = "#3a3f58"
SYSTEM_COLOR = "#8d99ae"
TEXT_COLOR = "#ffffff"
ENTRY_BG = "#2b2d42"
BTN_COLOR = "#4361ee"
BTN_HOVER = "#3a56d4"


class ESPChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP-NOW Chat")
        self.root.geometry("420x600")
        self.root.configure(bg=BG_COLOR)
        self.ser = None

        self.font_normal = tkfont.Font(family="Segoe UI", size=10)
        self.font_bold = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=8)

        # ---------- Header ----------
        header = tk.Frame(root, bg=HEADER_COLOR, height=70)
        header.pack(fill=tk.X)

        title_label = tk.Label(header, text="📡 ESP-NOW Chat", bg=HEADER_COLOR,
                                fg=TEXT_COLOR, font=("Segoe UI", 14, "bold"))
        title_label.pack(side=tk.LEFT, padx=15, pady=15)

        self.status_label = tk.Label(header, text="● Disconnected", bg=HEADER_COLOR,
                                      fg="#e63946", font=self.font_small)
        self.status_label.pack(side=tk.RIGHT, padx=15)

        # ---------- Connection Bar ----------
        conn_frame = tk.Frame(root, bg=BG_COLOR)
        conn_frame.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(conn_frame, text="Port:", bg=BG_COLOR, fg=TEXT_COLOR,
                 font=self.font_normal).pack(side=tk.LEFT, padx=(0, 5))

        self.port_var = tk.StringVar()
        self.port_menu = tk.OptionMenu(conn_frame, self.port_var, "")
        self.port_menu.config(bg=ENTRY_BG, fg=TEXT_COLOR, activebackground=BTN_HOVER,
                               highlightthickness=0, font=self.font_normal, width=10)
        self.port_menu["menu"].config(bg=ENTRY_BG, fg=TEXT_COLOR)
        self.port_menu.pack(side=tk.LEFT, padx=5)

        self.refresh_ports()

        self.connect_btn = self.make_button(conn_frame, "Connect", self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = self.make_button(conn_frame, "⟳", self.refresh_ports, width=3)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # ---------- Chat Area ----------
        chat_container = tk.Frame(root, bg=CHAT_BG)
        chat_container.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.chat_canvas = tk.Canvas(chat_container, bg=CHAT_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(chat_container, orient="vertical",
                                       command=self.chat_canvas.yview)
        self.chat_frame = tk.Frame(self.chat_canvas, bg=CHAT_BG)

        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=380)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ---------- Input Bar ----------
        input_frame = tk.Frame(root, bg=BG_COLOR)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.msg_entry = tk.Entry(input_frame, bg=ENTRY_BG, fg=TEXT_COLOR,
                                   insertbackground=TEXT_COLOR, font=self.font_normal,
                                   relief=tk.FLAT)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = self.make_button(input_frame, "Send ➤", self.send_message, width=8)
        self.send_btn.pack(side=tk.RIGHT)

    # ---------- Helper: styled button ----------
    def make_button(self, parent, text, command, width=10):
        btn = tk.Button(parent, text=text, command=command,
                         bg=BTN_COLOR, fg=TEXT_COLOR, activebackground=BTN_HOVER,
                         font=self.font_normal, relief=tk.FLAT, width=width,
                         cursor="hand2", bd=0, padx=6, pady=6)
        return btn

    # ---------- Port handling ----------
    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_menu['menu'].delete(0, 'end')
        for p in ports:
            self.port_menu['menu'].add_command(
                label=p, command=lambda value=p: self.port_var.set(value))
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("No ports")

    def connect(self):
        port = self.port_var.get()
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.status_label.config(text="● Connected", fg="#06d6a0")
            self.connect_btn.config(text="Connected", state=tk.DISABLED, bg="#06d6a0")
            self.add_system_message(f"Connected to {port}")
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def read_serial(self):
        while self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.startswith("Received:"):
                        msg = line.replace("Received:", "").strip()
                        self.root.after(0, self.add_bubble, msg, "received")
                    else:
                        self.root.after(0, self.add_system_message, line)
            except Exception:
                break

    # ---------- Sending ----------
    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.ser and self.ser.is_open:
            self.ser.write((msg + "\n").encode('utf-8'))
            self.add_bubble(msg, "sent")
            self.msg_entry.delete(0, tk.END)
        elif not self.ser:
            messagebox.showwarning("Not Connected", "Please connect to a COM port first.")

    # ---------- Chat bubble rendering ----------
    def add_bubble(self, msg, msg_type):
        bubble_frame = tk.Frame(self.chat_frame, bg=CHAT_BG)
        bubble_frame.pack(fill=tk.X, pady=4, padx=8,
                           anchor="e" if msg_type == "sent" else "w")

        bg_color = SENT_BG if msg_type == "sent" else RECV_BG
        anchor_side = "e" if msg_type == "sent" else "w"

        bubble = tk.Label(bubble_frame, text=msg, bg=bg_color, fg=TEXT_COLOR,
                           font=self.font_normal, wraplength=240, justify=tk.LEFT,
                           padx=12, pady=8)
        bubble.pack(side=tk.RIGHT if msg_type == "sent" else tk.LEFT)

        timestamp = datetime.now().strftime("%H:%M")
        time_label = tk.Label(bubble_frame, text=timestamp, bg=CHAT_BG,
                               fg=SYSTEM_COLOR, font=self.font_small)
        time_label.pack(side=tk.RIGHT if msg_type == "sent" else tk.LEFT, padx=4)

        self.scroll_to_bottom()

    def add_system_message(self, msg):
        label = tk.Label(self.chat_frame, text=msg, bg=CHAT_BG, fg=SYSTEM_COLOR,
                          font=self.font_small)
        label.pack(pady=4)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.chat_frame.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)


if __name__ == "__main__":
    root = tk.Tk()
    app = ESPChatApp(root)
    root.mainloop()
