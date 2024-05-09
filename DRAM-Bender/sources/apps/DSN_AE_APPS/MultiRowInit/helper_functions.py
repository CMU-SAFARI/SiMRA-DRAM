def read_result_file(file_name):
    # Initialize an empty list to store the results
    res = []

    # Open the file in read mode
    with open(file_name, 'r') as fp:
        # Read the file content, split it by comma and iterate over the items
        for item in fp.read().split(','):
            # Convert each item to float and append it to the result list
            res.append(float(item))

    # Return the result list
    return res

def write_to_file(arr, file_name):
    # Open the file in write mode
    with open(file_name, 'w') as fp:
        # Iterate over the items in the input array
        for item in arr:
            # Write each item on a new line in the file
            fp.write("%s\n" % item)