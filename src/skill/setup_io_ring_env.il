
;; Setup IO ring environment
libName = "IO_RING_LIB"
cellName = "io_ring_design"
viewName = "layout"

unless( ddGetObj(libName)
    ddCreateLib(libName nil nil "ams")
)

cv = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cv then
    hiSetCurrentWindow(cv~>window)
    println("Opened cellview " libName "/" cellName "/" viewName)
    return(t)
else
    println("Failed to open cellview")
    return(nil)
)
