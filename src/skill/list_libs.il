
procedure( list_libs()
    libs = ddGetObj()
    while (libs
        printf("%L\n" libs)
        libs = ddGetNextObj(libs)
    )
    "Done"
)
