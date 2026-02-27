
;; Return list of library names
libs = ddGetLibList()
mapcar('get libs~>name)
