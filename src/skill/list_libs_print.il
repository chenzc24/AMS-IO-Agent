
;; List all libraries
libs = ddGetObj(nil)
printf("Libraries:\n")
foreach(lib libs
    printf("%s\n" lib~>name)
)
