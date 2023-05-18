from collections import defaultdict
from nltk.tokenize import word_tokenize
from typing import Generator
import os
import re


class Tokenizer:
    def __init__(self, textFilePath: str) -> None:
        self.textFilePath = textFilePath
        self.tokenList = self.tokenize()
        self.tokenDict = self.computeWordFrequencies()

    def tokenize(self) -> list:
        # Obtains the directory name of the file path.
        directory = os.path.dirname(self.textFilePath)
        # Obtains the file name of the file path, which every file has regardless if it is in the same directory as the project or not.
        fileName = os.path.basename(self.textFilePath)
        # Checks if the directory exists.
        directoryExists = os.path.exists(directory)
        # Checks if the file name exists.
        fileExists = os.path.exists(fileName)
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
            print(
                f"File ({fileName}) is not a valid text file type or is not in utf-8, Python's default encoding standard.")

    def computeWordFrequencies(self) -> dict[str, int]:
        """computeWordFrequencies converts a list of tokens into a dictionary by looping and counting instances of the token. The key is the token and the value is the frequency of 
        how many times it appears in the list. The dictionary is then sorted with lambda so that the most frequent token appear on top and in alphabetical order.

        Args:
            tokenList (list): A list of tokens

        Returns:
            dict[str, int]: A dictionary with key = token and value = frequency count
        """
        tokenDict = defaultdict(int)  # Creates a default dict whose values will be integers (frequency count of token).
        # Iterates through the tokenList generated from the tokenize function, which consists of words.
        for token in self.tokenList:
            # Add token as key and 1 as a value if it doesn't exist in tokenDict. If it does, it adds one
            tokenDict[token] += 1
        return {token: freq for (token, freq) in sorted(
            tokenDict.items(), key=lambda x: (-x[1], x[0]))}  # Dictionary comprehension that sorts tokenDict based of frequency and then alphabetical ordering by creating a new dictionary.

    def processFileLines(self) -> "Generator[str]":
        # Opens the textFilePath as read using the encoding standard of utf-8.
        with open(self.textFilePath, 'r', encoding="utf-8") as file:
            for text in file:
                if not text.isspace():
                    tokens = word_tokenize(text)
                    for token in tokens:
                        yield token.lower()

    def printFreq(self) -> None:
        """Loops through the dictionary and prints out the token and frequency of it.
        Args:
            tokenDict (dict): a dictionary of tokens where key=token and value=frequency
        """
        for (token, freq) in self.tokenDict.items():  # Iterates through the token (key) and frequency count (value) stored in the tokenDict dictionary.
            print(f"{token} -> {freq}")


textFilePath = "example.txt"
tokenizer = Tokenizer(textFilePath)
tokenizer.printFreq()
