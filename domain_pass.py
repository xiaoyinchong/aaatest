# -*- coding: utf-8 -*-


f1 = open('shuzi.txt','rb')
f2 = open('zimu.txt','rb')
zimu=[]
shuzi=[]

f3 = open('mm.txt','wb')
while 1:
    i=f1.readline()
    if i.strip() != '':
        shuzi.append(i.strip())
        print i
    else:
        break

while 1:
    j=f2.readline()
    if j.strip() != '':
        zimu.append(j.strip())
        print j
    else:
        break

for i in zimu:
    for j in shuzi:
        f3.write(i+j+'\n')
        f3.write(i+'@'+j+'\n')
        f3.write(i+'_'+j+'\n')
    f3.write(i+'\n')

f1.close()
f2.close()
f3.close()


