import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

// Right panel: original/result previews + drag & drop + status bar.
// Replaces BackgroundRemoverApp._create_image_view_panel + ImageDisplayManager.
// No hardcoded colors/icons/strings: everything comes from `backend`.
ColumnLayout {
    id: root

    signal uploadRequested()

    spacing: 20

    RowLayout {
        Layout.fillWidth: true
        spacing: 20

        Label {
            text: backend.stringHeaderOriginal
            Layout.fillWidth: true
            font.pixelSize: 14
            font.bold: true
            color: backend.colorText
        }
        Label {
            text: backend.stringHeaderResult
            Layout.fillWidth: true
            font.pixelSize: 14
            font.bold: true
            color: backend.colorText
        }
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 20

        Rectangle {
            id: inputBox
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 250
            Layout.minimumHeight: 200
            radius: 16
            color: backend.colorSurface
            border.width: dropArea.containsDrag ? 3 : 2
            border.color: dropArea.containsDrag ? backend.colorPrimary : backend.colorBorder

            Image {
                anchors.fill: parent
                anchors.margins: 20
                fillMode: Image.PreserveAspectFit
                source: backend.inputImagePath
                visible: backend.inputImagePath !== ""
                asynchronous: true
                cache: false
            }

            ColumnLayout {
                anchors.centerIn: parent
                visible: backend.inputImagePath === ""
                spacing: 10

                Image {
                    id: inputPlaceholderIcon
                    Layout.alignment: Qt.AlignHCenter
                    source: backend.iconOriginal
                    sourceSize.width: 32
                    sourceSize.height: 32
                    visible: false
                }
                ColorOverlay {
                    Layout.alignment: Qt.AlignHCenter
                    width: inputPlaceholderIcon.width
                    height: inputPlaceholderIcon.height
                    source: inputPlaceholderIcon
                    color: backend.colorTextSecondary
                }
                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: backend.stringPlaceholderInput
                    color: backend.colorTextSecondary
                    font.pixelSize: 13
                }
            }

            DropArea {
                id: dropArea
                anchors.fill: parent
                onDropped: function(drop) {
                    if (drop.hasUrls && drop.urls.length > 0) {
                        backend.setInputImage(drop.urls[0])
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                enabled: backend.inputImagePath === ""
                onClicked: root.uploadRequested()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 250
            Layout.minimumHeight: 200
            radius: 16
            color: backend.colorSurface
            border.width: 2
            border.color: backend.colorBorder

            Image {
                anchors.fill: parent
                anchors.margins: 20
                fillMode: Image.PreserveAspectFit
                source: backend.outputImagePath
                visible: backend.outputImagePath !== ""
                asynchronous: true
                cache: false
            }

            ColumnLayout {
                anchors.centerIn: parent
                visible: backend.outputImagePath === ""
                spacing: 10

                Image {
                    id: outputPlaceholderIcon
                    Layout.alignment: Qt.AlignHCenter
                    source: backend.iconResult
                    sourceSize.width: 32
                    sourceSize.height: 32
                    visible: false
                }
                ColorOverlay {
                    Layout.alignment: Qt.AlignHCenter
                    width: outputPlaceholderIcon.width
                    height: outputPlaceholderIcon.height
                    source: outputPlaceholderIcon
                    color: backend.colorTextSecondary
                }
                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: backend.stringPlaceholderOutput
                    color: backend.colorTextSecondary
                    font.pixelSize: 13
                }
            }
        }
    }

    Rectangle {
        Layout.fillWidth: true
        radius: 12
        color: backend.colorSurface
        border.width: 1
        border.color: backend.colorBorder
        implicitHeight: statusLabel.implicitHeight + 32

        Label {
            id: statusLabel
            anchors.centerIn: parent
            text: backend.statusText
            font.pixelSize: 13
            font.bold: true
            color: backend.statusColor
        }
    }
}
