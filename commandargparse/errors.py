
__ALL__ = [
    'CommandArgParseError',
    'CommandArgParseMultiError',
    'CommandArgParseMissingArg',
    'CommandArgParseMissingArgValue',
    'CommandArgParseArgValidationFailed',
    'CommandArgParsePosValidationFailed',
    'CommandArgParseInvalidArg',
    'CommandArgParseInvalidFlag',
    'CommandArgParseUndefinedArg',
    'CommandArgParseUndefinedFlag',
    'CommandArgParseUndefinedPositional',
    'CommandArgParseMissingPositional',
    'CommandArgParseExtraPositionals',
]

banana = 1

class CommandArgParseError(Exception):
    pass

#
# Errors during parsing
#
class CommandArgParseMultiError(CommandArgParseError):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        # TODO
        return "Multple errors: {0}".format(self.errors)


class CommandArgParseMissingArg(CommandArgParseError):
    def __init__(self, arg_name):
        super(CommandArgParseMissingArg, self).__init__(arg_name)
        self.arg_name = arg_name

    def __str__(self):
        return 'Missing argument "{0}"'.format(self.arg_name)


class CommandArgParseMissingArgValue(CommandArgParseError):
    def __init__(self, arg_name):
        super(CommandArgParseMissingArgValue, self).__init__(arg_name)
        self.arg_name = arg_name

    def __str__(self):
        return 'Missing value for argument "{0}"'.format(self.arg_name)


class CommandArgParseArgValidationFailed(CommandArgParseError):
    def __init__(self, arg_name, error):
        super(CommandArgParseArgValidationFailed, self).__init__(arg_name, error)
        self.arg_name = arg_name
        self.error = error

    def __str__(self):
        #TODO make nice?
        return "Failed to validate {}:{}".format(self.arg_name, self.error)

class CommandArgParsePosValidationFailed(CommandArgParseError):
    def __init__(self, value, error):
        super(CommandArgParsePosValidationFailed, self).__init__(value, error)
        self.value = value
        self.error = error

    def __str__(self):
        #TODO make nice?
        return "Invalid argument {}:{}".format(self.value, self.error)


class CommandArgParseInvalidArg(CommandArgParseError):
    def __init__(self, arg_name):
        super(CommandArgParseInvalidArg, self).__init__(arg_name)
        self.arg_name = arg_name

    def __str__(self):
        return "Received undefined argument {0}".format(self.arg_name)


class CommandArgParseInvalidFlag(CommandArgParseError):
    def __init__(self, flag):
        super(CommandArgParseInvalidFlag, self).__init__(flag)
        self.flag = flag

    def __str__(self):
        return "Received undefined flag {0}".format(self.flag)


class CommandArgParseUndefinedPositional(CommandArgParseError):
    def __init__(self, flag):
        super(CommandArgParseUndefinedPositional, self).__init__(flag)
        self.flag_name = flag

    def __str__(self):
        return "Undefined positional {0}".format(self.flag)


class CommandArgParseExtraPositionals(CommandArgParseError):
    def __init__(self):
        super(CommandArgParseExtraPositionals, self).__init__()

    def __str__(self):
        return "Received extra arguments"

#
# Errors during running
#
class CommandArgParseUndefinedArg(CommandArgParseError):
    def __init__(self, arg_name):
        super(CommandArgParseUndefinedArg, self).__init__(arg_name)
        self.arg_name = arg_name

    def __str__(self):
        return "Undefined arg {0}".format(self.arg_name)


class CommandArgParseUndefinedFlag(CommandArgParseError):
    def __init__(self, flag):
        super(CommandArgParseUndefinedFlag, self).__init__(flag)
        self.flag_name = flag

    def __str__(self):
        return "Undefined flag {0}".format(self.flag)


class CommandArgParseMissingPositional(CommandArgParseError):
    def __init__(self):
        super(CommandArgParseMissingPositional, self).__init__()

    def __str__(self):
        return "Not enough arguments"


