
;; Create library llm_test if not exists
libName = "llm_test"
if( isDir(sprintf(nil "~/%s" libName)) then
    printf("Library %s already exists\n" libName)
else
    ddCreateLib(libName "" "" "tt")
    printf("Created library %s\n" libName)
)
