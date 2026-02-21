
;; Create library IO_RING_LIB if not exists
libName = "IO_RING_LIB"
cellName = "io_ring_design"
viewName = "layout"
techLib = "tpd018bcdnv5"
libId = ddGetObj(libName)
when( !libId
    libId = dbCreateLib(libName techLib)
    printf("Created library %s\n" libName)
)
;; Open cellview
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cvId then
    printf("Opened cellview %s/%s/%s\n" libName cellName viewName)
else
    printf("Failed to open cellview\n")
)
