
fp = outfile("tmp_libs.txt" "w")
libs = ddGetObj()
foreach(lib libs
    fprintf(fp "%s\n" lib~>name)
)
close(fp)
