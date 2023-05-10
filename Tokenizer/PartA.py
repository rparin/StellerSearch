from collections import defaultdict
from typing import Generator
import os
import re
import sys
"""
Assignment Notes:
- Your code cannot break because of...
    - Characters in non-English languages
    - Non-existing files
    - If a JPG, PNG, etc. is ran, the code shall not break
    - File sizes (that are too big)
    - Empty Argument 
    - Too many arguments
- If the file path is not a valid path, print a line indicating the the file doesn't exist. Looping until a valid file path is inputted may cause an infinite loop.
- If any non-alphanumeric character are in the file, split the string but the character (i.e, don't -->"don t" and niña --> "ni a")
- You should get file names from command line arguments. Yes, you can import sys. (Use sys.argv)
"""


# Time Complexity: O(N*M), where N is the number of lines in the file and M is the average number of words/letters per line.
def tokenize(TextFilePath: str) -> list:
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
        TextFilePath)  # Obtains the directory name of the file path.
    # Obtains the file name of the file path, which every file has regardless if it is in the same directory as PathA.py or not.
    fileName = os.path.basename(TextFilePath)
    # Checks if the directory exists.
    directoryExists = os.path.exists(directory)
    fileExists = os.path.exists(fileName)  # Checks if the file name exists.
    try:
        # Simultaneously runs processFileLines and does list comprehension of the result.
        return [text for text in processFileLines(TextFilePath)]
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
def computeWordFrequencies(tokenList: list) -> dict[str, int]:
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
    for token in tokenList:
        # Add token as key and 1 as a value if it doesn't exist in tokenDict. If it does, it adds one
        tokenDict[token] += 1
    return {token: freq for (token, freq) in sorted(
        tokenDict.items(), key=lambda x: (-x[1], x[0]))}  # Dictionary comprehension that sorts tokenDict based of frequency and then alphabetical ordering by creating a new dictionary.

# Time complexity: O(n), where n is the number of items (key and values) in tokenDict.


def printFreq(tokenDict: dict) -> None:
    """Loops through the dictionary and prints out the token and frequency of it.

    Args:
        tokenDict (dict): a dictionary of tokens where key=token and value=frequency
    """
    for (token, freq) in tokenDict.items():  # Iterates through the token (key) and frequency count (value) stored in the tokenDict dictionary.
        print(f"{token} -> {freq}")


# Time Complexity: O(N*M), where N is the number of lines in the file and M is the average number of words/letters per line. processFileLines contributes to the time complexity of the tokenize function because it is a helper function for it.
def processFileLines(TextFilePath: str) -> "Generator[str]":
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
    with open(TextFilePath, 'r', encoding="utf-8") as file:  # Opens the textFilePath as read using the encoding standard of utf-8.
        for text in file:  # Iterates through the lines in the file
            if not text.isspace():  # Checks if the line is not an empty space.
                # The text is lowercased and is searched through using regex to find where the alphanumeric characters are. Text is redefined to the list that re.find(all) makes for each line.
                text = re.findall("[a-z\d]+", text.lower())
                for word in text:  # For the word in each line,
                    # yield/return the word one at a time back to the tokenize function, where it is processed into a list.
                    yield word


# Time Complexity: O(1); a constant number of operations -- checking whether the inputted argument is valid -- always occurs regardless of the size.
def validateArgv(sysArgvList: list) -> str:
    """validateArgv is the first helper function that runs in PartA. It does simple validation of the argument written in the console by checking that
       (1) A file path was provided or (2) only one argument was provided. If only one argument was provided, it will return sys.argv[1] (indexed at 1).
       This is where the string file path is located.

    Args:
        sysArgvList (list): The sys.argv list, which consists of [python, fileName, argument(s)].

    Returns:
        str: The file path.
    """
    if len(sysArgvList) == 1:  # Checks if the length of the arguments typed into the command line is equal to 1.
        print("File path was not provided.")
        return
    # Checks if the length of the arguments typed into the command line is more than two.
    elif len(sysArgvList) > 2:
        multFilesList = sysArgvList[1:]
        print(
            f"Only one argument is accepted. {len(multFilesList)} ({multFilesList}) were provided.")
        return
    # Only two arguments were provided: PathA.py and the filePath. They look like [PathA.py, filePath]. We only want the filePath of the list so we index at 1.
    return sysArgvList[1]


if __name__ == "__main__":
    # Runs the arguments inserted in the command line into the validateArgv.
    sysArgv = validateArgv(sys.argv)
    # Checks if the system argv does not return None (which would occur if an error was found).
    if sysArgv is not None:
        # Executes the system argument (filePath) to be tokenized. It returns None or a list of tokens.
        tokenList = tokenize(sysArgv)
        # Checks if an error doesn't occur when the filePath is being tokenized (None is returned).
        if tokenList is not None:
            # Executes the computerWordFrequencies function, which coverts the list into a dictionary.
            tokenDict = computeWordFrequencies(tokenList)
            # Prints the token (key) and value(frequency) of each token.
            printFreq(tokenDict)
