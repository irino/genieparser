''' show_monitor.py

IOSXE parsers for the following show commands:
    * show monitor capture file {path} packet-number {number} detailed

'''


# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Any, Optional


# ======================================================
# Schema for 'show monitor capture buffer detailed '
# ======================================================
class ShowMonitorCaptureBufferDetailedSchema(MetaParser):
    schema = {
        'framenumber': {
            Any(): {
                Optional('source_ipv4'): str,
                Optional('destination_ipv4'): str,
                Optional('source_eth'): str,
                Optional('destination_eth'): str,
                Optional('interface_id'): str,
                Optional('interface_name'): str,
                Optional('encapsulation_type'): str,
                Optional('arrival_time'): str,
                Optional('time_shift_for_this_packet'): str,
                Optional('epoch_time'): str,
                Optional('time_delta_from_previous_captured_frame'): str,
                Optional('time_delta_from_previous_displayed_frame'): str,
                Optional('time_since_reference_or_first_frame'): str,
                Optional('frame_number'): int,
                Optional('frame_length'): str,
                Optional('capture_length'): str,
                Optional('frame_is_marked'): str,
                Optional('frame_is_ignored'): str,
                Optional('protocols_in_frame'): str,
                Optional('type'): str,
                Optional('sgt'): str,
                Optional('destination'): str,
                Optional('source'): str,
                Optional('address'): str,
                Optional('options'): str,
                Optional('version'): str,
                Optional('total_length'): int,
                Optional('identification'): str,
                Optional('flags'): str,
                Optional('fragment_offset'): int,
                Optional('time_to_live'): int,
                Optional('protocol'): str,
                Optional('header_checksum'): str,
                Optional('header_checksum_status'): str,
                Optional('length'): int,
                Optional('time_since_previous_frame'): str,
                Optional('time_since_first_frame'): str,
                Optional('reserved'): str,
                Optional('stream_index'): int,
                Optional('checksum'): str,
                Optional('source_port'): int,
                Optional('group_policy_id'): str,
                Optional('destination_port'): int,
                Optional('checksum_status'): str,
                Optional('tcp_segment_len'): str,
                Optional('sequence_number'): str,
                Optional('next_sequence_number'): str,
                Optional('acknowledgment_number'): str,
                Optional('window_size_value'): str,
                Optional('calculated_window_size'): str,
                Optional('window_size_scaling_factor'): str,
                Optional('urgent_pointer'): str,
                Optional('bytes_in_flight'): str,
                Optional('bytes_sent_since_last_psh_flag'): str,
                Optional('severity_level'): str,
                Optional('group'): str,
                Optional('the_rto_for_this_segment_was'): str,
                Optional('rto_based_on_delta_from_frame'): str,
                Optional('time_since_first_frame_in_this_tcp_stream'): str,
                Optional('time_since_previous_frame_in_this_tcp_stream'): str,
                Optional('tcp_source_port'): int,
                Optional('tcp_destination_port'): int,
                Optional('tcp_seq_num'): int,
                Optional('tcp_len'): int,
                Optional('udp_source_port'): int,
                Optional('udp_destination_port'): int,
                Optional('next_header'): str,
                Optional('hop_limit'): str,
                Optional('payload_length'): str,
                Optional('source_ipv6'): str,
                Optional('destination_ipv6'): str,
                Optional('vxlan_id'): int,
                Optional('dscp_value'): int,
                Optional('packet_identifier'): str,
                Optional('authenticator'): str,
                Optional('vendor_id'): str,
                Optional('code'): str,
                Optional('destination_address'): str,
                Optional('source_address'): str,
                Optional('capabilities'): str,
                Optional('port_id_subtype'): str,
                Optional('interface_number'): int,
                Optional('seconds'): int,
                Optional('enabled_capabilities'): str,
                Optional('interface_subtype'): str,
                Optional('trailer'): str,
                Optional('address_string_length'): int,
                Optional('management_address'): str,
                Optional('address_subtype'): str,
                Optional('port_id'): str,
                Optional('system_name'): str,
                Optional('port_description'): str,
                Optional('oid_string_length'): int,
                Optional('organization_unique_code'): str,
                Optional('chassis_id'): str,
                Optional('chassis_id_subtype'): str,
                Optional('cisco_netflow_ipfix'): {
                    Optional('version'): int,
                    Optional('count'): int,
                    Optional('sys_uptime'): str,
                    Optional('timestamp'): str,
                    Optional('current_secs'): int,
                    Optional('flow_sequence'): int,
                    Optional('source_id'): int,
                    Any(): {
                        Optional('id'): int,
                        Optional('flowset_id'): str,
                        Optional('flowset_length'): int,
                        Optional('template'): {
                            Optional('template_id'): int,
                            Optional('field_count'): int,
                            Optional('fields'): {
                                Any(): {
                                    Optional('type'): str,
                                    Optional('length'): int,
                                }
                            },
                        },
                        Optional('template_frame'): int,
                        Optional('flows'): {
                            Any(): {
                                Optional('src_addr'): str,
                                Optional('dst_addr'): str,
                                Optional('dst_port'): int,
                                Optional('tcp_flags'): str,
                                Optional('octets'): int,
                                Optional('packets'): int,
                                Optional('ipversion'): int,
                                Optional('ip_tos'): str,
                                Optional('protocol'): str,
                            }
                        },
                        Optional('padding'): int,
                    }
                },
                Optional('dhcp'): {
                    Optional('message_type'): str,
                    Optional('hardware_type'): str,
                    Optional('hardware_address_length'): int,
                    Optional('hops'): int,
                    Optional('transaction_id'): str,
                    Optional('seconds_elapsed'): int,
                    Optional('bootp_flags'): str,
                    Optional('client_ip_address'): str,
                    Optional('your_ip_address'): str,
                    Optional('next_server_ip_address'): str,
                    Optional('relay_agent_ip_address'): str,
                    Optional('client_mac_address'): str,
                    Optional('client_hardware_address_padding'): int,
                    Optional('server_host_name'): str,
                    Optional('boot_file_name'): str,
                    Optional('magic_cookie'): str,
                    Optional('option'): {
                        Any(): {
                            Optional('option_name'): str,
                            Optional('option_dhcp'): str,
                            Optional('option_length'): int,
                            Optional('option_dhcp_server_identifier'): str,
                            Optional('option_dhcp_ip_address_lease_time'): str,
                            Optional('option_dhcp_renewal_time_value'): str,
                            Optional('option_dhcp_rebinding_time_value'): str,
                            Optional('option_dhcp_subnet_mask'): str,
                            Optional('option_dhcp_router'): str,
                            Optional('option_router'): str,
                            Optional('option_subnet_mask'): str,
                            Optional('option_ip_address_lease_time'): str,
                            Optional('option_renewal_time_value'): str,
                            Optional('option_rebinding_time_value'): str,
                            Optional('option_end'): str,
                            Optional('option_end_padding'): str,
                            Optional('option_dhcp_code'): int,
                            Optional('option_value'): str,
                            Optional('lease_time_seconds'): int,
                            Optional('lease_time_minutes'): str,
                            Optional('renewal_time_seconds'): int,
                            Optional('renewal_time_minutes'): str,
                            Optional('rebinding_time_seconds'): int,
                            Optional('rebinding_time_minutes'): str,
                            Optional('router'): str,
                        }
                    },
                    Optional('padding'): str,
                }
            }
        }
    }

