import tkinter as tk
import socket
import datetime
import select
import threading
import json
from tkinter import messagebox
from ttkthemes import ThemedTk
import sys
import os
import pickle
import _pickle as cPickle
import bz2


class ServerWindow:

    def __init__(self):
        self.mainwindow = ThemedTk(theme='breeze')
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.close)
        self.address = tk.StringVar()
        self.port = tk.IntVar()
        self.room_name = tk.StringVar()
        self.address.set("127.0.0.1")
        self.port.set(5000)
        self.room_name.set("Chat Room")
        self.status = {'server': tk.StringVar(value="Incative"),
                       'conn': tk.StringVar(value='0 Connection(s)'),
                       'rooms': tk.StringVar(value='0 Room(s)'),
                       'verbose': tk.BooleanVar()}
        self.rooms = []
        self.is_update = True
        self.__init()
        self.restore()

    def title(self):
        self.mainwindow.title(self.room_entry.get())

    def start(self):
        self.title()
        self.mainwindow.mainloop()

    def __init(self):
        # Frame widgets
        self.__frame = tk.ttk.LabelFrame(self.mainwindow, text='Server Info')
        self.__frame.pack(side="top", padx=5, pady=5, fill='both', expand=True)
        self.__room_frame = tk.ttk.LabelFrame(
            self.mainwindow, text='Room List')
        self.__room_frame.pack(side='top', pady=(
            0, 5), padx=5, fill='both', expand=True)
        self.__status_frame = tk.ttk.LabelFrame(self.mainwindow, text='Status')
        self.__status_frame.pack(side='top', fill='x',
                                 padx=5, pady=(0, 5), expand=True)
        self.__verbose_frame = tk.ttk.LabelFrame(
            self.mainwindow, text='Verbose')
        # self.__verbose_frame.pack(side='top', padx=(
        #     0, 5), pady=5, fill='both', expand=True)
        # Chat Window
        self.verbose_window = tk.Text(
            self.__verbose_frame, width=60, height=10)
        self.scrollframe = ScrollFrame(self.__room_frame)
        # Status widgets
        tk.ttk.Label(self.__status_frame, text="Server").grid(
            row=0, column=0, sticky="W")
        tk.ttk.Label(self.__status_frame, text="Active Connection").grid(
            row=1, column=0, sticky="W")
        tk.ttk.Label(self.__status_frame, text="Rooms").grid(
            row=2, column=0, sticky="W")
        self.__status_label_server = tk.ttk.Label(
            self.__status_frame, textvariable=self.status['server'])
        self.__status_label_conn = tk.ttk.Label(
            self.__status_frame, textvariable=self.status['conn'])
        self.__status_label_rooms = tk.ttk.Label(
            self.__status_frame, textvariable=self.status['rooms'])
        self.__verbose_toggle = tk.ttk.Checkbutton(
            self.__status_frame, text='Verbose', variable=self.status['verbose'], command=self.toggle_verbose)
        # Connection Form widgets
        self.addr_label = tk.ttk.Label(self.__frame, text="Bind Address")
        self.addr_entry = tk.ttk.Entry(self.__frame, textvariable=self.address)
        self.port_label = tk.ttk.Label(self.__frame, text="Port")
        self.port_entry = tk.ttk.Entry(self.__frame, textvariable=self.port)
        self.room_label = tk.ttk.Label(self.__frame, text="Room Name")
        self.room_entry = tk.ttk.Entry(
            self.__frame, textvariable=self.room_name)
        self.listen_button = tk.ttk.Button(
            self.__frame, text="\u23f5 Listen", command=self.listen)
        self.stop_button = tk.ttk.Button(
            self.__frame, text="\u23f9 Stop", command=self.stop)
        self.room_button = tk.ttk.Button(
            self.__frame, text="Create", command=self.create_room)
        # Packing & grid widgets
        self.addr_label.grid(row=0, column=0, sticky="w")
        self.addr_entry.grid(row=0, column=1)
        self.port_label.grid(row=1, column=0, sticky="w")
        self.port_entry.grid(row=1, column=1)
        self.listen_button.grid(
            row=0, column=2, rowspan=2, sticky="NSEW", padx=2, pady=2)
        self.stop_button.grid(row=0, column=3, rowspan=2,
                              sticky="NSEW", padx=2, pady=2)
        self.room_label.grid(row=2, column=0)
        self.room_entry.grid(row=2, column=1)
        self.room_button.grid(
            row=2, column=2, columnspan=2, padx=2, pady=5, sticky="NSEW")
        self.scrollframe.pack()
        self.__status_label_server.grid(row=0, column=1, padx=5, sticky="w")
        self.__status_label_conn.grid(row=1, column=1, padx=5, sticky="w")
        self.__status_label_rooms.grid(
            row=2, column=1, padx=5, sticky="w", pady=(0, 5))
        self.__verbose_toggle.grid(row=0, column=2, rowspan=3, sticky='e')
        # self.verbose_window.pack(fill='both', expand=True)

    def insert(self, text):
        if self.verbose_window:
            self.verbose_window.insert("end", text + "\n")
            self.verbose_window.see('end')

    def save_room(self):
        self.title()

    def create_room(self, room=None):
        room_name = room if room is not None else self.room_entry.get()
        if any(room['name'] == room_name for room in self.rooms):
            messagebox.showwarning("Warning", "Room already exist.")
        elif len(room_name) not in range(3, 11, 1):
            messagebox.showwarning(
                "Warning", "Room name must 3 to 10 character.")
        else:
            row = len(self.rooms)
            self.rooms.append({'name': room_name,
                               'connections_var': tk.StringVar(value='Connection(s) : 0'),
                               #    'connections': 0,
                               #    'clients': [],
                               'frame': [tk.Frame(self.scrollframe.viewPort, highlightbackground='black', highlightthickness=1)],
                               'data': []})
            self.rooms[row]['frame'].append(
                tk.ttk.Frame(self.rooms[row]['frame'][0]))
            self.rooms[row]['frame'].append(
                tk.ttk.Frame(self.rooms[row]['frame'][0]))

            for i, frame in enumerate(self.rooms[row]['frame']):
                if i == 0:
                    frame.pack(fill='both', expand=1,
                               padx=(5, 2), pady=(0, 5))
                elif i == 1:
                    frame.pack(side='left', pady=(5, 10))
                else:
                    frame.pack(side='right', pady=(5, 10))
            self.rooms[row]['widgets'] = {
                'label_name': tk.ttk.Label(self.rooms[row]['frame'][1], text=room_name),
                'label_connection': tk.ttk.Label(self.rooms[row]['frame'][1], textvariable=self.rooms[row]['connections_var']),
                # 'enable': CustomButton(self.rooms[row]['frame'][2], text='\u23f5', width=40, height=30),
                # 'disable': CustomButton(self.rooms[row]['frame'][2], text='\u23f9', width=40, height=30, state='disabled'),
                'chat': CustomButton(self.rooms[row]['frame'][2], text='\u2338', width=40, height=30),
                'delete': CustomButton(self.rooms[row]['frame'][2], text='\u26a0', width=50, height=30),
            }
            self.rooms[row]['tips'] = {
                # 'enable_tip': ToolTip(self.rooms[row]['widgets']['enable'], 'Enable'),
                # 'disable_tip': ToolTip(self.rooms[row]['widgets']['disable'], 'Disable'),
                'chat_tip': ToolTip(self.rooms[row]['widgets']['chat'], 'Chat Window'),
                'delete_tip': ToolTip(self.rooms[row]['widgets']['delete'], 'Delete'),
            }
            for widget in self.rooms[row]['widgets']:
                if widget == 'label_connection' or widget == 'label_name':
                    self.rooms[row]['widgets'][widget].pack(side='top')
                elif widget == 'delete':
                    self.rooms[row]['widgets'][widget].pack(
                        side='left', padx=(0, 10))
                else:
                    self.rooms[row]['widgets'][widget].pack(side='left')
            self.status['rooms'].set(f'{len(self.rooms)} Room(s)')

    def get_address(self):
        return (self.address.get(), int(self.port_entry.get()))

    def listen(self):
        try:
            self.listen_server()
        except socket.error as e:
            self.insert(str(e))

    def listen_server(self):
        address = self.get_address()
        self.server = CreateServer(address)
        self.server.listen()
        self.status['server'].set(f"Listening")
        self.start_server(self.server)

    def start_server(self, server):
        self.room = HandleRooms(
            socket=self.server, window=self, name=self.room_entry.get())
        self.room.start()

    def stop(self):
        try:
            self.store()
            self.server.stop()
            self.is_update = False
            self.status['server'].set("Inactive")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def close(self):
        try:
            self.server.stop()
            self.mainwindow.destroy()
        except:
            self.mainwindow.destroy()

    def store(self):
        now = datetime.datetime.now()
        filename = f'{now.date()}'
        data = [{key: value for key, value in room.items() if key == 'name' or key == 'data'}
                for room in self.rooms]
        if self.rooms:
            with bz2.BZ2File(filename+'.pbz2', 'w') as file:
                cPickle.dump(data, file)
        else:
            pass

    def restore(self):
        filename = os.listdir()
        # print(filename)
        if 'pbz2' in [ext.split('.')[-1] for ext in filename]:
            file, = [f for f in filename if '.pbz2' in f]
            # print(file)
            data = bz2.BZ2File(file, 'rb')
            data = cPickle.load(data)
            # print(data)
            [self.create_room(room['name']) for room in data]
        else:
            pass

    def toggle_verbose(self):
        state = self.status['verbose'].get()
        if state:
            self.__verbose_frame.pack(side='top', padx=(
                0, 5), pady=5, fill='both', expand=True)
            self.verbose_window.pack(fill='both', expand=True)
        else:
            self.__verbose_frame.pack_forget()
            self.verbose_window.pack_forget()


