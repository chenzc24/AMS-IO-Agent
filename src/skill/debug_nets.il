
;; get_net_count.il - Get number of nets in layout
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (netCount 0))
  (when cv
    (setq netCount (length (cv~>nets)))
    (dbClose cv)
    netCount))