# ======================================================
# Parser for 'show monitor capture buffer detailed '
# ======================================================
class ShowMonitorCaptureBufferDetailed(ShowMonitorCaptureBufferDetailedSchema):
    """Parser for 'show monitor capture buffer detailed"""
    cli_command = ['show monitor capture file {path} packet-number {number} detailed']

    def cli(self, path, number, output=None):
        if output is None:
            cmd = self.cli_command[0].format(path=path, number=number)
            # Execute the command
            output = self.device.execute(cmd)

        # initial return dictionary
        ret_dict = {}
        section_name = None
        flowset_dict = None
        template_dict = None
        field_dict = None
        flow_dict = None

        # Frame 1: 1496 bytes on wire (11968 bits), 80 bytes captured (640 bits) on interface /tmp/epc_ws/wif_to_ts_pipe, id 0
        p0 = re.compile(r'^Frame (?P<frame_num>\d+): +(?P<bytes_on_wire>\d+)[\s\w]+\((?P<bits_1>[\w\s]+)\)'
                        r'\,\s+(?P<bytes_captured>\d+)[\s\w]+\((?P<bits_2>[\w\s]+)\).*$')

        # Frame Number: 1
        # Capture Length: 80 bytes (640 bits)
        # [Frame is marked: False]
        # Encapsulation type: Ethernet [1]
        p1 = re.compile(r'^(?P<pattern>[a-zA-Z \[]+): +(?P<value>[\w\s\(\)\:\,\.\/\]\[]+)$')

        # Internet Protocol Version 4, Src: 49.1.1.2, Dst: 91.4.1.1
        p2 = re.compile(r'^Internet Protocol Version 4, Src:+\s+(?P<source_ipv4>[\d\.]+)+, Dst:+\s+(?P<destination_ipv4>[\.\d]+)$')

        # Ethernet II, Src: fa:88:8e:78:00:02 (fa:88:8e:78:00:02), Dst: 00:a7:42:86:06:bf (00:a7:42:86:06:bf)
        p3 = re.compile(r'^Ethernet II, Src:+\s+(?P<source_eth>[\:\w\)\( ]+)+, Dst:+\s+(?P<destination_eth>[\:\w\(\) ]+)$')

        # Transmission Control Protocol, Src Port: 0, Dst Port: 0, Seq: 1, Len: 942
        p4 = re.compile(r'^Transmission Control Protocol, Src Port:+\s+(?P<tcp_source_port>[\d]+)+, Dst Port:+\s+(?P<tcp_destination_port>[\d]+)+, Seq:+\s+(?P<tcp_seq_num>[\d]+)+, Len:+\s+(?P<tcp_len>[\d]+)$')

        # User Datagram Protocol, Src Port: 65473, Dst Port: 4789
        p5 = re.compile(r'^User Datagram Protocol, Src Port:+\s+(?P<udp_source_port>[\d]+)+, Dst Port:+\s+(?P<udp_destination_port>[\d]+)$')

        # Internet Protocol Version 6, Src: 2000:10::10, Dst: 2000:14::20
        p6 = re.compile(r'^Internet Protocol Version 6, Src:+\s+(?P<source_ipv6>[\d\:]+)+, Dst:+\s+(?P<destination_ipv6>[\:\d]+)$')

        # VXLAN Network Identifier (VNI): 50000
        p7 = re.compile(r'^VXLAN +Network +Identifier +\(VNI+\): +(?P<vxlan_id>(\d+))$')

        #     1010 00.. = Differentiated Services Codepoint: Class Selector 5 (40)
        p8 = re.compile(r'^[\S\s]+\s+= Differentiated Services Codepoint: [\s\S]+ \((?P<dscp_value>\d+)\)$')

        # Cisco NetFlow/IPFIX
        p9 = re.compile(r'^Cisco NetFlow\/IPFIX$')

        # Version: 9
        p10 = re.compile(r'^Version: (?P<version>\d+)$')

        # Count: 2
        p11 = re.compile(r'^Count: (?P<count>\d+)$')

        # SysUptime: 589785.000000000 seconds
        p12 = re.compile(r'^SysUptime: (?P<sys_uptime>.+)$')

        # Timestamp: Jul  9, 2024 06:14:46.000000000 IST
        p13 = re.compile(r'^Timestamp: (?P<timestamp>.+)$')

        # CurrentSecs: 1720485886
        p14 = re.compile(r'^CurrentSecs: (?P<current_secs>\d+)$')

        # FlowSequence: 24
        p15 = re.compile(r'^FlowSequence: (?P<flow_sequence>\d+)$')

        # SourceId: 16777217
        p16 = re.compile(r'^SourceId: (?P<source_id>\d+)$')

        # FlowSet 1 [id=0] (Data Template): 257
        # FlowSet 2 [id=257] (46 flows)
        p17 = re.compile(r'^FlowSet (?P<flowset_num>\d+) \[id=(?P<id>\d+)\].*$')

        # FlowSet Id: Data Template (V9) (0)
        p18 = re.compile(r'^FlowSet Id: (?P<flowset_id>.+)$')

        # FlowSet Length: 44
        p19 = re.compile(r'^FlowSet Length: (?P<flowset_length>\d+)$')

        # Template (Id = 257, Count = 9)
        p20 = re.compile(r'^Template \(Id \= \d+\, Count \= \d+\)$')

        # Template Id: 257
        p21 = re.compile(r'^Template Id: (?P<template_id>\d+)$')

        # Field Count: 9
        p22 = re.compile(r'^Field Count: (?P<field_count>\d+)$')

        # Field (1/9): IP_SRC_ADDR
        p23 = re.compile(r'^Field \((?P<field_id>\d+)\/\d+\).*$')

        # Type: IP_SRC_ADDR (8)
        p24 = re.compile(r'^Type: (?P<type>.+)$')

        # Length: 4
        p25 = re.compile(r'^Length: (?P<length>\d+)$')

        # [Template Frame: 7291]
        p26 = re.compile(r'^\[Template Frame: (?P<template_frame>\d+)\]$')

        # Flow 5
        p27 = re.compile(r'^Flow (?P<flow_id>\d+)$')

        # SrcAddr: 6.6.6.8
        p28 = re.compile(r'^SrcAddr: (?P<src_addr>[\d.]+)$')

        # DstAddr: 15.15.15.8
        p29 = re.compile(r'^DstAddr: (?P<dst_addr>[\d.]+)$')

        # DstPort: 60
        p30 = re.compile(r'^DstPort: (?P<dst_port>\d+)$')

        # TCP Flags: 0x00
        p31 = re.compile(r'^TCP Flags: (?P<tcp_flags>\w+)$')

        # Octets: 2470
        p32 = re.compile(r'^Octets: (?P<octets>\d+)$')

        # Packets: 5
        p33 = re.compile(r'^Packets: (?P<packets>\d+)$')

        # IPVersion: 4
        p34 = re.compile(r'^IPVersion: (?P<ipversion>\d+)$')

        # IP ToS: 0x00
        p35 = re.compile(r'^IP ToS: (?P<ip_tos>\w+)$')

        # Protocol: TCP (6)
        p36 = re.compile(r'^Protocol: (?P<protocol>.+)$')

        # Padding: 0000
        p37 = re.compile(r'^Padding: (?P<padding>\d+)$')

        # Dynamic Host Configuration Protocol (Offer)
        p38 = re.compile(r'^Dynamic Host Configuration Protocol \((?P<dhcp_message_type>[\w\s]+)\)$')

        # Message type: Boot Reply (2)
        p39 = re.compile(r'^Message type: (?P<message_type>[\w\s]+) \(\d+\)$')

        # Hardware type: Ethernet (0x01)
        p40 = re.compile(r'^Hardware type: (?P<hardware_type>[\w\s]+) \([\w\s]+\)$')

        # Hardware address length: 6
        p41 = re.compile(r'^Hardware address length: (?P<hardware_address_length>\d+)$')

        # Hops: 0
        p42 = re.compile(r'^Hops: (?P<hops>\d+)$')

        # Transaction ID: 0x24415a66
        p43 = re.compile(r'^Transaction ID: (?P<transaction_id>0x[\dA-Fa-f]+)$')

        # Seconds elapsed: 0
        p44 = re.compile(r'^Seconds elapsed: (?P<seconds_elapsed>\d+)$')

        # Bootp flags: 0x0000 (Unicast)
        p45 = re.compile(r'^Bootp flags: (?P<bootp_flags>0x[\dA-Fa-f]+) \((?P<bootp_flags_type>[\w\s]+)\)$')

        # Client IP address: 0.0.0.0
        p46 = re.compile(r'^Client IP address: (?P<client_ip_address>[\d\.]+)$')

        # Your (client) IP address: 192.168.10.105
        p47 = re.compile(r'^Your \(client\) IP address: (?P<your_ip_address>[\d\.]+)$')

        # Next server IP address: 0.0.0.0
        p48 = re.compile(r'^Next server IP address: (?P<next_server_ip_address>[\d\.]+)$')

        # Relay agent IP address: 0.0.0.0
        p49 = re.compile(r'^Relay agent IP address: (?P<relay_agent_ip_address>[\d\.]+)$')

        # Client MAC address: 00:12:01:00:00:01 (00:12:01:00:00:01)
        p50 = re.compile(r'^Client MAC address: (?P<client_mac_address>[\w\:]+) \((?P<client_mac_address_2>[\w\:]+)\)$')

        # Client hardware address padding: 00000000000000000000
        p51 = re.compile(r'^Client hardware address padding: (?P<client_hardware_address_padding>[\d]+)$')

        # Server host name not given
        p52 = re.compile(r'^Server host name (?P<server_host_name>[\w\s]+)$')

        # Boot file name not given
        p53 = re.compile(r'^Boot file name (?P<boot_file_name>[\w\s]+)$')

        # Magic cookie: DHCP
        p54 = re.compile(r'^Magic cookie: (?P<magic_cookie>[\w]+)$')

        # Option: (53) DHCP Message Type (Offer)
        p55 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+) \((?P<option_value>[\w\s]+)\)$')

        # Length: 1
        p56 = re.compile(r'^Length: (?P<option_length>\d+)$')

        # DHCP: Offer (2)
        p57 = re.compile(r'^DHCP: (?P<option_dhcp>[\w\s]+) \((?P<option_dhcp_code>\d+)\)$')

        # Option: (54) DHCP Server Identifier (192.168.10.1)
        p58 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+) \((?P<option_value>[\d\.]+)\)$')

        # Option: (51) IP Address Lease Time
        p59 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+)$')

        # IP Address Lease Time: (3540s) 59 minutes
        p60 = re.compile(r'^IP Address Lease Time: \((?P<lease_time_seconds>\d+s)\) (?P<lease_time_minutes>[\d\s\w]+)$')

        # Option: (58) Renewal Time Value
        p61 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+)$')

        # Renewal Time Value: (1770s) 29 minutes, 30 seconds
        p62 = re.compile(r'^Renewal Time Value: \((?P<renewal_time_seconds>\d+s)\) (?P<renewal_time_minutes>[\d\s\w]+)$')

        # Option: (59) Rebinding Time Value
        p63 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+)$')

        # Rebinding Time Value: (3094s) 51 minutes, 34 seconds
        p64 = re.compile(r'^Rebinding Time Value: \((?P<rebinding_time_seconds>\d+s)\) (?P<rebinding_time_minutes>[\d\s\w]+)$')

        # Option: (1) Subnet Mask (255.255.255.0)
        p65 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+) \((?P<option_value>[\d\.]+)\)$')

        # Option: (3) Router
        p66 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+)$')

        # Router: 192.168.10.1
        p67 = re.compile(r'^Router: (?P<router>[\d\.]+)$')

        # Option: (255) End
        p68 = re.compile(r'^Option: \((?P<option_code>\d+)\) (?P<option_name>[\w\s]+)$')

        # Option End: 255
        p69 = re.compile(r'^Option End: (?P<option_end>\d+)$')

        # Padding: 0000000000000000000000000000000000000000
        p70 = re.compile(r'^Padding: (?P<padding>[\d]+)$')

        for line in output.splitlines():
            line = line.strip()

            # Frame 1: 1496 bytes on wire (11968 bits), 80 bytes captured (640 bits) on interface /tmp/epc_ws/wif_to_ts_pipe, id 0
            m = p0.match(line)
            if m:
                groups = m.groupdict()
                framenumber = int(groups["frame_num"])
                result_dict = ret_dict.setdefault('framenumber', {}).setdefault(framenumber, {})
                continue

            # Frame Number: 1
            # Capture Length: 80 bytes (640 bits)
            # [Frame is marked: False]
            # Encapsulation type: Ethernet [1]
            m = p1.match(line)
            if m and section_name is None:
                group = m.groupdict()
                key = group['pattern'].strip().replace(' ', '_').replace('[', '').lower()
                val = group['value'].replace(']', '').replace('[', '')
                try:
                    val = int(val)
                except ValueError:
                    pass
                result_dict.update({key: val})
                continue

            # Internet Protocol Version 4, Src: 49.1.1.2, Dst: 91.4.1.1
            m = p2.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({
                    "source_ipv4": groups['source_ipv4'],
                    "destination_ipv4": groups['destination_ipv4']
                })
                continue

            # Ethernet II, Src: fa:88:8e:78:00:02 (fa:88:8e:78:00:02), Dst: 00:a7:42:86:06:bf (00:a7:42:86:06:bf)
            m = p3.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({
                    "source_eth": groups['source_eth'],
                    "destination_eth": groups['destination_eth']
                })
                continue

            # Transmission Control Protocol, Src Port: 0, Dst Port: 0, Seq: 1, Len: 942
            m = p4.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({
                    "tcp_source_port": int(groups['tcp_source_port']),
                    "tcp_destination_port": int(groups['tcp_destination_port']),
                    "tcp_seq_num": int(groups['tcp_seq_num']),
                    "tcp_len": int(groups['tcp_len'])
                })
                continue

            # User Datagram Protocol, Src Port: 65473, Dst Port: 4789
            m = p5.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({
                    "udp_source_port": int(groups['udp_source_port']),
                    "udp_destination_port": int(groups['udp_destination_port'])
                })
                continue

            # Internet Protocol Version 6, Src: 2000:10::10, Dst: 2000:14::20
            m = p6.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({
                    "source_ipv6": groups['source_ipv6'],
                    "destination_ipv6": groups['destination_ipv6']
                })
                continue

            # VXLAN Network Identifier (VNI): 50000
            m = p7.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({"vxlan_id": int(groups['vxlan_id'])})
                continue

            # 1010 00.. = Differentiated Services Codepoint: Class Selector 5 (40)
            m = p8.match(line)
            if m:
                section_name = None
                groups = m.groupdict()
                result_dict.update({"dscp_value": int(groups['dscp_value'])})
                continue

            # Cisco NetFlow/IPFIX
            m = p9.match(line)
            if m:
                section_name = "cisco_netflow_ipfix"
                cisco_netflow_ipfix_dict = result_dict.setdefault(section_name, {})
                continue

            # Version: 9
            m = p10.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"version": int(groups['version'])})
                continue

            # Count: 2
            m = p11.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"count": int(groups['count'])})
                continue

            # SysUptime: 589785.000000000 seconds
            m = p12.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"sys_uptime": groups['sys_uptime']})
                continue

            # Timestamp: Jul  4, 2024 23:33:59.000000000 IST
            m = p13.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"timestamp": groups['timestamp']})
                continue

            # CurrentSecs: 1720485886
            m = p14.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"current_secs": int(groups['current_secs'])})
                continue

            # FlowSequence: 24
            m = p15.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"flow_sequence": int(groups['flow_sequence'])})
                continue

            # SourceId: 16777217
            m = p16.match(line)
            if m:
                groups = m.groupdict()
                cisco_netflow_ipfix_dict.update({"source_id": int(groups['source_id'])})
                continue

            # FlowSet 1 [id=0] (Data Template): 257
            # FlowSet 2 [id=257] (46 flows)
            m = p17.match(line)
            if m:
                groups = m.groupdict()
                flowset_dict = cisco_netflow_ipfix_dict.setdefault(groups["flowset_num"], {})
                flowset_dict.update({"id": int(groups["id"])})
                continue

            # FlowSet Id: Data Template (V9) (0)
            m = p18.match(line)
            if m and flowset_dict is not None:
                groups = m.groupdict()
                flowset_dict.update({"flowset_id": groups["flowset_id"]})
                continue

            # FlowSet Length: 44
            m = p19.match(line)
            if m and flowset_dict is not None:
                groups = m.groupdict()
                flowset_dict.update({"flowset_length": int(groups["flowset_length"])})
                continue

            # Template (Id = 257, Count = 9)
            m = p20.match(line)
            if m and flowset_dict is not None:
                template_dict = flowset_dict.setdefault("template", {})
                continue

            # Template Id: 257
            m = p21.match(line)
            if m and template_dict is not None:
                groups = m.groupdict()
                template_dict.update({"template_id": int(groups["template_id"])})
                continue

            # Field Count: 9
            m = p22.match(line)
            if m and template_dict is not None:
                groups = m.groupdict()
                template_dict.update({"field_count": int(groups["field_count"])})
                continue

            # Field (1/9): IP_SRC_ADDR
            m = p23.match(line)
            if m and template_dict is not None:
                groups = m.groupdict()
                field_dict = template_dict.setdefault("fields", {}).setdefault(groups["field_id"], {})
                continue

            # Type: IP_SRC_ADDR (8)
            m = p24.match(line)
            if m and field_dict is not None:
                groups = m.groupdict()
                field_dict.update({"type": groups["type"]})
                continue

            # Length: 4
            m = p25.match(line)
            if m and field_dict is not None:
                groups = m.groupdict()
                field_dict.update({"length": int(groups["length"])})
                continue

            # [Template Frame: 7291]
            m = p26.match(line)
            if m and flowset_dict is not None:
                groups = m.groupdict()
                flowset_dict.update({"template_frame": int(groups["template_frame"])})
                continue

            # Flow 5
            m = p27.match(line)
            if m and flowset_dict is not None:
                groups = m.groupdict()
                flow_dict = flowset_dict.setdefault("flows", {}).setdefault(groups["flow_id"], {})
                continue

            # SrcAddr: 6.6.6.8
            m = p28.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"src_addr": groups["src_addr"]})
                continue

            # DstAddr: 15.15.15.8
            m = p29.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"dst_addr": groups["dst_addr"]})
                continue

            # DstPort: 60
            m = p30.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"dst_port": int(groups["dst_port"])})
                continue

            # TCP Flags: 0x00
            m = p31.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"tcp_flags": groups["tcp_flags"]})
                continue

            # Octets: 2470
            m = p32.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"octets": int(groups["octets"])})
                continue

            # Packets: 5
            m = p33.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"packets": int(groups["packets"])})
                continue

            # IPVersion: 4
            m = p34.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"ipversion": int(groups["ipversion"])})
                continue

            # IP ToS: 0x00
            m = p35.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"ip_tos": groups["ip_tos"]})
                continue

            # Protocol: TCP (6)
            m = p36.match(line)
            if m and flow_dict is not None:
                groups = m.groupdict()
                flow_dict.update({"protocol": groups["protocol"]})
                continue

            # Padding: 0000
            m = p37.match(line)
            if m and flowset_dict is not None:
                groups = m.groupdict()
                flowset_dict.update({"padding": int(groups["padding"])})
                continue

            # Dynamic Host Configuration Protocol (Offer)
            m = p38.match(line)
            if m:
                section_name = "dhcp"
                dhcp_dict = result_dict.setdefault(section_name, {})
                continue

            # Message type: Boot Reply (2)
            m = p39.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({
                    "message_type": groups["message_type"]
                })
                continue

            # Hardware type: Ethernet (0x01)
            m = p40.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({
                    "hardware_type": groups["hardware_type"]
                })
                continue

            # Hardware address length: 6
            m = p41.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"hardware_address_length": int(groups["hardware_address_length"])})
                continue

            # Hops: 0
            m = p42.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"hops": int(groups["hops"])})
                continue

            # Transaction ID: 0x24415a66
            m = p43.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"transaction_id": groups["transaction_id"]})
                continue

            # Seconds elapsed: 0
            m = p44.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"seconds_elapsed": int(groups["seconds_elapsed"])})
                continue

            # Bootp flags: 0x0000 (Unicast)
            m = p45.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({
                    "bootp_flags": groups["bootp_flags"]
                })
                continue

            # Client IP address: 0.0.0.0
            m = p46.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"client_ip_address": groups["client_ip_address"]})
                continue

            # Your (client) IP address: 192.168.10.105
            m = p47.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"your_ip_address": groups["your_ip_address"]})
                continue

            # Next server IP address: 0.0.0.0
            m = p48.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"next_server_ip_address": groups["next_server_ip_address"]})
                continue

            # Relay agent IP address: 0.0.0.0
            m = p49.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"relay_agent_ip_address": groups["relay_agent_ip_address"]})
                continue

            # Client MAC address: 00:12:01:00:00:01 (00:12:01:00:00:01)
            m = p50.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({
                    "client_mac_address": groups["client_mac_address"]
                })
                continue

            # Client hardware address padding: 00000000000000000000
            m = p51.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"client_hardware_address_padding": int(groups["client_hardware_address_padding"])})
                continue

            # Server host name not given
            m = p52.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"server_host_name": groups["server_host_name"]})
                continue

            # Boot file name not given
            m = p53.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"boot_file_name": groups["boot_file_name"]})
                continue

            # Magic cookie: DHCP
            m = p54.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"magic_cookie": groups["magic_cookie"]})
                continue

            # Option: (53) DHCP Message Type (Offer)
            m = p55.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({
                    "option_name": groups["option_name"],
                    "option_value": groups["option_value"]
                })
                continue

            # Length: 1
            m = p56.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({"option_length": int(groups["option_length"])})
                continue

            # DHCP: Offer (2)
            m = p57.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({
                    "option_dhcp": groups["option_dhcp"],
                    "option_dhcp_code": int(groups["option_dhcp_code"])
                })
                continue

            # Option: (54) DHCP Server Identifier (192.168.10.1)
            m = p58.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({
                    "option_name": groups["option_name"],
                    "option_value": groups["option_value"]
                })
                continue

            # Option: (51) IP Address Lease Time
            m = p59.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({"option_name": groups["option_name"]})
                continue

            # IP Address Lease Time: (3540s) 59 minutes
            m = p60.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({
                    "lease_time_seconds": int(groups["lease_time_seconds"].replace('s', '')),
                    "lease_time_minutes": groups["lease_time_minutes"]
                })
                continue

            # Option: (58) Renewal Time Value
            m = p61.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({"option_name": groups["option_name"]})
                continue

            # Renewal Time Value: (1770s) 29 minutes, 30 seconds
            m = p62.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({
                    "renewal_time_seconds": int(groups["renewal_time_seconds"].replace('s', '')),
                    "renewal_time_minutes": groups["renewal_time_minutes"]
                })
                continue

            # Option: (59) Rebinding Time Value
            m = p63.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({"option_name": groups["option_name"]})
                continue

            # Rebinding Time Value: (3094s) 51 minutes, 34 seconds
            m = p64.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({
                    "rebinding_time_seconds": int(groups["rebinding_time_seconds"].replace('s', '')),
                    "rebinding_time_minutes": groups["rebinding_time_minutes"]
                })
                continue

            # Option: (1) Subnet Mask (255.255.255.0)
            m = p65.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({
                    "option_name": groups["option_name"],
                    "option_value": groups["option_value"]
                })
                continue

            # Option: (3) Router
            m = p66.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({"option_name": groups["option_name"]})
                continue

            # Router: 192.168.10.1
            m = p67.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({"router": groups["router"]})
                continue

            # Option: (255) End
            m = p68.match(line)
            if m:
                groups = m.groupdict()
                option_dict = dhcp_dict.setdefault("option", {}).setdefault(groups["option_code"], {})
                option_dict.update({"option_name": groups["option_name"]})
                continue

            # Option End: 255
            m = p69.match(line)
            if m:
                groups = m.groupdict()
                option_dict.update({"option_end": str(groups["option_end"])})
                continue

            # Padding: 0000000000000000000000000000000000000000
            m = p70.match(line)
            if m:
                groups = m.groupdict()
                dhcp_dict.update({"padding": groups["padding"]})
                continue

        return ret_dict