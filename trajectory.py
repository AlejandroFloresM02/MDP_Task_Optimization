import numpy as np

def gen_path(width, length, height, step):
    inverse = False
    max_width = width//step * step
    print(max_width)
    for i in np.arange(0,length,step):
        match inverse:
            case False:
                for j in np.arange(step,width + 0.01,step):
                    print("[%.3f,%.3f,%.3f]" % (j,i,height), end = ";")
                inverse = True
            case True:
                for j in np.arange(max_width,step - 0.01,-step):
                    print("[%.3f,%.3f,%.3f]" % (j,i,height), end = ";")
                inverse = False

    return


if __name__ =="__main__":
    gen_path(2.1,5.32,1.8,.3) #values in mts