# Python-based Sudoku 基於 Python 的數獨
Author: Yummysheep <br> You are allowed to copy, download, rewrite or use it personally 
<br><br>作者：Yummysheep<br>您可以複製、下載、改寫或個人使用

### Introduction to the Sudoku Puzzle Program 數獨謎題程序簡介
This Python program creates an interactive Sudoku puzzle game with a command-line interface. It features puzzle loading, solving, validation, and management capabilities, using color-coded visuals for an enhanced user experience.
<br><br>這個 Python 程式創建了一個帶有命令列介面的互動式數獨益智遊戲。它具有謎題載入、求解、驗證和管理功能，並使用顏色編碼的視覺效果來增強使用者體驗。
### Core Features 核心特點
1. **Puzzle Management System 數獨管理系統**
   - Stores puzzles in a dedicated directory with solution files 將謎題與解決方案檔案一起儲存在專用目錄中
   - Auto-generates puzzle files on first run 首次運行時自動產生拼圖文件
   - Supports three built-in puzzles with solutions 支援三個內置謎題及其解決方案
   - Reset functionality to restore puzzles to the original state 重置功能可將拼圖恢復到原始狀態

2. **Interactive Game Modes 互動遊戲模式**
   ```python
   def solve_puzzle(puzzle, file_path):  # Main solving interface
   def check_puzzle(puzzle, file_path):   # Solution validation
   ```
   - `Solve Mode 遊玩模式`: Players input moves using `row, column, number` format 玩家使用「行、列、數字」格式輸入動作
   - `Check Mode 檢查答案`: Compare player's solution against correct answer with error highlighting 將玩家的解決方案與正確答案進行比較，並突出顯示錯誤
   - Move-by-move saving system 逐步儲存系統

3. **Visual Interface 可視化介面**
   - Colorama library for terminal colouring 使用了終端著色的 Colorama 庫
   - Grid layout with row/column indicators 帶有行/列指示符的網格佈局
   - Error highlighting (red) for incorrect values 錯誤值突出顯示（紅色）
   - Bold separators between 3x3 Sudoku boxes 3x3 數獨框之間的粗體分隔符

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
