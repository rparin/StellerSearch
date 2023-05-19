import psutil

def main():
    print(psutil.virtual_memory())
    # print(psutil.virtual_memory()[2])

if __name__ == "__main__":
    main()