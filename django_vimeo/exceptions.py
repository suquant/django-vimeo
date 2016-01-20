class VimeoException(Exception):
    """ Parental class for all django_vimeo exceptions """
    pass


class VideoDoesntExistException(VimeoException):
    """ Exception thrown if video doesn't exist """
    pass


class UnknownIdException(VideoDoesntExistException):
    """
    Exception thrown if backend is detected, but video ID cannot be parsed.
    """
    pass


class SpaceNotEnoughtException(VimeoException):
    """
    Exception thrown if backend is detected, but video ID cannot be parsed.
    """
    pass