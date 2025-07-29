# ADA CEYLİN CENGİZ 2022211045 CMPE496 HW1

# I am more comfortable with pyhton than other languages therefore I decided to use tkinter for this project.
# I have added comments for the features I added and how they satisfy HCI goals.
# I have also made my peers test the app and updated some features to improve usability.

# here's some of the goals I have kept in mind while designing:
# >> Direct Manipulation: click, drag, move, resize, undo/redo
# >> User Control: tool selection, color choice, undo, redo, delete
# >> Feedback: shape counter, hover effects, animations, message boxes
# >> Error Prevention: color validation, delete confirmation
# >> Designing for Fun: bounce animations, random color mode, playful design


import tkinter as tk
import random

# random is imported because I wanted the user to have a random coloring option too.

class DrawingApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Drawing Editor")

        self.selected_tool = tk.StringVar(value="circle")
        self.current_color = "#3498db"
        self.random_color = tk.BooleanVar()

        self.shapes = []
        self.current_line = None
        self.moving_shape = None
        self.resizing_shape = None
        self.preview_line = None
        self.undo_stack = []
        self.redo_stack = []

        title = tk.Label(window, text="🎨 Welcome to the Drawing Playground!",
                         font=("Helvetica", 20, "bold"), bg="#fdf6e3", fg="#2c3e50", pady=10)
        title.pack(side="top", fill="x")

        self.canvas = tk.Canvas(window, width=800, height=600, bg="white", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.handle_mouse_click)
        self.canvas.bind("<B1-Motion>", self.handle_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_mouse_release)

        self.sidebar = tk.Frame(window, bg="#f2e9dc")
        self.sidebar.pack(side="right", fill="y")

        self.create_tool_selector()
        self.create_color_picker()
        self.create_undo_redo_buttons()
        self.create_save_delete_buttons()
        self.create_how_to_use()




 # As clarified in the "how to use" part in the sidebar, in order to change colors all the user has to do
 # is to enter the name of the color they would like to use in the "Color Options" part. A wide range of colors are available (even maroon and teal!)
 # However if user enters a color that is not recognized, a pop-up will appear also the box around the color picker will turn red.
 
    def set_color(self):
        color = self.color_entry.get()
        try:
            self.canvas.itemconfig("preview_test", fill=color)
            self.current_color = color
            self.color_preview.config(bg=color)
            self.color_display.config(bg=color)
            self.color_entry.config(highlightthickness=0)
        except tk.TclError:
            from tkinter import messagebox
            self.color_entry.config(highlightbackground="red", highlightthickness=2)
            messagebox.showerror("Invalid Color", f"'{color}' is not a recognized color name.")
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, self.current_color)



