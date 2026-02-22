
;; create_library_and_open.il
;; Creates a library and opens a cellview for IO ring design

libName = "IO_RING_LIB"
cellName = "io_ring_design"
viewName = "schematic"

;; Check if library exists
when( ddGetObj(libName)
    printf("Library %s already exists\n" libName)
    ;; Open the cellview
    cv = dbOpenCellViewByType(libName cellName viewName "schematic")
    if( cv then
        printf("Opened cellview %s/%s/%s\n" libName cellName viewName)
        geSetEditCellView(cv)
    else
        printf("Failed to open cellview\n")
    )
    t
    ;; Library doesn't exist, create it
    libId = dbCreateLib(libName)
    if( libId then
        printf("Created library %s\n" libName)
        cv = dbCreateCellViewByType(libId cellName viewName "schematic")
        if( cv then
            printf("Created cellview %s/%s/%s\n" libName cellName viewName)
            geSetEditCellView(cv)
        else
            printf("Failed to create cellview\n")
        )
    else
        printf("Failed to create library\n")
    )
)
