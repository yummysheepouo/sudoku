import os
import time
import random
from colorama import Fore, Style, Back
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUZZLE_DIR = os.path.join(BASE_DIR, "puzzle")  

PUZZLE_CONTENTS = {
    "puzzle1.txt": [
        "476598312",
        "852961437",
        "394287615",
        "719854632",
        "263693814",
        "648125739",
        "921346827",
        "137782469",
        "586473915"
    ],
    "puzzle1S.txt": [
        "476598312",
        "852961437",
        "394287615",
        "719854632",
        "263693814",
        "648125739",
        "921346827",
        "137782469",
        "586473915"
    ],
    "puzzle2.txt": [
        "381654729",
        "729381564",
        "564729318",
        "693217845",
        "857496213",
        "412835697",
        "248913675",
        "175264938",
        "936748251"
    ],
    "puzzle2S.txt": [
        "381654729",
        "729381564",
        "564729318",
        "693217845",
        "857496213",
        "412835697",
        "248913675",
        "175264938",
        "936748251"
    ],
    "puzzle3.txt": [
        "219348765",
        "765219348",
        "348765219",
        "672984513",
        "984513672",
        "513672984",
        "456723198",
        "897146235",
        "132895476"
    ],
    "puzzle3S.txt": [
        "219348765",
        "765219348",
        "348765219",
        "672984513",
        "984513672",
        "513672984",
        "456723198",
        "897146235",
        "132895476"
    ]
}

def initialize_puzzle_files():
    
    if not os.path.exists(PUZZLE_DIR):
        os.makedirs(PUZZLE_DIR)
    
    for filename, content in PUZZLE_CONTENTS.items():
        file_path = os.path.join(PUZZLE_DIR, filename)
        if not os.path.exists(file_path):
            
            with open(file_path, 'w') as file:
                for line in content:
                    file.write(line + "\n")

def load_puzzle():
    
    while True:
        filename = input(Fore.BLUE + "Enter puzzle filename\n(no need to enter '.txt')\nChoices:\npuzzle1\npuzzle2\npuzzle3\n\nNOW enter your choice: " + Style.RESET_ALL).strip()
       
        if not filename:
            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Error: Please enter a filename." + Style.RESET_ALL)
            continue
            
        full_path = os.path.join(PUZZLE_DIR, filename + ".txt")
        
        try:
            if not os.path.exists(full_path):
                available_files = [f for f in os.listdir(PUZZLE_DIR) if f.endswith('.txt')]
                print(Back.RED + Fore.WHITE + Style.BRIGHT + f"Error: Puzzle '{filename}' does not exist" + Style.RESET_ALL)
                continue
                
            with open(full_path, 'r') as file:
                puzzle = [list(line.strip()) for line in file.readlines()]
                time.sleep(0.5)
                print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Puzzle loaded! Back to the main menu and press 's' to enter solve mode!" + Style.RESET_ALL)
                return puzzle, full_path
        except Exception as e:
            print(Back.RED + Fore.WHITE + Style.BRIGHT + f"Error loading puzzle: {str(e)}" + Style.RESET_ALL)

def randomize_puzzle(puzzle):
    
    empty_positions = set()
    while len(empty_positions) < 30:
        row = random.randint(0, len(puzzle) - 1)
        col = random.randint(0, len(puzzle[row]) - 1)
        if puzzle[row][col] != '.':
            puzzle[row][col] = '.'
            empty_positions.add((row, col))
    return puzzle

def print_puzzle(puzzle, solution=None):
    
    print("    " + "   ".join(str(i) for i in range(1, 10)))
    print("  +" + "---+" * 9)

    for i, row in enumerate(puzzle, start=1):
        print(f"{i} | ", end="")
        for j, cell in enumerate(row):
            
            if solution and cell != '.' and cell != solution[i-1][j]:
                print(Fore.RED + cell + Style.RESET_ALL, end="")
            else:
                print(cell, end="")
            if j < len(row) - 1:
                print(" | ", end="")
        print(" |")
        if i % 3 == 0 and i < 9:  
            print("  +" + "===+" * 9)
        else:
            print("  +" + "---+" * 9)