# click to create/move/resize/erase etc, which satisfies immediate feedback and direct manipulation principles.
# erase tool additionally helps with error prevention.

    def handle_mouse_click(self, event):
        x, y = event.x, event.y
        tool = self.selected_tool.get()
        size = 40

        if self.random_color.get():
            color = random.choice(["red", "green", "blue", "orange", "purple", "pink", "cyan"])
        else:
            color = self.current_color

        if tool == "circle":
            shape = self.canvas.create_oval(x - size/2, y - size/2, x + size/2, y + size/2,
                                            fill=color, outline="black")
            self.shapes.append(shape)
            self.undo_stack.append(("create", "oval", self.canvas.coords(shape), {"fill": color, "outline": "black"}))
            self.animate_bounce(shape)
            self.update_shape_counter(increase=True)
            self.redo_stack.clear()

        elif tool == "square":
            shape = self.canvas.create_rectangle(x - size/2, y - size/2, x + size/2, y + size/2,
                                                 fill=color, outline="black")
            self.shapes.append(shape)
            self.undo_stack.append(("create", "rectangle", self.canvas.coords(shape), {"fill": color, "outline": "black"}))
            self.animate_bounce(shape)
            self.update_shape_counter(increase=True)
            self.redo_stack.clear()

        elif tool == "line":
            self.current_line = (x, y)

        elif tool == "erase":
            items = self.canvas.find_overlapping(x-3, y-3, x+3, y+3)
            for item in items:
                if item in self.shapes:
                    shape_type = self.canvas.type(item)
                    if shape_type == "line":
                        props = {
                            "fill": self.canvas.itemcget(item, "fill"),
                            "width": self.canvas.itemcget(item, "width")
                        }
                    else:
                        props = {
                            "fill": self.canvas.itemcget(item, "fill"),
                            "outline": self.canvas.itemcget(item, "outline"),
                            "width": self.canvas.itemcget(item, "width")
                        }
                    coords = self.canvas.coords(item)
                    self.canvas.delete(item)
                    self.shapes.remove(item)
                    self.undo_stack.append(("delete", shape_type, coords, props))
                    self.redo_stack.clear()
                    self.update_shape_counter(increase=False)

                    break

        elif tool == "move" or tool == "resize":
            items = self.canvas.find_overlapping(x-3, y-3, x+3, y+3)
            for item in items:
                if item in self.shapes:
                    self.moving_shape = item if tool == "move" else None
                    self.resizing_shape = item if tool == "resize" else None
                    self.prev_coords = (x, y)
                    self.resize_start = (x, y)
                    self.start_coords = self.canvas.coords(item)
                    self.shape_type = self.canvas.type(item)

                    if self.shape_type == "line":
                        self.shape_opts = {
                            "fill": self.canvas.itemcget(item, "fill"),
                            "width": self.canvas.itemcget(item, "width")
                        }
                    else:
                        self.shape_opts = {
                            "fill": self.canvas.itemcget(item, "fill"),
                            "outline": self.canvas.itemcget(item, "outline"),
                            "width": self.canvas.itemcget(item, "width")
                        }
                    break




# This is for move/resize/line buttons.
# Also helps with direct manipulation and control.
# A "ghost line" appears while creating a line to increase control over the drawing for the user.

    def handle_mouse_drag(self, event):
        if self.selected_tool.get() == "move" and self.moving_shape:
            dx = event.x - self.prev_coords[0]
            dy = event.y - self.prev_coords[1]
            self.canvas.move(self.moving_shape, dx, dy)
            self.prev_coords = (event.x, event.y)

        elif self.selected_tool.get() == "resize" and self.resizing_shape:
            coords = self.start_coords
            sx, sy = self.resize_start
            dx = event.x - sx
            dy = event.y - sy

            if self.shape_type == "line":
                x0, y0, x1, y1 = coords
                new_coords = [x0, y0, x1 + dx, y1 + dy]
                self.canvas.coords(self.resizing_shape, *new_coords)
            else:
                x0, y0, x1, y1 = coords
                new_x1 = x1 + dx if sx > (x0 + x1)/2 else x1
                new_x0 = x0 + dx if sx <= (x0 + x1)/2 else x0
                new_y1 = y1 + dy if sy > (y0 + y1)/2 else y1
                new_y0 = y0 + dy if sy <= (y0 + y1)/2 else y0
                self.canvas.coords(self.resizing_shape, new_x0, new_y0, new_x1, new_y1)

        elif self.selected_tool.get() == "line" and self.current_line:
            if self.preview_line:
                self.canvas.delete(self.preview_line)
            x1, y1 = self.current_line
            x2, y2 = event.x, event.y
            self.preview_line = self.canvas.create_line(x1, y1, x2, y2, dash=(4, 2), fill="gray")
            
            


