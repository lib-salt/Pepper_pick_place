import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import datetime
import math

class PepperRobotMap(object):
    def __init__(self, map_size=(5, 5), save_dir=None):

        plt.close('all')  # Close existing plots 
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        
        self.ax.set_xlim(map_size[0]/2.0, -map_size[0]/2.0)
        self.ax.set_ylim(-map_size[1]/2.0, map_size[1]/2.0)
        
        self.ax.set_title("Pepper Robot Object Localisation")
        self.ax.set_xlabel("Lateral Distance (meters)")
        self.ax.set_ylabel("Forward Distance (meters)")
        self.ax.grid(True, linestyle='--', alpha=0.7)

        # Set save directory
        if save_dir is None:
            save_dir = os.path.join(os.getcwd(), 'robot_maps')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        self.save_dir = save_dir

        self.colour_map = {
            'bottle': 'red',
            'cup': 'green',
            'remote': 'purple',
            'default': 'blue'
        }
        
        # Robot starts at centre of map
        self.current_robot_pos = {'x': 0, 'y': 0, 'theta': 0}
        
        # Force matplotlib to use ASCII
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = ['Arial']
        
        # Add a legend to the map
        self._create_legend()

    def _create_legend(self):
        # Create legend elements
        legend_elements = [
            patches.Patch(facecolor='blue', edgecolor='black', alpha=0.7, label='Actual Robot Position'),
            patches.Patch(facecolor='green', edgecolor='black', alpha=0.7, label='Target Robot Position'),
            plt.Line2D([0], [0], color='blue', lw=2, alpha=0.5, label='Robot Path'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Bottle'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Cup'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=10, label='Remote')
        ]
        
        # Add the legend to the axis
        self.ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    def draw_robot(self, x=0, y=0, theta=0, color='blue', alpha=0.7):
        # Draw robot
        robot_points = np.array([
            [0, 0.3],      # front
            [-0.2, -0.3],  # back left
            [0.2, -0.3]    # back right
        ])
        
        # Rotate points based on theta
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        
        rotation_matrix = np.array([
            [cos_theta, -sin_theta],
            [sin_theta, cos_theta]
        ])
        
        # Apply rotation and translation
        rotated_points = np.dot(robot_points, rotation_matrix.T)
        transformed_points = rotated_points + np.array([y, x])  # Note: x is forward, y is lateral
        
        # Create robot patch
        robot = patches.Polygon(
            transformed_points, 
            closed=True, 
            fill=True, 
            facecolor=color, 
            alpha=alpha,
            edgecolor='black'  
        )
        
        return self.ax.add_patch(robot)

    def clear_objects(self):
        # Remove existing collections and texts
        collections = self.ax.collections[:]
        texts = self.ax.texts[:]
        patches = self.ax.patches[:]
        lines = self.ax.lines[:]
        
        for collection in collections:
            collection.remove()
        
        for text in texts:
            text.remove()
            
        for patch in patches:
            patch.remove()
            
        for line in lines:
            line.remove()
            
        # Recreate the legend after clearing
        self._create_legend()

    def add_object(self, x_forward, y_lateral, category, depth=None):
        # Add object to map
        colour = self.colour_map.get(category.lower(), 'gray')
        
        # Plot object as a scatter point
        self.ax.scatter(y_lateral, x_forward, color=colour, s=100, alpha=0.7, edgecolor='black')
        
        # Add category label
        label_text = "{} (X: {:.2f}, Y: {:.2f})".format(str(category), x_forward, y_lateral)
        
        if depth is not None:
            label_text += '\n{:.2f}m'.format(depth)
        
        self.ax.annotate(
            label_text, 
            (y_lateral, x_forward), 
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=9,
            color='black'
        )

    def draw_robot_positions(self, robot_positions, target_positions):
        # Draw path to robot positions

        if len(robot_positions) > 0:
            # Actual positions
            actual_x_coords = [pos['y'] for pos in robot_positions]  # lateral
            actual_y_coords = [pos['x'] for pos in robot_positions]  # forward
            
            # Plot the path
            if len(robot_positions) > 1:
                self.ax.plot(actual_x_coords, actual_y_coords, 'b-', alpha=0.5, linewidth=2)
            
            # Add numbered markers at each actual position
            for i, (x, y) in enumerate(zip(actual_x_coords, actual_y_coords)):
                self.ax.scatter(x, y, color='blue', s=80, alpha=0.7, edgecolor='black', zorder=5)
                self.ax.text(x, y, str(i), ha='center', va='center', color='white', 
                            fontsize=9, fontweight='bold', zorder=6)
                
                # Add position details below the marker
                pos = robot_positions[i]
                details = "A{0}: ({1:.2f}, {2:.2f}, θ:{3:.2f})".format(i, pos['x'], pos['y'], pos['theta'])
                self.ax.text(x, y-0.2, details, ha='center', va='center', 
                        fontsize=8, color='blue', bbox=dict(facecolor='white', alpha=0.7))

        # Target positions
        if len(target_positions) > 0:
            target_x_coords = [pos['y'] for pos in target_positions]  # lateral
            target_y_coords = [pos['x'] for pos in target_positions]  # forward
            
            # Add markers at each target position
            for i, (x, y) in enumerate(zip(target_x_coords, target_y_coords)):
                self.ax.scatter(x, y, color='green', marker='x', s=100, alpha=0.7, linewidth=2, zorder=5)
                self.ax.text(x, y-0.1, "T"+str(i), ha='center', va='center', color='green', 
                            fontsize=9, fontweight='bold', zorder=6)
                
                # Add target position details
                pos = target_positions[i]
                details = "T{0}: ({1:.2f}, {2:.2f}, θ:{3:.2f})".format(i, pos['x'], pos['y'], pos['theta'])
                self.ax.text(x, y+0.2, details, ha='center', va='center', 
                        fontsize=8, color='green', bbox=dict(facecolor='white', alpha=0.7))
                
                # Checks for corresponding actual positions
                if i < len(robot_positions)  and i + 1 < len(robot_positions):  
                    # +1 because target corresponds to next position
                    actual_x = actual_x_coords[i+1] 
                    actual_y = actual_y_coords[i+1]
                    # Draw dotted line between target and actual
                    self.ax.plot([x, actual_x], [y, actual_y], 'r--', alpha=0.5, linewidth=1)
                    
                    # Calculate and show the error
                    error = math.sqrt((x - actual_x)**2 + (y - actual_y)**2)
                    midx = (x + actual_x) / 2
                    midy = (y + actual_y) / 2
                    self.ax.text(midx, midy, "err: {:.2f}m".format(error), ha='center', va='center',
                                color='red', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

    def update_map(self, new_objects, robot_positions=None, target_positions=None):
        # Update map and robot positions
        self.clear_objects()
        
        # Draw the robot paths and positions
        if robot_positions:
            self.draw_robot_positions(robot_positions, target_positions or [])
            
            # Draw the current robot position 
            if len(robot_positions) > 0:
                current_pos = robot_positions[-1]
                self.draw_robot(
                    x=current_pos['x'], 
                    y=current_pos['y'], 
                    theta=current_pos['theta'],
                    color='blue',
                    alpha=0.8
                )
                
                # Draw the latest target position if available
                if target_positions and len(target_positions) > 0:
                    latest_target = target_positions[-1]
                    self.draw_robot(
                        x=latest_target['x'],
                        y=latest_target['y'],
                        theta=latest_target['theta'],
                        color='green',
                        alpha=0.5
                    )
                
                # Save current position
                self.current_robot_pos = current_pos
        else:
            # If no positions provided, draw robot at center 
            self.draw_robot()
        
        # Add objects
        for obj in new_objects:
            x_forward = obj.get('x_forward', 0)
            y_lateral = obj.get('y_lateral', 0)
            category = obj.get('category', 'unknown')
            depth = obj.get('depth')
            
            # Add the object to the map
            self.add_object(x_forward, y_lateral, category, depth)

    def save(self, filename=None):
        # Save the map to a file
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = "pepper_robot_map_{}.png".format(timestamp)
            
            # Full path to save
            filepath = os.path.join(self.save_dir, filename)
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=300)
            plt.close(self.fig)  
            
            print("Map saved to {}".format(filepath))
            return filepath
        
        except Exception as e:
            print("Error saving map: {}".format(str(e)))
            return None