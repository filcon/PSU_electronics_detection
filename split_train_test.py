import random
import os
import subprocess
import sys
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--p", required=True, help="test percentage")
ap.add_argument("--f", required=True, help="images folder")
args = ap.parse_args()


def split_data_set(percentage, folder):

    f_val = open("data_test.txt", 'w')
    f_train = open("data_train.txt", 'w')
    
    path, dirs, files = next(os.walk(folder))
    data_size = len(files)

    ind = 0
    data_test_size = int((float(percentage)/100) * data_size)
    test_array = random.sample(range(data_size), k=data_test_size)
    
    for f in os.listdir(folder):
        if(f.split(".")[1] == "jpg"):
            ind += 1
            
            if ind in test_array:
                f_val.write(folder+'/'+f+'\n')
            else:
                f_train.write(folder+'/'+f+'\n')

split_data_set(args.p, args.f) 
