import os
import sys
from datetime import datetime


# defining the main function for S&P 500 project
def main():
    start_time = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        end_time = datetime.now().strftime("%Y%m%d%H%M%S")
        print("Total Execution Time : ", (int(end_time)-int(start_time)), " secs")
    except:
        print("Error while retrieving parameters and executing the codebase")     # command to print if any exceptions occur in the codebase


if __name__ == "__main__":     # start of the module
    main()     # calling the main function