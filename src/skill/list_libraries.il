
;; list_libraries.il
libs = ddGetLibList()
foreach(lib libs
    printf("%s\n" lib~>name)
)
