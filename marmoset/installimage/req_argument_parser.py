"""Simple module to get access to data from an http request."""


# pylint: disable=too-few-public-methods
class ReqArgumentParser:
    """Simple class to get access to data from an http request."""

    @staticmethod
    def parse_args(req):
        """Parse arguments from a request."""
        return req.form