def solve_puzzle(puzzle, file_path):
    
    print_puzzle(puzzle)
    print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Entered Solve puzzle mode" + Style.RESET_ALL)

    while True:
        time.sleep(0.5)
        move = input(Fore.BLUE + "Enter your move (row, column, number) or 'X' to exit: " + Style.RESET_ALL).strip().upper()

        if move == 'X':
            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Exiting solve puzzle mode. Progress Saved" + Style.RESET_ALL)
            time.sleep(0.5)
            break

        if len(move) != 3 or not move.isdigit():
            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Invalid input format. Use 'row column number' (e.g. 359)." + Style.RESET_ALL)
            continue

        row, col, num = int(move[0]) - 1, int(move[1]) - 1, move[2]

        if not (0 <= row < len(puzzle)) or not (0 <= col < len(puzzle[row])):
            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Invalid row or column index. Try again." + Style.RESET_ALL)
            continue

        if puzzle[row][col] != '.':
            print(Back.RED + Fore.WHITE + Style.BRIGHT + f"Error: Position {row+1}, {col+1} is already occupied." + Style.RESET_ALL)
            continue

        puzzle[row][col] = num

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as file:
            for row_data in puzzle:
                file.write("".join(row_data) + "\n")

        print(Fore.GREEN + "Puzzle updated successfully!" + Style.RESET_ALL)
        print_puzzle(puzzle)
            
def check_puzzle(puzzle, file_path):
   
    if puzzle is None:
        print(Back.RED + Fore.WHITE + Style.BRIGHT + "Error: No puzzle loaded. Please load a puzzle first." + Style.RESET_ALL)
        return None, None  

    solution_file = file_path.replace(".txt", "S.txt")
    
    try:
        
        os.makedirs(os.path.dirname(solution_file), exist_ok=True)
        
        with open(solution_file, 'r') as file:
            solution = [list(line.strip()) for line in file.readlines()]
            
            
            print("\n" + Fore.CYAN + "Choose check method:" + Style.RESET_ALL)
            print("1. Show solution only")
            print("2. Compare with my answer (errors in red)")
            
           
            while True:
                choice = input(Fore.BLUE + "Enter your choice (1 or 2): " + Style.RESET_ALL).strip()
                
                if choice in ["1", "2"]:
                    break
                else:
                    print(Back.RED + Fore.WHITE + Style.BRIGHT + "Invalid choice. Please enter 1 or 2." + Style.RESET_ALL)
            
            if choice == "1":
                
                print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Final Solution:" + Style.RESET_ALL)
                print_puzzle(solution)
            elif choice == "2":
                
                print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Your Solution (errors in red):" + Style.RESET_ALL)
                print_puzzle(puzzle, solution)
                print(Fore.RED + "Red numbers indicate incorrect values" + Style.RESET_ALL)
                
            return solution, solution_file
            
    except FileNotFoundError:
        time.sleep(0.5)
        print(Back.RED + Fore.WHITE + Style.BRIGHT + "Error: Solution file not found. Make sure the correct solution file exists." + Style.RESET_ALL)
        return None, None
    
    return None, None

def reset_all_puzzles():
    
    print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Resetting all puzzles to initial state..." + Style.RESET_ALL)
    time.sleep(1)
    
    for i in range(1, 4):
        puzzle_file = os.path.join(PUZZLE_DIR, f"puzzle{i}.txt")
        solution_file = os.path.join(PUZZLE_DIR, f"puzzle{i}S.txt")
        
        if os.path.exists(solution_file):
            try:
                shutil.copyfile(solution_file, puzzle_file)
                time.sleep(1)
            except Exception as e:
                print(Back.RED + Fore.WHITE + Style.BRIGHT + f"✗ Error resetting puzzle{i}.txt: {str(e)}" + Style.RESET_ALL)
        else:
            print(Back.YELLOW + Fore.BLACK + Style.BRIGHT + f"⚠ Solution file for puzzle{i} not found" + Style.RESET_ALL)
    
    print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "✓ All puzzles have been reset to their initial state!" + Style.RESET_ALL)
    time.sleep(1)
    return True

