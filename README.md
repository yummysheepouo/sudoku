# Python-based Sudoku 基於 Python 的數獨
Author: Yummysheep <br> You are allowed to copy, download, rewrite or use it personally 
<br><br>作者：Yummysheep<br>您可以複製、下載、改寫或個人使用

### Introduction to the Sudoku Puzzle Program
This Python program creates an interactive Sudoku puzzle game with a command-line interface. It features puzzle loading, solving, validation, and management capabilities, using color-coded visuals for an enhanced user experience.
<br><br>這個 Python 程式創建了一個帶有命令列介面的互動式數獨益智遊戲。它具有謎題載入、求解、驗證和管理功能，並使用顏色編碼的視覺效果來增強使用者體驗。
### Core Features 核心特點
1. **Puzzle Management System 數獨管理系統**
   - Stores puzzles in a dedicated directory with solution files
   - Auto-generates puzzle files on first run
   - Supports three built-in puzzles with solutions
   - Reset functionality to restore puzzles to original state

2. **Interactive Game Modes**
   ```python
   def solve_puzzle(puzzle, file_path):  # Main solving interface
   def check_puzzle(puzzle, file_path):   # Solution validation
   ```
   - `Solve Mode`: Players input moves using `row, column, number` format
   - `Check Mode`: Compare player's solution against correct answer with error highlighting
   - Move-by-move saving system

3. **Visual Interface**
   - Colorama library for terminal coloring
   - Grid layout with row/column indicators
   - Error highlighting (red) for incorrect values
   - Bold separators between 3x3 Sudoku boxes

4. **Puzzle Generation**
   ```python
   def randomize_puzzle(puzzle):  # Creates playable puzzle
   ```
   - Randomly clears 30 cells from solution to create playable puzzle
   - Maintains solvable state while providing challenge

### Technical Components
1. **File Management**
   - Automatic directory creation (`puzzle/`)
   - Solution preservation between sessions
   - File error handling

2. **Input Validation**
   - Robust input checking across all menus
   - Move validation (position availability, digit checks)
   - Error prevention for invalid inputs

3. **User Flow**
   ```
   Main Menu > Load Puzzle > Solve/Check > Reset/Exit
   ```
   - Intuitive menu navigation
   - Contextual help messages
   - Progress saving during gameplay

### Execution
Run from command line:
```bash
python sudoku_puzzle.py
```
The program guides users through puzzle selection and solving with visual feedback and error handling.

This implementation demonstrates file I/O operations, user input validation, grid-based display formatting, and state management in a console application. The color-coded interface and immediate feedback create an engaging puzzle-solving experience while maintaining data integrity through file-based storage.
