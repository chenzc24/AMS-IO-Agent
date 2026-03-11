
;; Create cellview llm_test/IO_RING_12x12/schematic
libName = "llm_test"
cellName = "IO_RING_12x12"
viewName = "schematic"
cvId = ddGetObj(libName cellName viewName)
when(cvId
    printf("CellView %s/%s/%s already exists\n" libName cellName viewName)
    ; else create it
    cvId = dbOpenCellViewByType(libName cellName viewName "schematic" "w")
    printf("Created cellview %s/%s/%s\n" libName cellName viewName)
)