# same as the two features above. lets user commit to the action or delete it.

    def handle_mouse_release(self, event):
        if self.selected_tool.get() == "line" and self.current_line:
            x1, y1 = self.current_line
            x2, y2 = event.x, event.y
            color = random.choice(["red", "green", "blue", "orange", "purple", "pink", "cyan"]) if self.random_color.get() else self.current_color
            line = self.canvas.create_line(x1, y1, x2, y2, width=2, fill=color)  
            self.shapes.append(line)
            self.undo_stack.append(("create", "line", [x1, y1, x2, y2], {"fill": self.current_color}))
            self.update_shape_counter(increase=True)
            self.redo_stack.clear()
            self.current_line = None

        elif self.moving_shape:
            new_coords = self.canvas.coords(self.moving_shape)
            if self.start_coords != new_coords:
                self.canvas.delete(self.moving_shape)
                self.shapes.remove(self.moving_shape)
                new_id = self.create_shape(self.shape_type, new_coords, self.shape_opts)
                self.shapes.append(new_id)
                self.undo_stack.append(("transform", self.shape_type, self.start_coords, new_coords, self.shape_opts, new_id))
                self.redo_stack.clear()

        elif self.resizing_shape:
            new_coords = self.canvas.coords(self.resizing_shape)
            if self.start_coords != new_coords:
                self.canvas.delete(self.resizing_shape)
                self.shapes.remove(self.resizing_shape)
                new_id = self.create_shape(self.shape_type, new_coords, self.shape_opts)
                self.shapes.append(new_id)
                self.undo_stack.append(("transform", self.shape_type, self.start_coords, new_coords, self.shape_opts, new_id))
                self.redo_stack.clear()

        if self.preview_line:
            self.canvas.delete(self.preview_line)
            self.preview_line = None

        self.moving_shape = None
        self.resizing_shape = None
        
        
        

# Aimed for consistent sidebar design, which includes the tool selector.
# This tool bar makes it easier to switch between tools.
# The user can also use C S L M R E on his/her keyboard to switch between tools.
        
    def create_tool_selector(self):
        tool_row = tk.Frame(self.sidebar, bg="#f2e9dc", pady=10)
        tool_row.pack(anchor="nw")

        label = tk.Label(tool_row, text="Choose tool:", font=("Helvetica", 12, "bold"), bg="#f2e9dc", fg="black")
        label.pack(side="left")

        tools = [
            ("🔵 Circle", "circle"),
            ("🟥 Square", "square"),
            ("🖊️ Line", "line"),
            ("🧽 Erase", "erase"),
            ("✋ Move", "move"),
            ("📏 Resize", "resize"),]

        for txt, val in tools:
            b = tk.Radiobutton(tool_row, text=txt, variable=self.selected_tool, value=val,
                               bg="#f2e9dc", font=("Helvetica", 11), anchor="w", fg="black", selectcolor="#f2e9dc")
            b.pack(side="left")
            self.add_hover_effect(b)

        self.status_label = tk.Label(self.sidebar, text="Tool: circle", bg="#f2e9dc", anchor="w",
                                     font=("Helvetica", 11), fg="black")
        self.status_label.pack(anchor="w", padx=10, pady=(0, 5))

        def update_tool(*args):
            self.status_label.config(text=f"Tool: {self.selected_tool.get()}")

        self.selected_tool.trace("w", update_tool)

        
        self.shape_count = 0
        self.counter_label = tk.Label(self.sidebar, text="Shapes Drawn: 0",
                                      bg="#f2e9dc", anchor="w", font=("Helvetica", 11), fg="black")
        self.counter_label.pack(anchor="w", padx=10, pady=(0, 5))





 # Being able to pick the color of the shapes gives user freedom of creativity and control.
 # I put the random color option to give the app an exploration and curiosity element.
 
    def create_color_picker(self):
        picker_frame = tk.LabelFrame(self.sidebar, text="🎨 Color Options", bg="#f2e9dc",
                                     font=("Helvetica", 13, "bold"), fg="black", padx=10, pady=10)
        picker_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(picker_frame, text="Color name (e.g. red):", font=("Helvetica", 10),
                 bg="#f2e9dc", anchor="w", fg="black").pack(anchor="w")

        self.color_entry = tk.Entry(picker_frame, font=("Helvetica", 11), width=15)
        self.color_entry.insert(0, self.current_color)
        self.color_entry.pack(pady=(0, 10))
        self.color_entry.bind("<Return>", lambda e: self.set_color())

        self.color_preview = tk.Canvas(picker_frame, width=30, height=30, bg=self.current_color,
                                       highlightthickness=2, highlightbackground="black")
        self.color_preview.pack()

        apply_btn = tk.Button(picker_frame, text="✅ Apply Color", font=("Helvetica", 11, "bold"),
                              bg="white", fg="green", command=self.set_color)
        apply_btn.pack(pady=8)

        random_checkbox = tk.Checkbutton(picker_frame, text="🌈 Rainbow Mode",
                                         variable=self.random_color, bg="#f2e9dc",
                                         font=("Helvetica", 10), fg="black")
        random_checkbox.pack()

        tk.Label(picker_frame, text="Current Color:", bg="#f2e9dc", font=("Helvetica", 10), fg="black").pack(pady=(10, 2))
        self.color_display = tk.Canvas(picker_frame, width=30, height=30, bg=self.current_color,
                                       highlightthickness=1, highlightbackground="black")
        self.color_display.pack()
        
        
        

