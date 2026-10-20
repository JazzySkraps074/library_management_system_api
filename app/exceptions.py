"""Application exceptions raised by the service layer."""


class MemberNotFoundError(Exception):
    """The requested Member does not exist."""


class BookNotFoundError(Exception):
    """The requested Book does not exist."""


class MemberHasBooksError(Exception):
    """A Member cannot be deleted while they have Books with them."""