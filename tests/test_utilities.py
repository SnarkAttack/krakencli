def lists_match(list1, list2):
    return sorted(list1) == sorted(list2)


def list_in_list(list1, list2):
    return all(e in list2 for e in list2)


def dict_value_length_check(key, dict, comp_dict):
    print(dict[key])
    print(comp_dict[key])
    return len(dict[key]) == comp_dict[key]
