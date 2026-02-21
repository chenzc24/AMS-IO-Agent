
;; Return list of library names as string
procedure(getLibList()
    let((libs result)
        libs = ddGetLibList()
        result = ""
        foreach(lib libs
            result = strcat(result lib~>name " ")
        )
        println(result)
        result
    )
)
