import os
import config
import csv
from prettytable import PrettyTable
import operator
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
            with open(config.UPDATES_DIR + filename, "r") as infile:
                for line in infile:
                    fields = line.split("|")
                    if "." in fields[5]:
                        for session in self.sessions:
                            if session in filename:
                                bgp_updates[session] += 1
        x = PrettyTable(["Session","Average Updates/Minute"])
        for session in self.sessions:
            x.add_row([session, bgp_updates[session]/(15*bgp_files_in_updates[session])])
        print(x)

    def compute_prefix_fractions(self):
        prefix_list = {}
        total_updates = {}
        
        for session in self.sessions:
            prefix_list[session] = {}
            total_updates[session] = 0
        
        for filename in os.listdir(config.RIB_DIR):
            with open(config.RIB_DIR + filename, "r") as infile:
                for line in infile:
                    prefix = line.split("|")[5].strip()
                    if "." in prefix:
                        for session in self.sessions:
                            if session in filename:
                                    prefix_list[session][prefix] = 0
        
        for filename in os.listdir(config.UPDATES_DIR):
            with open(config.UPDATES_DIR + filename,"r") as infile:
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
            x = PrettyTable(["IP Prefix","Fraction of Updates"])
            for prefix in prefix_list[session]:
                prefix_list[session][prefix] = 100*prefix_list[session][prefix]/total_updates[session]
            for row in sorted(prefix_list[session].items(), key=operator.itemgetter(1), reverse=True)[:3]:
                x.add_row(row)
            print(x)
        self.prefix_list = prefix_list
            
    def compute_no_update_fraction(self):
        self.compute_prefix_fractions()
        x = PrettyTable(["Session","0 update fraction"])
        for session in self.sessions:
            zero_count = 0
            for tup in self.prefix_list.items():
                if tup[1] == 0:
                    zero_count += 1
            x.add_row([session,zero_count])
        print(x)
a = BGPMeasurements()
a.compute_no_update_fraction()
# a.compute_updates()
