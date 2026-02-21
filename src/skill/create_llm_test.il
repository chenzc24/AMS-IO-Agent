
libName = "llm_test"
cellName = "test_v2"
viewName = "layout"
techLib = "tpd018bcdnv5"
libId = ddGetObj(libName)
if( !libId then
    libId = dbCreateLib(libName techLib)
    printf("Library %s created.\n" libName)
)
cv = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cv then
    geSetEditCellView(cv)
    printf("CellView opened.\n")
)
"Done"
