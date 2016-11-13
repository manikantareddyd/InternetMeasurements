import pandas
import config
import matplotlib.pyplot as plt
import numpy as np
import ipaddress

def get_ip_prefix(ip, mask):
    bi = ''.join([bin(int(x)+256)[3:] for x in ip.split('.')])
    n = bi[:mask] + '0'*(len(bi)-mask)
    ip_prefix = str(ipaddress.IPv4Address('%d.%d.%d.%d' % (int(n[:8],2),int(n[8:16],2),int(n[16:24],2),int(n[24:32],2))))
    return ip_prefix

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
        ax.set_title(column + ' CCDF')
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig(column + ' ccdf.png')

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(column + ' CCDF' + ' - Log Scale')
        ax.plot(base[:-1], 1-cumulative)
        fig.savefig(column + ' ccdf log.png')

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
        
    def aggregate_ip_prefix_traffic(self):
        def compute_ip_prefix(row):
            return get_ip_prefix(row['srcaddr'],row['src_mask'])
        data = self.dataframe[['srcaddr','src_mask','doctets']].copy()
        data['doctets'] = 100*data['doctets']/data['doctets'].sum()
        data['ip_prefix'] = data.apply(compute_ip_prefix, axis=1)
        data.drop('src_mask',1)
        data.drop('srcaddr',1)
        ip_prefix_group = data.groupby('ip_prefix').sum()
        ip_prefix_group = ip_prefix_group.sort_values(by='doctets',ascending=False)
        print(ip_prefix_group[['doctets']][:10])

im = InternetMeasurements()
# im.average_packet_size()
# im.plot_ccdf('flow_diff')
# im.plot_ccdf('doctets')
# im.plot_ccdf('dpkts')
# im.print_port_summary()
im.aggregate_ip_prefix_traffic()
# im.get_princeton_share()