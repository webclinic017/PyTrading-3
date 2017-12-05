from abc import ABCMeta, abstractmethod


class NotEnoughBytes(BaseException):
    """ Unable to decode message, available bytes are less than required """


class Serialization:
    __metaclass__ = ABCMeta

    # TODO: change buffer variable name
    @abstractmethod
    def decode_header(self, buffer):
        pass

    # TODO: change buffer variable name
    @abstractmethod
    def decode_buffer(self, buffer):
        pass

    @abstractmethod
    def encode_referential(self, referential):
        pass

    @abstractmethod
    def decode_referential(self, encoded_referential):
        pass

    @abstractmethod
    def encode_order_book(self, order_book):
        pass

    @abstractmethod
    def decode_order_book(self, encoded_order_book):
        pass

    @abstractmethod
    def encode_create_order(self, create_order):
        pass

    @abstractmethod
    def decode_create_order(self, encoded_create_order):
        pass

    @abstractmethod
    def encode_logon(self, logon):
        pass

    @abstractmethod
    def decode_logon(self, encoded_logon):
        pass
