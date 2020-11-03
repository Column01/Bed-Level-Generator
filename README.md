# Bed Level GCODE generator

A GCODE generator that generates patterns to help you level your printer bed! Only works for square or rectangle beds! (Delta could be supported at a later date if requested)

## Installation

1. Download or clone the repository
2. Install Python 3.6 or greater
3. Install dependencies with `pip install -r requirements.txt`
4. Run the script with `python bed_level_generator.py` and answer the prompts
5. Go to the newly created folder and GCODE file, copy it to your SD card or send it to your printer and follow the prompts on the LCD

## Patterns

- **Four corners - `4`**
  - Generates a point in each corner that is 15mm from the edge of the bed and moves in a "square" fashion (FL, BL, BR, FL)
- **Z pattern - `z`**
  - Generates a point in each corner 15mm from the edge, except it travels in a Z formation (FL, BL, FR, BR)
- **Tic Tac Toe - `#`**
  - Generates a 9 point grid across your bed 15mm from the edge and travels in columns (Bottom to Top)
- **Suggest more in an issue on this repository!**

## Plans

- Add more patterns.
- Possibly add a visualization of printer moves and a UI for entering the parameters.
- Package into an executable for ease of use.
