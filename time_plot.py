import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import os, sys
import fnmatch


def client(path):
    index = 0
    result = []
    with open(path, 'r') as f:
        for line in f:
            if 'WARNING' in line and 'Start of request bunch' in line:
                result.append([])
            if 'WARNING' in line and 'Elapsed' in line:
                values = line[line.find('Elapsed')+9:line.find('Elapsed')+23].split(':')
                values2 = values[2].split('.')
                mean = int(values2[0]) + int(values2[1])/1000000
                result[index].append(round(mean * 1000))
            if 'WARNING' in line and 'End of request bunch' in line:
                index += 1
    # print(result)
    return result


def frontend(path):
    result = []
    with open(path, 'r') as f:
        for line in f:
            if 'WARNING - Success GET' in line:
                values = line[line.find('Elapsed') + 9:line.find('Elapsed') + 23].split(':')
                values2 = values[2].split('.')
                mean = int(values2[0]) + int(values2[1]) / 1000000
                result.append(round(mean * 1000))
    # print(result)
    return result


clientdata = []
frontdata = []

for file in os.listdir('./Logs'):
    if fnmatch.fnmatch(file, 'client*'):
        clientdata = client(os.path.join(os.path.abspath('.'), 'Logs', file))
    elif fnmatch.fnmatch(file, 'frontend*'):
        frontdata = frontend(os.path.join(os.path.abspath('.'), 'Logs', file))


# =======================================================================================================
def client_plot():
    properwidth = 12  # Correct if number of requests in client has changed
    index = 0
    #  Fill in zeros if some series' length < properwidth
    for series in clientdata:
        print(series)
        if len(series) < properwidth:
            for t in range(0, properwidth-len(series)):
                clientdata[index].append(0)
        index += 1

    #  Transpose clientdata
    clientdata_tr = [list(row) for row in zip(*clientdata)]
    print("===============")
    for row in clientdata_tr:
        print(row)


    #  задай столбцы
    rawdata = {'req{0}'.format(c) : clientdata_tr[c-1] for c in range(1, len(clientdata_tr)+1)}
    rawdata['req0'] = ['Launch {0}'.format(c) for c in range(0, len(clientdata))]

    df = pd.DataFrame(rawdata, columns=['req{0}'.format(c) for c in range(0, len(clientdata_tr)+1)])


    # Setting the positions and width for the bars
    pos = list(range(len(clientdata)))
    width = 0.025

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(10,5))

    # Create a bar with pre_score data,
    # in position pos,
    counter = 0
    for x in range(1, len(clientdata_tr)+1):
        plt.bar([p + width*(x-1) for p in pos],
                # using df['mid_score'] data,
                df['req{0}'.format(x)],
                # of width
                width,
                # with alpha 0.5
                alpha=0.5,
                # with color
                color='#F78F1E',
                # with label the second value in first_name
                # label=df['columns'][x])
                label=str(x))

    # Set the y axis label
    ax.set_ylabel('Время выполнения запроса (ms)')

    # Set the chart's title
    ax.set_title('Клиент')

    # Set the position of the x ticks
    ax.set_xticks([p + 1.5 * width for p in pos])

    # Set the labels for the x ticks
    ax.set_xticklabels(df['req0'])

    # Setting the x-axis and y-axis limits
    plt.xlim(min(pos)-width, max(pos)+width*4)
    plt.ylim([0, max( [max(l) for l in clientdata_tr] )])

    # Adding the legend and showing the plot
    # plt.legend(['Pre Score', 'Mid Score', 'Post Score'], loc='upper left')
    plt.grid()
    plt.show()


def frontend_plot():
    fig, ax = plt.subplots(figsize=(10, 5))
    N = len(frontdata)
    x = range(N)
    width = 1 / 1.5
    plt.bar(x, frontdata, width, color='#F78F1E')
    ax.set_ylabel('Время выполнения запроса (ms)')
    ax.set_title('Frontend-узел')
    plt.grid()
    # fig = plt.gcf()
    plt.show()


frontend_plot()
client_plot()
