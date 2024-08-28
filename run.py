import operator
import random
from visualize_gates import *
import time
import numpy as np
from packer import RectanglePacker, PackedRectangle
from visualize import Visualize
import subprocess
import sys


def parse_input_file(file_path):
    """
    Reads rectangle dimensions from a file.

    Args:
        file_path: The path to the input file.

    Returns:
        A list of tuples representing rectangle dimensions (width, height).
    """
    with open(file_path, "r") as file:
       #p _ = file.readline()  # Skip bounding box line
        rectangles = []
        for line in file:
            dimensions = line.split()
            rectangles.append((int(dimensions[-2]), int(dimensions[-1])))
    return rectangles


def do_rectangles_intersect(rect_a, rect_b):
    """
    Checks if two rectangles overlap.

    Args:
        rect_a, rect_b: PackedRectangle objects.

    Returns:
        True if the rectangles overlap, False otherwise.
    """
    return not (
        rect_b.position[0] >= rect_a.position[0] + rect_a.dimensions[0]
        or rect_b.position[0] + rect_b.dimensions[0] <= rect_a.position[0]
        or rect_b.position[1] >= rect_a.position[1] + rect_a.dimensions[1]
        or rect_b.position[1] + rect_b.dimensions[1] <= rect_a.position[1]
    )


def is_solution_valid(packed_rectangles):
    """
    Checks if a packing solution is valid (no overlaps).

    Args:
        packed_rectangles: A list of PackedRectangle objects.

    Returns:
        True if the solution is valid, False otherwise.
    """
    for i, rect_a in enumerate(packed_rectangles):
        for rect_b in packed_rectangles[i + 1 :]:
            if do_rectangles_intersect(rect_a, rect_b):
                return False
    return True


def calculate_packing_efficiency(rectangles, solution_bounds):
    """
    Calculates the packing efficiency of a solution.

    Args:
        rectangles: A list of tuples representing rectangle dimensions.
        solution_bounds: A SolutionBounds object representing the bounding box of the solution.

    Returns:
        The packing efficiency as a percentage.
    """
    total_rectangle_area = np.sum([width * height for width, height in rectangles])
    solution_area = solution_bounds.dimensions[0] * solution_bounds.dimensions[1]
    return 100 * (total_rectangle_area / solution_area)


def determine_bounding_box(packed_rectangles):
    """
    Determines the bounding box (minimum rectangle enclosing all packed rectangles).

    Args:
        packed_rectangles: A list of PackedRectangle objects.

    Returns:
        A SolutionBounds object representing the bounding box.
    """
    max_x, max_y = 0, 0
    for rect in packed_rectangles:
        bottom_right_x = rect.position[0] + rect.dimensions[0]
        bottom_right_y = rect.position[1] + rect.dimensions[1]
        max_x = max(max_x, bottom_right_x)
        max_y = max(max_y, bottom_right_y)
    return SolutionBounds((max_x, max_y))


def generate_naive_solution(rectangles):
    """
    Generates a naive packing solution (placing rectangles side-by-side).

    Args:
        rectangles: A list of tuples representing rectangle dimensions.

    Returns:
        A list of PackedRectangle objects representing the naive solution.
    """
    x, y = 0, 0
    naive_packed_rectangles = []
    for width, height in rectangles:
        position = (x, y)
        naive_packed_rectangles.append(PackedRectangle(position, (width, height)))
        x += width
    return naive_packed_rectangles


def find_optimal_solution(rectangles):
    """
    Finds the optimal packing solution using different sorting strategies.

    Args:
        rectangles: A list of tuples representing rectangle dimensions.

    Returns:
        A list of PackedRectangle objects representing the optimal solution.
    """

    def sort_by_height_then_width(rectangles):
        return sorted(rectangles, key=operator.itemgetter(1, 0), reverse=True)

    def sort_by_width_then_height(rectangles):
        return sorted(rectangles, key=operator.itemgetter(0, 1), reverse=True)

    def sort_by_area(rectangles):
        return sorted(rectangles, key=lambda x: x[0] * x[1], reverse=True)

    def sort_by_max_side(rectangles):
        return sorted(rectangles, key=lambda x: max(x[0], x[1]), reverse=True)

    sorting_strategies = [
        sort_by_height_then_width,
        sort_by_width_then_height,
        sort_by_area,
        sort_by_max_side,
    ]

    best_solution = None
    min_area = float("inf")

    for strategy in sorting_strategies:
        sorted_rectangles = strategy(rectangles.copy())
        packer = RectanglePacker()
        current_solution = packer.arrange_rectangles(sorted_rectangles)
        solution_bounds = determine_bounding_box(current_solution)
        current_area = solution_bounds.dimensions[0] * solution_bounds.dimensions[1]

        if current_area < min_area:
            min_area = current_area
            best_solution = current_solution

    return best_solution


