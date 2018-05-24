def print_list(list, header):
    print(header)
    counter = 1
    for item in list:
        print(str(counter) + ". " + item)
        counter += 1


def print_dict_keys(dictionary, header):
    print(header)
    counter = 1
    for key in dictionary.keys():
        print(str(counter) + ". " + key)
        counter += 1