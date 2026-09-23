import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

// Root window. Replaces BackgroundRemoverApp (ui/main_window.py).
ApplicationWindow {
    id: window

    visible: true
    width: backend.windowDefaultWidth
    height: backend.windowDefaultHeight
    minimumWidth: backend.windowMinWidth
    minimumHeight: backend.windowMinHeight
    title: backend.windowTitle
    color: backend.colorBackground

    Component.onCompleted: backend.loadModels()

    RowLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 20

        ControlPanel {
            id: controlPanel
            Layout.minimumWidth: backend.controlPanelMinWidth
            Layout.maximumWidth: backend.controlPanelMaxWidth
            Layout.preferredWidth: backend.controlPanelMaxWidth
            Layout.fillHeight: true

            onUploadRequested: openDialog.open()
            onSaveRequested: {
                var folder = backend.inputImagePath.substring(0, backend.inputImagePath.lastIndexOf('/') + 1)
                saveDialog.currentFile = folder + backend.suggestedSaveName
                saveDialog.open()
            }
        }

        ImageViewPanel {
            id: imageView
            Layout.fillWidth: true
            Layout.fillHeight: true

            onUploadRequested: openDialog.open()
        }
    }

    FileDialog {
        id: openDialog
        title: backend.dialogOpenTitle
        nameFilters: [backend.imageFileFilter]
        onAccepted: backend.setInputImage(selectedFile)
    }

    FileDialog {
        id: saveDialog
        title: backend.dialogSaveTitle
        fileMode: FileDialog.SaveFile
        nameFilters: [backend.pngFileFilter]
        onAccepted: backend.saveImage(selectedFile)
    }

    MessageDialog {
        id: errorDialog
        title: backend.dialogErrorTitle
        buttons: MessageDialog.Ok
    }

    Connections {
        target: backend
        function onErrorOccurred(message) {
            errorDialog.text = message
            errorDialog.open()
        }
    }
}
