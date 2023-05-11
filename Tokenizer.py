from collections import defaultdict
from typing import Generator
import os
import re

class Tokenizer:
    def __init__(self, textFilePath:str) -> None:
        self.textFilePath = textFilePath
        self.tokenList = self.tokenize()
        self.tokenDict = self.computeWordFrequencies()

    def tokenize(self) -> list:
        """The tokenize function takes in a text file path which is passed into the processFileLines function. 
        - processFileLines is based of Professor Thornton's Notes from ICS33 (https://www.ics.uci.edu/~thornton/ics33/Notes/Generators/).

        The processFileLines tries to open the text file.
        - If it fails, it immediately exists because of FileNotFoundError, such as the directory or file not existing, or a UniCodeDecodeError, when the
        inputted text file is not a text file or is not in utf-8, the standard encoding for text files.
        - If it passes, it continues processing in the processFileLines helper function. The file is iterated using a for loop that acts as readline(). This returns every
        line in the text file. The lines are the checked if there is a space (whitespace). If there is not, then the text is passed through regex's findall method, which
        iterates over a string to find a subset of characters that are alpha-numerical and returns a list. The list of strings is then iterated to yield individual letters/words.
        As a result, the processes loops repeatedly until there is no words left in the file.

        Back in the tokenize function, the generator is looped through using list comprehension. This converts the words in the generator to a list of tokens, which is what we
        are looking for.

        Args:
            TextFilePath (str): Command line input

        Returns:
            list: A list of tokens
        """
        directory = os.path.dirname(
            self.textFilePath)  # Obtains the directory name of the file path.
        # Obtains the file name of the file path, which every file has regardless if it is in the same directory as PathA.py or not.
        fileName = os.path.basename(self.textFilePath)
        # Checks if the directory exists.
        directoryExists = os.path.exists(directory)
        fileExists = os.path.exists(fileName)  # Checks if the file name exists.
        try:
            # Simultaneously runs processFileLines and does list comprehension of the result.
            return [text for text in self.processFileLines()]
        except FileNotFoundError:
            # Checks if the directory exists or the directory is in the same location as PathA.py, but a file was not found.
            if (directoryExists or directory == "") and not fileExists:
                print(f"File ({fileName}) does not exist.")
            # Checks if the directory does not exist (which means it isn't in the same location as PartA.py, and a file was not found.
            elif not directoryExists:
                print(f"Path directory ({directory}) does not exist.")
        except UnicodeDecodeError:
            print(f"File ({fileName}) is not a valid text file type or is not in utf-8, Python's default encoding standard.")


    # Time complexity: O(n log n), where n is the length of tokenList.
    def computeWordFrequencies(self) -> dict[str, int]:
        """computeWordFrequencies converts a list of tokens into a dictionary by looping and counting instances of the token. The key is the token and the value is the frequency of 
        how many times it appears in the list. The dictionary is then sorted with lambda so that the most frequent token appear on top and in alphabetical order.

        Args:
            tokenList (list): A list of tokens

        Returns:
            dict[str, int]: A dictionary with key = token and value = frequency count
        """
        tokenDict = defaultdict(
            int)  # Creates a default dict whose values will be integers (frequency count of token).
        # Iterates through the tokenList generated from the tokenize function, which consists of words.
        for token in self.tokenList:
            # Add token as key and 1 as a value if it doesn't exist in tokenDict. If it does, it adds one
            tokenDict[token] += 1
        return {token: freq for (token, freq) in sorted(
            tokenDict.items(), key=lambda x: (-x[1], x[0]))}  # Dictionary comprehension that sorts tokenDict based of frequency and then alphabetical ordering by creating a new dictionary.

    # Time complexity: O(n), where n is the number of items (key and values) in tokenDict.


    # Time Complexity: O(N*M), where N is the number of lines in the file and M is the average number of words/letters per line. processFileLines contributes to the time complexity of the tokenize function because it is a helper function for it.
    def processFileLines(self) -> "Generator[str]":
        """processFileLines is based of Professor Thornton's Notes from ICS33 (https://www.ics.uci.edu/~thornton/ics33/Notes/Generators/)

        The processFileLines tries to open the text file.
        - If it fails, it immediately exists because of FileNotFoundError, such as the directory or file not existing, or a UniCodeDecodeError, when the
        inputted text file contains non-ASCII characters or non-text data.
        - If it passes, it continues processing in the processFileLines helper function. The file is iterated using a for loop that acts as readline(). This returns every
        line in the text file. The lines are the checked if there is a space (whitespace). If there is not, then the text is passed through regex's findall method, which
        iterates over a string to find a subset of characters that are alpha-numerical and returns a list. The list of strings is then iterated to yield individual letters/words.
        As a result, the processes loops repeatedly until there is no words left in the file.

        Args:
            TextFilePath (str): The file path from the console argument.

        Yields:
            Generator[str]: A generator of single strings iterated from the file.
        """
        with open(self.textFilePath, 'r', encoding="utf-8") as file:  # Opens the textFilePath as read using the encoding standard of utf-8.
            for text in file:  # Iterates through the lines in the file
                if not text.isspace():  # Checks if the line is not an empty space.
                    # The text is lowercased and is searched through using regex to find where the alphanumeric characters are. Text is redefined to the list that re.find(all) makes for each line.
                    text = re.findall("[a-z\d]+", text.lower())
                    for word in text:  # For the word in each line,
                        # yield/return the word one at a time back to the tokenize function, where it is processed into a list.
                        yield word

    def printFreq(self) -> None:
        """Loops through the dictionary and prints out the token and frequency of it.
        Args:
            tokenDict (dict): a dictionary of tokens where key=token and value=frequency
        """
        for (token, freq) in self.tokenDict.items():  # Iterates through the token (key) and frequency count (value) stored in the tokenDict dictionary.
            print(f"{token} -> {freq}")