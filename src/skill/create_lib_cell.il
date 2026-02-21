
;; Create library and cellview if not exists
procedure(create_lib_cell(libName cellName viewName)
    let((cv)
        unless( ddGetObj(libName)
            ddCreateLib(libName nil nil "ams")
        )
        cv = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
        if( cv then
            hiSetCurrentWindow(cv~>window)
            println("Created and opened cellview " libName "/" cellName "/" viewName)
            return(t)
        else
            println("Failed to open cellview")
            return(nil)
        )
    )
)
