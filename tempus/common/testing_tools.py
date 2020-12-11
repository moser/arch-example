from tempus.lib.utils.wrapper import Wrapper


class FakeMessageBus:
    def __init__(self):
        self.messages = []
        self.return_values = {}

    def handle(self, message):
        self.messages.append(message)
        return self.return_values.get(message.__class__, None)


class SqlAlchemyNoCommitWrapper(Wrapper):
    def commit(self):
        self.wrapped._session.flush()
