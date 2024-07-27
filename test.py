sample_dict = {'apple': 5, 'banana': 2, 'orange': 8, 'grape': 1}
sorted_keys = sorted(sample_dict, key=lambda k: sample_dict[k])
print(sorted_keys)
