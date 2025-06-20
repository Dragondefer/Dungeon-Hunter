import random
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import defaultdict, deque
from typing import cast
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class Room:
    """Represents a room in the dungeon with n-dimensional coordinates"""
    def __init__(self, coords, room_type="normal", time_state=0):
        self.coords = tuple(coords)  # n-dimensional coordinates
        self.room_type = room_type  # "start", "end", "treasure", "normal"
        self.time_state = time_state  # for time manipulation
        self.connections = set()  # connected rooms
        
    def __hash__(self):
        return hash((self.coords, self.time_state))
    
    def __eq__(self, other):
        return self.coords == other.coords and self.time_state == other.time_state
    
    def __repr__(self):
        return f"Room{self.coords}[{self.room_type}]"

class DungeonGenerator:
    """Main dungeon generation engine"""
    
    def __init__(self, dimensions=2, time_enabled=False):
        self.dimensions = dimensions
        self.time_enabled = time_enabled
        self.rooms = {}  # coords -> Room
        self.start_room = None
        self.end_room = None
        
    def distance(self, coord1, coord2):
        """Calculate Euclidean distance between two coordinates"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(coord1, coord2)))
    
    def get_neighbors(self, coords):
        """Get all possible neighboring coordinates"""
        neighbors = []
        for dim in range(self.dimensions):
            for delta in [-1, 1]:
                new_coords = list(coords)
                new_coords[dim] += delta
                neighbors.append(tuple(new_coords))
        return neighbors
    
    def generate_2d_organic(self, width=20, height=20, branch_probability=0.3):
        """Generate 2D dungeon with organic branching paths"""
        self.rooms = {}
        
        # Start at center
        start_coords = (width // 2, height // 2)
        self.start_room = Room(start_coords, "start")
        self.rooms[start_coords] = self.start_room
        
        # Main path using random walk with bias
        current = start_coords
        main_path = [current]
        
        # Generate main path
        for _ in range(random.randint(15, 25)):
            neighbors = self.get_neighbors(current)
            # Bias towards unexplored areas
            valid_neighbors = [n for n in neighbors if n not in self.rooms]
            if valid_neighbors:
                # Prefer continuing in same general direction
                if len(main_path) > 1:
                    prev_dir = (current[0] - main_path[-2][0], current[1] - main_path[-2][1])
                    weighted_neighbors = []
                    for n in valid_neighbors:
                        new_dir = (n[0] - current[0], n[1] - current[1])
                        # Weight by direction similarity
                        dot_product = prev_dir[0] * new_dir[0] + prev_dir[1] * new_dir[1]
                        weight = max(1, dot_product + 2)
                        weighted_neighbors.extend([n] * weight)
                    current = random.choice(weighted_neighbors)
                else:
                    current = random.choice(valid_neighbors)
                
                room = Room(current, "normal")
                self.rooms[current] = room
                self.rooms[main_path[-1]].connections.add(room)
                room.connections.add(self.rooms[main_path[-1]])
                main_path.append(current)
        
        # Set end room
        self.end_room = self.rooms[current]
        self.end_room.room_type = "end"
        
        # Generate branches
        for room_coords in list(self.rooms.keys()):
            if random.random() < branch_probability:
                self._generate_branch(room_coords, random.randint(2, 8))
    
    def generate_3d_layered(self, width=15, height=15, layers=5, branch_probability=0.25):
        """Generate 3D dungeon with vertical connections"""
        self.rooms = {}
        
        # Start at bottom center
        start_coords = (width // 2, height // 2, 0)
        self.start_room = Room(start_coords, "start")
        self.rooms[start_coords] = self.start_room
        
        current = start_coords
        
        # Generate spiral path going up
        for layer in range(layers):
            # Generate path on current layer
            layer_rooms = []
            for _ in range(random.randint(8, 15)):
                neighbors = [(x, y, layer) for x, y in 
                           [(current[0] + dx, current[1] + dy) 
                            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]]]
                valid_neighbors = [n for n in neighbors if n not in self.rooms]
                
                if valid_neighbors:
                    current = random.choice(valid_neighbors)
                    room = Room(current, "normal")
                    self.rooms[current] = room
                    layer_rooms.append(current)
                    
                    # Connect to previous room
                    prev_coords = layer_rooms[-2] if len(layer_rooms) > 1 else start_coords
                    if prev_coords in self.rooms:
                        self.rooms[prev_coords].connections.add(room)
                        room.connections.add(self.rooms[prev_coords])
            
            # Add vertical connections
            if layer < layers - 1:
                # Connect some rooms to upper layer
                for room_coords in layer_rooms:
                    if random.random() < 0.4:  # 40% chance of vertical connection
                        upper_coords = (room_coords[0], room_coords[1], room_coords[2] + 1)
                        if upper_coords not in self.rooms:
                            upper_room = Room(upper_coords, "normal")
                            self.rooms[upper_coords] = upper_room
                            self.rooms[room_coords].connections.add(upper_room)
                            upper_room.connections.add(self.rooms[room_coords])
                            current = upper_coords
            
            # Generate branches on this layer
            for room_coords in layer_rooms:
                if random.random() < branch_probability:
                    self._generate_branch(room_coords, random.randint(2, 6))
        
        # Set end room at top
        top_rooms = [coords for coords in self.rooms.keys() if coords[2] == layers - 1]
        if top_rooms:
            end_coords = random.choice(top_rooms)
            self.end_room = self.rooms[end_coords]
            self.end_room.room_type = "end"
    
    def generate_4d_temporal(self, width=10, height=10, depth=3, time_states=3, branch_probability=0.2):
        """Generate 4D dungeon with time manipulation"""
        self.rooms = {}
        self.time_enabled = True
        
        # Start in present (time_state=1)
        start_coords = (width // 2, height // 2, depth // 2)
        self.start_room = Room(start_coords, "start", time_state=1)
        self.rooms[(start_coords, 1)] = self.start_room
        
        current = start_coords
        current_time = 1
        
        # Generate main path with temporal shifts
        for _ in range(random.randint(20, 30)):
            # Decide on action: move in space or time
            if random.random() < 0.7:  # 70% spatial movement
                neighbors = self.get_neighbors(current)
                valid_neighbors = [n for n in neighbors 
                                 if (n, current_time) not in self.rooms]
                if valid_neighbors:
                    current = random.choice(valid_neighbors)
                    room = Room(current, "normal", current_time)
                    self.rooms[(current, current_time)] = room
                    
                    # Connect to previous room
                    prev_key = list(self.rooms.keys())[-2]
                    prev_room = self.rooms[prev_key]
                    prev_room.connections.add(room)
                    room.connections.add(prev_room)
            
            else:  # 30% temporal movement
                if random.random() < 0.5 and current_time > 0:
                    new_time = current_time - 1
                elif current_time < time_states - 1:
                    new_time = current_time + 1
                else:
                    continue
                
                # Create temporal connection
                if (current, new_time) not in self.rooms:
                    room = Room(current, "temporal", new_time)
                    self.rooms[(current, new_time)] = room
                    
                    # Connect across time
                    current_room = self.rooms[(current, current_time)]
                    current_room.connections.add(room)
                    room.connections.add(current_room)
                    current_time = new_time
        
        # Set end room
        end_coords = random.choice(list(self.rooms.keys()))
        self.end_room = self.rooms[end_coords]
        self.end_room.room_type = "end"
        
        # Generate branches
        for room_key in list(self.rooms.keys()):
            if random.random() < branch_probability:
                self._generate_temporal_branch(room_key, random.randint(2, 5))
    
    def _generate_branch(self, start_coords, length):
        """Generate a branch path from a starting room"""
        current = start_coords
        
        for _ in range(length):
            neighbors = self.get_neighbors(current)
            valid_neighbors = [n for n in neighbors if n not in self.rooms]
            
            if not valid_neighbors:
                break
                
            current = random.choice(valid_neighbors)
            room_type = "treasure" if random.random() < 0.1 else "normal"
            room = Room(current, room_type)
            self.rooms[current] = room
            
            # Connect to previous room
            prev_room = self.rooms[start_coords] if _ == 0 else self.rooms[prev_coords]
            prev_room.connections.add(room)
            room.connections.add(prev_room)
            
            prev_coords = current
    
    def _generate_temporal_branch(self, start_key, length):
        """Generate a branch in 4D space"""
        current_coords, current_time = start_key
        prev_key = start_key
        
        for _ in range(length):
            # Mix spatial and temporal movement
            if random.random() < 0.8:  # Spatial
                neighbors = self.get_neighbors(current_coords)
                valid_neighbors = [n for n in neighbors 
                                 if (n, current_time) not in self.rooms]
                if valid_neighbors:
                    current_coords = random.choice(valid_neighbors)
            else:  # Temporal
                if random.random() < 0.5 and current_time > 0:
                    current_time -= 1
                elif current_time < 2:
                    current_time += 1
            
            new_key = (current_coords, current_time)
            if new_key not in self.rooms:
                room_type = "treasure" if random.random() < 0.1 else "normal"
                room = Room(current_coords, room_type, current_time)
                self.rooms[new_key] = room
                
                # Connect to previous room
                prev_room = self.rooms[start_key] if _ == 0 else self.rooms[prev_key]
                prev_room.connections.add(room)
                room.connections.add(prev_room)
                
                prev_key = new_key

class DungeonVisualizer:
    """Handles visualization of n-dimensional dungeons"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
    
    def visualize_2d(self, generator):
        """Visualize 2D dungeon"""
        plt.figure(figsize=(12, 8))
        
        # Extract coordinates
        coords = list(generator.rooms.keys())
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        
        # Color by room type
        colors = []
        for coords in generator.rooms.keys():
            room = generator.rooms[coords]
            if room.room_type == "start":
                colors.append('green')
            elif room.room_type == "end":
                colors.append('red')
            elif room.room_type == "treasure":
                colors.append('gold')
            else:
                colors.append('lightblue')
        
        # Plot rooms
        plt.scatter(x_coords, y_coords, c=colors, s=100, alpha=0.7)
        
        # Draw connections
        for room in generator.rooms.values():
            for connected_room in room.connections:
                plt.plot([room.coords[0], connected_room.coords[0]], 
                        [room.coords[1], connected_room.coords[1]], 
                        'k-', alpha=0.3, linewidth=1)
        
        # Labels
        plt.scatter([], [], c='green', s=100, label='Start')
        plt.scatter([], [], c='red', s=100, label='End')
        plt.scatter([], [], c='gold', s=100, label='Treasure')
        plt.scatter([], [], c='lightblue', s=100, label='Normal')
        
        plt.title('2D Dungeon Generation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
    def visualize_3d(self, generator):
        """Visualize 3D dungeon"""
        fig = plt.figure(figsize=(14, 10))
        ax: Axes3D = cast(Axes3D, fig.add_subplot(111, projection='3d'))
        
        # Extract coordinates
        coords = list(generator.rooms.keys())
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        z_coords = [c[2] for c in coords]
        
        # Color by room type
        colors = []
        for coords in generator.rooms.keys():
            room = generator.rooms[coords]
            if room.room_type == "start":
                colors.append('green')
            elif room.room_type == "end":
                colors.append('red')
            elif room.room_type == "treasure":
                colors.append('gold')
            else:
                colors.append('lightblue')
        
        # Plot rooms
        ax.scatter(x_coords, y_coords, z_coords, c=colors, marker='o', s=10, alpha=0.7)
        
        # Draw connections
        for room in generator.rooms.values():
            for connected_room in room.connections:
                ax.plot([room.coords[0], connected_room.coords[0]], 
                       [room.coords[1], connected_room.coords[1]], 
                       [room.coords[2], connected_room.coords[2]], 
                       'k-', alpha=0.3, linewidth=1)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z (Layer)')
        ax.set_title('3D Dungeon Generation')
        plt.show()
    
    def visualize_4d(self, generator):
        """Visualize 4D dungeon (3D + time as color)"""
        fig = plt.figure(figsize=(16, 12))
        
        # Group by time state
        time_states = defaultdict(list)
        for key, room in generator.rooms.items():
            if isinstance(key, tuple) and len(key) == 2:
                coords, time_state = key
                time_states[time_state].append((coords, room))
        
        # Create subplots for each time state
        num_states = len(time_states)
        cols = min(3, num_states)
        rows = (num_states + cols - 1) // cols
        
        for i, (time_state, rooms_data) in enumerate(time_states.items()):
            ax: Axes3D = cast(Axes3D, fig.add_subplot(rows, cols, i + 1, projection='3d'))
            
            # Extract coordinates
            coords = [data[0] for data in rooms_data]
            rooms = [data[1] for data in rooms_data]
            
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            z_coords = [c[2] for c in coords]
            
            # Color by room type
            colors = []
            for room in rooms:
                if room.room_type == "start":
                    colors.append('green')
                elif room.room_type == "end":
                    colors.append('red')
                elif room.room_type == "treasure":
                    colors.append('gold')
                elif room.room_type == "temporal":
                    colors.append('purple')
                else:
                    colors.append('lightblue')
            
            # Plot rooms
            ax.scatter(x_coords, y_coords, z_coords, c=colors, s=100, alpha=0.7)
            
            # Draw connections (only within same time state)
            for room in rooms:
                for connected_room in room.connections:
                    if connected_room.time_state == time_state:
                        ax.plot([room.coords[0], connected_room.coords[0]], 
                               [room.coords[1], connected_room.coords[1]], 
                               [room.coords[2], connected_room.coords[2]], 
                               'k-', alpha=0.3, linewidth=1)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'Time State {time_state}')
        
        plt.tight_layout()
        plt.show()

