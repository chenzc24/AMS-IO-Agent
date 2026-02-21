
libName = "llm_test"
cellName = "test_v2"
viewName = "layout"
cvId = dbOpenCellViewByType(libName cellName viewName "maskLayout" "r")
if(cvId then
    "EXISTS"
else
    "NOT EXISTS"
)
