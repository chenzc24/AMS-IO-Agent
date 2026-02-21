
libName = "llm_test"
cellName = "test_v2"
viewName = "layout"
printf("Trying to open %s/%s/%s\n" libName cellName viewName)
cv = dbOpenCellViewByType(libName cellName viewName "maskLayout" "w")
if( cv then
    printf("Success.\n")
    geSetEditCellView(cv)
else
    printf("Failed.\n")
)
"Done"
