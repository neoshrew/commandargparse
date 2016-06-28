import unittest

from commandargparse import (
    ArgParser,
    CommandArgParseMultiError,
    CommandArgParseMissingArg,
    CommandArgParseArgValidationFailed,
    CommandArgParsePosValidationFailed,
    CommandArgParseInvalidArg,
    CommandArgParseInvalidFlag,
    CommandArgParseUndefinedArg,
    CommandArgParseUndefinedFlag,
    CommandArgParseUndefinedPositional,
    CommandArgParseMissingArgValue,
    CommandArgParseMissingPositional,
    CommandArgParseExtraPositionals,
)


class TestArgParser(unittest.TestCase):
    def test_nostrict_noset_empty(self):
        args = []

        parser = ArgParser(strict=False)
        parser.parse(args)

        self.assertEqual(parser.get_all_args_multi(), {})
        self.assertEqual(parser.get_all_flag_counts(), {})
        self.assertEqual(parser.get_all_positionals(), {})
        self.assertEqual(parser.get_leftovers(), [])

    def test_nostrict_noset_mixed_1(self):
        args = [
            '-f', '-fp', '--a=hello', 'banana', # First positional
            '-yyy', 'apple', '-t', '--a', 'zoro', '--x', 'cheese', # Second positional (apple)
            'bear', '-f', '-t', '--q=5', '--p', '6', #These should all be leftovers
        ]

        parser = ArgParser(strict=False, allow_leftovers=True)
        parser.add_positional('tree', count=2)
        parser.parse(args)

        self.assertEqual(parser.get_all_args_multi(), {'a':['hello', 'zoro'],'x':['cheese']})
        self.assertEqual(parser.get_arg_multi('a'), ['hello', 'zoro'])
        self.assertEqual(parser.get_arg_multi('x'), ['cheese'])
        self.assertEqual(parser.get_arg_multi('noexist'), [])

        self.assertEqual(parser.get_all_args(), {'a': 'zoro', 'x': 'cheese'})
        self.assertEqual(parser.get_arg('a'), 'zoro')
        self.assertEqual(parser.get_arg('x'), 'cheese')
        self.assertIsNone(parser.get_arg('noexist'))

        self.assertEqual(parser.get_all_flag_counts(), {'f': 2, 'p': 1, 'y': 3, 't': 1})
        self.assertEqual(parser.get_flag_count('f'), 2)
        self.assertEqual(parser.get_flag_count('p'), 1)
        self.assertEqual(parser.get_flag_count('y'), 3)
        self.assertEqual(parser.get_flag_count('t'), 1)
        self.assertEqual(parser.get_flag_count('z'), 0)

        self.assertEqual(parser.get_all_flags(), {'f', 'p', 'y', 't'})
        self.assertTrue(parser.get_flag('f'))
        self.assertTrue(parser.get_flag('p'))
        self.assertTrue(parser.get_flag('y'))
        self.assertTrue(parser.get_flag('t'))
        self.assertFalse(parser.get_flag('z'))

        self.assertEqual(parser.get_all_positionals(), {'tree': ['banana', 'apple']})
        self.assertEqual(parser.get_positional('tree'), ['banana', 'apple'])

        self.assertEqual(parser.get_leftovers(), ['bear', '-f', '-t', '--q=5', '--p', '6'])

    def test_strict_valid_mixed_1(self):
        args = [
            '-f', '-fp', '--a=hello', 'banana', # First positional
            '-yyy', 'apple', '-t', '--a', 'zoro', '--x', 'cheese', # Second positional
            'bear', '-f', '-t', '--q=5', '--p', '6', #These should all be leftovers
        ]

        parser = ArgParser(strict=True, allow_leftovers=True)
        parser.add_arg('a')
        parser.add_arg('x')
        parser.add_flag('f')
        parser.add_flag('p')
        parser.add_flag('y')
        parser.add_flag('t')
        parser.add_positional('tree', count=2)
        parser.parse(args)

        self.assertEqual(parser.get_all_args_multi(), {'a':['hello', 'zoro'],'x':['cheese']})
        self.assertEqual(parser.get_arg_multi('a'), ['hello', 'zoro'])
        self.assertEqual(parser.get_arg_multi('x'), ['cheese'])

        self.assertEqual(parser.get_all_args(), {'a': 'zoro', 'x': 'cheese'})
        self.assertEqual(parser.get_arg('a'), 'zoro')
        self.assertEqual(parser.get_arg('x'), 'cheese')

        self.assertEqual(parser.get_all_flag_counts(), {'f': 2, 'p': 1, 'y': 3, 't': 1})
        self.assertEqual(parser.get_flag_count('f'), 2)
        self.assertEqual(parser.get_flag_count('p'), 1)
        self.assertEqual(parser.get_flag_count('y'), 3)
        self.assertEqual(parser.get_flag_count('t'), 1)

        self.assertEqual(parser.get_all_flags(), {'f', 'p', 'y', 't'})
        self.assertTrue(parser.get_flag('f'))
        self.assertTrue(parser.get_flag('p'))
        self.assertTrue(parser.get_flag('y'))
        self.assertTrue(parser.get_flag('t'))

        self.assertEqual(parser.get_all_positionals(), {'tree': ['banana', 'apple']})
        self.assertEqual(parser.get_positional('tree'), ['banana', 'apple'])

        self.assertEqual(parser.get_leftovers(), ['bear', '-f', '-t', '--q=5', '--p', '6'])

    def test_strict_invalid_arg(self):
        args = ['--a', 1]

        parser = ArgParser(strict=True)

        with self.assertRaises(CommandArgParseInvalidArg):
            parser.parse(args)

    def test_strict_invalid_flag(self):
        args = ['-a']

        parser = ArgParser(strict=True)

        with self.assertRaises(CommandArgParseInvalidFlag):
            parser.parse(args)

    def test_strict_missing_arg(self):
        args = []

        parser = ArgParser(strict=True)
        parser.add_arg('a', required=True)

        with self.assertRaises(CommandArgParseMissingArg):
            parser.parse(args)

    def test_strict_undefined_arg(self):
        args = []

        parser = ArgParser(strict=True)
        parser.parse(args)

        with self.assertRaises(CommandArgParseUndefinedArg):
            parser.get_arg('not-exist')

    def test_strict_undefined_flag(self):
        args = []

        parser = ArgParser(strict=True)
        parser.parse(args)

        with self.assertRaises(CommandArgParseUndefinedFlag):
            parser.get_flag('x')

    def test_arg_default(self):
        args = []

        parser = ArgParser(strict=True)
        parser.add_arg('a', default='banana')

        parser.parse(args)

        self.assertEqual(parser.get_arg('a'), 'banana')

    def test_parse_error(self):
        args = ['--a', 'banana']
        def a_parser(*args, **kwargs):
            self.assertEqual(kwargs, {})
            self.assertEqual(args, ('banana',))
            raise TypeError('Banana is not a vegetable')

        parser = ArgParser()
        parser.add_arg('a', parser=a_parser)

        with self.assertRaises(CommandArgParseArgValidationFailed):
            parser.parse(args)

    def test_positional_arguments_1(self):
        args = ['delicious', 'apple', 'pie']

        parser = ArgParser(strict=False)
        parser.add_positional('adjective', count=1)
        parser.add_positional('nouns', count=2)
        parser.parse(args)

        self.assertEqual(parser.get_positional('adjective'), ['delicious'])
        self.assertEqual(parser.get_positional('nouns'), ['apple', 'pie'])

    def test_positional_argments_2(self):
        args = ['delicious', 'banana', 'pie']

        parser = ArgParser()
        parser.add_positional('a', count='*')

        parser.parse(args)

        self.assertEqual(parser.get_positional('a'), ['delicious', 'banana', 'pie'])

    def test_nostrict_undefined_positional(self):
        args = []

        parser = ArgParser(strict=False)
        parser.parse(args)

        self.assertEqual(parser.get_positional('not-exist'), [])

    def test_positional_args_not_filled(self):
        args = ['not', 'enough']

        parser = ArgParser()
        parser.add_positional('a', count=3, minimum=3)

        with self.assertRaises(CommandArgParseMissingPositional):
            parser.parse(args)

    def test_invalid_positional_arg(self):
        args = ['banana']

        def a_parser(*args, **kwargs):
            self.assertEqual(kwargs, {})
            self.assertEqual(args, (['banana'],))
            raise TypeError("A banana is not a vegetable!")

        parser = ArgParser()
        parser.add_positional('vegetable', parser=a_parser)

        with self.assertRaises(CommandArgParsePosValidationFailed):
            parser.parse(args)

    def test_undefied_positional_flag(self):
        args = []

        parser = ArgParser(strict=True)
        parser.parse(args)

        with self.assertRaises(CommandArgParseUndefinedPositional):
            parser.get_positional('not-exist')

    def test_argument_end_flag(self):
        args = ['-a', '--b=B', '--A', 'A', '--', '-b', '--b=B', '--A', 'A']

        parser = ArgParser(strict=False, allow_leftovers=True)
        parser.parse(args)

        self.assertEqual(parser.get_all_args_multi(), {'b': ['B'], 'A': ['A']})
        self.assertEqual(parser.get_all_flag_counts(), {'a': 1})
        self.assertEqual(parser.get_all_positionals(), {})
        self.assertEqual(parser.get_leftovers(), ['-b', '--b=B', '--A', 'A'])

    def test_argument_end_flag_defined_positionals(self):
        args = ['banana', '--', 'apple']

        parser = ArgParser(strict=False, allow_leftovers=True)
        parser.add_positional('a', count='*')

        parser.parse(args)

        self.assertEqual(parser.get_all_positionals(), {'a': ['banana', 'apple']})
        self.assertEqual(parser.get_leftovers(), [])

    def test_missing_arg_value(self):
        args = ['--A']

        parser = ArgParser(strict=False)

        with self.assertRaises(CommandArgParseMissingArgValue):
            parser.parse(args)

    def test_too_many_positionals(self):
        args = ['hello']

        parser = ArgParser(strict=True)

        with self.assertRaises(CommandArgParseExtraPositionals):
            parser.parse(args)

    def test_multi_error(self):
        args = ['-a', '--b', 'b', 'banana']

        parser = ArgParser(strict=True)

        try:
            parser.parse(args)

        except CommandArgParseMultiError, e:
            pass
            #TODO check the errors are as expected?

        else:
            self.fail("CommandArgParseMultiError not raised")

