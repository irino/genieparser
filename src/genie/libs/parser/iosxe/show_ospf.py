''' show_ospf.py

IOSXE parsers for the following show commands:

    * show ip ospf
    * show ip ospf interface
    * show ip ospf interface {interface}
    * show ip ospf sham-links
    * show ip ospf virtual-links
    * show ip ospf neighbor detail
    * show ip ospf neighbor
    * show ip ospf neighbor {interface}
    * show ip ospf mpls ldp interface
    * show ip ospf mpls traffic-eng link
    * show ip ospf max-metric
    * show ip ospf traffic
    * show ip ospf interface brief
    * show ip ospf {process_id} segment-routing adjacency-sid
    * show ip ospf fast-reroute ti-lfa
    * show ip ospf segment-routing protected-adjacencies
    * show ip ospf segment-routing global-block
    * show ip ospf {process_id} segment-routing global-block
    * show ip ospf segment-routing
    * show ipv6 ospf neighbor
    * show ipv6 ospf neighbor {interface}
    * show ip ospf rib redistribution
    * show ipv6 ospf interface {interface}
    * show ipv6 ospf neighbor detail
'''

# Python
import re
import xmltodict
from netaddr import IPAddress, IPNetwork, INET_ATON

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Or, Optional
from genie.libs.parser.utils.common import Common

