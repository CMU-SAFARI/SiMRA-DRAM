import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def b2i(binary):
    return int(binary, 2)

def d2b(decimal,length):
    return bin(decimal)[2:].zfill(length)

def maj_all_1_0_pattern_creator(n_open_rows,input_size,r_frac_idx,pattern):
    lst = []
    pattern_str = d2b(pattern, input_size)
    for i in range(input_size):
        lst.append(b2i(pattern_str[i]*32))
    lst = lst*int((n_open_rows-1)/input_size)
    remaning = n_open_rows - len(lst)
    for i in range(remaning):
        lst.append(b2i('1'*32))
    if remaning > 1:
        for lst_idx,i in enumerate(r_frac_idx):    
            #swap with random element
            lst[n_open_rows-remaning+lst_idx] = lst[i]
            lst[i] = b2i('1'*32)
    else:
        lst[-1] = lst[r_frac_idx[0]]
        lst[r_frac_idx[0]] = b2i('1'*32)
    return lst

def write_to_file(arr,file_name):
    with open(file_name, 'w') as fp:
        for item in arr:
            # write each item on a new line
            fp.write("%s\n" % item)

def read_result_file(file_name):
    res = []
    with open(file_name, 'r') as fp:
        for item in fp.read().split(','):
            res.append(float(item))
    return res