def load_puzzle_for(puzzle_name):
    
    full_path = os.path.join(PUZZLE_DIR, puzzle_name + ".txt")
    
    try:
        with open(full_path, 'r') as file:
            puzzle = [list(line.strip()) for line in file.readlines()]
            return puzzle, full_path
    except Exception as e:
        print(Back.RED + Fore.WHITE + Style.BRIGHT + f"Error loading puzzle: {str(e)}" + Style.RESET_ALL)
        return None, None

def main_menu():
    puzzle = None  
    file_path = None
    
    initialize_puzzle_files()

    while True:
        time.sleep(0.5)
        print(Style.RESET_ALL + Fore.MAGENTA + Style.BRIGHT + "===================\nMain Menu\n===================" + Style.RESET_ALL)
        print(Fore.GREEN + "L - Load new puzzle")
        print("S - Solve puzzle (solve mode)")
        print("C - Check solution")
        print("R - Reset all puzzles")
        print("X - Exit")
        
        choice = input(Fore.BLUE + "Enter your choice: ").strip().upper()

        if choice == 'L':
            time.sleep(0.5)
            puzzle_data = load_puzzle()
            if puzzle_data:
                puzzle, file_path = puzzle_data  
                puzzle = randomize_puzzle(puzzle) 
        elif choice == 'S':
            time.sleep(1)
            if puzzle:
                solve_puzzle(puzzle, file_path)  
            else:
                print(Back.RED + Fore.WHITE + Style.BRIGHT + "Error: No puzzle loaded. Please load a puzzle first." + Style.RESET_ALL)
        elif choice == 'R':
            if reset_all_puzzles():
                puzzle = None
                file_path = None
        elif choice == 'X':
            exit_choice = input(Fore.RED + "Are you sure to exit? Progress won't be saved! Input Y to exit or N to stay: ").strip().upper()
            if exit_choice == 'Y':
                print(Back.RED + Fore.WHITE + Style.BRIGHT + "Exiting the program." + Style.RESET_ALL)
                time.sleep(0.5)
                
                for i in range(1, 4):
                    puzzle_file = os.path.join(PUZZLE_DIR, f"puzzle{i}.txt")
                    solution_file = os.path.join(PUZZLE_DIR, f"puzzle{i}S.txt")
                    
                    if os.path.exists(solution_file):
                        try:
                            shutil.copyfile(solution_file, puzzle_file)
                        except Exception as e:
                            print(Back.RED + Fore.WHITE + Style.BRIGHT + f"Error updating puzzle{i}.txt: {str(e)}" + Style.RESET_ALL)
                    else:
                        print(Back.YELLOW + Fore.BLACK + Style.BRIGHT + f"Solution file for puzzle{i} not found" + Style.RESET_ALL)
                
                break
            else:
                continue  
        
        elif choice == "C":
            time.sleep(0.5)
            if puzzle:
                solution, solution_file = check_puzzle(puzzle, file_path)
                
                if solution:
                    print("\n" + Fore.CYAN + "Next steps:" + Style.RESET_ALL)
                    print("1. Back to Main Menu")
                    print("2. Reset all puzzles")
                    
                   
                    while True:
                        reset_choice = input(Fore.BLUE + "Enter your choice (1 or 2): " + Style.RESET_ALL).strip()
                        
                        if reset_choice in ["1", "2"]:
                            break
                        else:
                            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Invalid choice. Please enter 1 or 2." + Style.RESET_ALL)
                    
                    if reset_choice == "2":
                        if reset_all_puzzles():
                            puzzle = None
                            file_path = None
                            print(Fore.YELLOW + "All puzzles have been reset. Please load a puzzle again from the main menu." + Style.RESET_ALL)
            else:
                print(Back.RED + Fore.WHITE + Style.BRIGHT + "Error: No puzzle loaded. Please load a puzzle first." + Style.RESET_ALL)

        else:
            time.sleep(0.5)
            print(Back.RED + Fore.WHITE + Style.BRIGHT + "Invalid choice. Please try again." + Style.RESET_ALL)

if __name__ == "__main__":
    main_menu()

