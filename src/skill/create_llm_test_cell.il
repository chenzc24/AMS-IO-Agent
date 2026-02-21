
;; Create library llm_test if not exists
libName = "llm_test"
techLib = "tpd018bcdnv5"
cellName = "test_v2"
viewName = "layout"

;; Check if library exists
lib = ddGetObj(libName)
unless(lib
    ;; Create library
    lib = dbCreateLib(libName techLib)
    printf("Library %s created.\n" libName)
)

;; Open cellview
cv = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
unless(cv
    ;; Create cellview
    cv = dbCreateCellViewByType(libName cellName viewName "maskLayout" "w")
    printf("CellView %s/%s/%s created.\n" libName cellName viewName)
)

;; Set as edit
geSetEditCellView(cv)
printf("CellView set as edit.\n")
