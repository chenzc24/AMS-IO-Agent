
;; open_cell.il
libName = "tpd018bcdnv5"
cellName = "test_io_ring"
viewName = "schematic"
cvId = dbOpenCellView(libName cellName viewName)
unless(cvId
    cvId = dbCreateCellView(libName cellName viewName)
    printf("Created cellview %s/%s/%s\n" libName cellName viewName)
)
geSetEditCellView(cvId)
printf("Edit cellview set.\n")
t
