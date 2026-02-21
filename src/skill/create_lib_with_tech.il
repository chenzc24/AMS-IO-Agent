
libName = "llm_test"
techLib = "tpd018bcdnv5"
cellName = "test_v2"
viewName = "layout"

; Check if library exists
libId = ddGetObj(libName)
if( !libId then
    ; Create library
    libId = dbCreateLib(libName techLib)
    printf("Library %s created with technology %s.\n" libName techLib)
else
    printf("Library %s already exists.\n" libName)
)

; Create cellview
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cvId then
    printf("CellView %s/%s/%s created.\n" libName cellName viewName)
    geSetEditCellView(cvId)
    "SUCCESS"
else
    "FAILED"
)