# ===========================================================
# Schema for:
#   * 'show ip ospf {process_id} segment-routing local-block'
# ===========================================================
class ShowIpOspfSegmentRoutingLocalBlockSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf {process_id} segment-routing local-block'
    '''

    schema = {
        'instance': {
            Any(): {
                'router_id': str,
                'areas': {
                    Any(): {
                        'router_id': {
                            Any(): {
                                'sr_capable': str,
                                Optional('srlb_base'): int,
                                Optional('srlb_range'): int,
                            },
                        },
                    },
                },
            },
        },
    }


# ===========================================================
# Schema for:
#   * 'show ip ospf {process_id} segment-routing local-block'
# ===========================================================
class ShowIpOspfSegmentRoutingLocalBlock(ShowIpOspfSegmentRoutingLocalBlockSchema):

    ''' Parser for:
        * 'show ip ospf {process_id} segment-routing local-block'
    '''

    cli_command = ['show ip ospf segment-routing local-block',
                   'show ip ospf {process_id} segment-routing local-block']

    def cli(self, process_id=None, output=None):
        if output is None:
            if process_id:
                cmd = self.cli_command[1].format(process_id=process_id)
            else:
                cmd = self.cli_command[0]

            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        ret_dict = {}

        # OSPF Router with ID (10.4.1.1) (Process ID 65109)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\)'
                         r' +\(Process +ID +(?P<pid>(\S+))\)$')

        # OSPF Segment Routing Local Blocks in Area 8
        p2 = re.compile(r'^OSPF +Segment +Routing +Local +Blocks +in +Area'
                         r' +(?P<area>(\d+))$')

        # Router ID        SR Capable   SRLB Base   SRLB Range
        # --------------------------------------------------------
        # *10.4.1.1          Yes          15000       1000
        # 10.16.2.2          Yes          15000       1000
        # 10.169.197.252    No 
        p3 = re.compile(r'^(?P<value>\*)?(?P<router_id>\S+) +(?P<sr_capable>Yes|No)'
                         r'( +(?P<srlb_base>\d+) +(?P<srlb_range>\d+))?$')

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                inst_dict = ret_dict.setdefault('instance', {}).\
                                     setdefault(group['pid'], {})
                inst_dict['router_id'] = group['router_id']
                continue

            # OSPF Segment Routing Local Blocks in Area 8
            m = p2.match(line)
            if m:
                area_dict = inst_dict.setdefault('areas', {}).\
                    setdefault(str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON)), {})
                continue

            # Router ID        SR Capable   SRLB Base   SRLB Range
            # --------------------------------------------------------
            # *10.4.1.1          Yes          15000       1000
            # 10.16.2.2          Yes          15000       1000
            m = p3.match(line)
            if m:
                group = m.groupdict()
                smgt_dict = area_dict.setdefault('router_id', {}).\
                                      setdefault(group['router_id'], {})
                smgt_dict['sr_capable'] = group['sr_capable']
                if group['srlb_base']:
                    smgt_dict['srlb_base'] = int(group['srlb_base'])
                if group['srlb_range']:
                    smgt_dict['srlb_range'] = int(group['srlb_range'])
                continue

        return ret_dict


# ==================
# Schema for:
#   * 'show ip ospf'
# ==================
class ShowIpOspfSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf'
    '''

    schema = {
        'vrf': 
            {Any(): 
                {'address_family': 
                    {Any(): 
                        {'instance': 
                            {Any(): 
                                {'router_id': str,
                                Optional('enable'): bool,
                                'nsr':
                                    {'enable': bool},
                                'bfd': 
                                    {'enable': bool,
                                    Optional('strict_mode'): bool},
                                Optional('domain_id_type'): str,
                                Optional('domain_id_value'): str,
                                Optional('start_time'): str,
                                Optional('nssa'): bool,
                                Optional('area_transit'): bool,
                                Optional('redistribution'): 
                                    {Optional('max_prefix'): 
                                        {Optional('num_of_prefix'): int,
                                        Optional('prefix_thld'): int,
                                        Optional('warn_only'): bool},
                                    Optional('connected'): 
                                        {'enabled': bool,
                                        Optional('subnets'): str,
                                        Optional('metric'): int},
                                    Optional('static'): 
                                        {'enabled': bool,
                                        Optional('subnets'): str,
                                        Optional('metric'): int},
                                    Optional('bgp'): 
                                        {'bgp_id': int,
                                        Optional('metric'): int,
                                        Optional('subnets'): str,
                                        Optional('nssa_only'): str,
                                        },
                                    Optional('isis'): 
                                        {'isis_pid': str,
                                        Optional('subnets'): str,
                                        Optional('metric'): int}},
                                Optional('database_control'): 
                                    {'max_lsa': int,
                                     Optional('max_lsa_current'): int,
                                     Optional('max_lsa_threshold_value'): int,
                                     Optional('max_lsa_ignore_count'): int,
                                     Optional('max_lsa_current_count'): int,
                                     Optional('max_lsa_ignore_time'): int,
                                     Optional('max_lsa_reset_time'): int,
                                     Optional('max_lsa_limit'): int,
                                     Optional('max_lsa_warning_only'): bool},
                                Optional('stub_router'):
                                    {Optional('always'): 
                                        {'always': bool,
                                        Optional('include_stub'): bool,
                                        Optional('summary_lsa'): bool,
                                        Optional('external_lsa'): bool,
                                        Optional('summary_lsa_metric'): int,
                                        Optional('external_lsa_metric'): int,
                                        Optional('state'): str},
                                    Optional('on_startup'): 
                                        {'on_startup': int,
                                        Optional('include_stub'): bool,
                                        Optional('summary_lsa'): bool,
                                        Optional('summary_lsa_metric'): int,
                                        Optional('external_lsa'): bool,
                                        Optional('external_lsa_metric'): int,
                                        'state': str},
                                    },
                                Optional('spf_control'): 
                                    {Optional('incremental_spf'): bool,
                                    'throttle': 
                                        {'spf': 
                                            {'start': int,
                                            'hold': int,
                                            'maximum': int},
                                        'lsa': 
                                            {Optional('start'): int,
                                            Optional('hold'): int,
                                            Optional('maximum'): int,
                                            Optional('arrival'): int},
                                        },
                                    },
                                Optional('auto_cost'): 
                                    {'enable': bool,
                                    'reference_bandwidth': int,
                                    'bandwidth_unit': str},
                                Optional('adjacency_stagger'): 
                                    {'initial_number': int,
                                    'maximum_number': int,
                                    Optional('no_initial_limit'): bool},
                                Optional('graceful_restart'): 
                                    {Any(): 
                                        {'enable': bool,
                                        'type': str,
                                        Optional('helper_enable'): bool,
                                        Optional('restart_interval'): int}},
                                Optional('event_log'): 
                                    {'enable': bool,
                                    Optional('max_events'): int,
                                    Optional('mode'): str,
                                    },
                                Optional('numbers'): 
                                    {Optional('external_lsa'): int,
                                    Optional('external_lsa_checksum'): str,
                                    Optional('opaque_as_lsa'): int,
                                    Optional('opaque_as_lsa_checksum'): str,
                                    Optional('dc_bitless'): int,
                                    Optional('do_not_age'): int},
                                Optional('total_areas'): int,
                                Optional('total_normal_areas'): int,
                                Optional('total_stub_areas'): int,
                                Optional('total_nssa_areas'): int,
                                Optional('total_areas_transit_capable'): int,
                                Optional('lsa_group_pacing_timer'): int,
                                Optional('interface_flood_pacing_timer'): int,
                                Optional('retransmission_pacing_timer'): int,
                                Optional('external_flood_list_length'): int,
                                Optional('db_exchange_summary_list_optimization'): bool,
                                Optional('elapsed_time'): str,
                                Optional('lls'): bool,
                                Optional('opqaue_lsa'): bool,
                                Optional('flags'): 
                                    {Optional('abr'): bool,
                                    Optional('asbr'): bool},
                                Optional('areas'): 
                                    {Any(): 
                                        {'area_id': str,
                                        'area_type': str,
                                        Optional('summary'): bool,
                                        Optional('default_cost'): int,
                                        Optional('authentication'): bool,
                                        Optional('ranges'): 
                                            {Any(): 
                                                {'prefix': str,
                                                Optional('cost'): int,
                                                'advertise': bool}},
                                        Optional('rrr_enabled'): bool,
                                        Optional('statistics'): 
                                            {Optional('spf_runs_count'): int,
                                            Optional('spf_last_executed'): str,
                                            Optional('interfaces_count'): int,
                                            Optional('loopback_count'): int,
                                            Optional('area_scope_lsa_count'): int,
                                            Optional('area_scope_lsa_cksum_sum'): str,
                                            Optional('area_scope_opaque_lsa_count'): int,
                                            Optional('area_scope_opaque_lsa_cksum_sum'): str,
                                            Optional('dcbitless_lsa_count'): int,
                                            Optional('indication_lsa_count'): int,
                                            Optional('donotage_lsa_count'): int,
                                            Optional('flood_list_length'): int,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# ==================
# Parser for:
#   * 'show ip ospf'
# ==================
class ShowIpOspf(ShowIpOspfSchema):

    ''' Parser for:
        * 'show ip ospf'
    '''

    cli_command = 'show ip ospf'
    exclude = ['area_scope_lsa_cksum_sum' , ]

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        max_lsa = False
        redist_max_prefix = False
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'(?:^VRF +(?P<vrf>(\S+)) +in +)?Routing +Process'
                            r' +\"(?:ospf)? +(?P<instance>([a-zA-Z0-9\s]+))\"'
                            r' +with +ID +(?P<router_id>(\S+))$')

        p1_1 = re.compile(r'^Routing +Process +is +shutdown$')

        p2 = re.compile(r'^Domain +ID +type +(?P<domain_id>(\S+)), +value'
                            r' +(?P<value>(\S+))$')

        p3 = re.compile(r'^Start +time: +(?P<start>([0-9\:\.]+)), +Time'
                            r' +elapsed: +(?P<elapsed>(\S+))$')

        p4 = re.compile(r'^Supports +only +single +TOS(TOS0) routes$')

        p5 = re.compile(r'^Supports +opaque +LSA$')

        p6 = re.compile(r'^Supports +Link-local +Signaling +\(LLS\)$')

        p7 = re.compile(r'^Supports +area +transit +capability$')

        p8 = re.compile(r'^Supports +NSSA +\(compatible +with +RFC +3101\)$')

        p9 = re.compile(r'^Supports +Database +Exchange +Summary +List'
                            r' +Optimization +\(RFC +5243\)$')

        p10 = re.compile(r'^Event-log +(?P<event_log>(enabled|disabled)),'
                            r'(?: +Maximum +number +of +events:'
                            r' +(?P<max_events>(\d+)),'
                            r' +Mode: +(?P<mode>(\S+)))?$')

        p11 = re.compile(r'^It +is +an'
                            r'(?: +(?P<abr>(area border)))?'
                            r'(?: +and)?'
                            r'(?: +(?P<asbr>(autonomous system boundary)))?'
                            r' +router$')

        p12_1 = re.compile(r'^Redistributing +External +Routes +from,$')

        p12_2 = re.compile(r'^(?P<type>(connected|static))(?: +with +metric'
                            r' +mapped +to +(?P<metric>(\d+)))?$')

        p12_2_1 = re.compile(r'^(?P<type>(connected|static|isis))'
                                r', +includes +(?P<redist>(subnets)) +in +redistribution')

        p12_3 = re.compile(r'^(?P<prot>(bgp|isis)) +(?P<pid>(\d+))'
                            r'(?: +with +metric +mapped +to +(?P<metric>(\d+)))?'
                            r'(?:, +includes +(?P<redist>(subnets)) +in +redistribution)?'
                            r'(?:, +(?P<nssa>(nssa areas only)))?$')

        p12_4 = re.compile(r'^Maximum +limit +of +redistributed +prefixes'
                            r' +(?P<num_prefix>(\d+))'
                            r'(?: +\((?P<warn>(warning-only))\))?')

        p12_5 = re.compile(r'^Threshold +for +warning +message'
                            r' +(?P<thld>(\d+))\%$')

        p13 = re.compile(r'^Router +is +not +originating +router-LSAs'
                            r' +with +maximum +metric$')

        p14_1 = re.compile(r'^Originating +router-LSAs +with +maximum'
                            r' +metric$')

        p14_2 = re.compile(r'^Condition:'
                            r' +(?P<condition>(always|on \S+))'
                            r'(?: +for +(?P<seconds>(\d+)) +seconds,)?'
                            r' +State: +(?P<state>(\S+))$')

        p14_3 = re.compile(r'^Advertise +stub +links +with +maximum +metric'
                            r' +in +router\-LSAs$')

        p14_4 = re.compile(r'^Advertise +summary\-LSAs +with +metric'
                            r' +(?P<metric>(\d+))$')

        p14_5 = re.compile(r'^^Advertise +external\-LSAs +with +metric'
                            r' +(?P<metric>(\d+))$')

        p15 = re.compile(r'^Initial +SPF +schedule +delay +(?P<time>(\S+))'
                            r' +msecs$')

        p16 = re.compile(r'^Minimum +hold +time +between +two +consecutive'
                            r' +SPFs +(?P<time>(\S+)) +msecs$')

        p17 = re.compile(r'^Maximum +wait +time +between +two +consecutive'
                            r' +SPFs +(?P<time>(\S+)) +msecs$')

        p18 = re.compile(r'^Initial +LSA +throttle +delay +(?P<time>(\S+))'
                            r' +msecs$')

        p19 = re.compile(r'^Minimum +hold +time +for +LSA +throttle'
                            r' +(?P<time>(\S+)) +msecs$')

        p20 = re.compile(r'^Maximum +wait +time +for +LSA +throttle'
                            r' +(?P<time>(\S+)) +msecs$')

        p21 = re.compile(r'^Minimum +LSA +arrival'
                            r' +(?P<arrival>(\S+)) +msecs$')

        p22 = re.compile(r'^Incremental-SPF +(?P<incr>(disabled|enabled))$')

        p23 = re.compile(r'LSA +group +pacing +timer'
                            r' +(?P<pacing>(\d+)) +secs$')

        p24 = re.compile(r'Interface +flood +pacing +timer'
                            r' +(?P<interface>(\d+)) +msecs$')

        p25 = re.compile(r'Retransmission +pacing +timer'
                            r' +(?P<retransmission>(\d+)) +msecs$')

        p26 = re.compile(r'EXCHANGE/LOADING +adjacency +limit: +initial'
                            r' +(?P<initial>(\S+)), +process +maximum'
                            r' +(?P<maximum>(\d+))$')

        p27 = re.compile(r'^Number +of +external +LSA +(?P<ext>(\d+))\.'
                            r' +Checksum +Sum +(?P<checksum>(\S+))$')

        p28 = re.compile(r'^Number +of +opaque +AS +LSA +(?P<opq>(\d+))\.'
                            r' +Checksum +Sum +(?P<checksum>(\S+))$')

        p29 = re.compile(r'^Number +of +DCbitless +external +and +opaque'
                            r' +AS +LSA +(?P<num>(\d+))$')

        p30 = re.compile(r'^Number +of +DoNotAge +external +and +opaque'
                            r' +AS +LSA +(?P<num>(\d+))$')

        p31 = re.compile(r'^Number +of +areas +in +this +router +is'
                            r' +(?P<total_areas>(\d+))\. +(?P<normal>(\d+))'
                            r' +normal +(?P<stub>(\d+)) +stub +(?P<nssa>(\d+))'
                            r' +nssa$')

        p32 = re.compile(r'Number +of +areas +transit +capable +is'
                            r' +(?P<num>(\d+))$')

        p33 = re.compile(r'^Maximum +number +of +non +self-generated +LSA'
                            r' +allowed +(?P<max_lsa>(\d+))(?: +\((?P<warn>(warning-only))\))?')

        p33_1 = re.compile(r'^Current +number +of +non +self\-generated +LSA +(?P<max_lsa_current>\d+)$')

        p33_2 = re.compile(r'^Threshold +for +warning +message +(?P<max_lsa_threshold_value>\d+)\%$')

        p33_3 = re.compile(r'^Ignore\-time +(?P<max_lsa_ignore_time>\d+) +minutes,'
                            r' +reset\-time +(?P<max_lsa_reset_time>\d+) +minutes$')

        p33_4 = re.compile(r'^Ignore\-count +allowed +(?P<max_lsa_ignore_count>\d+),'
                            r' +current ignore\-count +(?P<max_lsa_current_count>\d+)$')

        p33_5 = re.compile(r'^Maximum +limit +of +redistributed +prefixes +(?P<max_lsa_limit>\d+) +\(warning\-only\)$')

        p34 = re.compile(r'^External +flood +list +length +(?P<num>(\d+))$')

        p35 = re.compile(r'^(?P<gr_type>(IETF|Cisco)) +Non-Stop +Forwarding'
                            r' +(?P<enable>(enabled|disabled))$')

        p36 = re.compile(r'^(?P<gr_type>(IETF|Cisco)) +NSF +helper +support'
                            r' +(?P<gr_helper>(enabled|disabled))$')

        p36_1 = re.compile(r'^restart-interval +limit *: +(?P<num>(\d+)) +sec$')

        p37 = re.compile(r'^Reference +bandwidth +unit +is'
                            r' +(?P<bd>(\d+)) +(?P<unit>(mbps))$')

        p38 = re.compile(r'^Area +(?P<area>(\S+))(?: *\((I|i)nactive\))?$')

        p39_1 = re.compile(r'^It +is +a +(?P<area_type>(\S+)) +area'
                            r'(?:, +(?P<summary>(no +summary +LSA +in +this'
                            r' +area)))?$')

        p39_2 = re.compile(r'^generates +stub +default +route +with +cost'
                            r' +(?P<default_cost>(\d+))$')

        p40_1 = re.compile(r'^Area ranges are$')

        p40_2 = re.compile(r'^(?P<prefix>([0-9\.\/]+)) +(Passive|Active)'
                            r'(?:\((?P<cost>(\d+)) +\- +configured\))?'
                            r' +(?P<advertise>(Advertise|DoNotAdvertise))$')

        p41 = re.compile(r'^Number +of +interfaces +in +this +area +is'
                            r' +(?P<num_intf>(\d+))(?:'
                            r' *\((?P<loopback>(\d+)) +loopback\))?$')

        p42 = re.compile(r'^Area +has +RRR +enabled$')

        p43 = re.compile(r'^SPF +algorithm +executed +(?P<count>(\d+))'
                            r' +times$')

        p44 = re.compile(r'^SPF +algorithm +last +executed'
                            r' +(?P<last_exec>(\S+)) +ago$')

        p45 = re.compile(r'^Area +has +no +authentication$')

        p46 = re.compile(r'^Number +of +LSA +(?P<lsa_count>(\d+))\.'
                            r' +Checksum +Sum +(?P<checksum_sum>(\S+))$')

        p47 = re.compile(r'^Number +of opaque +link +LSA'
                            r' +(?P<opaque_count>(\d+))\. +Checksum +Sum'
                            r' +(?P<checksum_sum>(\S+))$')

        p48 = re.compile(r'^Number +of +DCbitless +LSA +(?P<count>(\d+))$')

        p49 = re.compile(r'^Number +of +indication +LSA +(?P<count>(\d+))$')

        p50 = re.compile(r'^Number +of +DoNotAge +LSA +(?P<count>(\d+))$')

        p51 = re.compile(r'^Flood +list +length +(?P<len>(\d+))$')

        p52 = re.compile(r'^Non-Stop +Routing +(?P<nsr>(enabled))$')

        p53_1 = re.compile(r'^BFD +is +enabled +in +strict +mode$')

        p53_2 = re.compile(r'^BFD +is +enabled$')

        for line in out.splitlines():
            line = line.strip()

            # Routing Process "ospf 1" with ID 10.36.3.3
            # VRF VRF1 in Routing Process "ospf 1" with ID 10.36.3.3
            m = p1.match(line)
            if m:
                instance = str(m.groupdict()['instance'])
                router_id = str(m.groupdict()['router_id'])
                if m.groupdict()['vrf']:
                    vrf = str(m.groupdict()['vrf'])
                else:
                    vrf = 'default'

                # Set structure
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}

                # Set sub_dict
                sub_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                            ['instance'][instance]
                sub_dict['router_id'] = router_id
                sub_dict['enable'] = True
                # Set some default values
                if 'nsr' not in sub_dict:
                    sub_dict['nsr'] = {}
                    sub_dict['nsr']['enable'] = False
                if 'bfd' not in sub_dict:
                    sub_dict['bfd'] = {}
                    sub_dict['bfd']['enable'] = False
                continue

            # Routing Process is shutdown
            m = p1_1.match(line)
            if m:
                sub_dict['enable'] = False
                continue

            # Domain ID type 0x0005, value 0.0.0.2
            m = p2.match(line)
            if m:
                sub_dict['domain_id_type'] = str(m.groupdict()['domain_id'])
                sub_dict['domain_id_value'] = str(m.groupdict()['value'])
                continue

            # Start time: 00:23:49.050, Time elapsed: 1d01h
            m = p3.match(line)
            if m:
                sub_dict['start_time'] = str(m.groupdict()['start'])
                sub_dict['elapsed_time'] = str(m.groupdict()['elapsed'])
                continue

            # Supports only single TOS(TOS0) routes
            m = p4.match(line)
            if m:
                sub_dict['single_tos_route'] = True
                continue

            # Supports opaque LSA
            m = p5.match(line)
            if m:
                sub_dict['opqaue_lsa'] = True
                continue

            # Supports Link-local Signaling (LLS)
            m = p6.match(line)
            if m:
                sub_dict['lls'] = True
                continue

            # Supports area transit capability
            m = p7.match(line)
            if m:
                sub_dict['area_transit'] = True
                continue

            # Supports NSSA (compatible with RFC 3101)
            m = p8.match(line)
            if m:
                sub_dict['nssa'] = True
                continue

            # Supports Database Exchange Summary List Optimization (RFC 5243)
            m = p9.match(line)
            if m:
                sub_dict['db_exchange_summary_list_optimization'] = True
                continue

            # Event-log disabled
            # Event-log enabled, Maximum number of events: 1000, Mode: cyclic
            m = p10.match(line)
            if m:
                if 'event_log' not in sub_dict:
                    sub_dict['event_log'] = {}
                if 'enabled' in m.groupdict()['event_log']:
                    sub_dict['event_log']['enable'] = True
                else:
                    sub_dict['event_log']['enable'] = False
                if m.groupdict()['max_events']:
                    sub_dict['event_log']['max_events'] = \
                        int(m.groupdict()['max_events'])
                if m.groupdict()['mode']:
                    sub_dict['event_log']['mode'] = str(m.groupdict()['mode'])
                    continue

            # It is an area border router
            # It is an autonomous system boundary router
            # It is an area border and autonomous system boundary router
            m = p11.match(line)
            if m:
                if 'flags' not in sub_dict:
                    sub_dict['flags'] = {}
                if m.groupdict()['abr']:
                    sub_dict['flags']['abr'] = True
                if m.groupdict()['asbr']:
                    sub_dict['flags']['asbr'] = True
                continue

            # Redistributing External Routes from,
            m = p12_1.match(line)
            if m:
                if 'redistribution' not in sub_dict:
                    sub_dict['redistribution'] = {}
                    continue

            # connected 
            # connected with metric mapped to 10
            # static
            # static with metric mapped to 10
            m = p12_2.match(line)
            if m:
                the_type = str(m.groupdict()['type'])
                if the_type not in sub_dict['redistribution']:
                    sub_dict['redistribution'][the_type] = {}
                sub_dict['redistribution'][the_type]['enabled'] = True
                if m.groupdict()['metric']:
                    sub_dict['redistribution'][the_type]['metric'] = \
                        int(m.groupdict()['metric'])
                continue

            # connected, includes subnets in redistribution
            # static, includes subnets in redistribution
            # isis, includes subnets in redistribution
            m = p12_2_1.match(line)
            if m:
                the_type = str(m.groupdict()['type'])
                if the_type not in sub_dict['redistribution']:
                    sub_dict['redistribution'][the_type] = {}
                sub_dict['redistribution'][the_type]['enabled'] = True

                sub_dict['redistribution'][the_type]['subnets'] = m.groupdict()['redist']
                continue
            # bgp 100 with metric mapped to 111
            # isis 10 with metric mapped to 3333
            # bgp 100 with metric mapped to 100, includes subnets in redistribution, nssa areas only
            # bgp 100, includes subnets in redistribution
            m = p12_3.match(line)
            if m:
                prot = str(m.groupdict()['prot'])
                if prot not in sub_dict['redistribution']:
                    sub_dict['redistribution'][prot] = {}
                if prot == 'bgp':
                    sub_dict['redistribution'][prot]['bgp_id'] = \
                        int(m.groupdict()['pid'])
                else:
                    sub_dict['redistribution'][prot]['isis_pid'] = \
                        str(m.groupdict()['pid'])
                
                # Set parsed values
                if m.groupdict()['metric']:
                    sub_dict['redistribution'][prot]['metric'] = \
                        int(m.groupdict()['metric'])
                if m.groupdict()['redist']:
                    sub_dict['redistribution'][prot]['subnets'] = \
                        str(m.groupdict()['redist'])
                if m.groupdict()['nssa']:
                    sub_dict['redistribution'][prot]['nssa_only'] = True
                continue

            # Maximum number of redistributed prefixes 4000
            # Maximum number of redistributed prefixes 3000 (warning-only)
            m = p12_4.match(line)
            if m:
                redist_max_prefix = True
                if 'max_prefix' not in sub_dict['redistribution']:
                    sub_dict['redistribution']['max_prefix'] = {}
                sub_dict['redistribution']['max_prefix']['num_of_prefix'] = \
                    int(m.groupdict()['num_prefix'])
                if m.groupdict()['warn']:
                    sub_dict['redistribution']['max_prefix']['warn_only'] = True
                else:
                    sub_dict['redistribution']['max_prefix']['warn_only'] = False
                    continue

            # Threshold for warning message 70%
            m = p12_5.match(line)
            if m and redist_max_prefix:
                redist_max_prefix = False
                if 'max_prefix' not in sub_dict['redistribution']:
                    sub_dict['redistribution']['max_prefix'] = {}
                sub_dict['redistribution']['max_prefix']['prefix_thld'] = \
                    int(m.groupdict()['thld'])
                continue

            # Router is not originating router-LSAs with maximum metric
            m = p13.match(line)
            if m:
                if 'stub_router' not in sub_dict:
                    sub_dict['stub_router'] = {}
                if 'always' not in sub_dict['stub_router']:
                    sub_dict['stub_router']['always'] = {}
                # Set values
                sub_dict['stub_router']['always']['always'] = False
                sub_dict['stub_router']['always']['include_stub'] = False
                sub_dict['stub_router']['always']['summary_lsa'] = False
                sub_dict['stub_router']['always']['external_lsa'] = False
                continue

            # Originating router-LSAs with maximum metric
            m = p14_1.match(line)
            if m:
                if 'stub_router' not in sub_dict:
                    sub_dict['stub_router'] = {}
                    continue

            # Condition: always State: active
            # Condition: always, State: active
            # Condition: on start-up for 5 seconds, State: inactive
            # Condition: on startup for 300 seconds, State: inactive
            p14_2 = re.compile(r'^Condition:'
                               r' +(?P<condition>(always|on \S+))'
                               r'(?: +for +(?P<seconds>(\d+)) +seconds)?,?'
                               r' +State: +(?P<state>(\S+))$')
            m = p14_2.match(line)
            if m:
                condition = str(m.groupdict()['condition']).lower().replace("-", "")
                condition = condition.replace(" ", "_")
                if 'stub_router' not in sub_dict:
                    sub_dict['stub_router'] = {}
                if condition not in sub_dict['stub_router']:
                    sub_dict['stub_router'][condition] = {}
                sub_dict['stub_router'][condition]['state'] = \
                    str(m.groupdict()['state']).lower()
                # Set 'condition' key
                if condition == 'always':
                    sub_dict['stub_router'][condition][condition] = True
                else:
                    sub_dict['stub_router'][condition][condition] = \
                        int(m.groupdict()['seconds'])
                continue

            # Advertise stub links with maximum metric in router-LSAs
            m = p14_3.match(line)
            if m:
                sub_dict['stub_router'][condition]['include_stub'] = True
                continue

            # Advertise summary-LSAs with metric 16711680
            m = p14_4.match(line)
            if m:
                sub_dict['stub_router'][condition]['summary_lsa'] = True
                sub_dict['stub_router'][condition]['summary_lsa_metric'] = \
                    int(m.groupdict()['metric'])
                continue

            # Advertise external-LSAs with metric 16711680
            m = p14_5.match(line)
            if m:
                sub_dict['stub_router'][condition]['external_lsa'] = True
                sub_dict['stub_router'][condition]['external_lsa_metric'] = \
                    int(m.groupdict()['metric'])
                continue

            # Initial SPF schedule delay 50 msecs
            m = p15.match(line)
            if m:
                start = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'spf' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['spf'] = {}
                sub_dict['spf_control']['throttle']['spf']['start'] = start
                continue

            # Minimum hold time between two consecutive SPFs 200 msecs
            m = p16.match(line)
            if m:
                hold = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'spf' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['spf'] = {}
                sub_dict['spf_control']['throttle']['spf']['hold'] = hold
                continue

            # Maximum wait time between two consecutive SPFs 5000 msecs
            m = p17.match(line)
            if m:
                maximum = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'spf' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['spf'] = {}
                sub_dict['spf_control']['throttle']['spf']['maximum'] = maximum
                continue

            # Initial LSA throttle delay 50 msecs
            m = p18.match(line)
            if m:
                start = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'lsa' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['lsa'] = {}
                sub_dict['spf_control']['throttle']['lsa']['start'] = start
                continue

            # Minimum hold time for LSA throttle 200 msecs
            m = p19.match(line)
            if m:
                hold = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'lsa' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['lsa'] = {}
                sub_dict['spf_control']['throttle']['lsa']['hold'] = hold
                continue

            # Maximum wait time for LSA throttle 5000 msecs
            m = p20.match(line)
            if m:
                maximum = int(float(m.groupdict()['time']))
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'throttle' not in sub_dict['spf_control']:
                    sub_dict['spf_control']['throttle'] = {}
                if 'lsa' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['lsa'] = {}
                sub_dict['spf_control']['throttle']['lsa']['maximum'] = maximum
                continue

            # Minimum LSA interval 200 msecs. Minimum LSA arrival 100 msecs
            # Minimum LSA arrival 100 msecs
            m = p21.match(line)
            if m:
                if 'lsa' not in sub_dict['spf_control']['throttle']:
                    sub_dict['spf_control']['throttle']['lsa'] = {}
                sub_dict['spf_control']['throttle']['lsa']['arrival'] = \
                    int(float(m.groupdict()['arrival']))
                continue

            # Incremental-SPF disabled
            m = p22.match(line)
            if m:
                if 'spf_control' not in sub_dict:
                    sub_dict['spf_control'] = {}
                if 'enabled' in m.groupdict()['incr']:
                    sub_dict['spf_control']['incremental_spf'] = True
                else:
                    sub_dict['spf_control']['incremental_spf'] = False
                    continue

            # LSA group pacing timer 240 secs
            m = p23.match(line)
            if m:
                sub_dict['lsa_group_pacing_timer'] = \
                    int(float(m.groupdict()['pacing']))
                continue

            # Interface flood pacing timer 33 msecs
            m = p24.match(line)
            if m:
                sub_dict['interface_flood_pacing_timer'] = \
                    int(float(m.groupdict()['interface']))
                continue

            # Retransmission pacing timer 66 msecs
            m = p25.match(line)
            if m:
                sub_dict['retransmission_pacing_timer'] = \
                    int(float(m.groupdict()['retransmission']))
                continue

            # EXCHANGE/LOADING adjacency limit: initial 300, process maximum 300
            m = p26.match(line)
            if m:
                if 'adjacency_stagger' not in sub_dict:
                    sub_dict['adjacency_stagger'] = {}
                if m.groupdict()['initial'] == 'None':
                    sub_dict['adjacency_stagger']['no_initial_limit'] = True
                else:
                    sub_dict['adjacency_stagger']['initial_number'] = \
                        int(m.groupdict()['initial'])
                sub_dict['adjacency_stagger']['maximum_number'] = \
                    int(m.groupdict()['maximum'])
                continue

            # Number of external LSA 1. Checksum Sum 0x00607f
            m = p27.match(line)
            if m:
                if 'numbers' not in sub_dict:
                    sub_dict['numbers'] = {}
                sub_dict['numbers']['external_lsa'] = int(m.groupdict()['ext'])
                sub_dict['numbers']['external_lsa_checksum'] = \
                    str(m.groupdict()['checksum'])
                continue

            # Number of opaque AS LSA 0. Checksum Sum 00000000
            m = p28.match(line)
            if m:
                if 'numbers' not in sub_dict:
                    sub_dict['numbers'] = {}
                sub_dict['numbers']['opaque_as_lsa'] = int(m.groupdict()['opq'])
                sub_dict['numbers']['opaque_as_lsa_checksum'] = \
                    str(m.groupdict()['checksum'])
                continue

            # Number of DCbitless external and opaque AS LSA 0
            m = p29.match(line)
            if m:
                if 'numbers' not in sub_dict:
                    sub_dict['numbers'] = {}
                sub_dict['numbers']['dc_bitless'] = int(m.groupdict()['num'])
                continue

            # Number of DoNotAge external and opaque AS LSA 0
            m = p30.match(line)
            if m:
                if 'numbers' not in sub_dict:
                    sub_dict['numbers'] = {}
                sub_dict['numbers']['do_not_age'] = int(m.groupdict()['num'])
                continue

            # Number of areas in this router is 1. 1 normal 0 stub 0 nssa
            m = p31.match(line)
            if m:
                sub_dict['total_areas'] = int(m.groupdict()['total_areas'])
                sub_dict['total_normal_areas'] = int(m.groupdict()['normal'])
                sub_dict['total_stub_areas'] = int(m.groupdict()['stub'])
                sub_dict['total_nssa_areas'] = int(m.groupdict()['nssa'])
                continue

            # Number of areas transit capable is 0
            m = p32.match(line)
            if m:
                sub_dict['total_areas_transit_capable'] = int(m.groupdict()['num'])
                continue

            # Maximum number of non self-generated LSA allowed 123
            # Maximum number of non self-generated LSA allowed 123 warning-only
            m = p33.match(line)
            if m:
                max_lsa = True
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa'] = \
                    int(m.groupdict()['max_lsa'])
                if m.groupdict()['warn']:
                    sub_dict['database_control']['max_lsa_warning_only'] = True
                continue

            # Current number of non self-generated LSA 0
            m = p33_1.match(line)
            if m and max_lsa:
                max_lsa = False
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa_current'] = \
                    int(m.groupdict()['max_lsa_current'])
                continue

            # Threshold for warning message 75%
            m = p33_2.match(line)
            if m:
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa_threshold_value'] = \
                    int(m.groupdict()['max_lsa_threshold_value'])
                continue

            # Ignore-time 5 minutes, reset-time 10 minutes
            m = p33_3.match(line)
            if m:
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa_ignore_time'] = \
                    int(m.groupdict()['max_lsa_ignore_time']) * 60
                sub_dict['database_control']['max_lsa_reset_time'] = \
                    int(m.groupdict()['max_lsa_reset_time']) * 60
                continue

            # Ignore-count allowed 5, current ignore-count 0
            m = p33_4.match(line)
            if m:
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa_ignore_count'] = \
                    int(m.groupdict()['max_lsa_ignore_count'])
                sub_dict['database_control']['max_lsa_current_count'] = \
                    int(m.groupdict()['max_lsa_current_count'])
                continue

            # Maximum limit of redistributed prefixes 5000 (warning-only)
            m = p33_5.match(line)
            if m:
                if 'database_control' not in sub_dict:
                    sub_dict['database_control'] = {}
                sub_dict['database_control']['max_lsa_limit'] = int(m.groupdict()['max_lsa_limit'])
                sub_dict['database_control']['max_lsa_warning_only'] = False
                continue

            # External flood list length 0
            m = p34.match(line)
            if m:
                sub_dict['external_flood_list_length'] = int(m.groupdict()['num'])
                continue

            # Non-Stop Forwarding enabled
            # IETF Non-Stop Forwarding enabled
            m = p35.match(line)
            if m:
                gr_type = str(m.groupdict()['gr_type']).lower()
                if 'enabled' in m.groupdict()['enable']:
                    enable = True
                else:
                    enable = False
                if 'graceful_restart' not in sub_dict:
                    sub_dict['graceful_restart'] = {}
                if gr_type not in sub_dict['graceful_restart']:
                    sub_dict['graceful_restart'][gr_type] = {}
                # Set keys
                sub_dict['graceful_restart'][gr_type]['enable'] = True
                sub_dict['graceful_restart'][gr_type]['type'] = gr_type

            # IETF NSF helper support enabled
            # Cisco NSF helper support enabled
            m = p36.match(line)
            if m:
                gr_type = str(m.groupdict()['gr_type']).lower()
                if 'enabled' in m.groupdict()['gr_helper']:
                    gr_helper = True
                else:
                    gr_helper = False
                if 'graceful_restart' not in sub_dict:
                    sub_dict['graceful_restart'] = {}
                if gr_type not in sub_dict['graceful_restart']:
                    sub_dict['graceful_restart'][gr_type] = {}
                # Set keys
                sub_dict['graceful_restart'][gr_type]['type'] = gr_type
                sub_dict['graceful_restart'][gr_type]['helper_enable'] = gr_helper
                if 'enable' not in sub_dict['graceful_restart'][gr_type]:
                    sub_dict['graceful_restart'][gr_type]['enable'] = False
                continue

            # restart-interval limit: 11 sec
            m = p36_1.match(line)
            if m:
                sub_dict['graceful_restart'][gr_type]['restart_interval'] = \
                    int(m.groupdict()['num'])
                continue

            # Reference bandwidth unit is 100 mbps
            # Reference bandwidth unit is 4294967 mbps
            m = p37.match(line)
            if m:
                bd = int(m.groupdict()['bd'])
                if 'auto_cost' not in sub_dict:
                    sub_dict['auto_cost'] = {}
                sub_dict['auto_cost']['reference_bandwidth'] = bd
                sub_dict['auto_cost']['bandwidth_unit'] = str(m.groupdict()['unit'])
                if bd == 100:
                    # This is the default - set to False
                    sub_dict['auto_cost']['enable'] = False
                else:
                    sub_dict['auto_cost']['enable'] = True
                continue

            # Area BACKBONE(0)
            # Area BACKBONE(0.0.0.0) (Inactive)
            # Area 1
            m = p38.match(line)
            if m:
                parsed_area = str(m.groupdict()['area'])
                n = re.match(r'BACKBONE\((?P<area_num>(\S+))\)', parsed_area)
                if n:
                    area = str(IPAddress(str(n.groupdict()['area_num']), flags=INET_ATON))
                else:
                    area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))

                # Create dict
                if 'areas' not in sub_dict:
                    sub_dict['areas'] = {}
                if area not in sub_dict['areas']:
                    sub_dict['areas'][area] = {}
                
                # Set default values
                sub_dict['areas'][area]['area_id'] = area
                sub_dict['areas'][area]['area_type'] = 'normal'
                continue

            # It is a stub area
            # It is a stub area, no summary LSA in this area
            # It is a NSSA area
            m = p39_1.match(line)
            if m:
                area_type = str(m.groupdict()['area_type']).lower()
                sub_dict['areas'][area]['area_type'] = area_type
                if area_type == 'stub':
                    if m.groupdict()['summary']:
                        sub_dict['areas'][area]['summary'] = False
                    else:
                        sub_dict['areas'][area]['summary'] = True
                    continue

            # generates stub default route with cost 111
            # generates stub default route with cost 222
            m = p39_2.match(line)
            if m:
                sub_dict['areas'][area]['default_cost'] = \
                    int(m.groupdict()['default_cost'])
                continue

            # Area ranges are
            m = p40_1.match(line)
            if m:
                if 'ranges' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['ranges'] = {}
                continue

            # 10.4.1.0/24 Passive Advertise
            # 10.4.0.0/16 Passive DoNotAdvertise 
            # 10.4.0.0/16 Active(10 - configured) Advertise
            m = p40_2.match(line)
            if m:
                prefix = str(m.groupdict()['prefix'])
                if 'ranges' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['ranges'] = {}
                if prefix not in sub_dict['areas'][area]['ranges']:
                    sub_dict['areas'][area]['ranges'][prefix] = {}
                sub_dict['areas'][area]['ranges'][prefix]['prefix'] = prefix
                if m.groupdict()['cost']:
                    sub_dict['areas'][area]['ranges'][prefix]['cost'] = \
                        int(m.groupdict()['cost'])
                if 'Advertise' in m.groupdict()['advertise']:
                    sub_dict['areas'][area]['ranges'][prefix]['advertise'] = True
                else:
                    sub_dict['areas'][area]['ranges'][prefix]['advertise'] = False
                continue

            # Number of interfaces in this area is 3
            # Number of interfaces in this area is 3 (1 loopback)
            m = p41.match(line)
            if m:
                if 'areas' not in sub_dict:
                    sub_dict['areas'] = {}
                if area not in sub_dict['areas']:
                    sub_dict['areas'][area] = {}
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['interfaces_count'] =\
                    int(m.groupdict()['num_intf'])
                if m.groupdict()['loopback']:
                    sub_dict['areas'][area]['statistics']['loopback_count'] =\
                        int(m.groupdict()['loopback'])
                continue

            # Area has RRR enabled
            m = p42.match(line)
            if m:
                sub_dict['areas'][area]['rrr_enabled'] = True
                continue

            # SPF algorithm executed 26 times
            m = p43.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['spf_runs_count'] = \
                    int(m.groupdict()['count'])
                continue

            # SPF algorithm last executed 00:19:54.849 ago
            m = p44.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['spf_last_executed'] = \
                    str(m.groupdict()['last_exec'])
                continue

            # Area has no authentication
            m = p45.match(line)
            if m:
                continue

            # Number of LSA 19.  Checksum Sum 0x0a2fb5
            m = p46.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['area_scope_lsa_count'] =\
                    int(m.groupdict()['lsa_count'])
                sub_dict['areas'][area]['statistics']\
                    ['area_scope_lsa_cksum_sum'] = \
                        str(m.groupdict()['checksum_sum'])
                continue

            # Number of opaque link LSA 0.  Checksum Sum 00000000
            m = p47.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']\
                    ['area_scope_opaque_lsa_count'] = \
                        int(m.groupdict()['opaque_count'])
                sub_dict['areas'][area]['statistics']\
                    ['area_scope_opaque_lsa_cksum_sum'] = \
                        str(m.groupdict()['checksum_sum'])
                continue

            # Number of DCbitless LSA 5
            m = p48.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['dcbitless_lsa_count'] = \
                    int(m.groupdict()['count'])
                continue

            # Number of indication LSA 0
            m = p49.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['indication_lsa_count'] =\
                    int(m.groupdict()['count'])
                continue

            # Number of DoNotAge LSA 0
            m = p50.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['donotage_lsa_count'] = \
                    int(m.groupdict()['count'])
                continue

            # Flood list length 0
            m = p51.match(line)
            if m:
                if 'statistics' not in sub_dict['areas'][area]:
                    sub_dict['areas'][area]['statistics'] = {}
                sub_dict['areas'][area]['statistics']['flood_list_length'] = \
                    int(m.groupdict()['len'])
                continue
        
            # Non-Stop Routing enabled
            m = p52.match(line)
            if m:
                sub_dict['nsr']['enable'] = True
                continue

            # BFD is enabled in strict mode
            m = p53_1.match(line)
            if m:
                if 'bfd' not in sub_dict:
                    sub_dict['bfd'] = {}
                sub_dict['bfd']['enable'] = True
                sub_dict['bfd']['strict_mode'] = True
                continue

            # BFD is enabled
            m = p53_2.match(line)
            if m:
                if 'bfd' not in sub_dict:
                    sub_dict['bfd'] = {}
                sub_dict['bfd']['enable'] = True
                continue

        return ret_dict

# ============================
# Schema for:
#   * 'show ip ospf interface brief'
# ============================
class ShowIpOspfInterfaceBriefSchema(MetaParser):
    ''' Schema for:
        * 'show ip ospf interface brief'
    '''
    schema = {
        'instance': {
            Any(): {
                'areas': {
                    Any(): {
                        'interfaces': {
                            Any(): {
                                'ip_address': str,
                                'cost': int,
                                'state': str,
                                'nbrs_full': int,
                                'nbrs_count': int,
                                },
                        },
                    },
                },
            },
        },
    }

class ShowIpOspfInterfaceBrief(ShowIpOspfInterfaceBriefSchema):
    ''' Parser for:
        * 'show ip ospf interface brief'
    '''

    cli_command = 'show ip ospf interface brief'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        
        p1 = re.compile(r'^(?P<interface>\S+) +(?P<instance>\S+) +(?P<area>\d+) +'
            r'(?P<address>\S+) +(?P<cost>\d+) +(?P<state>\S+) +(?P<nbrs_full>\d+)'
            r'\/(?P<nbrs_count>\d+)$$')

        for line in out.splitlines():
            line = line.strip()
            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = Common.convert_intf_name(
                    str(group['interface']))
                instance = str(group['instance'])
                ip_address = str(group['address'])
                area = str(IPAddress(str(group['area']), flags=INET_ATON))
                state = group['state']
                cost = int(group['cost'])
                nbrs_full = int(group['nbrs_full'])
                nbrs_count = int(group['nbrs_count'])

                intf_dict = ret_dict.setdefault('instance', {}).\
                    setdefault(instance, {}).\
                    setdefault('areas', {}).\
                    setdefault(area, {}).\
                    setdefault('interfaces', {}).\
                    setdefault(interface, {})

                intf_dict.update({'ip_address' : ip_address})
                intf_dict.update({'cost' : cost})
                intf_dict.update({'state' : state})
                intf_dict.update({'nbrs_full' : nbrs_full})
                intf_dict.update({'nbrs_count' : nbrs_count})
                continue

        return ret_dict

# ============================
# Schema for:
#   * 'show ip ospf interface'
#   * 'show ip ospf interface {interface}''
# ============================
class ShowIpOspfInterfaceSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf interface'
        * 'show ip ospf interface {interface}'
    '''

    schema = {
        'vrf':
            {Any(): 
                {'address_family': 
                    {Any(): 
                        {'instance': 
                            {Any(): 
                                {'areas': 
                                    {Any(): 
                                        {Optional('interfaces'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int,
                                                    },
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                        Optional('virtual_links'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int,
                                                    },
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                        Optional('sham_links'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int},
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }


# ===========================================
# Parser for:
#   * 'show ospf vrf all-inclusive interface'
# ===========================================
class ShowIpOspfInterface(ShowIpOspfInterfaceSchema):

    ''' Parser for:
        * 'show ip ospf interface'
        * 'show ip ospf interface {interface}'
    '''

    cli_command = ['show ip ospf interface {interface}',
                   'show ip ospf interface']

    exclude = ['hello_timer', 'dead_timer',
        'bdr_ip_addr', 'bdr_router_id', 'last_flood_scan_length',
        'last_flood_scan_time_msec', 
        'max_flood_scan_length', 'max_flood_scan_time_msec', 'state']


    def cli(self, interface=None, output=None):
        if output is None:
            if interface:
                cmd = self.cli_command[0].format(interface=interface)
            else:
                cmd = self.cli_command[1]

            out = self.device.execute(cmd)
        else:
            out = output
        

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        # Mapping dict
        bool_dict = {'up': True, 'down': False, 'unknown': False}

        
        p1 = re.compile(r'^(?P<interface>(\S+)) +is( +administratively)?'
                            r' +(?P<enable>(unknown|up|down)), +line +protocol'
                            r' +is +(?P<line_protocol>(up|down))'
                            r'(?: +\(\S+\))?$')
        # Internet Address 0.0.0.1/30|Interface is unnumbered, Interface ID 55, Area 0
        p2 = re.compile(r'^(Internet +Address|Interface +is) +(?P<address>(\S+)),'
                            r'(?: +Interface +ID +(?P<intf_id>(\d+)),)?'
                            r' +Area +(?P<area>(\S+))(?:, +Attached +via'
                            r' +(?P<attach>(.*)))?$')
 
        p2_1 = re.compile(r'^Attached +via +(?P<attached>([a-zA-Z0-9\s]+))$')
 
        p3 = re.compile(r'^Process +ID +(?P<pid>(\S+)),'
                            r'(?: +VRF +(?P<vrf>(\S+)))?'
                            r' +Router +ID +(?P<router_id>(\S+)),'
                            r' +Network +Type +(?P<interface_type>(\S+)),'
                            r' +Cost: +(?P<cost>(\d+))$')

        p5 = re.compile(r'^Configured as demand circuit$')
 
        p6 = re.compile(r'^Run as demand circuit$')
 
        p7 = re.compile(r'^DoNotAge +LSA +not +allowed +\(Number +of'
                            r' +DCbitless +LSA +is +(?P<num>(\d+))\)\.$')
 
        p8 = re.compile(r'^Enabled +by +interface +config, +including'
                            r' +secondary +ip +addresses$')
 
        p9 = re.compile(r'^Transmit +Delay is +(?P<delay>(\d+)) +sec,'
                            r' +State +(?P<state>(\S+))'
                            r'(?:, +Priority +(?P<priority>(\d+)))?'
                            r'(?:, +BFD +(?P<bfd>(enabled|disabled)))?$')
 
        p10 = re.compile(r'^Designated +(R|r)outer +\(ID\)'
                            r' +(?P<dr_router_id>(\S+)), +(I|i)nterface'
                            r' +(A|a)ddress +(?P<dr_ip_addr>(\S+))$')
 
        p11 = re.compile(r'^Backup +(D|d)esignated +(R|r)outer +\(ID\)'
                            r' +(?P<bdr_router_id>(\S+)), +(I|i)nterface'
                            r' +(A|a)ddress +(?P<bdr_ip_addr>(\S+))$')
 
        p12 = re.compile(r'^Timer +intervals +configured,'
                            r' +Hello +(?P<hello>(\d+)),'
                            r' +Dead +(?P<dead>(\d+)),'
                            r' +Wait +(?P<wait>(\d+)),'
                            r' +Retransmit +(?P<retransmit>(\d+))$')
 
        p12_1 = re.compile(r'^oob-resync +timeout +(?P<oob>(\d+))$')
 
        p12_2 = re.compile(r'^Hello +due +in +(?P<hello_timer>(\S+))$')
 
        p13 = re.compile(r'^Supports +Link-local +Signaling +\(LLS\)$')
 
        p14 = re.compile(r'^(?P<gr_type>(Cisco|IETF)) +NSF +helper +support'
                            r' +(?P<helper>(enabled|disabled))$')
 
        p15 = re.compile(r'^Index +(?P<index>(\S+)),'
                            r' +flood +queue +length +(?P<length>(\d+))$')
 
        p16 = re.compile(r'^Next +(?P<next>(\S+))$')
 
        p17 = re.compile(r'^Last +flood +scan +length +is +(?P<num>(\d+)),'
                            r' +maximum +is +(?P<max>(\d+))$')
 
        p18 = re.compile(r'^Last +flood +scan +time +is +(?P<time1>(\d+))'
                            r' +msec, +maximum +is +(?P<time2>(\d+)) +msec$')
 
        p19 = re.compile(r'^Neighbor +Count +is +(?P<nbr_count>(\d+)),'
                            r' +Adjacent +neighbor +count +is'
                            r' +(?P<adj_nbr_count>(\d+))$')
 
        p20_1 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\((B|b)ackup +(D|d)esignated +(R|r)outer\)$')
 
        p20_2 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\((D|d)esignated +(R|r)outer\)$')
 
        p20_3 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\(Hello suppressed\)$')
 
        p21 = re.compile(r'^Suppress +hello +for +(?P<sup>(\d+))'
                            r' +neighbor\(s\)$')
 
        p22 = re.compile(r'^Loopback +interface +is +treated +as +a +stub'
                            r' +Host$')
 
        p23 = re.compile(r'^Can +be +protected +by per-+prefix +Loop-Free'
                            r' +FastReroute$')
 
        p24 = re.compile(r'^Can +be +used +for +per-prefix +Loop-Free'
                            r' +FastReroute +repair +paths$')
 
        p25 = re.compile(r'^Not +Protected +by +per-prefix +TI-LFA$')
 
        p26 = re.compile(r'^Prefix-suppression +is +(?P<ps>(enabled|disabled))$')
 
        p27 = re.compile(r'^Strict +TTL +checking'
                            r' +(?P<strict_ttl>(enabled|disabled))'
                            r'(?:, +up +to +(?P<hops>(\d+)) +hops +allowed)?$')
 
        p28_1 = re.compile(r'^Simple +password +authentication +enabled$')
 
        p28_2 = re.compile(r'^Cryptographic +authentication +enabled$')
 
        p28_3 = re.compile(r'^Youngest +key +id +is +(?P<id>(\d+))$')
 
        p28_4 = re.compile(r'^Rollover +in +progress, +(?P<num>(\d+))'
                            r' +neighbor(s) +using +the +old +key(s):$')
 
        p28_5 = re.compile(r'^key +id +1 +algorithm +MD5$')

        # Segment Routing enabled for MPLS forwarding
        p29 = re.compile(r'^Segment +Routing +enabled +for +MPLS +forwarding$')

        # TEAPP:
        p30 = re.compile(r'^TEAPP:$')

        # Topology Id:0x0
        p30_1 = re.compile(r'^Topology +Id: *(?P<topology_id>[\w]+)$')

        # TEAPP:SRTE
        p30_2 = re.compile(r'^TEAPP: *(?P<teapp>[\w]+)$')

        # Affinity: length 32, bits 0x00000010
        p30_3 = re.compile(r'^Affinity: *length +(?P<length>\d+), +bits +(?P<bits>\w+)$')

        # Extended affinity: length 32, bits 0x00000010
        p30_4 = re.compile(r'^Extended +affinity: *length +(?P<length>\d+), +bits +(?P<bits>\w+)$')

        # SR Policy Manager:
        p31 = re.compile(r'^SR +Policy +Manager:$')

        # TE Opaque LSA: Source of link information OSPF
        p31_1 = re.compile(r'^TE +Opaque +LSA: +(?P<te_opaque_lsa>[\S\s]+)$')

        for line in out.splitlines():
            line = line.strip()

            # Loopback0 is up, line protocol is up 
            # GigabitEthernet2 is up, line protocol is up
            # Port-channel2.100 is administratively down, line protocol is down
            # OSPF_SL1 is up, line protocol is up 
            # OSPF_VL3 is up, line protocol is up 
            # TenGigabitEthernet3/0/1 is up, line protocol is up (connected)
            # TenGigabitEthernet1/8 is down, line protocol is down (notconnect)
            # TenGigabitEthernet2/6.3052 is administratively down, line protocol is down (disabled)
            # TenGigabitEthernet1/15 is down, line protocol is down (err-disabled)
            m = p1.match(line)
            if m:
                interface = str(m.groupdict()['interface'])
                enable = str(m.groupdict()['enable'])
                line_protocol = str(m.groupdict()['line_protocol'])

                # Determine if 'interface' or 'sham_link' or 'virtual_link'
                if re.search('SL', interface):
                    x = re.match(r'(?P<ignore>\S+)_SL(?P<num>(\d+))', interface)
                    if x:
                        intf_type = 'sham_links'
                        name = 'SL' + str(x.groupdict()['num'])
                elif re.search('VL', interface):
                    x = re.match(r'(?P<ignore>\S+)_VL(?P<num>(\d+))', interface)
                    if x:
                        intf_type = 'virtual_links'
                        name = 'VL' + str(x.groupdict()['num'])
                else:
                    intf_type = 'interfaces'
                    name = interface
                continue

            # Internet Address 10.4.1.1/32, Interface ID 11, Area 0
            # Internet Address 0.0.0.0/0, Area 0, Attached via Not Attached
            # Internet Address 10.229.4.4/24, Area 1, Attached via Interface Enable
            m = p2.match(line)
            if m:
                ip_address = str(m.groupdict()['address'])
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                if m.groupdict()['intf_id']:
                    intf_id = int(m.groupdict()['intf_id'])
                if m.groupdict()['attach']:
                    attached = str(m.groupdict()['attach']).lower()
                continue

            # Attached via Interface Enable
            m = p2_1.match(line)
            if m:
                attached = str(m.groupdict()['attached']).lower()
                continue

            # Process ID 1, Router ID 10.64.4.4, Network Type VIRTUAL_LINK, Cost: 1
            # Process ID 2, Router ID 10.229.11.11, Network Type SHAM_LINK, Cost: 111
            # Process ID 1, Router ID 10.4.1.1, Network Type BROADCAST, Cost: 1
            m = p3.match(line)
            if m:
                instance = str(m.groupdict()['pid'])
                router_id = str(m.groupdict()['router_id'])
                interface_type = str(m.groupdict()['interface_type']).lower()
                interface_type = interface_type.replace("_", "-")

                # Get interface values
                intf_name = interface
                if intf_type == 'virtual_links':
                    # Init
                    vl_addr = None
                    vl_transit_area_id = None

                    # Execute command to get virtual-link address
                    cmd = 'show ip ospf virtual-links | i {interface}'.format(interface=interface)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()
                        # Virtual Link OSPF_VL0 to router 10.100.5.5 is down
                        p = re.search(r'Virtual +Link +(?P<intf>(\S+)) +to +router'
                                     r' +(?P<address>(\S+)) +is +(up|down)'
                                     r'(?:.*)?', line)
                        if p:
                            if interface == str(p.groupdict()['intf']):
                                vl_addr = str(p.groupdict()['address'])
                                break

                    # Execute command to get virtual-link transit_area_id
                    if vl_addr is not None:
                        cmd = 'show running-config | i virtual-link | i {addr}'.format(addr=vl_addr)
                        out = self.device.execute(cmd)

                        for line in out.splitlines():
                            line = line.rstrip()
                            #  area 1 virtual-link 10.100.5.5
                            q = re.search(r'area +(?P<q_area>(\d+)) +virtual-link'
                                          r' +(?P<addr>(\S+))(?: +(.*))?', line)
                            if q:
                                q_addr = str(q.groupdict()['addr'])

                                # Check parameters match
                                if q_addr == vl_addr:
                                    vl_transit_area_id = str(IPAddress(str(q.groupdict()['q_area']), flags=INET_ATON))
                                    break

                    if vl_transit_area_id is not None:
                        intf_name = '{} {}'.format(vl_transit_area_id, router_id)
                        area = vl_transit_area_id
                elif intf_type == 'sham_links':
                    # Init
                    sl_local_id = None
                    sl_remote_id = None

                    # Execute command to get sham-link remote_id
                    cmd = 'show ip ospf sham-links | i {interface}'.format(interface=interface)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()
                        # Sham Link OSPF_SL1 to address 10.151.22.22 is up
                        p = re.search(r'Sham +Link +(?P<intf>(\S+)) +to +address'
                                     r' +(?P<remote>(\S+)) +is +(up|down)', line)
                        if p:
                            if interface == str(p.groupdict()['intf']):
                                sl_remote_id = str(p.groupdict()['remote'])
                                break

                    # Execute command to get sham-link local_id
                    if sl_remote_id is not None:
                        cmd = 'show running-config | i sham-link | i {remote}'.format(remote=sl_remote_id)
                        out = self.device.execute(cmd)

                        for line in out.splitlines():
                            line = line.rstrip()
                            # area 1 sham-link 10.229.11.11 10.151.22.22 cost 111 ttl-security hops 3
                            q = re.search(r'area +(?P<q_area>(\d+)) +sham-link'
                                          r' +(?P<local_id>(\S+))'
                                          r' +(?P<remote_id>(\S+)) +(.*)', line)
                            if q:
                                q_area = str(IPAddress(str(q.groupdict()['q_area']), flags=INET_ATON))
                                q_remote_id = str(q.groupdict()['remote_id'])

                                # Check parameters match
                                if q_area == area and q_remote_id == sl_remote_id:
                                    sl_local_id = str(q.groupdict()['local_id'])
                                    break

                    # Set intf_name based on parsed values
                    if sl_local_id is not None:
                        intf_name = '{} {}'.format(sl_local_id, sl_remote_id)

                # Get VRF information based on OSPF instance
                cmd = 'show running-config | section router ospf {}'.format(instance)
                out = self.device.execute(cmd)

                for line in out.splitlines():
                    line = line.rstrip()

                    # Skip the show command line so as to not match
                    if re.search('show', line):
                        continue

                    # router ospf 1
                    # router ospf 2 vrf VRF1
                    p = re.search(r'router +ospf +(?P<instance>(\S+))'
                                  r'(?: +vrf +(?P<vrf>(\S+)))?', line)
                    if p:
                        p_instance = str(p.groupdict()['instance'])
                        if p_instance == instance:
                            if p.groupdict()['vrf']:
                                vrf = str(p.groupdict()['vrf'])
                                break
                            else:
                                vrf = 'default'
                                break

                # Build dictionary
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}
                if 'areas' not in ret_dict['vrf'][vrf]['address_family']\
                        [af]['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if intf_type not in ret_dict['vrf'][vrf]['address_family']\
                        [af]['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type] = {}
                if intf_name not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area][intf_type]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type][intf_name] = {}
                
                # Set sub_dict
                sub_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                            ['instance'][instance]['areas'][area]\
                            [intf_type][intf_name]
                # Delete variables to avoid overwrite issues for next intf
                del area
                del intf_name
                
                # Set values found in this regex
                sub_dict['router_id'] = router_id
                sub_dict['interface_type'] = interface_type
                if m.groupdict()['cost']:
                    sub_dict['cost'] = int(m.groupdict()['cost'])

                # Set defaault keys
                sub_dict['demand_circuit'] = False
                if 'bfd' not in sub_dict:
                    sub_dict['bfd'] = {}
                sub_dict['bfd']['enable'] = False

                # Set previously parsed keys
                try:
                    sub_dict['name'] = name
                    del name
                except Exception:
                    pass
                try:
                    sub_dict['ip_address'] = ip_address
                    del ip_address
                except Exception:
                    pass
                try:
                    sub_dict['interface_id'] = intf_id
                    del intf_id
                except Exception:
                    pass
                try:
                    sub_dict['attached'] = attached
                    del attached
                except Exception:
                    pass
                try:
                    sub_dict['enable'] = bool_dict[enable]
                except Exception:
                    pass
                try:
                    sub_dict['line_protocol'] = bool_dict[line_protocol]
                except Exception:
                    pass
                continue

            # Topology-MTID    Cost    Disabled    Shutdown      Topology Name
            #             0       1          no          no               Base
            p4 = re.compile(r'^(?P<mtid>(\d+)) +(?P<topo_cost>(\d+))'
                             r' +(?P<disabled>(yes|no)) +(?P<shutdown>(yes|no))'
                             r' +(?P<topo_name>(\S+))$')
            m = p4.match(line)
            if m:
                mtid = int(m.groupdict()['mtid'])
                if 'topology' not in sub_dict:
                    sub_dict['topology'] = {}
                if mtid not in sub_dict['topology']:
                    sub_dict['topology'][mtid] = {}
                sub_dict['topology'][mtid]['cost'] = int(m.groupdict()['topo_cost'])
                sub_dict['topology'][mtid]['name'] = str(m.groupdict()['topo_name'])
                if 'yes' in m.groupdict()['disabled']:
                    sub_dict['topology'][mtid]['disabled'] = True
                else:
                    sub_dict['topology'][mtid]['disabled'] = False
                if 'yes' in m.groupdict()['shutdown']:
                    sub_dict['topology'][mtid]['shutdown'] = True
                else:
                    sub_dict['topology'][mtid]['shutdown'] = False
                    continue

            # Configured as demand circuit
            m = p5.match(line)
            if m:
                sub_dict['demand_circuit'] = True
                continue

            # Run as demand circuit
            m = p6.match(line)
            if m:
                sub_dict['demand_circuit'] = True
                continue

            # DoNotAge LSA not allowed (Number of DCbitless LSA is 1).
            m = p7.match(line)
            if m:
                sub_dict['donotage_lsa'] = False
                sub_dict['total_dcbitless_lsa'] = int(m.groupdict()['num'])
                continue

            # Enabled by interface config, including secondary ip addresses
            m = p8.match(line)
            if m:
                sub_dict['if_cfg'] = True
                continue

            # Transmit Delay is 1 sec, State POINT_TO_POINT
            # Transmit Delay is 1 sec, State DR, Priority 1
            # Transmit Delay is 1 sec, State DR, Priority 111, BFD enabled
            m = p9.match(line)
            if m:
                sub_dict['transmit_delay'] = int(m.groupdict()['delay'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace("_", "-")
                sub_dict['state'] = state
                if m.groupdict()['priority']:
                    sub_dict['priority'] = int(m.groupdict()['priority'])
                if m.groupdict()['bfd']:
                    if 'bfd' not in sub_dict:
                        sub_dict['bfd'] = {}
                    if 'enabled' in m.groupdict()['bfd']:
                        sub_dict['bfd']['enable'] = True
                    else:
                        sub_dict['bfd']['enable'] = False
                        continue

            # Designated Router (ID) 10.36.3.3, Interface address 10.2.3.3
            m = p10.match(line)
            if m:
                sub_dict['dr_router_id'] = str(m.groupdict()['dr_router_id'])
                sub_dict['dr_ip_addr'] = str(m.groupdict()['dr_ip_addr'])
                continue

            # Backup Designated router (ID) 10.16.2.2, Interface address 10.2.3.2
            m = p11.match(line)
            if m:
                sub_dict['bdr_router_id'] = str(m.groupdict()['bdr_router_id'])
                sub_dict['bdr_ip_addr'] = str(m.groupdict()['bdr_ip_addr'])
                continue

            # Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
            m = p12.match(line)
            if m:
                sub_dict['hello_interval'] = int(m.groupdict()['hello'])
                sub_dict['dead_interval'] = int(m.groupdict()['dead'])
                sub_dict['wait_interval'] = int(m.groupdict()['wait'])
                sub_dict['retransmit_interval'] = int(m.groupdict()['retransmit'])
                continue

            #  oob-resync timeout 40
            m = p12_1.match(line)
            if m:
                sub_dict['oob_resync_timeout'] = int(m.groupdict()['oob'])
                continue
            
            # Hello due in 00:00:00
            m = p12_2.match(line)
            if m:
                sub_dict['passive'] = False
                sub_dict['hello_timer'] = str(m.groupdict()['hello_timer'])
                continue

            # Supports Link-local Signaling (LLS)
            m = p13.match(line)
            if m:
                sub_dict['lls'] = True
                continue
            
            # Cisco NSF helper support enabled
            # IETF NSF helper support enabled
            m = p14.match(line)
            if m:
                gr_type = str(m.groupdict()['gr_type']).lower()
                if 'graceful_restart' not in sub_dict:
                    sub_dict['graceful_restart'] = {}
                if gr_type not in sub_dict['graceful_restart']:
                    sub_dict['graceful_restart'][gr_type] = {}
                sub_dict['graceful_restart'][gr_type]['type'] = gr_type
                if 'enabled' in m.groupdict()['helper']:
                    sub_dict['graceful_restart'][gr_type]['helper'] = True
                else:
                    sub_dict['graceful_restart'][gr_type]['helper'] = False
                continue

            # Index 2/2, flood queue length 0
            m = p15.match(line)
            if m:
                sub_dict['index'] = str(m.groupdict()['index'])
                sub_dict['flood_queue_length'] = int(m.groupdict()['length'])
                continue

            # Next 0(0)/0(0)
            m = p16.match(line)
            if m:
                sub_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last flood scan length is 0, maximum is 11
            m = p17.match(line)
            if m:
                sub_dict['last_flood_scan_length'] = int(m.groupdict()['num'])
                sub_dict['max_flood_scan_length'] = int(m.groupdict()['max'])
                continue

            # Last flood scan time is 0 msec, maximum is 1 msec
            m = p18.match(line)
            if m:
                sub_dict['last_flood_scan_time_msec'] = \
                    int(m.groupdict()['time1'])
                sub_dict['max_flood_scan_time_msec'] = \
                    int(m.groupdict()['time2'])
                continue

            # Neighbor Count is 1, Adjacent neighbor count is 1
            m = p19.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['nbr_count'] = \
                    int(m.groupdict()['nbr_count'])
                sub_dict['statistics']['adj_nbr_count'] = \
                    int(m.groupdict()['adj_nbr_count'])
                continue

            # Adjacent with neighbor 10.16.2.2 (Backup Designated Router)
            m = p20_1.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                sub_dict['neighbors'][neighbor]['bdr_router_id'] = neighbor
                continue

            # Adjacent with neighbor 10.36.3.3 (Designated Router)
            m = p20_2.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                sub_dict['neighbors'][neighbor]['dr_router_id'] = neighbor
                continue

            # Adjacent with neighbor 10.64.4.4 (Hello suppressed)
            m = p20_3.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                continue

            # Suppress hello for 0 neighbor(s)
            m = p21.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['num_nbrs_suppress_hello'] = \
                    int(m.groupdict()['sup'])
                continue

            # Loopback interface is treated as a stub Host
            m = p22.match(line)
            if m:
                sub_dict['stub_host'] = True
                continue

            # Can be protected by per-prefix Loop-Free FastReroute
            m = p23.match(line)
            if m:
                sub_dict['ipfrr_protected'] = True
                continue

            # Can be used for per-prefix Loop-Free FastReroute repair paths
            m = p24.match(line)
            if m:
                sub_dict['ipfrr_candidate'] = True
                continue

            # Not Protected by per-prefix TI-LFA
            m = p25.match(line)
            if m:
                sub_dict['ti_lfa_protected'] = False
                continue

            # Prefix-suppression is enabled
            m = p26.match(line)
            if m:
                if 'enabled' in m.groupdict()['ps']:
                    sub_dict['prefix_suppression'] = True
                else:
                    sub_dict['prefix_suppression'] = False

            # Strict TTL checking enabled, up to 3 hops allowed
            m = p27.match(line)
            if m:
                if 'ttl_security' not in sub_dict:
                    sub_dict['ttl_security'] = {}
                if 'enabled' in m.groupdict()['strict_ttl']:
                    sub_dict['ttl_security']['enable'] = True
                else:
                    sub_dict['ttl_security']['enable'] = False
                if m.groupdict()['hops']:
                    sub_dict['ttl_security']['hops'] = int(m.groupdict()['hops'])
                    continue

            # Simple password authentication enabled
            m = p28_1.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'simple'
                continue

            # Cryptographic authentication enabled
            m = p28_2.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'md5'
                continue

            # Youngest key id is 2
            m = p28_3.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['youngest_key_id'] = int(m.groupdict()['id'])
                continue
            
            # Rollover in progress, 1 neighbor(s) using the old key(s):
            m = p28_4.match(line)
            if m:
                continue

            # key id 1 algorithm MD5
            m = p28_5.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'md5'
                continue

            # Segment Routing enabled for MPLS forwarding
            m = p29.match(line)
            if m:
                sub_dict.update({'sr_mpls_enabled': True})
                continue

            # TEAPP:
            m = p30.match(line)
            if m:
                teapp_dict = sub_dict.setdefault('teapp', {})
                continue

            # Topology Id:0x0
            m = p30_1.match(line)
            if m:
                topology_id = m.groupdict()['topology_id']
                teapp_dict = sub_dict.setdefault('teapp', {})
                teapp_dict.update({'topology_id': topology_id})
                continue

            # TEAPP:SRTE
            m = p30_2.match(line)
            if m:
                teapp = m.groupdict()['teapp']
                teapp_dict = sub_dict.setdefault('teapp', {})
                item_dict = teapp_dict.setdefault(teapp, {})
                continue

            # Affinity: length 32, bits 0x00000010
            m = p30_3.match(line)
            if m:
                length = int(m.groupdict()['length'])
                bits = m.groupdict()['bits']
                aff_dict = item_dict.setdefault('affinity', {})
                aff_dict.update({'length': length})
                aff_dict.update({'bits': bits})
                continue

            # Extended affinity: length 32, bits 0x00000010
            m = p30_4.match(line)
            if m:
                length = int(m.groupdict()['length'])
                bits = m.groupdict()['bits']
                exa_dict = item_dict.setdefault('extended_affinity', {})
                exa_dict.update({'length': length})
                exa_dict.update({'bits': bits})
                continue
            
            # SR Policy Manager:
            m = p31.match(line)
            if m:
                mgn_dict = sub_dict.setdefault('sr_policy_manager', {})
                continue

            # TE Opaque LSA: Source of link information OSPF
            m = p31_1.match(line)
            if m:
                mgn_dict.update({'te_opaque_lsa': m.groupdict()['te_opaque_lsa']})

        return ret_dict


# ============================
# Schema for:
#   * 'show ip ospf interface'
#   * 'show ip ospf interface {interface}''
# ============================
class ShowIpOspfInterface2Schema(MetaParser):

    ''' Schema for:
        * 'show ip ospf interface__'
    '''
    schema ={
                'address_family': 
                    {Any(): 
                        {'instance': 
                            {Any(): 
                                {'areas': 
                                    {Any(): 
                                        {Optional('interfaces'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int,
                                                    },
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                        Optional('virtual_links'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int,
                                                    },
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                        Optional('sham_links'): 
                                            {Any(): 
                                                {'name': str,
                                                'enable': bool,
                                                'line_protocol': bool,
                                                'ip_address': str,
                                                Optional('interface_id'): int,
                                                Optional('attached'): str,
                                                'demand_circuit': bool,
                                                'router_id': str,
                                                'interface_type': str,
                                                'bfd': 
                                                    {'enable': bool},
                                                Optional('if_cfg'): bool,
                                                Optional('cost'): int,
                                                Optional('transmit_delay'): int,
                                                Optional('state'): str,
                                                Optional('priority'): int,
                                                Optional('dr_router_id'): str,
                                                Optional('dr_ip_addr'): str,
                                                Optional('bdr_router_id'): str,
                                                Optional('bdr_ip_addr'): str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('passive'): bool,
                                                Optional('oob_resync_timeout'): int,
                                                Optional('hello_timer'): str,
                                                Optional('index'): str,
                                                Optional('flood_queue_length'): int,
                                                Optional('next'): str,
                                                Optional('lls'): bool,
                                                Optional('last_flood_scan_length'): int,
                                                Optional('max_flood_scan_length'): int,
                                                Optional('last_flood_scan_time_msec'): int,
                                                Optional('max_flood_scan_time_msec'): int,
                                                Optional('total_dcbitless_lsa'): int,
                                                Optional('donotage_lsa'): bool,
                                                Optional('ti_lfa_protected'): bool,
                                                Optional('ipfrr_candidate'): bool,
                                                Optional('ipfrr_protected'): bool,
                                                Optional('stub_host'): bool,
                                                Optional('prefix_suppression'): bool,
                                                Optional('ttl_security'): 
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                Optional('graceful_restart'): 
                                                    {Any(): 
                                                        {'type': str,
                                                        'helper': bool}},
                                                Optional('topology'): 
                                                    {Any(): 
                                                        {'cost': int,
                                                        'disabled': bool,
                                                        'shutdown': bool,
                                                        'name': str}},
                                                Optional('statistics'): 
                                                    {Optional('adj_nbr_count'): int,
                                                    Optional('nbr_count'): int,
                                                    Optional('num_nbrs_suppress_hello'): int},
                                                Optional('neighbors'): 
                                                    {Any(): 
                                                        {Optional('dr_router_id'): str,
                                                        Optional('bdr_router_id'): str,
                                                        },
                                                    },
                                                Optional('authentication'): 
                                                    {'auth_trailer_key': 
                                                        {'crypto_algorithm': str,
                                                        Optional('youngest_key_id'): int,
                                                        },
                                                    },
                                                Optional('teapp'): {
                                                    Optional('topology_id'): str,
                                                    Any(): {
                                                        Optional('affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                        Optional('extended_affinity'): {
                                                            'length': int,
                                                            'bits': str,
                                                        },
                                                    },
                                                },
                                                Optional('sr_policy_manager'): {
                                                    'te_opaque_lsa': str,
                                                },
                                                Optional('sr_mpls_enabled'): bool,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            }

# ===========================================
# Parser for:
#   * 'show ospf vrf all-inclusive interface'
# ===========================================
class ShowIpOspfInterface2(ShowIpOspfInterface2Schema):

    ''' Parser for:
        * 'show ip ospf interface__'
    '''

    cli_command = 'show ip ospf interface__'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        # Mapping dict
        bool_dict = {'up': True, 'down': False, 'unknown': False}

        
        p1 = re.compile(r'^(?P<interface>(\S+)) +is( +administratively)?'
                            r' +(?P<enable>(unknown|up|down)), +line +protocol'
                            r' +is +(?P<line_protocol>(up|down))'
                            r'(?: +\(\S+\))?$')
        # Internet Address 0.0.0.1/30|Interface is unnumbered, Interface ID 55, Area 0
        p2 = re.compile(r'^(Internet +Address|Interface +is) +(?P<address>(\S+)),'
                            r'(?: +Interface +ID +(?P<intf_id>(\d+)),)?'
                            r' +Area +(?P<area>(\S+))(?:, +Attached +via'
                            r' +(?P<attach>(.*)))?$')
 
        p2_1 = re.compile(r'^Attached +via +(?P<attached>([a-zA-Z0-9\s]+))$')
 
        p3 = re.compile(r'^Process +ID +(?P<pid>(\S+)),'
                            r'(?: +VRF +(?P<vrf>(\S+)))?'
                            r' +Router +ID +(?P<router_id>(\S+)),'
                            r' +Network +Type +(?P<interface_type>(\S+)),'
                            r' +Cost: +(?P<cost>(\d+))$')

        p5 = re.compile(r'^Configured as demand circuit$')
 
        p6 = re.compile(r'^Run as demand circuit$')
 
        p7 = re.compile(r'^DoNotAge +LSA +not +allowed +\(Number +of'
                            r' +DCbitless +LSA +is +(?P<num>(\d+))\)\.$')
 
        p8 = re.compile(r'^Enabled +by +interface +config, +including'
                            r' +secondary +ip +addresses$')
 
        p9 = re.compile(r'^Transmit +Delay is +(?P<delay>(\d+)) +sec,'
                            r' +State +(?P<state>(\S+))'
                            r'(?:, +Priority +(?P<priority>(\d+)))?'
                            r'(?:, +BFD +(?P<bfd>(enabled|disabled)))?$')
 
        p10 = re.compile(r'^Designated +(R|r)outer +\(ID\)'
                            r' +(?P<dr_router_id>(\S+)), +(I|i)nterface'
                            r' +(A|a)ddress +(?P<dr_ip_addr>(\S+))$')
 
        p11 = re.compile(r'^Backup +(D|d)esignated +(R|r)outer +\(ID\)'
                            r' +(?P<bdr_router_id>(\S+)), +(I|i)nterface'
                            r' +(A|a)ddress +(?P<bdr_ip_addr>(\S+))$')
 
        p12 = re.compile(r'^Timer +intervals +configured,'
                            r' +Hello +(?P<hello>(\d+)),'
                            r' +Dead +(?P<dead>(\d+)),'
                            r' +Wait +(?P<wait>(\d+)),'
                            r' +Retransmit +(?P<retransmit>(\d+))$')
 
        p12_1 = re.compile(r'^oob-resync +timeout +(?P<oob>(\d+))$')
 
        p12_2 = re.compile(r'^Hello +due +in +(?P<hello_timer>(\S+))$')
 
        p13 = re.compile(r'^Supports +Link-local +Signaling +\(LLS\)$')
 
        p14 = re.compile(r'^(?P<gr_type>(Cisco|IETF)) +NSF +helper +support'
                            r' +(?P<helper>(enabled|disabled))$')
 
        p15 = re.compile(r'^Index +(?P<index>(\S+)),'
                            r' +flood +queue +length +(?P<length>(\d+))$')
 
        p16 = re.compile(r'^Next +(?P<next>(\S+))$')
 
        p17 = re.compile(r'^Last +flood +scan +length +is +(?P<num>(\d+)),'
                            r' +maximum +is +(?P<max>(\d+))$')
 
        p18 = re.compile(r'^Last +flood +scan +time +is +(?P<time1>(\d+))'
                            r' +msec, +maximum +is +(?P<time2>(\d+)) +msec$')
 
        p19 = re.compile(r'^Neighbor +Count +is +(?P<nbr_count>(\d+)),'
                            r' +Adjacent +neighbor +count +is'
                            r' +(?P<adj_nbr_count>(\d+))$')
 
        p20_1 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\((B|b)ackup +(D|d)esignated +(R|r)outer\)$')
 
        p20_2 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\((D|d)esignated +(R|r)outer\)$')
 
        p20_3 = re.compile(r'^Adjacent +with +neighbor +(?P<nbr>(\S+))'
                            r' +\(Hello suppressed\)$')
 
        p21 = re.compile(r'^Suppress +hello +for +(?P<sup>(\d+))'
                            r' +neighbor\(s\)$')
 
        p22 = re.compile(r'^Loopback +interface +is +treated +as +a +stub'
                            r' +Host$')
 
        p23 = re.compile(r'^Can +be +protected +by per-+prefix +Loop-Free'
                            r' +FastReroute$')
 
        p24 = re.compile(r'^Can +be +used +for +per-prefix +Loop-Free'
                            r' +FastReroute +repair +paths$')
 
        p25 = re.compile(r'^Not +Protected +by +per-prefix +TI-LFA$')
 
        p26 = re.compile(r'^Prefix-suppression +is +(?P<ps>(enabled|disabled))$')
 
        p27 = re.compile(r'^Strict +TTL +checking'
                            r' +(?P<strict_ttl>(enabled|disabled))'
                            r'(?:, +up +to +(?P<hops>(\d+)) +hops +allowed)?$')
 
        p28_1 = re.compile(r'^Simple +password +authentication +enabled$')
 
        p28_2 = re.compile(r'^Cryptographic +authentication +enabled$')
 
        p28_3 = re.compile(r'^Youngest +key +id +is +(?P<id>(\d+))$')
 
        p28_4 = re.compile(r'^Rollover +in +progress, +(?P<num>(\d+))'
                            r' +neighbor(s) +using +the +old +key(s):$')
 
        p28_5 = re.compile(r'^key +id +1 +algorithm +MD5$')

        # Segment Routing enabled for MPLS forwarding
        p29 = re.compile(r'^Segment +Routing +enabled +for +MPLS +forwarding$')

        # TEAPP:
        p30 = re.compile(r'^TEAPP:$')

        # Topology Id:0x0
        p30_1 = re.compile(r'^Topology +Id: *(?P<topology_id>[\w]+)$')

        # TEAPP:SRTE
        p30_2 = re.compile(r'^TEAPP: *(?P<teapp>[\w]+)$')

        # Affinity: length 32, bits 0x00000010
        p30_3 = re.compile(r'^Affinity: *length +(?P<length>\d+), +bits +(?P<bits>\w+)$')

        # Extended affinity: length 32, bits 0x00000010
        p30_4 = re.compile(r'^Extended +affinity: *length +(?P<length>\d+), +bits +(?P<bits>\w+)$')

        # SR Policy Manager:
        p31 = re.compile(r'^SR +Policy +Manager:$')

        # TE Opaque LSA: Source of link information OSPF
        p31_1 = re.compile(r'^TE +Opaque +LSA: +(?P<te_opaque_lsa>[\S\s]+)$')

        for line in out.splitlines():
            line = line.strip()

            # Loopback0 is up, line protocol is up 
            # GigabitEthernet2 is up, line protocol is up
            # Port-channel2.100 is administratively down, line protocol is down
            # OSPF_SL1 is up, line protocol is up 
            # OSPF_VL3 is up, line protocol is up 
            # TenGigabitEthernet3/0/1 is up, line protocol is up (connected)
            # TenGigabitEthernet1/8 is down, line protocol is down (notconnect)
            # TenGigabitEthernet2/6.3052 is administratively down, line protocol is down (disabled)
            # TenGigabitEthernet1/15 is down, line protocol is down (err-disabled)
            m = p1.match(line)
            if m:
                interface = str(m.groupdict()['interface'])
                enable = str(m.groupdict()['enable'])
                line_protocol = str(m.groupdict()['line_protocol'])

                # Determine if 'interface' or 'sham_link' or 'virtual_link'
                if re.search('SL', interface):
                    x = re.match(r'(?P<ignore>\S+)_SL(?P<num>(\d+))', interface)
                    if x:
                        intf_type = 'sham_links'
                        name = 'SL' + str(x.groupdict()['num'])
                elif re.search('VL', interface):
                    x = re.match(r'(?P<ignore>\S+)_VL(?P<num>(\d+))', interface)
                    if x:
                        intf_type = 'virtual_links'
                        name = 'VL' + str(x.groupdict()['num'])
                else:
                    intf_type = 'interfaces'
                    name = interface
                continue

            # Internet Address 10.4.1.1/32, Interface ID 11, Area 0
            # Internet Address 0.0.0.0/0, Area 0, Attached via Not Attached
            # Internet Address 10.229.4.4/24, Area 1, Attached via Interface Enable
            m = p2.match(line)
            if m:
                ip_address = str(m.groupdict()['address'])
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                if m.groupdict()['intf_id']:
                    intf_id = int(m.groupdict()['intf_id'])
                if m.groupdict()['attach']:
                    attached = str(m.groupdict()['attach']).lower()
                continue

            # Attached via Interface Enable
            m = p2_1.match(line)
            if m:
                attached = str(m.groupdict()['attached']).lower()
                continue

            # Process ID 1, Router ID 10.64.4.4, Network Type VIRTUAL_LINK, Cost: 1
            # Process ID 2, Router ID 10.229.11.11, Network Type SHAM_LINK, Cost: 111
            # Process ID 1, Router ID 10.4.1.1, Network Type BROADCAST, Cost: 1
            m = p3.match(line)
            if m:
                instance = str(m.groupdict()['pid'])
                router_id = str(m.groupdict()['router_id'])
                interface_type = str(m.groupdict()['interface_type']).lower()
                interface_type = interface_type.replace("_", "-")

                # Get interface values
                intf_name = interface

                # Build dictionary
                if 'address_family' not in ret_dict:
                    ret_dict['address_family'] = {}
                if af not in ret_dict['address_family']:
                    ret_dict['address_family'][af] = {}
                if 'instance' not in ret_dict['address_family'][af]:
                    ret_dict['address_family'][af]['instance'] = {}
                if instance not in ret_dict['address_family'][af]\
                        ['instance']:
                    ret_dict['address_family'][af]['instance']\
                        [instance] = {}
                if 'areas' not in ret_dict['address_family']\
                        [af]['instance'][instance]:
                    ret_dict['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if intf_type not in ret_dict['address_family']\
                        [af]['instance'][instance]['areas'][area]:
                    ret_dict['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type] = {}
                if intf_name not in ret_dict['address_family'][af]\
                        ['instance'][instance]['areas'][area][intf_type]:
                    ret_dict['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type][intf_name] = {}
                
                # Set sub_dict
                sub_dict = ret_dict['address_family'][af]\
                            ['instance'][instance]['areas'][area]\
                            [intf_type][intf_name]
                # Delete variables to avoid overwrite issues for next intf
                del area
                del intf_name
                
                # Set values found in this regex
                sub_dict['router_id'] = router_id
                sub_dict['interface_type'] = interface_type
                if m.groupdict()['cost']:
                    sub_dict['cost'] = int(m.groupdict()['cost'])

                # Set default keys
                sub_dict['demand_circuit'] = False
                if 'bfd' not in sub_dict:
                    sub_dict['bfd'] = {}
                sub_dict['bfd']['enable'] = False

                # Set previously parsed keys
                try:
                    sub_dict['name'] = name
                    del name
                except Exception:
                    pass
                try:
                    sub_dict['ip_address'] = ip_address
                    del ip_address
                except Exception:
                    pass
                try:
                    sub_dict['interface_id'] = intf_id
                    del intf_id
                except Exception:
                    pass
                try:
                    sub_dict['attached'] = attached
                    del attached
                except Exception:
                    pass
                try:
                    sub_dict['enable'] = bool_dict[enable]
                except Exception:
                    pass
                try:
                    sub_dict['line_protocol'] = bool_dict[line_protocol]
                except Exception:
                    pass
                continue

            # Topology-MTID    Cost    Disabled    Shutdown      Topology Name
            #             0       1          no          no               Base
            p4 = re.compile(r'^(?P<mtid>(\d+)) +(?P<topo_cost>(\d+))'
                             r' +(?P<disabled>(yes|no)) +(?P<shutdown>(yes|no))'
                             r' +(?P<topo_name>(\S+))$')
            m = p4.match(line)
            if m:
                mtid = int(m.groupdict()['mtid'])
                if 'topology' not in sub_dict:
                    sub_dict['topology'] = {}
                if mtid not in sub_dict['topology']:
                    sub_dict['topology'][mtid] = {}
                sub_dict['topology'][mtid]['cost'] = int(m.groupdict()['topo_cost'])
                sub_dict['topology'][mtid]['name'] = str(m.groupdict()['topo_name'])
                if 'yes' in m.groupdict()['disabled']:
                    sub_dict['topology'][mtid]['disabled'] = True
                else:
                    sub_dict['topology'][mtid]['disabled'] = False
                if 'yes' in m.groupdict()['shutdown']:
                    sub_dict['topology'][mtid]['shutdown'] = True
                else:
                    sub_dict['topology'][mtid]['shutdown'] = False
                    continue

            # Configured as demand circuit
            m = p5.match(line)
            if m:
                sub_dict['demand_circuit'] = True
                continue

            # Run as demand circuit
            m = p6.match(line)
            if m:
                sub_dict['demand_circuit'] = True
                continue

            # DoNotAge LSA not allowed (Number of DCbitless LSA is 1).
            m = p7.match(line)
            if m:
                sub_dict['donotage_lsa'] = False
                sub_dict['total_dcbitless_lsa'] = int(m.groupdict()['num'])
                continue

            # Enabled by interface config, including secondary ip addresses
            m = p8.match(line)
            if m:
                sub_dict['if_cfg'] = True
                continue

            # Transmit Delay is 1 sec, State POINT_TO_POINT
            # Transmit Delay is 1 sec, State DR, Priority 1
            # Transmit Delay is 1 sec, State DR, Priority 111, BFD enabled
            m = p9.match(line)
            if m:
                sub_dict['transmit_delay'] = int(m.groupdict()['delay'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace("_", "-")
                sub_dict['state'] = state
                if m.groupdict()['priority']:
                    sub_dict['priority'] = int(m.groupdict()['priority'])
                if m.groupdict()['bfd']:
                    if 'bfd' not in sub_dict:
                        sub_dict['bfd'] = {}
                    if 'enabled' in m.groupdict()['bfd']:
                        sub_dict['bfd']['enable'] = True
                    else:
                        sub_dict['bfd']['enable'] = False
                        continue

            # Designated Router (ID) 10.36.3.3, Interface address 10.2.3.3
            m = p10.match(line)
            if m:
                sub_dict['dr_router_id'] = str(m.groupdict()['dr_router_id'])
                sub_dict['dr_ip_addr'] = str(m.groupdict()['dr_ip_addr'])
                continue

            # Backup Designated router (ID) 10.16.2.2, Interface address 10.2.3.2
            m = p11.match(line)
            if m:
                sub_dict['bdr_router_id'] = str(m.groupdict()['bdr_router_id'])
                sub_dict['bdr_ip_addr'] = str(m.groupdict()['bdr_ip_addr'])
                continue

            # Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
            m = p12.match(line)
            if m:
                sub_dict['hello_interval'] = int(m.groupdict()['hello'])
                sub_dict['dead_interval'] = int(m.groupdict()['dead'])
                sub_dict['wait_interval'] = int(m.groupdict()['wait'])
                sub_dict['retransmit_interval'] = int(m.groupdict()['retransmit'])
                continue

            #  oob-resync timeout 40
            m = p12_1.match(line)
            if m:
                sub_dict['oob_resync_timeout'] = int(m.groupdict()['oob'])
                continue
            
            # Hello due in 00:00:00
            m = p12_2.match(line)
            if m:
                sub_dict['passive'] = False
                sub_dict['hello_timer'] = str(m.groupdict()['hello_timer'])
                continue

            # Supports Link-local Signaling (LLS)
            m = p13.match(line)
            if m:
                sub_dict['lls'] = True
                continue
            
            # Cisco NSF helper support enabled
            # IETF NSF helper support enabled
            m = p14.match(line)
            if m:
                gr_type = str(m.groupdict()['gr_type']).lower()
                if 'graceful_restart' not in sub_dict:
                    sub_dict['graceful_restart'] = {}
                if gr_type not in sub_dict['graceful_restart']:
                    sub_dict['graceful_restart'][gr_type] = {}
                sub_dict['graceful_restart'][gr_type]['type'] = gr_type
                if 'enabled' in m.groupdict()['helper']:
                    sub_dict['graceful_restart'][gr_type]['helper'] = True
                else:
                    sub_dict['graceful_restart'][gr_type]['helper'] = False
                continue

            # Index 2/2, flood queue length 0
            m = p15.match(line)
            if m:
                sub_dict['index'] = str(m.groupdict()['index'])
                sub_dict['flood_queue_length'] = int(m.groupdict()['length'])
                continue

            # Next 0(0)/0(0)
            m = p16.match(line)
            if m:
                sub_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last flood scan length is 0, maximum is 11
            m = p17.match(line)
            if m:
                sub_dict['last_flood_scan_length'] = int(m.groupdict()['num'])
                sub_dict['max_flood_scan_length'] = int(m.groupdict()['max'])
                continue

            # Last flood scan time is 0 msec, maximum is 1 msec
            m = p18.match(line)
            if m:
                sub_dict['last_flood_scan_time_msec'] = \
                    int(m.groupdict()['time1'])
                sub_dict['max_flood_scan_time_msec'] = \
                    int(m.groupdict()['time2'])
                continue

            # Neighbor Count is 1, Adjacent neighbor count is 1
            m = p19.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['nbr_count'] = \
                    int(m.groupdict()['nbr_count'])
                sub_dict['statistics']['adj_nbr_count'] = \
                    int(m.groupdict()['adj_nbr_count'])
                continue

            # Adjacent with neighbor 10.16.2.2 (Backup Designated Router)
            m = p20_1.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                sub_dict['neighbors'][neighbor]['bdr_router_id'] = neighbor
                continue

            # Adjacent with neighbor 10.36.3.3 (Designated Router)
            m = p20_2.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                sub_dict['neighbors'][neighbor]['dr_router_id'] = neighbor
                continue

            # Adjacent with neighbor 10.64.4.4 (Hello suppressed)
            m = p20_3.match(line)
            if m:
                neighbor = str(m.groupdict()['nbr'])
                if 'neighbors' not in sub_dict:
                    sub_dict['neighbors'] = {}
                if neighbor not in sub_dict['neighbors']:
                    sub_dict['neighbors'][neighbor] = {}
                continue

            # Suppress hello for 0 neighbor(s)
            m = p21.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['num_nbrs_suppress_hello'] = \
                    int(m.groupdict()['sup'])
                continue

            # Loopback interface is treated as a stub Host
            m = p22.match(line)
            if m:
                sub_dict['stub_host'] = True
                continue

            # Can be protected by per-prefix Loop-Free FastReroute
            m = p23.match(line)
            if m:
                sub_dict['ipfrr_protected'] = True
                continue

            # Can be used for per-prefix Loop-Free FastReroute repair paths
            m = p24.match(line)
            if m:
                sub_dict['ipfrr_candidate'] = True
                continue

            # Not Protected by per-prefix TI-LFA
            m = p25.match(line)
            if m:
                sub_dict['ti_lfa_protected'] = False
                continue

            # Prefix-suppression is enabled
            m = p26.match(line)
            if m:
                if 'enabled' in m.groupdict()['ps']:
                    sub_dict['prefix_suppression'] = True
                else:
                    sub_dict['prefix_suppression'] = False

            # Strict TTL checking enabled, up to 3 hops allowed
            m = p27.match(line)
            if m:
                if 'ttl_security' not in sub_dict:
                    sub_dict['ttl_security'] = {}
                if 'enabled' in m.groupdict()['strict_ttl']:
                    sub_dict['ttl_security']['enable'] = True
                else:
                    sub_dict['ttl_security']['enable'] = False
                if m.groupdict()['hops']:
                    sub_dict['ttl_security']['hops'] = int(m.groupdict()['hops'])
                    continue

            # Simple password authentication enabled
            m = p28_1.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'simple'
                continue

            # Cryptographic authentication enabled
            m = p28_2.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'md5'
                continue

            # Youngest key id is 2
            m = p28_3.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['youngest_key_id'] = int(m.groupdict()['id'])
                continue
            
            # Rollover in progress, 1 neighbor(s) using the old key(s):
            m = p28_4.match(line)
            if m:
                continue

            # key id 1 algorithm MD5
            m = p28_5.match(line)
            if m:
                if 'authentication' not in sub_dict:
                    sub_dict['authentication'] = {}
                if 'auth_trailer_key' not in sub_dict['authentication']:
                    sub_dict['authentication']['auth_trailer_key'] = {}
                sub_dict['authentication']['auth_trailer_key']\
                    ['crypto_algorithm'] = 'md5'
                continue

            # Segment Routing enabled for MPLS forwarding
            m = p29.match(line)
            if m:
                sub_dict.update({'sr_mpls_enabled': True})
                continue

            # TEAPP:
            m = p30.match(line)
            if m:
                teapp_dict = sub_dict.setdefault('teapp', {})
                continue

            # Topology Id:0x0
            m = p30_1.match(line)
            if m:
                topology_id = m.groupdict()['topology_id']
                teapp_dict = sub_dict.setdefault('teapp', {})
                teapp_dict.update({'topology_id': topology_id})
                continue

            # TEAPP:SRTE
            m = p30_2.match(line)
            if m:
                teapp = m.groupdict()['teapp']
                teapp_dict = sub_dict.setdefault('teapp', {})
                item_dict = teapp_dict.setdefault(teapp, {})
                continue

            # Affinity: length 32, bits 0x00000010
            m = p30_3.match(line)
            if m:
                length = int(m.groupdict()['length'])
                bits = m.groupdict()['bits']
                aff_dict = item_dict.setdefault('affinity', {})
                aff_dict.update({'length': length})
                aff_dict.update({'bits': bits})
                continue

            # Extended affinity: length 32, bits 0x00000010
            m = p30_4.match(line)
            if m:
                length = int(m.groupdict()['length'])
                bits = m.groupdict()['bits']
                exa_dict = item_dict.setdefault('extended_affinity', {})
                exa_dict.update({'length': length})
                exa_dict.update({'bits': bits})
                continue
            
            # SR Policy Manager:
            m = p31.match(line)
            if m:
                mgn_dict = sub_dict.setdefault('sr_policy_manager', {})
                continue

            # TE Opaque LSA: Source of link information OSPF
            m = p31_1.match(line)
            if m:
                mgn_dict.update({'te_opaque_lsa': m.groupdict()['te_opaque_lsa']})

        return ret_dict

# ================================
# Super parser for:
#   * 'show ip ospf virtual-links'
#   * 'show ip ospf sham-links'
# ================================
class ShowIpOspfLinksParser(MetaParser):

    ''' Parser for:
        * 'show ip ospf virtual-links'
        * 'show ip ospf sham-links'
    '''

    def cli(self, cmd, link_type,output=None):

        assert link_type in ['virtual_links', 'sham_links']

        if output is None:
            out = self.device.execute(cmd)
        else:
            out = output
        
        # Init vars
        ret_dict = {}
        af = 'ipv4'

        # crypo_algorithm dict
        crypto_dict = {'cryptographic': 'md5', 'simple password': 'simple'}


        p1 = re.compile(r'^(Virtual|Sham) +Link +(?P<interface>(\S+)) +to'
                            r' +(address|router) +(?P<address>(\S+)) +is'
                            r' +(?P<link_state>(up|down))$')

        p2 = re.compile(r'^Area +(?P<area>(\S+)),? +source +address'
                            r' +(?P<source_address>(\S+))$')

        p3 = re.compile(r'^Run +as +demand +circuit$')

        p4 = re.compile(r'^DoNotAge +LSA +not +allowed'
                            r' +\(Number +of +DCbitless +LSA +is +(?P<dcbitless>(\d+))\).'
                            r'(?: +Cost +of +using +(?P<cost>(\d+)))?'
                            r'(?: State +(?P<state>(\S+)))?$')

        p5 = re.compile(r'^Transit +area +(?P<area>(\S+)),'
                            r'(?: +via +interface +(?P<intf>(\S+)))?$')

        p6 = re.compile(r'^(?P<mtid>(\d+)) +(?P<topo_cost>(\d+))'
                            r' +(?P<disabled>(yes|no)) +(?P<shutdown>(yes|no))'
                            r' +(?P<topo_name>(\S+))$')

        p7 = re.compile(r'^Transmit +Delay +is +(?P<transmit_delay>(\d+))'
                            r' +sec, +State +(?P<state>(\S+)),?$')

        p8 = re.compile(r'^Timer +intervals +configured,'
                            r' +Hello +(?P<hello>(\d+)),'
                            r' +Dead +(?P<dead>(\d+)),'
                            r' +Wait +(?P<wait>(\d+)),'
                            r'(?: +Retransmit +(?P<retransmit>(\d+)))?$')

        p9 = re.compile(r'^Strict +TTL +checking'
                            r' +(?P<strict_ttl>(enabled|disabled))'
                            r'(?:, +up +to +(?P<hops>(\d+)) +hops +allowed)?$')

        p10 = re.compile(r'^Hello +due +in +(?P<hello_timer>(\S+))$')

        p11 = re.compile(r'^Adjacency +State +(?P<adj_state>(\S+))$')

        p12 = re.compile(r'^Index +(?P<index>(\S+)), +retransmission +queue'
                            r' +length +(?P<length>(\d+)), +number +of'
                            r' +retransmission +(?P<retrans>(\d+))$')

        p13 = re.compile(r'^First +(?P<first>(\S+)) +Next +(?P<next>(\S+))$')

        p14 = re.compile(r'^Last +retransmission +scan +length +is'
                            r' +(?P<len>(\d+)), +maximum +is +(?P<max>(\d+))$')

        p15 = re.compile(r'^Last +retransmission +scan +time +is'
                            r' +(?P<time>(\d+)) +msec, +maximum +is'
                            r' +(?P<max>(\d+)) +msec$')

        for line in out.splitlines():
            line = line.strip()

            # Sham Link OSPF_SL0 to address 10.151.22.22 is up
            # Virtual Link OSPF_VL0 to router 10.64.4.4 is up
            m = p1.match(line)
            if m:
                address = str(m.groupdict()['address'])
                sl_remote_id = vl_router_id = address
                interface = str(m.groupdict()['interface'])
                link_state = str(m.groupdict()['link_state'])
                instance = None
                
                # Get link name
                n = re.match(r'(?P<ignore>\S+)_(?P<name>(S|V)L(\d+))', interface)
                if n:
                    real_link_name = str(n.groupdict()['name'])
                else:
                    real_link_name = interface
                
                # Get OSPF process ID from 'show ip ospf interface'
                cmd = 'show ip ospf interface {}'.format(interface)
                out = self.device.execute(cmd)

                for line in out.splitlines():
                    line = line.rstrip()

                    # Process ID 2, Router ID 10.229.11.11, Network Type SHAM_LINK, Cost: 111
                    p = re.search(r'Process +ID +(?P<instance>(\S+)), +Router'
                                  r' +(.*)', line)
                    if p:
                        instance = str(p.groupdict()['instance'])
                        break

                # Get VRF information using the ospf instance
                if instance is not None:
                    cmd = 'show running-config | section router ospf {}'.format(instance)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()

                        # Skip the show command line so as to not match
                        if re.search('show', line):
                            continue

                        # router ospf 1
                        # router ospf 2 vrf VRF1
                        p = re.search(r'router +ospf +(?P<instance>(\S+))'
                                      r'(?: +vrf +(?P<vrf>(\S+)))?', line)
                        if p:
                            p_instance = str(p.groupdict()['instance'])
                            if p_instance == instance:
                                if p.groupdict()['vrf']:
                                    vrf = str(p.groupdict()['vrf'])
                                    break
                                else:
                                    vrf = 'default'
                                    break

                # Build dict
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}
                continue

            # Area 1, source address 10.21.33.33
            # Area 1 source address 10.229.11.11
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                source_address = str(m.groupdict()['source_address'])

                # Set link_name for sham_link
                link_name = '{} {}'.format(source_address, sl_remote_id)

                # Build dict
                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if link_type not in  ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][link_type] = {}
                if link_name not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area][link_type]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][link_type][link_name] = {}

                # Set sub_dict
                sub_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                            ['instance'][instance]['areas'][area]\
                            [link_type][link_name]

                # Set values
                sub_dict['transit_area_id'] = area
                sub_dict['local_id'] = source_address
                sub_dict['demand_circuit'] = False

                # Set previously parsed values
                try:
                    sub_dict['name'] = real_link_name
                    sub_dict['remote_id'] = sl_remote_id
                    sub_dict['link_state'] = link_state
                except Exception:
                    pass
                continue

            # Run as demand circuit
            m = p3.match(line)
            if m:
                if link_type == 'sham_links':
                    sub_dict['demand_circuit'] = True
                else:
                    demand_circuit = True
                continue

            # DoNotAge LSA not allowed (Number of DCbitless LSA is 7).
            # DoNotAge LSA not allowed (Number of DCbitless LSA is 1). Cost of using 111 State POINT_TO_POINT,
            m = p4.match(line)
            if m:
                dcbitless_lsa_count = int(m.groupdict()['dcbitless'])
                donotage_lsa = 'not allowed'
                if m.groupdict()['cost']:
                    cost = int(m.groupdict()['cost'])
                if m.groupdict()['state']:
                    link_state =  str(m.groupdict()['state']).lower()

                # Set values for sham_links
                if link_type == 'sham_links':
                    sub_dict['dcbitless_lsa_count'] = dcbitless_lsa_count
                    sub_dict['donotage_lsa'] = donotage_lsa
                    if m.groupdict()['cost']:
                        sub_dict['cost'] = cost
                    if m.groupdict()['state']:
                        sub_dict['state'] = link_state
                    continue

            # Transit area 1
            # Transit area 1, via interface GigabitEthernet0/1
            m = p5.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))

                # Set link_name for virtual_link
                link_name = '{} {}'.format(area, vl_router_id)

                # Create dict
                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if link_type not in  ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][link_type] = {}
                if link_name not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area][link_type]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][link_type][link_name] = {}

                # Set sub_dict
                sub_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                            ['instance'][instance]['areas'][area]\
                            [link_type][link_name]

                # Set values
                sub_dict['transit_area_id'] = area
                sub_dict['demand_circuit'] = False
                if m.groupdict()['intf']:
                    sub_dict['interface'] = str(m.groupdict()['intf'])

                # Set previously parsed values
                try:
                    sub_dict['name'] = real_link_name
                except Exception:
                    pass
                try:
                    sub_dict['router_id'] = vl_router_id
                except Exception:
                    pass
                try:
                    sub_dict['dcbitless_lsa_count'] = dcbitless_lsa_count
                except Exception:
                    pass
                try:
                    sub_dict['donotage_lsa'] = donotage_lsa
                except Exception:
                    pass
                try:
                    sub_dict['demand_circuit'] = demand_circuit
                except Exception:
                    pass
                try:
                    sub_dict['link_state'] = link_state
                except Exception:
                    pass
                continue

            # Topology-MTID    Cost    Disabled     Shutdown      Topology Name
            #             0       1          no           no               Base
            m = p6.match(line)
            if m:
                mtid = int(m.groupdict()['mtid'])
                if 'topology' not in sub_dict:
                    sub_dict['topology'] = {}
                if mtid not in sub_dict['topology']:
                    sub_dict['topology'][mtid] = {}
                sub_dict['topology'][mtid]['cost'] = int(m.groupdict()['topo_cost'])
                sub_dict['topology'][mtid]['name'] = str(m.groupdict()['topo_name'])
                if 'yes' in m.groupdict()['disabled']:
                    sub_dict['topology'][mtid]['disabled'] = True
                else:
                    sub_dict['topology'][mtid]['disabled'] = False
                if 'yes' in m.groupdict()['shutdown']:
                    sub_dict['topology'][mtid]['shutdown'] = True
                else:
                    sub_dict['topology'][mtid]['shutdown'] = False
                    continue
            
            # Transmit Delay is 1 sec, State POINT_TO_POINT,
            m = p7.match(line)
            if m:
                sub_dict['transmit_delay'] = int(m.groupdict()['transmit_delay'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace("_", "-")
                sub_dict['state'] = state
                continue

            # Timer intervals configured, Hello 3, Dead 13, Wait 13, Retransmit 5
            # Timer intervals configured, Hello 4, Dead 16, Wait 16, Retransmit 44
            # Timer intervals configured, Hello 10, Dead 40, Wait 40,
            m = p8.match(line)
            if m:
                if m.groupdict()['hello']:
                    sub_dict['hello_interval'] = int(m.groupdict()['hello'])
                if m.groupdict()['dead']:
                    sub_dict['dead_interval'] = int(m.groupdict()['dead'])
                if m.groupdict()['wait']:
                    sub_dict['wait_interval'] = int(m.groupdict()['wait'])
                if m.groupdict()['retransmit']:
                    sub_dict['retransmit_interval'] = int(m.groupdict()['retransmit'])
                continue

            # Strict TTL checking enabled, up to 3 hops allowed
            m = p9.match(line)
            if m:
                if 'ttl_security' not in sub_dict:
                    sub_dict['ttl_security'] = {}
                if 'enabled' in m.groupdict()['strict_ttl']:
                    sub_dict['ttl_security']['enable'] = True
                else:
                    sub_dict['ttl_security']['enable'] = False
                if m.groupdict()['hops']:
                    sub_dict['ttl_security']['hops'] = int(m.groupdict()['hops'])
                    continue

            # Hello due in 00:00:03:179
            m = p10.match(line)
            if m:
                sub_dict['hello_timer'] = str(m.groupdict()['hello_timer'])
                continue          
          
            # Adjacency State FULL
            m = p11.match(line)
            if m:
                sub_dict['adjacency_state'] = str(m.groupdict()['adj_state']).lower()
                continue

            # Index 1/2/2, retransmission queue length 0, number of retransmission 2
            m = p12.match(line)
            if m:
                sub_dict['index'] = str(m.groupdict()['index'])
                sub_dict['retrans_qlen'] = int(m.groupdict()['length'])
                sub_dict['total_retransmission'] = int(m.groupdict()['retrans'])
                continue

            # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
            m = p13.match(line)
            if m:
                sub_dict['first'] = str(m.groupdict()['first'])
                sub_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last retransmission scan length is 1, maximum is 1
            m = p14.match(line)
            if m:
                sub_dict['last_retransmission_scan_length'] = \
                    int(m.groupdict()['len'])
                sub_dict['last_retransmission_max_length'] = \
                    int(m.groupdict()['max'])
                continue

            # Last retransmission scan time is 0 msec, maximum is 0 msec
            m = p15.match(line)
            if m:
                sub_dict['last_retransmission_scan_time'] = \
                    int(m.groupdict()['time'])
                sub_dict['last_retransmission_max_scan'] = \
                    int(m.groupdict()['max'])
                continue

        return ret_dict


# =============================
# Schema for:
#   * 'show ip ospf sham-links'
# =============================
class ShowIpOspfShamLinksSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf sham-links'
    '''

    schema = {
        'vrf':
            {Any():
                {'address_family':
                    {Any():
                        {'instance':
                            {Any():
                                {'areas':
                                    {Any():
                                        {'sham_links':
                                            {Any():
                                                {'name': str,
                                                'link_state': str,
                                                'local_id': str,
                                                'remote_id': str,
                                                'transit_area_id': str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                Optional('transmit_delay'): int,
                                                'cost': int,
                                                'state': str,
                                                Optional('hello_timer'): str,
                                                Optional('demand_circuit'): bool,
                                                Optional('dcbitless_lsa_count'): int,
                                                Optional('donotage_lsa'): str,
                                                Optional('adjacency_state'): str,
                                                Optional('ttl_security'):
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                    Optional('index'): str,
                                                    Optional('first'): str,
                                                    Optional('next'): str,
                                                    Optional('last_retransmission_max_length'): int,
                                                    Optional('last_retransmission_max_scan'): int,
                                                    Optional('last_retransmission_scan_length'): int,
                                                    Optional('last_retransmission_scan_time'): int,
                                                    Optional('total_retransmission'): int,
                                                    Optional('retrans_qlen'): int,
                                                    Optional('topology'):
                                                        {Any():
                                                            {'cost': int,
                                                            'disabled': bool,
                                                            'shutdown': bool,
                                                            'name': str,
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            }


# =============================
# Parser for:
#   * 'show ip ospf sham-links'
# =============================
class ShowIpOspfShamLinks(ShowIpOspfShamLinksSchema, ShowIpOspfLinksParser):

    ''' Parser for:
        * 'show ip ospf sham-links'
    '''

    cli_command = 'show ip ospf sham-links'

    def cli(self, output=None):

        return super().cli(cmd=self.cli_command, link_type='sham_links',output=output)


# ================================
# Schema for:
#   * 'show ip ospf virtual-links'
# ================================
class ShowIpOspfVirtualLinksSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf virtual-links'
    '''

    schema = {
        'vrf':
            {Any():
                {'address_family':
                    {Any():
                        {'instance':
                            {Any():
                                {'areas':
                                    {Any():
                                        {'virtual_links':
                                            {Any():
                                                {'name': str,
                                                'link_state': str,
                                                'router_id': str,
                                                'transit_area_id': str,
                                                Optional('hello_interval'): int,
                                                Optional('dead_interval'): int,
                                                Optional('wait_interval'): int,
                                                Optional('retransmit_interval'): int,
                                                'transmit_delay': int,
                                                'state': str,
                                                'demand_circuit': bool,
                                                Optional('cost'): int,
                                                Optional('hello_timer'): str,
                                                Optional('interface'): str,
                                                Optional('dcbitless_lsa_count'): int,
                                                Optional('donotage_lsa'): str,
                                                Optional('adjacency_state'): str,
                                                Optional('ttl_security'):
                                                    {'enable': bool,
                                                    Optional('hops'): int},
                                                    Optional('index'): str,
                                                    Optional('first'): str,
                                                    Optional('next'): str,
                                                    Optional('last_retransmission_max_length'): int,
                                                    Optional('last_retransmission_max_scan'): int,
                                                    Optional('last_retransmission_scan_length'): int,
                                                    Optional('last_retransmission_scan_time'): int,
                                                    Optional('total_retransmission'): int,
                                                    Optional('retrans_qlen'): int,
                                                    Optional('topology'):
                                                        {Any():
                                                            {'cost': int,
                                                            'disabled': bool,
                                                            'shutdown': bool,
                                                            'name': str,
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            }


# ================================
# Parser for:
#   * 'show ip ospf virtual-links'
# ================================
class ShowIpOspfVirtualLinks(ShowIpOspfVirtualLinksSchema, ShowIpOspfLinksParser):

    ''' Parser for:
        * 'show ip ospf virtual-links'
    '''

    cli_command = 'show ip ospf virtual-links'

    def cli(self, output=None):

        return super().cli(cmd=self.cli_command, link_type='virtual_links', output=output)


# ==================================
# Schema for:
#   * 'show ip ospf neighbor detail'
# =========================================
class ShowIpOspfNeighborDetailSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf neighbor detail'
    '''

    schema = {
        'vrf': 
            {Any():
                {'address_family':
                    {Any():
                        {'instance':
                            {Any():
                                {'areas': 
                                    {Any(): 
                                        {Optional('interfaces'): 
                                            {Any(): 
                                                {'neighbors': 
                                                    {Any(): 
                                                        {'neighbor_router_id': str,
                                                        'address': str,
                                                        'interface': str,
                                                        'priority': int,
                                                        'state': str,
                                                        'dr_ip_addr': str,
                                                        'bdr_ip_addr': str,
                                                        Optional('bfd_state'): str,
                                                        Optional('interface_id'): str,
                                                        Optional('hello_options'): str,
                                                        Optional('sr_adj_label'): str,
                                                        Optional('dbd_options'): str,
                                                        Optional('dead_timer'): str,
                                                        Optional('uptime'): str,
                                                        Optional('index'): str,
                                                        Optional('first'): str,
                                                        Optional('next'): str,
                                                        Optional('ls_ack_list'): str,
                                                        Optional('statistics'): 
                                                            {Optional('nbr_event_count'): int,
                                                            Optional('nbr_retrans_qlen'): int,
                                                            Optional('total_retransmission'): int,
                                                            Optional('last_retrans_scan_length'): int,
                                                            Optional('last_retrans_max_scan_length'): int,
                                                            Optional('last_retrans_scan_time_msec'): int,
                                                            Optional('last_retrans_max_scan_time_msec'): int},
                                                        },
                                                    },
                                                },
                                            },
                                        Optional('sham_links'): 
                                            {Any(): 
                                                {'neighbors': 
                                                    {Any(): 
                                                        {'neighbor_router_id': str,
                                                        'address': str,
                                                        'interface': str,
                                                        'priority': int,
                                                        'state': str,
                                                        'dr_ip_addr': str,
                                                        'bdr_ip_addr': str,
                                                        Optional('interface_id'): str,
                                                        Optional('hello_options'): str,
                                                        Optional('dbd_options'): str,
                                                        Optional('dead_timer'): str,
                                                        Optional('uptime'): str,
                                                        Optional('index'): str,
                                                        Optional('first'): str,
                                                        Optional('next'): str,
                                                        Optional('ls_ack_list'): str,
                                                        Optional('statistics'): 
                                                            {Optional('nbr_event_count'): int,
                                                            Optional('nbr_retrans_qlen'): int,
                                                            Optional('total_retransmission'): int,
                                                            Optional('last_retrans_scan_length'): int,
                                                            Optional('last_retrans_max_scan_length'): int,
                                                            Optional('last_retrans_scan_time_msec'): int,
                                                            Optional('last_retrans_max_scan_time_msec'): int},
                                                        },
                                                    },
                                                },
                                            },
                                        Optional('virtual_links'): 
                                            {Any(): 
                                                {'neighbors': 
                                                    {Any(): 
                                                        {'neighbor_router_id': str,
                                                        'address': str,
                                                        'interface': str,
                                                        'priority': int,
                                                        'state': str,
                                                        'dr_ip_addr': str,
                                                        'bdr_ip_addr': str,
                                                        Optional('interface_id'): str,
                                                        Optional('hello_options'): str,
                                                        Optional('dbd_options'): str,
                                                        Optional('dead_timer'): str,
                                                        Optional('uptime'): str,
                                                        Optional('index'): str,
                                                        Optional('first'): str,
                                                        Optional('next'): str,
                                                        Optional('ls_ack_list'): str,
                                                        Optional('statistics'): 
                                                            {Optional('nbr_event_count'): int,
                                                            Optional('nbr_retrans_qlen'): int,
                                                            Optional('total_retransmission'): int,
                                                            Optional('last_retrans_scan_length'): int,
                                                            Optional('last_retrans_max_scan_length'): int,
                                                            Optional('last_retrans_scan_time_msec'): int,
                                                            Optional('last_retrans_max_scan_time_msec'): int},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# ================================
# Parser for:
#   'show ip ospf neighbor detail'
# ================================
class ShowIpOspfNeighborDetail(ShowIpOspfNeighborDetailSchema):

    ''' Parser for:
        * 'show ip ospf neighbor detail'
    '''

    cli_command = ['show ip ospf neighbor detail', 'show ip ospf neighbor {neighbor} detail']
    exclude = ['hello_timer', 'dead_timer', 'bdr_ip_addr',
        'bdr_router_id', 'index', 'last_retrans_max_scan_length',
        'last_retrans_max_scan_time_msec', 'total_retransmission',
        'uptime', 'last_retrans_scan_length', 'last_retrans_scan_time_msec']


    def cli(self, neighbor='', output=None):

        if output is None:
            # Execute command on device
            if neighbor:
                out = self.device.execute(self.cli_command[1].format(neighbor=neighbor))
            else:
                out = self.device.execute(self.cli_command[0])
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'^Neighbor +(?P<neighbor>(\S+)), +interface'
                           r' +address +(?P<address>(\S+))'
                            r'(?:, +interface-id +(?P<intf_id>(\S+)))?$')
        
        p2 = re.compile(r'^In +the +area +(?P<area>(\S+)) +via +interface'
                            r' +(?P<interface>(\S+))(, +BFD +(?P<bfd_state>\S+))?$')
        
        p3 = re.compile(r'^Neighbor +priority +is +(?P<priority>(\d+)),'
                           r' +State +is +(?P<state>(\S+)),'
                            r' +(?P<num>(\d+)) +state +changes$')
        
        p4 = re.compile(r'^DR +is +(?P<dr_ip_addr>(\S+))'
                            r' +BDR +is +(?P<bdr_ip_addr>(\S+))$')
        
        p5 = re.compile(r'^Options +is +(?P<options>(\S+)) +in +Hello'
                            r' +\(E-bit\)$')
        
        p6 = re.compile(r'^Options +is +(?P<options>(\S+)) +in +DBD'
                            r' +\(E-bit, O-bit\)$')
        
        p7 = re.compile(r'^Dead +timer +due +in +(?P<dead_timer>(\S+))$')
        
        p8 = re.compile(r'^Neighbor +is +up +for +(?P<uptime>(\S+))$')
        
        p9 = re.compile(r'^Index +(?P<index>(\S+)) +retransmission +queue'
                            r' +length +(?P<ql>(\d+)), +number +of'
                            r' +retransmission +(?P<num_retrans>(\d+))$')
        
        p10 = re.compile(r'^First +(?P<first>(\S+)) +Next +(?P<next>(\S+))$')
        
        p11 = re.compile(r'^Last +retransmission +scan +length +is'
                            r' +(?P<num1>(\d+)), +maximum +is'
                            r' +(?P<num2>(\d+))$')
        
        p12 = re.compile(r'^Last +retransmission +scan +time +is'
                            r' +(?P<num1>(\d+)) +msec, +maximum +is'
                            r' +(?P<num2>(\d+)) +msec$')
        
        p13 = re.compile(r'^SR +adj +label +(?P<sr_adj_label>\d+)$')
        
        for line in out.splitlines():
            line = line.strip()

            # Neighbor 10.16.2.2, interface address 10.1.2.2
            # Neighbor 192.168.111.1, interface address 192.168.70.1, interface-id 192
            # Neighbor 192.168.255.9, interface address 10.0.109.9, interface-id unknown
            m = p1.match(line)
            if m:
                neighbor = str(m.groupdict()['neighbor'])
                address = str(m.groupdict()['address'])
                if m.groupdict()['intf_id']:
                    interface_id = str(m.groupdict()['intf_id'])
                continue

            # In the area 0 via interface GigabitEthernet2
            # In the area 0 via interface TenGigabitEthernet3/1/1, BFD enabled
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                interface = str(m.groupdict()['interface'])
                instance = None
                router_id = None
                bfd_state = m.groupdict().get('bfd_state', None)
                # Get OSPF process ID from 'show ip ospf interface'
                cmd = 'show ip ospf interface {}'.format(interface)
                out = self.device.execute(cmd)

                for line in out.splitlines():
                    line = line.rstrip()

                    # Process ID 2, Router ID 10.229.11.11, Network Type SHAM_LINK, Cost: 111
                    p = re.search(r'Process +ID +(?P<instance>(\S+)), +Router +ID'
                                  r' +(?P<router_id>(\S+)) +(.*)', line)
                    if p:
                        instance = str(p.groupdict()['instance'])
                        router_id = str(p.groupdict()['router_id'])
                        break

                # Get VRF information using the ospf instance
                if instance is not None:
                    cmd = 'show running-config | section router ospf {}'.format(instance)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()

                        # Skip the show command line so as to not match
                        if re.search('show', line):
                            continue

                        # router ospf 1
                        # router ospf 2 vrf VRF1
                        p = re.search(r'router +ospf +(?P<instance>(\S+))'
                                      r'(?: +vrf +(?P<vrf>(\S+)))?', line)
                        if p:
                            p_instance = str(p.groupdict()['instance'])
                            if p_instance == instance:
                                if p.groupdict()['vrf']:
                                    vrf = str(p.groupdict()['vrf'])
                                    break
                                else:
                                    vrf = 'default'
                                    break

                # Build dict
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}

                # Determine if 'interface' or 'virtual_links' or 'sham_links'
                if re.search('VL', interface):
                    # Init
                    intf_type = 'virtual_links'
                    vl_addr = None
                    vl_transit_area_id = None

                    # Execute command to get virtual-link address
                    cmd = 'show ip ospf virtual-links | i {interface}'.format(interface=interface)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()
                        # Virtual Link OSPF_VL0 to router 10.100.5.5 is down
                        p = re.search(r'Virtual +Link +(?P<intf>(\S+)) +to +router'
                                     r' +(?P<address>(\S+)) +is +(up|down)'
                                     r'(?:.*)?', line)
                        if p:
                            if interface == str(p.groupdict()['intf']):
                                vl_addr = str(p.groupdict()['address'])
                                break

                    # Execute command to get virtual-link transit_area_id
                    if vl_addr is not None and router_id is not None:
                        cmd = 'show running-config | i virtual-link | i {addr}'.format(addr=vl_addr)
                        out = self.device.execute(cmd)

                        for line in out.splitlines():
                            line = line.rstrip()
                            #  area 1 virtual-link 10.100.5.5
                            q = re.search(r'area +(?P<q_area>(\d+)) +virtual-link'
                                          r' +(?P<addr>(\S+))(?: +(.*))?', line)
                            if q:
                                q_addr = str(q.groupdict()['addr'])
                                # Check parameters match
                                if q_addr == vl_addr:
                                    vl_transit_area_id = str(IPAddress(str(q.groupdict()['q_area']), flags=INET_ATON))
                                    break

                    if vl_transit_area_id is not None:
                        intf_name = '{} {}'.format(vl_transit_area_id, router_id)
                        area = vl_transit_area_id
                elif re.search('SL', interface):
                    # Init
                    intf_type = 'sham_links'
                    sl_local_id = None
                    sl_remote_id = None

                    # Execute command to get sham-link remote_id
                    cmd = 'show ip ospf sham-links | i {interface}'.format(interface=interface)
                    out = self.device.execute(cmd)

                    for line in out.splitlines():
                        line = line.rstrip()
                        # Sham Link OSPF_SL1 to address 10.151.22.22 is up
                        p = re.search(r'Sham +Link +(?P<intf>(\S+)) +to +address'
                                     r' +(?P<remote>(\S+)) +is +(up|down)', line)
                        if p:
                            if interface == str(p.groupdict()['intf']):
                                sl_remote_id = str(p.groupdict()['remote'])
                                break

                    # Execute command to get sham-link local_id
                    if sl_remote_id is not None:
                        cmd = 'show running-config | i sham-link | i {remote}'.format(remote=sl_remote_id)
                        out = self.device.execute(cmd)

                        for line in out.splitlines():
                            line = line.rstrip()
                            # area 1 sham-link 10.229.11.11 10.151.22.22 cost 111 ttl-security hops 3
                            q = re.search(r'area +(?P<q_area>(\d+)) +sham-link'
                                          r' +(?P<local_id>(\S+))'
                                          r' +(?P<remote_id>(\S+)) +(.*)', line)
                            if q:
                                q_area = str(IPAddress(str(q.groupdict()['q_area']), flags=INET_ATON))
                                q_remote_id = str(q.groupdict()['remote_id'])

                                # Check parameters match
                                if q_area == area and q_remote_id == sl_remote_id:
                                    sl_local_id = str(q.groupdict()['local_id'])
                                    break

                    # Set intf_name based on parsed values
                    if sl_local_id is not None:
                        intf_name = '{} {}'.format(sl_local_id, sl_remote_id)
                else:
                    # Set values for dict
                    intf_type = 'interfaces'
                    intf_name = interface

                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if intf_type not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type] = {}
                if intf_name not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area][intf_type]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type][intf_name] = {}
                if 'neighbors' not in ret_dict['vrf'][vrf]['address_family']\
                        [af]['instance'][instance]['areas'][area][intf_type]\
                        [intf_name]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type][intf_name]\
                        ['neighbors'] = {}
                if neighbor not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area][intf_type]\
                        [intf_name]['neighbors']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area][intf_type][intf_name]\
                        ['neighbors'][neighbor] = {}
                
                # Set sub_dict
                sub_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                            ['instance'][instance]['areas'][area][intf_type]\
                            [intf_name]['neighbors'][neighbor]

                # Set values
                sub_dict['neighbor_router_id'] = neighbor
                sub_dict['interface'] = interface
                try:
                    sub_dict['address'] = address
                    del address
                except Exception:
                    pass
                try:
                    sub_dict['interface_id'] = interface_id
                    del interface_id
                except Exception:
                    pass
                if bfd_state:
                    sub_dict['bfd_state'] = bfd_state
                continue

            # Neighbor priority is 1, State is FULL, 6 state changes
            m = p3.match(line)
            if m:
                sub_dict['priority'] = int(m.groupdict()['priority'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace('_', '-')
                sub_dict['state'] = state
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['nbr_event_count'] = \
                    int(m.groupdict()['num'])
                continue

            # DR is 10.2.3.3 BDR is 10.2.3.2
            m = p4.match(line)
            if m:
                sub_dict['dr_ip_addr'] = str(m.groupdict()['dr_ip_addr'])
                sub_dict['bdr_ip_addr'] = str(m.groupdict()['bdr_ip_addr'])
                continue

            # Options is 0x2 in Hello (E-bit)
            m = p5.match(line)
            if m:
                sub_dict['hello_options'] = str(m.groupdict()['options'])
                continue

            # Options is 0x42 in DBD (E-bit, O-bit)
            # Options is 0x42 in DBD (E-bit, O-bit)
            m = p6.match(line)
            if m:
                sub_dict['dbd_options'] = str(m.groupdict()['options'])
                continue

            # Dead timer due in 00:00:38
            m = p7.match(line)
            if m:
                sub_dict['dead_timer'] = str(m.groupdict()['dead_timer'])
                continue

            # Neighbor is up for 08:22:07
            m = p8.match(line)
            if m:
                sub_dict['uptime'] = str(m.groupdict()['uptime'])
                continue

            # Index 1/2/2, retransmission queue length 0, number of retransmission 0
            m = p9.match(line)
            if m:
                sub_dict['index'] = str(m.groupdict()['index'])
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['nbr_retrans_qlen'] = \
                    int(m.groupdict()['ql'])
                sub_dict['statistics']['total_retransmission'] = \
                    int(m.groupdict()['num_retrans'])
                continue

            # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
            m = p10.match(line)
            if m:
                sub_dict['first'] = str(m.groupdict()['first'])
                sub_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last retransmission scan length is 0, maximum is 0
            m = p11.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['last_retrans_scan_length'] = \
                    int(m.groupdict()['num1'])
                sub_dict['statistics']['last_retrans_max_scan_length'] = \
                    int(m.groupdict()['num2'])
                continue

            # Last retransmission scan time is 0 msec, maximum is 0 msec
            m = p12.match(line)
            if m:
                if 'statistics' not in sub_dict:
                    sub_dict['statistics'] = {}
                sub_dict['statistics']['last_retrans_scan_time_msec'] = \
                    int(m.groupdict()['num1'])
                sub_dict['statistics']['last_retrans_max_scan_time_msec'] = \
                    int(m.groupdict()['num2'])
                continue
            
            # SR adj label 10
            m = p13.match(line)
            if m:
                sub_dict['sr_adj_label'] = str(m.groupdict()['sr_adj_label'])
                continue
            
        return ret_dict


# ==================================
# Schema for:
#   * 'show ip ospf neighbor detail'
# =========================================
class ShowIpOspfNeighborDetail2Schema(MetaParser):

    ''' Schema for:
        * 'show ip ospf neighbor detail'
    '''

    schema = {
                'address-family':{
                    'ipv4':{
                        'areas':{
                            Any():{
                                Any():{
                                    Any():{
                                        'neighbors': {
                                            Any(): {
                                                'neighbor_router_id': str,
                                                'address': str,
                                                'interface': str,
                                                'priority': int,
                                                'state': str,
                                                'dr_ip_addr': str,
                                                'bdr_ip_addr': str,
                                                Optional('bfd_state'): str,
                                                Optional('interface_id'): str,
                                                Optional('hello_options'): str,
                                                Optional('sr_adj_label'): str,
                                                Optional('dbd_options'): str,
                                                Optional('dead_timer'): str,
                                                Optional('uptime'): str,
                                                Optional('index'): str,
                                                Optional('first'): str,
                                                Optional('next'): str,
                                                Optional('ls_ack_list'): str,
                                                Optional('statistics'): {
                                                    Optional('nbr_event_count'): int,
                                                    Optional('nbr_retrans_qlen'): int,
                                                    Optional('total_retransmission'): int,
                                                    Optional('last_retrans_scan_length'): int,
                                                    Optional('last_retrans_max_scan_length'): int,
                                                    Optional('last_retrans_scan_time_msec'): int,
                                                    Optional('last_retrans_max_scan_time_msec'): int
                                                },
                                            },
                                        },
                                    },
                                },
                            }, 
                        }
                    }
                }
            }

# ================================
# Parser for:
#   'show ip ospf neighbor detail'
# ================================
class ShowIpOspfNeighborDetail2(ShowIpOspfNeighborDetail2Schema):

    ''' Parser for:
        * 'show ip ospf neighbor detail__'
    '''

    cli_command = 'show ip ospf neighbor detail__'

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'^Neighbor +(?P<neighbor>(\S+)), +interface'
                            r' +address +(?P<address>(\S+))'
                            r'(?:, +interface-id +(?P<intf_id>(\S+)))?$')
        
        p2 = re.compile(r'^In +the +area +(?P<area>(\S+)) +via +interface'
                            r' +(?P<interface>(\S+))(, +BFD +(?P<bfd_state>\S+))?$')
        
        p3 = re.compile(r'^Neighbor +priority +is +(?P<priority>(\d+)),'
                            r' +State +is +(?P<state>(\S+)),'
                            r' +(?P<num>(\d+)) +state +changes$')
        
        p4 = re.compile(r'^DR +is +(?P<dr_ip_addr>(\S+))'
                            r' +BDR +is +(?P<bdr_ip_addr>(\S+))$')
        
        p5 = re.compile(r'^Options +is +(?P<options>(\S+)) +in +Hello'
                            r' +\(E-bit\)$')
        
        p6 = re.compile(r'^Options +is +(?P<options>(\S+)) +in +DBD'
                            r' +\(E-bit, O-bit\)$')
        
        p7 = re.compile(r'^Dead +timer +due +in +(?P<dead_timer>(\S+))$')
        
        p8 = re.compile(r'^Neighbor +is +up +for +(?P<uptime>(\S+))$')
        
        p9 = re.compile(r'^Index +(?P<index>(\S+)) +retransmission +queue'
                            r' +length +(?P<ql>(\d+)), +number +of'
                            r' +retransmission +(?P<num_retrans>(\d+))$')
        
        p10 = re.compile(r'^First +(?P<first>(\S+)) +Next +(?P<next>(\S+))$')
        
        p11 = re.compile(r'^Last +retransmission +scan +length +is'
                            r' +(?P<num1>(\d+)), +maximum +is'
                            r' +(?P<num2>(\d+))$')
        
        p12 = re.compile(r'^Last +retransmission +scan +time +is'
                            r' +(?P<num1>(\d+)) +msec, +maximum +is'
                            r' +(?P<num2>(\d+)) +msec$')
        
        p13 = re.compile(r'^SR +adj +label +(?P<sr_adj_label>\d+)$')
        
        
        for line in out.splitlines():
            line = line.strip()

            # Neighbor 10.16.2.2, interface address 10.1.2.2
            # Neighbor 192.168.111.1, interface address 192.168.70.1, interface-id 192
            # Neighbor 192.168.255.9, interface address 10.0.109.9, interface-id unknown
            m = p1.match(line)
            if m:
                neighbor = str(m.groupdict()['neighbor'])
                address = str(m.groupdict()['address'])
                interface_id = m.groupdict().get('intf_id', None)
                continue

            # In the area 0 via interface GigabitEthernet2
            # In the area 0 via interface TenGigabitEthernet3/1/1, BFD enabled
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                interface = str(m.groupdict()['interface'])
                bfd_state = m.groupdict().get('bfd_state', None)

                # Determine if 'interface' or 'virtual_links' or 'sham_links'
                if re.search('VL', interface):
                    # Init
                    intf_type = 'virtual_links'
                elif re.search('SL', interface):
                    # Init
                    intf_type = 'sham_links'
                else:
                    # Set values for dict
                    intf_type = 'interfaces'
                intf_name = interface

                neighbor_dict = ret_dict.setdefault('address-family', {}).setdefault(af, {}).\
                                         setdefault('areas', {}).setdefault(area, {}).\
                                         setdefault(intf_type, {}).setdefault(intf_name, {}).\
                                         setdefault('neighbors', {}).setdefault(neighbor, {})

                # Set values
                neighbor_dict.update({'neighbor_router_id': neighbor,
                                      'interface': interface,
                                      'address': address})
                if interface_id:
                    neighbor_dict.update({'interface_id': interface_id})
                if bfd_state:
                    neighbor_dict.update({'bfd_state': bfd_state})

                continue

            # Neighbor priority is 1, State is FULL
            m = p3.match(line)
            if m:
                neighbor_dict['priority'] = int(m.groupdict()['priority'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace('_', '-')
                neighbor_dict['state'] = state
                if 'num' in m.groupdict():
                    statistics_dict = neighbor_dict.setdefault('statistics', {})
                    statistics_dict.update({'nbr_event_count': int(m.groupdict()['num'])})
                continue

            # DR is 10.2.3.3 BDR is 10.2.3.2
            m = p4.match(line)
            if m:
                neighbor_dict['dr_ip_addr'] = str(m.groupdict()['dr_ip_addr'])
                neighbor_dict['bdr_ip_addr'] = str(m.groupdict()['bdr_ip_addr'])
                continue

            # Options is 0x2 in Hello (E-bit)
            m = p5.match(line)
            if m:
                neighbor_dict['hello_options'] = str(m.groupdict()['options'])
                continue

            # Options is 0x42 in DBD (E-bit, O-bit)
            # Options is 0x42 in DBD (E-bit, O-bit)
            m = p6.match(line)
            if m:
                neighbor_dict['dbd_options'] = str(m.groupdict()['options'])
                continue

            # Dead timer due in 00:00:38
            m = p7.match(line)
            if m:
                neighbor_dict['dead_timer'] = str(m.groupdict()['dead_timer'])
                continue

            # Neighbor is up for 08:22:07
            m = p8.match(line)
            if m:
                neighbor_dict['uptime'] = str(m.groupdict()['uptime'])
                continue

            # Index 1/2/2, retransmission queue length 0, number of retransmission 0
            m = p9.match(line)
            if m:
                neighbor_dict['index'] = str(m.groupdict()['index'])
                statistics_dict = neighbor_dict.setdefault('statistics', {})
                statistics_dict['nbr_retrans_qlen'] = \
                    int(m.groupdict()['ql'])
                statistics_dict['total_retransmission'] = \
                    int(m.groupdict()['num_retrans'])
                continue

            # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
            m = p10.match(line)
            if m:
                neighbor_dict['first'] = str(m.groupdict()['first'])
                neighbor_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last retransmission scan length is 0, maximum is 0
            m = p11.match(line)
            if m:
                statistics_dict = neighbor_dict.setdefault('statistics', {})
                statistics_dict['last_retrans_scan_length'] = \
                    int(m.groupdict()['num1'])
                statistics_dict['last_retrans_max_scan_length'] = \
                    int(m.groupdict()['num2'])
                continue

            # Last retransmission scan time is 0 msec, maximum is 0 msec
            m = p12.match(line)
            if m:
                statistics_dict = neighbor_dict.setdefault('statistics', {})
                statistics_dict['last_retrans_scan_time_msec'] = \
                    int(m.groupdict()['num1'])
                statistics_dict['last_retrans_max_scan_time_msec'] = \
                    int(m.groupdict()['num2'])
                continue

            # SR adj label 10
            m = p13.match(line)
            if m:
                neighbor_dict['sr_adj_label'] = str(m.groupdict()['sr_adj_label'])
                continue

        return ret_dict


# =====================================
# Schema for:
#   * 'show ip ospf mpls ldp interface'
# =====================================
class ShowIpOspfMplsLdpInterfaceSchema(MetaParser):

    ''' Schema for:
        * "show ip ospf mpls ldp interface" 
    '''

    schema = {
        'vrf': 
            {Any(): 
                {'address_family': 
                    {Any(): 
                        {'instance': 
                            {Any(): 
                                {'mpls': 
                                    {'ldp': 
                                        {'autoconfig': bool,
                                        'autoconfig_area_id': str,
                                        },
                                    },
                                'areas': 
                                    {Any(): 
                                        {'interfaces': 
                                            {Any(): 
                                                {'mpls': 
                                                    {'ldp': 
                                                        {'autoconfig': bool,
                                                        'autoconfig_area_id': str,
                                                        'igp_sync': bool,
                                                        'holddown_timer': bool,
                                                        'state': str,
                                                         Optional('state_info') :str
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# =====================================
# Parser for:
#   * 'show ip ospf mpls ldp interface'
# =====================================
class ShowIpOspfMplsLdpInterface(ShowIpOspfMplsLdpInterfaceSchema):

    ''' Parser for:
        * 'show ip ospf mpls ldp interface'
    '''

    cli_command = ['show ip ospf mpls ldp interface', 'show ip ospf mpls ldp interface {interface}']

    def cli(self, interface='', output=None):

        if output is None:
            # Execute command on device
            if interface:
                out = self.device.execute(self.cli_command[1].format(interface=interface))
            else:
                out = self.device.execute(self.cli_command[0])
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'^(?P<interface>(Lo.*|.*Gig.*|.*(SL|VL).*|'
                            r'Cellular.*|FastEthernet.*|LISP.*|Po.*|Tunnel.*|'
                            r'VirtualPortGroup.*|Vlan.*))$')

        p2 = re.compile(r'^Process +ID +(?P<instance>(\S+)),'
                            r'(?: +VRF +(?P<vrf>(\S+)),)?'
                            r' +Area +(?P<area>(\S+))$')

        p3 = re.compile(r'^LDP +is'
                            r' +(?P<auto_config>(not configured|configured))'
                            r' +through +LDP +autoconfig$')

        p5 = re.compile(r'^Holddown +timer +is (?P<val>([a-zA-Z\s]+))$')
        # Interface is down and pending LDP
        p6 = re.compile(r'^Interface +is (?P<state>(up|down))( +and +(?P<state_info>[\w\s]*))?$')


        for line in out.splitlines():
            line = line.strip()

            # Loopback0
            # GigabitEthernet2
            # TenGigabitEthernet3/0/1
            # TwoGigabitEthernet
            # FiveGigabitEthernet
            # TwentyFiveGigE
            # FortyGigabitEthernet
            # HundredGigE
            # OSPF_SL1
            # OSPF_VL1
            # --extra--
            # Cellular
            # FastEthernet
            # LISP
            # Port-channel
            # Tunnel
            # VirtualPortGroup
            # Vlan
            m = p1.match(line)
            if m:
                interface = str(m.groupdict()['interface'])
                continue

            # Process ID 1, Area 0
            # Process ID 100, Area 0.0.0.0
            # Process ID 2, VRF VRF1, Area 1
            m = p2.match(line)
            if m:
                instance = str(m.groupdict()['instance'])
                try:
                    int(m.groupdict()['area'])
                    area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                except:
                    area = m.groupdict()['area']
                if m.groupdict()['vrf']:
                    vrf = str(m.groupdict()['vrf'])
                else:
                    vrf = 'default'

                # Create dict
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}
                # Create mpls dict
                if 'mpls' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['mpls'] = {}
                if 'ldp' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['mpls']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['mpls']['ldp'] = {}
                mpls_ldp_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['mpls']['ldp']
                # Set values to mpls_ldp_dict
                mpls_ldp_dict['autoconfig_area_id'] = area
                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if 'interfaces' not in ret_dict['vrf'][vrf]['address_family']\
                        [af]['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['interfaces'] = {}
                if interface not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]['interfaces']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['interfaces'][interface] = {}
                if 'mpls' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]['interfaces']\
                        [interface]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['interfaces'][interface]\
                        ['mpls'] = {}
                if 'ldp' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]['interfaces']\
                        [interface]['mpls']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['interfaces'][interface]\
                        ['mpls']['ldp'] = {}
                # Creat intf_dict
                intf_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                                ['instance'][instance]['areas'][area]\
                                ['interfaces'][interface]['mpls']['ldp']
                # Set values to intf_dict
                intf_dict['autoconfig_area_id'] = area
                continue

            # LDP is not configured through LDP autoconfig
            # LDP is configured through LDP autoconfig
            m = p3.match(line)
            if m:
                if m.groupdict()['auto_config'] == 'configured':
                    intf_dict['autoconfig'] = True
                    mpls_ldp_dict['autoconfig'] = True
                else:
                    intf_dict['autoconfig'] = False
                    mpls_ldp_dict['autoconfig'] = False
                    continue
            
            # LDP-IGP Synchronization : Not required
            # LDP-IGP Synchronization : Required
            p4 = re.compile(r'^LDP-IGP +Synchronization *:'
                              r' +(?P<igp_sync>(Not required|Required))$')
            m = p4.match(line)
            if m:
                if m.groupdict()['igp_sync'] == 'Required':
                    intf_dict['igp_sync'] = True
                else:
                    intf_dict['igp_sync'] = False
                    continue

            # Holddown timer is disabled
            m = p5.match(line)
            if m:
                if 'enabled' in m.groupdict()['val']:
                    intf_dict['holddown_timer'] = True
                else:
                    intf_dict['holddown_timer'] = False
                    continue

            # Interface is up 
            m = p6.match(line)
            if m:
                state_info = m.groupdict()['state_info']
                intf_dict['state'] = str(m.groupdict()['state'])
                if state_info:
                    intf_dict['state_info'] = str(state_info)
                continue

        return ret_dict


# ========================================
# Schema for:
#   * 'show ip ospf mpls traffic-eng link'
# ========================================
class ShowIpOspfMplsTrafficEngLinkSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf mpls traffic-eng link'
    '''

    schema = {
        'vrf': 
            {Any(): 
                {'address_family': 
                    {Any(): 
                        {'instance': 
                            {Any(): 
                                {'mpls': 
                                    {'te': 
                                        {'router_id': str},
                                    },
                                'areas': 
                                    {Any(): 
                                        {'mpls': 
                                            {'te': 
                                                {'enable': bool,
                                                Optional('total_links'): int,
                                                Optional('area_instance'): int,
                                                Optional('link_hash_bucket'):
                                                    {Any(): 
                                                        {'link_fragments': 
                                                            {Any(): 
                                                                {'link_instance': int,
                                                                'network_type': str,
                                                                'link_id': str,
                                                                'interface_address': str,
                                                                'te_admin_metric': int,
                                                                'igp_admin_metric': int,
                                                                'max_bandwidth': int,
                                                                'max_reservable_bandwidth': int,
                                                                'affinity_bit': str,
                                                                'total_priority': int,
                                                                Optional('unreserved_bandwidths'): 
                                                                    {Any(): 
                                                                        {'priority': int,
                                                                        'unreserved_bandwidth': int,
                                                                        },
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# ========================================
# Parser for:
#   * 'show ip ospf mpls traffic-eng link'
# ========================================
class ShowIpOspfMplsTrafficEngLink(ShowIpOspfMplsTrafficEngLinkSchema):

    ''' Parser for:
        * 'show ip ospf mpls traffic-eng link'
    '''

    cli_command = 'show ip ospf mpls traffic-eng link'

    def cli(self, output=None):

        if output is None:
            # Execute command on device
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\)'
                            r' +\(Process +ID +(?P<instance>(\S+))\)$')

        p2 = re.compile(r'^Area +(?P<area>(\d+)) +has +(?P<links>(\d+))'
                            r' +MPLS +TE +links. +Area +instance +is'
                            r' +(?P<area_instance>(\d+))\.$')

        p3 = re.compile(r'^Area +(?P<area>(\S+)) +MPLS +TE +not +initialized$')

        p4 = re.compile(r'^Links +in +hash +bucket +(?P<hash>(\d+))\.$')

        p5 = re.compile(r'^Link +is +associated +with +fragment'
                            r' +(?P<fragment>(\d+))\. +Link +instance +is'
                            r' +(?P<link_instance>(\d+))$')

        p6 = re.compile(r'^Link +connected +to +(?P<type>([a-zA-Z\s]+))$')

        p7 = re.compile(r'^Link +ID *: +(?P<link_id>(\S+))$')

        p8 = re.compile(r'^Interface +Address *: +(?P<addr>(\S+))$')

        p9 = re.compile(r'^Admin +Metric +te: +(?P<te>(\d+)) +igp:'
                            r' +(?P<igp>(\d+))$')

        p14 = re.compile(r'^Maximum +(B|b)andwidth *: +(?P<mband>(\d+))$')

        p10 = re.compile(r'^Maximum +(R|r)eservable +(B|b)andwidth *:'
                            r' +(?P<res_band>(\d+))$')

        p11 = re.compile(r'^Affinity +Bit *: +(?P<admin_group>(\S+))$')

        p12 = re.compile(r'^Number +of +Priority +: +(?P<priority>(\d+))$')

        p13 = re.compile(r'^Priority +(?P<num1>(\d+)) *:'
                            r' +(?P<band1>(\d+))(?: +Priority +(?P<num2>(\d+))'
                            r' *: +(?P<band2>(\d+)))?$')


        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 1)
            m = p1.match(line)
            if m:
                router_id = str(m.groupdict()['router_id'])
                instance = str(m.groupdict()['instance'])
                # Get VRF information using the ospf instance
                cmd = 'show running-config | section router ospf {}'.format(instance)
                out = self.device.execute(cmd)

                for line in out.splitlines():
                    line = line.rstrip()

                    # Skip the show command line so as to not match
                    if re.search('show', line):
                        continue

                    # router ospf 1
                    # router ospf 2 vrf VRF1
                    p = re.search(r'router +ospf +(?P<instance>(\S+))'
                                  r'(?: +vrf +(?P<vrf>(\S+)))?', line)
                    if p:
                        p_instance = str(p.groupdict()['instance'])
                        if p_instance == instance:
                            if p.groupdict()['vrf']:
                                vrf = str(p.groupdict()['vrf'])
                                break
                            else:
                                vrf = 'default'
                                break
                # Create dict
                if 'vrf' not in ret_dict:
                    ret_dict['vrf'] = {}
                if vrf not in ret_dict['vrf']:
                    ret_dict['vrf'][vrf] = {}
                if 'address_family' not in ret_dict['vrf'][vrf]:
                    ret_dict['vrf'][vrf]['address_family'] = {}
                if af not in ret_dict['vrf'][vrf]['address_family']:
                    ret_dict['vrf'][vrf]['address_family'][af] = {}
                if 'instance' not in ret_dict['vrf'][vrf]['address_family'][af]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance'] = {}
                if instance not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance] = {}
                if 'mpls' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['mpls'] = {}
                if 'te' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['mpls']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['mpls']['te'] = {}
                ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['mpls']['te']['router_id'] = router_id
                continue

            # Area 0 has 2 MPLS TE links. Area instance is 2.
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                total_links = int(m.groupdict()['links'])
                area_instance = int(m.groupdict()['area_instance'])
                # Create dict
                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if 'mpls' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls'] = {}
                if 'te' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]['mpls']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls']['te'] = {}
                # Set values
                ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                    [instance]['areas'][area]['mpls']['te']['enable'] = True
                ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                    [instance]['areas'][area]['mpls']['te']['total_links'] = \
                        total_links
                ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                    [instance]['areas'][area]['mpls']['te']['area_instance'] = \
                        area_instance
                continue

            # Area 1 MPLS TE not initialized
            # Area 0.0.0.0 MPLS TE not initialized
            m = p3.match(line)
            if m:
                try:
                    int(m.groupdict()['area'])
                    area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                except:
                    area = m.groupdict()['area']
                # Create dict
                if 'areas' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'] = {}
                if area not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area] = {}
                if 'mpls' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls'] = {}
                if 'te' not in ret_dict['vrf'][vrf]['address_family'][af]\
                        ['instance'][instance]['areas'][area]['mpls']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls']['te'] = {}
                # Set values
                ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                    [instance]['areas'][area]['mpls']['te']['enable'] = False
                continue

            # Links in hash bucket 8.
            m = p4.match(line)
            if m:
                link_hash_bucket = int(m.groupdict()['hash'])
                if 'link_hash_bucket' not in ret_dict['vrf'][vrf]\
                        ['address_family'][af]['instance'][instance]['areas']\
                        [area]['mpls']['te']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls']['te']\
                        ['link_hash_bucket'] = {}
                if link_hash_bucket not in ret_dict['vrf'][vrf]\
                        ['address_family'][af]['instance'][instance]['areas']\
                        [area]['mpls']['te']['link_hash_bucket']:
                    ret_dict['vrf'][vrf]['address_family'][af]['instance']\
                        [instance]['areas'][area]['mpls']['te']\
                        ['link_hash_bucket'][link_hash_bucket] = {}
                link_dict = ret_dict['vrf'][vrf]['address_family'][af]\
                                ['instance'][instance]['areas'][area]['mpls']\
                                ['te']['link_hash_bucket'][link_hash_bucket]
                continue

            # Link is associated with fragment 2. Link instance is 2
            m = p5.match(line)
            if m:
                link_fragment = int(m.groupdict()['fragment'])
                if 'link_fragments' not in link_dict:
                    link_dict['link_fragments'] = {}
                if link_fragment not in link_dict['link_fragments']:
                    link_dict['link_fragments'][link_fragment] = {}
                sub_dict = link_dict['link_fragments'][link_fragment]
                sub_dict['link_instance'] = int(m.groupdict()['link_instance'])
                continue

            # Link connected to Broadcast network
            m = p6.match(line)
            if m:
                sub_dict['network_type'] = str(m.groupdict()['type']).lower()
                continue

            # Link ID : 10.1.2.1
            m = p7.match(line)
            if m:
                sub_dict['link_id'] = str(m.groupdict()['link_id'])
                continue

            # Interface Address : 10.1.2.1
            m = p8.match(line)
            if m:
                sub_dict['interface_address'] = str(m.groupdict()['addr'])
                continue

            # Admin Metric te: 1 igp: 1
            m = p9.match(line)
            if m:
                sub_dict['te_admin_metric'] = int(m.groupdict()['te'])
                sub_dict['igp_admin_metric'] = int(m.groupdict()['igp'])
                continue

            # Maximum bandwidth : 125000000
            m = p14.match(line) #Modified from p9 to p14
            if m:
                sub_dict['max_bandwidth'] = int(m.groupdict()['mband'])
                continue

            # Maximum reservable bandwidth : 93750000
            m = p10.match(line)
            if m:
                sub_dict['max_reservable_bandwidth'] = \
                    int(m.groupdict()['res_band'])
                continue

            # Affinity Bit : 0x0
            m = p11.match(line)
            if m:
                sub_dict['affinity_bit'] = str(m.groupdict()['admin_group'])
                continue

            # Number of Priority : 8
            m = p12.match(line)
            if m:
                sub_dict['total_priority'] = int(m.groupdict()['priority'])
                continue

            # Priority 0 : 93750000     Priority 1 : 93750000
            m = p13.match(line)
            if m:
                value1 = '{} {}'.format(str(m.groupdict()['num1']), str(m.groupdict()['band1']))
                value2 = '{} {}'.format(str(m.groupdict()['num2']), str(m.groupdict()['band2']))
                if 'unreserved_bandwidths' not in sub_dict:
                    sub_dict['unreserved_bandwidths'] = {}
                if value1 not in sub_dict['unreserved_bandwidths']:
                    sub_dict['unreserved_bandwidths'][value1] = {}
                    sub_dict['unreserved_bandwidths'][value1]['priority'] =  \
                        int(m.groupdict()['num1'])
                    sub_dict['unreserved_bandwidths'][value1]\
                        ['unreserved_bandwidth'] = int(m.groupdict()['band1'])
                if value2 not in sub_dict['unreserved_bandwidths']:
                    sub_dict['unreserved_bandwidths'][value2] = {}
                    sub_dict['unreserved_bandwidths'][value2]['priority'] = \
                        int(m.groupdict()['num2'])
                    sub_dict['unreserved_bandwidths'][value2]\
                        ['unreserved_bandwidth'] = int(m.groupdict()['band2'])
                continue

        return ret_dict


# ========================================
# Schema for:
#   * 'show ip ospf mpls traffic-eng link__'
# ========================================
class ShowIpOspfMplsTrafficEngLink2Schema(MetaParser):

    ''' Schema for:
        * 'show ip ospf mpls traffic-eng link__'
    '''

    schema = {
            'address_family': 
                {Any(): 
                    {'instance': 
                        {Any(): 
                            {'mpls': 
                                {'te': 
                                    {'router_id': str},
                                },
                            'areas': 
                                {Any(): 
                                    {'mpls': 
                                        {'te': 
                                            {'enable': bool,
                                            Optional('total_links'): int,
                                            Optional('area_instance'): int,
                                            Optional('link_hash_bucket'):
                                                {Any(): 
                                                    {'link_fragments': 
                                                        {Any(): 
                                                            {'link_instance': int,
                                                            'network_type': str,
                                                            'link_id': str,
                                                            'interface_address': str,
                                                            'te_admin_metric': int,
                                                            'igp_admin_metric': int,
                                                            'max_bandwidth': int,
                                                            'max_reservable_bandwidth': int,
                                                            'affinity_bit': str,
                                                            'total_priority': int,
                                                            Optional('unreserved_bandwidths'): 
                                                                {Any(): 
                                                                    {'priority': int,
                                                                    'unreserved_bandwidth': int
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            }

# ========================================
# Parser for:
#   * 'show ip ospf mpls traffic-eng link__'
# ========================================
class ShowIpOspfMplsTrafficEngLink2(ShowIpOspfMplsTrafficEngLink2Schema):

    ''' Parser for:
        * 'show ip ospf mpls traffic-eng link__'
    '''

    cli_command = 'show ip ospf mpls traffic-eng link__'

    def cli(self, output=None):

        if output is None:
            # Execute command on device
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4' # this is ospf - always ipv4

        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\)'
                            r' +\(Process +ID +(?P<instance>(\S+))\)$')

        p2 = re.compile(r'^Area +(?P<area>(\d+)) +has +(?P<links>(\d+))'
                            r' +MPLS +TE +links. +Area +instance +is'
                            r' +(?P<area_instance>(\d+))\.$')

        p3 = re.compile(r'^Area +(?P<area>(\S+)) +MPLS +TE +not +initialized$')

        p4 = re.compile(r'^Links +in +hash +bucket +(?P<hash>(\d+))\.$')

        p5 = re.compile(r'^Link +is +associated +with +fragment'
                            r' +(?P<fragment>(\d+))\. +Link +instance +is'
                            r' +(?P<link_instance>(\d+))$')

        p6 = re.compile(r'^Link +connected +to +(?P<type>([a-zA-Z\s]+))$')

        p7 = re.compile(r'^Link +ID *: +(?P<link_id>(\S+))$')

        p8 = re.compile(r'^Interface +Address *: +(?P<addr>(\S+))$')

        p9 = re.compile(r'^Admin +Metric +te: +(?P<te>(\d+)) +igp:'
                            r' +(?P<igp>(\d+))$')

        p14 = re.compile(r'^Maximum +(B|b)andwidth *: +(?P<mband>(\d+))$')

        p10 = re.compile(r'^Maximum +(R|r)eservable +(B|b)andwidth *:'
                            r' +(?P<res_band>(\d+))$')

        p11 = re.compile(r'^Affinity +Bit *: +(?P<admin_group>(\S+))$')

        p12 = re.compile(r'^Number +of +Priority +: +(?P<priority>(\d+))$')

        p13 = re.compile(r'^Priority +(?P<num1>(\d+)) *:'
                            r' +(?P<band1>(\d+))(?: +Priority +(?P<num2>(\d+))'
                            r' *: +(?P<band2>(\d+)))?$')


        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 1)
            m = p1.match(line)
            if m:
                router_id = str(m.groupdict()['router_id'])
                instance = str(m.groupdict()['instance'])
                # Create dict
                instance_dict = ret_dict.setdefault('address_family',{}).\
                                         setdefault(af,{}).\
                                         setdefault('instance',{}).\
                                         setdefault(instance,{})
                                       
                router_dict = instance_dict.setdefault('mpls',{}).\
                                            setdefault('te',{})
                
                router_dict.update({'router_id': router_id})
                continue

            # Area 0 has 2 MPLS TE links. Area instance is 2.
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                total_links = int(m.groupdict()['links'])
                area_instance = int(m.groupdict()['area_instance'])
                # Create dict
                area_dict = instance_dict.setdefault('areas', {}).\
                                          setdefault(area, {}).\
                                          setdefault('mpls', {}).\
                                          setdefault('te', {})

                area_dict.update({'enable': True, 'total_links': total_links,
                                  'area_instance': area_instance})
                continue

            # Area 1 MPLS TE not initialized
            # Area 0.0.0.0 MPLS TE not initialized
            m = p3.match(line)
            if m:
                try:
                    int(m.groupdict()['area'])
                    area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                except:
                    area = m.groupdict()['area']
                # Create dict
                area_dict = instance_dict.setdefault('areas', {}).\
                                          setdefault(area, {}).\
                                          setdefault('mpls', {}).\
                                          setdefault('te', {})
                # Set values
                area_dict.update({'enable': False})
                continue

            # Links in hash bucket 8.
            m = p4.match(line)
            if m:
                link_hash_bucket = int(m.groupdict()['hash'])
                link_dict = area_dict.setdefault('link_hash_bucket', {}).\
                                                  setdefault(link_hash_bucket, {})
                continue

            # Link is associated with fragment 2. Link instance is 2
            m = p5.match(line)
            if m:
                link_fragment = int(m.groupdict()['fragment'])
                sub_dict = link_dict.setdefault('link_fragments', {}).\
                                     setdefault(link_fragment, {})
                sub_dict['link_instance'] = int(m.groupdict()['link_instance'])
                continue

            # Link connected to Broadcast network
            m = p6.match(line)
            if m:
                sub_dict['network_type'] = str(m.groupdict()['type']).lower()
                continue

            # Link ID : 10.1.2.1
            m = p7.match(line)
            if m:
                sub_dict['link_id'] = str(m.groupdict()['link_id'])
                continue

            # Interface Address : 10.1.2.1
            m = p8.match(line)
            if m:
                sub_dict['interface_address'] = str(m.groupdict()['addr'])
                continue

            # Admin Metric te: 1 igp: 1
            m = p9.match(line)
            if m:
                sub_dict['te_admin_metric'] = int(m.groupdict()['te'])
                sub_dict['igp_admin_metric'] = int(m.groupdict()['igp'])
                continue

            # Maximum bandwidth : 125000000
            m = p14.match(line) #Modified from p9 to p14
            if m:
                sub_dict['max_bandwidth'] = int(m.groupdict()['mband'])
                continue

            # Maximum reservable bandwidth : 93750000
            m = p10.match(line)
            if m:
                sub_dict['max_reservable_bandwidth'] = \
                    int(m.groupdict()['res_band'])
                continue

            # Affinity Bit : 0x0
            m = p11.match(line)
            if m:
                sub_dict['affinity_bit'] = str(m.groupdict()['admin_group'])
                continue

            # Number of Priority : 8
            m = p12.match(line)
            if m:
                sub_dict['total_priority'] = int(m.groupdict()['priority'])
                continue

            # Priority 0 : 93750000     Priority 1 : 93750000
            m = p13.match(line)
            if m:
                value1 = '{} {}'.format(str(m.groupdict()['num1']), str(m.groupdict()['band1']))
                value2 = '{} {}'.format(str(m.groupdict()['num2']), str(m.groupdict()['band2']))
                if 'unreserved_bandwidths' not in sub_dict:
                    sub_dict['unreserved_bandwidths'] = {}
                if value1 not in sub_dict['unreserved_bandwidths']:
                    sub_dict['unreserved_bandwidths'][value1] = {}
                    sub_dict['unreserved_bandwidths'][value1]['priority'] =  \
                        int(m.groupdict()['num1'])
                    sub_dict['unreserved_bandwidths'][value1]\
                        ['unreserved_bandwidth'] = int(m.groupdict()['band1'])
                if value2 not in sub_dict['unreserved_bandwidths']:
                    sub_dict['unreserved_bandwidths'][value2] = {}
                    sub_dict['unreserved_bandwidths'][value2]['priority'] = \
                        int(m.groupdict()['num2'])
                    sub_dict['unreserved_bandwidths'][value2]\
                        ['unreserved_bandwidth'] = int(m.groupdict()['band2'])

                continue

        return ret_dict

# =============================
# Schema for:
#   * 'show ip ospf max-metric'
# =============================
class ShowIpOspfMaxMetricSchema(MetaParser):
    
    ''' Schema for:
        * 'show ip ospf max-metric'
    '''

    schema = {
        'vrf':
            {Any():
                {'address_family':
                    {Any():
                        {'instance':
                            {Any():
                                {'router_id': str,
                                'base_topology_mtid':
                                    {Any():
                                        {'start_time': str,
                                        'time_elapsed': str,
                                        'router_lsa_max_metric':
                                            {Any(): 
                                                {Optional('condition'): str,
                                                Optional('state'): str,
                                                Optional('advertise_lsa_metric'): int,
                                                Optional('unset_reason'): str,
                                                Optional('unset_time'): str,
                                                Optional('unset_time_elapsed'): str,
                                                Optional('time_remaining'): str,
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# =============================
# Parser for:
#   * 'show ip ospf max-metric'
# =============================
class ShowIpOspfMaxMetric(ShowIpOspfMaxMetricSchema):

    ''' Parser for:
        * 'show ip ospf max-metric'
    '''

    cli_command = 'show ip ospf max-metric'

    def cli(self, output=None):

        if output is None:
            # Execute command on device
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        address_family = 'ipv4'

        # Load for five secs: 71%/0%; one minute: 11%; five minutes: 9%
        # Time source is NTP, 20:29:26.348 EST Fri Nov 11 2016

        # OSPF Router with ID (172.16.1.214) (Process ID 65109)
        # OSPF Router with ID (10.36.3.3) (Process ID 1, VRF VRF1)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\)'
                         r' +\(Process +ID +(?P<instance>(\d+))'
                         r'(?:, +VRF +(?P<vrf>(\S+)))?\)$')

        # Base Topology (MTID 0)
        p2 = re.compile(r'^Base +Topology +\(MTID +(?P<mtid>(\d+))\)$')

        # Start time: 00:01:58.314, Time elapsed: 00:54:43.858
        p3 = re.compile(r'^Start +time: +(?P<start_time>(\S+)), +Time +elapsed:'
                         r' +(?P<time_elapsed>(\S+))$')

        # Originating router-LSAs with maximum metric
        # Originating router-LSAs with maximum metric, Time remaining: 00:03:55
        p4_1 = re.compile(r'^Originating +router-LSAs +with +maximum +metric(, +Time +remaining: +(?P<time_remaining>([\d\:]+)))?$')

        # Router is not originating router-LSAs with maximum metric
        p4_2 = re.compile(r'^Router +is +not +originating +router-LSAs +with'
                           r' +maximum +metric$')

        # Condition: on startup for 5 seconds, State: inactive
        p5 = re.compile(r'^Condition: +(?P<condition>(.*)), +State:'
                          r' +(?P<state>([a-zA-Z\s]+))$')

        # Advertise summary-LSAs with metric 16711680
        p6 = re.compile(r'^Advertise +summary-LSAs +with +metric'
                         r' +(?P<metric>(\d+))$')

        # Unset reason: timer expired, Originated for 5 seconds
        p7 = re.compile(r'^Unset +reason: (?P<reason>(.*))$')

        # Unset time: 00:02:03.314, Time elapsed: 00:54:38.858
        p8 = re.compile(r'^Unset +time: +(?P<time>(\S+)), +Time +elapsed:'
                         r' +(?P<elapsed>(\S+))$')

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.36.3.3) (Process ID 1, VRF VRF1)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                router_id = str(group['router_id'])
                instance = str(group['instance'])
                if group['vrf']:
                    vrf = str(group['vrf'])
                else:
                    vrf = 'default'
                # Create dict
                ospf_dict = ret_dict.setdefault('vrf', {}).\
                                     setdefault(vrf, {}).\
                                     setdefault('address_family', {}).\
                                     setdefault(address_family, {}).\
                                     setdefault('instance', {}).\
                                     setdefault(instance, {})
                ospf_dict['router_id'] = router_id
                continue

            # Base Topology (MTID 0)
            m = p2.match(line)
            if m:
                mtid = m.groupdict()['mtid']
                mtid_dict = ospf_dict.setdefault('base_topology_mtid', {}).\
                                      setdefault(mtid, {})
                continue

            # Start time: 00:01:58.314, Time elapsed: 00:54:43.858
            m = p3.match(line)
            if m:
                group = m.groupdict()
                mtid_dict['start_time'] = group['start_time']
                mtid_dict['time_elapsed'] = group['time_elapsed']
                continue

            # Originating router-LSAs with maximum metric
            # Originating router-LSAs with maximum metric, Time remaining: 00:03:55
            m = p4_1.match(line)
            if m:
                rtr_lsa_dict = mtid_dict.\
                                    setdefault('router_lsa_max_metric', {}).\
                                    setdefault(True, {})
                if m.groupdict()['time_remaining']:
                    rtr_lsa_dict['time_remaining'] = m.groupdict()['time_remaining']
                continue

            # Router is not originating router-LSAs with maximum metric
            m = p4_2.match(line)
            if m:
                rtr_lsa_dict = mtid_dict.\
                                    setdefault('router_lsa_max_metric', {}).\
                                    setdefault(False, {})
                continue

            # Condition: on startup for 5 seconds, State: inactive
            m = p5.match(line)
            if m:
                group = m.groupdict()
                rtr_lsa_dict['condition'] = group['condition']
                rtr_lsa_dict['state'] = group['state']
                continue

            # Advertise summary-LSAs with metric 16711680
            m = p6.match(line)
            if m:
                rtr_lsa_dict['advertise_lsa_metric'] = int(m.groupdict()['metric'])

            # Unset reason: timer expired, Originated for 5 seconds
            m = p7.match(line)
            if m:
                rtr_lsa_dict['unset_reason'] = m.groupdict()['reason']
                continue

            # Unset time: 00:02:03.314, Time elapsed: 00:54:38.858
            m = p8.match(line)
            if m:
                group = m.groupdict()
                rtr_lsa_dict['unset_time'] = group['time']
                rtr_lsa_dict['unset_time_elapsed'] = group['elapsed']
                continue

        return ret_dict


# ==========================
# Schema for:
#   * 'show ip ospf traffic'
# ==========================
class ShowIpOspfTrafficSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf traffic'
    '''

    schema = {
        Optional('ospf_statistics'):
            {'last_clear_traffic_counters': str,
            'rcvd':
                {'total': int,
                'checksum_errors': int,
                'hello': int,
                'database_desc': int,
                'link_state_req': int,
                'link_state_updates': int,
                'link_state_acks': int,
                },
            'sent':
                {'total': int,
                'hello': int,
                'database_desc': int,
                'link_state_req': int,
                'link_state_updates': int,
                'link_state_acks': int,
                },
            },
        'vrf':
            {Any():
                {'address_family':
                    {Any():
                        {'instance':
                            {Any():
                                {
                                Optional('router_id'): str,
                                Optional('ospf_queue_statistics'):
                                    {'limit': 
                                        {'inputq': int,
                                        'outputq': int,
                                        'updateq': int,
                                        },
                                    'drops': 
                                        {'inputq': int,
                                        'outputq': int,
                                        'updateq': int,
                                        },
                                    'max_delay_msec': 
                                        {'inputq': int,
                                        'outputq': int,
                                        'updateq': int,
                                        },
                                    'max_size': 
                                        {'total': 
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'invalid':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'hello':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'db_des':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_req':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_upd':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_ack':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        },
                                    'current_size': 
                                        {'total': 
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'invalid':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'hello':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'db_des':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_req':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_upd':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        'ls_ack':
                                            {'inputq': int,
                                            'outputq': int,
                                            'updateq': int,
                                            },
                                        },
                                    },
                                Optional('interface_statistics'):
                                    {'interfaces':
                                        {Any():
                                            {'last_clear_traffic_counters': str,
                                            'ospf_packets_received_sent':
                                                {'type': 
                                                    {Any():
                                                        {'packets': int,
                                                        'bytes': int,
                                                        },
                                                    },
                                                },
                                            'ospf_header_errors':
                                                {'length': int,
                                                'instance_id': int,
                                                'checksum': int,
                                                'auth_type': int,
                                                'version': int,
                                                'bad_source': int,
                                                'no_virtual_link': int,
                                                'area_mismatch': int,
                                                'no_sham_link': int,
                                                'self_originated': int,
                                                'duplicate_id': int,
                                                'hello': int,
                                                'mtu_mismatch': int,
                                                'nbr_ignored': int,
                                                'lls': int,
                                                'unknown_neighbor': int,
                                                'authentication': int,
                                                'ttl_check_fail': int,
                                                Optional('adjacency_throttle'): int,
                                                Optional('bfd'): int,
                                                'test_discard': int,
                                                },
                                            'ospf_lsa_errors':
                                                {'type': int,
                                                'length': int,
                                                'data': int,
                                                'checksum': int,
                                                },
                                            },
                                        },
                                    },
                                'summary_traffic_statistics':
                                    {'ospf_packets_received_sent': 
                                        {'type':
                                            {Any():
                                                {'packets': int,
                                                'bytes': int,
                                                },
                                            },
                                        },
                                    'ospf_header_errors':
                                        {'length': int,
                                        'instance_id': int,
                                        'checksum': int,
                                        'auth_type': int,
                                        'version': int,
                                        'bad_source': int,
                                        'no_virtual_link': int,
                                        'area_mismatch': int,
                                        'no_sham_link': int,
                                        'self_originated': int,
                                        'duplicate_id': int,
                                        'hello': int,
                                        'mtu_mismatch': int,
                                        'nbr_ignored': int,
                                        'lls': int,
                                        'unknown_neighbor': int,
                                        'authentication': int,
                                        'ttl_check_fail': int,
                                        Optional('adjacency_throttle'): int,
                                        Optional('bfd'): int,
                                        'test_discard': int,
                                        },
                                    'ospf_lsa_errors':
                                        {'type': int,
                                        'length': int,
                                        'data': int,
                                        'checksum': int,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


# ==========================
# Parser for:
#   * 'show ip ospf traffic'
# ==========================
class ShowIpOspfTraffic(ShowIpOspfTrafficSchema):

    ''' Parser for:
        * "show ip ospf traffic"
    '''

    cli_command = 'show ip ospf traffic'

    def cli(self, output=None):

        if output is None:
            # Execute command on device
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        ret_dict = {}
        address_family = 'ipv4'
        vrf = 'default'
        received = False ; sent = False
        interface_stats = False ; summary_stats = False
        max_size_stats = False ; current_size_stats = False

        # OSPF statistics:
        p1 = re.compile(r'^OSPF +statistics:$')

        # Last clearing of OSPF traffic counters never
        # Last clearing of interface traffic counters never
        p2 = re.compile(r'^Last +clearing +of +(?P<type>(OSPF|interface)) +traffic'
                         r' +counters +(?P<last_clear>([a-zA-Z0-9\:\s]+))$')

        # Rcvd: 2112690 total, 0 checksum errors
        p3 = re.compile(r'^Rcvd: +(?P<total>(\d+)) total, +(?P<csum_errors>(\d+))'
                         r' +checksum +errors$')

        # 2024732 hello, 938 database desc, 323 link state req
        # 2381794 hello, 1176 database desc, 43 link state req
        p4 = re.compile(r'^(?P<hello>(\d+)) +hello, +(?P<db_desc>(\d+))'
                         r' +database +desc, +(?P<link_state_req>(\d+))'
                         r' +link +state +req$')

        # 11030 link state updates, 75666 link state acks
        # 92224 link state updates, 8893 link state acks
        p5 = re.compile(r'^(?P<link_state_updates>(\d+)) +link +state +updates,'
                         r' +(?P<link_state_acks>(\d+)) +link +state +acks$')

        # Sent: 2509472 total
        p6 = re.compile(r'^Sent: +(?P<total>(\d+)) +total$')


        # OSPF Router with ID (10.169.197.252) (Process ID 65109)
        # OSPF Router with ID (10.36.3.3) (Process ID 1, VRF VRF1)
        p7 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\)'
                         r' +\(Process +ID +(?P<instance>(\d+))'
                         r'(?:, +VRF +(?P<vrf>(\S+)))?\)$')

        # OSPF queue statistics for process ID 65109:
        p8 = re.compile(r'^OSPF +queue +statistics +for +process +ID +(?P<pid>(\d+)):$')

        #                   InputQ   UpdateQ      OutputQ
        # Limit             0        200          0
        # Drops             0          0          0
        # Max delay [msec] 49          2          2
        p9_1 = re.compile(r'^(?P<item>(Limit|Drops|Max delay \[msec\])) +'
                        r'(?P<inputq>(\d+)) +(?P<updateq>(\d+)) +(?P<outputq>(\d+))$')
        
        # Invalid           0          0          0
        # Hello             0          0          0
        # DB des            0          0          0
        # LS req            0          0          0
        # LS upd            0          0          0
        # LS ack           14         14          6
        p9_2 = re.compile(r'^(?P<item>(Invalid|Hello|DB des|LS '
                        r'req|LS upd|LS ack)) +(?P<inputq>(\d+)) '
                        r'+(?P<updateq>(\d+)) +(?P<outputq>(\d+))$')

        #                   InputQ   UpdateQ      OutputQ
        # Max size         14         14          6
        # Current size      0          0          0
        p9_3 = re.compile(r'^(?P<item>(Max size|Current size)) +(?P<inputq>(\d+))'
                           r' +(?P<updateq>(\d+)) +(?P<outputq>(\d+))$')

        # Interface statistics:
        p10 = re.compile(r'^Interface +statistics:$')

        # Interface GigabitEthernet0/0/6
        p11 = re.compile(r'^Interface +(?P<intf>(\S+))$')

        # OSPF packets received/sent
        # Type          Packets              Bytes
        # RX Invalid    0                    0
        # RX Hello      169281               8125472
        # RX DB des     36                   1232
        # RX LS req     20                   25080
        # RX LS upd     908                  76640
        # RX LS ack     9327                 8733808
        # RX Total      179572               16962232
        # TX Failed     0                    0
        # TX Hello      169411               13552440
        # TX DB des     40                   43560
        # TX LS req     4                    224
        # TX LS upd     12539                12553264
        # TX LS ack     899                  63396
        # TX Total      182893               26212884
        p12 = re.compile(r'^(?P<type>([a-zA-Z\s]+)) +(?P<packets>(\d+))'
                          r' +(?P<bytes>(\d+))$')

        # OSPF header errors
        p13 = re.compile(r'^OSPF +header +errors$')

        # Length 0, Instance ID 0, Checksum 0, Auth Type 0,
        p14 = re.compile(r'^Length +(?P<len>(\d+)), +Instance +ID'
                          r' +(?P<iid>(\d+)), +Checksum +(?P<csum>(\d+)),'
                          r' +Auth +Type +(?P<auth>(\d+)),?$')

        # Version 0, Bad Source 0, No Virtual Link 0,
        p15 = re.compile(r'^Version +(?P<version>(\d+)), +Bad +Source'
                          r' +(?P<bad_source>(\d+)), +No +Virtual +Link'
                          r' +(?P<no_virtual_link>(\d+)),?$')

        # Area Mismatch 0, No Sham Link 0, Self Originated 0,
        p16 = re.compile(r'^Area +Mismatch +(?P<area_mismatch>(\d+)),'
                          r' +No +Sham +Link +(?P<no_sham_link>(\d+)),'
                          r' +Self +Originated +(?P<self_originated>(\d+)),?$')

        # Duplicate ID 0, Hello 0, MTU Mismatch 0,
        p17 = re.compile(r'^Duplicate +ID +(?P<duplicate_id>(\d+)),'
                          r' +Hello +(?P<hello>(\d+)), +MTU +Mismatch'
                          r' +(?P<mtu_mismatch>(\d+)),$')

        # Nbr Ignored 0, LLS 0, Unknown Neighbor 0,
        p18 = re.compile(r'^Nbr +Ignored +(?P<nbr_ignored>(\d+)), +LLS'
                          r' +(?P<lls>(\d+)), +Unknown +Neighbor'
                          r' +(?P<unknown_neighbor>(\d+)),?$')

        # Authentication 0, TTL Check Fail 0, Adjacency Throttle 0,
        p19 = re.compile(r'^Authentication +(?P<authentication>(\d+)), +TTL'
                          r' +Check +Fail +(?P<ttl_check_fail>(\d+)), +Adjacency'
                          r' +Throttle +(?P<adjacency_throttle>(\d+)),?$')

        # Authentication 0, TTL Check Fail 0, Test discard 0
        p19_1 = re.compile(r'^Authentication +(?P<authentication>\d+), +TTL'
                          r' +Check +Fail +(?P<ttl_check_fail>\d+), +Test discard'
                          r' +(?P<test_discard>\d+),?$')

        # BFD 0, Test discard 0
        p20 = re.compile(r'^BFD +(?P<bfd>(\d+)), +Test +discard'
                          r' +(?P<test_discard>(\d+))$')

        # OSPF LSA errors
        p21 = re.compile(r'^OSPF +LSA +errors$')

        # Type 0, Length 0, Data 0, Checksum 0
        p22 = re.compile(r'^Type +(?P<type>(\d+)), +Length +(?P<len>(\d+)),'
                          r' +Data +(?P<data>(\d+)), +Checksum +(?P<csum>(\d+))$')

        # Summary traffic statistics for process ID 65109:
        p23 = re.compile(r'^Summary +traffic +statistics +for +process +ID'
                          r' +(?P<pid>(\d+)):$')

        for line in out.splitlines():
            line = line.strip()

            # OSPF statistics:
            m = p1.match(line)
            if m:
                ospf_stats_dict = ret_dict.setdefault('ospf_statistics', {})
                continue

            # Last clearing of OSPF traffic counters never
            # Last clearing of interface traffic counters never
            m = p2.match(line)
            if m:
                if m.groupdict()['type'] == 'OSPF':
                    ospf_stats_dict['last_clear_traffic_counters'] = \
                                                m.groupdict()['last_clear']
                if m.groupdict()['type'] == 'interface':
                    intf_dict['last_clear_traffic_counters'] = \
                                                m.groupdict()['last_clear']
                continue

            # Rcvd: 2112690 total, 0 checksum errors
            m = p3.match(line)
            if m:
                group = m.groupdict()
                rcvd_dict = ospf_stats_dict.setdefault('rcvd', {})
                rcvd_dict['total'] = int(group['total'])
                rcvd_dict['checksum_errors'] = int(group['csum_errors'])
                received = True ; sent = False
                continue

            # 2024732 hello, 938 database desc, 323 link state req
            # 2381794 hello, 1176 database desc, 43 link state req
            m = p4.match(line)
            if m:
                group = m.groupdict()
                if received:
                    sdict = rcvd_dict
                elif sent:
                    sdict = sent_dict
                else:
                    continue
                sdict['hello'] = int(group['hello'])
                sdict['database_desc'] = int(group['db_desc'])
                sdict['link_state_req'] = int(group['link_state_req'])
                continue

            # 11030 link state updates, 75666 link state acks
            # 92224 link state updates, 8893 link state acks
            m = p5.match(line)
            if m:
                group = m.groupdict()
                if received:
                    sdict = rcvd_dict
                elif sent:
                    sdict = sent_dict
                else:
                    continue
                sdict['link_state_updates'] = int(group['link_state_updates'])
                sdict['link_state_acks'] = int(group['link_state_acks'])
                continue

            # Sent: 2509472 total
            m = p6.match(line)
            if m:
                group = m.groupdict()
                sent_dict = ospf_stats_dict.setdefault('sent', {})
                sent_dict['total'] = int(group['total'])
                sent = True ; received = False
                continue

            # OSPF Router with ID (10.169.197.252) (Process ID 65109)
            # OSPF Router with ID (10.36.3.3) (Process ID 1, VRF VRF1)
            m = p7.match(line)
            if m:
                group = m.groupdict()
                router_id = str(group['router_id'])
                instance = str(group['instance'])
                if group['vrf']:
                    vrf = str(group['vrf'])
                else:
                    vrf = 'default'
                # Create dict
                ospf_dict = ret_dict.setdefault('vrf', {}).\
                                     setdefault(vrf, {}).\
                                     setdefault('address_family', {}).\
                                     setdefault(address_family, {}).\
                                     setdefault('instance', {}).\
                                     setdefault(instance, {})
                ospf_dict['router_id'] = router_id
                continue

            # OSPF queue statistics for process ID 65109:
            m = p8.match(line)
            if m:
                queue_stats_dict = ospf_dict.setdefault('ospf_queue_statistics', {})
                continue

            #                   InputQ   UpdateQ      OutputQ
            # Limit             0        200          0
            # Drops             0          0          0
            # Max delay [msec] 49          2          2
            m = p9_1.match(line)
            if m:
                group = m.groupdict()
                item = group['item'].strip().lower().replace(" ", "_").\
                                    replace("[", "").replace("]", "")
                tmp_dict = queue_stats_dict.setdefault(item, {})
                tmp_dict['inputq'] = int(group['inputq'])
                tmp_dict['updateq'] = int(group['updateq'])
                tmp_dict['outputq'] = int(group['outputq'])
                continue
                
            # Invalid           0          0          0
            # Hello             0          0          0
            # DB des            0          0          0
            # LS req            0          0          0
            # LS upd            0          0          0
            # LS ack           14         14          6
            m = p9_2.match(line)
            if m:
                group = m.groupdict()
                item = group['item'].strip().lower().replace(" ", "_").\
                                    replace("[", "").replace("]", "")
                if max_size_stats:
                    tmp_dict = max_size_queue_stats_dict.setdefault(item, {})
                elif current_size_stats:
                    tmp_dict = current_size_queue_stats_dict.setdefault(item, {})
                else:
                    tmp_dict = queue_stats_dict.setdefault(item, {})
                tmp_dict['inputq'] = int(group['inputq'])
                tmp_dict['updateq'] = int(group['updateq'])
                tmp_dict['outputq'] = int(group['outputq'])
                continue


            #                   InputQ   UpdateQ      OutputQ
            # Max size         14         14          6
            # Current size      0          0          0
            m = p9_3.match(line)
            if m:
                group = m.groupdict()
                item = group['item'].strip().lower().replace(" ", "_")
                tmp_dict = queue_stats_dict.setdefault(item, {})
                if item == 'max_size':
                    max_size_stats = True
                    current_size_stats = False
                    max_size_queue_stats_dict = tmp_dict
                elif item == 'current_size':
                    current_size_stats = True
                    max_size_stats = False
                    current_size_queue_stats_dict = tmp_dict
                tmp_dict.setdefault('total', {})['inputq'] = int(group['inputq'])
                tmp_dict.setdefault('total', {})['updateq'] = int(group['updateq'])
                tmp_dict.setdefault('total', {})['outputq'] = int(group['outputq'])
                continue

            # Interface statistics:
            m = p10.match(line)
            if m:
                intf_stats_dict = ospf_dict.setdefault('interface_statistics', {})
                continue

            # Interface GigabitEthernet0/0/6
            m = p11.match(line)
            if m:
                intf = m.groupdict()['intf']
                intf_dict = intf_stats_dict.setdefault('interfaces', {}).\
                                            setdefault(intf, {})
                interface_stats = True ; summary_stats = False
                continue

            # Type          Packets              Bytes
            # RX Invalid    0                    0
            # RX Hello      169281               8125472
            # RX DB des     36                   1232
            # RX LS req     20                   25080
            # RX LS upd     908                  76640
            # RX LS ack     9327                 8733808
            # RX Total      179572               16962232
            # TX Failed     0                    0
            # TX Hello      169411               13552440
            # TX DB des     40                   43560
            # TX LS req     4                    224
            # TX LS upd     12539                12553264
            # TX LS ack     899                  63396
            # TX Total      182893               26212884
            m = p12.match(line)
            if m:
                group = m.groupdict()
                if interface_stats:
                    sdict = intf_dict
                elif summary_stats:
                    sdict = summary_stats_dict
                else:
                    continue
                item_type = group['type'].strip().lower().replace(" ", "_")
                tmp_dict = sdict.setdefault('ospf_packets_received_sent', {}).\
                            setdefault('type', {}).setdefault(item_type, {})
                tmp_dict['packets'] = int(group['packets'])
                tmp_dict['bytes'] = int(group['bytes'])
                continue

            # OSPF header errors
            m = p13.match(line)
            if m:
                group = m.groupdict()
                if interface_stats:
                    sdict = intf_dict
                elif summary_stats:
                    sdict = summary_stats_dict
                else:
                    continue
                ospf_header_errors_dict = sdict.setdefault('ospf_header_errors', {})
                continue

            # Length 0, Instance ID 0, Checksum 0, Auth Type 0,
            m = p14.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['length'] = int(group['len'])
                ospf_header_errors_dict['instance_id'] = int(group['iid'])
                ospf_header_errors_dict['checksum'] = int(group['csum'])
                ospf_header_errors_dict['auth_type'] = int(group['auth'])
                continue

            # Version 0, Bad Source 0, No Virtual Link 0,
            m = p15.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['version'] = int(group['version'])
                ospf_header_errors_dict['bad_source'] = int(group['bad_source'])
                ospf_header_errors_dict['no_virtual_link'] = int(group['no_virtual_link'])
                continue

            # Area Mismatch 0, No Sham Link 0, Self Originated 0,
            m = p16.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['area_mismatch'] = int(group['area_mismatch'])
                ospf_header_errors_dict['no_sham_link'] = int(group['no_sham_link'])
                ospf_header_errors_dict['self_originated'] = int(group['self_originated'])
                continue

            # Duplicate ID 0, Hello 0, MTU Mismatch 0,
            m = p17.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['duplicate_id'] = int(group['duplicate_id'])
                ospf_header_errors_dict['hello'] = int(group['hello'])
                ospf_header_errors_dict['mtu_mismatch'] = int(group['mtu_mismatch'])
                continue

            # Nbr Ignored 0, LLS 0, Unknown Neighbor 0,
            m = p18.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['nbr_ignored'] = int(group['nbr_ignored'])
                ospf_header_errors_dict['lls'] = int(group['lls'])
                ospf_header_errors_dict['unknown_neighbor'] = int(group['unknown_neighbor'])
                continue

            # Authentication 0, TTL Check Fail 0, Adjacency Throttle 0,
            m = p19.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['authentication'] = int(group['authentication'])
                ospf_header_errors_dict['ttl_check_fail'] = int(group['ttl_check_fail'])
                ospf_header_errors_dict['adjacency_throttle'] = int(group['adjacency_throttle'])
                continue

            # Authentication 0, TTL Check Fail 0, Test discard 0
            m = p19_1.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['authentication'] = int(group['authentication'])
                ospf_header_errors_dict['ttl_check_fail'] = int(group['ttl_check_fail'])
                ospf_header_errors_dict['test_discard'] = int(group['test_discard'])
                continue

            # BFD 0, Test discard 0
            m = p20.match(line)
            if m:
                group = m.groupdict()
                ospf_header_errors_dict['bfd'] = int(group['bfd'])
                ospf_header_errors_dict['test_discard'] = int(group['test_discard'])
                continue

            # OSPF LSA errors
            m = p21.match(line)
            if m:
                if interface_stats:
                    sdict = intf_dict
                elif summary_stats:
                    sdict = summary_stats_dict
                else:
                    continue
                ospf_lsa_errors_dict = sdict.setdefault('ospf_lsa_errors', {})
                continue

            # Type 0, Length 0, Data 0, Checksum 0
            m = p22.match(line)
            if m:
                group = m.groupdict()
                ospf_lsa_errors_dict['type'] = int(group['type'])
                ospf_lsa_errors_dict['length'] = int(group['len'])
                ospf_lsa_errors_dict['data'] = int(group['data'])
                ospf_lsa_errors_dict['checksum'] = int(group['csum'])
                continue

            # Summary traffic statistics for process ID 65109:
            m = p23.match(line)
            if m:
                pid = m.groupdict()['pid']
                ospf_dict = ret_dict.setdefault('vrf', {}).\
                                     setdefault(vrf, {}).\
                                     setdefault('address_family', {}).\
                                     setdefault(address_family, {}).\
                                     setdefault('instance', {}).\
                                     setdefault(pid, {})
                summary_stats_dict = ospf_dict.\
                                setdefault('summary_traffic_statistics', {})
                interface_stats = False ; summary_stats = True
                vrf = 'default'
                continue

        return ret_dict


# ===========================
# Schema for:
#   * 'show ip ospf neighbor'
#   * 'show ip ospf neighbor {interface}'
#   * 'show ip ospf {process_id} neighbor'
#   * 'show ip ospf {process_id} neighbor {interface}'
# ===========================
class ShowIpOspfNeighborSchema(MetaParser):

    ''' Schema for:
        * 'show ip ospf neighbor'
        * 'show ip ospf neighbor {interface}'
        * 'show ip ospf {process_id} neighbor'
        * 'show ip ospf {process_id} neighbor {interface}'
    '''

    schema = {
        'interfaces':
            {Any():
                {'neighbors':
                    {Any():
                        {'priority': int,
                        'state':str,
                        'dead_time':str,
                        'address':str,
                        },
                    },
                },
            },
        }


# ===========================
# Parser for:
#   * 'show ip ospf neighbor'
#   * 'show ip ospf neighbor {interface}'
#   * 'show ip ospf {process_id} neighbor'
#   * 'show ip ospf {process_id} neighbor {interface}'
# ===========================
class ShowIpOspfNeighbor(ShowIpOspfNeighborSchema):

    ''' Parser for:
        * 'show ip ospf neighbor'
        * 'show ip ospf neighbor {interface}'
        * 'show ip ospf {process_id} neighbor'
        * 'show ip ospf {process_id} neighbor {interface}'
    '''

    cli_command = [
        'show ip ospf neighbor {interface}',
        'show ip ospf neighbor',
        'show ip ospf {process_id} neighbor',
        'show ip ospf {process_id} neighbor {interface}']
    exclude = ['dead_time']

    def cli(self, interface='', output=None, process_id=''):

        if output is None:
            # Execute command on device
            if interface and process_id:
                cmd = self.cli_command[3].format(process_id=process_id, interface=interface)
            elif interface:
                cmd = self.cli_command[0].format(interface=interface)
            elif process_id:
                cmd = self.cli_command[2].format(process_id=process_id)
            else:
                cmd = self.cli_command[1]

            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        ret_dict = {}

        # Neighbor ID     Pri   State           Dead Time   Address         Interface
        # 172.16.197.253 128   FULL/DR         00:00:30    172.16.165.49  GigabitEthernet0/0/1
        # 10.169.197.252   0   FULL/  -        00:00:36    10.169.197.93  GigabitEthernet2
        
        p1=re.compile(r'^(?P<neighbor>\S+) +(?P<pri>\d+) +(?P<state>\S+(?:\s+\S+)?)'
                       r' +(?P<dead_time>\S+) +(?P<address>\S+) +(?P<interface>\S+)$')

        for line in out.splitlines():

            line = line.strip()
            m = p1.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                interface = m.groupdict()['interface']

                #Build Dict

                intf_dict = ret_dict.setdefault('interfaces', {}).setdefault(interface, {})
                nbr_dict = intf_dict.setdefault('neighbors', {}).setdefault(neighbor, {})

                # Set values
                nbr_dict['priority'] = int(m.groupdict()['pri'])
                nbr_dict['state'] = str(m.groupdict()['state'])
                nbr_dict['dead_time'] = str(m.groupdict()['dead_time'])
                nbr_dict['address'] = str(m.groupdict()['address'])
                continue

        return ret_dict


class ShowIpOspfSegmentRoutingAdjacencySidSchema(MetaParser):
    ''' Schema for commands:
            * show ip ospf {process_id} segment-routing adjacency-sid
    '''
    schema = {        
        'process_id': {
            Any(): {
                'router_id': str,
                'adjacency_sids': {
                    Any(): {
                        'neighbor_id': str,
                        'neighbor_address': str,
                        'interface': str,
                        'flags': str,
                        Optional('backup_nexthop'): str,
                        Optional('backup_interface'): str,
                    }
                }
            }
        }
    }
        

class ShowIpOspfSegmentRoutingAdjacencySid(ShowIpOspfSegmentRoutingAdjacencySidSchema):
    ''' Parser for commands:
            * show ip ospf {process_id} segment-routing adjacency-sid
    '''

    cli_command = [
        'show ip ospf {process_id} segment-routing adjacency-sid',
        'show ip ospf segment-routing adjacency-sid',
    ]

    def cli(self, process_id=None, output=None):

        if output is None:
            if process_id:
                command = self.cli_command[0].format(process_id=process_id)
            else:
                command = self.cli_command[1]

            out = self.device.execute(command)
        else:
            out = output

        # OSPF Router with ID (10.4.1.1) (Process ID 65109)
        r1 = re.compile(r'OSPF\s+Router\s+with\s+ID\s+\((?P<router_id>\S+)\)\s+'
                         r'\(Process\s+ID\s+(?P<process_id>\d+)\)')

        # 16       10.16.2.2         Gi0/1/2            192.168.154.2       D U   
        # 17       10.16.2.2         Gi0/1/1            192.168.4.2       D U   
        r2 = re.compile(r'(?P<adj_sid>\d+)\s+(?P<neighbor_id>\S+)\s+'
                         r'(?P<interface>\S+)\s+(?P<neighbor_address>\S+)\s+'
                         r'(?P<flags>[SDPUGL\s]+)\s*(?:(?P<backup_nexthop>\S+))?'
                         r'\s*(?:(?P<backup_interface>\S+))?')

        parsed_output = {}

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            result = r1.match(line)
            if result:
                group = result.groupdict()

                router_id = group['router_id']
                process_id = group['process_id']

                process_id_dict = parsed_output.setdefault('process_id', {})\
                .setdefault(process_id, {})

                process_id_dict['router_id'] = router_id

                continue

            # 16       10.16.2.2         Gi0/1/2            192.168.154.2       D U
            # 17       10.16.2.2         Gi0/1/1            192.168.4.2       D U
            result = r2.match(line)
            if result:

                group = result.groupdict()
                adj_sid = group['adj_sid']

                adjs_sid_dict = process_id_dict.setdefault('adjacency_sids', {})\
                .setdefault(adj_sid, {})

                adjs_sid_dict['neighbor_id'] = group['neighbor_id']
                interface = group['interface']
                adjs_sid_dict['interface'] = Common.convert_intf_name(str(interface))
                adjs_sid_dict['neighbor_address'] = group['neighbor_address']
                adjs_sid_dict['flags'] = group['flags']

                backup_nexthop = group['backup_nexthop']                
                if backup_nexthop:
                    adjs_sid_dict['backup_nexthop'] = backup_nexthop

                backup_interface = group['backup_interface']
                if backup_interface:
                    adjs_sid_dict['backup_interface'] = backup_interface

                continue

        return parsed_output

# =================================================
# Schema for:
#   * 'show ip ospf fast-reroute ti-lfa'
# =================================================

class ShowIpOspfFastRerouteTiLfaSchema(MetaParser):
    """Schema for show ip ospf fast-reroute ti-lfa
    """

    schema = {
        'process_id': {
            Any(): {
                'router_id': str,
                'ospf_object': {
                    Any(): {
                        'ipfrr_enabled': str,
                        'sr_enabled': str,
                        'ti_lfa_configured': str,
                        'ti_lfa_enabled': str,
                    }
                }
            }
        }
    }

# =================================================
# Parser for:
#   * 'show ip ospf fast-reroute ti-lfa'
# =================================================

class ShowIpOspfFastRerouteTiLfa(ShowIpOspfFastRerouteTiLfaSchema):
    """Parser for show ip ospf fast-reroute ti-lfa
    """

    cli_command = 'show ip ospf fast-reroute ti-lfa'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # OSPF Router with ID (10.4.1.1) (Process ID 65109)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>\S+)'
            r'\) +\(Process +ID +(?P<process_id>\d+)\)')

        # Process ID (65109)       no       yes      no          no
        # Area 8                  no       yes      no          no
        # Loopback0               no       no       no          no
        # GigabitEthernet0/1/2    no       yes      no          no
        p2 = re.compile(r'^(?P<ospf_object>[\S\s]+) +(?P<ipfrr_enabled>(yes|no)'
                         r'( +\(inactive\))?) +(?P<sr_enabled>(yes|no)( +\(inactive\))?) '
                         r'+(?P<ti_lfa_configured>(yes|no)( +\(inactive\))?) +'
                         r'(?P<ti_lfa_enabled>(yes|no)( +\(inactive\))?)$')

        # initial variables
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                router_id = group['router_id']
                process_id = int(group['process_id'])
                process_id_dict = ret_dict.setdefault('process_id', {}). \
                                setdefault(process_id, {})
                process_id_dict.update({'router_id': router_id})
                ospf_object_dict = process_id_dict.setdefault('ospf_object', {})
                continue

            # Process ID (65109)       no       yes      no          no
            # Area 8                  no       yes      no          no
            # Loopback0               no       no       no          no
            # GigabitEthernet0/1/2    no       yes      no          no
            m = p2.match(line)
            if m:
                group = m.groupdict()
                ospf_object = group['ospf_object'].strip()
                ipfrr_enabled = group['ipfrr_enabled']
                sr_enabled = group['sr_enabled']
                ti_lfa_configured = group['ti_lfa_configured']
                ti_lfa_enabled = group['ti_lfa_enabled']

                ospf_object = ospf_object_dict.setdefault(ospf_object, {})

                ospf_object.update({'ipfrr_enabled': ipfrr_enabled })
                ospf_object.update({'sr_enabled': sr_enabled })
                ospf_object.update({'ti_lfa_configured': ti_lfa_configured })
                ospf_object.update({'ti_lfa_enabled': ti_lfa_enabled })
                continue

        return ret_dict


# ===============================================================
# Schema for 'show ip ospf segment-routing protected-adjacencies'
# ===============================================================

class ShowIpOspfSegmentRoutingProtectedAdjacenciesSchema(MetaParser):

    ''' Schema for show ip ospf segment-routing protected-adjacencies
    '''

    schema = {
        'process_id': {
            Any(): {
                'router_id': str,
                Optional('areas'): {
                    Any(): {                        
                        'neighbors': {
                            Any(): {
                                'interfaces': {
                                    Any(): {
                                        'address': str,
                                        'adj_sid': int,
                                        Optional('backup_nexthop'): str,
                                        Optional('backup_interface'): str
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

# ========================================================
# Parser for:
#   * 'show ip ospf segment-routing protected-adjacencies'
# ========================================================

class ShowIpOspfSegmentRoutingProtectedAdjacencies(ShowIpOspfSegmentRoutingProtectedAdjacenciesSchema):
    """ Parser for show ip ospf segment-routing protected-adjacencies
    """

    cli_command = 'show ip ospf segment-routing protected-adjacencies'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # OSPF Router with ID (10.4.1.1) (Process ID 65109)
        p1 = re.compile(r'OSPF +Router +with +ID +\((?P<router_id>\S+)\) +\('
                         r'Process +ID +(?P<process_id>\d+)\)')

        # Area with ID (8)
        p2 = re.compile(r'^Area +with +ID \((?P<area_id>\d+)\)$')

        # 10.234.30.22     Gi10                192.168.10.2       17           192.168.10.3       Gi14
        p3 = re.compile(
            r'^(?P<neighbor_id>\S+) +(?P<interface>\S+) +(?P<address>\S+) +('
            r'?P<adj_sid>\d+)( +(?P<backup_nexthop>\S+))?( +(?P<backup_interface>\S+))?$')

        # initial variables
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                router_id = group['router_id']
                process_id = int(group['process_id'])
                process_id_dict = ret_dict.setdefault('process_id', {}). \
                                    setdefault(process_id, {})
                process_id_dict['router_id'] = router_id
                continue

            # Area with ID (8)
            m = p2.match(line)
            if m:
                group = m.groupdict()
                area_id = str(IPAddress(str(group['area_id']), flags=INET_ATON))
                area_dict = process_id_dict.setdefault('areas', {}). \
                                setdefault(area_id, {})                
                continue

            # 10.234.30.22     Gi10                192.168.10.2       17           192.168.10.3       Gi14
            m = p3.match(line)
            if m:
                group = m.groupdict()
                neighbor_id = group['neighbor_id']
                interface = group['interface']
                address = group['address']
                adj_sid = int(group['adj_sid'])
                backup_nexthop = group['backup_nexthop']
                backup_interface = group['backup_interface']
                neighbor_dict = area_dict.setdefault('neighbors', {}). \
                                    setdefault(neighbor_id, {}). \
                                    setdefault('interfaces', {}). \
                                    setdefault(Common.convert_intf_name(interface), {})

                neighbor_dict.update({'address': address})
                neighbor_dict.update({'adj_sid': adj_sid})
                if backup_nexthop:
                    neighbor_dict.update({'backup_nexthop': backup_nexthop})
                if backup_interface:
                    neighbor_dict.update({'backup_interface':
                        Common.convert_intf_name(backup_interface)})
                continue

        return ret_dict


class ShowIpOspfSegmentRoutingSidDatabaseSchema(MetaParser):
    ''' Schema for commands:
            * show ip ospf segment-routing sid-database
    '''
    schema = {
        'process_id': {
            Any(): {
                'router_id': str,
                Optional('sids'): {
                    Any(): {
                        'index': {
                            Any(): {  # 1, 2, 3, ...
                                Optional('codes'): str,
                                'prefix': str,
                                Optional('adv_rtr_id'): str,
                                Optional('area_id'): str,
                                Optional('type'): str,
                                Optional('algo'): int
                            }
                        }
                    },
                    'total_entries': int
                }
            }
        }
    }


class ShowIpOspfSegmentRoutingSidDatabase(ShowIpOspfSegmentRoutingSidDatabaseSchema):
    """ Parser for commands:
            * show ip ospf segment-routing sid-database
    """

    cli_command = ['show ip ospf segment-routing sid-database']

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command[0])
        else:
            out = output

        # OSPF Router with ID (10.4.1.1) (Process ID 65109)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>[\d+\.]+)\) +'
                        r'\(Process +ID +(?P<pid>\d+)\)$')

        # 1       (L)     10.4.1.1/32          10.4.1.1          8        Intra     0
        # 2               10.16.2.2/32          10.16.2.2          8        Intra     0
        #                 10.16.2.3/32          10.16.2.2          8        Intra     0
        # 3       (M)     10.16.2.3/32                                    Unknown   0
        #                 10.36.3.3/32               10.16.2.10         0
        p2 = re.compile(r'(?:(?P<sid>\d+) +)?(?:\((?P<codes>[LNM,]+)\) +)?(?P<prefix>[\d\.\/]+)'
                        r'( +(?P<adv_rtr_id>[\d\.]+))?( +(?P<area_id>\d+))?(?: +(?P<type>\w+))?'
                        r'(?: +(?P<algo>\d+))?')

        ret_dict = {}
        sid_entries = 0

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()

                process_dict = ret_dict.setdefault('process_id', {}).setdefault(int(group['pid']), {})
                process_dict.update({'router_id': group['router_id']})
                continue

            # 1       (L)     10.4.1.1/32          10.4.1.1          8        Intra     0
            # 2               10.16.2.2/32          10.16.2.2          8        Intra     0
            #                 10.16.2.3/32          10.16.2.2          8        Intra     0
            # 3       (M)     10.16.2.3/32                                    Unknown   0
            #                 10.36.3.3/32               10.16.2.10         0
            m = p2.match(line)
            if m:
                group = m.groupdict()
                sid_entries += 1

                sids_dict = process_dict.setdefault('sids', {})
                sids_dict.update({'total_entries': sid_entries})

                if group.get('sid'):
                    index = 1
                    sid_dict = sids_dict.setdefault(int(group['sid']), {})
                else:
                    # No sid found. Using previous sid.
                    index += 1

                index_dict = sid_dict.setdefault('index', {}).setdefault(index, {})
                index_dict.update({'prefix': group['prefix']})

                if group.get('codes'):
                    index_dict.update({'codes': group['codes']})
                if group.get('adv_rtr_id'):
                    index_dict.update({'adv_rtr_id': group['adv_rtr_id']})
                if group.get('area_id'):
                    index_dict.update({'area_id': str(IPAddress(group['area_id'], flags=INET_ATON))})
                if group.get('type'):
                    index_dict.update({'type': group['type']})
                if group.get('algo'):
                    index_dict.update({'algo': int(group['algo'])})
                continue

        return ret_dict

# =====================================================
# Schema for:
#   * 'show ip ospf {pid} segment-routing global-block'
# =====================================================
class ShowIpOspfSegmentRoutingGlobalBlockSchema(MetaParser):
    """ Schema for commands:
            * show ip ospf {pid} segment-routing global-block
    """
    schema = {
        'process_id': {
            Any(): {
                'router_id': str,
                'area': int,
                'routers': {
                    Any(): {
                        'router_id': str,
                        'sr_capable': str,
                        Optional('sr_algorithm'): str,
                        Optional('srgb_base'): int,
                        Optional('srgb_range'): int,
                        Optional('sid_label'): str
                    }
                }
            }
        }
    }

# =====================================================
# Parser for:
#   * 'show ip ospf {pid} segment-routing global-block'
# =====================================================
class ShowIpOspfSegmentRoutingGlobalBlock(ShowIpOspfSegmentRoutingGlobalBlockSchema):
    """ Parser for commands:
            * show ip ospf {pid} segment-routing global-block
    """

    cli_command = ['show ip ospf segment-routing global-block',
                   'show ip ospf {process_id} segment-routing global-block']

    def cli(self, process_id=None, output=None):

        if not output:
            if not process_id:
                cmd = self.cli_command[0]
            else:
                cmd = self.cli_command[1].format(process_id=process_id)

            out = self.device.execute(cmd)
        else:
            out = output

        # OSPF Router with ID (10.4.1.1) (Process ID 1234)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>[\d+\.]+)\) +'
                         r'\(Process +ID +(?P<pid>\d+)\)$')

        # OSPF Segment Routing Global Blocks in Area 3
        p2 = re.compile(r'^OSPF +Segment +Routing +Global +Blocks +in +Area (?P<area>\d+)$')

        # *10.4.1.1         Yes         SPF,StrictSPF 16000      8000         Label
        # 10.16.2.2         Yes         SPF,StrictSPF 16000      8000         Label
        # *10.4.1.1         No
        # 10.16.2.2         No
        p3 = re.compile(r'^\*?(?P<router_id>[\d\.]+) +(?P<sr_capable>\w+)'
                         r'(?: +(?P<sr_algorithm>[\w,]+) +(?P<srgb_base>\d+) +'
                         r'(?P<srgb_range>\d+) +(?P<sid_label>\w+))?$')

        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 1234)
            m = p1.match(line)
            if m:
                group = m.groupdict()

                router_dict = ret_dict.setdefault('process_id', {}).setdefault(int(group['pid']), {})
                router_dict.update({'router_id': group['router_id']})
                continue

            # OSPF Segment Routing Global Blocks in Area 3
            m = p2.match(line)
            if m:
                group = m.groupdict()

                router_dict.update({'area': int(group['area'])})
                continue

            # *10.4.1.1         Yes         SPF,StrictSPF 16000      8000         Label
            # 10.16.2.2         Yes         SPF,StrictSPF 16000      8000         Label
            m = p3.match(line)
            if m:
                group = m.groupdict()

                router_entry_dict = router_dict.setdefault('routers', {}).setdefault(group['router_id'], {})
                router_entry_dict.update({'router_id': group['router_id']})
                router_entry_dict.update({'sr_capable': group['sr_capable']})

                if group['sr_algorithm']:
                    router_entry_dict.update({'sr_algorithm': group['sr_algorithm']})

                if group['srgb_base']:
                    router_entry_dict.update({'srgb_base': int(group['srgb_base'])})

                if group['srgb_range']:
                    router_entry_dict.update({'srgb_range': int(group['srgb_range'])})

                if group['sid_label']:
                    router_entry_dict.update({'sid_label': group['sid_label']})
                continue

        return ret_dict

# ==========================================
# Parser for 'show ip ospf segment-routing'
# ==========================================

class ShowIpOspfSegmentRoutingSchema(MetaParser):

    ''' Schema for show ip ospf segment-routing
    '''

    schema = {
        'process_id': {
            Any(): {
                'router_id': str,
                Optional('global_segment_routing_state'): str,
                Optional('segment_routing_enabled'): {
                    'area': {
                        Any(): {
                            'topology_name': str,
                            'forwarding': str,
                            'strict_spf': str
                        }
                    }
                },
                'sr_attributes': {
                    'sr_label_preferred': bool,
                    'advertise_explicit_null': bool,
                },
                Optional('global_block_srgb'): {
                    'range': {
                        'start': int,
                        'end': int
                    },
                    'state': str,
                },
                Optional('local_block_srlb'): {
                    'range': {
                        'start': int,
                        'end': int
                    },
                    'state': str,
                },
                Optional('registered_with'): {
                    Any(): {
                        Optional('client_handle'): int,
                        Optional('sr_algo'): {
                            Any(): {
                                Any(): {
                                    'handle': str,
                                    'bit_mask': str,
                                }
                            }
                        },
                        Optional('client_id'): int,
                    }
                },
                Optional('max_labels'): {
                    'platform': int,
                    'available': int,
                    'pushed_by_ospf': {
                        'uloop_tunnels': int,
                        'ti_lfa_tunnels': int
                    }
                },
                'mfi_label_reservation_ack_pending': bool,
                'bind_retry_timer_running': bool,
                Optional('bind_retry_timer_left'): str,
                Optional('adj_label_bind_retry_timer_running'): bool,
                Optional('adj_label_bind_retry_timer_left'): str,
                Optional('srp_app_locks_requested'): {
                    'srgb': int,
                    'srlb': int
                },
                Optional('teapp'): {
                    'te_router_id': str
                }
            }
        }
    }

class ShowIpOspfSegmentRouting(ShowIpOspfSegmentRoutingSchema):
    ''' Parser for show ip ospf segment-routing
    '''

    cli_command = 'show ip ospf segment-routing'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output
        
        # OSPF Router with ID (10.16.2.2) (Process ID 65109)
        p1 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>\S+)\) +\('
                         r'Process +ID +(?P<process_id>\d+)\)$')

        # Global segment-routing state: Enabled
        p2 = re.compile(r'^Global +segment\-routing +state: +'
                         r'(?P<global_segment_routing_state>\S+)$')
        
        # Prefer non-SR (LDP) Labels
        p3 = re.compile(r'^Prefer +non\-SR +\(LDP\) +Labels$')

        # Do not advertise Explicit Null
        p4 = re.compile(r'^Do +not +advertise +Explicit +Null$')

        # Global Block (SRGB):
        p5 = re.compile(r'^Global +Block +\(SRGB\):$')

        # Range: 16000 - 23999
        p6 = re.compile(r'^Range: +(?P<start>\d+) +\- +(?P<end>\d+)$')

        # State: Created
        p7 = re.compile(r'^State: +(?P<state>\S+)$')

        # Local Block (SRLB):
        p8 = re.compile(r'^Local +Block +\(SRLB\):$')

        # Registered with SR App, client handle: 2
        p9 = re.compile(r'^Registered +with +(?P<app_name>[\S\s]+), +'
                         r'client +handle: +(?P<client_handle>\d+)$')

        # SR algo 0 Connected map notifications active (handle 0x0), bitmask 0x1
        p10 = re.compile(r'^SR +algo +(?P<algo>\d+) +(?P<notifications>[\S\s]+) +\('
                          r'handle +(?P<handle>\w+)\), +bitmask +(?P<bitmask>\w+)$')

        # Registered with MPLS, client-id: 100
        p12 = re.compile(r'^Registered +with +(?P<app_name>[\S\s]+), +client\-id: +'
                          r'(?P<client_id>\d+)$')

        # Max labels: platform 16, available 13
        p13 = re.compile(r'^Max +labels: +platform +(?P<platform>\d+), available +(?P<available>\d+)$')

        # Max labels pushed by OSPF: uloop tunnels 10, TI-LFA tunnels 10
        p14 = re.compile(r'^Max +labels +pushed +by +OSPF: +uloop +tunnels +(?P<uloop_tunnels>\d+)'
                          r', +TI\-LFA +tunnels +(?P<ti_lfa_tunnels>\d+)$')

        # mfi label reservation ack not pending
        p15 = re.compile(r'^mfi +label +reservation +ack +not +pending$')

        # Bind Retry timer not running
        p16 = re.compile(r'^Bind +Retry +timer +not +running$')
        
        # Bind Retry timer running, left ???
        p16_1 = re.compile(r'^Bind +Retry +timer +running, +left +(?P<bind_retry_timer_left>\S+)$')

        # Adj Label Bind Retry timer not running
        p17 = re.compile(r'^Adj +Label +Bind +Retry +timer +not +running$')

        # Adj Label Bind Retry timer running, left ???
        p17_1 = re.compile(r'^Adj +Label +Bind +Retry +timer +running, +left +(?P<adj_label_bind_retry_timer_left>\S+)$')

        # sr-app locks requested: srgb 0, srlb 0
        p18 = re.compile(r'^sr\-app +locks +requested: +srgb +(?P<srgb>\d+), +srlb +(?P<srlb>\d+)$')

        # TE Router ID 10.16.2.2
        p19 = re.compile(r'^TE +Router +ID +(?P<te_router_id>\S+)$')

        # Area Topology name Forwarding Strict SPF
        p20 = re.compile(r'^Area +Topology +name +Forwarding +Strict +SPF$')

        # 8    Base             MPLS          Capable
        # AS external    Base             MPLS          Not applicable
        p21 = re.compile(r'^(?P<area>(\d+|(\w+ +\w+))) +(?P<topology_name>\w+)'
                         r' +(?P<forwarding>\w+) +(?P<strict_spf>\w+( +\w+)?)$')
        
        # initial variables
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.16.2.2) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                router_id = group['router_id']
                process_id = int(group['process_id'])
                process_id_dict = ret_dict.setdefault('process_id', {}). \
                                    setdefault(process_id, {})
                process_id_dict.update({'router_id': router_id})
                sr_attributes_dict = process_id_dict.setdefault('sr_attributes', {})
                sr_attributes_dict.update({'sr_label_preferred': True})
                sr_attributes_dict.update({'advertise_explicit_null': True})
                process_id_dict.update({'mfi_label_reservation_ack_pending': True})
                process_id_dict.update({'bind_retry_timer_running': True})
                process_id_dict.update({'adj_label_bind_retry_timer_running': True})
                continue
            
            # Global segment-routing state: Enabled
            m = p2.match(line)
            if m:
                group = m.groupdict()
                global_segment_routing_state = group['global_segment_routing_state']
                process_id_dict.update({'global_segment_routing_state': global_segment_routing_state})
                continue
            
            # Prefer non-SR (LDP) Labels
            m = p3.match(line)
            if m:
                group = m.groupdict()
                sr_attributes_dict = process_id_dict.setdefault('sr_attributes', {})
                sr_attributes_dict.update({'sr_label_preferred': False})
                continue
            
            # Do not advertise Explicit Null
            m = p4.match(line)
            if m:
                group = m.groupdict()
                sr_attributes_dict = process_id_dict.setdefault('sr_attributes', {})
                sr_attributes_dict.update({'advertise_explicit_null': False})
                continue
            
            # Global Block (SRGB):
            m = p5.match(line)
            if m:
                group = m.groupdict()
                block_dict = process_id_dict.setdefault('global_block_srgb', {})
                continue
            
            # Range: 16000 - 23999
            m = p6.match(line)
            if m:
                group = m.groupdict()
                range_dict = block_dict.setdefault('range', {})
                range_dict.update({'start': int(group['start'])})
                range_dict.update({'end': int(group['end'])})
                continue
            
            # State: Created
            m = p7.match(line)
            if m:
                group = m.groupdict()
                state = group['state']
                block_dict.update({'state': state})
                continue
            
            # Local Block (SRLB):
            m = p8.match(line)
            if m:
                group = m.groupdict()
                block_dict = process_id_dict.setdefault('local_block_srlb', {})
                continue
            
            # Registered with SR App, client handle: 2
            m = p9.match(line)
            if m:
                group = m.groupdict()
                app_name = group['app_name']
                client_handle = int(group['client_handle'])
                registered_with_sr_app_dict = process_id_dict.setdefault('registered_with', {}). \
                                                setdefault(app_name, {})
                registered_with_sr_app_dict.update({'client_handle': client_handle})
                continue
            
            # SR algo 0 Connected map notifications active (handle 0x0), bitmask 0x1
            # SR algo 0 Active policy map notifications active (handle 0x2), bitmask 0xC
            m = p10.match(line)
            if m:
                group = m.groupdict()
                algo = int(group['algo'])
                notifications = group['notifications'].lower().replace(' ', '_')
                handle = group['handle']
                bitmask = group['bitmask']

                sr_algo_dict = registered_with_sr_app_dict.setdefault('sr_algo', {}). \
                                setdefault(algo, {}). \
                                setdefault(notifications, {})
                
                sr_algo_dict.update({'handle': handle})
                sr_algo_dict.update({'bit_mask': bitmask})
                continue
            
            # Registered with MPLS, client-id: 100
            m = p12.match(line)
            if m:
                group = m.groupdict()
                app_name = group['app_name']
                client_id = int(group['client_id'])
                registered_with_mpls_dict = process_id_dict.setdefault('registered_with', {}). \
                                                setdefault(app_name, {})
                registered_with_mpls_dict.update({'client_id': client_id})
                continue
            
            # Max labels: platform 16, available 13
            m = p13.match(line)
            if m:
                group = m.groupdict()
                platform = int(group['platform'])
                available = int(group['available'])
                match_labels_dict = process_id_dict.setdefault('max_labels', {})
                match_labels_dict.update({'platform': platform})
                match_labels_dict.update({'available': available})
                continue
            
            # Max labels pushed by OSPF: uloop tunnels 10, TI-LFA tunnels 10
            m = p14.match(line)
            if m:
                group = m.groupdict()
                uloop_tunnels = int(group['uloop_tunnels'])
                ti_lfa_tunnels = int(group['ti_lfa_tunnels'])
                match_labels_dict = process_id_dict.setdefault('max_labels', {})
                pushed_by_ospf_dict = match_labels_dict.setdefault('pushed_by_ospf', {})
                pushed_by_ospf_dict.update({'uloop_tunnels': uloop_tunnels})
                pushed_by_ospf_dict.update({'ti_lfa_tunnels': ti_lfa_tunnels})
                continue

            # mfi label reservation ack not pending
            m = p15.match(line)
            if m:
                process_id_dict.update({'mfi_label_reservation_ack_pending': False})
                continue

            # Bind Retry timer not running
            m = p16.match(line)
            if m:
                process_id_dict.update({'bind_retry_timer_running': False})
                continue
            
            # Bind Retry timer running, left ???
            m = p16_1.match(line)
            if m:
                group = m.groupdict()
                bind_retry_timer_left = group['bind_retry_timer_left']
                process_id_dict.update({'bind_retry_timer_left': bind_retry_timer_left})
                continue

            # Adj Label Bind Retry timer not running
            m = p17.match(line)
            if m:
                process_id_dict.update({'adj_label_bind_retry_timer_running': False})
                continue
            
            # adj_label_bind_retry_timer_left
            m = p17_1.match(line)
            if m:
                group = m.groupdict()
                adj_label_bind_retry_timer_left = group['adj_label_bind_retry_timer_left']
                process_id_dict.update({'adj_label_bind_retry_timer_left': adj_label_bind_retry_timer_left})
                continue

            # sr-app locks requested: srgb 0, srlb 0
            m = p18.match(line)
            if m:
                group = m.groupdict()
                srgb = int(group['srgb'])
                srlb = int(group['srlb'])
                srp_app_locks_requested_dict = process_id_dict.setdefault('srp_app_locks_requested', {})
                srp_app_locks_requested_dict.update({'srgb': srgb})
                srp_app_locks_requested_dict.update({'srlb': srlb})
                continue
            
            # TE Router ID 10.16.2.2
            m = p19.match(line)
            if m:
                group = m.groupdict()
                te_router_id = group['te_router_id']
                process_id_dict.setdefault('teapp', {}). \
                    update({'te_router_id': te_router_id})
                continue

            # Area Topology name Forwarding Strict SPF
            m = p20.match(line)
            if m:
                segment_routing_enabled_dict = process_id_dict.setdefault('segment_routing_enabled', {})
                continue

            # 8    Base             MPLS          Capable
            # AS external    Base             MPLS          Not applicable
            m = p21.match(line)
            if m:
                group = m.groupdict()
                area = group['area']
                if area.isdigit():
                    area = str(IPAddress(str(area), flags=INET_ATON))
                topology_name = group['topology_name']
                forwarding = group['forwarding']
                strict_spf = group['strict_spf']
                area_dict = segment_routing_enabled_dict.setdefault('area', {}). \
                             setdefault(area, {})
                area_dict.update({'topology_name' : topology_name})
                area_dict.update({'forwarding' : forwarding})
                area_dict.update({'strict_spf' : strict_spf})
                continue
        
        return ret_dict



# ================================
# Super parser for:
#   * 'show ip ospf virtual-links'
#   * 'show ip ospf sham-links'
# ================================
class ShowIpOspfLinksParser2(MetaParser):

    ''' Parser for:
        * 'show ip ospf virtual-links __'
        * 'show ip ospf sham-links __'
    '''

    def cli(self, cmd, link_type,output=None):

        assert link_type in ['virtual_links', 'sham_links']

        if output is None:
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        ret_dict = {}
        af = 'ipv4'

        # crypo_algorithm dict
        crypto_dict = {'cryptographic': 'md5', 'simple password': 'simple'}

        # Sham Link OSPF_SL0 to address 10.151.22.22 is up
        # Virtual Link OSPF_VL0 to router 10.64.4.4 is up
        p1 = re.compile(r'^(Virtual|Sham) +Link +(?P<interface>(\S+)) +to'
                            r' +(address|router) +(?P<address>(\S+)) +is'
                            r' +(?P<link_state>(up|down))$')

        # Area 1, source address 10.21.33.33
        # Area 1 source address 10.229.11.11
        p2 = re.compile(r'^Area +(?P<area>(\S+)),? +source +address'
                            r' +(?P<source_address>(\S+))$')
        
        # Run as demand circuit
        p3 = re.compile(r'^Run +as +demand +circuit$')

        # DoNotAge LSA not allowed (Number of DCbitless LSA is 7).
        # DoNotAge LSA not allowed (Number of DCbitless LSA is 1). Cost of using 111 State POINT_TO_POINT,
        p4 = re.compile(r'^DoNotAge +LSA +not +allowed'
                            r' +\(Number +of +DCbitless +LSA +is +(?P<dcbitless>(\d+))\).'
                            r'(?: +Cost +of +using +(?P<cost>(\d+)))?'
                            r'(?: State +(?P<state>(\S+)))?$')

        # Transit area 1
        # Transit area 1, via interface GigabitEthernet0/1
        p5 = re.compile(r'^Transit +area +(?P<area>(\S+)),'
                            r'(?: +via +interface +(?P<intf>(\S+)))?$')

        # Topology-MTID    Cost    Disabled     Shutdown      Topology Name
        #             0       1          no           no               Base
        p6 = re.compile(r'^(?P<mtid>(\d+)) +(?P<topo_cost>(\d+))'
                            r' +(?P<disabled>(yes|no)) +(?P<shutdown>(yes|no))'
                            r' +(?P<topo_name>(\S+))$')

        # Transmit Delay is 1 sec, State POINT_TO_POINT,
        p7 = re.compile(r'^Transmit +Delay +is +(?P<transmit_delay>(\d+))'
                            r' +sec, +State +(?P<state>(\S+)),?$')

        # Timer intervals configured, Hello 3, Dead 13, Wait 13, Retransmit 5
        # Timer intervals configured, Hello 4, Dead 16, Wait 16, Retransmit 44
        # Timer intervals configured, Hello 10, Dead 40, Wait 40,
        p8 = re.compile(r'^Timer +intervals +configured,'
                            r' +Hello +(?P<hello>(\d+)),'
                            r' +Dead +(?P<dead>(\d+)),'
                            r' +Wait +(?P<wait>(\d+)),'
                            r'(?: +Retransmit +(?P<retransmit>(\d+)))?$')

        # Strict TTL checking enabled, up to 3 hops allowed
        p9 = re.compile(r'^Strict +TTL +checking'
                            r' +(?P<strict_ttl>(enabled|disabled))'
                            r'(?:, +up +to +(?P<hops>(\d+)) +hops +allowed)?$')

        # Hello due in 00:00:03:179
        p10 = re.compile(r'^Hello +due +in +(?P<hello_timer>(\S+))$')

        # Adjacency State FULL
        p11 = re.compile(r'^Adjacency +State +(?P<adj_state>(\S+))$')

        # Index 1/2/2, retransmission queue length 0, number of retransmission 2
        p12 = re.compile(r'^Index +(?P<index>(\S+)), +retransmission +queue'
                            r' +length +(?P<length>(\d+)), +number +of'
                            r' +retransmission +(?P<retrans>(\d+))$')
        
        # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
        p13 = re.compile(r'^First +(?P<first>(\S+)) +Next +(?P<next>(\S+))$')

        # Last retransmission scan length is 1, maximum is 1
        p14 = re.compile(r'^Last +retransmission +scan +length +is'
                            r' +(?P<len>(\d+)), +maximum +is +(?P<max>(\d+))$')

        # Last retransmission scan time is 0 msec, maximum is 0 msec
        p15 = re.compile(r'^Last +retransmission +scan +time +is'
                            r' +(?P<time>(\d+)) +msec, +maximum +is'
                            r' +(?P<max>(\d+)) +msec$')

        for line in out.splitlines():
            line = line.strip()

            # Sham Link OSPF_SL0 to address 10.151.22.22 is up
            # Virtual Link OSPF_VL0 to router 10.64.4.4 is up
            m = p1.match(line)
            if m:
                address = str(m.groupdict()['address'])
                sl_remote_id = vl_router_id = address
                interface = str(m.groupdict()['interface'])
                link_state = str(m.groupdict()['link_state'])

                n = re.match(r'(?P<ignore>\S+)_(?P<name>(S|V)L(\d+))', interface)
                if n:
                    real_link_name = str(n.groupdict()['name'])
                else:
                    real_link_name = interface

                # Build dict
                if 'address_family' not in ret_dict:
                    ret_dict['address_family'] = {}
                if af not in ret_dict['address_family']:
                    ret_dict['address_family'][af] = {}
                continue

            # Area 1, source address 10.21.33.33
            # Area 1 source address 10.229.11.11
            m = p2.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))
                source_address = str(m.groupdict()['source_address'])

                # Set link_name for sham_link
                link_name = '{} {}'.format(source_address, sl_remote_id)

                # Build dict
                if 'areas' not in ret_dict['address_family'][af]:
                    ret_dict['address_family'][af]['areas'] = {}
                if area not in ret_dict['address_family'][af]['areas']:
                    ret_dict['address_family'][af]['areas'][area] = {}
                if link_type not in  ret_dict['address_family'][af]['areas'][area]:
                    ret_dict['address_family'][af]['areas'][area][link_type] = {}
                if link_name not in ret_dict['address_family'][af]['areas'][area][link_type]:
                    ret_dict['address_family'][af]['areas'][area][link_type][link_name] = {}

                # Set sub_dict
                sub_dict = ret_dict['address_family'][af]['areas'][area]\
                            [link_type][link_name]

                # Set values
                sub_dict['transit_area_id'] = area
                sub_dict['local_id'] = source_address
                sub_dict['demand_circuit'] = False

                # Set previously parsed values
                try:
                    sub_dict['name'] = real_link_name
                    sub_dict['remote_id'] = sl_remote_id
                    sub_dict['link_state'] = link_state
                except Exception:
                    pass
                continue

            # Run as demand circuit
            m = p3.match(line)
            if m:
                if link_type == 'sham_links':
                    sub_dict['demand_circuit'] = True
                else:
                    demand_circuit = True
                continue

            # DoNotAge LSA not allowed (Number of DCbitless LSA is 7).
            # DoNotAge LSA not allowed (Number of DCbitless LSA is 1). Cost of using 111 State POINT_TO_POINT,
            m = p4.match(line)
            if m:
                dcbitless_lsa_count = int(m.groupdict()['dcbitless'])
                donotage_lsa = 'not allowed'
                if m.groupdict()['cost']:
                    cost = int(m.groupdict()['cost'])
                if m.groupdict()['state']:
                    link_state =  str(m.groupdict()['state']).lower()

                # Set values for sham_links
                if link_type == 'sham_links':
                    sub_dict['dcbitless_lsa_count'] = dcbitless_lsa_count
                    sub_dict['donotage_lsa'] = donotage_lsa
                    if m.groupdict()['cost']:
                        sub_dict['cost'] = cost
                    if m.groupdict()['state']:
                        sub_dict['state'] = link_state
                    continue

            # Transit area 1
            # Transit area 1, via interface GigabitEthernet0/1
            m = p5.match(line)
            if m:
                area = str(IPAddress(str(m.groupdict()['area']), flags=INET_ATON))

                # Set link_name for virtual_link
                link_name = '{} {}'.format(area, vl_router_id)

                # Create dict
                if 'areas' not in ret_dict['address_family'][af]:
                    ret_dict['address_family'][af]['areas'] = {}
                if area not in ret_dict['address_family'][af]['areas']:
                    ret_dict['address_family'][af]['areas'][area] = {}
                if link_type not in  ret_dict['address_family'][af]['areas'][area]:
                    ret_dict['address_family'][af]['areas'][area][link_type] = {}
                if link_name not in ret_dict['address_family'][af]['areas'][area][link_type]:
                    ret_dict['address_family'][af]['areas'][area][link_type][link_name] = {}

                # Set sub_dict
                sub_dict = ret_dict['address_family'][af]['areas'][area]\
                            [link_type][link_name]

                # Set values
                sub_dict['transit_area_id'] = area
                sub_dict['demand_circuit'] = False
                if m.groupdict()['intf']:
                    sub_dict['interface'] = str(m.groupdict()['intf'])

                # Set previously parsed values
                try:
                    sub_dict['name'] = real_link_name
                except Exception:
                    pass
                try:
                    sub_dict['router_id'] = vl_router_id
                except Exception:
                    pass
                try:
                    sub_dict['dcbitless_lsa_count'] = dcbitless_lsa_count
                except Exception:
                    pass
                try:
                    sub_dict['donotage_lsa'] = donotage_lsa
                except Exception:
                    pass
                try:
                    sub_dict['demand_circuit'] = demand_circuit
                except Exception:
                    pass
                try:
                    sub_dict['link_state'] = link_state
                except Exception:
                    pass
                continue

            # Topology-MTID    Cost    Disabled     Shutdown      Topology Name
            #             0       1          no           no               Base
            m = p6.match(line)
            if m:
                mtid = int(m.groupdict()['mtid'])
                if 'topology' not in sub_dict:
                    sub_dict['topology'] = {}
                if mtid not in sub_dict['topology']:
                    sub_dict['topology'][mtid] = {}
                sub_dict['topology'][mtid]['cost'] = int(m.groupdict()['topo_cost'])
                sub_dict['topology'][mtid]['name'] = str(m.groupdict()['topo_name'])
                if 'yes' in m.groupdict()['disabled']:
                    sub_dict['topology'][mtid]['disabled'] = True
                else:
                    sub_dict['topology'][mtid]['disabled'] = False
                if 'yes' in m.groupdict()['shutdown']:
                    sub_dict['topology'][mtid]['shutdown'] = True
                else:
                    sub_dict['topology'][mtid]['shutdown'] = False
                    continue
            
            # Transmit Delay is 1 sec, State POINT_TO_POINT,
            m = p7.match(line)
            if m:
                sub_dict['transmit_delay'] = int(m.groupdict()['transmit_delay'])
                state = str(m.groupdict()['state']).lower()
                state = state.replace("_", "-")
                sub_dict['state'] = state
                continue

            # Timer intervals configured, Hello 3, Dead 13, Wait 13, Retransmit 5
            # Timer intervals configured, Hello 4, Dead 16, Wait 16, Retransmit 44
            # Timer intervals configured, Hello 10, Dead 40, Wait 40,
            m = p8.match(line)
            if m:
                if m.groupdict()['hello']:
                    sub_dict['hello_interval'] = int(m.groupdict()['hello'])
                if m.groupdict()['dead']:
                    sub_dict['dead_interval'] = int(m.groupdict()['dead'])
                if m.groupdict()['wait']:
                    sub_dict['wait_interval'] = int(m.groupdict()['wait'])
                if m.groupdict()['retransmit']:
                    sub_dict['retransmit_interval'] = int(m.groupdict()['retransmit'])
                continue

            # Strict TTL checking enabled, up to 3 hops allowed
            m = p9.match(line)
            if m:
                if 'ttl_security' not in sub_dict:
                    sub_dict['ttl_security'] = {}
                if 'enabled' in m.groupdict()['strict_ttl']:
                    sub_dict['ttl_security']['enable'] = True
                else:
                    sub_dict['ttl_security']['enable'] = False
                if m.groupdict()['hops']:
                    sub_dict['ttl_security']['hops'] = int(m.groupdict()['hops'])
                    continue

            # Hello due in 00:00:03:179
            m = p10.match(line)
            if m:
                sub_dict['hello_timer'] = str(m.groupdict()['hello_timer'])
                continue          
          
            # Adjacency State FULL
            m = p11.match(line)
            if m:
                sub_dict['adjacency_state'] = str(m.groupdict()['adj_state']).lower()
                continue

            # Index 1/2/2, retransmission queue length 0, number of retransmission 2
            m = p12.match(line)
            if m:
                sub_dict['index'] = str(m.groupdict()['index'])
                sub_dict['retrans_qlen'] = int(m.groupdict()['length'])
                sub_dict['total_retransmission'] = int(m.groupdict()['retrans'])
                continue

            # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
            m = p13.match(line)
            if m:
                sub_dict['first'] = str(m.groupdict()['first'])
                sub_dict['next'] = str(m.groupdict()['next'])
                continue

            # Last retransmission scan length is 1, maximum is 1
            m = p14.match(line)
            if m:
                sub_dict['last_retransmission_scan_length'] = \
                    int(m.groupdict()['len'])
                sub_dict['last_retransmission_max_length'] = \
                    int(m.groupdict()['max'])
                continue

            # Last retransmission scan time is 0 msec, maximum is 0 msec
            m = p15.match(line)
            if m:
                sub_dict['last_retransmission_scan_time'] = \
                    int(m.groupdict()['time'])
                sub_dict['last_retransmission_max_scan'] = \
                    int(m.groupdict()['max'])
                continue

        return ret_dict


# =============================
# Schema for:
#   * 'show ip ospf sham-links'
# =============================
class ShowIpOspfShamLinks2Schema(MetaParser):

    ''' Schema for:
        * 'show ip ospf sham-links __'
    '''

    schema =   {'address_family':
                    {Any():
                        {'areas':
                            {Any():
                                {'sham_links':
                                    {Any():
                                        {'name': str,
                                        'link_state': str,
                                        'local_id': str,
                                        'remote_id': str,
                                        'transit_area_id': str,
                                        Optional('hello_interval'): int,
                                        Optional('dead_interval'): int,
                                        Optional('wait_interval'): int,
                                        Optional('retransmit_interval'): int,
                                        Optional('transmit_delay'): int,
                                        'cost': int,
                                        'state': str,
                                        Optional('hello_timer'): str,
                                        Optional('demand_circuit'): bool,
                                        Optional('dcbitless_lsa_count'): int,
                                        Optional('donotage_lsa'): str,
                                        Optional('adjacency_state'): str,
                                        Optional('ttl_security'):
                                            {'enable': bool,
                                            Optional('hops'): int},
                                            Optional('index'): str,
                                            Optional('first'): str,
                                            Optional('next'): str,
                                            Optional('last_retransmission_max_length'): int,
                                            Optional('last_retransmission_max_scan'): int,
                                            Optional('last_retransmission_scan_length'): int,
                                            Optional('last_retransmission_scan_time'): int,
                                            Optional('total_retransmission'): int,
                                            Optional('retrans_qlen'): int,
                                            Optional('topology'):
                                                {Any():
                                                    {'cost': int,
                                                    'disabled': bool,
                                                    'shutdown': bool,
                                                    'name': str,
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    }


# =============================
# Parser for:
#   * 'show ip ospf sham-links'
# =============================
class ShowIpOspfShamLinks2(ShowIpOspfShamLinks2Schema, ShowIpOspfLinksParser2):

    ''' Parser for:
        * 'show ip ospf sham-links __'
    '''

    cli_command = 'show ip ospf sham-links __'

    def cli(self, output=None):

        return super().cli(cmd=self.cli_command, link_type='sham_links',output=output)


# ================================
# Schema for:
#   * 'show ip ospf virtual-links'
# ================================
class ShowIpOspfVirtualLinks2Schema(MetaParser):

    ''' Schema for:
        * 'show ip ospf virtual-links __'
    '''

    schema = {  
                'address_family':
                    {Any():
                        {'areas':
                            {Any():
                                {'virtual_links':
                                    {Any():
                                        {'name': str,
                                        'link_state': str,
                                        'router_id': str,
                                        'transit_area_id': str,
                                        Optional('hello_interval'): int,
                                        Optional('dead_interval'): int,
                                        Optional('wait_interval'): int,
                                        Optional('retransmit_interval'): int,
                                        'transmit_delay': int,
                                        'state': str,
                                        'demand_circuit': bool,
                                        Optional('cost'): int,
                                        Optional('hello_timer'): str,
                                        Optional('interface'): str,
                                        Optional('dcbitless_lsa_count'): int,
                                        Optional('donotage_lsa'): str,
                                        Optional('adjacency_state'): str,
                                        Optional('ttl_security'):
                                            {'enable': bool,
                                            Optional('hops'): int},
                                            Optional('index'): str,
                                            Optional('first'): str,
                                            Optional('next'): str,
                                            Optional('last_retransmission_max_length'): int,
                                            Optional('last_retransmission_max_scan'): int,
                                            Optional('last_retransmission_scan_length'): int,
                                            Optional('last_retransmission_scan_time'): int,
                                            Optional('total_retransmission'): int,
                                            Optional('retrans_qlen'): int,
                                            Optional('topology'):
                                                {Any():
                                                    {'cost': int,
                                                    'disabled': bool,
                                                    'shutdown': bool,
                                                    'name': str,
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    }

# ================================
# Parser for:
#   * 'show ip ospf virtual-links'
# ================================
class ShowIpOspfVirtualLinks2(ShowIpOspfVirtualLinks2Schema, ShowIpOspfLinksParser2):

    ''' Parser for:
        * 'show ip ospf virtual-links __'
    '''

    cli_command = 'show ip ospf virtual-links __'

    def cli(self, output=None):

        return super().cli(cmd=self.cli_command, link_type='virtual_links', output=output)

# ===========================
# Schema for:
#   * 'show ipv6 ospf neighbor'
#   * 'show ipv6 ospf neighbor {interface}'
# ===========================
class ShowIpv6OspfNeighborSchema(MetaParser):

    ''' Schema for:
        * 'show ipv6 ospf neighbor'
        * 'show ipv6 ospf neighbor {interface}'
    '''

    schema = {
        'interfaces':
            {Any():
                {'neighbors':
                    {Any():
                        {'priority': int,
                        'state': str,
                        'dead_time': str,
                        'interface_id': int,
                        },
                    },
                },
            },
        }

# ===========================
# Parser for:
#   * 'show ipv6 ospf neighbor'
#   * 'show ipv6 ospf neighbor {interface}'
# ===========================
class ShowIpv6OspfNeighbor(ShowIpv6OspfNeighborSchema):
    ''' Parser for:
        * 'show ipv6 ospf neighbor'
        * 'show ipv6 ospf neighbor {interface}'
    '''
    cli_command = [
        'show ipv6 ospf neighbor {interface}',
        'show ipv6 ospf neighbor']
    exclude = ['dead_time']

    def cli(self, interface='', output=None):

        if output is None:
            # Execute command on device
            if interface:
                output = self.device.execute(self.cli_command[0].format(interface=interface))
            else:
                output = self.device.execute(self.cli_command[1])

        # Init vars
        ret_dict = {}

        # Neighbor ID     Pri   State           Dead Time   Interface ID   Interface
        # 172.16.197.253 128   FULL/DR         00:00:30          21       GigabitEthernet0/0/1
        # 10.169.197.252   0   FULL/  -        00:00:36          23       GigabitEthernet2

        p1 = re.compile(r'^(?P<neighbor>\S+) +(?P<pri>\d+) +(?P<state>\S+(?:\s+\S+)?)'
                        r' +(?P<dead_time>\S+) +(?P<interface_id>\S+) +(?P<interface>\S+)$')

        for line in output.splitlines():

            line = line.strip()
            m = p1.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                interface = m.groupdict()['interface']

                # Build Dict

                intf_dict = ret_dict.setdefault('interfaces', {}).setdefault(interface, {})
                nbr_dict = intf_dict.setdefault('neighbors', {}).setdefault(neighbor, {})

                # Set values
                nbr_dict['priority'] = int(m.groupdict()['pri'])
                nbr_dict['state'] = str(m.groupdict()['state'])
                nbr_dict['dead_time'] = str(m.groupdict()['dead_time'])
                nbr_dict['interface_id'] = int(m.groupdict()['interface_id'])
                continue

        return ret_dict

class ShowIpOspfNsrSchema(MetaParser):
    """Schema for show ip ospf nsr"""

    schema = {
        'redundancy_state': str,
        'peer_redundancy_state': str,
        'ospf_num': int,
        'ospf_id': str,
        'sequence_num': int,
        'sync_operations': int,
        'check_time': str,
        'check_date': str,
        'lsa_count': int,
        'checksum': str,
    }


class ShowIpOspfNsr(ShowIpOspfNsrSchema):
    """Parser for show ip ospf nsr"""

    cli_command = 'show ip ospf nsr'

    def cli(self, output=None):
        if output is None:
            output = self.device.execute(self.cli_command)

        # Redundancy state: ACTIVE
        p1 = re.compile(r"^Redundancy\s+state:\s+(?P<redundancy_state>\w+)$")
        
        # Peer redundancy state: STANDBY HOT
        p2 = re.compile(r"^Peer\s+redundancy\s+state:\s+(?P<peer_redundancy_state>\S+\s+\S+)$")
        
        # Routing Process "ospf 50" with ID 2.200.1.2
        p3 = re.compile(r"^Routing\s+Process\s+\"ospf\s+(?P<ospf_num>\d+)\"\s+with\s+ID\s+(?P<ospf_id>(\d{1,3}\.){3}\d{1,3})$")
        
        # Checkpoint message sequence number: 12358
        p4 = re.compile(r"^Checkpoint\s+message\s+sequence\s+number:\s+(?P<sequence_num>\d+)$")
        
        # Bulk sync operations:  1
        p5 = re.compile(r"^Bulk\s+sync\s+operations:\s+(?P<sync_operations>\d+)$")
        
        # Next sync check time:  20:29:44.061 IST Thu Oct 6 2022
        p6 = re.compile(r"^Next\s+sync\s+check\s+time:\s+(?P<check_time>\S+)\s+(?P<check_date>\S+\s+\S+\s+\S+\s+\S+\s+\S+)$")
        
        # LSA Count: 60, Checksum Sum 0x001DF372
        p7 = re.compile(r"^LSA\s+Count:\s+(?P<lsa_count>\d+),\s+Checksum\s+Sum\s+(?P<checksum>\S+)$")

        ret_dict = {}

        for line in output.splitlines():
            line = line.strip()

            # Redundancy state: ACTIVE
            match_obj = p1.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['redundancy_state'] = dict_val['redundancy_state']
                continue

            # Peer redundancy state: STANDBY HOT
            match_obj = p2.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['peer_redundancy_state'] = dict_val['peer_redundancy_state']
                continue

            # Routing Process "ospf 50" with ID 2.200.1.2
            match_obj = p3.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['ospf_num'] = int(dict_val['ospf_num'])
                ret_dict['ospf_id'] = dict_val['ospf_id']
                continue

            # Checkpoint message sequence number: 12358
            match_obj = p4.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['sequence_num'] = int(dict_val['sequence_num'])
                continue
            
            # Bulk sync operations:  1
            match_obj = p5.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['sync_operations'] = int(dict_val['sync_operations'])
                continue

            # Next sync check time:  20:29:44.061 IST Thu Oct 6 2022
            match_obj = p6.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['check_time'] = dict_val['check_time']
                ret_dict['check_date'] = dict_val['check_date']
                continue

            # LSA Count: 60, Checksum Sum 0x001DF372
            match_obj = p7.match(line)
            if match_obj:
                dict_val = match_obj.groupdict()
                ret_dict['lsa_count'] = int(dict_val['lsa_count'])
                ret_dict['checksum'] = dict_val['checksum']
                continue

        return ret_dict

# =================================================================
# Schema for:
#   * 'show ip ospf rib redistribution'
# =================================================================
class ShowIpOspfRibRedistributionSchema(MetaParser):
    """Schema for show ip ospf rib redistribution
    """
    schema = {
        "instance": {
            Any(): {
                "router_id": str,
                "mtid": int,
                Optional("network"): {
                    Any(): {
                        "type": int,
                        "metric": int,
                        "tag": int,
                        "origin": str,
                        Optional("via_network"): str,
                        Optional("interface"): str,
                    }
                },
            }
        }
    }

# ========================================================
# Parser for:
#   * 'Show ip ospf rib redistribution'
# ========================================================
class ShowIpOspfRibRedistribution(ShowIpOspfRibRedistributionSchema):
    """ Parser for show ip ospf rib redistribution
    """
    cli_command = 'show ip ospf rib redistribution'
    
    def cli(self, output=None):
        if output is None:
            output = self.device.execute(self.cli_command)

        # OSPF Router with ID (10.4.1.1) (Process ID 100)
        p1 = re.compile(r'OSPF+ Router +with +ID +\((?P<router_id>\S+)\)+\s+\(Process +ID +(?P<instance>\d+)\)')

        # Base Topology (MTID 0)
        p2 = re.compile(r'Base +Topology +\(MTID (?P<mtid>\d+)\)$')

        # 40.0.0.1/32, type 2, metric 20, tag 0, from IS-IS Router
        p3 = re.compile(r'(?P<network>\S+), type (?P<type>\d+), metric (?P<metric>\d+), tag (?P<tag>\d+), from (?P<from>.*)$')
        
        # via 40.60.1.40, Ethernet0/2
        # via Null0
        p4 = re.compile(r'via ((?P<via_network>\S+),)?\s*(?P<interface>\S+)')

        # initial variables
        ret_dict = {}
        for line in output.splitlines():
            line = line.strip()

            # OSPF Router with ID (10.4.1.1) (Process ID 65109)
            m = p1.match(line)
            if m:
                group = m.groupdict()
                router_id = str(IPAddress(group['router_id'], flags=INET_ATON))
                instance = int(group['instance'])

                # Create dict
                process_id_dict = ret_dict.setdefault('instance',{}).\
                                           setdefault(instance,{})
                process_id_dict.update({'router_id': router_id})
                continue

            #         Base Topology (MTID 0)
            m = p2.match(line)
            if m:
                group = m.groupdict()
                mtid = group['mtid']
                process_id_dict.update({'mtid': int(mtid)}) 
                continue

            # 40.0.0.1/32, type 2, metric 20, tag 0, from IS-IS Router
            m = p3.match(line)
            if m:
                group = m.groupdict()
                network = group['network']
                type = group['type']
                metric = group['metric']
                tag = group['tag']
                origin = group['from']
                network_dict = process_id_dict.setdefault('network',{}).setdefault(network,{})
                network_dict.update(type= int(type), metric = int(metric), tag = int(tag), origin = origin)                
                continue

            #  via 40.60.1.40, Ethernet0/2
            m = p4.match(line)
            if m:
                group = m.groupdict()
                via_network = group['via_network']
                interface= group['interface']
                interface= group['interface']
                if via_network is not None:
                    network_dict.update({'via_network': str(IPAddress(via_network, flags=INET_ATON))})
                else:
                    network_dict.update({'via_network': 'None'})
                 
                network_dict.update({'interface': interface})
                continue

        return ret_dict    


# =================================================================
# Schema for:
#   * 'show ipv6 ospf interface'
# =================================================================

class ShowIpv6OspfInterfaceSchema(MetaParser):
    """ Schema for show ipv6 ospf interface {interface} """

    schema = {
        'interface': {
            Any(): {
                'interface_status': str,
                'line_status': str,
                'connect_status': str,
                'link_local_address': str,
                'interface_id': int,
                'if_index': str,
                'area': int,
                'process_id': int,
                'instance_id': int,
                'router_id': str,
                'network_type': str,
                'cost': int,
                'transmit_delay': str,
                'state': str,
                'timer_intervals': {
                    'hello': int,
                    'dead': int,
                    'wait': int,
                    'retransmit': int,
                    'hello_due': str
                },
                'graceful_restart_helper_support': str,
                'flood_list': {
                    'index': str,
                    'next': str,
                    'flood_queue_length': int,
                    'last_flood_scan': {
                        'scan_length': int,
                        'scan_length_maximum': int,
                        'scan_time_msec': int,
                        'scan_time_maximum_msec': int
                    },
                },
                'neighbor_count': int,
                'adjacent_neighbor_count': int,
                'adjacent_neighbor_address': str,
                'suppressed_hello_neighbor_count': int
            }
        }
    }


# =================================================================
# Parser for:
#   * 'show ipv6 ospf interface'
# =================================================================

class ShowIpv6OspfInterface(ShowIpv6OspfInterfaceSchema):
    """ Parser for show ipv6 ospf interface {interface}"""

    cli_command = 'show ipv6 ospf interface {interface}'

    def cli(self, interface, output=None):
        if output is None:
            cmd = self.cli_command.format(interface=interface)
        
        output = self.device.execute(cmd)

        # TwentyFiveGigE1/0/3 is up, line protocol is up (connected)
        p1 = re.compile(r'^(?P<interface>[\S]+) is (?P<interface_status>[\S]+), line protocol is (?P<line_status>[\S]+)\s+\((?P<connect_status>[\S]+)\)$')

        # Link Local Address FE80::2A7:42FF:FED7:4CFF, Interface ID 5 (snmp-if-index)
        p2 = re.compile(r'^Link Local Address (?P<link_local_address>[\S]+), Interface ID (?P<interface_id>[\d]+)\s+\((?P<if_index>[\S]+)\)$')

        # Area 0, Process ID 1, Instance ID 0, Router ID 109.0.0.1
        p3 = re.compile(r'^Area (?P<area>[\d]+), Process ID (?P<process_id>[\d]+), Instance ID (?P<instance_id>[\d]+), Router ID (?P<router_id>[\S]+)$')

        # Network Type POINT_TO_POINT, Cost: 1
        p4 = re.compile(r'^Network Type (?P<network_type>[\S]+), Cost: (?P<cost>[\d]+)$')
        
        # Transmit Delay is 1 sec, State POINT_TO_POINT
        p5 = re.compile(r'^Transmit Delay is (?P<transmit_delay>[\d\s\w]+), State (?P<state>[\S]+)$')

        # Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
        p6 = re.compile(r'^Timer intervals configured, Hello (?P<hello>[\d]+), Dead (?P<dead>[\d]+), Wait (?P<wait>[\d]+), Retransmit (?P<retransmit>[\d]+)$')

        # Hello due in 00:00:08
        p6_1 = re.compile(r'^Hello due in (?P<hello_due>\S+)$')
        
        # Graceful restart helper support enabled
        p7 = re.compile(r'^Graceful restart helper support (?P<graceful_restart_helper_support>[\S]+)$')

        # Index 1/4/4, flood queue length 0
        p8 = re.compile(r'^Index (?P<index>\S+), flood queue length (?P<flood_queue_length>\d+)$')

        # Next 0x0(0)/0x0(0)/0x0(0)
        p9 = re.compile(r'^Next (?P<next>\S+)$')

        # Last flood scan length is 3, maximum is 3
        p10 = re.compile(r'^Last flood scan length is (?P<scan_length>\d+), maximum is (?P<scan_length_maximum>\d+)$')

        # Last flood scan time is 0 msec, maximum is 0 msec
        p11 = re.compile(r'^Last flood scan time is (?P<scan_time_msec>\d+) msec, maximum is (?P<scan_time_maximum_msec>\d+) msec$')

        # Neighbor Count is 1, Adjacent neighbor count is 1
        p12 = re.compile(r'^Neighbor Count is (?P<neighbor_count>[\d]+), Adjacent neighbor count is (?P<adjacent_neighbor_count>[\d]+)$')

        # Adjacent with neighbor 109.0.0.5
        p13 = re.compile(r'^Adjacent with neighbor (?P<adjacent_neighbor_address>[\S]+)$')

        # Suppress hello for 0 neighbor(s)
        p14 = re.compile(r'^Suppress hello for (?P<suppressed_hello_neighbor_count>\d+) neighbor\(s\)$')
        
        ret_dict ={}

        for line in output.splitlines():
            line = line.strip()

            # TwentyFiveGigE1/0/3 is up, line protocol is up (connected)
            m = p1.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict = ret_dict.setdefault('interface', {}).setdefault(Common.convert_intf_name(dict_val['interface']), {})
                int_dict['interface_status'] = dict_val['interface_status']
                int_dict['line_status'] = dict_val['line_status']
                int_dict['connect_status'] = dict_val['connect_status']
                continue

            # Link Local Address FE80::2A7:42FF:FED7:4CFF, Interface ID 5 (snmp-if-index)
            m = p2.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['link_local_address'] = dict_val['link_local_address']
                int_dict['interface_id'] = int(dict_val['interface_id'])
                int_dict['if_index'] = dict_val['if_index']
                continue
            
            # Area 0, Process ID 1, Instance ID 0, Router ID 109.0.0.1
            m = p3.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['area'] = int(dict_val['area'])
                int_dict['process_id'] = int(dict_val['process_id'])
                int_dict['instance_id'] = int(dict_val['instance_id'])
                int_dict['router_id'] = dict_val['router_id']
                continue
            
            # Network Type POINT_TO_POINT, Cost: 1
            m = p4.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['network_type'] = dict_val['network_type']
                int_dict['cost'] = int(dict_val['cost'])
                continue

            # Transmit Delay is 1 sec, State POINT_TO_POINT
            m = p5.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['transmit_delay'] = dict_val['transmit_delay']
                int_dict['state'] = dict_val['state']
                continue
            
            # Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
            m = p6.match(line)
            if m:
                dict_val = m.groupdict()
                timer_intervals_dict = int_dict.setdefault('timer_intervals', {})
                timer_intervals_dict['hello'] = int(dict_val['hello'])
                timer_intervals_dict['dead'] = int(dict_val['dead'])
                timer_intervals_dict['wait'] = int(dict_val['wait'])
                timer_intervals_dict['retransmit'] = int(dict_val['retransmit'])
                continue

            # Hello due in 00:00:08
            m = p6_1.match(line)
            if m:
                int_dict.setdefault('timer_intervals', {}).setdefault('hello_due', m.groupdict()['hello_due'])
                continue

            # Graceful restart helper support enabled
            m = p7.match(line)
            if m:
                int_dict['graceful_restart_helper_support'] = m.groupdict()['graceful_restart_helper_support']
                continue
            
            # Index 1/4/4, flood queue length 0
            m = p8.match(line)
            if m:
                flood_dict = int_dict.setdefault('flood_list', {})
                flood_dict['index'] = m.groupdict()['index']
                flood_dict['flood_queue_length'] = int(m.groupdict()['flood_queue_length'])
                continue

            # Next 0x0(0)/0x0(0)/0x0(0)
            m = p9.match(line)
            if m:
                flood_dict['next'] = m.groupdict()['next']
                continue

            # Last flood scan length is 3, maximum is 3
            m = p10.match(line)
            if m:
                last_flood_scan_dict = flood_dict.setdefault('last_flood_scan', {})
                last_flood_scan_dict['scan_length'] = int(m.groupdict()['scan_length'])
                last_flood_scan_dict['scan_length_maximum'] = int(m.groupdict()['scan_length_maximum'])
                continue

            # Last flood scan time is 0 msec, maximum is 0 msec
            m = p11.match(line)
            if m:
                last_flood_scan_dict['scan_time_msec'] = int(m.groupdict()['scan_time_msec'])
                last_flood_scan_dict['scan_time_maximum_msec'] = int(m.groupdict()['scan_time_maximum_msec'])
                continue

            # Neighbor Count is 1, Adjacent neighbor count is 1
            m = p12.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['neighbor_count'] = int(dict_val['neighbor_count'])
                int_dict['adjacent_neighbor_count'] = int(dict_val['adjacent_neighbor_count'])
                continue
            
            # Adjacent with neighbor 109.0.0.5
            m = p13.match(line)
            if m:
                dict_val = m.groupdict()
                int_dict['adjacent_neighbor_address'] = dict_val['adjacent_neighbor_address']
                continue

            # Suppress hello for 0 neighbor(s)
            m = p14.match(line)
            if m:
                int_dict['suppressed_hello_neighbor_count'] = int(m.groupdict()['suppressed_hello_neighbor_count'])
                continue

        return ret_dict


# =================================================================
# Schema for:
#   * 'show ipv6 ospf interface'
# =================================================================

class ShowIpv6OspfNeighborDetailSchema(MetaParser):
    """ Schema for ShowIpv6OspfNeighborDetail """

    schema = {
        'router_id': {
            Any():{
                'process_id':{
                    Any():{
                        'neighbor': {
                            Any():{
                                'area': int,
                                'interface': str,
                                'interface_id': str,
                                'link_local_address': str,
                                'priority': int,
                                'state': str,
                                'state_changes': int,
                                'hello_options': str,
                                'hello_bits': str,
                                'dbd_options': str,
                                'dbd_bits': str,
                                'dead_timer': str,
                                'neighbor_up_time': str,
                                'index': str,
                                'retransmission_length': int,
                                'number_of_transmission': int,
                                'first': str,
                                'next': str,
                                'last_retransmission_length': int,
                                'retransmission_length_maximum': int,
                                'last_retransmission_time': int,
                                'retransmission_time_maximum': int
                            }
                        }
                    }
                }
            }
        }
    }

# =================================================================
# Parser for:
#   * 'show ipv6 ospf interface'
# =================================================================

class ShowIpv6OspfNeighborDetail(ShowIpv6OspfNeighborDetailSchema):
    """ Parser for ShowIpv6OspfNeighborDetail """

    cli_command = 'show ipv6 ospf neighbor detail'

    def cli(self, output=None):
        if output is None:
            cmd = self.cli_command
        
        output = self.device.execute(cmd)

        # OSPFv3 Router with ID (109.0.0.5) (Process ID 1)
        p1 = re.compile(r'^OSPFv3 Router with ID \((?P<router_id>[\S]+)\)\s+\(Process ID (?P<process_id>[\d]+)\)$')

        # Neighbor 109.0.0.1
        p2 = re.compile(r'^Neighbor (?P<neighbor>[\S]+)$')

        # In the area 0 via interface HundredGigE1/0/7
        p3 = re.compile(r'^In the area (?P<area>[\d]+)\s+via interface (?P<interface>[\S]+)$')

        # Neighbor: interface-id 5, link-local address FE80::2A7:42FF:FED7:4CFF
        p4 = re.compile(r'^Neighbor: interface-id (?P<interface_id>[\d]+),\s+link-local address (?P<link_local_address>[\S]+)$')

        # Neighbor priority is 0, State is FULL, 6 state changes
        p5 = re.compile(r'^Neighbor priority is (?P<priority>[\d]+), State is (?P<state>[\S]+), (?P<state_changes>[\d]+) state changes$')

        # Options is 0x000013 in Hello (V6-Bit, E-Bit, R-Bit)
        p6 = re.compile(r'^Options is (?P<hello_options>[\S]+) in Hello \((?P<hello_bits>[\S\s]+)\)$')

        # Options is 0x000013 in DBD (V6-Bit, E-Bit, R-Bit)
        p7 = re.compile(r'^Options is (?P<dbd_options>[\S]+) in DBD \((?P<dbd_bits>[\S\s]+)\)$')

        # Dead timer due in 00:00:39
        p8 = re.compile(r'^Dead timer due in (?P<dead_timer>\S+)$')
        
        # Neighbor is up for 17:54:26
        p9 = re.compile(r'^Neighbor is up for (?P<neighbor_up_time>\S+)$')
        
        # Index 1/2/2, retransmission queue length 0, number of retransmission 0
        p10 = re.compile(r'^Index (?P<index>\S+)\, retransmission queue length (?P<retransmission_length>\d+)\, number of retransmission (?P<number_of_transmission>\d+)$')
        
        # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
        p11 = re.compile(r'^First (?P<first>\S+) Next (?P<next>\S+)$')

        # Last retransmission scan length is 0, maximum is 0
        p12 = re.compile(r'^Last retransmission scan length is (?P<last_retransmission_length>\d+)\, maximum is (?P<retransmission_length_maximum>\d+)$')

        # Last retransmission scan time is 0 msec, maximum is 0 msec
        p13 = re.compile(r'^Last retransmission scan time is (?P<last_retransmission_time>\d+) msec\, maximum is (?P<retransmission_time_maximum>\d+) msec$')

        ret_dict = {}

        for line in output.splitlines():
            line = line.strip()

            # OSPFv3 Router with ID (109.0.0.5) (Process ID 1)
            m = p1.match(line)
            if m:
                dict_val = m.groupdict()
                process_dict = ret_dict.setdefault('router_id', {}).setdefault(dict_val['router_id'], {})
                neighbor_dict = process_dict.setdefault('process_id', {}).setdefault(dict_val['process_id'], {})
                continue

            # Neighbor 109.0.0.1
            m = p2.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict = neighbor_dict.setdefault('neighbor', {}).setdefault(dict_val['neighbor'], {})
                continue

            # In the area 0 via interface HundredGigE1/0/7
            m = p3.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['area'] = int(dict_val['area'])
                sub_dict['interface'] = dict_val['interface']
                continue
            
            # Neighbor: interface-id 5, link-local address FE80::2A7:42FF:FED7:4CFF
            m = p4.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['interface_id'] = dict_val['interface_id']
                sub_dict['link_local_address'] = dict_val['link_local_address']
                continue

            # Neighbor priority is 0, State is FULL, 6 state changes
            m = p5.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['priority'] = int(dict_val['priority'])
                sub_dict['state'] = dict_val['state']
                sub_dict['state_changes'] = int(dict_val['state_changes'])
                continue

            # Options is 0x000013 in Hello (V6-Bit, E-Bit, R-Bit)
            m = p6.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['hello_options'] = dict_val['hello_options']
                sub_dict['hello_bits'] = dict_val['hello_bits']
                continue

            # Options is 0x000013 in DBD (V6-Bit, E-Bit, R-Bit)
            m = p7.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['dbd_options'] = dict_val['dbd_options']
                sub_dict['dbd_bits'] = dict_val['dbd_bits']
                continue

            # Dead timer due in 00:00:39
            m = p8.match(line)
            if m:
                sub_dict['dead_timer'] = m.groupdict()['dead_timer']
                continue
            
            # Neighbor is up for 17:54:26
            m = p9.match(line)
            if m:
                sub_dict['neighbor_up_time'] = m.groupdict()['neighbor_up_time']
                continue

            # Index 1/2/2, retransmission queue length 0, number of retransmission 0
            m = p10.match(line)
            if m:
                dict_val = m.groupdict()
                sub_dict['index'] = dict_val['index']
                sub_dict['retransmission_length'] = int(dict_val['retransmission_length'])
                sub_dict['number_of_transmission'] = int(dict_val['number_of_transmission'])
                continue

            # First 0x0(0)/0x0(0)/0x0(0) Next 0x0(0)/0x0(0)/0x0(0)
            m = p11.match(line)
            if m:
                sub_dict['first'] = m.groupdict()['first']
                sub_dict['next'] = m.groupdict()['first']

            # Last retransmission scan length is 0, maximum is 0
            m = p12.match(line)
            if m:
                sub_dict['last_retransmission_length'] = int(m.groupdict()['last_retransmission_length'])
                sub_dict['retransmission_length_maximum'] = int(m.groupdict()['retransmission_length_maximum'])

            # Last retransmission scan time is 0 msec, maximum is 0 msec
            m = p13.match(line)
            if m:
                sub_dict['last_retransmission_time'] = int(m.groupdict()['last_retransmission_time'])
                sub_dict['retransmission_time_maximum'] = int(m.groupdict()['retransmission_time_maximum'])

        return ret_dict

# ===========================================================
# Schema for:
#   * 'show ip ospf {process_id} rib {route}'
# =================================================================
 
class ShowIpOspfRibRouteSchema(MetaParser):
 
    ''' Schema for:
        * 'show ip ospf {process_id} rib {route}'
    '''

    schema = {
        'vrf':{
            Any():{
                'instance':{
                    Any():{
                        Optional('network'):{
                        Any(): {
                            'route_type': str,
                            'cost': int,
                            'area': str,
                            'total_paths': int,
                            'nexthop_ip':
                                {Any():
                                    {'interface':
                                        {Any():
                                            {Optional('label'): int,
                                            Optional('strict_label'): int,
                                            Optional('cost'): int,
                                            'flags': list,
                                            Optional('repair'):
                                                {'nexthop_ip': str,
                                                 'interface': str,
                                                 Optional('label'): int,
                                                 Optional('strict_label'): int,
                                                 'cost': int,
                                                 'flags': list,
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }
# ================================================================
# Parser for:
#   * 'show ip ospf {process_id} rib {route}'
# ================================================================

class ShowIpOspfRibRoute(ShowIpOspfRibRouteSchema):
 
    ''' Parser for:
        * "show ip ospf rib {route}"
        * "show ip ospf {process_id} rib {route}"
    '''
 
    cli_command = ['show ip ospf rib {route}', 'show ip ospf {process_id} rib {route}']
 
    def cli(self, process_id=None, route=None, output=None):
 
        if not output:
            if process_id:
                output = self.device.execute(self.cli_command[1].format(process_id=process_id, route=route))
            else:
                output = self.device.execute(self.cli_command[0].format(route=route))
        # OSPF Router with ID (10.36.3.3) (Process ID 1)
        # OSPF Router with ID (20.3.5.6) (Process ID 2, VRF VRF1)
        p0 = re.compile(r'^OSPF +Router +with +ID +\((?P<router_id>(\S+))\) +\(Process +ID +(?P<instance>(\d+))'
                        r'(?:, +VRF +(?P<vrf>(\S+)))?\)$')
  
        # 20.20.20.0/24, Intra, cost 10, area 0
        p1 = re.compile(r'^\*\>?\s+(?P<network>\S+),\s+(?P<route_type>\S+),\s+cost\s+(?P<cost>\d+),\s+area\s+(?P<area>\d+)*$')
        
        # via 40.60.1.40, Ethernet0/2
        # via 40.60.1.40, Ethernet0/2, label 16001, strict label 17001
        # via 40.60.1.40, Ethernet0/2, label 16001, strict label 17001, cost 100
        # via Null0
        p2 = re.compile(r'via ((?P<nexthop_ip>\S+),)?\s*(?P<interface>[A-Za-z0-9./-]+)(,\s+label\s+(?P<label>\d+))?(,\s+strict\s+label\s+(?P<strict_label>\d+))?(,\s+cost\s+(?P<cost>\d+))?')

        # Flags: RIB, MFI
        p3 = re.compile(r'Flags: (?P<flags>[\S\s]+)')
        
        # repair path via 40.60.1.40, Ethernet0/2, label 16001, strict label 17001, cost 100
        p4 = re.compile(r'.*repair path via (?P<nexthop_ip>\S+),\s*(?P<interface>[A-Za-z0-9./-]+)(,\s+label\s+(?P<label>\d+))?(,\s+strict\s+label\s+(?P<strict_label>\d+))?(,\s+cost\s+(?P<cost>\d+))?')

        # initial variables
        ret_dict = {}
        network_dict = {}
        af = 'ipv4' # this is ospf - always ipv4
        vrf = '' # default vrf
        primary_path = False
        repair_path = False

        for line in output.splitlines():
            line = line.strip()
            # OSPF Router with ID (10.36.3.3) (Process ID 1)
            # OSPF Router with ID (20.3.5.6) (Process ID 2, VRF VRF1)
            m = p0.match(line)
            if m:
                group = m.groupdict()
                instance = str(group['instance'])
                if group['vrf']:
                    vrf = str(group['vrf'])
                else:
                    vrf = 'default'
                ospf_dict = ret_dict.setdefault('vrf', {}).setdefault(vrf, {}).setdefault('instance', {}).setdefault(instance, {})
                continue
            # 20.20.20.0/24, Intra, cost 10, area 0
            m = p1.match(line)
            if m:
                group = m.groupdict()
                network = group['network']
                route_type = group['route_type']
                cost = group['cost']
                area = group['area']
                network_dict = ospf_dict.setdefault('network', {}).setdefault(network, {})
                network_dict['route_type'] = group['route_type']
                network_dict['cost'] = int(group['cost'])
                network_dict['area'] = group['area']
                network_dict.update(total_paths = 0)
                continue
            #  via 40.60.1.40, Ethernet0/2, label 16001, strict label 17001, cost 100
            m = p2.match(line)
            if m:
                primary_path = True
                repair_path = False
                group = m.groupdict()
                nexthop_ip  = group['nexthop_ip']
                interface   = group['interface']
                label        = group['label']
                strict_label = group['strict_label']
                cost        = group['cost']
                if nexthop_ip is None:
                    nexthop_ip = 'None'
                nexthop_ip_dict = network_dict.setdefault('nexthop_ip', {}).setdefault(nexthop_ip, {})
                interface_dict = nexthop_ip_dict.setdefault('interface', {}).setdefault(interface, {})
                if (label):
                    interface_dict['label'] = int(label)
                if (strict_label):
                    interface_dict['strict_label'] = int(strict_label)
                if (cost):
                    interface_dict['cost'] = int(cost)
                network_dict['total_paths'] = network_dict['total_paths'] + 1
                continue
            # Flags: RIB, MFI
            m = p3.match(line)
            if m:
                if (primary_path):
                    group = m.groupdict()
                    flags = group['flags']
                    interface_dict['flags'] = flags.replace(" ", "").split(",")
                elif (repair_path):
                    group = m.groupdict()
                    flags = group['flags']
                    repair_dict['flags'] = flags.replace(" ", "").split(",")
                continue
            # repair path via 40.60.1.40, Ethernet0/2, label 16001, strict label 17001, cost 100
            m = p4.match(line)
            if m:
                repair_path = True
                primary_path = False
                group = m.groupdict()
                nexthop_ip  = group['nexthop_ip']
                interface   = group['interface']
                label        = group['label']
                strict_label = group['strict_label']
                cost        = group['cost']
                repair_dict = interface_dict.setdefault('repair', {})
                repair_dict['nexthop_ip'] = nexthop_ip
                repair_dict['interface'] = interface
                if (label):
                    repair_dict['label'] = int(label)
                if (strict_label):
                    repair_dict['strict_label'] = int(strict_label)
                if (cost):
                    repair_dict['cost'] = int(cost)
                continue

        return ret_dict