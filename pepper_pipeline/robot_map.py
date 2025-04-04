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
        
        self.ax.set_xlim(-map_size[0]/2.0, map_size[0]/2.0)
        self.ax.set_ylim(-map_size[1]/2.0, map_size[1]/2.0)
        
        self.ax.set_title("Pepper Robot Object Localization")
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
        
        # Draw robot at center
        self.draw_robot()

    def draw_robot(self):
        # Draw robot at the center of the map
        robot = patches.Polygon(
            [(0, 0.3), (-0.2, -0.3), (0.2, -0.3)], 
            closed=True, 
            fill=True, 
            color='blue', 
            alpha=0.7
        )
        self.ax.add_patch(robot)

    def clear_objects(self):
        # Remove existing collections and texts
        collections = self.ax.collections[:]
        texts = self.ax.texts[:]
        
        for collection in collections:
            collection.remove()
        
        for text in texts:
            text.remove()

    def add_object(self, x_forward, theta, category, depth=None):

        self.clear_objects()
        colour = self.colour_map.get(category.lower(), 'gray')

        y_lateral = depth * math.sin(theta)
        
        # Plot object as a scatter point
        self.ax.scatter(y_lateral, x_forward, color=colour, s=100, alpha=0.7, edgecolor='black')
        
        # Add category label
        label_text = category + '(X: {:.3f}, Y: {:.3f})'.format(x_forward, y_lateral)
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

    def update_map(self, new_objects):
        # Clear previous objects
        self.clear_objects()
        
        # Redraw robot
        self.draw_robot()
        
        # Add new objects
        for obj in new_objects:
            self.add_object(
                obj.get('x_forward', 0), 
                obj.get('y_lateral', 0), 
                obj.get('category', 'unknown'), 
                obj.get('depth')
            )

    def save(self, filename=None):
      
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
            print("Error saving map: {}").format(e)
            return None

# Test to check if working
if __name__ == '__main__':
    # Sample data for testing
    sample_objects = [
        {
            'x_forward': 1.0, 
            'y_lateral': 0.5, 
            'category': 'bottle', 
            'depth': 1.2
        },
        {
            'x_forward': 2.0, 
            'y_lateral': -0.3, 
            'category': 'cup', 
            'depth': 1.5
        }
    ]

    # Create map and update with sample objects
    robot_map = PepperRobotMap(save_dir='.')
    robot_map.update_map(sample_objects)
    robot_map.save()