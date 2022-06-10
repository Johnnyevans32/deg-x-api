import math
from collections import deque
from time import time


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
    linked_list: list[LinkedList] = []
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


# print(
#     get_smallest_target_letter(
#         [
#             ["W", "L", "W", "W", "W"],
#             ["W", "L5", "W", "W", "W"],
#             ["W", "W", "W", "L", "W"],
#             ["W", "W", "L", "L", "W"],
#             ["L", "W", "W", "L", "L"],
#             ["L", "L", "W", "W", "W"],
#         ]
#     )
# )
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


def valid_paren(s: str) -> bool:
    """
    :type s: str - String to be tested for validity
    :rtype: bool - Returns true if the string is valid else false
    """
    if not s:
        return False
    if s[0] in ["}", ")", "]"]:
        return False
    if s[-1] in ["[", "{", "("]:
        return False
    stack = []
    for i in range(len(s)):
        if s[i] == "(" or s[i] == "{" or s[i] == "[":
            stack.append(s[i])
        else:
            top = stack[-1]
            if (
                s[i] == ")"
                and top == "("
                or s[i] == "]"
                and top == "["
                or s[i] == "}"
                and top == "{"
            ):
                stack.pop()
            else:
                return False
    return True


def traverse_list_for_node_difference(nodes: list[int]):
    count = 0
    current_highest_diff = 0
    for x in range(len(nodes)):
        for y in range(x + 1, len(nodes)):
            print(x, y)
            count += 1
            diff = nodes[y] - nodes[x]
            if diff > current_highest_diff:
                current_highest_diff = diff

    print(count)
    return current_highest_diff


# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")


def get_missing_number(A):
    # write your code in Python 3.6
    max_num = max(A)
    if max_num <= 0:
        return 1
    formated_A = [*range(1, max_num)]
    diff = list(set(formated_A) - set(sorted(A)))
    diff.index()
    if diff:
        return diff[0]
    return max_num + 1


def get_binary_gap(N):

    """
    that, given a positive integer N, returns the length of its lon
    gest binary gap. The function should return 0 if N doesn't
    contain a binary gap.
    """
    # write your code in Python 3.6
    base_num = "{0:b}".format(int(N))
    gap_arr = []
    gap_count = 0
    for n in base_num:
        if n == "1":
            gap_arr.append(gap_count)
            gap_count = 0
        else:
            gap_count += 1
    return max(gap_arr)


def fuel_distro(fuel_arr, dist_arr):
    # write your code in Python 3.6
    n = len(fuel_arr)
    trips = dict()
    for i in range(n):
        trips[(i, i, i)] = fuel_arr[i]
    max_towns = 1
    for _ in range(n):
        new_trips = dict()
        for k, cur_fuel in trips.items():
            start, end, cur_town = k
            if (
                start - 1 >= 0
                and abs(dist_arr[cur_town] - dist_arr[start - 1]) <= cur_fuel
            ):
                new_start = start - 1
                new_fuel = (
                    cur_fuel
                    - abs(dist_arr[cur_town] - dist_arr[start - 1])
                    + fuel_arr[new_start]
                )
                new_key = (new_start, end, new_start)
                if new_key not in new_trips:
                    max_towns = max(max_towns, end - new_start + 1)
                    new_trips[new_key] = new_fuel
                else:
                    new_trips[new_key] = max(new_trips[new_key], new_fuel)
            if end + 1 < n and abs(dist_arr[end + 1] - dist_arr[cur_town]) <= cur_fuel:
                new_end = end + 1
                new_key = (start, new_end, new_end)
                new_fuel = (
                    cur_fuel
                    - abs(dist_arr[new_end] - dist_arr[cur_town])
                    + fuel_arr[new_end]
                )
                if new_key not in new_trips:
                    max_towns = max(max_towns, new_end - start + 1)
                    new_trips[new_key] = new_fuel
                else:
                    new_trips[new_key] = max(new_trips[new_key], new_fuel)
        trips = new_trips
    return max_towns


def get_req_filters_to_half_population(factories: list[float | int]):
    total_pop = sum(factories)
    target_pop = total_pop / 2
    filters = 0
    while total_pop > target_pop:
        factories.sort(reverse=True)
        factories[0] = factories[0] / 2
        total_pop = sum(factories)
        filters += 1

    return filters


