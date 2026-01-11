
procedure( open_io_ring_schematic()
    lib = "IO_RING_LIB"
    cell = "io_ring_schematic"
    view = "schematic"
    cvId = dbOpenCellViewByType(lib cell view "schematic" "w")
    if (cvId then
        printf("Opened cellview %s/%s/%s\n" lib cell view)
        geSetEditCellView(cvId)
    else
        printf("Failed to open cellview\n")
    )
    "Schematic opened"
)
