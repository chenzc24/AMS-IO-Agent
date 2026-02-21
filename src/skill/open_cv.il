
libName = "IO_RING_LIB"
cellName = "io_ring_design"
viewName = "layout"
techLib = "tpd018bcdnv5"
libId = ddGetObj(libName)
if( !libId then
    libId = dbCreateLib(libName techLib)
    printf("Library created\n")
)
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cvId then
    printf("Cellview opened successfully\n")
    dbSave(cvId)
    printf("Saved\n")
else
    printf("Failed to open cellview\n")
)
