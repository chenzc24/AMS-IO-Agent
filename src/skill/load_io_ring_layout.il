;; SKILL tool to load IO ring layout
libName = "llm_test"
cellName = "test_v1"
viewName = "layout"

;; Check if library exists
libId = ddGetObj(libName)
when(!libId
    libId = dbCreateLib(libName)
    printf("Created library %s\n" libName)
)

;; Open cellview (create if not exist)
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
when(!cvId
    printf("Failed to open cellview %s/%s/%s\n" libName cellName viewName)
    exit()
)
geSetEditCellView(cvId)
printf("Cellview opened and set as current edit.\n")

;; Load the layout IL file
load("output/turn_20260225_225852/io_ring_layout.il")
