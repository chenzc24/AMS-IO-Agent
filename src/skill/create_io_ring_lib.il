
procedure( create_io_ring_lib()
    libName = "IO_RING_LIB"
    techLib = "tpd018bcdnv5"
    if (isLib(libName) then
        printf("Library %s already exists\n" libName)
    else
        libId = dmCreateLib(libName "technology.lib" techLib ".")
        printf("Created library %L\n" libId)
    )
    "Library creation done"
)
