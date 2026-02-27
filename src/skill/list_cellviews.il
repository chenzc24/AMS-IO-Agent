
;; List cellviews of a given library and cell
procedure(listCellViews(libName cellName)
    let((libId cellId)
        libId = ddGetObj(libName)
        unless(libId error("Library %s not found" libName))
        cellId = dbFindCellByName(libId cellName)
        unless(cellId error("Cell %s not found in library %s" cellName libName))
        foreach(cvId cellId~>cellViews
            printf("View: %s\n" cvId~>viewName)
        )
        t
    )
)
listCellViews("llm_test" "test_v2")
