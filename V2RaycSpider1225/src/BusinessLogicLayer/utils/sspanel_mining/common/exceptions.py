from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException


class StaffMiningError(Exception):
    """
    Base webdriver exception.
    """

    def __init__(self, msg=None, screen=None, stacktrace=None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = f"Message: {self.msg}\n"
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += f"Stacktrace:\n{stacktrace}"
        return exception_msg


class CollectorSwitchError(StaffMiningError):
    """
    Thrown when the collector access is intercepted by man-machine verification.
    """
    pass


class CollectorNoTouchElementError(NoSuchElementException):
    """
    Thrown when the collector fails to identify the target element within the specified operating time.
    """
    pass


class ManuallyCloseTheCollectorError(NoSuchWindowException):
    """
    Thrown when the collector task is manually closed when the task is executed.
    """
    pass
