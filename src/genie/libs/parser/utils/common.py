'''Common functions to be used in parsers'''

# python
import re
import os
import sys
import json
import math
import logging
import warnings
import importlib
import pkg_resources
from packaging import version
from inspect import getfullargspec
from json.decoder import JSONDecodeError

from pyats.log.utils import banner
from pyats.configuration import configuration as cfg

from genie.abstract.package import AbstractTree, DEFAULT_ABSTRACT_ORDER
from genie.abstract import Lookup

from .extension import ExtendParsers

PARSER_MODULE_NAME = 'genie.libs.parser'
ENTRY_POINT_NAME = PARSER_MODULE_NAME
PYATS_EXT_PARSER = 'pyats.libs.external.parser'

log = logging.getLogger(__name__)

try:
    from genie.libs.cisco.telemetry import add_parser_usage_data
    INTERNAL = True
except:
    INTERNAL = False

parser_data = None

INTERFACE_ABBREVIATION_MAPPING_TABLE = {
    # Please add more when face other type of interface
        'generic':
        # generic keys for when no OS detected
        {
            'Eth': 'Ethernet',
            'SEth': 'Service-Ethernet',
            'Lo': 'Loopback',
            'lo': 'Loopback',
            'Fa': 'FastEthernet',
            'Fas': 'FastEthernet',
            'Po': 'Port-channel',
            'PO': 'Port-channel',
            'Null': 'Null',
            'Gi': 'GigabitEthernet',
            'Gig': 'GigabitEthernet',
            'GE': 'GigabitEthernet',
            'Te': 'TenGigabitEthernet',
            'Ten': 'TenGigabitEthernet',
            'Tw': 'TwoGigabitEthernet',
            'Two': 'TwoGigabitEthernet',
            'Twe': 'TwentyFiveGigE',
            'Fi': 'FiveGigabitEthernet',
            'Fiv': 'FiveGigabitEthernet',
            'Fif': 'FiftyGigE',
            'Fifty': 'FiftyGigabitEthernet',
            'mgmt': 'mgmt',
            'Vl': 'Vlan',
            'Tu': 'Tunnel',
            'Hs': 'HSSI',
            'AT': 'ATM',
            'Et': 'Ethernet',
            'BD': 'BDI',
            'Ser': 'Serial',
            'Se': 'Serial',
            'Fo': 'FortyGigabitEthernet',
            'For': 'FortyGigabitEthernet',
            'Hu': 'HundredGigE',
            'Hun': 'HundredGigE',
            'TwoH': 'TwoHundredGigabitEthernet',
            'Fou': 'FourHundredGigE',
            'vl': 'vasileft',
            'vr': 'vasiright',
            'BE': 'Bundle-Ether',
            'tu': 'Tunnel',
            'M-E': 'M-Ethernet',  # comware
            'BAGG': 'Bridge-Aggregation',  # comware
            'Ten-GigabitEthernet': 'TenGigabitEthernet',  # HP
            'Wl': 'Wlan-GigabitEthernet',
            'Di': 'Dialer',
            'Vi': 'Virtual-Access',
            'Ce': 'Cellular',
            'Vp': 'Virtual-PPP',
            'pw': 'pseudowire'
        },
        'iosxr':
        # interface formats specific to iosxr
        {
            'BV': 'BVI',
            'BE': 'Bundle-Ether',
            'BP': 'Bundle-POS',
            'Eth': 'Ethernet',
            'Fa': 'FastEthernet',
            'Gi': 'GigabitEthernet',
            'Te': 'TenGigE',
            'Tf': 'TwentyFiveGigE',
            'Fo': 'FortyGigE',
            'Fi': 'FiftyGigE',
            'Hu': 'HundredGigE',
            'Th': 'TwoHundredGigE',
            'Fh': 'FourHundredGigE',
            'Tsec': 'tunnel-ipsec',
            'Ti': 'tunnel-ip',
            'Tm': 'tunnel-mte',
            'Tt': 'tunnel-te',
            'Tp': 'tunnel-tp',
            'IMA': 'IMA',
            'IL': 'InterflexLeft',
            'IR': 'InterflexRight',
            'Lo': 'Loopback',
            'Mg': 'MgmtEth',
            'Ml': 'Multilink',
            'Nu': 'Null',
            'POS': 'POS',
            'Pw': 'PW-Ether',
            'Pi': 'PW-IW',
            'SRP': 'SRP',
            'Se': 'Serial',
            'CS': 'CSI',
            'G0': 'GCC0',
            'G1': 'GCC1',
            'nG': 'nVFabric-GigE',
            'nT': 'nVFabric-TenGigE',
            'nF': 'nVFabric-FortyGigE',
            'nH': 'nVFabric-HundredGigE'
        }
    }

