
;; Create library and cellview if not exist
procedure(createLibCell(libName cellName viewName)
    let((libId cellId)
        libId = ddGetObj(libName)
        when(!libId
            libId = dbCreateLib(libName)
            printf("Created library %s\n" libName)
        )
        cellId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
        printf("Opened cellview %s/%s/%s\n" libName cellName viewName)
        t
    )
)
