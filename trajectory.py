import numpy as np

def gen_path(width, length, height, step, padding):
    inverse = False
    #print(max_width)
    for i in np.arange(2*padding,length-padding*2+0.01,step):
        match inverse:
            case False:
                for j in np.arange(padding,width-padding + 0.01,step):
                    print("(%.3f,%.3f,%.3f,0)" % (i,j,height), end = ",\n")
                inverse = True
            case True:
                for j in np.arange(width - padding,padding-0.01,-step):
                    print("(%.3f,%.3f,%.3f,0)" % (i,j,height), end = ",\n")
                inverse = False

    return


if __name__ =="__main__":
    gen_path(2.2,5.3,1.5,0.3,0.5) #values in mts