# Permitting easy revisal of actions is important which is why I have added undo/redo buttons.
# They also work with control + z and control + y on the keyboard.

    def create_undo_redo_buttons(self):
        btn_frame = tk.Frame(self.sidebar, bg="#f2e9dc")
        btn_frame.pack(pady=(0, 10))

        self.undo_btn = tk.Button(btn_frame, text="↩️ Undo", font=("Helvetica", 11),
                                  command=self.undo, width=10)
        self.undo_btn.pack(pady=3)

        self.redo_btn = tk.Button(btn_frame, text="↪️ Redo", font=("Helvetica", 11),
                                  command=self.redo, width=10)
        self.redo_btn.pack(pady=3)



# save / delete buttons for more user control.
    def create_save_delete_buttons(self):
        btn_frame = tk.Frame(self.sidebar, bg="#f2e9dc")
        btn_frame.pack(pady=(0, 10))

        save_btn = tk.Button(btn_frame, text="💾 Save", font=("Helvetica", 11),
                             command=self.save_drawing, width=10)
        save_btn.pack(pady=3)

        delete_btn = tk.Button(btn_frame, text="🗑️ Delete", font=("Helvetica", 11),
                               command=self.confirm_delete, width=10)
        delete_btn.pack(pady=3)
        about_btn = tk.Button(btn_frame, text="ℹ️ About", font=("Helvetica", 11),
                              command=self.show_about_info, width=10)
        about_btn.pack(pady=3)



# In order to reduce memory load and help the user I made a "how to use" frame in the sidebar.
# The "how to use" part does not require any clicking or interaction to open, it is always there when needed
# Also it is not eye-tiring since it is on the right corner of the screen.

    def create_how_to_use(self):
        usage_frame = tk.LabelFrame(self.sidebar, text="🧑‍🏫 How to Use", bg="#f2e9dc",
                                    font=("Helvetica", 13, "bold"), fg="black", padx=12, pady=12)
        usage_frame.pack(padx=12, pady=(10, 20), fill="x", expand=True)

        steps = [
            "1. Select a tool above ",
            "2. Click the canvas and watch the shapes appear!",
            "3. Use 'Move' to drag shapes ✋",
            "4. Use 'Erase' to remove 🧽",
            "5. Type a color and press Enter 🎨",
            "6. Try the Rainbow Mode for fun! 🌈",
            "7. Use 'Resize' to stretch shapes 📏",
            "8. Press Ctrl+Z to undo 🔄",
            "9. Press Ctrl+Y to redo ↩️",
            "10. Press C/S/L/M/R/E to switch tools on your keyboard️"
        ]

        for step in steps:
            tk.Label(usage_frame, text=step, font=("Helvetica", 11),
                     bg="#f2e9dc", anchor="w", fg="black").pack(anchor="w", pady=1)



  
