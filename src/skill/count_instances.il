
;; Get instance count in current cellview
cv = geGetWindowCellView()
if cv then
    insts = cv~>instances
    printf("Layout instance count: %d\n" length(insts))
    ;; Print first few
    for(i 0 min(5 length(insts)-1)
        printf("  %s (%s)\n" insts[i]~>name insts[i]~>cellName)
    )
else
    printf("No cellview open\n")
)
