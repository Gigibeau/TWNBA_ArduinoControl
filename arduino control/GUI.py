# Importing Libraries
import serial
from tkinter import *  # NOQA
import time
from tkinter import ttk
from tkinter import filedialog
import pickle
import threading

''' ==== Arduino communication ==== '''

# Establish connection to the Arduino
global arduino
port = '/dev/cu.usbmodem142401'
baudrate = 9600
timeout = 0.1
# arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

# Function that communicates with the Arduino
startMarker = "<"
endMarker = ">"
dataStarted = False
dataBuf = ""
messageComplete = False


def write_read(x):
    send_to_arduino(x)
    while True:
        arduino_reply = recv_from_arduino()
        if not (arduino_reply == 'XXX'):
            rec_list = arduino_reply.split(";")
            xposition.set(rec_list[0])
            yposition.set(rec_list[1])
            return rec_list[2]
            # break


def send_to_arduino(string_to_send):
    global arduino

    arduino.write(bytes(string_to_send, 'utf-8'))  # encode needed for Python3


def recv_from_arduino():
    global startMarker, endMarker, arduino, dataStarted, dataBuf, messageComplete

    if arduino.inWaiting() > 0 and messageComplete == False:
        y = arduino.read().decode("utf-8")  # decode needed for Python3

        if dataStarted:
            if y != endMarker:
                dataBuf = dataBuf + y
            else:
                dataStarted = False
                messageComplete = True
        elif y == startMarker:
            dataBuf = ''
            dataStarted = True

    if messageComplete:
        messageComplete = False
        return dataBuf
    else:
        return "XXX"


''' ==== GUI ==== '''

root = Tk()


# Functions
def on_press(direction):
    send_to_arduino(direction)
    # log(received)


def on_release():
    send_to_arduino("f")
    # log(received)


def log(message):
    now = time.strftime("%I:%M:%S", time.localtime())
    text.insert("end", now + " " + message.strip() + "\n")
    text.see("end")


def write_read_gui(x):
    received = write_read(x)
    log(received)


def some_callback(event):  # to delete the preset text once clicked
    event.widget.delete(0, "end")
    return None


''' ==== Manual Mode ==== '''

mmlabelframe = LabelFrame(root, text='Manual Mode', width=450, height=50)
mmlabelframe.grid(row=0, column=0, columnspan=4, rowspan=3)

# Placement of the buttons
entry_speed = Entry(mmlabelframe, width=5)
entry_speed.insert(5, '[1-5]')
entry_speed.grid(row=0, column=1, padx=2, pady=2)
entry_speed.bind("<Button-1>", some_callback)

button_setspeed = Button(mmlabelframe, text='Set Speed', state=DISABLED,
                         command=lambda: write_read_gui("<1, " + entry_speed.get() + ", " + entry_speed.get() + ">"))
button_setspeed.grid(row=0, column=2, padx=0, pady=0)

button_up = Button(mmlabelframe, text="\u2191", state=DISABLED, height=3, width=3)
button_up.grid(row=1, column=2, padx=0, pady=0)

button_down = Button(mmlabelframe, text="\u2193", state=DISABLED, height=3, width=3)
button_down.grid(row=3, column=2, padx=0, pady=0)

button_left = Button(mmlabelframe, text="\u2190", state=DISABLED, height=3, width=3)
button_left.grid(row=2, column=1, padx=0, pady=0)

button_right = Button(mmlabelframe, text="\u2192", state=DISABLED, height=3, width=3)
button_right.grid(row=2, column=3, padx=0, pady=0)

button_enter = Button(mmlabelframe, text='Enter', state=DISABLED,
                      command=lambda: [write_read_gui("<8, 0, 0>"), enter_mm()])
button_enter.grid(row=4, column=1, padx=0, pady=0)

button_exit = Button(mmlabelframe, text='Exit', state=DISABLED, command=lambda: [write_read_gui("e"), exit_mm()])
button_exit.grid(row=4, column=3, padx=0, pady=0)

