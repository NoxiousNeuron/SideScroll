import tkinter as tk 

# Create the main window
window = tk.Tk()

# Set the window title
window.title("Box with Floor and Continuous Movement After Jump")

# Set the window size
window.geometry("800x600")  # Width x Height
window.resizable(False, False)

# Set the background color
window.configure(bg="black")

# Create a canvas to draw the white box and floor
canvas = tk.Canvas(window, width=800, height=600, bg="black", highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor="center")  # Center the canvas

# Side Scroll Level Parameters
level_length = 2000  # Total length of the level
viewable_width = 800  # Width of the window
canvas_width = viewable_width  # Width of the visible canvas
floor_y = 500  # Y-coordinate of the floor
left_wall_x = 10  # Fixed position of the left wall
right_wall_x = level_length - 10  # Fixed position of the right wall
scroll_offset = 0  # Tracks the current scroll position of the canvas

# Draw the floor
canvas.create_line(0, floor_y, level_length, floor_y, fill="white")  # Full-length floor

# Initial position and size of the white box
box_size = 10
x0 = (canvas_width // 2) - (box_size // 2)
y0 = floor_y - box_size  # Start just above the floor
y1 = floor_y  # Bottom edge aligns with the floor

# Create the white box
box = canvas.create_rectangle(x0, y0, x0 + box_size, y1, fill="white", outline="")

# Movement parameters
jump_height = box_size * 5  # Five box heights
jump_speed = 3  # Speed of the jump (pixels per frame)
move_speed = 10  # Speed of horizontal movement
jump_horizontal_speed_factor = 0.5  # Scale horizontal speed during jump
is_jumping = False  # Flag to prevent multiple jumps
horizontal_direction = 0  # Tracks horizontal movement during a jump
keys_held = {"Left": False, "Right": False}  # Track key presses

# Add camera thresholds
camera_start_threshold = 200  # Pixels from the start before camera begins scrolling
camera_end_threshold = level_length - viewable_width - 0  # Stops 300 pixels before the end


# Movement Parameters 

def move_left(event):
    global scroll_offset
    keys_held["Left"] = True
    keys_held["Right"] = False  # Ensure opposite key is released

    box_coords = canvas.coords(box)

    # Calculate absolute positions
    left_edge_absolute = box_coords[0] + scroll_offset

    # Debug: Print box position and scroll offset
    print(f"Box Left Edge: {box_coords[0]} (Absolute: {left_edge_absolute}), "
          f"Right Edge: {box_coords[2]} (Absolute: {box_coords[2] + scroll_offset}), "
          f"Scroll Offset: {scroll_offset}")

    # Prevent the box from moving beyond the left wall
    if left_edge_absolute - move_speed >= left_wall_x:  # Subtract move_speed to predict the next move
        if scroll_offset > 0 and box_coords[0] <= camera_start_threshold:
            scroll_canvas(move_speed)
        else:
            canvas.move(box, -move_speed, 0)
    else:
        # Snap the box back to the barrier if it crosses
        canvas.move(box, left_wall_x - left_edge_absolute, 0)



def move_right(event):
    global scroll_offset
    keys_held["Right"] = True
    keys_held["Left"] = False  # Ensure opposite key is released

    box_coords = canvas.coords(box)

    # Calculate absolute positions
    right_edge_absolute = box_coords[2] + scroll_offset

    # Debug: Print box position and scroll offset
    print(f"Box Left Edge: {box_coords[0]} (Absolute: {box_coords[0] + scroll_offset}), "
          f"Right Edge: {box_coords[2]} (Absolute: {right_edge_absolute}), "
          f"Scroll Offset: {scroll_offset}")

    # Prevent the box from moving beyond the right wall
    if right_edge_absolute + move_speed <= right_wall_x:  # Add move_speed to predict the next move
        if scroll_offset < camera_end_threshold and box_coords[2] >= viewable_width - camera_start_threshold:
            scroll_canvas(-move_speed)
        else:
            canvas.move(box, move_speed, 0)
    else:
        # Snap the box back to the barrier if it crosses
        canvas.move(box, right_wall_x - right_edge_absolute, 0)



#Canvas Scroll

def scroll_canvas(delta):
    global scroll_offset
    # Adjust the scroll offset and ensure it remains within valid bounds
    new_offset = scroll_offset - delta
    if 0 <= new_offset <= level_length - viewable_width:
        scroll_offset = new_offset
        canvas.move("all", delta, 0)  # Move all elements on the canvas


#Horizontal Direction

def resume_horizontal_movement():
    """Resume horizontal movement if a key is still held after jumping."""
    global horizontal_direction
    if keys_held["Left"]:
        horizontal_direction = -move_speed
    elif keys_held["Right"]:
        horizontal_direction = move_speed
    else:
        horizontal_direction = 0  # Stop movement if no keys are held

    # Ensure the box moves within barriers
    box_coords = canvas.coords(box)
    left_edge_absolute = box_coords[0] + scroll_offset
    right_edge_absolute = box_coords[2] + scroll_offset

    if horizontal_direction > 0 and right_edge_absolute + horizontal_direction > right_wall_x:
        horizontal_direction = 0  # Stop at the right barrier
    elif horizontal_direction < 0 and left_edge_absolute + horizontal_direction < left_wall_x:
        horizontal_direction = 0  # Stop at the left barrier

    if horizontal_direction != 0 and not is_jumping:
        canvas.move(box, horizontal_direction, 0)
        window.after(30, resume_horizontal_movement)


def stop_movement(event):
    global horizontal_direction
    if event.keysym in keys_held:
        keys_held[event.keysym] = False
    # Stop horizontal movement if no keys are held
    if not keys_held["Left"] and not keys_held["Right"]:
        horizontal_direction = 0

#Jump Code

def jump(event):
    global is_jumping
    if is_jumping:
        return
    is_jumping = True
    initial_y = canvas.coords(box)[1]

    # Determine the initial horizontal direction
    horizontal_direction = move_speed if keys_held["Right"] else -move_speed if keys_held["Left"] else 0

    def go_up(horizontal_direction):
        box_coords = canvas.coords(box)

        # Dynamically update horizontal direction
        if keys_held["Right"]:
            horizontal_direction = move_speed
        elif keys_held["Left"]:
            horizontal_direction = -move_speed
        else:
            horizontal_direction = 0

        # Calculate absolute positions
        left_edge_absolute = box_coords[0] + scroll_offset
        right_edge_absolute = box_coords[2] + scroll_offset

        # Check barriers
        if horizontal_direction > 0:  # Moving right
            if right_edge_absolute + horizontal_direction > right_wall_x:
                horizontal_direction = 0  # Stop at the right barrier
        elif horizontal_direction < 0:  # Moving left
            if left_edge_absolute + horizontal_direction < left_wall_x:
                horizontal_direction = 0  # Stop at the left barrier

        # Camera scrolling logic
        if horizontal_direction > 0 and scroll_offset < camera_end_threshold and box_coords[2] >= viewable_width - camera_start_threshold:
            scroll_canvas(-move_speed)
        elif horizontal_direction < 0 and scroll_offset > 0 and box_coords[0] <= camera_start_threshold:
            scroll_canvas(move_speed)

        if box_coords[1] > initial_y - jump_height:  # Ascend
            canvas.move(box, horizontal_direction, -jump_speed)
            window.after(10, lambda: go_up(horizontal_direction))
        else:
            fall_down(horizontal_direction)

    def fall_down(horizontal_direction):
        global is_jumping
        box_coords = canvas.coords(box)

        # Dynamically update horizontal direction
        if keys_held["Right"]:
            horizontal_direction = move_speed
        elif keys_held["Left"]:
            horizontal_direction = -move_speed
        else:
            horizontal_direction = 0

        # Calculate absolute positions
        left_edge_absolute = box_coords[0] + scroll_offset
        right_edge_absolute = box_coords[2] + scroll_offset

        # Check barriers
        if horizontal_direction > 0:  # Moving right
            if right_edge_absolute + horizontal_direction > right_wall_x:
                horizontal_direction = 0  # Stop at the right barrier
        elif horizontal_direction < 0:  # Moving left
            if left_edge_absolute + horizontal_direction < left_wall_x:
                horizontal_direction = 0  # Stop at the left barrier

        # Camera scrolling logic
        if horizontal_direction > 0 and scroll_offset < camera_end_threshold and box_coords[2] >= viewable_width - camera_start_threshold:
            scroll_canvas(-move_speed)
        elif horizontal_direction < 0 and scroll_offset > 0 and box_coords[0] <= camera_start_threshold:
            scroll_canvas(move_speed)

        if box_coords[3] < floor_y:  # Descend
            canvas.move(box, horizontal_direction, jump_speed)
            window.after(10, lambda: fall_down(horizontal_direction))
        else:
            canvas.move(box, 0, floor_y - box_coords[3])  # Snap to the floor
            is_jumping = False  # Allow jumping again
            resume_horizontal_movement()

    go_up(horizontal_direction)




# Bind arrow keys to the movement functions
window.bind("<Left>", move_left)
window.bind("<Right>", move_right)
window.bind("<KeyRelease-Left>", stop_movement)
window.bind("<KeyRelease-Right>", stop_movement)
window.bind("<Up>", jump)

# Visual Barriers
canvas.create_line(left_wall_x, 0, left_wall_x, 600, fill="red", tags="barrier")  # Left barrier
canvas.create_line(right_wall_x, 0, right_wall_x, 600, fill="blue", tags="barrier")  # Right barrier

print(f"Left Barrier: {left_wall_x}, Right Barrier: {right_wall_x}, Scroll Offset: {scroll_offset}")

# Run the GUI event loop
window.mainloop()
