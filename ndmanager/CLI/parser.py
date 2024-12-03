import argparse as ap
import abc


class Command:
    """A class that defines how command classes should look like.
    Command classes should both define a `parser` and `run` method."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, args: ap.Namespace) -> None:
        """When the class is called, simply run the
        `run` command

        Args:
            args (ap.Namespace): The CLI arguments namespace
        """
        self.run(args)

    @classmethod
    @abc.abstractmethod
    def parser(self, subparsers: ap._SubParsersAction):  # pragma: no cover
        """This should define a parser to add to the subparser list

        Args:
            subparsers (ap._SubParsersAction): A subparser object
        """
        pass

    @abc.abstractmethod
    def run(self, args: ap.Namespace) -> None:  # pragma: no cover
        """This should define what the command does based on the passed
        CLI arguments

        Args:
            args (ap.Namespace): The CLI arguments namespace
        """
        pass
