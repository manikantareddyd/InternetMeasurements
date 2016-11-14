from traffic_measurements import TrafficMeasurements
from bgp_measurements import BGPMeasurements

# im = TrafficMeasurements()
# im.average_packet_size()
# im.plot_all()
# im.print_port_summary()
# im.aggregate_ip_prefix_traffic()
# im.get_princeton_share()

bg = BGPMeasurements()
bg.compute_no_update_fraction()
# bg.compute_distibution_unstable_prefixes()