class ParserNotFound(Exception):
    '''raise exception if parser command is not found
       first argument is parser class
       second argument is token '''
    def __init__(self, *args):
        self.parser_command = args[0]
        self.token = args[1]

    def __str__(self):
        return (
            f"Could not find parser for '{self.parser_command}' under {self.token}"
        )


def _load_parser_json():
    '''get all parser data in json file'''

    global parser_data

    try:
        mod = importlib.import_module(PARSER_MODULE_NAME)
        token_order = getattr(getattr(mod, '__abstract_pkg'), 'order',
                              DEFAULT_ABSTRACT_ORDER)
        parsers = os.path.join(mod.__path__[0], 'parsers.json')
    except Exception:
        token_order = DEFAULT_ABSTRACT_ORDER
        parsers = ''

    if not os.path.isfile(parsers):
        raise Exception('parsers.json does not exist, make sure you '
                        'are running with latest version of '
                        'genie.libs.parsers. Do make json to generate '
                        'json files to use the parsers.')

    # Open all the parsers in json file
    with open(parsers) as f:
        try:
            json_data = json.load(f)
        except JSONDecodeError:
            log.error(banner("parser json file could be corrupted. "
                                "Please try 'make json'"))
            raise
    parser_data = AbstractTree.from_json(json_data,
                                            package=PARSER_MODULE_NAME,
                                            feature='parser')
    if parser_data.order != token_order:
        raise KeyError('Loaded token order from json does not match '
                        'package token order\n{} != {}'.\
                            format(parser_data.order, token_order))

    # check if provided external parser packages
    PYATS_EXT_PARSER_ENV_VAR = PYATS_EXT_PARSER.upper().replace('.', '_')
    ext_parser_packages = []

    ext_parser_package_conf = cfg.get(PYATS_EXT_PARSER)
    if ext_parser_package_conf:
        ext_parser_packages_from_conf = ext_parser_package_conf.split(',')
        ext_parser_packages.extend(ext_parser_packages_from_conf)

    ext_parser_package_env = os.environ.get(PYATS_EXT_PARSER_ENV_VAR)
    if ext_parser_package_env:
        ext_parser_packages_from_env = ext_parser_package_env.split(',')
        ext_parser_packages.extend(ext_parser_packages_from_env)

    for ep in pkg_resources.iter_entry_points(ENTRY_POINT_NAME):
        parser_package = ep.load()
        if callable(parser_package):
            log.warning(
                f'{ep.name}: callable parser loading is deprecated. '
                'Please create an abstracted package instead.')
            _load_parser_callable(parser_package, parser_data)
        else:
            ext_parser_packages.append(ep.module_name)

    # remove duplicates
    ext_parser_packages = set(ext_parser_packages)
    log.debug(f'External parser packages: {ext_parser_packages}')

    for ext_parser_package in ext_parser_packages:
        log.debug(f'Extending {ext_parser_package}')
        ext = ExtendParsers(ext_parser_package)
        ext.extend()

        extend_info = ext.output.pop('extend_info', None)

        extend_matrix = AbstractTree.from_json(ext.output,
                                                package=PARSER_MODULE_NAME,
                                                feature='parser')
        parser_data.update(extend_matrix)

        log.debug("External parser {} counts: {}\nSummary:\n{}".format(
            ext_parser_package,
            len(extend_info),
            json.dumps(extend_info, indent=2)))

    return parser_data


def _load_parser_callable(package, parser_data):
    '''_load_parser_callable

    *** DEPRECATED This is only here for backward compatibility ***

    The genie parser entrypoint can point to a function which returns a dict of
    new parsers. This dict should have the format
    {<os>: [<parser_classes, ...], <os>: [more_parser_classes, ...]}
    These parsers are then added to the abstract matrix to be available for
    lookup.
    '''
    if not 'os' in parser_data.order:
        warnings.warn('"os"')

    for os, parser_list in package().items():
        for parser in parser_list:
            # get list of commands which are the top-level keys of the abstract
            # matrix
            cli_commands = parser.cli_command
            if isinstance(cli_commands, str):
                cli_commands = [cli_commands]
            for cmd in cli_commands:
                # add or get this command to the matrix, and drill down to the
                # os token level
                matrix_ptr = parser_data.get_create(cmd)
                for i in range(parser_data.order.index('os')):
                    matrix_ptr = matrix_ptr.get_create(None)
                # add or overwrite the parser for this command and os
                matrix_ptr = matrix_ptr.get_create(os, ptr=parser)


