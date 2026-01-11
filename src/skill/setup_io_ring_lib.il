
procedure( setup_io_ring_lib()
    ;; Setup IO ring library and cellview
    libName = "IO_RING_LIB"
    cellName = "io_ring_schematic"
    viewName = "schematic"

    ;; Create library if not exists
    if (isLib(libName) then
        printf("Library %s already exists\n" libName)
    else
        libId = dmCreateLib(libName "technology.lib" "NCSU_TechLib_FreePDK45" ".")
        printf("Created library %L\n" libId)
    )

    ;; Open schematic cellview
    cvId = dbOpenCellViewByType(libName cellName viewName "schematic" "w")
    if (cvId then
        printf("Opened cellview %s/%s/%s\n" libName cellName viewName)
        geSetEditCellView(cvId)
    else
        printf("Failed to open cellview\n")
    )

    ;; Return success
    "Library setup complete"
)