class HandleRooms(threading.Thread):

    HEADER = 8

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, socket=None, window=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.socket = socket
        self.window = window
        return

    def run(self):
        def send_all(sock, data):
            serialize_data = json.dumps(data)
            header = f"{len(serialize_data):<{self.HEADER}}".encode(
                'utf-8')
            sock.send(header + serialize_data.encode('utf-8'))

        def chage_status(client, user_room, conn):
            self.window.status['conn'].set(
                f"{len(client)} Connection(s)")
            room_connection, = [
                room for room in self.window.rooms if room['name'] == user_room]
            room_connection['connections_var'].set(
                f"Connection(s) : {conn}")
        self.window.insert("Server is starting ...\n{}:{}".format(
            self.socket.address, self.socket.port))
        try:
            socket_lists = {self.socket.server: 'server'}
            client_lists = {}
            while self.socket.is_listen:
                read_sockets, _, exception_sockets = select.select(
                    list(socket_lists.keys()), [], list(socket_lists.keys()))
                for notified_socket in read_sockets:
                    if notified_socket == self.socket.server:
                        client_socket, client_address = self.socket.server.accept()
                        user = self.socket.receive_message(client_socket)
                        if user is False:
                            continue
                        elif user['data']['type'] == 'request_room':
                            data = {'type': 'respond_room',
                                    'rooms': [room['name'] for room in self.window.rooms]}
                            send_all(client_socket, data)
                        elif user['data']['type'] == 'initialize':
                            if any(x['name'] == user['data']['room'] for x in self.window.rooms):
                                socket_lists[client_socket] = user['data']['room']
                                client_lists[client_socket] = user
                                self.window.status['conn'].set(
                                    f"{len(client_lists)} Connection(s)")
                                room_connection, = [
                                    room for room in self.window.rooms if room['name'] == user['data']['room']]
                                room_connection['connections_var'].set(
                                    f"Connection(s) : {list(socket_lists.values()).count(user['data']['room'])}")
                                self.window.insert("Accepted new connection from {}:{}, username: {}, room: {}".format(
                                    *client_address, user["data"]['username'], user['data']['room']))
                                data = {'type': 'success',
                                        'message': f"Connected to {user['data']['room']}"}
                                send_all(client_socket, data)
                            else:
                                data = {'type': 'error',
                                        'message': "Room not available"}
                                send_all(client_socket, data)
                        elif user['data']['type'] == 'sync':
                            data = {'type': 'ack'}
                            send_all(client_socket, data)
                    else:
                        message = self.socket.receive_message(notified_socket)
                        if message is False:
                            try:
                                self.window.insert("Closed Connection From: {}, room: {}".format(
                                    client_lists[notified_socket]['data']['username'], client_lists[notified_socket]['data']['room']))
                                del socket_lists[notified_socket]
                                del client_lists[notified_socket]
                                chage_status(len(client_lists),
                                             user['data']['room'],
                                             list(socket_lists.values()).count(user['data']['room']))
                            except:
                                continue
                        elif message['data']['type'] != 'initialize':
                            user = client_lists[notified_socket]
                            if message['data']['type'] == 'message':
                                self.window.insert(
                                    f"Received message from {user['data']['username']}: {message['data']['message']}")
                                # print(message)
                                for room in self.window.rooms:
                                    if room['name'] == message['data']['room']:
                                        room['data'].append(
                                            {'username': user['data']['username'], 'message': message['data']['message']})
                                # print(room['data'])
                            send_list = {k: v for k, v in client_lists.items(
                            ) if v['data']['room'] == socket_lists[notified_socket]}
                            for client_socket in send_list:
                                if message['data']['type'] == 'message':
                                    if client_socket != notified_socket:
                                        data = {'type': 'message',
                                                'username': user['data']['username'],
                                                'message': message['data']['message']}
                                        send_all(client_socket, data)
                            if message['data']['type'] == 'request_room':
                                send_list_room = {k: v for k, v in client_lists.items(
                                ) if v['data']['username'] == message['data']['username']}
                                for send_room in send_list_room:
                                    data = {'type': 'respond_room',
                                            'rooms': [room['name'] for room in self.window.rooms]}
                                    send_all(send_room, data)
                for notified_socket in exception_sockets:
                    del socket_lists[notified_socket]
                    del client_lists[notified_socket]
            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.window.insert(str(e))
            self.window.insert("Server closed ...")
            return True


