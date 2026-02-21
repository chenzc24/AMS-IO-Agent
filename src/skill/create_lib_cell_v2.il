
;; Create library and cell if they don't exist
procedure(createLibCell(libName cellName viewName)
    let((lib cellView)
        ; Check if library exists
        unless(ddGetObj(libName)
            lib = dbCreateLib(libName)
            printf("Created library %s\n" libName)
        )
        ; Open or create cellView
        cellView = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
        if(cellView then
            printf("Opened cellView %s/%s/%s\n" libName cellName viewName)
        else
            printf("Failed to open/create cellView\n")
        )
        cellView
    )
)
