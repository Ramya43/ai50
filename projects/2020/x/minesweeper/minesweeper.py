import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if (len(self.cells) == self.count):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            if self.count > 0:
                self.count = self.count-1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """        
        #  1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        #  2) mark the cell as safe
        self.safes.add(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # ??? Be sure to only include cells whose state is still undetermined in the sentence.
        neighbors = self.get_neighbor_cells(cell[0], cell[1])
        newCells = set()
        for neighbor in neighbors:
            if neighbor not in self.safes:
                newCells.add(neighbor)

        sentence = Sentence(newCells, count)
        if sentence not in self.knowledge:
            self.knowledge.append(sentence)

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        self.mark_cells(self.mines, self.safes)

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        self.infer_sentences()
        self.mark_cells(self.mines, self.safes)
        print("Safes: " + str(self.safes-self.moves_made))
        print("Mines: " + str(self.mines))

    def mark_cells(self, mines, safes):
        newSafes = set()
        newMines = set()
        for sentence in self.knowledge:
            #for move in self.moves_made:
                #if move not in safes:
                #    sentence.mark_safe(move)           

            for safe in sentence.known_safes():
                if safe not in newSafes and safe not in safes:
                    newSafes.add(safe)

            for mine in sentence.known_mines():
                if mine not in newMines and mine not in mines:
                    newMines.add(mine)

        for newSafe in newSafes:
            self.mark_safe(newSafe)

        for newMine in newMines:
            self.mark_mine(newMine)


    def infer_sentences(self):
        #   Any time we have two sentences set1 = count1 and set2 = count2 where set1 is a subset of set2,
        #   then we can construct the new sentence set2 - set1 = count2 - count1
        newSentences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and len(sentence1.cells) > 0 and len(sentence2.cells) > 0 and sentence1.cells.issubset(sentence2.cells):
                    newSet = sentence2.cells-sentence1.cells                    
                    newCount = sentence2.count - sentence1.count
                    if len(newSet) > 0 and newCount > -1:
                        newSentences.append(Sentence(newSet, newCount))

        for newSentence in newSentences:
            if newSentence not in self.knowledge:                
                self.knowledge.append(newSentence)


    def get_neighbor_cells(self, i, j):
        cells = set()

        # Upper left corder
        if i > 0 and j > 0:
            cells.add((i-1, j-1))

        # North
        if i > 0:
            cells.add((i-1, j))

        # Upper right
        if i > 0 and j < self.width-1:
            cells.add((i-1, j+1))

        # East
        if j < self.width-1:
            cells.add((i, j+1))

        # Lower right
        if i < self.height-1 and j < self.width-1:
            cells.add((i+1, j+1))

        # South
        if i < self.height-1:
            cells.add((i+1, j))

        # Lower left
            if i < self.height-1 and j > 0:
                cells.add((i+1, j-1))

        # West
        if j > 0:
            cells.add((i, j-1))

        return cells

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0:
            return None

        for safe in self.safes:
            if safe not in self.moves_made and safe not in self.mines:
                print("Selected safe cell: " + str(safe))
                return safe

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height-1):
            for j in range(self.width-1):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    return cell

        return None