def get_parser_commands(device, data=None):
    '''Remove all commands which contain { as this requires
       extra kwargs which cannot be guessed dynamically
       Remove the ones that arent related to this os'''
    global parser_data
    if data is None:
        if parser_data is None:
            data = _load_parser_json()
        else:
            data = parser_data

    return [
        command for command, values in data.items()
        if '{' not in command and command != 'tokens' and device.os in values
    ]


def format_output(parser_data, tab=2):
    '''Format the parsed output in an aligned intended structure'''

    s = ['{\n']
    if parser_data is None:
        return parser_data
    for k, v in sorted(parser_data.items(), key=str):
        v = format_output(v, tab + 2) if isinstance(v, dict) else repr(v)
        s.append('%s%r: %s,\n' % ('  ' * tab, k, v))
    s.append('%s}' % ('  ' * (tab - 2)))
    return ''.join(s)


def get_parser_exclude(command, device):
    try:
        return get_parser(command, device)[0].exclude
    except AttributeError:
        return []


def get_parser(command, device, fuzzy=False, revision=None, abstract=None, **kwargs):
    '''From a show command and device, return parser class and kwargs if any'''
    global parser_data

    if parser_data is None:
        data = _load_parser_json()
    else:
        data = parser_data

    # get tokens from device including specific ones for genie.libs.parser
    tokens = Lookup.tokens_from_device(device, data.order, PARSER_MODULE_NAME)
    if abstract:
        tokens.update(abstract)
    revision = revision or tokens.get('revision')
    if revision and not isinstance(revision, list):
        revision = [revision]
    if revision:
        tokens['revision'] = revision

    revision = revision or tokens.get('revision')
    if revision and not isinstance(revision, list):
        revision = [revision]
    if revision:
        tokens['revision'] = revision

    results = _fuzzy_search_command(command, fuzzy, tokens)
    valid_results = []

    for result in results:
        found_command, parser_cls, kwargs = result

        if found_command == 'tokens':
            continue

        # parser_cls can be None if there is no abstract data, but a matching
        # command is still found
        if parser_cls is None:
            continue

        valid_results.append((found_command, parser_cls, kwargs))

    if not valid_results:
        # result is not valid. raise custom ParserNotFound exception
        raise ParserNotFound(command, tokens)

    log.debug('Parsers found for command "{}": {}'.format(command,
                                                         str(valid_results)))

    # Try to add parser to telemetry data
    if INTERNAL:
        try:
            # valid_results is a list of found parsers for a given show command
            #  - first element in this list is the closest parser match found
            #  - each element has the format (show command, class, kwargs)
            # valid_results[0] is the best parser match
            add_parser_usage_data(valid_results[0], device)
        except Exception as e:
            log.debug("Encountered an unexpected error while adding parser "
                      "telemetry data: %s" % e)

    if not fuzzy:
        # valid_results is a list of found parsers for a given show command
        #  - first element in this list is the closest parser match found
        #  - each element has the format (show command, class, kwargs)
        # valid_results[0][0] is the matched command string from the parser cli_command
        # valid_results[0][1] is the class of the best match
        # valid_results[0][2] is a dict of parser kwargs
        parser_class = valid_results[0][1]
        parser_kwargs = valid_results[0][2]
        spec = getfullargspec(parser_class.cli)
        if 'command' in spec.args:
            cmd = valid_results[0][0]
            parser_kwargs['command'] = cmd.format(**parser_kwargs)
        log.debug(f'Parser class: {parser_class} arguments: {parser_kwargs}')
        return parser_class, parser_kwargs

    log.debug(f'Parser search results: {valid_results}')
    return valid_results


