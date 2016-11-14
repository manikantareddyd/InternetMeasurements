import os
import config
import csv
from prettytable import PrettyTable
import operator
import numpy as np
class BGPMeasurements:
    def __init__(self):
        self.sessions=["20140103","20140203","20140303"]
    
    def compute_updates(self):
        bgp_updates = {}
        bgp_files_in_updates = {}
        for session in self.sessions:
            bgp_updates[session] = 0
            bgp_files_in_updates[session] = 0
        for filename in os.listdir(config.UPDATES_DIR):
            for session in self.sessions:
                if session in filename:
                    bgp_files_in_updates[session] += 1
            with open(
                config.UPDATES_DIR + filename,
                "r") as infile:
                for line in infile:
                    fields = line.split("|")
                    if "." in fields[5]:
                        for session in self.sessions:
                            if session in filename:
                                bgp_updates[session] += 1
        x = PrettyTable([
            "Session",
            "Average Updates/Minute"
            ])
        for session in self.sessions:
            minutes = 15*bgp_files_in_updates[session]
            fraction = bgp_updates[session]/(minutes)
            x.add_row([
                session, 
                fraction
                ])
        print(x)

    def compute_prefix_fractions(self):
        prefix_list = {}
        total_updates = {}
        
        for session in self.sessions:
            prefix_list[session] = {}
            total_updates[session] = 0
        
        for filename in os.listdir(config.RIB_DIR):
            with open(
                config.RIB_DIR + filename, 
                "r") as infile:
                for line in infile:
                    prefix = line.split("|")[5].strip()
                    if "." in prefix:
                        for session in self.sessions:
                            if session in filename:
                                    prefix_list[session][prefix] = 0
        
        for filename in os.listdir(config.UPDATES_DIR):
            with open(
                config.UPDATES_DIR + filename,
                "r") as infile:
                for line in infile:
                    prefix = line.split("|")[5].strip()
                    if "." in prefix:
                        for session in self.sessions:
                            if session in filename:
                                total_updates[session] += 1
                                if prefix in prefix_list[session]:
                                    prefix_list[session][prefix] += 1
                                else:
                                    prefix_list[session][prefix] = 1
        
        for session in self.sessions:
            print("\nSession:\t",session)
            x = PrettyTable([
                "IP Prefix",
                "Fraction of Updates"
                ])
            for prefix in prefix_list[session]:
                counts = prefix_list[session][prefix]
                total  = total_updates[session]
                prefix_list[session][prefix] = 100*counts/total
            for row in sorted(
                prefix_list[session].items(), 
                key=operator.itemgetter(1), 
                reverse=True
                )[:3]:
                x.add_row(row)
            print(x)
        self.prefix_list = prefix_list
            
    def compute_no_update_fraction(self):
        self.compute_prefix_fractions()
        x = PrettyTable([
            "Session",
            "0 update Prefixes", 
            "Total Prefixes", 
            "% Fraction"
            ])
        for session in self.sessions:
            zero_count = 0
            for prefix in self.prefix_list[session]:
                if self.prefix_list[session][prefix] != 0:
                    zero_count += 1
            total_prefixes = len(self.prefix_list[session])
            fraction =100 - 100*zero_count/total_prefixes
            x.add_row([
                session,
                zero_count,
                total_prefixes,
                fraction,
                ])
        print(x)
    
    def compute_distibution_unstable_prefixes(self):
        self.compute_prefix_fractions()
        print("\nTop shares of updates")
        for session in self.sessions:
            fraction_list = np.array(
                sorted(
                    self.prefix_list[session].items(), 
                    key=operator.itemgetter(1), 
                    reverse=True)
                    )[:,1].astype(float)
            _0_1 = int(len(fraction_list)*0.1/100)
            _1_0 = int(len(fraction_list)*1/100)
            _10_0 = int(len(fraction_list)*10/100)
            top_0_1 = fraction_list[:_0_1].sum()
            top_1_0 = fraction_list[:_1_0].sum()
            top_10_0 = fraction_list[:_10_0].sum()
            print("\nSession",session)
            x = PrettyTable(["Top","Updates %"])
            x.add_row(["0.1%",top_0_1])
            x.add_row(["1%",top_1_0])
            x.add_row(["10%",top_10_0])
            print(x)
