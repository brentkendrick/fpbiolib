def make_list_vals_unique(input_list):
    output_list = []
    count = 1
    for name in input_list:
        if name not in output_list:
            output_list.append(name)
        else:
            output_list.append(f"{name}_{count}")
            count += 1
    return output_list