def _fuzzy_search_command(search,
                          fuzzy,
                          abstract=None):
    """ Find commands that match the search criteria.

        Args:
            search (`str`): the search query
            fuzzy (`bool`): whether or not fuzzy mode should be used
            abstract (`dict`): abstract tokens dict

        Returns:
            list: the result of the search
    """
    global parser_data

    if parser_data is None:
        data = _load_parser_json()
    else:
        data = parser_data

    # Perfect match should return
    if search in data:
        parser_cls = None
        if abstract:
            parser_cls = _get_parser_cls(search, abstract)
        if parser_cls is not None:
            return [(search, parser_cls, {})]

    # Preprocess if fuzzy
    if fuzzy:
        search = search.lstrip('^').rstrip('$').replace(r'\ ', ' ').replace(
            r'\-', '-').replace('\\"', '"').replace('\\,', ',').replace(
                '\\\'', '\'').replace('\\*', '*').replace('\\:', ':').replace(
                    '\\^', '^').replace('\\/', '/').replace('\\(', '(').replace('\\)', ')')

    # Fix search to remove extra spaces
    search = ' '.join(filter(None, search.split()))
    tokens = search.split()
    best_score = -math.inf
    result = []

    for command in data:
        # ! This was a band-aid fix. Root cause has been resolved, but this will
        # ! remain in-place for peace of mind
        if command is None:
            continue
        # Tokens and kwargs parameter must be non reference
        match_result = _matches_fuzzy(0, 0, tokens.copy(), command, {}, fuzzy)

        if match_result:
            kwargs, score = match_result

            if score < best_score:
                # If we found a worse match, ignore it
                continue

            parser_cls = None
            if abstract:
                parser_cls = _get_parser_cls(command, abstract)
                if parser_cls is None:
                    # No matching class found for this abstract token dict, not
                    # the right parser
                    continue

            entry = (command, parser_cls, kwargs)

            if score > best_score:
                # If we found a better match, discard everything and start new
                result = [entry]
                best_score = score

            elif score == best_score:
                result.append(entry)

    # Return only one instance if fuzzy is not used
    # Check if any ambiguous commands
    if not fuzzy and len(result) > 1:
        # If all results have the same argument positions but different names
        # It should return the first result

        # Check if the result regex match the search
        for instance in result:
            s = re.sub('{.*?}', '(.*)', instance[0])
            p = re.compile(s)
            if p.match(search):
                return [instance]

        if (len({re.sub('{.*?}', '---', instance[0])
                 for instance in result}) == 1):
            return [result[0]]
        else:
            # Search is ambiguous
            raise Exception("\nSearch for '" + search + "' is ambiguous. " +
                            "Please be more specific in your keywords.\n\n" +
                            "Results matched:\n" + '\n'.join('> ' + i[0]
                                                             for i in result))

    return result


def _get_parser_cls(command, abstract):
    '''_get_parser_cls

    retrieves a parser class from the abstract matrix given an abstract token
    dict and command

        Args:
            command (`str`): the unformatted command to load a class for
            abstract (`dict`): abstract tokens dict with device values

        Returns:
            class: Class of the parser implementation for the given tokens
            None: No matching parser for that command
    '''
    global parser_data

    if parser_data is None:
        data = _load_parser_json()
    else:
        data = parser_data

    # Ensure the matching command is valid for this device
    for matrix_ptr in data.iter_lookup(tokens=abstract, top=command):

        # get the best fit class of the command for this device
        try:
            return matrix_ptr.load_ptr()
            # we only need one result for this command
        except KeyError:
            # fallback to lower priority token values
            continue
    # No appropriate class found, return None
    return None


def _is_regular_token(token):
    """ Checks if a token is regular (does not contain regex symbols).

        Args:
            token (`str`): the token to be tested

        Returns:
            bool: whether or not the token is regular

    """
    token_is_regular = True

    if not token.isalnum():
        # Remove escaped characters
        candidate = token.replace('/', '')
        candidate = candidate.replace('"', '')
        candidate = candidate.replace('\\^', '')
        candidate = candidate.replace('\'', '')
        candidate = candidate.replace('-', '')
        candidate = candidate.replace('^', '')
        candidate = candidate.replace('_', '')
        candidate = candidate.replace(':', '')
        candidate = candidate.replace(',', '')
        candidate = candidate.replace('\\.', '')
        candidate = candidate.replace('\\|', '')
        candidate = candidate.replace('(', '')
        candidate = candidate.replace(')', '')

        token_is_regular = candidate.isalnum() or candidate == ''

    return token_is_regular


