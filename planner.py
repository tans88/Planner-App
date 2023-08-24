from tkinter import *
from tkcalendar import Calendar
from tkinter import ttk
from tkinter.font import Font
import atexit 
import datetime
import os

# create app 
window = Tk()
window.title("Planner")
window.geometry("900x800")

# define fonts
calendar_font = Font(family = "Geneva", size = 18, weight="bold")
general_font = Font(family = "Geneva", size = 14)
schedule_button_font = Font(family = "Geneva", size = 16, weight = "bold")

# style app
style = ttk.Style(window)
style.theme_use("clam")

# create calendar 
current_date = datetime.datetime.now()
year = current_date.year
month = current_date.month
day = current_date.day

cal = Calendar(window, selectmode="day", year=year, month=month,
day=day, font=calendar_font, background="purple", bordercolor="black", 
headersbackground="purple", normalbackground="black", 
foreground="white", normalforeground="white", headersforeground="white")
cal.pack(pady=20)

# holds tasks based on the dates 
task_dict = {}

# modify path where files are saved 
save_directory = os.path.join(os.path.expanduser("~"), "Desktop", "cs projects", "planner_app_DB")
# create the directory if it does not exist 
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
# change current working directory to save_directory
os.chdir(save_directory)

# read saved tasks from files and populate task_dict
for filename in os.listdir():
    if filename.endswith(".txt"):
        # get date 
        formatted_date = filename.split(".")[0]
        tasks = []
        try:
            with open(filename, "r", encoding="utf-8", errors='replace') as file:
                for line in file:
                    tasks.append(line.strip())
            task_dict[formatted_date] = tasks
        except UnicodeDecodeError as e:
            print(f"Error decoding {filename}: {e}")

# create frame 
my_frame = Frame(window)
my_frame.pack(pady=10)

def delete_item(my_list):
    """
    deletes item from schedule 
    """
    delete = my_list.curselection()
    if delete:
        my_list.delete(delete)

def add_item(my_entry, my_list):
    """
    adds item to schedule 
    """
    new_item = my_entry.get()
    if new_item:
        my_list.insert(END, new_item)
        my_entry.delete(0, END)

def cross_item(my_list):
    """
    crosses off task if completed 
    """
    my_list.itemconfig(
        my_list.curselection(),
        fg="#dedede")
    my_list.selection_clear(0, END)

def uncross_item(my_list):
    """
    uncrosses off task if not completed
    """
    my_list.itemconfig(
        my_list.curselection(),
        fg="black")
    my_list.selection_clear(0, END)
    
def delete_crossed(my_list):
    """
    deletes all completed tasks 
    """
    items_to_delete = []
    for index in reversed(range(my_list.size())):
        if my_list.itemcget(index, "fg") == "#dedede":
            items_to_delete.append(index)
    for index in items_to_delete:
        my_list.delete(index)

def save_list(my_list):
    """
    saves list of tasks for each date
    """
    try:
        selected_date_str = cal.get_date()
        selected_date = datetime.datetime.strptime(selected_date_str, "%m/%d/%y")  # Use %y instead of %Y
        formatted_date = selected_date.strftime("%Y-%m-%d")

        # extend tasks list with tasks from the listbox
        # save crossed out tasks with X in front 
        task_dict[formatted_date] = [f"X {task}" if my_list.itemcget(index, "fg") == "#dedede" else task for index, task in enumerate(my_list.get(0, END))]

        # use save_directory to create the full path
        file_path = os.path.join(save_directory, f"{formatted_date}.txt")

        print("Saving file to:", file_path)  # Print the file path

        with open(file_path, "w", encoding="utf-8") as file:
            for task in task_dict[formatted_date]:
                file.write(task + "\n")
        Label(window, text=f"Saved Successfully!", font=schedule_button_font, fg="green").pack()
    
    except Exception as e:
        Label(window, text=f"Did Not Save Successfully.", font=schedule_button_font, fg="red").pack()
        print("Error: {e}")

def schedule():
    """
    creates schedule for chosen date 
    """
    # clear existing widgets from my_frame 
    for widget in my_frame.winfo_children():
        widget.destroy()

    selected_date_str = cal.get_date()
    selected_date = datetime.datetime.strptime(selected_date_str, "%m/%d/%y")
    formatted_date = selected_date.strftime("%Y-%m-%d")

    tasks = task_dict.get(formatted_date, [])

    # list of items 
    global my_list
    my_list = Listbox(my_frame, 
        font=general_font, 
        width = 50,
        height = 10, 
        highlightthickness=0, 
        selectbackground="#d692f9", 
        activestyle="none", 
        selectmode=SINGLE)
    my_list.pack(side=LEFT, fill=BOTH)

    for task in tasks:
        if task.startswith("X "): 
            index = tasks.index(task)
            my_list.insert(END, task[2:])
            my_list.itemconfig(index, {'fg':'#dedede'})
        else:
            my_list.insert(END, task)

    # scroll bar 
    my_scroll = Scrollbar(my_frame)
    my_scroll.pack(side=RIGHT, fill=BOTH)
    my_list.config(yscrollcommand=my_scroll.set)
    my_scroll.config(command=my_list.yview)

    # create entry box for adding items if not already present
    if not hasattr(schedule, 'entry_created'):
        schedule.entry_created = True
    
        my_entry = Entry(window, font=general_font, width=50)
        my_entry.pack(pady=5)

     # add buttons if not already present 
    if not hasattr(schedule, 'buttons_created'):
        schedule.buttons_created = True

        # create button frame
        button_frame = Frame(window)
        button_frame.pack(pady=5)

        # add buttons 
        delete = Button(button_frame, text="Delete Item", command=lambda: delete_item(my_list))
        add = Button(button_frame, text="Add Item", command=lambda: add_item(my_entry, my_list))
        cross_off = Button(button_frame, text="Cross Off Item", command=lambda: cross_item(my_list))
        uncross = Button(button_frame, text="Uncross Item", command=lambda: uncross_item(my_list))
        delete_cross = Button(button_frame, text="Delete Crossed Items", command=lambda: delete_crossed(my_list))
        save_items = Button(button_frame, text="Save Tasks", command=lambda: save_list(my_list))

        delete.grid(row=0, column=0)
        add.grid(row=0, column=1, padx=20)
        cross_off.grid(row=0, column=2)
        uncross.grid(row=0, column=3, padx=20)
        delete_cross.grid(row=0, column=4, padx=20)
        save_items.grid(row=0, column=5)

def save_tasks_on_exit():
    """
    save tasks to files once the application is closed 
    """
    for date, tasks in task_dict.items():
        formatted_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        file_path = os.path.join(save_directory, f"{formatted_date.strftime('%Y-%m-%d')}.txt")
        with open(file_path, "w") as file:
            for task in tasks:
                file.write(task + "\n")
atexit.register(save_tasks_on_exit)

# buttons 
my_button = Button(window, text="Get Schedule", font=schedule_button_font, command=schedule)
my_button.pack(pady=10)

# labels
my_label = Label(window, text="")
my_label.pack(pady=20)

window.mainloop()