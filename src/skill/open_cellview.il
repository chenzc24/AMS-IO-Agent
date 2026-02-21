
;; Open or create cellview
libName = "llm_test"
cellName = "test_v2"
viewName = "layout"

lib = ddGetObj(libName)
when(!lib
    lib = dbCreateLib(libName)
    printf("Library %s created.\n" libName)
)
cv = dbOpenCellViewByType(lib cellName viewName "maskLayout" "w")
if(cv then
    printf("CellView opened.\n")
else
    cv = dbCreateCellViewByType(lib cellName viewName "maskLayout" "w")
    printf("CellView created.\n")
)
geSetEditCellView(cv)
return(sprintf("CellView %s/%s/%s ready." libName cellName viewName))
