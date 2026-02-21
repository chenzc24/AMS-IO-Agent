
libName = "IO_RING_LIB"
cellName = "io_ring_design"
viewName = "layout"
techLib = "tpd018bcdnv5"
libId = ddGetObj(libName)
if( !libId then
    libId = dbCreateLib(libName techLib)
)
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cvId then
    hiSetCurrentWindow(cvId)
    printf("Current window set\n")
else
    printf("Failed\n")
)
