import pandas
import config
import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable

class InternetMeasurements:
    def __init__(self):
        self.dataframe = pandas.read_csv(config.FLOW_RECORD_FILE)
        
    def average_packet_size(self):
        self.datadescribe = self.dataframe.describe()
        self.dataframe['flow_diff'] = self.dataframe['last'] - self.dataframe['first']
        mean_dpkts = self.datadescribe['dpkts']['mean']
        mean_doctets = self.datadescribe['doctets']['mean']
        return mean_doctets/mean_dpkts

    def plot_ccdf(self, column):
        column_data = np.copy(self.dataframe[column].values)
        values, base = np.histogram(column_data, bins=column_data.shape[0]//2)
        cumulative = np.cumsum(values)/len(column_data)

        fig, ax = plt.subplots()
        ax.set_title(column + " CCDF")
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig(column + ' ccdf.png')

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(column + " CCDF" + " - Log Scale")
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig(column + ' ccdf log.png')

    def print_port_summary(self):
        print("Top 10 - Sender Traffic")
        x = PrettyTable(["Port", "%Bytes", "Times"])
        src_port_bytes = {}
        src_port_count = {}
        dst_port_bytes = {}
        dst_port_count = {}
        for i in range(65536): 
            src_port_bytes[i]=0
            src_port_count[i]=0
        for i in range(65536): 
            dst_port_bytes[i]=0
            dst_port_count[i]=0
        data = self.dataframe
        for i in data.index:
            src_port_bytes[data['srcport'][i]] = src_port_bytes[data['srcport'][i]] + data['doctets'][i]
            src_port_count[data['srcport'][i]] = src_port_count[data['srcport'][i]] + 1
            dst_port_bytes[data['dstport'][i]] = dst_port_bytes[data['dstport'][i]] + data['doctets'][i]
            dst_port_count[data['dstport'][i]] = dst_port_count[data['dstport'][i]] + 1
        for w in sorted(src_port_bytes, key=src_port_bytes.get, reverse=True)[:10]:
            x.add_row([w, 100*src_port_bytes[w]/data['srcport'].sum(), src_port_count[w]])
        print(x)
        print("\n")
        print("Top 10 - Receiver Traffic")
        y = PrettyTable(["Port", "%Bytes", "Times"])
        for w in sorted(dst_port_bytes, key=dst_port_bytes.get, reverse=True)[:10]:
            y.add_row([w, 100*dst_port_bytes[w]/data['dstport'].sum(), dst_port_count[w]])
        print(y)
        

    def get_princeton_share(self):
        data = self.dataframe
        src_doctets=0
        src_dpkts=0
        dst_doctets=0
        dst_dpkts=0
        net_doctets=0
        net_dpkts=0
        for i in data.index:
            if data['srcaddr'][i].split('.')[:2] == ['128','112']:
                src_doctets = src_doctets + data['doctets'][i]
                src_dpkts   = src_dpkts   + data['dpkts'][i]
            
            if data['dstaddr'][i].split('.')[:2] == ['128','112']:
                dst_doctets = dst_doctets + data['doctets'][i]
                dst_dpkts   = dst_dpkts   + data['dpkts'][i]
            
            net_doctets = net_doctets + data['doctets'][i]
            net_dpkts   = net_dpkts   + data['dpkts'][i]
        print('net doctets\t',net_doctets)
        print('net dpkts\t',net_dpkts)
        print('*'*16)
        print('src docktets\t',src_doctets)
        print('src doctets fraction\t',src_doctets/net_doctets)
        print('src dpkts\t',src_dpkts)
        print('src dpkts fraction\t',src_dpkts/net_dpkts)
        print('*'*16)
        print('dst docktets\t',dst_doctets)
        print('dst doctets fraction\t',dst_doctets/net_doctets)
        print('dst dpkts\t',dst_dpkts)
        print('dst dpkts fraction\t',dst_dpkts/net_dpkts)
        

im = InternetMeasurements()
im.average_packet_size()
im.plot_ccdf('flow_diff')
im.plot_ccdf('doctets')
im.plot_ccdf('dpkts')
im.print_port_summary()
# im.get_princeton_share()