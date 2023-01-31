# BASKETBALL STATS

## Description:
    This python project extracts data from https://api.sportsdata.io and creates a report with the data of a
    specific basketball team. In this report, it can also be found a forecast of their next match (either they
    win, tie or lose).

## Run program:
    Prerequisite: Install requirements specified on the "requirements.txt" file inside the "/src" directory and
    have Python 3:10 or similar in your computer.

    First, you need to subscribe to https://api.sportsdata.io and have an API Key. With this key, you shall
    copy it in the config.txt file, in the src directory. To do so, replace the following text: "Enter your key
    here (without quotation marks and spaces)" with your key. Please, make sure you have copied your key
    correctly and right next to the colon (DO NOT WRITE IT IN BETWEEN QUOTATION MARKS, BRACKETS, etc...).
    As an example, it should look something like this: Ocp-Apim-Subscription-Key:73758HHEDJH2833739938978GH.
    
    Now, you have ended configuring the program. Just run main.py in your interpreter or in your shell/bash
    terminal. You may also run the Dockerfile inside this directory.

    Eventually, open the pdf file created on the "/basketball_stats" parent directory, where you will find a
    table with the team details, and a forecast of their next match at the bottom.

    DO NOT ALTER THE STRUCTURE OF THE DIRECTORIES. You may delete all the files inside images or data, although
    they might be useful if there is a ConnectionError, or if you have exceeded your API free requests.

## Extras:
    Some lines of code have been commented out inside main.py's main. The first of them, if the "#" have been
    previously removed, allows the user to enter the team name they want to have a report of in terminal. The
    second of them, opens the pdf report directly, however the Dockerfile will not function (a pdf image will
    be required).
    
## Output example:
![alt text](https://github.com/SeroviICAI/Basketball-API-Stats/blob/master/example_report.png)

## Brief summary:
    In a nutshell: install all the requirements, enter your key on the "/src/config.txt" file, run "/src/main.py"
    and enjoy your report.