def _matches_fuzzy(i,
                   j,
                   tokens,
                   command,
                   kwargs,
                   fuzzy,
                   required_arguments=None,
                   score=0):
    """ Compares between given tokens and command to see if they match.

        Args:
            i (`int`): current end of tokens
            j (`int`): current index of command tokens
            tokens (`list`): the search tokens
            command (`str`): the command to be compared with
            kwargs (`dict`): the collected arguments
            fuzzy (`bool`): whether or not fuzzy should be used
            required_arguments (`int`): number of arguments command has
            score (`int`): the current similarity score between token and command

            Returns:
                bool: whether or not search matches the command

    """
    command_tokens = command.split()

    # Initialize by counting how many arguments this command needs
    if required_arguments is None:
        required_arguments = len(re.findall(r'{.*?}', command))

    while i < len(tokens):
        # If command token index is greater than its length, stop
        if j >= len(command_tokens):
            return None

        token = tokens[i]
        command_token = command_tokens[j]
        token_is_regular = True

        if fuzzy:
            token_is_regular = True if token == '*' else _is_regular_token(
                token)
            if token_is_regular:
                # Special case for `:\|Swap:`
                token = token.replace(r'\|', '|')

                # Special case for command `vim-cmd vmsvc/snapshot.get {vmid}`
                token = token.replace(r'\.', '.')

        if token_is_regular:
            # Current token might be command or argument
            if '{' in command_token:
                # Handle the edge case of argument not being a token
                # When this is implemented there is only one case:
                # /dna/intent/api/v1/interface/{interface}
                if not command_token.startswith('{'):
                    # Find before and after string
                    groups = re.match(r'(.*){.*?}(.*)', command_token).groups()
                    is_found = False

                    if len(groups) == 2:
                        start, end = groups

                        # Need to have perfect match with token
                        if token.startswith(start) and token.endswith(end):
                            # Escape regex
                            start = re.escape(start)
                            end = re.escape(end)

                            # Find the argument using the escaped start and end
                            kwargs[re.search(
                                r'{(.*)}',
                                command_token).groups()[0]] = re.match(
                                    r'{}(.*){}'.format(start, end),
                                    token).groups()[0]

                            is_found = True
                            score += 103

                    if not is_found:
                        return None
                else:
                    argument_key = re.search(r'{(.*)}',
                                             command_token).groups()[0]
                    i += 1
                    j += 1

                    # Plus 101 once to favor nongreedy argument fit
                    score += 100

                    # If argument is any of these, argument can only be 1 token
                    # Else argument can be up to 2 tokens
                    endpoint = (i + 1 if argument_key in [
                        'vrf',
                        'rd',
                        'instance',
                        'vrf_type',
                        'feature',
                        'fileA',
                        'fileB',
                    ] else i + 2)

                    # Try out ways we can assign search tokens into argument
                    for index in range(i, endpoint):
                        if index > len(tokens):
                            return None

                        # Make sure not to use regex expression as argument
                        if (index > i and fuzzy
                                and not _is_regular_token(tokens[index - 1])):
                            return None

                        # Currently spanned argument
                        if 'match' in tokens or 'include' in tokens:
                            argument_value = ' '.join(
                                tokens[i - 1:index]).replace('\\', '')
                        else:
                            argument_value = ' '.join(
                                tokens[i - 1:index]).rstrip('"').replace(
                                    '\\', '')

                        # argument_value = ' '.join(tokens[i - 1:index]).replace('\\', '')

                        # Delete the extra tokens if spanning more than one
                        tokens_copy = tokens[:i] + tokens[index:]
                        tokens_copy[i - 1] = command_token
                        kwargs_copy = kwargs.copy()
                        kwargs_copy.setdefault(argument_key, argument_value)

                        result = _matches_fuzzy(i, j, tokens_copy, command,
                                                kwargs_copy, fuzzy,
                                                required_arguments, score)

                        if result:
                            result_kwargs, score = result

                            if len(result_kwargs) == required_arguments:
                                return result_kwargs, score

                    return None
            elif token == command_token:
                # Same token, assign higher score
                score += 102
            else:
                # Not matching, check if prefix
                if not command_token.startswith(token):
                    return None

                # The two tokens are similar to each other, replace
                tokens[i] = command_token
                score += 100

            # Matches current, go to next token
            i += 1
            j += 1
        else:
            # Count number of regex tokens that got ate
            skipped = 1

            # Not a token, should be a regex expression
            # Keep eating if next token is also regex
            while i + 1 < len(tokens) and not _is_regular_token(tokens[i + 1]):
                i += 1
                skipped += 1

            # Match current span with command
            test = re.match(' '.join(tokens[:i + 1]), command)

            if not test:
                # Failed to match fuzzy
                return None

            # Perform command token lookahead
            _, end = test.span()

            # Expression matches command to end
            if i + 1 == len(tokens) and end == len(command):
                # Return result if from start to end there are no arguments
                if all('{' not in ct for ct in command_tokens[j:]):
                    return kwargs, score
                else:
                    # Else in range we have another unspecified argument
                    return None

            if end == 0:
                # If regex matched nothing, we stop because
                # expression = "d? a b c" search in "a b c"
                # expression = "a b d? c" search in "a b c"
                return None

                # Span single command token
            if abs(end - sum(len(ct)
                             for ct in command_tokens[:j + 1]) - j) <= 1:
                if '{' in command_token:
                    # Faulty match
                    return None
                # Span single token if it is not argument
                i += 1
                j += 1

                continue
            else:
                # Span multiple command tokens
                # Find which command token it spans up to
                current_sum = 0
                token_end = 0

                while current_sum + len(command_tokens[token_end]) <= end:
                    current_sum += len(command_tokens[token_end])

                    if current_sum >= end:
                        break

                    # Account for space
                    current_sum += 1
                    token_end += 1
                # Incrememt token index
                i += 1

                # For matched range, perform submatches on next real token
                for subindex in range(j + skipped, token_end + 1):
                    # Make sure items are passed by copies, not by reference
                    submatch_result = _matches_fuzzy(i, subindex,
                                                     tokens.copy(), command,
                                                     kwargs.copy(), fuzzy,
                                                     required_arguments, score)

                    # If any match is found, return true
                    if submatch_result:
                        result_kwargs, score = submatch_result

                        # Result kwargs must match
                        # number of arguments this command requires
                        if required_arguments == len(result_kwargs):
                            return result_kwargs, score

                # Fail to match
                return None
    # Reached end of tokens
    if len(command_tokens) == j:
        # If command pointer is at end then it matches
        return kwargs, score
    else:
        # It doesn't match
        return None