def save_results_to_file(rectangles, packed_rectangles, output_file_path, bounding_box_width, bounding_box_height):
    """
    Writes the packing solution to a file.

    Args:
        rectangles: A list of tuples representing rectangle dimensions.
        packed_rectangles: A list of PackedRectangle objects.
        output_file_path: The path to the output file.
        bounding_box_width, bounding_box_height: Dimensions of the bounding box.
    """
    dimensions_to_location = {rect.dimensions: rect.position for rect in packed_rectangles}
    with open(output_file_path, "w") as file:
        file.write(f"bounding_box {bounding_box_width} {bounding_box_height}\n")
        for i, (width, height) in enumerate(rectangles):
            position = dimensions_to_location.get((width, height))
            if position:
                file.write(f"g{i + 1} {position[0]} {bounding_box_height - height - position[1]}\n")


class SolutionBounds:
    """
    Represents the bounding box of a packing solution.
    """

    def __init__(self, dimensions):
        self.dimensions = dimensions

    def calculate_perimeter(self):
        """
        Calculates the perimeter of the bounding box.

        Returns:
            The perimeter.
        """
        return (self.dimensions[0] + self.dimensions[1]) * 2


import operator
import random

import time
import numpy as np
from packer import RectanglePacker, PackedRectangle  # Assuming you've made the changes to packer.py as well
import os


def main(input_file, output_file):
    """
    Main function to run the rectangle packing process.
    """
    
    rectangles = parse_input_file(input_file_path)

    naive_packed_rectangles = generate_naive_solution(rectangles)

    start_time = time.time()
    optimal_packed_rectangles = find_optimal_solution(rectangles)
    elapsed_time = time.time() - start_time

    print(f"Solution found in {elapsed_time:.2f} seconds")

    optimal_bounds = determine_bounding_box(optimal_packed_rectangles)
    naive_bounds = determine_bounding_box(naive_packed_rectangles)
    packing_efficiency = calculate_packing_efficiency(rectangles, optimal_bounds)
    bounding_box_width, bounding_box_height = optimal_bounds.dimensions
    

    # Write the results to the output file
    save_results_to_file(
        rectangles, optimal_packed_rectangles, output_file_path, bounding_box_width, bounding_box_height
    )

    # This is slow
    # if not is_solution_valid(optimal_packed_rectangles):
    #     print("Solution invalid.  Overlap detected.")

    print("Dimensions of solution are {}.".format(optimal_bounds.dimensions))
    print("Perimeter of solution is {}.".format(optimal_bounds.calculate_perimeter()))
    print("Dimensions of naive solution are {}.".format(naive_bounds.dimensions))
    print("Perimeter of naive solution is {}.".format(naive_bounds.calculate_perimeter()))
    print("Percentage improvement is {}.".format(
        (100 - (optimal_bounds.calculate_perimeter() / naive_bounds.calculate_perimeter()) * 100)
    ))
    print("Packing Fraction is {}".format(packing_efficiency))


    try:
        import pygame
        assert pygame
        pass
    except (ImportError, AssertionError):
        print("Pygame not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])

    """
    Implementation of the new visualizing tool
    """

    # visualizer = Visualize(optimal_packed_rectangles, optimal_bounds)
    # visualizer.display()
    

    
    root = visualize_gates( input_file, output_file, (50,50))
    root.mainloop()
  

    

# Runs the code.
if __name__ == "__main__":
    main("input.txt", "output.txt")
