a = 1
b = 2

def var:
    global a
    global b
    
    a+=1
   

def var2:
    global a
    global b

    b+=1
    print a


print a
var()
print a
var2()