class DungeonTesterGUI:
    """GUI for testing dungeon generation algorithms"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dungeon Generation Tester")
        self.root.geometry("800x600")
        
        self.generator = None
        self.visualizer = DungeonVisualizer()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dimension selection
        ttk.Label(main_frame, text="Dimension:").grid(row=0, column=0, sticky=tk.W)
        self.dim_var = tk.StringVar(value="2D")
        dim_combo = ttk.Combobox(main_frame, textvariable=self.dim_var, 
                                values=["2D", "3D", "4D"], state="readonly")
        dim_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Algorithm selection
        ttk.Label(main_frame, text="Algorithm:").grid(row=1, column=0, sticky=tk.W)
        self.algo_var = tk.StringVar(value="Organic")
        self.algo_combo = ttk.Combobox(main_frame, textvariable=self.algo_var, 
                                      values=["Organic", "Layered", "Temporal"], 
                                      state="readonly")
        self.algo_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Parameters frame
        params_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="5")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Size parameters
        ttk.Label(params_frame, text="Width:").grid(row=0, column=0)
        self.width_var = tk.StringVar(value="20")
        ttk.Entry(params_frame, textvariable=self.width_var, width=10).grid(row=0, column=1)
        
        ttk.Label(params_frame, text="Height:").grid(row=0, column=2)
        self.height_var = tk.StringVar(value="20")
        ttk.Entry(params_frame, textvariable=self.height_var, width=10).grid(row=0, column=3)
        
        ttk.Label(params_frame, text="Branch Prob:").grid(row=1, column=0)
        self.branch_var = tk.StringVar(value="0.3")
        ttk.Entry(params_frame, textvariable=self.branch_var, width=10).grid(row=1, column=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Generate Single", 
                  command=self.generate_single).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Generate Multiple", 
                  command=self.generate_multiple).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Analyze", 
                  command=self.analyze_dungeon).pack(side=tk.LEFT, padx=5)
        
        # Results text area
        self.results_text = tk.Text(main_frame, height=20, width=80)
        self.results_text.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Update algorithm options based on dimension
        dim_combo.bind('<<ComboboxSelected>>', self.update_algorithms)
    
    def update_algorithms(self, event=None):
        """Update available algorithms based on selected dimension"""
        dim = self.dim_var.get()
        if dim == "2D":
            self.algo_combo['values'] = ["Organic", "Grid", "Maze-like"]
        elif dim == "3D":
            self.algo_combo['values'] = ["Layered", "Spiral", "Cave"]
        elif dim == "4D":
            self.algo_combo['values'] = ["Temporal", "Portal", "Quantum"]
        
        self.algo_combo.set(self.algo_combo['values'][0])
    
    def generate_single(self):
        """Generate and visualize a single dungeon"""
        try:
            dim = self.dim_var.get()
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            branch_prob = float(self.branch_var.get())
            
            if dim == "2D":
                self.generator = DungeonGenerator(2, False)
                self.generator.generate_2d_organic(width, height, branch_prob)
                self.visualizer.visualize_2d(self.generator)
            elif dim == "3D":
                self.generator = DungeonGenerator(3, False)
                self.generator.generate_3d_layered(width, height, 5, branch_prob)
                self.visualizer.visualize_3d(self.generator)
            elif dim == "4D":
                self.generator = DungeonGenerator(3, True)
                self.generator.generate_4d_temporal(width, height, 3, 3, branch_prob)
                self.visualizer.visualize_4d(self.generator)
            
            self.log_result(f"Generated {dim} dungeon with {len(self.generator.rooms)} rooms")
            
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {str(e)}")
    
    def generate_multiple(self):
        """Generate multiple dungeons and compare statistics"""
        try:
            dim = self.dim_var.get()
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            branch_prob = float(self.branch_var.get())
            
            results = []
            
            for i in range(10):  # Generate 10 dungeons
                if dim == "2D":
                    gen = DungeonGenerator(2, False)
                    gen.generate_2d_organic(width, height, branch_prob)
                elif dim == "3D":
                    gen = DungeonGenerator(3, False)
                    gen.generate_3d_layered(width, height, 5, branch_prob)
                elif dim == "4D":
                    gen = DungeonGenerator(3, True)
                    gen.generate_4d_temporal(width, height, 3, 3, branch_prob)
                
                # Calculate statistics
                num_rooms = len(gen.rooms)
                num_connections = sum(len(room.connections) for room in gen.rooms.values()) // 2
                treasure_rooms = sum(1 for room in gen.rooms.values() if room.room_type == "treasure")
                
                results.append({
                    'rooms': num_rooms,
                    'connections': num_connections,
                    'treasures': treasure_rooms,
                    'connectivity': num_connections / num_rooms if num_rooms > 0 else 0
                })
            
            # Display statistics
            avg_rooms = sum(r['rooms'] for r in results) / len(results)
            avg_connections = sum(r['connections'] for r in results) / len(results)
            avg_treasures = sum(r['treasures'] for r in results) / len(results)
            avg_connectivity = sum(r['connectivity'] for r in results) / len(results)
            
            self.log_result(f"\n{dim} Dungeon Statistics (10 generations):")
            self.log_result(f"Average Rooms: {avg_rooms:.1f}")
            self.log_result(f"Average Connections: {avg_connections:.1f}")
            self.log_result(f"Average Treasures: {avg_treasures:.1f}")
            self.log_result(f"Average Connectivity: {avg_connectivity:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Multiple generation failed: {str(e)}")
    
    def analyze_dungeon(self):
        """Analyze the current dungeon"""
        if not self.generator:
            messagebox.showwarning("Warning", "Generate a dungeon first!")
            return
        
        try:
            # Path analysis
            if self.generator.start_room and self.generator.end_room:
                path = self.find_shortest_path(self.generator.start_room, self.generator.end_room)
                if path:
                    self.log_result(f"\nShortest path length: {len(path)} rooms")
                else:
                    self.log_result("\nNo path found between start and end!")
            
            # Room type distribution
            room_types = defaultdict(int)
            for room in self.generator.rooms.values():
                room_types[room.room_type] += 1
            
            self.log_result(f"\nRoom distribution:")
            for room_type, count in room_types.items():
                self.log_result(f"  {room_type}: {count}")
            
            # Connectivity analysis
            connections = [len(room.connections) for room in self.generator.rooms.values()]
            avg_connections = sum(connections) / len(connections)
            max_connections = max(connections)
            min_connections = min(connections)
            
            self.log_result(f"\nConnectivity:")
            self.log_result(f"  Average: {avg_connections:.2f}")
            self.log_result(f"  Max: {max_connections}")
            self.log_result(f"  Min: {min_connections}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def find_shortest_path(self, start_room, end_room):
        """Find shortest path between two rooms using BFS"""
        if start_room == end_room:
            return [start_room]
        
        queue = deque([(start_room, [start_room])])
        visited = {start_room}
        
        while queue:
            current_room, path = queue.popleft()
            
            for connected_room in current_room.connections:
                if connected_room == end_room:
                    return path + [connected_room]
                
                if connected_room not in visited:
                    visited.add(connected_room)
                    queue.append((connected_room, path + [connected_room]))
        
        return None  # No path found
    
    def log_result(self, message):
        """Add message to results text area"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

# Example usage and testing
if __name__ == "__main__":
    # Create and run the GUI
    app = DungeonTesterGUI()
    app.run()
    
    # Alternative: Command line testing
    # print("Testing 2D Dungeon Generation...")
    # gen_2d = DungeonGenerator(2, False)
    # gen_2d.generate_2d_organic(20, 20, 0.3)
    # 
    # visualizer = DungeonVisualizer()
    # visualizer.visualize_2d(gen_2d)
    # 
    # print("Testing 3D Dungeon Generation...")
    # gen_3d = DungeonGenerator(3, False)
    # gen_3d.generate_3d_layered(15, 15, 5, 0.25)
    # visualizer.visualize_3d(gen_3d)
    # 
    # print("Testing 4D Dungeon Generation...")
    # gen_4d = DungeonGenerator(3, True)
    # gen_4d.generate_4d_temporal(10, 10, 3, 3, 0.2)
    # visualizer.visualize_4d(gen_4d)