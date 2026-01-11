
;; get_schematic_net_count.il - Get number of nets in schematic
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "schematic" "" "a"))
      (netCount 0))
  (when cv
    (setq netCount (length (cv~>nets)))
    (dbClose cv)
    netCount))
