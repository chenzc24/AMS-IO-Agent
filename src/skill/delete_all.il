;; Delete all shapes in current cellview
pteSetAllVisible(?mode "All" ?panel "Layers")
selectedFigs = geSelectAllFig();
if (selectedFigs != nil) {
    leHiDelete();
}
hiRedraw()
"Deleted all shapes"