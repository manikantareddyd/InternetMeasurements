import pandas
import config
import matplotlib.pyplot as plt
import numpy as np

class InternetMeasurements:
    def __init__(self):
        self.dataframe = pandas.read_csv(config.FLOW_RECORD_FILE)
        self.datadescribe = self.dataframe.describe()

    def average_packet_size(self):
        mean_dpkts = self.datadescribe['dpkts']['mean']
        mean_doctets = self.datadescribe['doctets']['mean']
        return mean_doctets/mean_dpkts

    def plot_ccdf(self):
        self.dataframe['flow_diff'] = self.dataframe['last'] - self.dataframe['first']
        X = np.array([i for i in range(len(self.dataframe['flow_diff']))])
        flow_diff = np.array([self.dataframe['flow_diff'][i] for i in range(len(self.dataframe['flow_diff']))])
        doctets = np.array([self.dataframe['doctets'][i] for i in range(len(self.dataframe['flow_diff']))])
        dpkts = np.array([self.dataframe['dpkts'][i] for i in range(len(self.dataframe['flow_diff']))])

        flow_diff = flow_diff/flow_diff.sum()
        doctets = doctets/doctets.sum()
        dpkts = dpkts/dpkts.sum()

        C_flow_diff = np.cumsum(flow_diff)
        C_doctets = np.cumsum(doctets)
        C_dpkts = np.cumsum(dpkts)

        fig, ax = plt.subplots()
        ax.set_title("Flow Diff CCDF")
        ax.plot(X,1-C_flow_diff)
        fig.savefig('flow_diff_ccdf.png')


        fig, ax = plt.subplots()
        ax.set_title("Dpkts CCDF")
        ax.plot(X,1-C_dpkts)
        fig.savefig('dpkts_ccdf.png')


        fig, ax = plt.subplots()
        ax.set_title("Dockets CCDF")
        ax.plot(X,1-C_doctets)
        fig.savefig('docktets_ccdf.png')



        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title("Flow Diff CCDF - log")
        ax.plot(X,1-C_flow_diff)
        fig.savefig('flow_diff_ccdf_log.png')

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title("Dpkts CCDF - log")
        ax.plot(X,1-C_dpkts)
        fig.savefig('dpkts_ccdf_log.png')

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title("Dockets CCDF - log")
        ax.plot(X,1-C_doctets)
        fig.savefig('docktets_ccdf_log.png')


im = InternetMeasurements()
im.plot_ccdf()