# Defining the outcome of a press/release
button_up.bind("<ButtonPress>", lambda x: on_press("w"))
button_up.bind("<ButtonRelease>", lambda x: on_release())
button_down.bind("<ButtonPress>", lambda x: on_press("s"))
button_down.bind("<ButtonRelease>", lambda x: on_release())
button_left.bind("<ButtonPress>", lambda x: on_press("a"))
button_left.bind("<ButtonRelease>", lambda x: on_release())
button_right.bind("<ButtonPress>", lambda x: on_press("d"))
button_right.bind("<ButtonRelease>", lambda x: on_release())

''' ==== LOG ==== '''

# Placement of the log
text = Text(root, width=80, height=10)
vsb = Scrollbar(root, command=text.yview)
text.configure(yscrollcommand=vsb.set)
vsb.grid(row=12, column=10)
text.grid(row=12, column=0, columnspan=10)

''' ==== Recipe User Interface ==== '''

# Placement of the buttons
button_setorigin = Button(root, text='Set Origin', state=DISABLED, command=lambda: write_read_gui("<5, 0, 0>"))
button_setorigin.grid(row=3, column=4, columnspan=2, padx=10, pady=5)

# Display for the current position
xposition = StringVar()
xposition.set("0")
yposition = StringVar()
yposition.set("0")

positionlabel = Label(root, text="Current position:", font=("Bold", 20))
positionlabel.grid(row=0, column=4, columnspan=2)

xtext = Label(root, text="x-position")
xtext.grid(row=1, column=4)
ytext = Label(root, text="y-position")
ytext.grid(row=1, column=5)

xlabel = Label(root, textvariable=xposition, bg="white", font=("Bold", 10))
xlabel.grid(row=2, column=4)
ylabel = Label(root, textvariable=yposition, bg="white", font=("Bold", 10))
ylabel.grid(row=2, column=5)


# Recipe input
class Command:
    def __init__(self, row, column):
        self.column = column
        self.options = ["Up", "Down", "Left",
                        "Right", "Sleep"]
        self.Combo = ttk.Combobox(root, values=self.options)
        self.Combo.set("Pick an Option")
        self.Combo.grid(row=row, column=column, padx=2, pady=2)

        self.input_distance = Entry(root, width=15)
        self.input_distance.insert(0, '[mm] or [min]')
        self.input_distance.grid(row=row, column=column + 1, padx=2, pady=2)
        self.input_distance.bind("<Button-1>", some_callback)

        self.input_speed = Entry(root, width=15)
        self.input_speed.insert(0, '[1-5] or [sec]')
        self.input_speed.grid(row=row, column=column + 2, padx=2, pady=2)
        self.input_speed.bind("<Button-1>", some_callback)

        self.button_exec = Button(root, text='Execute', state=DISABLED,
                                  command=lambda: threading.Thread(target=self.exec_line(self.Combo.get())).start())
        self.button_exec.grid(row=row, column=column + 3, padx=2, pady=2)

    def exec_line(self, function):
        if function == "Up":
            write_read_gui("<4, " + self.input_distance.get() + ", " + self.input_speed.get() + ">")

        if function == "Down":
            write_read_gui("<4, -" + self.input_distance.get() + ", " + self.input_speed.get() + ">")

        if function == "Left":
            write_read_gui("<3, -" + self.input_distance.get() + ", " + self.input_speed.get() + ">")

        if function == "Right":
            write_read_gui("<3, " + self.input_distance.get() + ", " + self.input_speed.get() + ">")

        if function == "Sleep":
            duration = 0
            try:
                duration = int(self.input_speed.get())
            except ValueError:
                pass

            try:
                duration = duration + (int(self.input_distance.get()) * 60)
            except ValueError:
                pass

            time.sleep(duration)
            log("slept for " + str(duration) + " seconds")


label_distance = Label(root, text='Distance/Minutes')
label_distance.grid(row=4, column=4)
label_speed = Label(root, text='Speed/Seconds')
label_speed.grid(row=4, column=5)

