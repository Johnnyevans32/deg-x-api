from collections import deque
import math
from time import time
from typing import Any, List


def timer_func(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return wrap_func


class Node:
    def __init__(self, value: int, left=None, right=None) -> None:
        self.value = value
        self.left = left
        self.right = right


class LinkedList:
    def __init__(self, value):
        self.value = value
        self.next = None


a = Node(3)
b = Node(3)
c = Node(4)
d = Node(3)
e = Node(4)
f = Node(1)

a.left = b
a.right = c

b.left = d
b.right = e

c.right = f


#       a
#     /   \
#    b      c
#   /  \        \
#  d    e        f


def depth_first_search(root: Node | None):
    if root is None:
        return []
    stack_list = deque([root])
    result = []

    while len(list(stack_list)) > 0:
        current_node = stack_list.pop()
        result.append(current_node.value)

        stack_list.append(
            current_node.right
        ) if current_node.right is not None else None
        stack_list.append(current_node.left) if current_node.left is not None else None

    return result


def breath_first_search(root: Node | None):
    if root is None:
        return []
    stack_list = deque([root])
    result = []

    while len(list(stack_list)) > 0:
        current_node = stack_list.popleft()
        result.append(current_node.value)

        stack_list.append(current_node.left) if current_node.left is not None else None
        stack_list.append(
            current_node.right
        ) if current_node.right is not None else None

    return result


def recursive_depth_first_search(root: Node | None):
    if root is None:
        return []

    return [
        root.value,
        *recursive_depth_first_search(root.left),
        *recursive_depth_first_search(root.right),
    ]


def recursive_depth_first_search_for_target(root: Node | None, target: str):
    if root is None:
        return False

    if root.value == target:
        return True

    return recursive_depth_first_search_for_target(
        root.left, target
    ) or recursive_depth_first_search_for_target(root.right, target)


def recursive_depth_first_search_sum(root: Node | None):
    if root is None:
        return sum([])

    return sum(
        [
            root.value,
            *recursive_depth_first_search(root.left),
            *recursive_depth_first_search(root.right),
        ]
    )


def depth_first_seach_min_value(root: Node | None):

    min_value = math.inf
    if root is None:
        return min_value
    stack_list = deque([root])

    while len(list(stack_list)) > 0:
        current_node = stack_list.pop()
        if current_node.value < min_value:
            min_value = current_node.value

        stack_list.append(
            current_node.right
        ) if current_node.right is not None else None
        stack_list.append(current_node.left) if current_node.left is not None else None

    return min_value


def recursive_depth_first_seach_min_value(root: Node | None):

    if root is None:
        return math.inf

    return min(
        [
            root.value,
            recursive_depth_first_seach_min_value(root.left),
            recursive_depth_first_seach_min_value(root.right),
        ]
    )


def recursive_max_path_sum(root: Node | None):
    if root is None:
        return -math.inf

    if root.left is None and root.right is None:
        return root.value

    max_path_sum = max(
        [recursive_max_path_sum(root.left), recursive_max_path_sum(root.right)]
    )

    print(max_path_sum)

    return root.value + max_path_sum


def get_river_sizes(matrix: list[list[int]]):
    visited = [[False for num in arr_mat] for arr_mat in matrix]
    sizes = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if visited[i][j]:
                continue
            if matrix[i][j] == 0:
                continue
            transverse_river_size = depth_first_transverse(i, j, matrix, visited)
            if transverse_river_size > 0:
                sizes.append(transverse_river_size)

    return sizes


def depth_first_transverse(i, j, matrix, visited):
    current_river_size = 0
    nodes_to_search = [[i, j]]
    while len(nodes_to_search) > 0:
        current_node = nodes_to_search.pop()
        i, j = current_node
        if visited[i][j]:
            continue
        visited[i][j] = True
        if matrix[i][j] == 0:
            continue

        current_river_size += 1

        unvisted = get_unvisited_nodes(i, j, matrix, visited)
        nodes_to_search += unvisted

    return current_river_size


def get_unvisited_nodes(i, j, matrix, visited):
    unvisited_nodes = []
    if i > 0 and not visited[i - 1][j]:
        unvisited_nodes.append([i - 1, j])

    if i < len(matrix) - 1 and not visited[i + 1][j]:
        unvisited_nodes.append([i + 1, j])

    if j > 0 and not visited[i][j - 1]:
        unvisited_nodes.append([i, j - 1])

    if j < len(matrix[i]) - 1 and not visited[i][j + 1]:
        unvisited_nodes.append([i, j + 1])

    return unvisited_nodes


def shift_linked_list(head: LinkedList, k: int):
    linked_list: List[LinkedList] = []
    new_head = head
    while new_head is not None:
        linked_list.append(new_head)
        new_head = new_head.next

    formatted_k = int(abs(k) % len(linked_list) * math.copysign(1, k))
    if formatted_k == 0:
        return head
    new_tail_position = (
        len(linked_list) - 1 - formatted_k if formatted_k > 0 else -formatted_k - 1
    )
    new_head_position = (
        len(linked_list) - formatted_k if formatted_k > 0 else -formatted_k
    )

    linked_list[new_tail_position].next = None
    linked_list[-1].next = linked_list[0]

    new_head = linked_list[new_head_position]

    return new_head


@timer_func
def get_smallest_target_letter(matrix: list[list[str]]):
    visited = [[False for num in arr_mat] for arr_mat in matrix]
    sizes = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if visited[i][j]:
                continue
            if matrix[i][j] == "W":
                continue
            transverse_target_letter_size = depth_first_transverse_letter_matrix(
                i, j, matrix, visited
            )
            if transverse_target_letter_size > 0:
                sizes.append(transverse_target_letter_size)

    return min(sizes)


def depth_first_transverse_letter_matrix(i, j, matrix, visited):
    current_target_letter_size = 0
    nodes_to_search = [[i, j]]
    while len(nodes_to_search) > 0:
        current_node = nodes_to_search.pop()
        i, j = current_node
        if visited[i][j]:
            continue
        visited[i][j] = True
        if matrix[i][j] == "W":
            continue

        current_target_letter_size += 1

        unvisted = get_unvisited_nodes(i, j, matrix, visited)
        nodes_to_search += unvisted

    return current_target_letter_size


print(
    get_smallest_target_letter(
        [
            ["W", "L", "W", "W", "W"],
            ["W", "L5", "W", "W", "W"],
            ["W", "W", "W", "L", "W"],
            ["W", "W", "L", "L", "W"],
            ["L", "W", "W", "L", "L"],
            ["L", "L", "W", "W", "W"],
        ]
    )
)
# print("depthhhhh")
# print(depth_first_search(a))

# print("breathhhh")
# print(breath_first_search(a))

# print(recursive_depth_first_search(a))

# print(recursive_depth_first_search_for_target(a, "k"))

# print("summm", recursive_depth_first_search_sum(None))

# print(recursive_max_path_sum(a))

# format_matrix(
#     [
#         [1, 0, 0, 1, 0],
#         [1, 0, 1, 0, 0],
#         [0, 0, 1, 0, 1],
#         [1, 0, 1, 0, 1],
#         [1, 0, 1, 1, 0],
#     ]
# )


# head = LinkedList(0)
# head.next = LinkedList(1)
# head.next.next = LinkedList(2)
# head.next.next.next = LinkedList(3)
# head.next.next.next.next = LinkedList(4)
# head.next.next.next.next.next = LinkedList(5)


# print(shift_linked_list(head, -1).value)


# def max_transactions_with_k_txns(prices, k):

# new_array = [[0 for p in prices] for i in range(k + 1)]

# profits_last_k = [0] * len(prices)
# profits_current_k = [0] * len(prices)

# print(new_array, profits_last_k, profits_current_k)


# print(max_transactions_with_k_txns([1, 2, 1], 1))


# @timer_func
# def sumup(n: int):
#     if n == 0:
#         return 1

#     return n + sumup(n - 1)


# @timer_func
# def sumupm(n: int):
#     return (n / 2) * (1 + n)


# print(sumup(100))
# print(sumupm(100))
