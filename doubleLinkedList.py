class Node:
    """
    Nodo para una Lista Doblemente Enlazada.

    Esta clase representa un nodo individual en una Lista Doblemente Enlazada.
    Cada nodo almacena un dato y referencias a los nodos siguiente y anterior en la lista.

    Atributos:
        data (any): El dato almacenado en el nodo.
        next_node (Node, None): Referencia al siguiente nodo en la lista (puede ser None).
        prev_node (Node, None): Referencia al nodo anterior en la lista (puede ser None).
    """
    def __init__(self, data):
        self.data = data
        self.next_node = None
        self.prev_node = None


class DoubleLinkedList:
    """
    Lista Doblemente Enlazada.

    Esta clase representa una Lista Doblemente Enlazada, que es una estructura de datos
    lineal donde cada nodo contiene un dato y referencias a los nodos siguiente y anterior.

    Atributos:
        head (Node, None): Referencia al nodo inicial de la lista (puede ser None).
        tail (Node, None): Referencia al nodo final de la lista (puede ser None).
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, data):
        """
        Agrega un nuevo nodo al final de la lista.

        Args:
            data (any): El dato a almacenar en el nuevo nodo.

        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev_node = self.tail
            self.tail.next_node = new_node
            self.tail = new_node

    def get(self, data):
        """
        Busca un nodo con un dato específico en la lista.

        Args:
            data (any): El dato a buscar en el nodo.

        Returns:
            Node: El nodo encontrado con el dato especificado, o None si no se encuentra.
        """
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next_node
        return None

    def display(self):
        """
        Imprime el contenido de la lista enlazada.

        Imprime el contenido de cada nodo en la lista,
        mostrando el dato y la dirección de memoria del siguiente nodo.
        """
        current = self.head
        while current:
            print(current.data, end=" <-> ")
            current = current.next_node
        print("None")
