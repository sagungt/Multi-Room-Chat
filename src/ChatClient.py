import tkinter as tk
import socket
import errno
import sys
import threading
import json
from tkinter import messagebox
from ttkthemes import ThemedTk
from functools import partial
# TODO: Lanjut fix ui, export & restore, refactor, close window and server is all destroy function and message finalizing


class ClientWindow:

    def __init__(self):
        self.mainwindow = ThemedTk(theme='breeze')
        self.mainwindow.resizable(0, 0)
        self.address = tk.StringVar()
        self.port = tk.IntVar()
        self.username = tk.StringVar()
        self.room_var = tk.StringVar()
        self.address.set("127.0.0.1")
        self.port.set(5000)
        self.room_list = []
        self.is_join_room = False
        self.connection = None
        self.room = None
        self.title("ChatClient")
        self.__init()

    def title(self, title):
        self.mainwindow.title(title)

    def __init(self):
        # Frame Widgets
        self.__server_frame = tk.ttk.LabelFrame(
            self.mainwindow, text="Connection Info")
        self.__chat_frame = tk.ttk.LabelFrame(
            self.mainwindow, text="Chat Room")
        self.__input_frame = tk.ttk.Frame(self.mainwindow)
        # Frame Packing
        self.__server_frame.pack(side='top', fill='both', pady=(10, 0), padx=5)
        self.__chat_frame.pack(side='top', fill='both', padx=5, pady=5)
        self.__input_frame.pack(side='top', fill='both', pady=10, padx=10)
        # Widgets
        # Connection Form Widgets
        self.room_entry = tk.ttk.Entry(
            self.__server_frame, textvariable=self.room_var)
        self.address_label = tk.ttk.Label(
            self.__server_frame, text="Address")
        self.address_entry = tk.ttk.Entry(
            self.__server_frame, textvariable=self.address)
        self.port_label = tk.ttk.Label(
            self.__server_frame, text="Port")
        self.port_entry = tk.ttk.Entry(
            self.__server_frame, textvariable=self.port)
        self.connect_button = tk.ttk.Button(
            self.__server_frame, text="Connect", command=lambda: self.connecting(self.room_entry.get()))
        self.disconnect_button = tk.ttk.Button(
            self.__server_frame, text="Disconnect", command=self.disconnect)
        self.username_label = tk.ttk.Label(
            self.__server_frame, text="Username")
        self.username_entry = tk.ttk.Entry(
            self.__server_frame, textvariable=self.username)
        self.username_button_edit = tk.ttk.Button(
            self.__server_frame, text="Edit", state='disabled')
        self.room_label = tk.ttk.Label(
            self.__server_frame, text="Room")
        self.room_button_scan = tk.ttk.Button(
            self.__server_frame, text="Scan", command=self.request_room)
        # Chat Scrollframe Widget
        self.scrollframe = ScrollFrame(self.__chat_frame)
        # Message Form Widgets
        self.message_label = tk.ttk.Label(self.__input_frame, text="Message")
        self.message_text = tk.ttk.Entry(self.__input_frame, width=35)
        self.message_text.bind("<Return>", self.send)
        self.message_button = tk.ttk.Button(
            self.__input_frame, text="Send", command=self.send)
        ### Packing & Grid
        # Connection Form Grid
        self.address_label.grid(row=0, column=0)
        self.address_entry.grid(row=0, column=1)
        self.port_label.grid(row=1, column=0)
        self.port_entry.grid(row=1, column=1)
        self.connect_button.grid(
            row=0, column=2, rowspan=2, sticky="NSEW", padx=5)
        self.disconnect_button.grid(
            row=0, column=3, rowspan=2, sticky="NSEW", padx=5)
        self.username_label.grid(row=2, column=0)
        self.username_entry.grid(row=2, column=1)
        self.username_button_edit.grid(
            row=2, column=2, columnspan=2, sticky="NSEW", padx=5, pady=5)
        self.room_label.grid(row=3, column=0, pady=(0, 10))
        self.room_entry.grid(row=3, column=1, pady=(0, 10))
        self.room_button_scan.grid(
            row=3, column=2, columnspan=2, sticky="NSEW", padx=5, pady=(0, 10))
        # Chat Field Pack
        self.scrollframe.pack(side="top", fill="both", expand=True)
        # Message Widget Grid
        self.message_label.grid(row=0, column=0, sticky="NSEW")
        self.message_text.grid(row=0, column=1, sticky="NSEW")
        self.message_button.grid(row=0, column=2, sticky="NSEW", padx=(10, 2))

    def connecting(self, room=None):
        try:
            username = bool(self.username_entry.get())
            if username:
                self.connection = ConnectServer(username=self.username_entry.get(
                ), address=(self.address_entry.get(), int(self.port_entry.get())), room=room)
                self.connection.connect()
                self.connected()
                self.title(room)
                self.username_button_edit.config(state='normal')
                self.username_entry.config(state='disabled')
                self.room_button_scan.config(state='disabled')
                self.room_entry.delete(0, 'end')
                self.room_entry.insert(0, room)
                self.room_entry.config(state='disabled')
            else:
                messagebox.showwarning(
                    "Warning", "Please fill username field.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def connected(self):
        try:
            self.room = threading.Thread(
                target=self.connection.receive_message, kwargs={'window': self, })
            self.room.start()
        except:
            messagebox.showerror('error', 'Failed')

    def disconnect(self):
        if self.connection != None:
            self.connection.disconnect()
            self.connection = None
            self.room = None
            messagebox.showinfo("Success", "Disconnected from server.")
            self.address_entry.configure(state='normal')
            self.port_entry.configure(state='normal')
            self.connect_button.configure(
                state='normal', text='Connect')
            self.username_entry.config(state='normal')
            self.username_button_edit.config(state='disabled')
            self.room_entry.config(state='normal')
            self.room_button_scan.config(state='normal')
        else:
            messagebox.showinfo("Info", "Connect to a Server First.")

    def send(self, event=None):
        try:
            message = self.message_text.get()
            data = {'type': 'message',
                    'username': self.username_entry.get(),
                    'room': self.room_entry.get(),
                    'message': message}
            if message:
                self.connection.send_message(data)
                self.message_text.delete(0, 'end')
                self.insert(json.dumps(data), 'e')
        except:
            messagebox.showerror("Error", "Please connect to server and room.")

    def insert(self, text, anchor):
        data = json.loads(text)
        if data['type'] == 'message':
            f = tk.Frame(self.scrollframe.viewPort, width=25,
                         highlightbackground='#3daee9', highlightthickness=1)
            f.pack(fill='x', side='top', expand=True, padx=5, pady=5)
            tk.ttk.Label(f, text=data['username'], anchor=anchor, font=(
                'helvetica', 7)).pack(fill='x')
            tk.ttk.Label(f, text='  '+data['message'],
                         anchor=anchor).pack(fill='x')
            self.scrollframe.canvas.yview_moveto(1)
        elif data['type'] == 'respond_room':
            for room in data['rooms']:
                self.room_list.append(tk.ttk.Button(
                    self.scrollframe.viewPort, text=room, command=partial(self.connecting, room)))
            for room in self.room_list:
                room.pack()
            if self.is_join_room is False:
                self.connection.disconnect()
                self.connection = None
        elif data['type'] == 'error':
            messagebox.showerror('error', data['message'])
            self.connection.disconnect()
        elif data['type'] == 'success':
            self.clear()
            if self.room_list:
                for room in self.room_list:
                    room.pack_forget()
                self.room_list = []
            f = tk.Frame(self.scrollframe.viewPort, width=25,
                         highlightbackground='#3daee9', highlightthickness=1)
            f.pack(fill='x', side='top', expand=True, padx=5, pady=5)
            tk.ttk.Label(f, text=data['message'],
                         anchor='n').pack(fill='x')
            self.scrollframe.canvas.yview_moveto(1)
            self.is_join_room = True
            self.address_entry.configure(state='disabled')
            self.port_entry.configure(state='disabled')
            self.connect_button.configure(
                state='disabled', text='Connected')

    def request_room(self):
        try:
            data = {'type': 'request_room',
                    'username': self.username_entry.get()}
            if self.room_list:
                for x in self.room_list:
                    x.pack_forget()
                self.room_list = []
            if self.connection == None:
                self.connection = ConnectServer()
                self.connection.connect_socket.connect(
                    (self.address_entry.get(), int(self.port_entry.get())))
                self.connection.is_connect = True
                self.connected()
                self.connection.send_message(data)
            else:
                self.connection.send_message(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.connection.disconnect()
            self.connection = None

    def clear(self):
        for widget in self.scrollframe.viewPort.winfo_children():
            widget.destroy()

    def sync(self):
        pass


class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, borderwidth=0, width=400, height=300)
        self.viewPort = tk.Frame(self.canvas)
        self.vsb = tk.ttk.Scrollbar(self, orient="vertical",
                                    command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.bind_all(
            "<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120), 'units'))
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window(
            (4, 4), window=self.viewPort, anchor="nw", tags="self.viewPort")
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        self.onFrameConfigure(None)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox(
            "all"))

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)


class ConnectServer:

    def __init__(self, username=None, address=(), room=None):
        self.HEADER = 8
        self.address = address
        self.username = username
        self.room = room
        self.connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connect = False

    def connect(self):
        self.connect_socket.connect(self.address)
        self.is_connect = True
        data = {'type': 'initialize',
                'username': self.username,
                'room': self.room}
        self.send_message(data)

    def disconnect(self):
        self.is_connect = False
        self.connect_socket.close()

    def receive_message(self, window):
        while self.is_connect:
            try:
                while True:
                    header = self.connect_socket.recv(self.HEADER)
                    print(header)
                    if not len(header):
                        # messagebox.showwarning(
                        #     "Warning", "Connection closed by server")
                        sys.exit()
                    data_length = int(
                        header.decode('utf-8').strip())
                    data = self.connect_socket.recv(
                        data_length).decode('utf-8')
                    window.insert(data, 'w')
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    sys.exit()
                continue
            except Exception as e:
                sys.exit()
        return True

    def send_message(self, message):
        serialize_message = json.dumps(message).encode('utf-8')
        message_header = f"{len(serialize_message):<{self.HEADER}}".encode(
            'utf-8')
        self.connect_socket.send(message_header + serialize_message)


x = ClientWindow()
x.mainwindow.mainloop()
