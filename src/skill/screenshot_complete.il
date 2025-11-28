procedure(completeScreenshot(savePath)
    let((window timestamp filename)
        hiRedraw()
        window = hiGetCurrentWindow()
        if(!window then
            printf("Error: No active window found\n")
            return(nil)
        )
        hiZoomAbsoluteScale(window 0.9)
        sleep(2)
        hiWindowSaveImage(
            ?target window 
            ?path savePath 
            ?format "png" 
            ?toplevel nil
        )
        printf("Screenshot saved to: %s\n" savePath)
        savePath
    )
)