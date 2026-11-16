"""Application exceptions raised by service implementations."""


class BookNotFoundError(Exception):
    """The requested Book does not exist."""


class MemberNotFoundError(Exception):
    """The requested Member does not exist."""


class MemberHasBooksError(Exception):
    """A Member cannot be deleted while it has Books."""


class DuplicateRecordError(Exception):
    """A unique Book or Member value is already in use."""
