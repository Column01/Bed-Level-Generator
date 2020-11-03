import os
import numpy as np


class BedLevelGenerator:
    def __init__(self):
        print("Welcome to Colin's bed level GCODE generator! Follow the on screen prompts and it should generate bed level gcode for your printer!\n")

        self.configure_parameters()
        if self.configured:
            print("Generting gcode...")
            # GCODE for a safe Z move
            self.safe_z_code = "G0 Z{} F{} ; Move Z to safe height\n".format(self.safe_z, self.travel_speed)
            self.header = "G28 ; Home axes\n" \
                          "G21 ; Set units to mm\n" \
                          "G90 ; Set positioning to absolute mode\n" \
                          "\n; DEBUG INFORMATION:\n" \
                          "; max_x: {}, max_y: {}\n" \
                          "; safe_z: {}, travel_speed: {}, pattern: {}\n" \
                          "\n".format(self.max_x, self.max_y, self.safe_z, self.travel_speed, self.pattern)

            try:
                os.mkdir("generated")
            except FileExistsError:
                pass

            output_file_name = os.path.join("generated", "_bed_level-{pattern}@{travel_speed}mm.gcode".format(pattern=self.pattern, travel_speed=self.travel_speed))
            self.gcode_file = open(output_file_name, "w")
            self.generate_gcode()
            print("Generated gcode and outputted to a file: {}".format(output_file_name))
            
    def configure_parameters(self):
        # Configure X and Y dimensions of bed
        while True:
            max_x = input("Please enter the max X coordinate of your print bed in mm: ")
            max_y = input("Please enter the max Y coordinate of your print bed in mm: ")
            try:
                self.max_x = int(max_x)
                self.max_y = int(max_y)
                if self.max_x > 0 and self.max_y > 0:
                    break
                else:
                    print("One or more max dimensions of your printer was not configured. Please enter them again.\n")
            except ValueError:
                print("Please enter numbers for bed dimensions, not letters!\n")
            
        # Get safe Z travel height or default of 10 if the user inputs something wrong
        safe_z = input("Please enter a safe Z height in mm (def: 10mm) to make travel moves or leave blank: ")
        try:
            self.safe_z = int(safe_z)
            if self.safe_z < 5:
                print("Safe Z was less than 5mm, this is not a safe Z height and it has been changed to 5mm!\n")
                self.safe_z = 5
        except ValueError:
            print("Value for safe Z was not a number, using default of 10mm\n")
            self.safe_z = 10

        # Get the desired travel speed or 1500mm/min if the user inputs something wrong
        travel_speed = input("\nPlease enter a number for travel speed (def: 1500) in mm/min or leave blank: ")
        try:
            self.travel_speed = int(travel_speed)
            if self.travel_speed > 5000:
                print("A travel speed greater than 5000mm/min is not safe! Reducing to 5000mm/min\n")
                self.travel_speed = 5000
        except ValueError:
            print("Value for travel speed was not a number, using default of 1500mm/min\n")
            self.travel_speed = 1500

        patterns = ["4", "#", "z"]
        while True:
            print("\nPlease choose a pattern from the following options: "
                  "\nFour corners --- 4"
                  "\nZ Pattern --- z"
                  "\nTic Tac Toe  --- #")
            pattern = input("Enter your choice: ").lower()
            if pattern in patterns:
                self.pattern = pattern
                break
            else:
                print("Invalid pattern: {}. Please enter an option from the list!\n".format(pattern))
        
        num_times = input("\nPlease enter how many times would you like to go over the level cycle: ")

        try:
            self.num_times = int(num_times)
        except ValueError:
            print("Number of times was not a number, defaulting to one loop.\n")
            self.num_times = 1
        
        self.configured = True

    def generate_gcode(self):
        # Macro the write function to reduce processing time
        write_f = self.gcode_file.write

        # Write the header GCODE to configure the printer in the way we need
        write_f(self.header)

        if self.pattern == "4" or self.pattern == "z":
            points = self.get_corners()
        elif self.pattern == "#":
            points = self.get_grid_points(3, 3)
        else:
            points = []

        if len(points) > 0:
            for point in points:
                # Write a safe Z move
                write_f(self.safe_z_code)
                # Go to the point
                write_f(point)
                # Wait the for user to place the paper below the nozzle
                write_f("M0 Place paper below nozzle ; Wait for the user to place the paper below the nozzle\n")
                # Move Z down
                write_f("G0 Z0 F{} ; Move Z down to bed\n".format(self.travel_speed))
                # Wait for the user to adjust the level
                write_f("M0 Adjust level ; Wait for the user to adjust the level\n\n")
        else:
            print("There was an error generating GCODE for the provided inputs.")
        
        # Move to a safe Z height
        write_f(self.safe_z_code)
        # Move to 25, 25 on the print bed
        write_f("G0 X25 Y25 F{} ; Move to 25, 25 and stop\n".format(self.travel_speed))

        # Close the gcode file
        self.gcode_file.close()
        
    def get_corners(self):
        """Generates the GCODE for a 4 corners pattern

        Returns:
            List: A list of conrners (varies in length depending on number of times to loop)
        """
        corners = []
        # Generate a loop to each corner for all times entered
        for _ in range(self.num_times):
            for corner in range(4):

                if corner == 0:
                    corners.append("G0 X15 Y15 F{} ; Move to front left corner\n".format(self.travel_speed))

                elif corner == 1:
                    corners.append("G0 X15 Y{} F{} ; Move to back left corner\n".format(self.max_y - 15, self.travel_speed))

                elif corner == 2:
                    if self.pattern == "4":
                        corners.append("G0 X{} Y15 F{} ; Move to back right corner\n".format(self.max_x - 15, self.travel_speed))
                    elif self.pattern == "z":
                        corners.append("G0 X{} Y{} F{} ; Move to front right corner\n".format(self.max_x - 15, self.max_y - 15, self.travel_speed))

                elif corner == 3:
                    if self.pattern == "4":
                        corners.append("G0 X{} Y{} F{} ; Move to front right corner\n".format(self.max_x - 15, self.max_y - 15, self.travel_speed))
                    elif self.pattern == "z":
                        corners.append("G0 X{} Y15 F{} ; Move to back right corner\n".format(self.max_x - 15, self.travel_speed))
                        
        return corners
    
    def get_grid_points(self, num_rows, num_cols):
        """Generates an arbitrary point grid 15mm from the edge of the bed

        Args:
            num_rows (int): Number of rows (x)
            num_cols ([type]): Number of cols (y)

        Returns:
            List: List of points in the grid
        """
        points = []
        for _ in range(self.num_times):
            cols = list(np.linspace(15, self.max_x - 15, num_cols))
            rows = list(np.linspace(15, self.max_y - 15, num_rows))

            positions = [(x, y) for x in cols for y in rows]
            for pos in positions:
                points.append("G0 X{} Y{} F{} ; Move to point in grid.\n".format(int(pos[0]), int(pos[1]), self.travel_speed))

        print(points)
        return points


if __name__ == "__main__":
    bed_level_generator = BedLevelGenerator()
