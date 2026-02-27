
;; Load layout IL file
procedure( load_layout_il()
    let((cv filePath)
        filePath = "output/turn_20260225_145047/io_ring_layout.il"
        ;; Ensure a cellview is open
        cv = geGetWindowCellView()
        unless(cv
            ;; Try to open default cellview
            cv = dbOpenCellViewByType("llm_test" "test_v2" "layout" "maskLayout" "w")
            unless(cv
                printf("No cellview open and cannot create one\n")
                return(nil)
            )
        )
        ;; Load the file
        load(filePath)
        printf("Loaded layout IL file %s\n" filePath)
        t
    )
)
