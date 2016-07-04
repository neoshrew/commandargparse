import sys
from collections import OrderedDict
from copy import deepcopy

from .errors import (
    CommandArgParseError,
    CommandArgParseMultiError,
    CommandArgParseMissingArg,
    CommandArgParseMissingArgValue,
    CommandArgParseMissingPositional,
    CommandArgParseArgValidationFailed,
    CommandArgParsePosValidationFailed,
    CommandArgParseInvalidArg,
    CommandArgParseInvalidFlag,
    CommandArgParseUndefinedArg,
    CommandArgParseUndefinedFlag,
    CommandArgParseUndefinedPositional,
    CommandArgParseExtraPositionals,
)


__ALL__ = ['ArgParser']


class ArgParser(object):
    """
    arguments:
        `name` name of parser for display purposes.
        `strict` raise exceptions on extra args/flags in parsing, or
            if an unknown arg/flag is requested.
        `allow_leftovers` whether or not to capture and store the remainder of
            the arguments if a positional argument is encoutered after
            `num_positionals` has been exhausted.

            e.g. if allow_leftovers is true, and number of defined positionals is 2
                -f -f --a=hello banana -y apple -t --x cheese bear -f -t --q=5 --p 6
            will yield:
                flags = ff, y, t
                args = a=hello, x==cheese
                positionals = banana, apple
                leftovers = bear, -f, -t, --q=5, --p, 6
    """

    def __init__(self, name='ArgParser', strict=True, allow_leftovers=False):
        self._name = name
        self._strict = strict
        self._allow_leftovers = allow_leftovers

        self._positional_defs = OrderedDict()
        self._flag_defs = dict()
        self._arg_defs = dict()

        self._parsed = False
        self._working_positional_def = None

        self._data = list()
        self._flags = dict()
        self._args = dict()
        self._positionals = dict()
        self._leftovers = list()

    def add_arg(
        self, arg_name, help='', required=False,
        parser=None, default=None
    ):
        assert arg_name not in self._arg_defs, "Duplicate arg def"

        self._arg_defs[arg_name] = {
            'help': help,
            'required': required,
            'parser': parser,
            'default': default,
        }

    def add_flag(self, flag_char, help=''):
        assert flag_char not in self._flag_defs, "Duplicate flag def"
        self._flag_defs[flag_char] = {'help': help}

    def add_positional(self, name, help='', parser=None, count=1, minimum=0):
        """`count` is the number of items to expect, and can be set
        to '*' to indicate that it should consume all positionals
        it can.
        `parser` should take a list of positional arguments.
        """
        assert name not in self._positional_defs, "Duplicate positional def"
        assert not self._positional_defs or \
                list(self._positional_defs.values())[-1]['count'] != '*', \
                "Received another positional def greey def."
        assert (isinstance(count, int) and count > 0) or count == '*', \
                "count should be an integer >0 or '*'"
        assert count == '*' or count >= minimum

        self._positional_defs[name] ={
            'help': help,
            'parser': parser,
            'count': count,
            'minimum': minimum,
        }

    def parse(self, args):
        assert self._parsed is False, "ArgParser asked to re-parse"
        self._parsed = True
        self._work_pos_def = list(deepcopy(self._positional_defs).items())

        self._data = args[::]
        working_args = args[::]

        found_break = False

        while working_args:
            if not working_args[0].startswith('-') or found_break:
                if self._parse_positional(working_args):
                    continue
                break

            curr_arg = working_args.pop(0)
            if curr_arg == '--' or found_break:
                found_break = True
                continue

            elif curr_arg.startswith('--') and curr_arg[2] != '-':
                curr_arg = curr_arg[2:] # strip leading --
                self._parse_arg(curr_arg, working_args)

            elif curr_arg.startswith('-') and curr_arg[1] != '-':
                curr_arg = curr_arg[1:] # strip leading -
                self._parse_flag(curr_arg)

            else:
                raise CommandArgParseError("Invalid token {}".format(curr_arg))

        self._leftovers = working_args

        self._validate()

    def get_arg_multi(self, arg_name):
        if arg_name in self._args:
            return self._args[arg_name][::]

        elif arg_name in self._arg_defs:
            return [self._arg_defs[arg_name]['default']]

        elif self._strict:
            raise CommandArgParseUndefinedArg(arg_name)

        else:
            return []

    def get_arg(self, arg_name):
        args = self.get_arg_multi(arg_name)
        try:
            return args[-1]
        except IndexError:
            return None

    def get_all_args_multi(self):
        return deepcopy(self._args)

    def get_all_args(self):
        return {k: v[-1] for k, v in self._args.items()}

    def get_flag_count(self, flag_name):
        if flag_name in self._flags:
            return self._flags[flag_name]

        elif flag_name not in self._arg_defs and self._strict:
            raise CommandArgParseUndefinedFlag(flag_name)

        else:
            return 0

    def get_flag(self, flag_name):
        count = self.get_flag_count(flag_name)
        return count > 0

    def get_all_flag_counts(self):
        return dict(self._flags)

    def get_all_flags(self):
        return set(k for k, v in self._flags.items() if v > 0)

    def get_all_positionals(self):
        return deepcopy(self._positionals)

    def get_positional(self, name):
        #TODO clear this up
        if name in self._positionals:
            return self._positionals[name][::]

        elif self._strict and name not in self._positional_defs:
            raise CommandArgParseUndefinedPositional(name)

        else:
            return []

    def get_leftovers(self):
        return self._leftovers[::]

    def _parse_arg(self, arg_str, working_args):
        split = arg_str.split('=')

        arg_name = split[0]
        if len(split) == 2:
            arg_val = split[1]
        else:
            try:
                arg_val = working_args.pop(0)
            except IndexError:
                arg_val = CommandArgParseMissingArgValue(arg_name)

        try:
            arg_def = self._arg_defs[arg_name]
        except KeyError:
            if self._strict:
                arg_val = CommandArgParseInvalidArg(arg_name)
            parser = None
        else:
            parser = arg_def['parser']


        if isinstance(arg_val, CommandArgParseMissingArg) or parser is None:
            fmt_arg_val = arg_val
        else:
            try:
                fmt_arg_val = parser(arg_val)
            except (ValueError, TypeError) as e:
                fmt_arg_val = CommandArgParseArgValidationFailed(arg_name, e)

        if arg_name not in self._args:
            self._args[arg_name] = [fmt_arg_val]
        else:
            self._args[arg_name].append(fmt_arg_val)

    def _parse_flag(self, flag_str):
        for flag_char in flag_str:
            if self._strict and flag_char not in self._flag_defs:
                self._flags[flag_char] = CommandArgParseInvalidFlag(flag_char)
            else:
                if flag_char not in self._flags:
                    self._flags[flag_char] = 1
                else:
                    self._flags[flag_char] += 1

    def _parse_positional(self, working_args):
        pos_defs = self._work_pos_def

        if pos_defs and pos_defs[0][1]['count'] == 0: # '*' != 0
            self._work_pos_def.pop(0)

        if not self._work_pos_def:
            return False

        pos_def_name, pos_def = pos_defs[0]

        raw_value = working_args.pop(0)

        if pos_def_name not in self._positionals:
            self._positionals[pos_def_name] = [raw_value]
        else:
            self._positionals[pos_def_name].append(raw_value)

        if isinstance(pos_def['count'], int):
            pos_def['count'] -= 1

        return True

    def _validate(self):
        errs = self._validate_args()
        errs.extend(self._validate_flags())
        errs.extend(self._validate_positionals())
        errs.extend(self._validate_leftovers())

        if len(errs) == 1:
            raise errs[0]
        elif errs:
            raise CommandArgParseMultiError(errs)

    def _validate_args(self):
        errs = list(
            arg_val
            for arg_vals in self._args.values()
            for arg_val in arg_vals
            if isinstance(arg_val, CommandArgParseError)
        )

        errs.extend(
            CommandArgParseMissingArg(arg_name)
            for arg_name, arg_def in self._arg_defs.items()
            if arg_def['required'] and arg_name not in self._args
        )

        return errs

    def _validate_flags(self):
        return [
            flag_count
            for flag_count in self._flags.values()
            if isinstance(flag_count, CommandArgParseError)
        ]

    def _validate_positionals(self):
        errs = []
        have_missing = False
        for pos_name, pos_def in self._positional_defs.items():
            values = self._positionals.get(pos_name, [])

            if pos_def['minimum'] > len(values) and not have_missing:
                errs.append(CommandArgParseMissingPositional())

            parser = pos_def['parser']
            if parser is not None:
                try:
                    self._positionals['pos_name'] = parser(values)
                except (ValueError, TypeError) as e:
                    errs.append(CommandArgParsePosValidationFailed(pos_name, e))

        return errs

    def _validate_leftovers(self):
        if not self._allow_leftovers and self._leftovers:
            return [CommandArgParseExtraPositionals()]
        return []


    def print_usage(self): # TODO
        sys.stdout.write("""USAGE:
        cmd flags args command
        flags: {}
        args: {}
""".format(self._arg_defs, self._flag_defs))