line_1 = Command(5, 3)
line_2 = Command(6, 3)
line_3 = Command(7, 3)
line_4 = Command(8, 3)
line_5 = Command(9, 3)
line_6 = Command(10, 3)

lines_to_exec = [line_1, line_2, line_3, line_4, line_5, line_6]
button_exec_all = Button(root, text="Execute All", state=DISABLED,
                         command=lambda: threading.Thread(target=exec_all).start())
button_exec_all.grid(row=3, column=6, columnspan=2)


def exec_all():
    for entry_line in lines_to_exec:
        entry_line.exec_line(entry_line.Combo.get())


button_stop = Button(root, text='Stop', state=DISABLED, bg='red', command=lambda: stop())
button_stop.grid(row=11, column=4)


def stop():
    send_to_arduino('9')


''' ==== Saving and Loading entries ==== '''

# Adding the save and load buttons
button_save = Button(root, text="\U0001f4be", state=DISABLED, command=lambda: save_files())
button_save.grid(row=11, column=5)

button_open = Button(root, text="\U0001F4C2", state=DISABLED, command=lambda: open_files())
button_open.grid(row=11, column=6)


# Saving the current entries and combos

def save_files():
    file_name = filedialog.asksaveasfilename(
        title="Save File",
        filetypes=(("Dat Files", "*.dat"), ("All Files", "*.*"))
    )
    if file_name:
        if file_name.endswith(".dat"):
            pass
        else:
            file_name = f'{file_name}.dat'

    # Grab all the entries and combos
    combos = []
    distances = []
    speeds = []

    for entry_line in lines_to_exec:
        combos.append(entry_line.Combo.get())
        distances.append(entry_line.input_distance.get())
        speeds.append(entry_line.input_speed.get())

    all_entries = [combos, distances, speeds]

    # Open the file and adding the lists
    output_file = open(file_name, 'wb')
    pickle.dump(all_entries, output_file)


def open_files():
    file_name = filedialog.askopenfilename(
        title="Open File",
        filetypes=(("Dat Files", "*.dat"), ("All Files", "*.*"))
    )
    input_file = open(file_name, 'rb')

    input_entries = pickle.load(input_file)
    combos = input_entries[0]
    distances = input_entries[1]
    speeds = input_entries[2]

    count = 0
    for entry_line in lines_to_exec:
        entry_line.Combo.set(combos[count])
        entry_line.input_distance.delete(0, END)
        entry_line.input_distance.insert(0, distances[count])
        entry_line.input_speed.delete(0, END)
        entry_line.input_speed.insert(0, speeds[count])
        count += 1


''' ==== Enabling and disabling buttons to prevent crashes ==== '''

buttons_state1 = [button_setorigin, button_setspeed, button_open, button_save, button_stop, button_exec_all,
                  button_enter]
for line in lines_to_exec:
    buttons_state1.append(line.button_exec)

buttons_state2 = [button_exit, button_up, button_down, button_left, button_right]


def enter_mm():
    for button in buttons_state1:
        button.config(state=DISABLED)
    for button in buttons_state2:
        button.config(state="normal")


def exit_mm():
    for button in buttons_state2:
        button.config(state=DISABLED)
    for button in buttons_state1:
        button.config(state="normal")


''' ==== Bluetooth Button ==== '''


# TODO: make functional bluetooth button

def bluetooth():
    button_start.config(state='normal')


def start():
    global arduino
    arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    while True:
        arduino_reply = recv_from_arduino()
        if not (arduino_reply == 'XXX'):
            log(arduino_reply)
            for button in buttons_state1:
                button.config(state="normal")
            break


button_bluetooth = Button(root, text="Bluetooth", command=lambda: bluetooth())
button_bluetooth.grid(row=0, column=7)

button_start = Button(root, text="Start", state=DISABLED, command=lambda: start())
button_start.grid(row=0, column=6)

root.mainloop()
