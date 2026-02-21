
printf("=== Debug ===\n")
libs = ddGetLibList()
foreach(lib libs
    printf("Library: %s\n" lib~>name)
)
printf("---\n")
libName = "llm_test"
techLib = "tpd018bcdnv5"
libId = ddGetObj(libName)
if( libId then
    printf("Library %s exists.\n" libName)
else
    printf("Library %s does not exist.\n" libName)
    ; Try to create with default tech
    libId = dbCreateLib(libName)
    if( libId then
        printf("Created library %s.\n" libName)
    else
        printf("Failed to create library %s.\n" libName)
    )
)
"Done"
