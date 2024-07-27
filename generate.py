import sys
from copy import deepcopy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            newSet = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    newSet.add(word)
            self.domains[var] = newSet

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        xIntersectionIndex = self.crossword.overlaps[x, y][0]
        yIntersectionIndex = self.crossword.overlaps[x, y][1]

        newXDomain = set()

        for xWord in self.domains[x]:
            if any(xWord[xIntersectionIndex] == yWord[yIntersectionIndex] for yWord in self.domains[y]):
                newXDomain.add(xWord)

        revisionMade = not(newXDomain == self.domains[x])

        if revisionMade:
            self.domains[x] = deepcopy(newXDomain)

        return revisionMade

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs = []
            for var in self.domains:
                for neighbour in self.crossword.neighbors(var):
                    arcs.append((var, neighbour))

        
        while len(arcs) != 0:
            nextArc = arcs.pop(0)
            
            if self.revise(nextArc[0], nextArc[1]):
                if len(self.domains[nextArc[0]]) == 0:
                    return False
                
                # Iterates through a list containing all the neighbours of nextArc[0] except nextArc[1]
                for neighbour in [item for item in self.crossword.neighbors(nextArc[0]) if item != nextArc[1]]:
                    arcs.append((neighbour, nextArc[0]))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
            if type(assignment[variable]) != str:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        keys = [key for key in assignment]
        # If duplicate word present...
        for keyIndex in range(len(assignment)):
            for nestedKeyIndex in range(keyIndex+1, len(assignment)):
                if assignment[keys[keyIndex]] == assignment[keys[nestedKeyIndex]]:
                    return False
                    #return "Case 2"

        # If word length incorrect for variable...
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False
                #return "Case 3"
        
        # Contains all arcs in the crossword
        arcs = []
        for var in assignment:
            for neighbour in [item for item in self.crossword.neighbors(var) if item in assignment]:
                arcs.append((var, neighbour))
        
        # If any arc in assignment is inconsistent...
        for arc in arcs:
            x = arc[0]
            y = arc[1]

            xIntersectionIndex = self.crossword.overlaps[x, y][0]
            yIntersectionIndex = self.crossword.overlaps[x, y][1]

            if assignment[x][xIntersectionIndex] != assignment[y][yIntersectionIndex]:
                return False
                #return "Case 4"
        
        # Otherwise assignment is consistent
        return True
        
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domainOnChoices = {}

        for domain in self.domains[var]:
            choicesRuledOut = 0

            for neighbour in [item for item in self.crossword.neighbors(var) if item not in assignment]:
                for neighbourDomain in self.domains[neighbour]:
                    varIntersectionIndex = self.crossword.overlaps[var, neighbour][0]
                    neighbourIntersectionIndex = self.crossword.overlaps[var, neighbour][1]

                    if domain[varIntersectionIndex] != neighbourDomain[neighbourIntersectionIndex]:
                        choicesRuledOut += 1

            domainOnChoices[domain] = choicesRuledOut
        
        return sorted(domainOnChoices, key=lambda k: domainOnChoices[k])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        fewestRemainingDomains = {}

        lowestDomainVal = float('inf')
        for variable in [var for var in self.domains if var not in assignment]:
            if len(self.domains[variable]) < lowestDomainVal:
                lowestDomainVal = len(self.domains[variable])
                fewestRemainingDomains.clear()
                fewestRemainingDomains[variable] = lowestDomainVal
            elif len(self.domains[variable]) == lowestDomainVal:
                fewestRemainingDomains[variable] = lowestDomainVal

        if len(fewestRemainingDomains) == 1:
            return [key for key in fewestRemainingDomains][0]
        
        else:
            largestDegree = {}
            largestDegreeVal = 0
            for variable in fewestRemainingDomains:
                if len(self.crossword.neighbors(variable)) > largestDegreeVal:
                    largestDegreeVal = len(self.crossword.neighbors(variable))
                    largestDegree.clear()
                    largestDegree[variable] = largestDegreeVal
                elif len(self.crossword.neighbors(variable)) == largestDegreeVal:
                    largestDegree[variable] = largestDegreeVal

        return [key for key in largestDegree][0]


        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