# This is used for returning the shapes that were adjusted by the "Resize" tool back to their original shape.

    def create_shape(self, shape_type, coords, opts):
        if shape_type == "oval":
            return self.canvas.create_oval(*coords, **opts)
        elif shape_type == "rectangle":
            return self.canvas.create_rectangle(*coords, **opts)
        elif shape_type == "line":
            return self.canvas.create_line(*coords, **opts)
    
    
    
# undo and redo are defined below here.
# It allows revisal of actions which is essential for usability and control.

    def undo(self, event=None):
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        kind = action[0]

        if kind == "create":
            shape_type, coords, opts = action[1], action[2], action[3]
            items = self.canvas.find_all()
            shape_id = items[-1] if items else None
            if shape_id and shape_id in self.shapes:
                self.canvas.delete(shape_id)
                self.shapes.remove(shape_id)
                self.redo_stack.append(("create", shape_type, coords, opts))
                self.update_shape_counter(increase=False)

        elif kind == "delete":
            shape_type, coords, opts = action[1], action[2], action[3]
            new_id = self.create_shape(shape_type, coords, opts)
            self.shapes.append(new_id)
            self.redo_stack.append(("delete", shape_type, coords, opts))
            self.update_shape_counter(increase=True)

        elif kind == "transform":
            shape_type, before, after, opts, shape_id = action[1:]
            if shape_id in self.shapes:
                self.canvas.delete(shape_id)
                self.shapes.remove(shape_id)
            new_id = self.create_shape(shape_type, before, opts)
            self.shapes.append(new_id)
            self.redo_stack.append(("transform", shape_type, before, after, opts, new_id))

    def redo(self, event=None):
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        kind = action[0]

        if kind == "create":
            shape_type, coords, opts = action[1], action[2], action[3]
            new_id = self.create_shape(shape_type, coords, opts)
            self.shapes.append(new_id)
            self.undo_stack.append(("create", shape_type, coords, opts))
            self.update_shape_counter(increase=True)

        elif kind == "delete":
            items = self.canvas.find_all()
            shape_id = items[-1] if items else None
            if shape_id and shape_id in self.shapes:
                coords = self.canvas.coords(shape_id)
                shape_type = self.canvas.type(shape_id)
                options = self.canvas.itemconfig(shape_id)
                if shape_type == "line":
                    props = {
                        "fill": options["fill"][-1],
                        "width": options["width"][-1]
                    }
                else:
                    props = {
                        "fill": options["fill"][-1],
                        "outline": options["outline"][-1],
                        "width": options["width"][-1]
                    }
                self.canvas.delete(shape_id)
                self.shapes.remove(shape_id)
                self.undo_stack.append(("delete", shape_type, coords, props))
                self.update_shape_counter(increase=False)

        elif kind == "transform":
            shape_type, before, after, opts, shape_id = action[1:]
            if shape_id in self.shapes:
                self.canvas.delete(shape_id)
                self.shapes.remove(shape_id)
            new_id = self.create_shape(shape_type, after, opts)
            self.shapes.append(new_id)
            self.undo_stack.append(("transform", shape_type, after, before, opts, new_id))
            
            
            
        

