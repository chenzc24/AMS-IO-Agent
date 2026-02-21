
libs = ddGetObj()
while( libs
    printf("%s\n" libs~>name)
    libs = libs~>next
)
"Done"
