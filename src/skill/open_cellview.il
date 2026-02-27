
;; SKILL tool to open llm_test/test_v2/layout
procedure( open_llm_test()
    let((lib "llm_test" cell "test_v2" view "layout" cv)
        cv = dbOpenCellViewByType(lib cell view "maskLayout" "w")
        if(cv then
            printf("Successfully opened %s/%s/%s\n" lib cell view)
            hiSetCurrentWindow(cv->window)
            t
        else
            printf("Failed to open cellview\n")
            nil
        )
    )
)
