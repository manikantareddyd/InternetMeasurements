import pandas
import config
import matplotlib.pyplot as plt
import numpy as np

class InternetMeasurements:
    def __init__(self):
        self.dataframe = pandas.read_csv(config.FLOW_RECORD_FILE)
        self.datadescribe = self.dataframe.describe()
        self.dataframe['flow_diff'] = self.dataframe['last'] - self.dataframe['first']

    def average_packet_size(self):
        mean_dpkts = self.datadescribe['dpkts']['mean']
        mean_doctets = self.datadescribe['doctets']['mean']
        return mean_doctets/mean_dpkts

    def plot_ccdf(self, column):
        column_data = np.array(self.dataframe[column].tolist())
        column_data = column_data/column_data.sum()
        column_cdf  = np.cumsum(column_data)

        fig, ax = plt.subplots()
        ax.set_title(column + " CCDF")
        ax.plot(self.dataframe.index,1-column_cdf)
        fig.savefig(column + ' ccdf.png')

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(column + " CCDF" + " - Log Scale")
        ax.plot(self.dataframe.index,1-column_cdf)
        fig.savefig(column + ' ccdf log.png')

    def print_port_summary(self):
        print("Top 10 - Sender Traffic")
        print("Port\tCounts")
        src_port_bytes = {}
        for i in range(65536): src_port_bytes[i]=0
        data = self.dataframe
        for i in data.index:
            src_port_bytes[data['srcport'][i]] = src_port_bytes[data['srcport'][i]] + data['doctets'][i]
        for w in sorted(src_port_bytes, key=src_port_bytes.get, reverse=True)[:10]:
            print(w,'\t', src_port_bytes[w])
    
        print("\n")
        print("Top 10 - Receiver Traffic")
        print("Port\tCounts")
        dst_port_bytes = {}
        for i in range(65536): dst_port_bytes[i]=0
        data = self.dataframe
        for i in data.index:
            dst_port_bytes[data['dstport'][i]] = dst_port_bytes[data['dstport'][i]] + data['doctets'][i]
        for w in sorted(dst_port_bytes, key=dst_port_bytes.get, reverse=True)[:10]:
            print(w,'\t', dst_port_bytes[w])


im = InternetMeasurements()
# im.plot_ccdf('flow_diff')
im.print_port_summary()