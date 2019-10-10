#!/usr/bin/env python3

# Copyright (C) 2019 Andrea Di Pasquale <spikey.it@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR OR HIS RELATIVES BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF MIND, USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import datetime as dtm
import optparse as opt
import signal as sn
import sys

import matplotlib.pyplot as plt
import pandas as pd

def handle_sn(signum, frame):
    """
    Handle signals.
    """
    print("\nInterrupted by user.")
    sys.exit(0)

##
# This application reads and detects outlier data points from an input CSV file.
# Take note that during the analysis of each point, the outlier algorithm does
# not use historical data, as it is not allowed to see into the future.
#
# Therefore the steps are:
#
# - read the input CSV file;
# - inform user of the outlier found via message console;
# - write out a output chart figure of cleaned data with outlier plots removed;
# - write out a output CSV file of cleaned data with outlier points removed.
#
def main():
    """
    Main handler.
    """
    CSV_INPUT = "input.csv"
    DELIMITER = ","
    CONSTANT = 1.5
    WINDOW = 5
    CHART_OUTPUT = "output.png"
    CSV_OUTPUT = "output.csv"

    # Set signals handler
    sn.signal(sn.SIGINT, handle_sn)
    sn.signal(sn.SIGTERM, handle_sn)

    # Set options parser
    parser = opt.OptionParser(
        usage="usage: %prog [options]", version="%prog 1.0"
    )
    parser.add_option(
        "-i", dest="csv_input", default=CSV_INPUT, type="string",
        help="input CSV file (default: " + CSV_INPUT + ")"
    )
    parser.add_option(
        "-d", dest="delimiter", default=DELIMITER, type="string",
        help="delimiter CSV file (default: '" + DELIMITER + "')"
    )
    parser.add_option(
        "-k", dest="constant", default=CONSTANT, type="float",
        help="Tukey's fences constant (default: " + str(CONSTANT) + ")"
    )
    parser.add_option(
        "-w", dest="window", default=WINDOW, type="int",
        help="input data window (default: " + str(WINDOW) + ")"
    )
    parser.add_option(
        "-c", dest="chart_output", default=CHART_OUTPUT, type="string",
        help="input CSV file (default: " + CHART_OUTPUT + ")"
    )
    parser.add_option(
        "-o", dest="csv_output", default=CSV_OUTPUT, type="string",
        help="input CSV file (default: " + CSV_OUTPUT + ")"
    )

    # Parse options
    options, reminder = parser.parse_args()

    # Print some verbose informations
    print("Input CSV filename: " + options.csv_input)
    print("Delimiter of CSV: '" + options.delimiter + "'")
    print("Multiplier of IRQ: " + str(options.constant))
    print("Window data frame: " + str(options.window))
    print("Chart filename: " + options.chart_output)
    print("Output CSV filename: " + options.csv_output + "\n")
    print("[Press ENTER]")
    input()

    # Read data from input csv file
    dt = read_dt(options.csv_input, options.delimiter)

    # Clean dt from outliers
    dt_clean = compute_dt(dt, options.constant, options.window)

    # Plot dt and cleaned dt
    plot_dts(dt, dt_clean, options.chart_output)

    # Write cleaned dt to output csv file
    write_dt(dt_clean, options.csv_output, options.delimiter)

def read_dt(csv, delimiter):
    """
    Read data from input csv file.
    """
    # Return data from input csv file using a specific delimiter
    return pd.read_csv(csv, delimiter=delimiter)

def compute_dt(dt, k, win):
    """
    Compute data.
    """
    # Create empty both dt_clean and dt_temp
    dt_clean = pd.DataFrame()
    dt_temp = pd.DataFrame()

    # Initialize number of outliers
    num_outliers = 0

    # For each dt's element
    for i in range(0, len(dt)):
        # Append next dt's element inside of dt_temp
        dt_temp = dt_temp.append(dt[i:i+1])

        # Compute dt_temp without outliers with Tukey's fences criterion
        dt_temp, new_outliers = compute_tf_df(dt_temp, k)

        # Sum number of outliers to total outliers
        num_outliers += new_outliers

        # If dt's window is full or dt has reached last window
        if i % win == 0 or i == len(dt) - 1:
            # Append computed dt_temp inside of dt_clean
            dt_clean = dt_clean.append(dt_temp)

            # Clean dt_temp
            dt_temp = pd.DataFrame()

    # Show some statistics
    print(str(len(dt)) + " data read ")
    print(str(len(dt) - num_outliers) + " cleaned data read")
    print(str(num_outliers) + " outliers found by detector ")

    # Return computed dt_clean without outliers
    return dt_clean

def compute_tf_df(df, k):
    """
    Compute subdata with Tukey's fences criterion.
    """
    # Compute both first and third quartiles
    Q1 = df.quantile(0.25)['Price']
    Q3 = df.quantile(0.75)['Price']

    # Compute IQR (InterQuartile Range)
    IQR = Q3 - Q1

    # Convert k costant from any types to string
    k = str(k)

    ##
    # Compute df without outliers.
    #                
    # df's element is not a quartile if:
    # (Q1 - k * IQR) <= df_element['Price'] <= (Q3 + k * IQR)
    #
    qi = '(@Q1 - ' + k + ' * @IQR) <= Price <= (@Q3 + ' + k + ' * @IQR)'
    df_clean = df.query(qi)

    ##
    # Compute df with only outliers.
    #
    # df's element is a quartile if:
    # df_element['Price'] < (Q1 - k * IQR) OR
    # df_element['Price'] > (Q3 + k * IQR)
    #
    qi = 'Price < (@Q1 - ' + k + ' * @IQR) or Price > (@Q3 + ' + k + ' * @IQR)'
    df_outliers = df.query(qi)

    # Are there any outliers?
    if len(df_outliers):
        print("Outliers FOUND:\n" + str(df_outliers) + "\n")

    # Return df without outliers and number of outliers
    return df_clean, len(df_outliers)

def plot_dts(dt, dt_clean, chart):
    """
    Plot data.
    """
    # Add dt as first subplot
    plot_dt(dt, "Data ticks", 211)

    # More space between subplots
    plt.subplots_adjust(hspace = 0.5)

    # Add dt_clean as second subplot
    plot_dt(dt_clean, "Data ticks without outliers", 212)

    # Save both dt and dt_clean subplots inside output chart file
    plt.savefig(chart)

def plot_dt(dt, title, pos):
    """
    Plot subdata.
    """
    # Compute x and y coordinates
    x = [dtm.datetime.strptime(d, "%d/%m/%Y") for d in dt['Date'].tolist()]
    y = dt['Price'].tolist()

    # Plot dt as next position subplot
    plt.subplot(pos)
    plt.plot(x, y)

    # Add some other details
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(title)
    plt.grid(True)

def write_dt(dt, csv, delimiter):
    """
    Write data (without outliers) to output csv file.
    """
    # Write data to output csv file using a specific delimiter
    dt.to_csv(csv, sep=delimiter, index=False)

if __name__ == "__main__":
    main()
