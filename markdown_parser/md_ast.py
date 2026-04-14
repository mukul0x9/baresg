class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self):
        return f"Node({self.type}, value={self.value}, children={self.children})"
