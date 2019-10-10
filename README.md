README
======

This application reads and detects outlier data points from an input CSV file.
Take note that during the analysis of each point, the outlier algorithm does
not use historical data, as it is not allowed to see into the future.

Therefore the steps are:

 - read the input CSV file;
 - inform user of the outlier found via message console;
 - write out a output chart figure of cleaned data with outlier plots removed;
 - write out a output CSV file of cleaned data with outlier points removed.

INSTALL
=======

Install application's dependencies:

    $ sudo apt-get install python3
    $ sudo apt-get install python3-pip
    $ pip3 install pandas
    $ pip3 install matplotlib

EXECUTION
=========

Show detector's usage:

    $ ./detector.py -h
    Usage: detector.py [options]

    Options:
      --version        show program's version number and exit
      -h, --help       show this help message and exit
      -i CSV_INPUT     input CSV file (default: input.csv)
      -d DELIMITER     delimiter CSV file (default: ',')
      -k CONSTANT      Tukey's fences constant (default: 1.5)
      -w WINDOW        input data window (default: 5)
      -c CHART_OUTPUT  input CSV file (default: output.png)
      -o CSV_OUTPUT    input CSV file (default: output.csv)

Run detector with default parameters:

    $ ./detector.py
    Input CSV filename: input.csv
    Delimiter of CSV: ','
    Multiplier of IRQ: 1.5
    Window data frame: 5
    Chart filename: output.png
    Output CSV filename: output.csv

    [Press ENTER]

    Outliers FOUND:
             Date      Price
    4  15/01/1990  101.62153

    Outliers FOUND:
              Date       Price
    15  30/01/1990  110.925788

    ...

    1000 data read
    901 cleaned data read
    99 outliers found by detector

Show detector's cleaned data results:

    $ vim output.csv

Show detector's data and cleaned data charts:

    $ display output.png
