from tkinter import *
from routing_cube import RoutingCube  # Assuming this module and class exist
from ThreeD import ThreeD

class TestUI:

    # Constants

    queue_size = 4

    # cube dimensions
    routing_cube_x = 25
    routing_cube_y = 25

    # queue dimensions
    queue_x = 12
    queue_y = 12

    # Class Definition
    def __init__(self, canvas_height=1000, canvas_width=1500):
        # Creating window
        self.window = Tk()
        # Setting height
        self.canvas_height = canvas_height
        # Setting width
        self.canvas_width = canvas_width
        # Creating canvas size
        self.canvas = Canvas(self.window, height=canvas_height, width=canvas_width)
        self.canvas.pack()
        # Setting array
        self.arr = None

    def create_routing_cube(self, x, y):
        self.canvas.create_rectangle(x, y, x + self.routing_cube_x, y + self.routing_cube_y, fill="white", outline='black')

    def create_line(self, x, y):
        self.canvas.create_rectangle(x, y, x + self.routing_cube_x, y + self.routing_cube_y, fill="white", outline='black')

    def create_routing_queue(self, pos, x, y):
        if pos == "North":
            for j in range(y,  y - (self.queue_size * self.queue_y), -self.queue_y):
                self.canvas.create_rectangle(x + (self.queue_x/2) , j, x + self.queue_x + (self.queue_x/2), j - self.queue_y, fill="white", outline='black')
        elif pos == "South":
            for j in range(y + self.routing_cube_y , (y + self.routing_cube_y) + (self.queue_size * self.queue_y), self.queue_y):
                self.canvas.create_rectangle(x + (self.queue_x/2) , j, x + self.queue_x + (self.queue_x/2), j + self.queue_y, fill="white", outline='black')
        elif pos == "East":
            for i in range(x + self.routing_cube_x, (x + self.routing_cube_x) + (self.queue_size * self.queue_x), self.queue_x):
                self.canvas.create_rectangle(i, y + (self.queue_y/2), i + self.queue_x, y + self.queue_y + (self.queue_y/2), fill="white", outline='black')
        elif pos == "West":
             for i in range(x , x - (self.queue_size * self.queue_x), -self.queue_x):
                self.canvas.create_rectangle(i, y + (self.queue_y/2), i - self.queue_x, y + self.queue_y + (self.queue_y/2), fill="white", outline='black')

        
       

    def draw_environment(self):
        start_pos_x = self.routing_cube_x
        end_pos_x = self.canvas_width - self.routing_cube_x
        start_pos_y = self.routing_cube_y
        end_pos_y = self.canvas_height - self.routing_cube_y

        # X increment
        x_increment =  2*(self.queue_x * (self.queue_size + 1)) + self.routing_cube_x
        y_increment =  2*(self.queue_y* (self.queue_size + 1)) + self.routing_cube_y

        # Number of cubes
        num_cubes_x = round(end_pos_x/x_increment)
        num_cubes_y = round(end_pos_y/y_increment)

        # Printing cube size
        #print("The max amount of cubes in x axis:" + str(num_cubes_x))
        #print("The max amount of cubes in y axis:" + str(num_cubes_y))

        #print("========================================================")

        # Instatating arr
        arr = ThreeD(x=num_cubes_x, y=num_cubes_y, z=1)
        arr.print()

        #print("========================================================")
        
#        arr.set_element(x=8,y=0,z=0,element="hi")
#        arr.print()
#        arr.get_element(x=8,y=0,z=0)

        #print("========================================================")
        arr.random_populate(RoutingCube())
        arr.print()

        curr_cube_x = 0
        # Variable queue size
        for x in range(start_pos_x, end_pos_x, 2*(self.queue_x * (self.queue_size + 1)) + self.routing_cube_x):
            curr_cube_y = 0
            for y in range(start_pos_y, end_pos_y, 2*(self.queue_y* (self.queue_size + 1)) + self.routing_cube_y):

                # Current Routing Cube
                if(arr.get_element(curr_cube_x,curr_cube_y,0) != None):
                    print("=====================================================")
                    print(arr.get_element(curr_cube_x,curr_cube_y,0))
                    print(arr.is_neighbor(curr_cube_x,curr_cube_y,0))
                    self.create_routing_cube(x, y) 
                    next_x =  x + 2*(self.queue_x * (self.queue_size + 1)) + self.routing_cube_x
                    next_y = y + 2*(self.queue_y* (self.queue_size + 1)) + self.routing_cube_y
                
                    if(x > start_pos_x):
                        self.create_routing_queue(x=x,y=y, pos="West")
                  
                    if(next_x < end_pos_x):
                        self.create_routing_queue(x=x,y=y,pos="East")
                
                    if(y > start_pos_y):
                        self.create_routing_queue(x=x,y=y,pos="North")

                    if(next_y < end_pos_y):
                        self.create_routing_queue(x=x,y=y,pos="South")
                curr_cube_y+=1
            curr_cube_x+=1
                
    # Window Start Method
    def window_start(self):
        self.draw_environment()
        self.window.mainloop()

# Creating an instance of the TestUI class and starting the window
if __name__ == "__main__":
    # Window Dimensions
    window_height = 900
    window_width = 1000

    # Creating an instance of TestUI and passing the ThreeD instance
    ui = TestUI()

    # Starting the window
    ui.window_start()