def get_change(amount_given: int, price: int):
    # list_of_change = ['1c', '5c', '10c', '25c', '50c'," $1"]
    change = (amount_given - price) * 100
    change_result = [0, 0, 0, 0, 0, 0]

    index_change = {
        0: 1,
        1: 5,
        2: 10,
        3: 25,
        4: 50,
        5: 100,
    }

    for i in range(len(change_result) - 1, -1, -1):
        change_result[i] = int(change // index_change[i])
        change -= change_result[i] * index_change[i]

    return change_result


# print(traverse_list_for_node_difference([14, 20, 4, 12, 5, 11, 2, 4]))
# print(traverse_list_for_node_difference([1, 2, 3, 4, 5, 6]))


# input1 = "{{}}()[()]"
# input2 = "{][}"
# input3 = ")"
# print(valid_paren(input1))
# print(valid_paren(input2))
# print(valid_paren(input3))


def get_best_block_based_users_req(
    reqs: list[str],
    blocks: list[dict[str, str]],
):

    block_index_score: list[int] = []
    for i in range(len(blocks)):
        block_index_score.insert(i, 0)
        for req in reqs:
            # print(i, block_index_score, req)
            if blocks[i][req]:
                # block_index_score[i].append(0)
                continue

            lowest_distance = 999999999
            for n in range(len(blocks)):
                if n == i:
                    continue
                if blocks[n][req]:
                    if abs(n - i) < lowest_distance:
                        lowest_distance = abs(n - i)
            if lowest_distance > block_index_score[i]:
                block_index_score[i] = lowest_distance

    return min(block_index_score)


# print(
#     get_best_block_based_users_req(
#         ["gym", "school", "store"],
#         [
#             {"gym": False, "school": True, "store": False},
#             {"gym": True, "school": False, "store": False},
#             {"gym": True, "school": True, "store": False},
#             {"gym": False, "school": True, "store": False},
#             {"gym": False, "school": True, "store": True},
#         ],
#     )
# )


def get_max_profit_with_k_txn(stock_list: list[int], k=1):
    # max_profit = 0
    # [1, 2, 3]
    profits: list[list[int]] = [[0] * len(stock_list) for i in range(k + 1)]
    print(profits)
    # time complexity as less than o(N^2)
    for t in range(1, k + 1):
        max_thus_far = -999999999999999999999
        for d in range(1, len(stock_list)):
            profit_on_previous_day_with_less_txn = profits[t - 1][d - 1]
            stock_price_on_previous_day = stock_list[d - 1]
            profit_on_previous_day = profits[t][d - 1]
            stock_price_on_day = stock_list[d]
            new_max_thus_far = (
                profit_on_previous_day_with_less_txn - stock_price_on_previous_day
            )
            max_thus_far = max(new_max_thus_far, max_thus_far)

            profits[t][d] = max(
                profit_on_previous_day, (stock_price_on_day + max_thus_far)
            )

            print(
                t,
                d,
                stock_price_on_day,
                stock_price_on_previous_day,
                profit_on_previous_day,
                profit_on_previous_day_with_less_txn,
                new_max_thus_far,
                profits[t][d],
            )
    print(profits)
    return profits[-1][-1]


def get_max_profit_with_k_txn_op(stock_list: list[int], k=1):
    # max_profit = 0
    even_profits = [0] * len(stock_list)
    odd_profits = [0] * len(stock_list)
    # time complexity as less than o(N^2)
    for t in range(1, k + 1):
        # print(odd_profits, even_profits)
        max_thus_far = -999999999999999999999
        if t % 2 == 1:
            current_profits = odd_profits
            previous_profits = even_profits
        else:
            current_profits = even_profits
            previous_profits = odd_profits
        # print(odd_profits, even_profits)
        for d in range(1, len(stock_list)):
            profit_on_previous_day_with_less_txn = previous_profits[d - 1]
            stock_price_on_previous_day = stock_list[d - 1]
            profit_on_previous_day = current_profits[d - 1]
            stock_price_on_day = stock_list[d]
            new_max_thus_far = (
                profit_on_previous_day_with_less_txn - stock_price_on_previous_day
            )
            max_thus_far = max(new_max_thus_far, max_thus_far)
            print(odd_profits, even_profits)
            current_profits[d] = max(
                profit_on_previous_day, (stock_price_on_day + max_thus_far)
            )
            print(odd_profits, even_profits)

    print(odd_profits, even_profits)
    return even_profits[-1] if k % 2 == 0 else odd_profits[-1]


# print(get_max_profit_with_k_txn_op([5, 11, 3, 50, 60, 90]))


def solve_pizza_hashcode_prob(
    max_pizza_slice: int, pizza_type_count: int, pizza_types: list[int]
):
    sum_pizza_slice = 0
    index_list = []
    # pizza_types.sort(reverse=True)
    for s in range(pizza_type_count - 1, -1, -1):
        print(s)
        if sum_pizza_slice + pizza_types[s] <= max_pizza_slice:
            sum_pizza_slice += pizza_types[s]
            index_list.append(s)
        else:
            continue
    print(index_list)
    return sum_pizza_slice


print(solve_pizza_hashcode_prob(17, 4, [2, 5, 6, 8]))
