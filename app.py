from vpython import sphere, vector, mag, hat, color, rate, scene, arrow, curve, label, wtext, button
import random
import math
import time

# Function to calculate the electric field
def E(rq, ro, q):
    k = 9e9 
    r = ro - rq
    r_mag = mag(r)
    if r_mag < 1e-10:  
        return vector(0, 0, 0)
    Etemp = k * q * hat(r) / r_mag**2  # Electric field due to point charge
    return Etemp

# Parameters
Q = 3e-6  
R = 0.1 
N = 2000  
dQ = Q / N  

# Set up the scene
scene.title = "Electric Field of a Charged Sphere"
scene.width = 1000
scene.height = 700
scene.background = color.white
scene.caption = "Electric Field Simulation"

charged_sphere = sphere(pos=vector(0, 0, 0), radius=R, color=color.blue, opacity=0.3)

ro = vector(3 * R, 0, 0)  
test_charge = sphere(pos=ro, radius=R/5, color=color.green, make_trail=True, 
                    trail_radius=R/10, trail_color=color.green)


# Electric field vector
field_arrow = arrow(pos=ro, axis=vector(0, 0, 0), color=color.red, shaftwidth=R/20)


field_label = label(pos=vector(0, -1.5*R, 0), text="Calculating...", height=16, box=False)
distance_label = label(pos=vector(0, -1.8*R, 0), text="Distance: ", height=16, box=False)

scene.append_to_caption("\n\nAnimation Speed\n\n")

reset_button = button(text="Reset Animation", bind=lambda: reset_animation())
scene.append_to_caption("\n\n")

show_field_lines = False  
status_text = wtext(text="Generating point charges...")

# Function to distribute charges uniformly on sphere surface
def fibonacci_sphere(samples):
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  
    
    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y) 
        
        theta = phi * i
        
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        
        points.append(vector(x * R, y * R, z * R))
    
    return points

point_positions = fibonacci_sphere(N)

# Create point charges
point_charges = []
for pos in point_positions:
    point_charge = sphere(pos=pos, radius=R/30, color=color.red)
    point_charges.append(point_charge)

status_text.text = "Charges generated. Starting simulation..."

# Function to calculate the theoretical field
def theoretical_field(r):
    r_mag = mag(r)
    if r_mag <= R:  # Inside
        return 9e9 * Q * r / (R**3)
    else:  # Outside
        return 9e9 * Q * r / (r_mag**3)

# Function to draw field lines
field_lines = []
def draw_field_lines():
    global field_lines
    # Clear old field lines
    for line in field_lines:
        line.visible = False
    field_lines = []
    
    # Draw new field lines
    if show_field_lines:
        num_lines = 16
        for i in range(num_lines):
            theta = 2 * math.pi * i / num_lines
            start_pos = vector(1.1*R * math.cos(theta), 1.1*R * math.sin(theta), 0)
            
            line_points = [start_pos]
            current_pos = start_pos
            
            # Trace the field line
            for _ in range(15):
                E_at_point = vector(0, 0, 0)
                for charge in point_charges:
                    E_at_point += E(charge.pos, current_pos, dQ)
                
                step_size = 0.2 * R
                next_pos = current_pos + hat(E_at_point) * step_size
                line_points.append(next_pos)
                current_pos = next_pos
                
                if mag(current_pos) > 5*R:
                    break
            
            # Create the curve
            field_line = curve(pos=line_points, color=color.blue, radius=R/50)
            field_lines.append(field_line)

# Animation parameters
running = True
animation_phase = 0 
t = 0  
path_radius = 4 * R  
speed_factor = 1.0 

def reset_animation():
    global running, animation_phase, t
    animation_phase = 0
    t = 0
    test_charge.clear_trail()
    test_charge.pos = vector(3 * R, 0, 0)
    field_arrow.pos = test_charge.pos
    running = True

# Main animation loop
while True:
    rate(30 * speed_factor)  
    
    # Different animation phases
    if animation_phase == 0:  # Circular motion around the sphere
        t += 0.02
        if t > 2 * math.pi:
            t = 0
            animation_phase = 1
        
        ro = vector(path_radius * math.cos(t), path_radius * math.sin(t), 0)
        
    elif animation_phase == 1:  # Spiral inward
        t += 0.02
        current_radius = path_radius * (1 - t/(4*math.pi))
        
        if current_radius < 1.5 * R:
            t = 0
            animation_phase = 2
        
        ro = vector(current_radius * math.cos(4*t), current_radius * math.sin(4*t), 0)
        
    elif animation_phase == 2:  
        t += 0.02
        if t < math.pi:
            distance = 1.5*R + 3*R * (1 + math.cos(t))/2
            ro = vector(distance, 0, 0)
        else:
            angle = (t - math.pi) * 2
            ro = vector(4*R * math.cos(angle), 4*R * math.sin(angle), 0)
            
            if t > 2 * math.pi:
                t = 0
                animation_phase = 3
    
    elif animation_phase == 3: 
        t += 0.02
        if t > 4 * math.pi:
            t = 0
            animation_phase = 0
            
        # Helical path
        ro = vector(3*R * math.cos(t), 3*R * math.sin(t), 2*R * math.sin(t/2))
    
    # Update position of test charge
    test_charge.pos = ro
    field_arrow.pos = ro
    
    Es = vector(0, 0, 0)
    for charge in point_charges:
        Es += E(charge.pos, ro, dQ)
    
    Et = theoretical_field(ro - charged_sphere.pos)
    
    # Update the field arrow
    scale_factor = 1e-7 * R / max(1e-10, mag(Es))  
    field_arrow.axis = Es * scale_factor
    
    distance = mag(ro - charged_sphere.pos)
    field_label.text = f"E = {mag(Es):.2e} N/C    Theory = {mag(Et):.2e} N/C"
    distance_label.text = f"Distance from center: {distance/R:.2f}R"
    
    if int(t * 20) % 10 == 0 and show_field_lines:
        draw_field_lines()