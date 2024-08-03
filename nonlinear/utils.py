def detect_position_changes(input_index: list[int]) -> list[tuple[int, int]]:
    """
    Detects changes in position of elements a list of indexes
    Returns a list of tuples with the element and the new position.
    """
    changes = []
    for i1,i2 in enumerate(input_index):
        if i1 != i2:
            changes.append((i1, i2))
    return changes



def swap_task_positions(
    tasks_order_old = [2, 3, 5, 6, 19, 25], 
    tasks_order = [25, 2, 3, 5, 6, 19],
    tasks_index = [5, 0, 1, 2, 3, 4],
    tasks_id = [25, 2, 3, 5, 6, 19],
):
    tasks_order = [1, 2, 5, 20, 15, 18]
    tasks_index = [0, 1, 2, 5, 3, 4]
    tasks_id = [25, 2, 5, 19, 3, 6]

    old_order = [None] * len(tasks_order)
    for i,j in enumerate(tasks_index):
        old_order[j] = tasks_order[i]


    

    



    for i,j in enumerate(tasks_order):
        ...
        # print(tasks_index[i]
    return None


if __name__ == "__main__":
    swap_task_positions()

    