class Common:
    '''Common functions to be used in parsers.'''
    @classmethod
    def regexp(self, expression):
        def match(value):
            if re.match(expression, value):
                return value
            else:
                raise TypeError("Value '%s' doesnt match regex '%s'" %
                                (value, expression))

        return match

    @classmethod
    def convert_intf_name(self, intf, os='generic', ignore_case=False):
        '''return the full interface name

            Args:
                intf (`str`): Short version of the interface name
                os (`str`): picks what operating system the interface needs to be translated for.
                ignore_case (`bool`): Case in-sensitive matching of names

            Returns:
                Full interface name fit the standard

            Raises:
                None

            example:

                >>> convert_intf_name(intf='Eth2/1')
        '''

        # takes in the words preceding a digit e.g. the Ge in Ge0/0/1
        m = re.search(r'([-a-zA-Z]+)', intf)
        # takes in everything after the first encountered digit, e.g. the 0/0/1 in Ge0/0/1
        m1 = re.search(r'(\d[\w./]*)', intf)

        # checks if an interface has both Ge and 0/0/1 in the example of Ge0/0/1
        if hasattr(m, 'group') and hasattr(m1, 'group'):
            # fetches the interface type
            int_type = m.group(0)
            # fetch the interface number
            int_port = m1.group(0)

            try:
                os_type_dict = INTERFACE_ABBREVIATION_MAPPING_TABLE[os]
            except KeyError as k:
                log.error((
                    "Check '{}' is in convert dict in utils/common.py, otherwise leave blank.\nMissing key {}\n"
                    .format(os, k)))
                return intf

            if ignore_case:
                mapping = {k.lower():v for k,v in os_type_dict.items()}
                name = int_type.lower()
                if name in mapping:
                    return mapping[name] + int_port
                else:
                    return intf[0].capitalize() + intf[1:].replace(
                        ' ', '').replace('ethernet', 'Ethernet')
            else:
                if int_type in os_type_dict.keys():
                    return os_type_dict[int_type] + int_port
                else:
                    return intf[0].capitalize() + intf[1:].replace(
                        ' ', '').replace('ethernet', 'Ethernet')

        else:
            return intf

    @classmethod
    def retrieve_xml_child(self, root, key):
        '''return the root which contains the key from xml

            Args:

                root (`obj`): ElementTree Object, point to top of the tree
                key (`str`): Expceted tag name. ( without namespace)

            Returns:
                Element object of the given tag

            Raises:
                None

            example:

                >>> retrieve_xml_child(
                        root=<Element '{urn:ietf:params:xml:ns:netconf:base:1.0}rpc-reply' at 0xf760434c>,
                        key='TABLE_vrf')
        '''
        for item in root:
            if key in item.tag:
                return item
            root = item
            return self.retrieve_xml_child(root, key)

    @classmethod
    def compose_compare_command(self, root, namespace, expect_command):
        '''compose commmand from the xml Element object from the root,
           then compare with the command with the expect_command.
           Only work for cisco standard output.

            Args:

                root (`obj`): ElementTree Object, point to top of the tree
                namespace (`str`): Namesapce. Ex. {http://www.cisco.com/nxos:8.2.0.SK.1.:rip}
                expect_command (`str`): expected command.

            Returns:
                None

            Raises:
                AssertionError: xml tag cli and command is not matched
                Exception: No mandatory tag __readonly__ in output

            example:

                >>> compose_compare_command(
                        root=<Element '{urn:ietf:params:xml:ns:netconf:base:1.0}rpc-reply' at 0xf760434c>,
                        namespace='{http://www.cisco.com/nxos:8.2.0.SK.1.:rip}',
                        expect_command='show bgp all dampening flap-statistics')
        '''
        # get to data node
        cmd_node = list(root)[0]
        # compose command from element tree
        # ex.  <nf:data>
        #        <show>
        #         <bgp>
        #          <all>
        #           <dampening>
        #            <flap-statistics>
        #             <__readonly__>
        cli = ''
        while True:
            # get next node
            try:
                cmd_node = list(cmd_node)
                if len(cmd_node) == 1:

                    # when only have one child
                    cmd_node = cmd_node[0]

                    # <__XML__PARAM__vrf-name>
                    #  <__XML__value>VRF1</__XML__value>
                    # </__XML__PARAM__vrf-name>
                    if '__XML__value' in cmd_node.tag:
                        cli += ' ' + cmd_node.text

                elif len(cmd_node) > 1:

                    # <__XML__PARAM__interface>
                    #   <__XML__value>loopback100</__XML__value>
                    #   <vrf>
                    for item in cmd_node:
                        if '__XML__value' in item.tag:
                            cli += ' ' + item.text
                        else:
                            cmd_node = item
                            break
                else:
                    break
            except Exception:
                pass

            # get tag name
            tag = cmd_node.tag.replace(namespace, '')

            # __readonly__ is the end of the command
            if '__readonly__' in tag:
                break

            if '__XML__PARAM__' not in tag and \
                    '__XML__value' not in tag and \
                    'TABLE' not in tag:
                cli += ' ' + tag
            # if there is no __readonly__ but the command has outputs
            # should be warining
            if 'TABLE' in tag:
                warnings.warn(
                    'Tag "__readonly__" should exsist in output when '
                    'there are actual values in output')
                break

        cli = cli.strip()
        # compare the commands
        assert cli == expect_command, \
            'Cli created from XML tags does not match the actual cli:\n' \
            'XML Tags cli: {c}\nCli command: {e}'.format(c=cli, e=expect_command)

    @classmethod
    def convert_xml_time(self, xml_time):
        '''Convert xml time "PT1H4M41S" to normal time "01:04:41"

            Args:
                xml_time (`str`): XML time

            Returns:
                Standard time string

            Raises:
                None

            example:

                >>> convert_xml_time(xml_time='PT1H4M41S')
                >>> "01:04:41"
        '''
        # P4DT12M38S
        # PT1H4M41S
        p = re.compile(
            r'^P((?P<day>\d+)D)?T((?P<hour>\d+)H)?((?P<minute>\d+)M)?((?P<second>\d+)S)?$'
        )
        m = p.match(xml_time)
        if m:
            day = m.groupdict()['day']
            hour = m.groupdict()['hour']
            hour = 0 if not hour else int(hour)
            minute = m.groupdict()['minute']
            minute = 0 if not minute else int(minute)
            second = m.groupdict()['second']
            second = 0 if not second else int(second)

            if day:
                standard_time = "{d}d{h}h".format(d=day, h="%02d" % (hour))
            else:
                standard_time = ''
                standard_time += format("%02d" % (hour))
                standard_time += ' ' + format("%02d" % (minute))
                standard_time += ' ' + format("%02d" % (second))

                standard_time = ':'.join(standard_time.strip().split())
        else:
            # P4M13DT21H21M19S
            standard_time = xml_time
        return standard_time

    @classmethod
    def find_keys(self, key, dictionary):
        '''
        find all keys in dictionary
        Args:
            dictionary:

        Returns:

        '''
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                yield from self.find_keys(key, v)
            elif isinstance(v, list):
                for d in v:
                    yield from self.find_keys(key, d)

    @classmethod
    def combine_units_of_time(self, hours=None, minutes=None, seconds=None):
        '''Combine seperate units of time to 'normal time': HH:MM:SS

            Args (All are optional. Nothing returns 00:00:00):
                hours (`int`): number of hours
                minutes (`int`): number of minutes
                seconds (`int`): number of seconds

            Returns:
                Standard time string

            Raises:
                None

            example:

                >>> convert_xml_time(minutes=500)
                >>> "08:20:00"
        '''
        total_combined_seconds = 0

        if hours:
            total_combined_seconds += hours * 60 * 60

        if minutes:
            total_combined_seconds += minutes * 60

        if seconds:
            total_combined_seconds += seconds

        final_seconds = total_combined_seconds % 60
        if final_seconds <= 9:
            final_seconds = "0{}".format(final_seconds)

        final_minutes = (total_combined_seconds // 60) % 60
        if final_minutes <= 9:
            final_minutes = "0{}".format(final_minutes)

        final_hours = (total_combined_seconds // 60) // 60
        if final_hours <= 9:
            final_hours = "0{}".format(final_hours)

        return "{}:{}:{}".format(final_hours, final_minutes, final_seconds)


def check_for_duplicate(data):
    """
    Checks for duplicate entries within a nested data structure and logs warnings for each duplicate found.

    This function iterates over the nodes of AbstractTree. For each command, it constructs
    a dictionary representation of its sub-trees and checks for duplicates within these sub-trees.
    If duplicates are found, a warning is logged with the command name, and the command is added to
    a list of duplicates.

    Parameters:
    data (AbstractTree): The AbstractTree to be checked for duplicates

    Returns:
    list: A list of command names that have duplicates.
    """
    duplicates = []
    for cmd, cmd_value in data.nodes.items():
        data_dict = {}
        if isinstance(cmd_value.nodes, dict) and len(cmd_value.nodes.keys()) >= 2:
            for node, sub_tree in cmd_value.nodes.items():
                sub_tree_dict = data_dict.setdefault(node, {})
                _check_tree(sub_tree, sub_tree_dict)
            if _find_duplicate(data_dict):
                log.warning(f'{cmd} is a duplicate')
                duplicates.append(cmd)
    return duplicates

def _check_tree(tree, sub_tree_dict):
    """
    Recursively constructs a dictionary representation of a tree structure.

    This function traverses a tree starting from the given `tree` object. For each node in the tree,
    it updates `sub_tree_dict` to include the node and its sub-nodes, effectively building a nested
    dictionary representation of the tree.

    Parameters:
    tree (object): An object with a `nodes` attribute that is a dictionary. Each key-value pair represents
                   a node and its associated value, which may contain further nodes.
    sub_tree_dict (dict): A dictionary used to store the nested structure of the tree.

    Returns:
    None
    """
    for node, node_value in tree.nodes.items():
        node_dict = sub_tree_dict.setdefault(node, {})
        if node_value.nodes != {}:
            for key, value in node_value.nodes.items():
                node_output = node_dict.setdefault(key, {})
                _check_tree(value, node_output)


def _find_duplicate(tree_dict):
    """
    Determines if there are duplicate structures within a tree dictionary.

    This function checks for duplicates by comparing branches of a tree stored in `tree_dict`.
    It assumes that one of the branches (stored in `base`) is used as a reference and compares it
    against other branches in the tree dictionary. If a duplicate structure is found, the function
    returns True.

    Parameters:
    tree_dict (dict): A dictionary representing a tree structure with nodes as keys and sub-trees as values.
                      It is assumed to have a 'base' branch initially stored under the None key.

    Returns:
    bool: True if a duplicate structure is found, False otherwise.
    """
    base = tree_dict.pop(None)  # Assumes there is a base structure under the None key
    nodes = set(tree_dict.keys())
    for key in base.keys():
        for node in nodes:
            if key in tree_dict[node].keys():
                if _check_branch(base[key], tree_dict[node][key]):
                    return True
    return False


def _check_branch(base, other):
    """
    Compares two branches of a tree structure to determine if they are identical.

    This recursive function checks if two branches (`base` and `other`) of a tree are identical by
    comparing their keys and corresponding sub-branches. If both branches are empty, they are considered
    identical.

    Parameters:
    base (dict): A dictionary representing a branch of a tree.
    other (dict): Another dictionary representing a branch of a tree to compare with `base`.

    Returns:
    bool: True if both branches are identical, False otherwise.
    """
    if base == {} and other == {}:
        return True

    for key in base.keys():
        if key in other:
            # Check if the sub-branches are identical
            if not _check_branch(base[key], other[key]):
                return False
        else:
            return False

    return True
