class Node:
    def __init__(self, data):
        self.data = data
        self.next_node = None
        self.prev_node = None


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev_node = self.tail
            self.tail.next_node = new_node
            self.tail = new_node

    def get(self, data):
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next_node
        return None

    def display(self):
        current = self.head
        while current:
            print(current.data, end=" <-> ")
            current = current.next_node
        print("None")