class CustomButton(tk.ttk.Frame):
    def __init__(self, parent, height=None, width=None, text='', command=None, style=None, state='normal'):
        tk.ttk.Frame.__init__(self, parent, height=height,
                              width=width, style='MyButton.TFrame')
        self.pack_propagate(0)
        self.btn = tk.ttk.Button(
            self, text=text, command=command, style=style, state=state)
        self.btn.pack(fill='both', expand=1)


class ToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.close)

    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f'+{x}+{y}')
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background='white', relief='solid', borderwidth=1,
                         font=("times", "8", "normal"))
        label.pack()

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()


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


class CreateServer:

    def __init__(self, address=()):
        self.FORMAT = "utf-8"
        self.HEADER = 8
        self.address = address[0]
        self.port = address[1]
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_listen = False
        self.socket_list = [self.server]
        self.clients = {}

    def listen(self):
        self.is_listen = True

        try:
            self.server.bind((self.address, self.port))
        except socket.error as e:
            str(e)

        self.server.listen()

    def stop(self):
        self.is_listen = False
        self.server.close()

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER)
            if not len(message_header):
                return False

            message_length = int(message_header.decode('utf-8').strip())
            data = json.loads(client_socket.recv(
                message_length).decode('utf-8'))
            return {'header': message_length, 'data': data}
        except:
            return False

    def handle_clients(self, window):
        window.insert("Server is starting ...\n{}:{}".format(
            self.address, self.port))
        try:
            while self.is_listen:
                read_sockets, _, exception_sockets = select.select(
                    self.socket_list, [], self.socket_list)
                for notified_socket in read_sockets:
                    if notified_socket == self.server:
                        client_socket, client_address = self.server.accept()
                        user = self.receive_message(client_socket)
                        if user is False:
                            continue
                        self.socket_list.append(client_socket)
                        self.clients[client_socket] = user
                        window.insert("Accepted new connection from {}:{}, username: {}".format(
                            *client_address, user["data"].decode("utf-8")))
                    else:
                        message = self.receive_message(notified_socket)
                        if message is False:
                            window.insert("Closed Connection From: {}".format(
                                self.clients[notified_socket]['data'].decode("utf-8")))
                            self.socket_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue
                        user = self.clients[notified_socket]
                        window.insert(
                            f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                        for client_socket in self.clients:
                            if client_socket != notified_socket:
                                client_socket.send(
                                    user['header'] + user['data'] + message['header'] + message['data'])
                for notified_socket in exception_sockets:
                    self.socket_list.remove(notified_socket)
                    del self.clients[notified_socket]
            return True
        except Exception as e:
            window.insert("Server closed ...")
            return True


x = ServerWindow()
x.start()
x.mainwindow.mainloop()