# I have added an option to save the drawing! This also helps with closure and user control.
# It took a few tried but I made it so that the user could save the drawing on any location in their computer.
# I use a Mac and it worked without any issues on mine.

    def save_drawing(self):
        from tkinter import filedialog, messagebox
        import json

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")])
        if file_path:
            drawing = []
            for shape_id in self.shapes:
                coords = self.canvas.coords(shape_id)
                shape_type = self.canvas.type(shape_id)
                options = self.canvas.itemconfig(shape_id)
                if shape_type == "line":
                    props = {
                        "fill": options["fill"][-1],
                        "width": options["width"][-1]
                    }
                else:
                    props = {
                        "fill": options["fill"][-1],
                        "outline": options["outline"][-1],
                        "width": options["width"][-1]
                    }
                drawing.append((shape_type, coords, props))
            with open(file_path, "w") as f:
                json.dump(drawing, f)
            messagebox.showinfo("Saved", f"Your drawing was saved to:\n{file_path}")



# This is added for closure principle of Shneiderman’s rules. messagebox is imported to show a little warning message.

    def confirm_delete(self):
        from tkinter import messagebox
        result = messagebox.askyesno("Delete Drawing", "Are you sure you want to delete everything?")
        if result:
            self.delete_all_shapes()
            
                    
            
# This one allows user to delete all shapes and start anew. Also resets the created shape counter back to zero.

    def delete_all_shapes(self):
        for shape in self.shapes:
            self.canvas.delete(shape)
        self.shapes.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.shape_count = 0  
        self.counter_label.config(text=f"Shapes Drawn: 0")



# I added the next two feauters to fit the "designing for fun" principles.
# I added a bouncing-like effect to when a circle and square is created to
# make the design look more fun and playful since it's a "playground" :)

    def animate_bounce(self, shape_id, steps=5, scale_factor=1.2, delay=30):
        coords = self.canvas.coords(shape_id)
        x0, y0, x1, y1 = coords
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2

        def grow(step, steps_left):
            if steps_left == 0:
                return
            factor = 1 + (scale_factor - 1) * (step / steps)
            new_x0 = cx - (cx - x0) * factor
            new_y0 = cy - (cy - y0) * factor
            new_x1 = cx + (x1 - cx) * factor
            new_y1 = cy + (y1 - cy) * factor
            self.canvas.coords(shape_id, new_x0, new_y0, new_x1, new_y1)
            self.window.after(delay, lambda: grow(step + 1, steps_left - 1))

        grow(0, steps)



# Added a slight hovering effect on the toolbox for a more aesthetic look.
# This also makes it clearer for the user which button they are about to click on.

    def add_hover_effect(self, button, hover_color="#e0d6c8", normal_color="SystemButtonFace"):
        def on_enter(e):
            button.config(bg=hover_color)
        def on_leave(e):
            button.config(bg=normal_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        
        
# The shape counter is for evaluation purposes and feedback during use which are a part of Greenberg's usability goals
# I updated it to also adjust for undo, redo and erase.

    def update_shape_counter(self, increase=True):
        if increase:
            self.shape_count += 1
        else:
            if self.shape_count > 0:
                self.shape_count -= 1
        self.counter_label.config(text=f"Shapes Drawn: {self.shape_count}")
 
 
 
# I thought it would be informative to add a little "about" part for this project.
# We have already covered how to use the app in the sidebar.

    def show_about_info(self):
        from tkinter import messagebox
        messagebox.showinfo("About This App", 
                            "🎨 Drawing Playground!!\n\n"
                            "Created by Ada for CMPE496 course :)\n\n"
                            "Designed with usability\n"
                            "and fun in mind,\n"
                            "following HCI design principles!\n\n"
                            "Special thanks to everyone who tested it and for their feedback :)")





if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)

    root.bind("<Control-z>", app.undo)
    root.bind("<Control-y>", app.redo)
    root.bind("c", lambda e: app.selected_tool.set("circle"))
    root.bind("s", lambda e: app.selected_tool.set("square"))
    root.bind("l", lambda e: app.selected_tool.set("line"))
    root.bind("m", lambda e: app.selected_tool.set("move"))
    root.bind("r", lambda e: app.selected_tool.set("resize"))
    root.bind("e", lambda e: app.selected_tool.set("erase"))

    root.mainloop()

