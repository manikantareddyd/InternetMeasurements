import pandas
import config
import matplotlib.pyplot as plt
import numpy as np
import ipaddress 
from prettytable import PrettyTable

def get_ip_prefix(ip, mask):
    bi = ''.join([bin(int(x)+256)[3:] for x in ip.split('.')])
    n = bi[:mask] + '0'*(len(bi)-mask)
    ip_prefix = str(ipaddress.IPv4Address('%d.%d.%d.%d' % (int(n[:8],2),int(n[8:16],2),int(n[16:24],2),int(n[24:32],2))))
    return ip_prefix

def compute_src_ip_prefix(row):
    return get_ip_prefix(row['srcaddr'],row['src_mask'])

def compute_dst_ip_prefix(row):
    return get_ip_prefix(row['dstaddr'],row['dst_mask'])

class TrafficMeasurements:
    def __init__(self):
        self.dataframe = pandas.read_csv(config.FLOW_RECORD_FILE)
        
    def average_packet_size(self):
        self.datadescribe = self.dataframe.describe()
        self.dataframe['flow_diff'] = self.dataframe['last'] - self.dataframe['first']
        mean_dpkts = self.datadescribe['dpkts']['mean']
        mean_doctets = self.datadescribe['doctets']['mean']
        print("Average packet size: ", mean_doctets/mean_dpkts, "bytes/packet")

    def plot_all(self):
        self.plot_ccdf('flow_diff')
        self.plot_ccdf('dpkts')
        self.plot_ccdf('doctets')
    
    def plot_ccdf(self, column):
        column_data = np.copy(self.dataframe[column].values)
        values, base = np.histogram(column_data,bins='auto')
        cumulative = np.cumsum(values)/len(column_data)
        fig, ax = plt.subplots()
        ax.set_title(column + ' CCDF')
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig('plots/' + column + ' ccdf.png')
        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(column + ' CCDF' + ' - Log Scale')
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig('plots/' + column + ' ccdf log.png')

    def print_port_summary(self):
        data = self.dataframe[['srcport','dstport','doctets']].copy()
        print('Top 10 - Sender Traffic')
        src_port_grouped = data.groupby('srcport').sum()
        sorted_src_port_grouped = src_port_grouped.sort_values(by='doctets',ascending=False)
        sorted_src_port_grouped['doctets'] = 100*sorted_src_port_grouped['doctets']/data['doctets'].sum()
        print(sorted_src_port_grouped[['doctets']][:10])
        print('\n')
        print('Top 10 - Receiver Traffic')
        dst_port_grouped = data.groupby('dstport').sum()
        sorted_dst_port_grouped = dst_port_grouped.sort_values(by='doctets',ascending=False)
        sorted_dst_port_grouped['doctets'] = 100*sorted_dst_port_grouped['doctets']/data['doctets'].sum()
        print(sorted_dst_port_grouped[['doctets']][:10])

    def get_princeton_share(self):
        data = self.dataframe[['srcaddr','src_mask','dstaddr','dst_mask','doctets','dpkts']].copy()
        data['doctets'] = 100*data['doctets']/data['doctets'].sum()
        data['dpkts'] = 100*data['dpkts']/data['dpkts'].sum()
        data['src_ip_prefix'] = data.apply(compute_src_ip_prefix,axis=1)
        data['dst_ip_prefix'] = data.apply(compute_dst_ip_prefix,axis=1)
        data_src = data[['src_ip_prefix','doctets','dpkts']].copy()
        data_dst = data[['dst_ip_prefix','doctets','dpkts']].copy()
        del data
        src_prefix_group = data_src.groupby('src_ip_prefix').sum()
        dst_prefix_group = data_dst.groupby('dst_ip_prefix').sum()
        x = PrettyTable(['ip prefix','doctets','dpkts'])
        x.add_row([
            '128.112.0.0 as src',
            src_prefix_group['doctets']['128.112.0.0'],
            src_prefix_group['dpkts']['128.112.0.0']
            ])
        x.add_row([
            '128.112.0.0 as dst',
            dst_prefix_group['doctets']['128.112.0.0'],
            dst_prefix_group['dpkts']['128.112.0.0']
            ])
        print(x)

    def aggregate_ip_prefix_traffic(self):
        data = self.dataframe[['srcaddr','src_mask','doctets']].copy()
        data['doctets'] = 100*data['doctets']/data['doctets'].sum()
        data['ip_prefix'] = data.apply(compute_src_ip_prefix, axis=1)
        data.drop('src_mask',1)
        data.drop('srcaddr',1)
        ip_prefix_group = data.groupby('ip_prefix').sum()
        ip_prefix_group = ip_prefix_group.sort_values(by='doctets',ascending=False)
        print(ip_prefix_group[['doctets']][:10])